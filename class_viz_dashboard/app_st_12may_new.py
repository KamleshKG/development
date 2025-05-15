import os
import pandas as pd
import streamlit as st
from streamlit_agraph import agraph, Node, Edge, Config
from typing import Dict, List, Any, Tuple
import ast
from abc import ABC, abstractmethod
from javalang import parse
from javalang.tree import ClassDeclaration, InterfaceDeclaration
from utils.core_parser import *

# ======================
# CONSTANTS & STYLING
# ======================
RELATIONSHIP_TYPES = {
    "inheritance": {
        "color": "#E15759",
        "width": 3,
        "dashes": False,
        "arrow": "triangle",
        "label": "inherits",
        "arrow_to": {"enabled": True, "type": "triangle"}
    },
    "implements": {
        "color": "#499894",
        "width": 2,
        "dashes": True,
        "arrow": "triangle",
        "label": "implements",
        "arrow_to": {"enabled": True, "type": "triangle", "fill": False}
    },
    "composition": {
        "color": "#B07AA1",
        "width": 3,
        "dashes": False,
        "arrow": "diamond",
        "label": "composition",
        "arrow_to": {"enabled": True, "type": "diamond", "scaleFactor": 1}
    },
    "aggregation": {
        "color": "#FF9DA7",
        "width": 2,
        "dashes": False,
        "arrow": "diamond",
        "label": "aggregation",
        "arrow_to": {"enabled": True, "type": "diamond", "scaleFactor": 1, "fill": False}
    },
    "association": {
        "color": "#9D7660",
        "width": 2,
        "dashes": False,
        "arrow": None,
        "label": "association"
    },
    "dependency": {
        "color": "#76B7B2",
        "width": 1,
        "dashes": True,
        "arrow": "arrow",
        "label": "dependency",
        "arrow_to": {"enabled": True, "type": "arrow"}
    }
}

NODE_COLORS = {
    "python": {"class": "#4E79A7", "interface": "#F28E2B"},
    "java": {"class": "#59A14F", "interface": "#E15759"},
    "default": {"class": "#8CD17D", "interface": "#FFD700"}
}


# ======================
# CORE FUNCTIONS
# ======================

def analyze_code(folder_path: str) -> None:
    """Analyze codebase and store results in session state"""
    if not folder_path or not os.path.exists(folder_path):
        st.error("Please provide a valid folder path")
        return

    with st.spinner(f"Analyzing {folder_path}..."):
        try:
            structure = analyze_codebase(folder_path)
            if structure['errors']:
                st.warning(f"Found {len(structure['errors'])} errors during analysis")
                for error in structure['errors']:
                    st.error(error)

            nodes, edges, metrics = process_structure(structure)

            st.session_state.graph_data = {
                "nodes": nodes,
                "edges": edges,
                "metrics": metrics,
                "raw_data": structure
            }
            st.session_state.selected_node = None
            st.toast("Analysis completed successfully!", icon="✅")

        except Exception as e:
            st.error(f"Analysis failed: {str(e)}")


def process_structure(structure: Dict[str, Any]) -> Tuple[List[Node], List[Edge], Dict[str, Any]]:
    """Convert raw analysis data into visualization components"""
    nodes = []
    edges = []
    class_info = {}
    metrics = {
        "total_classes": 0,
        "total_relationships": 0,
        "by_type": {k: 0 for k in RELATIONSHIP_TYPES}
    }

    # Process classes
    for cls in structure["classes"]:
        class_info[cls["name"]] = cls
        metrics["total_classes"] += 1

        node_type = "interface" if cls["type"] == "interface" else "class"
        language = cls.get("language", "default")

        nodes.append(Node(
            id=cls["name"],
            label=cls["name"],
            size=25 if node_type == "interface" else 20,
            color=NODE_COLORS.get(language, {}).get(node_type, NODE_COLORS["default"][node_type]),
            shape="ellipse" if node_type == "interface" else "box",
            title=f"{cls['name']}\nType: {node_type}\nMethods: {len(cls['methods'])}",
            borderWidth=2,
            font={"size": 14}
        ))

    # Process relationships
    for rel in structure.get("relationships", []):
        rel_type = rel.get("type", "association").lower()
        if rel_type not in RELATIONSHIP_TYPES:
            continue

        if rel["source"] in class_info and rel["target"] in class_info:
            style = RELATIONSHIP_TYPES[rel_type]
            edge_data = {
                "source": rel["source"],
                "target": rel["target"],
                "label": style["label"],
                "color": style["color"],
                "width": style["width"],
                "dashes": style["dashes"],
                "arrows_to": style.get("arrow_to",
                                    {"enabled": True, "type": style["arrow"]} if style["arrow"] else None),
                "title": rel.get("context", ""),
                "smooth": True,
            }

            edges.append(Edge(**edge_data))
            metrics["total_relationships"] += 1
            metrics["by_type"][rel_type] += 1
    return nodes, edges, metrics



