"""
Modern settings page with professional blue palette
"""

from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PySide6.QtCore import Qt

class SettingsPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # Modern centered content
        layout.addStretch()
        
        icon_label = QLabel("⚙️")
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet("""
            QLabel {
                font-size: 72px;
                color: #023e7d;
                margin-bottom: 20px;
            }
        """)
        layout.addWidget(icon_label)
        
        title_label = QLabel("Application Settings")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: 700;
                color: #ffffff;
                margin-bottom: 12px;
            }
        """)
        layout.addWidget(title_label)
        
        desc_label = QLabel("Configuration options and preferences\nComing in Day 3 of development")
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #d5d7dd;
                line-height: 22px;
            }
        """)
        layout.addWidget(desc_label)
        
        layout.addStretch()
        self.setLayout(layout)
