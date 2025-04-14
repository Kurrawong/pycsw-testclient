# CSW Test Client

This repository contains a tool that can be used to test the conformance of a [Catalogue Service for the Web](https://www.ogc.org/publications/standard/cat/) endpoint to a stated set of version, operation and profile requirements. It is expected to be used against installations of tools such as [pyCSW](https://pycsw.org), [GeoNetwork](https://geonetwork-opensource.org/) and so on.

> [!NOTE]
> The _Open Geospatial Consurium_ provides the official [CSW Conformance Test Suite](https://cite.opengeospatial.org/te2/about/csw/2.0.2/site/) but this tool is designed to be simpler to configure for customised testing - only certain versions of CSW implemented etc. - and to be used both 'manually' by people and automatically within system checking workflows to ensure that CSW servers are working as expected.

## How It Works

This library contains a list of 30+ individual test functions, created using Python's [pytest](https://pypi.org/project/pytest/) testing framework. The tests work nicely running and displaing results within a Python environment, on a Linux/Mac/Windows command line or within infrastructure pipeline code, e.g. system checking functions.

The tests are run multiple times each with different parameters, chosen by declared configuration, to cover all the elements required to be tested of the target CSW installation.

The actual sending of web requests to a CSW server is managed by the basic Python HTTP interactions library [httpx](https://pypi.org/project/httpx/) with some dditional testing using the [OWSLib](https://pypi.org/project/OWSLib/) OGC Web Service client. 

The testing of responses is doe either with HTTPX - is the endpoint even up? - or by parsing response XML with the general-purpose [lxml](https://pypi.org/project/lxml/) library which performs schema validation and XPath queries on results, the specifics of which have been established per test.

## Installation

This application is designed to be used as a Python application, executed within a Python IDE such as PyCharm or Visual Studio Code. It does not provide all the necessary features to operate as a stand-alone Command Line application.

It may be used as a Python library in other Python applications such as automated testing scripts.

To install this test client on a computer, you will need to be able to:

1. Provide a Python (virtual) environment
    * Python 3.12 is recommended
2. Install the required Python packages
    * as listed in `requirements-conda.txt` - for Conda
    * as listed in `requirements-pip.txt` - for PIP

## Use

### Configure the testing parameters

You need a file called `config.yml` in the root directory of the repository that gives the testing parameters, such as server location.

There is an example file - `config-example.yml` - that can be copied to `config.yml`, have it's values altered, and used.

### Run the tests from the command line

From within the root folder of the repository, with the application's dependencies installed on the available Python environment, run:

```bash
python tclient
```

You should see a result like this:

```bash
testing https://mesac-dev-csw.azurewebsites.net/csw
┏━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━┓
┃ Test ID ┃ Version ┃ Test Description                      ┃ Result ┃
┡━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━┩
│ 1a      │ 2.0.2   │ GetCapabilities response received     │ ok     │
│ 1b      │ 2.0.2   │ GetCapabilities root element ok       │ ok     │
│ 2       │ 2.0.2   │ GetCapabilities Section parameters ok │ ok     │
└─────────┴─────────┴───────────────────────────────────────┴────────┘
```

## License & Reuse

_This test client has initially been developed to test the [Geological Survey of South Australia](https://www.energymining.sa.gov.au/industry/geological-survey)'s pyCSW installation and is optimised for that. For use elsewhere, some recoding will likely be needed._

The code in this repository is licensed for reuse using the [MIT License](https://opensource.org/license/mit), as is the code of the pyCSW application. See the LICENSE file for details.

The implementation of CSW in Python as pyCSW is governed by the [pyCSW Steering Committee](https://pycsw.org/community/psc.html).

The Catalogue Service for the Web (CSW) specification that pyCSW implements is an [Open Geospatial Consortium](https://www.ogc.org) standard that is freely available.

## Contact

This test client was developed by KurrawongAI. Contact them for more info:

**KurrawongAI**  
<https://kurrawong.ai>  
<info@kurrawong.net>  

...you can also add Issues etc. to the GitHub repository this is in...

## Admin

### Commands

Generate conda dependencies:

```
conda list -e > requirements-conda.txt
```

Generate PIP dependencies:

```
pip list --format=freeze > requirements-pip.txt
```

### Release process

* commit changes
* pass all tests
* update version in pyproject.toml
* git tag {VERSION}
* git push
* git push --tags
* make release on GitHub
