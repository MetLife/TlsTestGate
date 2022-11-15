# Changelog for TlsTestGate

# v1.0.0
- Initial Release

# v1.1.0
- Version bump for sslyze and junitparser
- Added tox for testing scanner functionality on Python 3.7 and 3.8
- Fixed dns resolution error handling
- Added azure-pipelines.yaml to automate tox testing

# v1.2.0
- Rename internal variable (non breaking change)
- Update node packages
- Improved documentation with screen shots
- Imporved python version detection and error handling

# v1.3.0
- Added support for Python 3.9 with upgrade of SSLyze to 4.0.x
- Added support for junitparser 2.0.0 (fixes breaking change)
- Removed hardcoded python package configuration from tlstestgate.ts
- Added tox tests for Python 3.9
- Added pytest to validate junitparser functionality in scanner.py

# v1.4.0
- Created docker development environment in VS Code to work around M1 compatibility issues with SSLyze/NaSSL
- Updated to SSLyze 5.0.0
- Changed minimum Azure Pipeline Agent version to 2.144.0 in support of Node10
- Updated azure-pipelines-task-lib and azure-pipelines-tool-lib to latest version
- Formatted python files with black and linted with pylint
- Fixed test case that purposely failed resolving bbbbbbbbbbbbbbb.com because someone out there is now using it

# v1.0.10
- Align changelog version scheme with Azure DevOps Marketplace
- Removed chai, mocha, tfx-cli, ts-node, and typescript from dev-dependencies and moved install into Dockerfile
- Added eslint to project and pipelines
- Updated SSLyze to 5.0.3 for Python 3.10 support
- Removed is-Ip TypeScript dependency
- Fixed test case that purposely failed resolving bbbbbbbbbbbbbbbbbbbbbbbbb.com because someone out there is now using it

# v1.0.11
- Fix yaml example on Visual Studio marketplace

# v1.0.12
- Updated all npm and python dependencies
- Added dependabot
- Added Microsoft Typescript security linters
- Removed deprecated node api call (url.parse)
