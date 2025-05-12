import os
import streamlit as st
from streamlit_agraph import agraph, Node, Edge, Config
from utils.core_parser import analyze_codebase  # Your existing parsing logic


def main():
    st.set_page_config(layout="wide", page_title="Code Structure Visualizer")

    # Sidebar for input
    with st.sidebar:
        st.title("Settings")
        folder_path = st.text_input(
            "Project Folder Path",
            value="E:/PYTHON_PROJECTS/designPattern"
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
                # Get class structure
                class_structure = analyze_codebase(folder_path)

                # Group duplicate classes
                class_groups = {}
                for cls in class_structure["classes"]:
                    if cls["name"] not in class_groups:
                        class_groups[cls["name"]] = {
                            "files": [cls["file"]],
                            "language": cls.get("language", "unknown"),
                            "type": cls.get("type", "class"),
                            "methods": cls.get("methods", [])
                        }
                    else:
                        class_groups[cls["name"]]["files"].append(cls["file"])
                        class_groups[cls["name"]]["methods"].extend(cls.get("methods", []))

                # Create nodes and edges
                nodes = [
                    Node(
                        id=name,
                        label=name,
                        title=generate_tooltip(name, data),
                        size=25,
                        color=get_node_color(data["language"]),
                        shape="box"
                    )
                    for name, data in class_groups.items()
                ]

                edges = []
                for rel in class_structure.get("relationships", []):
                    if rel["source"] in class_groups and rel["target"] in class_groups:
                        edges.append(Edge(
                            source=rel["source"],
                            target=rel["target"],
                            label=rel.get("type", "relation"),
                            color=get_edge_color(rel.get("type")),
                            width=2
                        ))

                # Show summary
                total_occurrences = sum(len(v["files"]) for v in class_groups.values())
                st.success(
                    f"Found {len(nodes)} classes ({total_occurrences} occurrences) and {len(edges)} relationships")

                # Graph config
                config = Config(
                    width="100%",
                    height=700,
                    directed=True,
                    physics={"hierarchicalRepulsion": {"nodeDistance": 150}}
                )

                # Render graph
                agraph(nodes=nodes, edges=edges, config=config)

                # Show duplicates
                duplicates = {k: v for k, v in class_groups.items() if len(v["files"]) > 1}
                if duplicates:
                    with st.expander(f"⚠️ {len(duplicates)} Duplicate Classes"):
                        for name, data in duplicates.items():
                            st.markdown(f"""
                                **{name}**  
                                📂 Files: {", ".join(data["files"])}  
                                ⚙️ Methods: {", ".join(data["methods"]) or "None"}
                            """)

            except Exception as e:
                st.error(f"Analysis failed: {str(e)}")


def generate_tooltip(name, data):
    return f"""
        <b>{name}</b><br>
        <i>Type:</i> {data['type']}<br>
        <i>Language:</i> {data['language']}<br>
        <i>Files:</i> {len(data['files'])}<br>
        <i>Methods:</i> {len(data['methods'])}
    """


def get_node_color(language):
    return "#64B5F6" if language == "python" else "#81C784"


def get_edge_color(rel_type):
    return "#FFA726" if rel_type == "inheritance" else "#78909C"


if __name__ == "__main__":
    main()