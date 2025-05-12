import os
import ast
from javalang import parse
from javalang.tree import ClassDeclaration, InterfaceDeclaration


def analyze_codebase(root_folder):
    print(f"\n📂 Starting analysis of: {root_folder}")
    structure = {
        'classes': [],
        'relationships': [],
        'errors': [],
        '_debug': {'files_processed': 0}
    }

    try:
        for root, dirs, files in os.walk(root_folder):
            print(f"\n📁 Entering directory: {root}")
            print(f"📝 Files found: {files}")

            for file in files:
                filepath = os.path.join(root, file)
                structure['_debug']['files_processed'] += 1

                try:
                    print(f"\n🔧 Processing: {filepath}")
                    if file.endswith('.py'):
                        parse_python_file(filepath, structure)
                    elif file.endswith('.java'):
                        parse_java_file(filepath, structure)
                    print(f"✅ Processed successfully")
                except Exception as e:
                    error_msg = f"⚠️ Error in {filepath}: {str(e)}"
                    print(error_msg)
                    structure['errors'].append(error_msg)

    except Exception as e:
        error_msg = f"🚨 Directory walk failed: {str(e)}"
        print(error_msg)
        structure['errors'].append(error_msg)

    print(f"\n📊 Analysis complete. Processed {structure['_debug']['files_processed']} files")
    return structure

def parse_python_file(filepath, structure):
    with open(filepath, 'r', encoding='utf-8') as f:
        tree = ast.parse(f.read())

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            class_info = {
                'name': node.name,
                'language': 'python',
                'file': filepath,
                'methods': [n.name for n in node.body if isinstance(n, ast.FunctionDef)],
                'bases': [base.id for base in node.bases if isinstance(base, ast.Name)],
                'type': 'class'
            }
            structure['classes'].append(class_info)

            # Record inheritance relationships
            for base in class_info['bases']:
                structure['relationships'].append({
                    'source': base,
                    'target': node.name,
                    'type': 'inheritance'
                })


def parse_java_file(filepath, structure):
    with open(filepath, 'r', encoding='utf-8') as f:
        tree = parse.parse(f.read())

    for path, node in tree:
        if isinstance(node, (ClassDeclaration, InterfaceDeclaration)):
            class_info = {
                'name': node.name,
                'language': 'java',
                'file': filepath,
                'methods': [m.name for m in node.methods] if hasattr(node, 'methods') else [],
                'type': 'interface' if isinstance(node, InterfaceDeclaration) else 'class'
            }

            if isinstance(node, ClassDeclaration):
                if node.extends:
                    class_info['extends'] = node.extends.name
                    structure['relationships'].append({
                        'source': node.extends.name,
                        'target': node.name,
                        'type': 'extends'
                    })

                if node.implements:
                    class_info['implements'] = [imp.name for imp in node.implements]
                    for interface in node.implements:
                        structure['relationships'].append({
                            'source': interface.name,
                            'target': node.name,
                            'type': 'implements'
                        })

            structure['classes'].append(class_info)