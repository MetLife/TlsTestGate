""" TlsTestGate pytest tests

usage: pytest -v test_tlstestgate.py --cov=buildAndReleaseTask

"""
import html
import json
import os

from junitparser import JUnitXml

from buildAndReleaseTask.python.scanner import scan, write_output

DNS_SERVER = "8.8.8.8"

TEST_RESULTS = {
    "Results": [
        {"Version": "TLS_1_1", "Cipher": "TLS_RSA_WITH_AES_256_CBC_SHA"},
        {"Version": "TLS_1_1", "Cipher": "TLS_RSA_WITH_AES_128_CBC_SHA"},
        {"Version": "TLS_1_1", "Cipher": "TLS_RSA_WITH_3DES_EDE_CBC_SHA"},
        {"Version": "TLS_1_1", "Cipher": "TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA"},
        {"Version": "TLS_1_1", "Cipher": "TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA"},
        {"Version": "TLS_1_0", "Cipher": "TLS_RSA_WITH_AES_256_CBC_SHA"},
        {"Version": "TLS_1_0", "Cipher": "TLS_RSA_WITH_AES_128_CBC_SHA"},
        {"Version": "TLS_1_0", "Cipher": "TLS_RSA_WITH_3DES_EDE_CBC_SHA"},
        {"Version": "TLS_1_0", "Cipher": "TLS_ECDHE_RSA_WITH_AES_256_CBC_SHA"},
        {"Version": "TLS_1_0", "Cipher": "TLS_ECDHE_RSA_WITH_AES_128_CBC_SHA"},
    ]
}


def test_scan_no_violations():
    """Test scan on a host with no violations"""

    results = scan(DNS_SERVER, "api.metlife.com", 443)

    # Check the output to ensure there are no violations
    assert results["Results"] == ["No SSL/TLS Violations found."]


def test_scan_with_violations():
    """Test scan on a host with violations"""

    results = scan(DNS_SERVER, "espn.com", 443)

    # Check the output to ensure there are no violations
    assert results["Results"] != ["No SSL/TLS Violations found."]


def test_dns_name_not_resolved():
    """Test dns name not resolved"""

    results = scan(DNS_SERVER, "joegatt.com", 443)

    # Check the output to ensure the DNS name could not resolve
    assert results["Results"] == ["joegatt.com exists but no A record."]


def test_external_dns_name_not_exist():
    """Test NXDOMAIN"""

    results = scan(DNS_SERVER, "jeogatt.com", 443)

    # Check the output to ensure the DNS name could not resolve
    assert results["Results"] == ["The DNS name jeogatt.com does not exist."]


def test_sslyze_timeout():
    """Test sslyze timeout"""

    bad_dns_domain = "bbbbbbbbbbbbbbbbbbbbbbbbb.com"
    results = scan(DNS_SERVER, bad_dns_domain, 443)

    # Check the output to ensure the DNS name could not resolve
    assert results["Results"] == [f"The DNS name {bad_dns_domain} does not exist."]


def test_bad_dnsserver():
    """Test bad dns server"""

    results = scan("8.8.7.6", "espn.com", 443)

    # Check the output to ensure the DNS name could not resolve
    assert results["Results"] == ["The DNS operation timed out."]


def test_port_timeout():
    """Test timeout connecting to a port"""

    results = scan(DNS_SERVER, "yahoo.com", 8443)

    # Check the output to ensure the scan could not complete
    assert results["Results"] == ["Error: Could not connect to yahoo.com:8443"]


def test_by_ip_no_violations():
    """Test policy scan on an external ip with no violations"""

    results = scan(DNS_SERVER, "216.163.251.205", 443)

    # Check the output to ensure there are no violations
    assert results["Results"] != ["No SSL/TLS Violations found."]


def test_junit_parser_with_violations():
    """Test writing results to test-output.xml and reading output"""

    # Write the test-output.xml
    write_output("foo", TEST_RESULTS)

    # Load it
    output = os.path.normpath(
        os.path.abspath(os.path.expanduser(os.path.expandvars("test-output.xml")))
    )

    xml = JUnitXml.fromfile(output)
    for suite in xml:
        # Should be one failure
        assert suite.failures == 1

        for case in suite:
            for element in case:
                results = html.unescape(element.message)
                json_results = json.loads(results.replace("'", '"'))
                # Should be 10 results
                assert len(json_results["Results"]) == 10
