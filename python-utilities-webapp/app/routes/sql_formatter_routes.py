from flask import Blueprint, request, render_template
from app.utilities.sql_formatter import format_sql

bp = Blueprint('sql_formatter', __name__, url_prefix='/sql-formatter')

@bp.route('/', methods=['GET', 'POST'])
def sql_format():
    result = None
    if request.method == 'POST':
        sql = request.form.get('sql', '')
        indent = int(request.form.get('indent', 2))
        case = request.form.get('case', 'upper')
        result = format_sql(sql, indent, case)
    return render_template('sql_formatter.html', result=result)