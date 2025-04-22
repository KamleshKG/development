from flask import Blueprint, request, render_template
from app.utilities.yaml_utils import validate_yaml, format_yaml

bp = Blueprint('yaml', __name__)


@bp.route('/yaml', methods=['GET', 'POST'])
def yaml_tool():
    if request.method == 'POST':
        action = request.form.get('action')
        content = request.form.get('content')

        if action == 'validate':
            result = validate_yaml(content)
            return render_template('yaml_utility.html',
                                   result=result,
                                   content=content)
        elif action == 'format':
            result = format_yaml(content)
            return render_template('yaml_utility.html',
                                   result=result,
                                   content=result.get('formatted', content))

    return render_template('yaml_utility.html')