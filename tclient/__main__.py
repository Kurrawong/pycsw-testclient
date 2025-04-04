from pathlib import Path

import httpx
import yaml
from box import Box
from lxml import etree
from owslib.csw import CatalogueServiceWeb
from rich.console import Console
from rich.table import Table

from utils import *


# @pytest.fixture(scope="module")
# def get_csw_server_202():
#     return CatalogueServiceWeb(config.csw.endpoint, version="2.0.2")
#
#
# @pytest.fixture(scope="module")
# def get_csw_server_300():
#     return CatalogueServiceWeb(config.csw.endpoint, version="3.0.0")


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
    print("01...")
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
    print("02...")
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
    print("03...")
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
    print("04...")
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

        print("04b...")
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
                print("04c...long wait...")
                xmlschema = etree.XMLSchema(etree.parse(REPO_ROOT / "tclient/schemas/CSW-discovery.xsd"))

                test = Box({
                    "id": "04 c",
                    "name": "DescribeRecord schematically valid",
                    "result": xmlschema.validate(et),
                    "message": f"DescribeRecord is not schema valid",
                })
                table.add_row(test.id, version, test.name, print_result(test.result, test.message),
                              style=make_row_style(version))

                print("04d...")
                # only call JSON as the original request called XML
                r1 = httpx.get(
                    config.csw.endpoint,
                    params={
                        "service": "CSW",
                        "version": version,
                        "request": "DescribeRecord",
                        "outputFormat": "application/json",
                    }
                )

                test = Box({
                    "id": "04 d",
                    "name": "DescribeRecord Description of Record Schema as XML and JSON",
                    "result": r1.is_success,
                    "message": f"DescribeRecord is not available in both XML and JSON",
                })
                table.add_row(test.id, version, test.name, print_result(test.result, test.message),
                              style=make_row_style(version))

                print("04e...")
                schema_languages = [
                    "http://www.w3.org/2001/XMLSchema",
                    "http://www.w3.org/TR/xmlschema-1/",
                    "http://www.w3.org/XML/Schema",
                ]
                p4 = True
                for schema_language in schema_languages:
                    r3 = httpx.get(
                        config.csw.endpoint,
                        params={
                            "service": "CSW",
                            "version": version,
                            "request": "DescribeRecord",
                            "schemaLanguage": schema_language,
                        }
                    )
                    if not "csw:DescribeRecordResponse" in r3.text:
                        p4 = False

                r4 = httpx.get(
                    config.csw.endpoint,
                    params={
                        "service": "CSW",
                        "version": version,
                        "request": "DescribeRecord",
                        "schemaLanguage": "http://www.w3.org/2001/BROKEN",
                    }
                )
                if not "ows:ExceptionReport" in r4.text:
                    p4 = False

                test = Box({
                    "id": "04 e",
                    "name": "DescribeRecord Description of Record Schema with schemaLanguage param",
                    "result": p4,
                    "message": f"Description of Record Schema with schemaLanguage param is invalid",
                })
                table.add_row(test.id, version, test.name, print_result(test.result, test.message),
                              style=make_row_style(version))

                print("04f...")
                type_names = [
                    "csw:Record",
                    "mdb:MD_Metadata"
                ]
                p5 = True
                for type_name in type_names:
                    r5 = httpx.get(
                        config.csw.endpoint,
                        params={
                            "service": "CSW",
                            "version": version,
                            "request": "DescribeRecord",
                            "typeName": type_name,
                        }
                    )
                    if not "csw:DescribeRecordResponse" in r5.text:
                        p5 = False

                test = Box({
                    "id": "04 f",
                    "name": "DescribeRecord Description of Record Schema with typeName param",
                    "result": p5,
                    "message": f"Description of Record Schema with typeName param is invalid",
                })
                table.add_row(test.id, version, test.name, print_result(test.result, test.message),
                              style=make_row_style(version))


