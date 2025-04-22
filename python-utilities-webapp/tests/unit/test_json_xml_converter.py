import pytest
from app.utilities.json_xml_converter import json_to_xml, xml_to_json

def test_json_to_xml():
    test_json = '{"name": "John", "age": 30}'
    result = json_to_xml(test_json)
    assert result['success']
    assert '<name>John</name>' in result['xml']
    assert '<age>30</age>' in result['xml']

def test_xml_to_json():
    test_xml = '''
    <person>
        <name>John</name>
        <age>30</age>
    </person>
    '''
    result = xml_to_json(test_xml)
    assert result['success']
    assert '"name": "John"' in result['json']
    assert '"age": "30"' in result['json']