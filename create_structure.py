import os
from pathlib import Path

def create_structure(base_dir="python-utilities-webapp"):
    """Generates the complete folder structure for the utilities web app."""
    structure = {
        "app": {
            "__init__.py": "",
            "main.py": "# Flask/FastAPI app entry point",
            "config.py": "# App configuration",
            "static": {
                "css": {"styles.css": "/* Main CSS */"},
                "js": {"scripts.js": "// Client-side JS"},
                "images": {}
            },
            "templates": {
                "base.html": "<!DOCTYPE html>\n<html>...</html>",
                "index.html": "{% extends 'base.html' %}",
                "yaml_utility.html": "",
                "pretty_files.html": "",
                "confluence_template.html": "",
                "regex_tester.html": "",
                "json_xml_converter.html": "",
                "drawing_tool.html": "<!-- Canvas for drawing -->"
            },
            "utilities": {
                "__init__.py": "",
                "yaml_utils.py": "# YAML validation/formatting",
                "file_formatter.py": "# File prettifying",
                "confluence_templates.py": "# Confluence templates",
                "regex_tester.py": "# Regex testing",
                "drawing_utils.py": "# Drawing tool backend",
                "json_xml_converter.py": "",
                "sql_formatter.py": ""
            },
            "routes": {
                "__init__.py": "",
                "main_routes.py": "# Homepage routes",
                "yaml_routes.py": "",
                "drawing_routes.py": "# Handles drawing tool endpoints"
            }
        },
        "tests": {
            "unit": {
                "test_yaml_utils.py": "",
                "test_drawing_utils.py": ""
            },
            "integration": {}
        },
        "requirements.txt": "flask\npyyaml",
        "README.md": "# Python Utilities Web App",
        ".gitignore": "__pycache__/\n*.pyc",
        "Dockerfile": "FROM python:3.9\n..."
    }

    def build_path(path, contents):
        if isinstance(contents, dict):
            os.makedirs(path, exist_ok=True)
            for name, content in contents.items():
                build_path(os.path.join(path, name), content)
        else:
            with open(path, "w") as f:
                f.write(contents)

    build_path(base_dir, structure)
    print(f"✅ Folder structure created at: {Path(base_dir).resolve()}")

if __name__ == "__main__":
    create_structure()