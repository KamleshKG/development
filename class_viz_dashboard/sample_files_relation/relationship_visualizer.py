import ast
import graphviz
from pathlib import Path


def get_relationships(files):
    # Track all classes and their locations
    class_locations = {}
    relationships = []

    # First pass: Find all classes
    for file in files:
        with open(file) as f:
            tree = ast.parse(f.read())
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_locations[node.name] = file

    # Second pass: Find all relationships
    for file in files:
        with open(file) as f:
            tree = ast.parse(f.read())

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                current_class = node.name

                # Inheritance
                for base in node.bases:
                    if isinstance(base, ast.Name) and base.id in class_locations:
                        relationships.append((current_class, base.id, 'inheritance'))

                # Composition and attributes
                for item in node.body:
                    # Direct composition (self.engine = Engine())
                    if (isinstance(item, ast.Assign) and
                            isinstance(item.value, ast.Call) and
                            isinstance(item.value.func, ast.Name) and
                            item.value.func.id in class_locations):
                        relationships.append((current_class, item.value.func.id, 'composition'))

                    # List composition (self.rooms.append(Room()))
                    if (isinstance(item, ast.FunctionDef) and
                            any(isinstance(n, ast.Attribute) and n.attr == 'append'
                                for n in ast.walk(item))):
                        relationships.append((current_class, 'Room', 'composition'))

    return class_locations, relationships


def generate_diagram(files):
    class_locations, relationships = get_relationships(files)

    dot = graphviz.Digraph('Class Relationships',
                           engine='dot',
                           graph_attr={'rankdir': 'TB', 'compound': 'true'},
                           node_attr={'shape': 'box', 'fontname': 'Arial'})

    # Group classes by file
    file_groups = {}
    for cls, file in class_locations.items():
        file_groups.setdefault(file, []).append(cls)

    # Add grouped classes
    for file, classes in file_groups.items():
        with dot.subgraph(name=f'cluster_{Path(file).stem}') as c:
            c.attr(label=Path(file).stem, style='filled', color='lightgray')
            for cls in classes:
                c.node(cls)

    # Add all relationships
    for src, dst, rel_type in relationships:
        if src in class_locations and dst in class_locations:
            if rel_type == 'inheritance':
                dot.edge(src, dst, arrowhead='empty', color='blue')
            elif rel_type == 'composition':
                dot.edge(src, dst, arrowhead='diamond', color='red')

    dot.render('class_relationships', format='png', cleanup=True)
    print("✅ Generated 'class_relationships.png'")


if __name__ == '__main__':
    files = ['vehicles.py', 'university.py', 'house.py', 'reporting.py']
    generate_diagram(files)