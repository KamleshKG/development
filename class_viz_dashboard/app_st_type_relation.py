import os
import pandas as pd
import streamlit as st
from streamlit_agraph import agraph, Node, Edge, Config
from utils.core_parser import analyze_codebase

# ======================
# CONSTANTS & UTILITIES
# ======================
RELATIONSHIP_TYPES = {
    "inheritance": {
        "color": "#E15759",
        "width": 3,
        "dashes": False,
        "arrow": "triangle"
    },
    "implements": {
        "color": "#499894",
        "width": 2,
        "dashes": True,
        "arrow": "triangle"
    },
    "composition": {
        "color": "#B07AA1",
        "width": 2,
        "dashes": False,
        "arrow": "diamond"
    },
    "aggregation": {
        "color": "#FF9DA7",
        "width": 2,
        "dashes": False,
        "arrow": "diamond"
    },
    "association": {
        "color": "#9D7660",
        "width": 1,
        "dashes": False,
        "arrow": "circle"
    },
    "dependency": {
        "color": "#D3D3D3",
        "width": 1,
        "dashes": True,
        "arrow": "circle"
    }
}


def get_node_color(language):
    """Returns color based on programming language"""
    return {
        "python": "#4E79A7",
        "java": "#F28E2B",
        "unknown": "#59A14F"
    }.get(language.lower(), "#8CD17D")


def get_relationship_style(rel_type):
    """Returns styling for different relationship types"""
    return RELATIONSHIP_TYPES.get(rel_type.lower(), {
        "color": "#9D7660",
        "width": 1,
        "dashes": False,
        "arrow": "circle"
    })


# ======================
# CORE ANALYSIS FUNCTIONS
# ======================
def analyze_code(folder_path):
    """Analyzes codebase and stores results in session state"""
    with st.spinner("Analyzing project structure..."):
        try:
            class_structure = analyze_codebase(folder_path)
            nodes, edges, class_groups, df_relations = process_structure(class_structure)

            st.session_state.graph_data = {
                "nodes": nodes,
                "edges": edges,
                "class_groups": class_groups,
                "relations_df": df_relations
            }
            st.session_state.selected_node = None
            st.session_state.current_folder = folder_path

        except Exception as e:
            st.error(f"Analysis failed: {str(e)}")


def process_structure(class_structure):
    """Processes raw class structure into visualization components"""
    class_groups = {}
    relations = []

    # Process classes
    for cls in class_structure["classes"]:
        if cls["name"] not in class_groups:
            class_groups[cls["name"]] = {
                "files": [cls["file"]],
                "language": cls.get("language", "unknown"),
                "type": cls.get("type", "class"),
                "methods": list(set(cls.get("methods", [])))
            }
        else:
            class_groups[cls["name"]]["files"].append(cls["file"])
            class_groups[cls["name"]]["methods"].extend(cls.get("methods", []))

    # Process relationships
    for rel in class_structure.get("relationships", []):
        if rel["source"] in class_groups and rel["target"] in class_groups:
            rel_type = rel.get("type", "association").lower()
            style = get_relationship_style(rel_type)

            relations.append({
                "Source": rel["source"],
                "Target": rel["target"],
                "Type": rel_type,
                "Style": style
            })

    # Create nodes
    nodes = []
    for name, data in class_groups.items():
        is_interface = data["type"].lower() == "interface"
        nodes.append(Node(
            id=name,
            label=name,
            title=f"{name}\nType: {data['type']}\nMethods: {len(data['methods'])}",
            size=25 if is_interface else 20,
            color="#FFD700" if is_interface else get_node_color(data["language"]),
            shape="ellipse" if is_interface else "box",
            borderWidth=2,
            font={"size": 14}
        ))

    # Create edges
    edges = []
    for rel in relations:
        edges.append(Edge(
            source=rel["Source"],
            target=rel["Target"],
            label=rel["Type"],
            color=rel["Style"]["color"],
            width=rel["Style"]["width"],
            dashes=rel["Style"]["dashes"],
            arrows_to={"enabled": True, "type": rel["Style"]["arrow"]}
        ))

    return nodes, edges, class_groups, pd.DataFrame(relations)


