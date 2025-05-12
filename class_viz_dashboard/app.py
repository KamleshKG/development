from flask import Flask, render_template, request, jsonify
import os
from utils.core_parser import analyze_codebase
from utils.visualization import generate_visualization_data

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/visualization-data')
def visualization_data():
    test_path = "E:\\PYTHON_PROJECTS\\python_checklist"
    class_structure = analyze_codebase(test_path)
    viz_data = generate_visualization_data(class_structure)

    # Debug output
    print("\n🔥 RAW VISUALIZATION DATA:")
    print(f"Nodes: {len(viz_data['nodes'])}")
    print(f"Edges: {len(viz_data['links'])}")
    print("Sample node:", viz_data['nodes'][0] if viz_data['nodes'] else "None")
    print("Sample edge:", viz_data['links'][0] if viz_data['links'] else "None")

    return jsonify(viz_data)


@app.route('/analyze', methods=['POST'])
def analyze_code():
    try:
        folder_path = request.json.get('folder_path', '').strip()
        if not folder_path:
            return jsonify({'error': 'Empty folder path'}), 400

        folder_path = os.path.normpath(folder_path)

        if not os.path.exists(folder_path):
            return jsonify({'error': 'Path does not exist'}), 400

        class_structure = analyze_codebase(folder_path)
        viz_data = generate_visualization_data(class_structure)

        # Debug output
        print(f"\n🔥 Visualization Data:")
        print(f"Nodes: {len(viz_data['nodes'])}")
        print(f"Edges: {len(viz_data['links'])}")
        print(f"Sample Node: {viz_data['nodes'][0] if viz_data['nodes'] else 'None'}")

        return jsonify(viz_data)

    except Exception as e:
        print(f"Error in analysis: {str(e)}")
        return jsonify({'error': str(e)}), 500
@app.route('/test-data')
def test_data():
    """Return sample data matching your debug output structure"""
    return jsonify({
        "nodes": [
            {
                "id": "DoSomething::demo.py",
                "label": "DoSomething",
                "title": "<b>DoSomething</b><br>Type: class<br>Language: python",
                "file": "demo.py",
                "type": "class",
                "language": "python"
            },
            {
                "id": "WorkflowBase::external",
                "label": "WorkflowBase",
                "title": "<b>WorkflowBase</b><br>Type: class<br>Language: unknown",
                "file": "external",
                "type": "class"
            }
        ],
        "links": [
            {
                "from": "WorkflowBase::external",
                "to": "DoSomething::demo.py",
                "type": "inheritance"
            }
        ]
    })
@app.route('/debug-data', methods=['GET'])
def debug_data():
    # Use the same path you're testing in the frontend
    test_path = "E:\\PYTHON_PROJECTS\\python_checklist"

    try:
        print(f"\n🔍 Debugging path: {test_path}")

        if not os.path.exists(test_path):
            return jsonify({"error": "Path does not exist", "path": test_path}), 404

        structure = analyze_codebase(test_path)

        # Add diagnostic info
        structure['_diagnostics'] = {
            "path_exists": os.path.exists(test_path),
            "is_directory": os.path.isdir(test_path),
            "files_found": sum(len(files) for _, _, files in os.walk(test_path))
        }

        return jsonify(structure)

    except Exception as e:
        print(f"🔥 Debug error: {str(e)}")
        return jsonify({
            "error": str(e),
            "type": type(e).__name__,
            "traceback": traceback.format_exc()
        }), 500

if __name__ == '__main__':
    app.run(debug=True)
