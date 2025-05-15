import sys
from pylint.pyreverse.main import Run

if __name__ == "__main__":
    # Configure for maximum relationship visibility
    sys.argv = [
        "pyreverse",
        "-o", "png",
        "-p", "ClassDiagram",
        "--filter-mode=ALL",
        "--ignore=test",
        "--colorized",
        "--max-color-depth=8",
        "vehicles.py",
        "university.py",
        "house.py",
        "reporting.py"
    ]

    if __name__ == "__main__":
        Run(sys.argv[1:])