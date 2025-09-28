#!/usr/bin/env python3
"""
Menu bar application launcher
"""

import sys
import os
from pathlib import Path

# Add src to Python path
current_dir = Path(__file__).parent
src_path = current_dir / "src"
sys.path.insert(0, str(src_path))

def main():
    """Launch the menu bar application"""
    try:
        # Import and run the menu bar app (same pattern as run_gui.py)
        from src.menubar.menu_app import main as menu_main
        
        print("Starting Database Manager menu bar app...")
        menu_main()
        
    except ImportError as e:
        print(f"Import error: {e}")
        print("Available modules in src:")
        src_dir = Path(__file__).parent / "src"
        if src_dir.exists():
            for item in src_dir.iterdir():
                if item.is_dir() and not item.name.startswith('__'):
                    print(f"  - {item.name}/")
        else:
            print("  src directory not found!")
        sys.exit(1)
    except Exception as e:
        print(f"Error starting menu bar app: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
