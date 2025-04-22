from flask import Blueprint, request, render_template
from app.utilities.json_xml_converter import json_to_xml, xml_to_json

bp = Blueprint('json_xml', __name__, url_prefix='/json-xml')


@bp.route('/', methods=['GET', 'POST'])
def converter():
    result = None
    if request.method == 'POST':
        content = request.form.get('content')
        direction = request.form.get('direction')

        if direction == 'json-to-xml':
            result = json_to_xml(content)
        elif direction == 'xml-to-json':
            result = xml_to_json(content)

    return render_template('json_xml_converter.html', result=result)