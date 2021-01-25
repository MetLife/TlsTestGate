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
