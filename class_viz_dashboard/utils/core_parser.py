import os
import ast
from typing import Dict, List, Any, Tuple
from javalang import parse
from javalang.tree import ClassDeclaration, InterfaceDeclaration
from abc import ABC, abstractmethod


def _get_imported_names(tree: ast.AST) -> Dict[str, str]:
    """Extract imported class names and their origins"""
    imports = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports[alias.name.split('.')[-1]] = alias.name
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                imports[alias.name] = f"{node.module}.{alias.name}"
    return imports


def analyze_codebase(root_folder: str) -> Dict[str, Any]:
    """Analyzes a codebase and extracts class relationships"""
    structure = {
        'classes': [],
        'relationships': [],
        'errors': [],
        '_meta': {
            'files_processed': 0,
            'languages': set()
        }
    }

    try:
        for root, dirs, files in os.walk(root_folder):
            # Skip hidden and virtual env directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ('venv', '__pycache__')]

            for file in files:
                filepath = os.path.join(root, file)
                structure['_meta']['files_processed'] += 1

                try:
                    if file.endswith('.py'):
                        parse_python_file(filepath, structure)
                        structure['_meta']['languages'].add('python')
                    elif file.endswith('.java'):
                        parse_java_file(filepath, structure)
                except Exception as e:
                    error_msg = f"Error processing {filepath}: {str(e)}"
                    structure['errors'].append(error_msg)

    except Exception as e:
        structure['errors'].append(f"Directory traversal failed: {str(e)}")

    return structure


def parse_python_file(filepath: str, structure: Dict[str, Any]) -> None:
    """Parse Python files and extract OOP relationships"""
    with open(filepath, 'r', encoding='utf-8') as f:
        tree = ast.parse(f.read())

    imported_names = _get_imported_names(tree)
    classes = {node.name: node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)}

    for class_name, class_node in classes.items():
        class_info = {
            'name': class_name,
            'language': 'python',
            'file': filepath,
            'methods': [node.name for node in class_node.body if isinstance(node, ast.FunctionDef)],
            'attributes': [
                node.target.attr
                for node in class_node.body
                if isinstance(node, ast.Assign)
                   and len(node.targets) == 1
                   and isinstance(node.targets[0], ast.Attribute)
                   and isinstance(node.targets[0].value, ast.Name)
                   and node.targets[0].value.id == 'self'
            ],
            'type': 'class',
            'docstring': ast.get_docstring(class_node) or ''
        }

        # Check for abstract base class
        bases = [base.id for base in class_node.bases]

        if any(isinstance(b, ast.Name) and b.id == 'ABC' for b in class_node.bases):
            class_info['type'] = 'interface'

        structure['classes'].append(class_info)

        # Add inheritance/implementation relationships
        for base in class_node.bases:
            if isinstance(base, ast.Name):
                if base.id in imported_names and imported_names[base.id] == 'abc.ABC':
                    continue

                base_type = 'inheritance'
                target_class = classes.get(base.id)  # Use .get() to avoid KeyError
                if target_class and target_class.type == 'interface':  # check if target_class exists and then check its type
                    base_type = 'implements'

                structure['relationships'].append({
                    'source': base.id,
                    'target': class_name,
                    'type': base_type,
                    'file': filepath
                })

        # Process class body for relationships
        for node in class_node.body:
            if isinstance(node, ast.FunctionDef):
                # Detect dependencies in method parameters
                for arg in node.args.args:
                    if arg.annotation and isinstance(arg.annotation, ast.Name):
                        structure['relationships'].append({
                            'source': class_name,
                            'target': arg.annotation.id,
                            'type': 'dependency',
                            'context': f'Parameter in {node.name}()',
                            'file': filepath
                        })

                # Detect method calls to other classes
                for call in [n for n in ast.walk(node) if isinstance(n, ast.Call)]:
                    if isinstance(call.func, ast.Attribute):
                        var_name = call.func.value.id if isinstance(call.func.value, ast.Name) else None
                        if var_name and var_name != 'self':
                            # Check if the variable is in the imported names.
                            if var_name in imported_names:
                                target_class_name = imported_names[var_name].split('.')[-1]  # Get the class name
                                structure['relationships'].append({
                                    'source': class_name,
                                    'target': target_class_name,
                                    'type': 'association',
                                    'context': f'Method call in {node.name}()',
                                    'file': filepath
                                })
                            elif var_name in classes:
                                structure['relationships'].append({
                                    'source': class_name,
                                    'target': var_name,
                                    'type': 'association',
                                    'context': f'Method call in {node.name}()',
                                    'file': filepath
                                })



            elif isinstance(node, ast.Assign):
                # Detect composition/aggregation
                for target in node.targets:
                    if (isinstance(target, ast.Attribute) and
                            isinstance(target.value, ast.Name) and
                            target.value.id == 'self'):

                        attr_name = target.attr
                        if isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Name):
                            target_class = node.value.func.id
                            structure['relationships'].append({
                                'source': class_name,
                                'target': target_class,
                                'type': 'composition',
                                'context': f'Attribute: {attr_name}',
                                'file': filepath
                            })
                        elif isinstance(node.value, ast.Name):
                            target_class = node.value.id
                            structure['relationships'].append({
                                'source': class_name,
                                'target': target_class,
                                'type': 'aggregation',
                                'context': f'Attribute: {attr_name}',
                                'file': filepath
                            })
    return structure


def parse_java_file(filepath: str, structure: Dict[str, Any]) -> None:
    """Parse Java files and extract OOP relationships"""
    with open(filepath, 'r', encoding='utf-8') as f:
        tree = parse.parse(f.read())

    for path, node in tree:
        if isinstance(node, (ClassDeclaration, InterfaceDeclaration)):
            class_info = {
                'name': node.name,
                'language': 'java',
                'file': filepath,
                'methods': [m.name for m in node.methods] if hasattr(node, 'methods') else [],
                'type': 'interface' if isinstance(node, InterfaceDeclaration) else 'class',
                'docstring': node.documentation or ''
            }

            structure['classes'].append(class_info)

            if isinstance(node, ClassDeclaration):
                if node.extends:
                    structure['relationships'].append({
                        'source': node.extends.name,
                        'target': node.name,
                        'type': 'inheritance',
                        'file': filepath
                    })

                if node.implements:
                    for interface in node.implements:
                        structure['relationships'].append({
                            'source': interface.name,
                            'target': node.name,
                            'type': 'implements',
                            'file': filepath
                        })
