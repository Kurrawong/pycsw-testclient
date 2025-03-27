# pyCSW Test Client

This repository contains the source code for a testing web client for the [pyCSW](https://pycsw.org) application.

This client runs and makes a series of web requests of a pyCSW installation and checks that the XML responses sent back match requirements.

## How It Works

This library contains a list of 30+ individual test functions, created using Pythons [pytest](https://pypi.org/project/pytest/) testing framework. This framework allows nice running and reporting of tests within a Python environment.

The tests are run multiple times each with different parameters, chosen to cover all the elements of the target pyCSW installation.

The actual sending of web requests to a pyCSW server is managed by [OWSLib](https://pypi.org/project/OWSLib/) and [httpx](https://pypi.org/project/httpx/) Python code. The first is a dedicated OGC API client library. The second a general web requests library.

The testing of response payloads is doe either with OWLLib or by parsing response XML with the general-purpose [lxml](https://pypi.org/project/lxml/) library which performs validation and XPath queries on results.

Results from tests are reported to the command line in the usual pytest way.

## License & Reuse

_This test client has initially been developed to test the [Geological Survey of South Australia](https://www.energymining.sa.gov.au/industry/geological-survey)'s pyCSW installation and is optimised for that. For use elsewhere, some recoding will likely be needed._

The code in this repository is licensed for reuse using the [MIT License](https://opensource.org/license/mit), as is the code of the pyCSW application. See the LICENSE file for details.

The implementation of CSW in Python as pyCSW is governed by the [pyCSW Steering Committee](https://pycsw.org/community/psc.html).

The Catalogue Service for the Web (CSW) specification that pyCSW implements is an [Open Geospatial Consortium](https://www.ogc.org) standard that is freely available.

## Installation

This application is designed to be used as a Python application, executed within a Python IDE such as PyCharm or Visual Studio Code. It does not provide all the necessary features to operate as a stand-alone Command Line application.

It may be used as a Python library in other Python applications such as automated testing scripts.

To install this test client on a computer, you will need to be able to:

1. Provide a Python (virtual) environment
    * Python 3.12 is recommended
2. Install the required Python packages
    * as listed in `requirements-conda.txt` - for Conda
    * as listed in `requirements-pip.txt` - for PIP

## Contact

This test client was developed by KurrawongAI. Contact them for more info:

**KurrawongAI**  
<https://kurrawong.ai>  
<info@kurrawong.net>  

...you can also add Issues etc. to the GitHub repository this is in...

## Admin

conda list -e > requirements-conda.txt

pip list --format=freeze > requirements-pip.txt
