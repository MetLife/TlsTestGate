""" Scanner module """

import argparse
import os

from dns import resolver
from junitparser import TestCase, TestSuite, JUnitXml, Failure
from sslyze.errors import ConnectionToServerFailed
from sslyze.plugins import scan_commands
from sslyze.plugins.openssl_cipher_suites.implementation import CipherSuitesScanResult
from sslyze.scanner.models import ServerScanRequest, ServerScanStatusEnum
from sslyze.scanner.scanner import Scanner
from sslyze.scanner.scan_command_attempt import ScanCommandAttemptStatusEnum
from sslyze.server_setting import ServerNetworkLocation


# SSl 2.0/3.0 and TLS 1.0/1.1 are prohibited cipher suites
CIPHER_SUITES = {
    scan_commands.ScanCommand.SSL_2_0_CIPHER_SUITES,
    scan_commands.ScanCommand.SSL_3_0_CIPHER_SUITES,
    scan_commands.ScanCommand.TLS_1_0_CIPHER_SUITES,
    scan_commands.ScanCommand.TLS_1_1_CIPHER_SUITES,
    scan_commands.ScanCommand.TLS_1_2_CIPHER_SUITES,
}

# Currently, only The following TLS 1.2 ciphers are considered "strong"
OK_TLS12_CIPHERS = {
    "TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256",
    "TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256",
    "TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384",
    "TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384",
    "TLS_ECDHE_ECDSA_WITH_CHACHA20_POLY1305_SHA256",
    "TLS_ECDHE_RSA_WITH_CHACHA20_POLY1305_SHA256",
    "TLS_DHE_RSA_WITH_AES_128_GCM_SHA256",
    "TLS_DHE_RSA_WITH_AES_256_GCM_SHA384",
    "TLS_DHE_RSA_WITH_CHACHA20_POLY1305_SHA256",
}

# Create the parser
arg_parser = argparse.ArgumentParser(prog="scanner")

# Add the arguments
arg_parser.add_argument(
    "--target",
    "-t",
    metavar="target",
    type=str,
    required=True,
    help="The target to test",
)

arg_parser.add_argument(
    "--dns",
    "-d",
    metavar="dnsserver",
    type=str,
    required=True,
    help="The DNS server to use",
)

arg_parser.add_argument(
    "--port",
    "-p",
    metavar="port",
    type=int,
    required=False,
    default=443,
    help="The port to test (default is 443)",
)

arg_parser.add_argument(
    "--decision",
    metavar="decision",
    type=str,
    required=True,
    default="pass",
    choices=["fail", "pass"],
    help="Fail task if there are test failures?",
)

# Alias str type to better reflect the intented type and value
FQDN = str
IpAddr = str


def resolve_dnsname_to_ip(dns_server: IpAddr, dnsname: FQDN) -> IpAddr:
    """Resolve dns name and return IP"""
    ip_list = []  # results

    # dnspython config
    res = resolver.Resolver(configure=False)  # Do not read resolv.conf
    res.timeout = 3
    res.lifetime = 3  # How many seconds a query should run before timing out
    res.nameservers = [dns_server]  # DNS server may not be online
    #  Need better error handling in case internal DNS server is not online
    #  Right now it just times out the query, which is handled below

    try:
        answers = res.resolve(dnsname, search=False)
        for answer in answers.rrset:
            ip_list.append(answer.address)
        return ip_list[0]  # Return the first IP of the DNS Answer

    except resolver.NoAnswer as err:
        raise Exception(f"{dnsname} exists but no A record.") from err

    except resolver.NXDOMAIN as err:
        raise Exception(f"The DNS name {dnsname} does not exist.") from err

    except resolver.Timeout as err:
        raise Exception("The DNS operation timed out.") from err

    except resolver.NoNameservers as err:
        raise Exception(err.msg) from err  # Should trigger if a DNS server is offline

    except Exception as err:
        # If you are here, you are jacked
        raise ValueError("Catch all error in scanner.py") from err


