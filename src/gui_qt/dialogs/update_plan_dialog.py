"""
Update plan display dialog
"""

from PySide6.QtWidgets import QDialog, QLabel, QVBoxLayout, QPushButton, QTextEdit
from PySide6.QtCore import Qt

class UpdatePlanDialog(QDialog):
    def __init__(self, plan=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("📋 Update Plan")
        self.setFixedSize(500, 400)
        self.setModal(True)
        
        layout = QVBoxLayout()
        
        # Title
        title_label = QLabel("📋 Update Plan Analysis")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #3daee9; margin-bottom: 15px;")
        layout.addWidget(title_label)
        
        # Plan details
        plan_text = QTextEdit()
        plan_text.setReadOnly(True)
        plan_text.setStyleSheet("""
            QTextEdit {
                background-color: #2a2a2a;
                border: 1px solid #555555;
                border-radius: 6px;
                color: #ffffff;
                font-family: 'Courier New', monospace;
                padding: 10px;
            }
        """)
        
        if plan:
            total_symbols = plan['total_symbols']
            need_full = len(plan['symbols_needing_full_fetch'])
            need_update = len(plan['symbols_needing_update'])
            up_to_date = len(plan['symbols_up_to_date'])
            
            if need_full == 0 and need_update == 0:
                plan_content = f"✅ All {total_symbols} symbols are up to date!\n\nNo updates needed."
            else:
                plan_content = f"Update Plan for {total_symbols} symbols:\n\n"
                if need_full > 0:
                    plan_content += f"📥 {need_full} symbols need FULL data fetch\n"
                    plan_content += "   (No existing data)\n\n"
                if need_update > 0:
                    plan_content += f"🔄 {need_update} symbols need INCREMENTAL update\n"
                    plan_content += "   (Recent data only)\n\n"
                if up_to_date > 0:
                    plan_content += f"✅ {up_to_date} symbols are already up to date\n\n"
                plan_content += "Recommendation:\n"
                plan_content += "• Use 'Update Data' for incremental update\n"
                plan_content += "• Use 'Full Refresh' only if rebuilding database"
        else:
            plan_content = "No plan data available."
            
        plan_text.setPlainText(plan_content)
        layout.addWidget(plan_text)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #3daee9;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
                color: #ffffff;
            }
            QPushButton:hover {
                background-color: #2e96d6;
            }
        """)
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)
