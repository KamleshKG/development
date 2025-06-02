import ast
import os
from graphviz import Digraph

RELATIONSHIP_KEYS = [
    'aggregation',
    'composition',
    'inheritance',
    'interface_implementation',
    'strong_composition'
]

def find_py_files(root_dir):
    py_files = []
    for dirpath, _, filenames in os.walk(root_dir):
        for fname in filenames:
            if fname.endswith('.py'):
                py_files.append(os.path.join(dirpath, fname))
    return py_files

def analyze_file(filepath, relationships):
    with open(filepath, "r", encoding="utf-8") as f:
        source = f.read()
    tree = ast.parse(source, filename=filepath)

    class_defs = {node.name: node for node in tree.body if isinstance(node, ast.ClassDef)}

    # Inheritance
    for class_name, class_node in class_defs.items():
        for base in class_node.bases:
            if isinstance(base, ast.Name):
                relationships['inheritance'].append((class_name, base.id))
            elif isinstance(base, ast.Attribute):
                relationships['inheritance'].append((class_name, base.attr))

    # Composition, strong composition, aggregation, interface implementation
    for class_name, class_node in class_defs.items():
        base_names = [b.id if isinstance(b, ast.Name) else getattr(b, 'attr', None) for b in class_node.bases]
        if 'Drivable' in base_names:
            relationships['interface_implementation'].append((class_name, 'Drivable'))

        for stmt in class_node.body:
            # Detect composition/strong composition via type annotation or assignment in __init__
            if isinstance(stmt, ast.FunctionDef) and stmt.name == "__init__":
                for node in ast.walk(stmt):
                    # Handle annotated assignments (AnnAssign)
                    if isinstance(node, ast.AnnAssign):
                        if (isinstance(node.target, ast.Attribute) and
                            isinstance(node.target.value, ast.Name) and
                            node.target.value.id == "self"):
                            # List[Type]
                            if isinstance(node.annotation, ast.Subscript) and getattr(node.annotation.value, 'id', None) == "List":
                                elt_type = None
                                sub = node.annotation.slice
                                if isinstance(sub, ast.Name):
                                    elt_type = sub.id
                                elif hasattr(sub, 'id'):
                                    elt_type = sub.id
                                if elt_type:
                                    if node.target.attr.startswith("__"):
                                        print(f"Detected strong composition: {class_name} -> {elt_type} (private)")
                                        relationships['strong_composition'].append((class_name, elt_type))
                                        relationships['composition'].append((class_name, elt_type))
                                    else:
                                        print(f"Detected composition: {class_name} -> {elt_type}")
                                        relationships['composition'].append((class_name, elt_type))
                            # Direct type annotation (e.g. Engine)
                            elif isinstance(node.annotation, ast.Name):
                                elt_type = node.annotation.id
                                if elt_type:
                                    if node.target.attr.startswith("__"):
                                        print(f"Detected strong composition: {class_name} -> {elt_type} (private)")
                                        relationships['strong_composition'].append((class_name, elt_type))
                                        relationships['composition'].append((class_name, elt_type))
                                    else:
                                        print(f"Detected composition: {class_name} -> {elt_type}")
                                        relationships['composition'].append((class_name, elt_type))
                    # Handle assignments (Assign)
                    if isinstance(node, ast.Assign):
                        for target in node.targets:
                            if (isinstance(target, ast.Attribute) and
                                isinstance(target.value, ast.Name) and
                                target.value.id == "self" and
                                isinstance(node.value, ast.Call) and
                                isinstance(node.value.func, ast.Name)):
                                attr_name = target.attr
                                type_name = node.value.func.id
                                if attr_name.startswith("__"):
                                    print(f"Detected strong composition: {class_name} -> {type_name} (private)")
                                    relationships['strong_composition'].append((class_name, type_name))
                                    relationships['composition'].append((class_name, type_name))
                                else:
                                    print(f"Detected composition: {class_name} -> {type_name}")
                                    relationships['composition'].append((class_name, type_name))
            # For dataclass fields (aggregation)
            if isinstance(stmt, ast.AnnAssign):
                if (isinstance(stmt.annotation, ast.Subscript) and
                    getattr(stmt.annotation.value, 'id', None) == "List"):
                    elt_type = None
                    sub = stmt.annotation.slice
                    if isinstance(sub, ast.Name):
                        elt_type = sub.id
                    elif hasattr(sub, 'id'):
                        elt_type = sub.id
                    if elt_type:
                        relationships['aggregation'].append((class_name, elt_type))

def main():
    relationships = {k: [] for k in RELATIONSHIP_KEYS}
    py_files = find_py_files('test_samples')
    for filename in py_files:
        try:
            analyze_file(filename, relationships)
        except Exception as e:
            print(f"Error analyzing {filename}: {e}")

    # Remove duplicates and sort for consistent output
    for k in relationships:
        relationships[k] = sorted(list(set(relationships[k])))

    import pprint
    pprint.pprint(relationships)
def visualize_relationships(relationships, output_file='class_diagram'):
    dot = Digraph(comment='Class Diagram', format='png')
    dot.attr(rankdir='LR')

    # Collect all class names
    class_names = set()
    for rels in relationships.values():
        for a, b in rels:
            class_names.add(a)
            class_names.add(b)

    # Add nodes for each class
    for cls in class_names:
        dot.node(cls, cls, shape='box')

    # Add edges for each relationship type
    for a, b in relationships.get('inheritance', []):
        dot.edge(b, a, label='inherits', arrowhead='onormal', color='black')
    for a, b in relationships.get('interface_implementation', []):
        dot.edge(b, a, label='implements', style='dashed', color='blue')
    for a, b in relationships.get('composition', []):
        dot.edge(a, b, label='composes', arrowhead='diamond', color='green')
    for a, b in relationships.get('aggregation', []):
        dot.edge(a, b, label='aggregates', arrowhead='odiamond', color='orange')
    for a, b in relationships.get('strong_composition', []):
        dot.edge(a, b, label='strong comp.', arrowhead='diamond', color='red', penwidth='2')

    # Render to file
    dot.render(output_file, view=True)
    print(f"Diagram saved to {output_file}.png")

if __name__ == "__main__":
    main()