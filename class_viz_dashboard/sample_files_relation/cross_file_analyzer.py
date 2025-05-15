import ast
import graphviz
from pathlib import Path


def analyze_relationships(files):
    print(f"🔍 Analyzing {len(files)} files together...")

    dot = graphviz.Digraph('Cross-File Relationships',
                           engine='dot',
                           graph_attr={'rankdir': 'TB', 'compound': 'true'},
                           node_attr={'shape': 'box'})

    # Track all classes and their source files
    class_locations = {}  # {class_name: source_file}
    relationships = []

    # First pass: Collect all classes and their locations
    for file in files:
        with open(file) as f:
            code = f.read()

        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_locations[node.name] = file

    # Second pass: Find all relationships
    for file in files:
        with open(file) as f:
            code = f.read()

        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Inheritance
                for base in node.bases:
                    if isinstance(base, ast.Name) and base.id in class_locations:
                        relationships.append((node.name, base.id, 'inheritance'))

                # Composition
                for item in node.body:
                    if isinstance(item, ast.Assign):
                        if (isinstance(item.value, ast.Call) and
                                isinstance(item.value.func, ast.Name) and
                                item.value.func.id in class_locations):
                            relationships.append((node.name, item.value.func.id, 'composition'))

    # Add all classes grouped by file
    file_groups = {}
    for cls, file in class_locations.items():
        file_groups.setdefault(file, []).append(cls)

    for file, classes in file_groups.items():
        with dot.subgraph(name=f'cluster_{Path(file).stem}') as c:
            c.attr(label=Path(file).stem, style='filled', color='lightgrey')
            for cls in classes:
                c.node(cls)

    # Add relationships with cross-file awareness
    for src, dst, rel_type in relationships:
        if src in class_locations and dst in class_locations:
            src_file = class_locations[src]
            dst_file = class_locations[dst]

            if rel_type == 'inheritance':
                dot.edge(src, dst, arrowhead='empty')
            elif rel_type == 'composition':
                dot.edge(src, dst, arrowhead='diamond')

    dot.render('final_diagram', format='png', cleanup=True)
    print("✅ Generated 'final_diagram.png' with ALL relationships")


if __name__ == '__main__':
    files = ['vehicles.py', 'university.py', 'house.py', 'reporting.py']
    analyze_relationships(files)