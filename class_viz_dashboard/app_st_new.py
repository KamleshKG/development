import os
import streamlit as st
from streamlit_agraph import agraph, Node, Edge, Config
from utils.core_parser import analyze_codebase


def main():
    st.set_page_config(layout="wide", page_title="Code Structure Visualizer")

    # Sidebar controls
    with st.sidebar:
        st.title("Visualization Settings")
        folder_path = st.text_input("Project Path", value="E:/PYTHON_PROJECTS/designPattern")

        col1, col2 = st.columns(2)
        with col1:
            analyze_btn = st.button("Analyze", type="primary")
        with col2:
            reset_btn = st.button("Reset")

        st.markdown("---")
        st.caption("Display Options")
        show_duplicates = st.checkbox("Show duplicate classes", True)
        cluster_nodes = st.checkbox("Cluster related nodes", True)

    # Main visualization area
    st.title("Code Structure Explorer")

    if reset_btn:
        st.session_state.clear()
        st.rerun()

    if analyze_btn and folder_path:
        visualize_code_structure(folder_path, show_duplicates, cluster_nodes)


def visualize_code_structure(folder_path, show_duplicates, cluster_nodes):
    with st.spinner("Analyzing project structure..."):
        try:
            # 1. Parse codebase
            class_structure = analyze_codebase(folder_path)

            # 2. Process nodes with grouping
            class_groups = {}
            for cls in class_structure["classes"]:
                if cls["name"] not in class_groups:
                    class_groups[cls["name"]] = {
                        "files": [cls["file"]],
                        "language": cls.get("language", "unknown"),
                        "type": cls.get("type", "class"),
                        "methods": list(set(cls.get("methods", [])))  # Dedupe methods
                    }
                else:
                    class_groups[cls["name"]]["files"].append(cls["file"])
                    class_groups[cls["name"]]["methods"].extend(cls.get("methods", []))

            # 3. Create visualization elements
            nodes = create_nodes(class_groups)
            edges = create_edges(class_structure, class_groups)

            # 4. Display summary
            display_summary(nodes, edges, class_groups, show_duplicates)

            # 5. Configure and render graph
            config = Config(
                width="100%",
                height=800,  # Increased height
                directed=True,
                physics={
                    "hierarchicalRepulsion": {
                        "nodeDistance": 200 if cluster_nodes else 100,
                        "centralGravity": 0.3,
                        "springLength": 200
                    },
                    "barnesHut": {
                        "avoidOverlap": 0.5 if cluster_nodes else 0.2
                    }
                },
                node={"labelProperty": "label"},
                link={"highlightColor": "#ff0000"}
            )

            agraph(nodes=nodes, edges=edges, config=config)

        except Exception as e:
            st.error(f"Visualization failed: {str(e)}")
            st.exception(e)


def create_nodes(class_groups):
    return [
        Node(
            id=name,
            label=name,
            title=generate_tooltip(name, data),
            size=20 + min(len(data["methods"]), 10),  # Dynamic sizing
            color=get_node_color(data["language"]),
            shape="box",
            borderWidth=1,
            font={"size": 14}
        )
        for name, data in class_groups.items()
    ]


def create_edges(class_structure, class_groups, rel=None):
    return [
        Edge(
            source=rel["source"],
            target=rel["target"],
            label=rel.get("type", "rel"),
            color=get_edge_color(rel.get("type")),
            width=1 + (2 if rel.get("type") == "inheritance" else 0),  # Thicker inheritance lines
            dashes = rel.get("type") == "dependency"  # Dashed for dependencies
        )
    for rel in class_structure.get("relationships", [])
        if rel["source"] in class_groups and rel["target"] in class_groups

]

def display_summary(nodes, edges, class_groups, show_duplicates):
    total_occurrences = sum(len(v["files"]) for v in class_groups.values())

    # Summary cards
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Unique Classes", len(nodes))
    with col2:
        st.metric("Total Occurrences", total_occurrences)
    with col3:
        st.metric("Relationships", len(edges))

    # Duplicates section
    duplicates = {k: v for k, v in class_groups.items() if len(v["files"]) > 1}
    if duplicates and show_duplicates:
        with st.expander(f"🗃️ {len(duplicates)} Duplicate Classes", expanded=False):
            for name, data in duplicates.items():
                st.markdown(f"""
                **`{name}`**  
                📍 Files: `{", ".join(data["files"])}`  
                ⚙️ Methods: `{", ".join(sorted(set(data["methods"]))) or "None"}`
                """)


def generate_tooltip(name, data):
    return f"""
        <div style="font-family: Arial; max-width: 300px">
            <b style="color: #333">{name}</b><br>
            <span style="color: #666">📂 {len(data['files'])} locations</span><br>
            <span style="color: #666">⚙️ {len(data['methods'])} methods</span><br>
            <hr style="margin: 5px 0">
            <small style="color: #888">
                Language: {data['language']}<br>
                Type: {data['type']}
            </small>
        </div>
    """


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