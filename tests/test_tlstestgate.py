""" TlsTestGate pytest tests

usage: pytest -v test_tlstestgate.py --cov=buildAndReleaseTask

"""

from buildAndReleaseTask.python.scanner import scan

DNS_SERVER = '8.8.8.8'


def test_scan_no_violations():
    """ Test scan on a host with no violations """

    results = scan(DNS_SERVER, "api.metlife.com", 443)

    # Check the output to ensure there are no violations
    assert results["Results"] == ["No SSL/TLS Violations found."]


def test_scan_with_violations():
    """ Test scan on a host with violations """

    results = scan(DNS_SERVER, "espn.com", 443)

    # Check the output to ensure there are no violations
    assert results["Results"] != ["No SSL/TLS Violations found."]


def test_dns_name_not_resolved():
    """ Test dns name not resolved """

    results = scan(DNS_SERVER, "joegatt.com", 443)

    # Check the output to ensure the DNS name could not resolve
    assert results["Results"] == ["joegatt.com exists but no A record."]


def test_external_dns_name_not_exist():
    """ Test NXDOMAIN """

    results = scan(DNS_SERVER, "jeogatt.com", 443)

    # Check the output to ensure the DNS name could not resolve
    assert results["Results"] == ["The DNS name jeogatt.com does not exist."]


def test_sslyze_timeout():
    """ Test sslyze timeout """

    results = scan(DNS_SERVER, "bbbbbbbbbbbbbbb.com", 443)

    # Check the output to ensure the DNS name could not resolve
    assert results["Results"] == ["Connection to the server timed out"]


def test_bad_dnsserver():
    """ Test bad dns server """

    results = scan('8.8.7.6', "espn.com", 443)

    # Check the output to ensure the DNS name could not resolve
    assert results["Results"] == ["The DNS operation timed out."]


def test_port_timeout():
    """ Test timeout connecting to a port """

    results = scan(DNS_SERVER, "yahoo.com", 8443)

    # Check the output to ensure the DNS name could not resolve
    assert results["Results"] == ["Connection to the server timed out"]


def test_by_ip_no_violations():
    """ Test policy scan on an external ip with no violations """

    results = scan(DNS_SERVER, "216.163.251.205", 443)

    # Check the output to ensure there are no violations
    assert results["Results"] != ["No SSL/TLS Violations found."]
