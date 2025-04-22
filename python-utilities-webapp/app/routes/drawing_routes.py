from flask import Blueprint, render_template, request, jsonify
from app.utilities.drawing_utils import DrawingTool

drawing_bp = Blueprint('drawing', __name__)

@drawing_bp.route('/drawing-tool')
def drawing_tool():
    return render_template('drawing_tool.html')

@drawing_bp.route('/api/save-drawing', methods=['POST'])
def save_drawing():
    data = request.get_json()
    # Save drawing data (base64 or SVG)
    return jsonify({"status": "success"})