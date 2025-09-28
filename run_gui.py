#!/usr/bin/env python3
"""GUI application launcher"""

import sys
import os
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

os.environ['TK_SILENCE_DEPRECATION'] = '1'

def main():
    try:
        from src.gui.main_window import main as gui_main
        gui_main()
    except ImportError as e:
        print(f"Import error: {e}")
        print("Please run: pip install -r setup/requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"Application error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
