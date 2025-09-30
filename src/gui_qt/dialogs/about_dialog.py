"""
About and system info dialog
"""

from PySide6.QtWidgets import QDialog

class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        # TODO: Implement about dialog