def scan(dns_server: IpAddr, name: str, port: int) -> dict:
    """Three inputs: DNS server, web site name, and ip"""

    scan_output = new_results()
    scan_output["Hostname"] = name
    scan_output["DNS"] = dns_server

    # Validate hostname and resolve to IP
    try:
        target_ip = resolve_dnsname_to_ip(dns_server, name)
        scan_output["IP"] = target_ip

    except Exception as err:
        scan_output["Results"].append(err.args[0])
        return scan_output

    server_location = ServerNetworkLocation(name, port, target_ip)
    try:
        # pylint: disable=too-many-function-args
        scan_request = [
            ServerScanRequest(
                server_location=server_location, scan_commands=CIPHER_SUITES
            )
        ]
    except ConnectionToServerFailed as err:
        scan_output["Results"].append(err.args[0])
        return scan_output

    scanner = Scanner()
    scanner.queue_scans(scan_request)

    for results in scanner.get_results():
        if results.scan_status == ServerScanStatusEnum.ERROR_NO_CONNECTIVITY:
            scan_output["Results"].append(f"Error: Could not connect to {name}:{port}")
            return scan_output

        for suite in CIPHER_SUITES:
            tlsscanresult: CipherSuitesScanResult = getattr(
                results.scan_result, suite
            ).result
            tlsscanstatus = getattr(results.scan_result, suite).status
            if tlsscanresult.is_tls_version_supported:
                if tlsscanstatus == ScanCommandAttemptStatusEnum.ERROR:
                    scan_output["Results"].append(
                        {
                            "Version": f"{cipher_version}",
                            "Cipher": f"Error during scan of {cipher_version}",
                        }
                    )
                else:
                    cipher_version: str = tlsscanresult.tls_version_used.name
                    if cipher_version == "TLS_1_2":
                        for (
                            accepted_cipher_suite
                        ) in tlsscanresult.accepted_cipher_suites:
                            if (
                                accepted_cipher_suite.cipher_suite.name
                                not in OK_TLS12_CIPHERS
                            ):
                                scan_output["Results"].append(
                                    {
                                        "Version": f"{cipher_version}",
                                        "Cipher": f"{accepted_cipher_suite.cipher_suite.name}",
                                    }
                                )
                    else:
                        for (
                            accepted_cipher_suite
                        ) in tlsscanresult.accepted_cipher_suites:
                            scan_output["Results"].append(
                                {
                                    "Version": f"{cipher_version}",
                                    "Cipher": f"{accepted_cipher_suite.cipher_suite.name}",
                                }
                            )

    if len(scan_output["Results"]) == 0:
        scan_output["Results"].append("No SSL/TLS Violations found.")

    return scan_output


def new_results() -> dict:
    """Create the results dict"""

    return {"Hostname": None, "IP": None, "DNS": None, "Results": []}


def write_output(target, results) -> None:
    """Write scan results in junitxml format"""

    test_case = TestCase(f"{target}")
    test_case.name = f"{target}"
    if results["Results"] != ["No SSL/TLS Violations found."]:
        test_case.result = [Failure(results)]
    else:
        test_case.result = results

    suite = TestSuite("SSLChecker")
    suite.add_testcase(test_case)

    xml = JUnitXml()
    xml.add_testsuite(suite)
    xml.write("test-output.xml")


def main() -> None:

    """Main function"""
    # Execute the parse_args() method
    args = arg_parser.parse_args()
    target = args.target
    dns = args.dns
    arg_port = args.port
    if args.decision == "pass":
        decision = "false"
    else:
        decision = "true"

    scan_results = scan(dns, target, arg_port)

    write_output(target, scan_results)

    output = os.path.normpath(
        os.path.abspath(os.path.expanduser(os.path.expandvars("test-output.xml")))
    )

    # Borrowed from pytest-azurepipelines
    # https://github.com/tonybaloney/pytest-azurepipelines/blob/master/pytest_azurepipelines.py
    print(
        f"##vso[results.publish type=JUnit;runTitle='TlsTestGate';failTaskOnFailedTests={decision};publishRunAttachments=false;]{output}"  # pylint: disable=line-too-long
    )


if __name__ == "__main__":

    main()
