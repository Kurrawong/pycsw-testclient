from pathlib import Path

import httpx
import pytest
import yaml
from box import Box
from lxml import etree
from owslib.csw import CatalogueServiceWeb
from rich.console import Console
from rich.table import Table

from utils import *


@pytest.fixture(scope="module")
def get_csw_server_202():
    return CatalogueServiceWeb(config.csw.endpoint, version="2.0.2")


@pytest.fixture(scope="module")
def get_csw_server_300():
    return CatalogueServiceWeb(config.csw.endpoint, version="3.0.0")


def get_capabilities(version):
    return httpx.get(
        config.csw.endpoint,
        params={
            "service": "CSW",
            "version": version,
            "request": "GetCapabilities",
        }
    )


def test_01_GetCapabilities_validity():
    for version in config.csw.versions:
        r = get_capabilities(version)
        test = Box({
            "id": "01",
            "name": "GetCapabilities response received",
            "result": r.is_success,
            "message": f"Status code is {r.status_code}",
        })
        table.add_row(test.id, version, test.name, print_result(test.result, test.message), style=make_row_style(version))

        if r.is_success:
            et = etree.fromstring(r.content)
            test = Box({
                "id": "01 b",
                "name": "GetCapabilities root element",
                "result": et.tag == f"{{http://www.opengis.net/cat/csw/{version}}}Capabilities",
                "message": f"{et.tag} is the root",
            })
            table.add_row(test.id, version, test.name, print_result(test.result, test.message), style=make_row_style(version))

            sections = [
                '<ows:Value>Filter_Capabilities</ows:Value>',
                '<ows:Value>OperationsMetadata</ows:Value>',
                '<ows:Value>ServiceIdentification</ows:Value>',
                '<ows:Value>ServiceProvider</ows:Value>'
            ]
            section_results = [True if section in r.text else False for section in sections]
            message = ""
            for i, result in enumerate(section_results):
                if not result:
                    message += sections[i]
            message += " not found"
            test = Box({
                "id": "01 d",
                "name": "GetCapabilities Section parameters",
                "result": all(section_results),
                "message": message,
            })
            table.add_row(test.id, version, test.name, print_result(test.result, test.message), style=make_row_style(version))


def test_02_GetCapabilities_operations():
    for version in config.csw.versions:
        csw = CatalogueServiceWeb(config.csw.endpoint, version="2.0.2")
        expected_ops = set(config.csw.operations)
        actual_ops = set([x.name for x in csw.operations])
        test = Box({
            "id": "02",
            "name": "GetCapabilities operations listing",
            "result": expected_ops == actual_ops,
            "message": f"{', '.join(expected_ops - actual_ops)} missing on server, {', '.join(actual_ops - expected_ops)} present on server",
        })
        table.add_row(test.id, version, test.name, print_result(test.result, test.message), style=make_row_style(version))


def test_03_GetCapabilities_filter_capabilities():
    for version in config.csw.versions:
        r = httpx.get(
            config.csw.endpoint,
            params={
                "service": "CSW",
                "version": version,
                "request": "GetCapabilities",
                "sections": "filter_capabilities"
            }
        )

        test = Box({
            "id": "03",
            "name": "GetCapabilities Filter Capabilities",
            "result": '<ogc:SpatialOperator name="BBOX"/>' in r.text,
            "message": '<ogc:SpatialOperator name="BBOX"/> not see in response',
        })
        table.add_row(test.id, version, test.name, print_result(test.result, test.message), style=make_row_style(version))


def test_04_DescribeRecord():
    for version in config.csw.versions:
        r = httpx.get(
            config.csw.endpoint,
            params={
                "service": "CSW",
                "version": version,
                "request": "DescribeRecord",
            }
        )

        test = Box({
            "id": "04",
            "name": "DescribeRecord response received",
            "result": r.is_success,
            "message": f"Status code is {r.status_code}",
        })
        table.add_row(test.id, version, test.name, print_result(test.result, test.message), style=make_row_style(version))

        if r.is_success:
            et = etree.fromstring(r.content)
            test = Box({
                "id": "04 b",
                "name": "DescribeRecord root element",
                "result": et.tag == f"{{http://www.opengis.net/cat/csw/{version}}}DescribeRecordResponse",
                "message": f"{et.tag} is the root",
            })
            table.add_row(test.id, version, test.name, print_result(test.result, test.message), style=make_row_style(version))

            if test.result:
                xmlschema = etree.XMLSchema(etree.parse(REPO_ROOT / "tclient/schemas/CSW-discovery.xsd"))

                test = Box({
                    "id": "04 c",
                    "name": "DescribeRecord schematically valid",
                    "result": xmlschema.validate(et),
                    "message": f"DescribeRecord is not schema valid",
                })
                table.add_row(test.id, version, test.name, print_result(test.result, test.message),
                              style=make_row_style(version))


if __name__ == "__main__":
    REPO_ROOT = Path(__file__).parent.parent.resolve()
    config = Box.from_yaml(filename=REPO_ROOT / "config.yml", Loader=yaml.FullLoader)

    console = Console()

    console.print(f"testing {config.csw.endpoint}")

    table = Table("Test ID", "Version", "Test Description", "Result")

    # Tests
    test_01_GetCapabilities_validity()
    test_02_GetCapabilities_operations()
    test_03_GetCapabilities_filter_capabilities()
    test_04_DescribeRecord()
    # End Tests

    console.print(table)