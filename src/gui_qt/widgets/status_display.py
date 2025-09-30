"""
Rich status display widget
"""

from PySide6.QtWidgets import QTextEdit

class StatusDisplay(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        # TODO: Implement rich status display