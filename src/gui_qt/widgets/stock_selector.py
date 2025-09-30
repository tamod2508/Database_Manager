"""
Advanced stock selector widget
"""

from PySide6.QtWidgets import QComboBox

class StockSelector(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        # TODO: Implement advanced stock selector