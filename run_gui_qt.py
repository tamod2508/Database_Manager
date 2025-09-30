#!/usr/bin/env python3
"""
PySide6 GUI application launcher - Fixed deprecation warnings
"""

import sys
import os
import platform
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt, QLoggingCategory
from PySide6.QtGui import QIcon, QFont, QFontDatabase

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def main():
    try:
        # Suppress Qt font warnings
        QLoggingCategory.setFilterRules("qt.qpa.fonts.debug=false")
        
        app = QApplication(sys.argv)
        app.setApplicationName("Database Manager")
        app.setOrganizationName("StockAnalysis")
        
        # Set appropriate font based on platform (fixed deprecation)
        if platform.system() == "Darwin":  # macOS
            available_fonts = ["Helvetica", "SF Pro Display", "Arial", "system-ui"]
        elif platform.system() == "Windows":
            available_fonts = ["Segoe UI", "Arial", "Helvetica", "system-ui"]
        else:  # Linux
            available_fonts = ["Ubuntu", "DejaVu Sans", "Arial", "Helvetica"]
        
        # Use static method instead of creating instance (fixes deprecation)
        available_families = QFontDatabase.families()
        
        selected_font = None
        for font_name in available_fonts:
            if font_name in available_families:
                selected_font = QFont(font_name)
                break
        
        if selected_font is None:
            # Fallback to system default
            selected_font = QFont()
        
        selected_font.setPointSize(13)
        app.setFont(selected_font)
        
        # Apply modern dark theme
        theme_css = load_dark_theme()
        if theme_css:
            app.setStyleSheet(theme_css)
        
        from src.gui_qt.main_window import MainWindow
        window = MainWindow()
        window.show()
        
        sys.exit(app.exec())
        
    except ImportError as e:
        print(f"Import error: {e}")
        print("Please run: pip install PySide6 matplotlib")
        sys.exit(1)
    except Exception as e:
        print(f"Application error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

def load_dark_theme():
    """Load modern dark theme"""
    theme_path = Path(__file__).parent / "src" / "gui_qt" / "styles" / "dark_theme.qss"
    if theme_path.exists():
        try:
            with open(theme_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Error loading theme: {e}")
            return ""
    else:
        print(f"Theme file not found: {theme_path}")
        return ""

if __name__ == "__main__":
    main()