# ======================
# UI COMPONENTS
# ======================
def render_visualization(layout_mode: str, physics_options: Dict[str, Any]) -> None:
    """Render interactive graph visualization"""
    if "graph_data" not in st.session_state:
        return

    config = Config(
        width="100%",
        height=700,
        directed=True,
        nodeHighlightBehavior=True,
        highlightColor="#F7A7A6",
        collapsible=True,
        node={'labelProperty': 'label'},
        link={'highlightColor': '#F7A7A6'},
        physics={
            "hierarchicalRepulsion": {
                "nodeDistance": physics_options.get("node_distance", 150),
                "centralGravity": physics_options.get("central_gravity", 0.1),
                "springLength": physics_options.get("spring_length", 200)
            } if layout_mode == "Hierarchical" else {
                "barnesHut": {
                    "gravitationalConstant": physics_options.get("gravity", -2000),
                    "centralGravity": physics_options.get("central_gravity", 0.3),
                    "avoidOverlap": physics_options.get("avoid_overlap", 0.8)
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
        st.rerun()



def show_node_details() -> None:
    """Display detailed information about selected node"""
    if "selected_node" not in st.session_state or not st.session_state.selected_node:
        return

    node_name = st.session_state.selected_node
    graph_data = st.session_state.graph_data
    node_data = next((c for c in graph_data["raw_data"]["classes"] if c["name"] == node_name), None)

    if not node_data:
        return

    with st.expander(f"🔍 {node_name} Details", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Type", node_data["type"].capitalize())
            st.metric("Language", node_data.get("language", "unknown").capitalize())
            st.metric("Methods", len(node_data["methods"]))

        with col2:
            st.metric("Attributes", len(node_data.get("attributes", [])))
            st.metric("Relationships",
                      len([e for e in graph_data["edges"]
                           if e.source == node_name or e.target == node_name]))

        st.subheader("📜 Docstring")
        st.code(node_data.get("docstring", "No docstring available"), language='python')

        st.subheader("📦 Attributes")
        st.code('\n'.join(node_data.get("attributes", ["No attributes"])))

        st.subheader("⚙️ Methods")
        st.code('\n'.join(node_data["methods"]) if node_data["methods"] else "No methods")



def show_metrics() -> None:
    """Display analysis metrics"""
    if "graph_data" not in st.session_state:
        return

    metrics = st.session_state.graph_data["metrics"]
    raw_data = st.session_state.graph_data.get("raw_data", {})

    st.subheader("📊 Codebase Metrics")
    cols = st.columns(3)
    cols[0].metric("Total Classes", metrics["total_classes"])
    cols[1].metric("Total Relationships", metrics["total_relationships"])

    # Handle missing _meta data gracefully
    files_processed = raw_data.get("_meta", {}).get("files_processed", "N/A")
    cols[2].metric("Files Processed", files_processed)

    st.subheader("Relationship Distribution")
    rel_data = {k: v for k, v in metrics["by_type"].items() if v > 0}
    if rel_data:
        st.bar_chart(pd.DataFrame.from_dict(rel_data, orient='index', columns=['Count']))
    else:
        st.warning("No relationships detected")



# ======================
# MAIN APP
# ======================
def main():
    # Initialize session state
    if 'graph_data' not in st.session_state:
        st.session_state.graph_data = None
    if 'selected_node' not in st.session_state:
        st.session_state.selected_node = None

    # Page config
    st.set_page_config(layout="wide", page_title="Code Relationship Visualizer")

    # Main layout
    left_panel, center_panel, right_panel = st.columns([1, 1.5, 2], gap="large")

    with left_panel:
        st.title("🔍 Analysis")

        folder_path = st.text_input(
            "Project Folder Path",
            value=".",  # Default to current directory
            help="Path to directory containing Python/Java files"
        )

        if st.button("Analyze Code", type="primary"):
            analyze_code(folder_path)

        st.markdown("---")
        st.markdown("**Relationship Legend**")
        for rel_type, style in RELATIONSHIP_TYPES.items():
            st.markdown(f"""
            <div style="margin: 5px 0; display: flex; align-items: center;">
                <div style="width:20px; height:1px;
                            border: 2px solid {style['color']};
                            background: {style['color']};
                            margin-right:5px;"></div>
                {style['label'].capitalize()}
            </div>
            """, unsafe_allow_html=True)

        if st.session_state.graph_data:
            st.markdown("---")
            show_metrics()

    with center_panel:
        if st.session_state.graph_data:
            st.title("📋 Relationships")

            # Filter controls
            rel_type = st.selectbox("Filter by type:", ["All"] + list(RELATIONSHIP_TYPES.keys()))

            # Create relationship DataFrame
            relationships = []
            for rel in st.session_state.graph_data["raw_data"]["relationships"]:
                relationships.append({
                    "Source": rel["source"],
                    "Target": rel["target"],
                    "Type": rel["type"],
                    "Context": rel.get("context", ""),
                    "File": rel.get("file", "")
                })

            df = pd.DataFrame(relationships)

            if rel_type != "All":
                df = df[df["Type"] == rel_type]

            st.dataframe(
                df.style.apply(
                    lambda x: [
                        f"background: {RELATIONSHIP_TYPES[x['Type']]['color']}33"
                        if i == df.columns.get_loc('Type')
                        else ''
                        for i in range(len(x))
                    ],
                    axis=1
                ),
                height=600,
                use_container_width=True
            )

    with right_panel:
        st.title("🌐 Visualization")

        if st.session_state.graph_data:
            # Visualization settings
            with st.expander("⚙️ Display Settings", expanded=True):
                layout_mode = st.selectbox(
                    "Layout Algorithm",
                    ["Hierarchical", "Force-directed"],
                    index=0
                )
                physics_options = {
                    "node_distance": st.slider("Node Distance", 50, 300, 150),
                    "central_gravity": st.slider("Central Gravity", 0.0, 1.0, 0.3),
                    "avoid_overlap": st.slider("Avoid Overlap", 0.0, 1.0, 0.8)
                }

            # Render graph
            render_visualization(layout_mode, physics_options)

            # Node details
            if st.session_state.selected_node:
                show_node_details()



if __name__ == "__main__":
    main()
