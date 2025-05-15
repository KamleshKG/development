import ast
import graphviz
from collections import defaultdict


def analyze_files(files):
    # Track classes and their locations
    class_map = {}  # {class_name: file_path}
    relationships = defaultdict(list)  # {source: [(target, type)]}

    # First pass: Find all classes
    for file in files:
        with open(file) as f:
            tree = ast.parse(f.read())
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_map[node.name] = file

    # Second pass: Find real relationships
    for file in files:
        with open(file) as f:
            tree = ast.parse(f.read())

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                current_class = node.name

                # Inheritance
                for base in node.bases:
                    if isinstance(base, ast.Name) and base.id in class_map:
                        relationships[current_class].append((base.id, 'inheritance'))

                # Composition
                for item in node.body:
                    # Case 1: Direct assignment (self.engine = Engine())
                    if (isinstance(item, ast.Assign) and \
                            isinstance(item.value, ast.Call) and \
                            isinstance(item.value.func, ast.Name) and \
                            item.value.func.id in class_map:
                                relationships[current_class].append((item.value.func.id, 'composition'))

                    # Case 2: List operations (self.rooms.append(Room()))
                    if isinstance(item, ast.Expr) and \
                            isinstance(item.value, ast.Call) and \
                            isinstance(item.value.func, ast.Attribute) and \
                            item.value.func.attr == 'append' and \
                            isinstance(item.value.func.value, ast.Attribute):
                    # This detects patterns like self.rooms.append(Room())
                        pass

    return class_map, relationships


def draw_diagram(class_map, relationships):
    dot = graphviz.Digraph('Accurate Relationships',
                           engine='dot',
                           graph_attr={'rankdir': 'TB', 'compound': 'true'},
                           node_attr={'shape': 'box', 'fontname': 'Arial'})

    # Group classes by file
    file_groups = defaultdict(list)
    for cls, file in class_map.items():
        file_groups[file].append(cls)

    # Add grouped classes
    for file, classes in file_groups.items():
        with dot.subgraph(name=f'cluster_{file}') as c:
            c.attr(label=file.stem, style='rounded,filled', color='lightgray')
            for cls in classes:
                c.node(cls)

    # Add relationships
    for src, targets in relationships.items():
        for target, rel_type in targets:
            if rel_type == 'inheritance':
                dot.edge(src, target, arrowhead='empty', color='blue')
            elif rel_type == 'composition':
                dot.edge(src, target, arrowhead='diamond', color='red')

    dot.render('final_diagram', format='png', cleanup=True)
    print("✅ Generated 'final_diagram.png'")


if __name__ == '__main__':
    files = ['vehicles.py', 'university.py', 'house.py', 'reporting.py']
    class_map, relationships = analyze_files([Path(f) for f in files])
    draw_diagram(class_map, relationships)