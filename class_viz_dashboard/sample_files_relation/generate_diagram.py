import ast
import graphviz
from pathlib import Path


def generate_class_diagram(files):
    dot = graphviz.Digraph(comment='Class Diagram', format='png',
                           graph_attr={'rankdir': 'TB'})

    # Process each file
    for file in files:
        with open(file) as f:
            tree = ast.parse(f.read())

        # Add classes and relationships
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Add class node
                dot.node(node.name, shape='record',
                         label=f"{node.name}|<methods>methods")

                # Handle inheritance
                for base in node.bases:
                    if isinstance(base, ast.Name):
                        dot.edge(node.name, base.id, arrowhead='empty')

                # Handle composition/attributes
                for item in node.body:
                    if isinstance(item, ast.Assign):
                        if isinstance(item.value, ast.Call) and isinstance(item.value.func, ast.Name):
                            dot.edge(node.name, item.value.func.id, arrowhead='diamond')

    # Save and render
    output_file = 'class_diagram'
    dot.render(output_file, view=True)
    print(f"Diagram saved as {output_file}.png")


if __name__ == "__main__":
    files = ['vehicles.py', 'university.py', 'house.py', 'reporting.py']
    generate_class_diagram(files)