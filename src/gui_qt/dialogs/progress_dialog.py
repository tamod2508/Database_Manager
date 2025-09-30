"""
Professional progress dialog for updates
"""

from PySide6.QtWidgets import QDialog, QLabel, QVBoxLayout, QProgressBar
from PySide6.QtCore import Qt

class ProgressDialog(QDialog):
    def __init__(self, incremental=True, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Update Progress")
        self.setFixedSize(400, 150)
        self.setModal(True)
        
        layout = QVBoxLayout()
        
        # Title
        title = "Incremental Update" if incremental else "Full Refresh"
        title_label = QLabel(f"📊 {title} in Progress...")
        title_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #3daee9; margin-bottom: 10px;")
        layout.addWidget(title_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #555555;
                border-radius: 5px;
                text-align: center;
                background-color: #2a2a2a;
            }
            QProgressBar::chunk {
                background-color: #3daee9;
                border-radius: 3px;
            }
        """)
        layout.addWidget(self.progress_bar)
        
        # Status label
        self.status_label = QLabel("Initializing...")
        self.status_label.setStyleSheet("color: #ffffff; margin-top: 10px;")
        layout.addWidget(self.status_label)
        
        self.setLayout(layout)
        
    def update_progress(self, progress, symbol, successful, failed):
        """Update progress display"""
        self.progress_bar.setValue(int(progress * 100))
        self.status_label.setText(f"Processing {symbol}... ({successful} success, {failed} failed)")
