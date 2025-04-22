# import json
# import xmltodict
#
#
# def json_to_xml(json_str):
#     """Convert JSON string to XML"""
#     try:
#         data = json.loads(json_str)
#         return {"success": True, "xml": xmltodict.unparse(data, pretty=True)}
#     except Exception as e:
#         return {"success": False, "error": str(e)}
#
#
# def xml_to_json(xml_str):
#     """Convert XML string to JSON"""
#     try:
#         data = xmltodict.parse(xml_str)
#         return {"success": True, "json": json.dumps(data, indent=2)}
#     except Exception as e:
#         return {"success": False, "error": str(e)}
#
#
# # Test Example:
# if __name__ == "__main__":
#     sample_json = '{"person": {"name": "Alice", "age": 25}}'
#     print("JSON to XML:", json_to_xml(sample_json)["xml"])
#
#     sample_xml = '''
#     <person>
#         <name>Alice</name>
#         <age>25</age>
#     </person>
#     '''
#     print("XML to JSON:", xml_to_json(sample_xml)["json"])

import json
import xmltodict

def json_to_xml(json_str):
    try:
        data = json.loads(json_str)
        return {"success": True, "xml": xmltodict.unparse(data, pretty=True)}
    except Exception as e:
        return {"success": False, "error": str(e)}

def xml_to_json(xml_str):
    try:
        data = xmltodict.parse(xml_str)
        return {"success": True, "json": json.dumps(data, indent=2)}
    except Exception as e:
        return {"success": False, "error": str(e)}