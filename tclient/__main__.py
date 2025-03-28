import httpx
import pytest
import yaml
from pathlib import Path
from box import Box
from owslib.csw import CatalogueServiceWeb
from lxml import etree
from rich.console import Console
from rich.table import Table


REPO_ROOT = Path(__file__).parent.parent.resolve()

config = Box.from_yaml(filename=REPO_ROOT / "config.yml", Loader=yaml.FullLoader)

print()
print(f"testing {config.csw.endpoint}")


@pytest.fixture(scope="module")
def get_csw_server_202():
    return CatalogueServiceWeb(config.csw.endpoint, version="2.0.2")


@pytest.fixture(scope="module")
def get_csw_server_300():
    return CatalogueServiceWeb(config.csw.endpoint, version="3.0.0")


def test_operations():
    for version in config.csw.versions:
        csw = CatalogueServiceWeb(config.csw.endpoint, version="2.0.2")
        expected_ops = set(config.csw.operations)
        actual_ops = set([x.name for x in csw.operations])

        table.add_row("2", version, "GetCapabilities operations listing", (expected_ops == actual_ops))


def get_capabilities(version):
    return httpx.get(
        config.csw.endpoint,
        params={
            "service": "CSW",
            "version": version,
            "request": "GetCapabilities",
        }
    )

def print_result(value, message):
    if value:
        return "ok"
    else:
        return f"ERROR: {message}"


def test_GetCapabilities_validity(get_csw_server_202):
    for version in config.csw.versions:
        r = get_capabilities(version)

        table.add_row("1a", version, "GetCapabilities response received", print_result(r.is_success, r.status_code))

        et = etree.fromstring(r.content)
        result = et.tag == f"{{http://www.opengis.net/cat/csw/{version}}}Capabilities"
        table.add_row("1b", version, "GetCapabilities root element ok", print_result(result, f"csw:Capabilities is not the root element, {et.tag} is"))

        _21 = '<ows:Value>Filter_Capabilities</ows:Value>' in r.text
        _22 = '<ows:Value>OperationsMetadata</ows:Value>' in r.text
        _23 = '<ows:Value>ServiceIdentification</ows:Value>' in r.text
        _24 = '<ows:Value>ServiceProvider</ows:Value>' in r.text
        table.add_row("2", version, "GetCapabilities Section parameters ok", print_result(_21 and _22 and _23 and _24, "<ows:Value> not correctly listed"))  # TODO: make specific


def test_GetCapabilities_filter_capabilities(get_csw_server_202):
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
        table.add_row("3", version, "GetCapabilities Filter Capabilities ok", print_result(r.is_success, r.status_code))




if __name__ == "__main__":
    table = Table("Test ID", "Version", "Test Description", "Result")
    console = Console()
    test_GetCapabilities_validity(get_csw_server_202)
    console.print(table)