import os
import streamlit as st
from streamlit_agraph import agraph, Node, Edge, Config
from utils.core_parser import analyze_codebase

# Session state initialization
if 'graph_data' not in st.session_state:
    st.session_state.graph_data = None
if 'selected_node' not in st.session_state:
    st.session_state.selected_node = None


def main():
    st.set_page_config(layout="wide", page_title="Code Structure Visualizer")

    # Sidebar controls
    with st.sidebar:
        st.title("Visualization Settings")
        folder_path = st.text_input("Project Path", value="E:/PYTHON_PROJECTS/designPattern")

        if st.button("Analyze", type="primary"):
            analyze_code(folder_path)

        st.markdown("---")
        with st.expander("Display Options"):
            st.checkbox("Show inheritance hierarchy", True, key="show_hierarchy")
            st.slider("Node spacing", 50, 300, 150, key="node_spacing")
            st.selectbox("Layout", ["Hierarchical", "Force-directed"], key="layout")

    # Main visualization area
    st.title("Code Structure Explorer")

    if st.session_state.graph_data:
        render_visualization()

    if st.session_state.selected_node:
        show_node_details()


def analyze_code(folder_path):
    with st.spinner("Analyzing project structure..."):
        try:
            class_structure = analyze_codebase(folder_path)
            nodes, edges, class_groups = process_structure(class_structure)

            st.session_state.graph_data = {
                "nodes": nodes,
                "edges": edges,
                "class_groups": class_groups
            }
            st.session_state.selected_node = None  # Reset selection

            st.success(f"Found {len(nodes)} classes and {len(edges)} relationships")

        except Exception as e:
            st.error(f"Analysis failed: {str(e)}")


def process_structure(class_structure):
    class_groups = {}
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

    nodes = [
        Node(
            id=name,
            label=name,
            title=f"{name} ({len(data['methods'])} methods)",
            size=15 + min(len(data["methods"]), 5),
            color=get_node_color(data["language"]),
            shape="box",
            borderWidth=1
        )
        for name, data in class_groups.items()
    ]

    edges = [
        Edge(
            source=rel["source"],
            target=rel["target"],
            label=rel.get("type", ""),
            color=get_edge_color(rel.get("type")),
            width=1,
            dashes=rel.get("type") == "dependency"
        )
        for rel in class_structure.get("relationships", [])
        if rel["source"] in class_groups and rel["target"] in class_groups
    ]

    return nodes, edges, class_groups


def render_visualization():
    config = Config(
        width="100%",
        height=700,
        directed=True,
        physics={
            "hierarchicalRepulsion": {
                "nodeDistance": st.session_state.node_spacing,
                "centralGravity": 0.1,
                "springLength": 200
            } if st.session_state.layout == "Hierarchical" else {
                "barnesHut": {
                    "gravitationalConstant": -2000,
                    "centralGravity": 0.3,
                    "avoidOverlap": 0.8
                }
            }
        }
    )

    # Remove the 'key' parameter and handle selection differently
    selected_node = agraph(
        nodes=st.session_state.graph_data["nodes"],
        edges=st.session_state.graph_data["edges"],
        config=config
    )

    if selected_node:
        st.session_state.selected_node = selected_node
        st.experimental_rerun()


def show_node_details():
    node_name = st.session_state.selected_node
    data = st.session_state.graph_data["class_groups"].get(node_name)

    if not data:
        st.warning("Node data not found")
        return

    with st.expander(f"🔍 {node_name} Details", expanded=True):
        st.markdown(f"""
        **📂 Files ({len(data['files'])})**  
        ```python
        {chr(10).join(data['files'])}
        ```

        **⚙️ Methods ({len(data['methods'])})**  
        ```python
        {chr(10).join(sorted(data['methods'])) or "None"}
        ```
        """)


def get_node_color(language):
    return {
        "python": "#4E79A7",
        "java": "#F28E2B",
        "unknown": "#59A14F"
    }.get(language, "#8CD17D")


def get_edge_color(rel_type):
    return {
        "inheritance": "#E15759",
        "implements": "#499894",
        "composition": "#B07AA1",
        "dependency": "#9D7660"
    }.get(rel_type, "#D3D3D3")


if __name__ == "__main__":
    main()