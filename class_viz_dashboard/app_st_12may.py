import os
import pandas as pd
import streamlit as st
from streamlit_agraph import agraph, Node, Edge, Config
from utils.core_parser import analyze_codebase


# ======================
# UTILITY FUNCTIONS (Defined First)
# ======================
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


# ======================
# CORE ANALYSIS FUNCTIONS
# ======================
def process_structure(class_structure):
    class_groups = {}
    relations = []

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

    for rel in class_structure.get("relationships", []):
        if rel["source"] in class_groups and rel["target"] in class_groups:
            relations.append({
                "Source": rel["source"],
                "Target": rel["target"],
                "Type": rel.get("type", "association")
            })

    nodes = [
        Node(
            id=name,
            label=name,
            title=f"{name}\n{len(data['methods'])} methods",
            size=20,
            color=get_node_color(data["language"]),
            shape="box",
            borderWidth=1,
            font={"size": 14}
        )
        for name, data in class_groups.items()
    ]

    edges = [
        Edge(
            source=rel["Source"],
            target=rel["Target"],
            label=rel["Type"],
            color=get_edge_color(rel["Type"]),
            width=2
        )
        for rel in relations
    ]

    return nodes, edges, class_groups, pd.DataFrame(relations)


def analyze_code(folder_path):
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


# ======================
# VISUALIZATION FUNCTIONS
# ======================
def render_visualization(layout_mode, node_spacing):
    if not st.session_state.graph_data:
        return

    config = Config(
        width="100%",
        height=700,
        directed=True,
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
    if not st.session_state.selected_node or not st.session_state.graph_data:
        return

    node_name = st.session_state.selected_node
    data = st.session_state.graph_data["class_groups"].get(node_name)

    if not data:
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


# ======================
# MAIN APP FUNCTION
# ======================
def main():
    # Session state initialization
    if 'graph_data' not in st.session_state:
        st.session_state.graph_data = None
    if 'selected_node' not in st.session_state:
        st.session_state.selected_node = None
    if 'current_folder' not in st.session_state:
        st.session_state.current_folder = ""

    # Page config
    st.set_page_config(layout="wide", page_title="Code Structure Visualizer")

    # Three-column layout
    left_panel, center_panel, right_panel = st.columns([0.5, 1 , 2], gap="large")

    # ======================
    # LEFT PANEL (INPUT/ANALYSIS)
    # ======================
    with left_panel:
        st.title("🔍 Analysis Setup")

        # Folder input with validation
        folder_path = st.text_input(
            "Project Folder Path",
            value=st.session_state.current_folder,
            placeholder="E:/PYTHON_PROJECTS/your_project"
        )

        if st.button("Analyze Code", type="primary", key="analyze_btn"):
            if os.path.exists(folder_path):
                analyze_code(folder_path)
            else:
                st.error("Folder does not exist!")

        st.markdown("---")

        # Display analysis results if available
        if st.session_state.graph_data:
            st.success(f"Analyzed: {st.session_state.current_folder}")
            st.metric("Classes Found", len(st.session_state.graph_data["nodes"]))
            st.metric("Relationships", len(st.session_state.graph_data["edges"]))

            # Enhanced export options
            with st.expander("💾 Export Data"):
                st.download_button(
                    "Download Relationships (CSV)",
                    data=st.session_state.graph_data["relations_df"].to_csv(index=False),
                    file_name="class_relationships.csv"
                )
                st.download_button(
                    "Download Class Summary (CSV)",
                    data=pd.DataFrame({
                        "Class": list(st.session_state.graph_data["class_groups"].keys()),
                        "Methods": [len(data["methods"]) for data in
                                    st.session_state.graph_data["class_groups"].values()],
                        "Files": [len(data["files"]) for data in st.session_state.graph_data["class_groups"].values()]
                    }).to_csv(index=False),
                    file_name="class_summary.csv"
                )

    # ======================
    # CENTER PANEL (TABULAR DATA)
    # ======================
    with center_panel:
        if st.session_state.graph_data:
            st.title("📋 Relationships")

            # Interactive filtering
            relation_filter = st.selectbox(
                "Filter by type:",
                ["All"] + list(st.session_state.graph_data["relations_df"]["Type"].unique()),
                key="relation_filter"
            )

            # Display filtered table
            df = st.session_state.graph_data["relations_df"]
            if relation_filter != "All":
                df = df[df["Type"] == relation_filter]

            st.dataframe(
                df.style.applymap(
                    lambda x: f"color: {get_edge_color(x)}" if x in ["inheritance", "implements"] else "",
                    subset=["Type"]
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
                col1, col2 = st.columns(2)
                with col1:
                    layout_mode = st.selectbox(
                        "Layout Algorithm",
                        ["Hierarchical", "Force-directed"],
                        key="layout_mode"
                    )
                with col2:
                    node_spacing = st.slider(
                        "Node Spacing",
                        50, 300, 150,
                        key="node_spacing"
                    )

            # Render the graph
            render_visualization(layout_mode, node_spacing)

            # Node details panel
            if st.session_state.selected_node:
                show_node_details()


if __name__ == "__main__":
    main()