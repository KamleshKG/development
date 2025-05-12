import os


def generate_visualization_data(class_structure):
    """
    Convert parsed class structure into visualization-ready format
    Handles:
    - Missing parent classes
    - Duplicate class names
    - Relationship validation
    """
    nodes = []
    edges = []
    created_nodes = set()

    # 1. First collect all class names we've found
    detected_classes = {cls['name'] for cls in class_structure['classes']}

    # 2. Add missing parent classes from relationships
    for rel in class_structure.get('relationships', []):
        if rel['source'] not in detected_classes:
            class_structure['classes'].append({
                'name': rel['source'],
                'type': 'class',
                'language': 'unknown',
                'file': 'external',
                'methods': [],
                'bases': []
            })

    # 3. Create unique nodes with file-based IDs
    for cls in class_structure['classes']:
        # Create unique ID using filename and classname
        node_id = f"{cls['name']}::{os.path.basename(cls['file'])}"

        if node_id not in created_nodes:
            nodes.append({
                'id': node_id,
                'label': cls['name'],
                'title': generate_tooltip(cls),
                'color': get_node_color(cls),
                'shape': 'box',
                'borderWidth': 2,
                'font': {'size': 14},
                'file': cls['file'],
                'type': cls.get('type', 'class'),
                'language': cls.get('language', 'unknown')
            })
            created_nodes.add(node_id)

    # 4. Create edges with validated references
    for rel in class_structure.get('relationships', []):
        # Find source node (could be in multiple files)
        source_nodes = [n for n in nodes if n['label'] == rel['source']]
        target_nodes = [n for n in nodes if n['label'] == rel['target']]

        if source_nodes and target_nodes:
            # Connect first matching pair
            edges.append({
                'from': source_nodes[0]['id'],
                'to': target_nodes[0]['id'],
                'label': rel.get('type', 'relation'),
                'arrows': 'to',
                'color': get_edge_color(rel.get('type')),
                'smooth': {'type': 'curvedCW', 'roundness': 0.2}
            })

    return {
        'nodes': nodes,
        'links': edges,
        'stats': {
            'total_classes': len(nodes),
            'total_relationships': len(edges),
            'files_processed': class_structure.get('_debug', {}).get('files_processed', 0)
        }
    }


def generate_tooltip(cls):
    """Generate HTML tooltip content"""
    return (
        f"<b>{cls['name']}</b><br>"
        f"<i>Type:</i> {cls.get('type', 'class')}<br>"
        f"<i>Language:</i> {cls.get('language', 'unknown')}<br>"
        f"<i>File:</i> {cls['file']}<br>"
        f"<i>Methods:</i> {', '.join(cls.get('methods', [])) or 'None'}<br>"
        f"<i>Inherits:</i> {', '.join(cls.get('bases', [])) or 'None'}"
    )


def get_node_color(cls):
    """Determine node color based on language and type"""
    if cls.get('type') == 'interface':
        return {'background': '#FFF9C4', 'border': '#FFEE58'}
    elif cls.get('language') == 'python':
        return {'background': '#E3F2FD', 'border': '#64B5F6'}
    else:  # Java or unknown
        return {'background': '#E8F5E9', 'border': '#81C784'}


def get_edge_color(rel_type):
    """Determine edge color based on relationship type"""
    return {
        'inheritance': '#FFA726',
        'implements': '#66BB6A',
        'extends': '#FFA726',
        'composition': '#AB47BC',
        'dependency': '#42A5F5'
    }.get(rel_type, '#78909C')  # Default gray