# ======================
# VISUALIZATION FUNCTIONS
# ======================
def render_visualization(layout_mode, node_spacing):
    """Renders the interactive graph visualization"""
    if not st.session_state.graph_data:
        return

    config = Config(
        width="100%",
        height=700,
        directed=True,
        nodeHighlightBehavior=True,
        highlightColor="#F7A7A6",
        physics={
            "hierarchicalRepulsion": {
                "nodeDistance": node_spacing,
                "centralGravity": 0.1,
                "springLength": 200
            } if layout_mode == "Hierarchical" else {
                "barnesHut": {
                    "gravitationalConstant": -2000,
                    "centralGravity": 0.3,
                    "avoidOverlap": 0.8
                }
            }
        }
    )

    selected_node = agraph(
        nodes=st.session_state.graph_data["nodes"],
        edges=st.session_state.graph_data["edges"],
        config=config
    )

    if selected_node:
        st.session_state.selected_node = selected_node
        st.experimental_rerun()


def show_node_details():
    """Displays detailed information about selected node"""
    if not st.session_state.selected_node or not st.session_state.graph_data:
        return

    node_name = st.session_state.selected_node
    data = st.session_state.graph_data["class_groups"].get(node_name)

    if not data:
        return

    with st.expander(f"🔍 {node_name} Details", expanded=True):
        st.markdown(f"""
        **Type:** {data['type'].capitalize()}  
        **Language:** {data['language'].capitalize()}  

        **📂 Files ({len(data['files'])})**  
        ```python
        {chr(10).join(data['files'])}
        ```

        **⚙️ Methods ({len(data['methods'])})**  
        ```python
        {chr(10).join(sorted(data['methods'])) or "None"}
        ```
        """)


# ======================
# MAIN APPLICATION
# ======================
def main():
    # Initialize session state
    if 'graph_data' not in st.session_state:
        st.session_state.graph_data = None
    if 'selected_node' not in st.session_state:
        st.session_state.selected_node = None
    if 'current_folder' not in st.session_state:
        st.session_state.current_folder = ""

    # Page configuration
    st.set_page_config(layout="wide", page_title="Advanced Class Visualizer")

    # Three-column layout
    left_panel, center_panel, right_panel = st.columns([0.5, 1.5, 1.5], gap="large")

    # ======================
    # LEFT PANEL (CONTROLS)
    # ======================
    with left_panel:
        st.title("🔍 Analysis Setup")

        # Folder input
        folder_path = st.text_input(
            "Project Folder Path",
            value=st.session_state.current_folder,
            placeholder="E:/PYTHON_PROJECTS/your_project"
        )

        # Analysis button
        if st.button("Analyze Code", type="primary"):
            if os.path.exists(folder_path):
                analyze_code(folder_path)
            else:
                st.error("Folder does not exist!")

        st.markdown("---")

        # Relationship legend
        st.markdown("**Relationship Types**")
        for rel_type, style in RELATIONSHIP_TYPES.items():
            st.markdown(f"""
            <div style="margin: 5px 0; display: flex; align-items: center;">
                <div style="width:20px; height:20px; 
                            border: 1px solid {style['color']};
                            background: {style['color'] + '33'}; 
                            margin-right:10px;"></div>
                {rel_type.capitalize()}
            </div>
            """, unsafe_allow_html=True)

    # ======================
    # CENTER PANEL (TABULAR DATA)
    # ======================
    with center_panel:
        if st.session_state.graph_data:
            st.title("📋 Relationships")

            # Filter controls
            relation_filter = st.selectbox(
                "Filter by type:",
                ["All"] + list(RELATIONSHIP_TYPES.keys())
            )

            # Display filtered table
            df = st.session_state.graph_data["relations_df"]
            if relation_filter != "All":
                df = df[df["Type"] == relation_filter]

            st.dataframe(
                df.style.apply(
                    lambda x: [f"background: {get_relationship_style(x['Type'])['color'] + '33'}"
                               if i == df.columns.get_loc('Type') else ''
                               for i in range(len(x))],
                    axis=1
                ),
                height=500,
                use_container_width=True
            )

    # ======================
    # RIGHT PANEL (VISUALIZATION)
    # ======================
    with right_panel:
        st.title("🌐 Visualization")

        if st.session_state.graph_data:
            # Visualization controls
            with st.expander("⚙️ Display Settings", expanded=True):
                layout_mode = st.selectbox(
                    "Layout Algorithm",
                    ["Hierarchical", "Force-directed"],
                    index=0
                )
                node_spacing = st.slider(
                    "Node Spacing",
                    50, 300, 150
                )

            # Render graph
            render_visualization(layout_mode, node_spacing)

            # Show node details if selected
            if st.session_state.selected_node:
                show_node_details()


if __name__ == "__main__":
    main()