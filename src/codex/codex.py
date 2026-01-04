#!/usr/bin/env python3
"""
CodeEx - ParserCraft Execution Environment

A specialized IDE for developing and running applications created with ParserCraft.
Provides professional development environment for ParserCraft-based languages.

Features:
- Multi-interpreter support (load any ParserCraft language)
- Project management (organize code files and resources)
- Professional editor with syntax highlighting
- Real-time code execution
- Integrated console output
- Debugging capabilities
- Project templates
- Version control integration
"""

import sys
import tkinter as tk
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Local imports must come after sys.path modification
from codex.codex_gui import (  # noqa: E402 pylint: disable=wrong-import-position
    CodeExIDE,
)


def main():
    """Launch CodeEx IDE."""
    root = tk.Tk()
    root.title("CodeEx - ParserCraft Execution Environment")
    root.geometry("1600x900")

    CodeExIDE(root)

    root.mainloop()


if __name__ == "__main__":
    main()
