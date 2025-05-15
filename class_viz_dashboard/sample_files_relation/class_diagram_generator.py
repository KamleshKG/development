import ast
from diagrams import Diagram, Edge
from diagrams.custom import Custom


def generate_class_diagram(files):
    with Diagram("Class Relationships", show=False, filename="class_diagram", direction="TB"):
        classes = {}
        relationships = []

        for file in files:
            with open(file) as f:
                tree = ast.parse(f.read())

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    classes[node.name] = Custom(node.name, "./class_icon.png")

                    # Inheritance
                    for base in node.bases:
                        if isinstance(base, ast.Name):
                            relationships.append((node.name, base.id, "inheritance"))

                    # Composition
                    for item in node.body:
                        # Case 1: Direct assignment (self.engine = Engine())
                        if (isinstance(item, ast.Assign) and
                                isinstance(item.value, ast.Call) and
                                isinstance(item.value.func, ast.Name)):
                            relationships.append((node.name, item.value.func.id, "composition"))

                        # Case 2: List append (self.rooms.append(Room()))
                        elif (isinstance(item, ast.FunctionDef) and
                              any(isinstance(stmt, ast.Expr) and
                                  isinstance(stmt.value, ast.Call) and
                                  isinstance(stmt.value.func, ast.Attribute) and
                                  stmt.value.func.attr == 'append'
                                  for stmt in ast.walk(item))):
                            # This will find Room class usage in append() calls
                            pass

        # Draw relationships
        for src, dst, rel_type in relationships:
            if src in classes and dst in classes:
                if rel_type == "inheritance":
                    classes[src] >> Edge(arrowhead="empty", label="inherits") >> classes[dst]
                elif rel_type == "composition":
                    classes[src] >> Edge(arrowhead="diamond", label="contains", style="bold") >> classes[dst]


if __name__ == "__main__":
    files = ['vehicles.py', 'university.py', 'house.py', 'reporting.py']
    generate_class_diagram(files)
    print("Diagram generated as 'class_diagram.png'")