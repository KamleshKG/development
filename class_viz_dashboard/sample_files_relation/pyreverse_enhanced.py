# pyreverse_enhanced.py
import sys
from pylint.pyreverse.main import Run
from pylint.pyreverse.inspector import Linker

# Override linker to show all relationships
class ForceLinker(Linker):
    def get_relationships(self, *args, **kwargs):
        rels = super().get_relationships(*args, **kwargs)
        # Force show all possible relationships
        return [r for r in rels if r.relation_type in ('association', 'composition', 'inheritance')]

sys.argv = [
    "pyreverse",
    "-o", "png",
    "-p", "EnhancedDiagram",
    "--linker=ForceLinker",
    "--all-associated",
    "--show-ancestors=5",
    "vehicles.py",
    "university.py",
    "house.py",
    "reporting.py"
]

if __name__ == "__main__":
    Run(sys.argv[1:])