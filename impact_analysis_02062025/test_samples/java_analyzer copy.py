import os
import re
from graphviz import Digraph

RELATIONSHIP_KEYS = [
    'aggregation',
    'composition',
    'strong_composition',  # Not typical in Java, but included for symmetry
    'association',
    'inheritance',
    'interface_implementation'
]

def find_java_files(root_dir):
    java_files = []
    for dirpath, _, filenames in os.walk(root_dir):
        for fname in filenames:
            if fname.endswith('.java'):
                java_files.append(os.path.join(dirpath, fname))
    return java_files

def analyze_java_file(filepath, relationships, class_names):
    with open(filepath, "r", encoding="utf-8") as f:
        source = f.read()

    # Remove comments
    source = re.sub(r'//.*?$|/\*.*?\*/', '', source, flags=re.DOTALL | re.MULTILINE)

    # Find all class/interface definitions
    class_pattern = re.compile(
        r'(class|interface)\s+(\w+)(?:\s+extends\s+(\w+))?(?:\s+implements\s+([\w,\s]+))?', re.MULTILINE)
    classes = class_pattern.findall(source)

    for kind, class_name, parent, interfaces in classes:
        class_names.add(class_name)
        if parent:
            relationships['inheritance'].append((class_name, parent))
        if interfaces:
            for iface in [i.strip() for i in interfaces.split(',') if i.strip()]:
                relationships['interface_implementation'].append((class_name, iface))

def analyze_java_fields_and_associations(filepath, relationships, class_names):
    with open(filepath, "r", encoding="utf-8") as f:
        source = f.read()

    # Remove comments
    source = re.sub(r'//.*?$|/\*.*?\*/', '', source, flags=re.DOTALL | re.MULTILINE)

    # Improved regex for class body (handles { on new line and nested braces)
    class_body_pattern = re.compile(
        r'(class|interface)\s+(\w+)[^{]*\{((?:[^{}]|\{[^{}]*\})*)}', re.DOTALL)
    for match in class_body_pattern.finditer(source):
        kind, class_name, body = match.groups()

        # Fields (composition/aggregation)
        field_pattern = re.compile(r'(private|protected|public)?\s*(\w+)\s+(\w+)\s*(=|;)', re.MULTILINE)
        for _, field_type, var_name, _ in field_pattern.findall(body):
            if field_type in class_names:
                if re.search(r'List<\s*' + field_type + r'\s*>', body) or var_name.endswith('s'):
                    relationships['aggregation'].append((class_name, field_type, var_name))
                else:
                    relationships['composition'].append((class_name, field_type, var_name))

        # Method parameters (association)
        method_pattern = re.compile(r'(?:public|protected|private)?\s*\w+\s+\w+\s*\(([^)]*)\)', re.MULTILINE)
        for params in method_pattern.findall(body):
            for param in params.split(','):
                param = param.strip()
                if not param:
                    continue
                parts = param.split()
                if len(parts) == 2:
                    param_type, param_name = parts
                    if param_type in class_names:
                        relationships['association'].append((class_name, param_type, param_name))

        # Local variables in methods (association)
        local_var_pattern = re.compile(r'(\w+)\s+(\w+)\s*=\s*new\s+(\w+)\s*\(', re.MULTILINE)
        for var_type, var_name, new_type in local_var_pattern.findall(body):
            if new_type in class_names:
                relationships['association'].append((class_name, new_type, var_name))

def analyze_spring_annotations(filepath, spring_info):
    with open(filepath, "r", encoding="utf-8") as f:
        source = f.read()

    # Remove comments
    source = re.sub(r'//.*?$|/\*.*?\*/', '', source, flags=re.DOTALL | re.MULTILINE)

    # Find class-level annotations
    class_anno_pattern = re.compile(r'@(\w+)\s*\n\s*(public\s+)?(class|interface)\s+(\w+)', re.MULTILINE)
    for anno, _, _, class_name in class_anno_pattern.findall(source):
        if anno in ['Component', 'Service', 'Repository', 'Controller', 'RestController']:
            spring_info.setdefault('class_annotations', []).append((class_name, anno))

    # Find field-level @Autowired
    field_anno_pattern = re.compile(r'@Autowired\s*\n\s*(private|protected|public)?\s*(\w+)\s+(\w+)\s*[;=]', re.MULTILINE)
    for _, field_type, var_name in field_anno_pattern.findall(source):
        spring_info.setdefault('autowired_fields', []).append((var_name, field_type, filepath))

    # Find constructor-level @Autowired
    ctor_anno_pattern = re.compile(r'@Autowired\s*\n\s*(public|protected|private)?\s+(\w+)\s*\(([^)]*)\)', re.MULTILINE)
    for _, class_name, params in ctor_anno_pattern.findall(source):
        spring_info.setdefault('autowired_ctors', []).append((class_name, params, filepath))

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
    class_names = set()
    spring_info = {}
    java_files = find_java_files('test_samples')
    # First pass: collect all class names and inheritance/interfaces
    for filename in java_files:
        try:
            analyze_java_file(filename, relationships, class_names)
        except Exception as e:
            print(f"Error analyzing {filename}: {e}")
    # Second pass: collect fields and associations
    for filename in java_files:
        try:
            analyze_java_fields_and_associations(filename, relationships, class_names)
        except Exception as e:
            print(f"Error analyzing {filename}: {e}")
    # Third pass: collect Spring annotations
    for filename in java_files:
        try:
            analyze_spring_annotations(filename, spring_info)
        except Exception as e:
            print(f"Error analyzing {filename}: {e}")

    # Remove duplicates and sort for consistent output
    for k in relationships:
        relationships[k] = sorted(list(set(relationships[k])))

    import pprint
    pprint.pprint(relationships)

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

    print("\n--- Spring Annotations ---")
    for class_name, anno in spring_info.get('class_annotations', []):
        print(f"Class '{class_name}' is annotated with @{anno}")
    for var_name, field_type, file in spring_info.get('autowired_fields', []):
        print(f"Field '{var_name}' of type '{field_type}' is @Autowired in {file}")
    for class_name, params, file in spring_info.get('autowired_ctors', []):
        print(f"Constructor of '{class_name}' is @Autowired with params ({params}) in {file}")

    visualize_relationships(relationships)

if __name__ == "__main__":
    main()