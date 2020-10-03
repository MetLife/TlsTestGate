# TlsTestGate Azure DevOps Extension

## Overview

Test public or internal endpoints for non-compliant SSL/TLS settings. The extension can be inserted into a build or release pipeline and can serve as a compliance gate. This extension leverages the [SSLyze](https://github.com/nabla-c0d3/sslyze) API. Currently, SSL 2.0/3.0 and TLS 1.0/1.1 cipher suites are considered non-compliant and will fail the scan. Additionally, certain TLS 1.2 ciphers that are considered "weak" will also fail the scan.

## Valid TLS 1.2 Ciphers

Some cipher suites within TLS 1.2 are considered [weak](https://blog.qualys.com/product-tech/2019/04/22/zombie-poodle-and-goldendoodle-vulnerabilities#). The cipher suites listed below are considered "secure" for now and may be updated in the future:

* TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256
* TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256
* TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384
* TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384
* TLS_ECDHE_ECDSA_WITH_CHACHA20_POLY1305_SHA256
* TLS_ECDHE_RSA_WITH_CHACHA20_POLY1305_SHA256
* TLS_DHE_RSA_WITH_AES_128_GCM_SHA256
* TLS_DHE_RSA_WITH_AES_256_GCM_SHA384
* TLS_DHE_RSA_WITH_CHACHA20_POLY1305_SHA256

## Usage

There are four inputs to the extension: Base URL, port, DNS server, and fail task:

* "Base URL" should be the DNS domain name or IP that you would like to scan (i.e., github.com or 140.82.113.4)

* "port" is optional and if omitted will default to TCP 443

* Since corporations often use [split-view DNS](https://en.wikipedia.org/wiki/Split-horizon_DNS), "DNS server" in this context is the network viewpoint you want to scan, either internal or external. This is accomplished by specifying a valid DNS server to use for name resolution. The default value for external will use Google (e.g. 8.8.8.8)

* "Fail task" will fail the task in the build or release pipeline if the test fails. The default is to simply publish the test results whether the test passes or fails. Check the box if you want to gate on a failing test.

## Fixing Issues Identified by TlsTestGate

The Mozilla SSL Configuration [Generator](https://ssl-config.mozilla.org/) is an excellent resource to use to securely configure a web server. However, SSL/TLS settings are also often set on load balancers or reverse proxies. Fixing your local web server config may not fix the issue, depending on your network topology.

## Feedback

Send me mail at joe@metlife.com or visit our page at https://github.com/MetLife/TlsTestGate
