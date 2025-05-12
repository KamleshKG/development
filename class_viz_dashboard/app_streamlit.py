import os
import streamlit as st
from streamlit_agraph import agraph, Node, Edge, Config
# from code_parser import analyze_codebase  # Your existing parsing logic
from utils.core_parser import analyze_codebase

def main():
    st.set_page_config(layout="wide", page_title="Code Structure Visualizer")

    # Sidebar for input
    with st.sidebar:
        st.title("Settings")
        folder_path = st.text_input(
            "Project Folder Path",
            value="E:/PYTHON_PROJECTS/python_checklist"
        )
        analyze_btn = st.button("Analyze Code")

    # Main visualization area
    st.title("Class Structure Visualizer")

    if analyze_btn and folder_path:
        if not os.path.exists(folder_path):
            st.error("Error: Folder path does not exist!")
            return

        with st.spinner("Analyzing code..."):
            try:
                # Get class structure using your existing parser
                class_structure = analyze_codebase(folder_path)

                # Convert to nodes and edges
                # Replace the nodes/edges generation code with this:
                nodes = []
                seen_ids = set()  # Track used IDs to avoid duplicates

                for cls in class_structure["classes"]:
                    # Create unique ID by combining class name and file path hash
                    unique_id = f"{cls['name']}_{abs(hash(cls['file']))}"

                    nodes.append(Node(
                        id=unique_id,  # Use unique ID
                        label=cls["name"],
                        title=f"""
                            Class: {cls["name"]}
                            File: {cls["file"]}
                            Type: {cls.get("type", "class")}
                            Language: {cls.get("language", "unknown")}
                        """,
                        size=25,
                        color="#64B5F6" if cls.get("language") == "python" else "#81C784",
                        shape="box"
                    ))
                    seen_ids.add(unique_id)

                edges = []
                for rel in class_structure.get("relationships", []):
                    # Find source/target nodes by matching class names
                    source_nodes = [n for n in nodes if n.label == rel["source"]]
                    target_nodes = [n for n in nodes if n.label == rel["target"]]

                    if source_nodes and target_nodes:
                        edges.append(Edge(
                            source=source_nodes[0].id,  # Use the unique ID
                            target=target_nodes[0].id,
                            label=rel.get("type", "relation"),
                            color="#FFA726" if rel.get("type") == "inheritance" else "#78909C"
                        ))

                # Display graph
                config = Config(
                    width="100%",
                    height=700,
                    directed=True,
                    nodeHighlightBehavior=True,
                    highlightColor="#F7A7A6",
                    collapsible=True,
                    node={"labelProperty": "label"},
                    link={"highlightColor": "#ff0000"},
                    physics={
                        "hierarchicalRepulsion": {"nodeDistance": 150},
                        "barnesHut": {"avoidOverlap": 0.5}
                    }
                )

                st.success(f"Found {len(nodes)} classes and {len(edges)} relationships")
                agraph(nodes=nodes, edges=edges, config=config)

            except Exception as e:
                st.error(f"Analysis failed: {str(e)}")


if __name__ == "__main__":
    main()