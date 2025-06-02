import ast
import os
from graphviz import Digraph

RELATIONSHIP_KEYS = [
    'aggregation',
    'composition',
    'strong_composition',
    'association',
    'inheritance',
    'interface_implementation'
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
    class_names = set(class_defs.keys())

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
                            var_name = node.target.attr
                            # List[Type]
                            if isinstance(node.annotation, ast.Subscript) and getattr(node.annotation.value, 'id', None) == "List":
                                elt_type = None
                                sub = node.annotation.slice
                                if isinstance(sub, ast.Name):
                                    elt_type = sub.id
                                elif hasattr(sub, 'id'):
                                    elt_type = sub.id
                                if elt_type and elt_type in class_names:
                                    if var_name.startswith("__"):
                                        print(f"Detected strong composition: {class_name} -> {elt_type} (private, var: {var_name})")
                                        relationships['strong_composition'].append((class_name, elt_type, var_name))
                                        relationships['composition'].append((class_name, elt_type, var_name))
                                    else:
                                        print(f"Detected composition: {class_name} -> {elt_type} (var: {var_name})")
                                        relationships['composition'].append((class_name, elt_type, var_name))
                            # Direct type annotation (e.g. Engine)
                            elif isinstance(node.annotation, ast.Name):
                                elt_type = node.annotation.id
                                if elt_type and elt_type in class_names:
                                    if var_name.startswith("__"):
                                        print(f"Detected strong composition: {class_name} -> {elt_type} (private, var: {var_name})")
                                        relationships['strong_composition'].append((class_name, elt_type, var_name))
                                        relationships['composition'].append((class_name, elt_type, var_name))
                                    else:
                                        print(f"Detected composition: {class_name} -> {elt_type} (var: {var_name})")
                                        relationships['composition'].append((class_name, elt_type, var_name))
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
                                if type_name in class_names:
                                    if attr_name.startswith("__"):
                                        print(f"Detected strong composition: {class_name} -> {type_name} (private, var: {attr_name})")
                                        relationships['strong_composition'].append((class_name, type_name, attr_name))
                                        relationships['composition'].append((class_name, type_name, attr_name))
                                    else:
                                        print(f"Detected composition: {class_name} -> {type_name} (var: {attr_name})")
                                        relationships['composition'].append((class_name, type_name, attr_name))
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
                    var_name = stmt.target.id if isinstance(stmt.target, ast.Name) else None
                    if elt_type and var_name and elt_type in class_names:
                        relationships['aggregation'].append((class_name, elt_type, var_name))

    # Association: method parameters or local variables using other classes
    for class_name, class_node in class_defs.items():
        for stmt in class_node.body:
            if isinstance(stmt, ast.FunctionDef):
                # Parameters
                for arg in stmt.args.args:
                    if arg.annotation and isinstance(arg.annotation, ast.Name):
                        param_type = arg.annotation.id
                        if param_type in class_names and param_type != class_name:
                            relationships['association'].append((class_name, param_type, arg.arg))
                # Local variables
                for node in ast.walk(stmt):
                    if isinstance(node, ast.Assign):
                        if isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Name):
                            type_name = node.value.func.id
                            if type_name in class_names and type_name != class_name:
                                # Get variable name
                                var_name = node.targets[0].id if isinstance(node.targets[0], ast.Name) else None
                                if var_name:
                                    relationships['association'].append((class_name, type_name, var_name))

def visualize_relationships(relationships, output_file='class_diagram'):
    dot = Digraph(comment='Class Diagram', format='png')
    dot.attr(rankdir='LR')

    # Collect all class names
    class_names = set()
    for rels in relationships.values():
        for rel in rels:
            class_names.add(rel[0])
            class_names.add(rel[1])

    # Add nodes for each class
    for cls in class_names:
        dot.node(cls, cls, shape='box')

    # Add edges for each relationship type, showing variable name if present
    for a, b, var in relationships.get('composition', []):
        dot.edge(a, b, label=f"{var} (composes)", arrowhead='diamond', color='green')
    for a, b, var in relationships.get('strong_composition', []):
        dot.edge(a, b, label=f"{var} (strong comp.)", arrowhead='diamond', color='red', penwidth='2')
    for a, b, var in relationships.get('aggregation', []):
        dot.edge(a, b, label=f"{var} (aggregates)", arrowhead='odiamond', color='orange')
    for a, b, var in relationships.get('association', []):
        dot.edge(a, b, label=f"{var} (associates)", style='dotted', color='purple')
    for a, b in relationships.get('inheritance', []):
        dot.edge(b, a, label='inherits', arrowhead='onormal', color='black')
    for a, b in relationships.get('interface_implementation', []):
        dot.edge(b, a, label='implements', style='dashed', color='blue')

    dot.render(output_file, view=True)
    print(f"Diagram saved to {output_file}.png")

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

    # Print relationships with variable names
    print("\n--- Relationships with variable names ---")
    for rel in relationships['composition']:
        print(f"{rel[0]} composes {rel[1]} via variable '{rel[2]}'")
    for rel in relationships['strong_composition']:
        print(f"{rel[0]} strong composes {rel[1]} via variable '{rel[2]}'")
    for rel in relationships['aggregation']:
        print(f"{rel[0]} aggregates {rel[1]} via variable '{rel[2]}'")
    for rel in relationships['association']:
        print(f"{rel[0]} associates {rel[1]} via variable '{rel[2]}'")
    for rel in relationships['inheritance']:
        print(f"{rel[0]} inherits {rel[1]}")
    for rel in relationships['interface_implementation']:
        print(f"{rel[0]} implements {rel[1]}")

    visualize_relationships(relationships)

if __name__ == "__main__":
    main()