def test_05_GetDomain():
    print("05...")
    for version in config.csw.versions:
        parameters = [
            "DescribeRecord.outputFormat",
            "DescribeRecord.schemaLanguage",
            "DescribeRecord.typeName",
            "GetCapabilities.sections",
            "GetRecordById.ElementSetName",
            "GetRecordById.outputFormat",
            "GetRecordById.outputSchema",
            "GetRecords.CONSTRAINTLANGUAGE",
            "GetRecords.ElementSetName",
            "GetRecords.outputFormat",
            "GetRecords.outputSchema",
            "GetRecords.resultType",
            "GetRecords.typeNames",
        ]
        p = True
        e = None
        for parameter in parameters:
            r = httpx.get(
                config.csw.endpoint,
                params={
                    "service": "CSW",
                    "version": version,
                    "request": "GetDomain",
                    "ParameterName": parameter,
                }
            )
            if not f"<csw:ParameterName>{parameter}</csw:ParameterName>" in r.text:
                p = False
                e = parameter

        test = Box({
            "id": "05",
            "name": "GetDomain Return lists of names of requested parameters",
            "result": p,
            "message": f"The parameter not responding correctly is {e}",
        })
        table.add_row(test.id, version, test.name, print_result(test.result, test.message), style=make_row_style(version))

        print("05b...")
        properties = [
            "dc:subject",
            "mdb:Subject",
            "mdb:Type",
        ]
        p = True
        e = None
        for property in properties:
            r2 = httpx.get(
                config.csw.endpoint,
                params={
                    "service": "CSW",
                    "version": version,
                    "request": "GetDomain",
                    "PropertyName": property,
                }
            )
            if not f"<csw:PropertyName>{property}</csw:PropertyName>" in r2.text:
                p = False
                e = property

        test = Box({
            "id": "05 b",
            "name": "GetDomain Return list of values as per available queryables",
            "result": p,
            "message": f"The list of value not responding correctly is {e}",
        })
        table.add_row(test.id, version, test.name, print_result(test.result, test.message), style=make_row_style(version))

        # don't do the next test if any of the previous failed
        if p:
            print("05c...")
            p = True
            e = None
            r3 = httpx.get(
                config.csw.endpoint,
                params={
                    "service": "CSW",
                    "version": "2.0.2",
                    "request": "GetDomain",
                    "PropertyName": "mdb:Subject",
                }
            )
            et = etree.fromstring(r3.content)
            kws = et.xpath('//csw:Value', namespaces={"csw": "http://www.opengis.net/cat/csw/2.0.2"})
            for kw in kws:
                if "," in kw.text:
                    p = False
                    e = kw.text

            test = Box({
                "id": "05 c",
                "name": "GetDomain Ensure subject terms are not concatenated",
                "result": p,
                "message": f"The following subject term appears concatenated: {e}",
            })
            table.add_row(test.id, version, test.name, print_result(test.result, test.message),
                          style=make_row_style(version))


def test_06_GetRecords():
    print("06...")
    for version in config.csw.versions:
        r = httpx.get(
            config.csw.endpoint,
            params={
                "service": "CSW",
                "version": "2.0.2",
                "request": "GetRecords",
            }
        )

        test = Box({
            "id": "06",
            "name": "GetRecords default request",
            "result": r.is_success,
            "message": f"Status code is {r.status_code}",
        })
        table.add_row(test.id, version, test.name, print_result(test.result, test.message),
                      style=make_row_style(version))

        if r.is_success:
            # ensure 'hits' is default
            print("06b...")
            et = etree.fromstring(r.content)
            print(r.text)
            sr = et.xpath("//csw:GetRecordsResponse/csw:SearchResults", namespaces={"csw": "http://www.opengis.net/cat/csw/2.0.2"})
            p = True
            e = None
            if len(sr) < 1:
                p = False
                etext = et.xpath("//ows:ExceptionText", namespaces={"ows": "http://www.opengis.net/ows"})[0]
                e = f"Query returned an error: {etext.text}"
            elif len(sr[0].getchildren()) > 0:
                p = False
                e =  f"GetRecords returned a result but it is not 'hits' by default"

            test = Box({
                "id": "06 b",
                "name": "GetRecords default hits result",
                "result": p,
                "message": e
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
    tests = {
        1: "test_01_GetCapabilities_validity",
        2: "test_02_GetCapabilities_operations",
        3: "test_03_GetCapabilities_filter_capabilities",
        4: "test_04_DescribeRecord",
        5: "test_05_GetDomain",
        6: "test_06_GetRecords",
    }

    for test in config.tests:
        globals()[tests[test]]()
    # End Tests

    console.print(table)