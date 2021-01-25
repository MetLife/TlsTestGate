# TlsTestGate Azure DevOps Extension

## Overview

Test public or internal endpoints for non-compliant SSL/TLS settings. The extension can be inserted into a build or release pipeline and can serve as a compliance gate. This extension leverages the [SSLyze](https://github.com/nabla-c0d3/sslyze) API. Currently, SSL 2.0/3.0 and TLS 1.0/1.1 cipher suites are considered non-compliant. Additionally, certain TLS 1.2 ciphers that are considered "weak" are also considered non-compliant.

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

There are four inputs to the extension: Base URL, port, DNS server, and an option to fail the build or release:

* "Base URL" should be the DNS domain name or IP that you would like to scan (i.e., github.com or 140.82.113.4)

* "port" is optional and if omitted will default to TCP 443

* Since corporations often use [split-view DNS](https://en.wikipedia.org/wiki/Split-horizon_DNS), "DNS server" in this context is the network viewpoint you want to scan, either internal or external. This is accomplished by specifying a valid DNS server to use for name resolution. The default value for external will use Google (e.g. 8.8.8.8)

* "Fail task" will fail the build or release if non-compliant SSL/TLS settings are identified. The default is to publish the test results whether or not non-compliant settings are identified. Check the box if you want to gate on a failing test.

### Classic Pipeline Example

![TlsTestGate Extension](https://github.com/MetLife/TlsTestGate/blob/master/images/tlstestgateextension.png)

### YAML sample

Below is sample YAML to insert into your build or release pipeline.

```
steps:
- task: JoeGatt.TlsTestGate.custom-build-release-task.TlsTestGate@1
  displayName: 'github.com SSL/TLS Test Gate'
  inputs:
    baseURL: github.com
    port: 443
    dnsserver: 8.8.8.8
    failBuild: true
```

## Results
Vulnerabilities (if any) are automatically published to the build or release pipeline. To view them, simply click on the "Tests" tab. For each vulnerability discovered, a "failed test" will appear in the results.

![TlsTestGate Summary Results](https://github.com/MetLife/TlsTestGate/blob/master/images/resultsummary.png)

![TlsTestGate Summary Detail](https://github.com/MetLife/TlsTestGate/blob/master/images/resultdetail.png)

## Fixing Issues Identified by TlsTestGate

The Mozilla SSL Configuration [Generator](https://ssl-config.mozilla.org/) is an excellent resource to use to securely configure a web server. However, SSL/TLS settings are also often set on load balancers or reverse proxies. Fixing your local web server config may not fix the issue, depending on your network topology.

# Pre-requisites to Develop Locally

For more information on developing Azure DevOps extensions, refer to this [link](https://docs.microsoft.com/en-us/azure/devops/extend/develop/add-build-task?view=azure-devops) from Microsoft.

Development Environment Setup:

1. Create and setup virtual environment for python:
```bash
python3 -m venv foo
cd foo
source bin/activate
git clone https://github.com/metlife/tlstestgate.git
cd tlstestgate
pip install -r requirements.txt
```

2. Environment setup at a high level:

* Download and install node from [here](https://nodejs.org/en/download/).

* Install the typescript compiler: `npm install -g typescript`

* Install the TFS Cross Platform Command Line Interface (tfx-cli): `npm install -g tfx-cli`

* Install node packages:
```bash
cd buildAndReleaseTask
npm init
npm install azure-pipelines-task-lib
npm install azure-pipelines-tool-lib
npm install is-ip
npm install @types/node --save-dev
npm install @types/q --save-dev
```

3. Compile the extension:
```bash
cd buildAndReleaseTask
tsc
```
    
4. Test the extension locally:
```bash
cd buildAndReleaseTask
export INPUT_BASEURL = github.com
export INPUT_PORT = 443
export INPUT_DNSSERVER = 8.8.8.8
export INPUT_DECISION = false
node tlstestgate.js
```

## Testing the Scanner

To test the TLS/SSL scanning functionality, run:

```bash
cd tests
pytest -v test_tlstestgate.py --cov=buildAndReleaseTask --cov-report=xml
```

## Known Issues and Limitations of the Microsoft hosted Azure Pipeline agent

If you intend to test a private endpoint, it is probable that the Microsoft hosted agents do not have access to your internal network. If you want to test a private endpoint, please use a self-hosted Azure Pipeline agent. For self-hosted agents, Python 3.7 and above is required. Please refer to the links below for your target platform:

* [Linux](https://docs.microsoft.com/en-us/azure/devops/pipelines/agents/v2-linux?view=azure-devops)
* [MacOS](https://docs.microsoft.com/en-us/azure/devops/pipelines/agents/v2-osx?view=azure-devops)
* [Windows](https://docs.microsoft.com/en-us/azure/devops/pipelines/agents/v2-windows?view=azure-devops)

The location of the latest self-hosted agents is [here](https://docs.microsoft.com/en-us/azure/devops/pipelines/agents/v2-windows?view=azure-devops)

## References

[Here](https://www.paraesthesia.com/archive/2020/02/25/tips-for-custom-azure-devops-build-tasks/) are some useful tips for developing tasks for Azure DevOps.
