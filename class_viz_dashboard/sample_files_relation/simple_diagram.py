import ast
import graphviz


def analyze_relationships(files):
    print("🔍 Analyzing files:", ", ".join(files))

    dot = graphviz.Digraph('Class Diagram')
    dot.attr(rankdir='TB')

    classes = set()
    relationships = []

    for file in files:
        with open(file) as f:
            code = f.read()

        tree = ast.parse(code)

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                classes.add(node.name)

                # Inheritance
                for base in node.bases:
                    if isinstance(base, ast.Name):
                        relationships.append((node.name, base.id, 'inheritance'))

                # Composition (simple detection)
                for item in node.body:
                    if isinstance(item, ast.Assign):
                        for target in item.targets:
                            if (isinstance(target, ast.Attribute) and
                                    isinstance(item.value, ast.Call)):
                                relationships.append((node.name, item.value.func.id, 'composition'))

    # Add all classes
    for cls in sorted(classes):
        dot.node(cls)

    # Add relationships
    for src, dst, rel_type in relationships:
        if src in classes and dst in classes:
            if rel_type == 'inheritance':
                dot.edge(src, dst, arrowhead='empty')
            elif rel_type == 'composition':
                dot.edge(src, dst, arrowhead='diamond')

    dot.render('class_diagram', format='png', cleanup=True)
    print("✅ Diagram generated as 'class_diagram.png'")


if __name__ == '__main__':
    files = ['vehicles.py', 'university.py', 'house.py', 'reporting.py']
    analyze_relationships(files)