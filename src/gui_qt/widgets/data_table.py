"""
Data table widget with separated filter controls
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QComboBox, 
    QLabel, QCheckBox, QTreeWidget, QTreeWidgetItem,
    QPushButton
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
import pandas as pd

def is_widget_deleted(widget):
    """Check if widget is deleted or invalid"""
    if widget is None:
        return True
    try:
        widget.isVisible()
        return False
    except RuntimeError:
        return True


class DataTable(QWidget):
    """Data table with separated filter controls"""
    
    # Signals
    selection_changed = Signal(str)  # Emits selected ticker
    filter_controls_needed = Signal(object)  # Emits filter widget
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_data = pd.DataFrame()
        self.ticker_combo = None
        self.show_all_var = None
        self.setup_ui()
        
    def setup_ui(self):
        """Setup table without filter controls (they go to top of page)"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)
        
        # Create and emit filter controls for top of page
        self.create_filter_controls()
        
        # Tree widget only
        self.setup_tree(layout)
        
        # Info label
        self.setup_info(layout)
        
    def create_filter_controls(self):
        """Create filter controls to be placed at top of page"""
        filter_widget = QWidget()
        filter_layout = QHBoxLayout(filter_widget)
        filter_layout.setContentsMargins(0, 0, 0, 0)
        filter_layout.setSpacing(16)
        
        # Ticker selection
        ticker_label = QLabel("📊 Select Stock:")
        ticker_label.setStyleSheet("font-weight: 700; color: #ffffff; font-size: 14px;")
        filter_layout.addWidget(ticker_label)
        
        self.ticker_combo = QComboBox()
        self.ticker_combo.setMinimumWidth(200)
        self.ticker_combo.setStyleSheet("""
            QComboBox {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                           stop:0 #3a4558, stop:1 #2d3441);
                border: 1px solid #4a5468;
                border-radius: 8px;
                padding: 8px 12px;
                color: #ffffff;
                font-weight: 600;
                font-size: 13px;
            }
            QComboBox:hover {
                border-color: #0466c8;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox QAbstractItemView {
                background-color: #2d3441;
                color: #ffffff;
                selection-background-color: #0466c8;
                border: 1px solid #4a5468;
            }
        """)
        self.ticker_combo.currentTextChanged.connect(self.on_ticker_changed)
        filter_layout.addWidget(self.ticker_combo)
        
        # Show all data checkbox
        self.show_all_var = QCheckBox("Show all records")
        self.show_all_var.setStyleSheet("""
            QCheckBox {
                color: #ffffff;
                font-weight: 600;
                font-size: 13px;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border-radius: 3px;
                border: 2px solid #4a5468;
                background-color: #2d3441;
            }
            QCheckBox::indicator:checked {
                background-color: #0466c8;
                border-color: #0466c8;
            }
        """)
        self.show_all_var.stateChanged.connect(self.on_show_all_changed)
        filter_layout.addWidget(self.show_all_var)
        
        filter_layout.addStretch()
        
        # Emit this widget to be placed at top of page
        self.filter_controls_needed.emit(filter_widget)
        
    def setup_tree(self, layout):
        """Setup tree widget"""
        # Create tree widget with columns
        columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(columns)
        self.tree.setRootIsDecorated(False)
        self.tree.setAlternatingRowColors(True)
        self.tree.setSortingEnabled(True)
        
        # Style the tree
        self.tree.setStyleSheet("""
            QTreeWidget {
                background-color: #141720;
                alternate-background-color: #1a1d22;
                color: #ffffff;
                border: 2px solid #4a5468;
                border-radius: 12px;
                font-size: 12px;
                gridline-color: #3a4558;
            }
            QTreeWidget::item {
                padding: 6px;
                border-bottom: 1px solid #2d3441;
            }
            QTreeWidget::item:selected {
                background-color: #0466c8;
                color: #ffffff;
            }
            QTreeWidget::item:hover {
                background-color: #3a4558;
            }
            QHeaderView::section {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                           stop:0 #3a4558, stop:1 #2d3441);
                border: 1px solid #4a5468;
                padding: 8px;
                font-weight: 700;
                color: #ffffff;
            }
            QHeaderView::section:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                           stop:0 #4a5468, stop:1 #3a4558);
            }
        """)
        
        # Set column widths
        self.tree.setColumnWidth(0, 120)  # Date
        self.tree.setColumnWidth(1, 100)  # Open
        self.tree.setColumnWidth(2, 100)  # High
        self.tree.setColumnWidth(3, 100)  # Low
        self.tree.setColumnWidth(4, 100)  # Close
        self.tree.setColumnWidth(5, 120)  # Volume
        
        # Connect selection
        self.tree.itemSelectionChanged.connect(self.on_selection_changed)
        
        layout.addWidget(self.tree)
        
    def setup_info(self, layout):
        """Setup info panel"""
        info_frame = QWidget()
        info_layout = QHBoxLayout(info_frame)
        info_layout.setContentsMargins(0, 0, 0, 0)
        
        self.status_label = QLabel("Select a stock to view data...")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #979dac;
                font-size: 11px;
                font-weight: 500;
            }
        """)
        info_layout.addWidget(self.status_label)
        
        info_layout.addStretch()
        
        layout.addWidget(info_frame)
    
    def update_data(self, data):
        """Update table with new data - with widget safety checks"""
        if data is None or data.empty:
            self.current_data = pd.DataFrame()
            # Check if widgets still exist before accessing
            try:
                if self.ticker_combo and not is_widget_deleted(self.ticker_combo):
                    self.ticker_combo.clear()
                if hasattr(self, 'tree') and self.tree and not is_widget_deleted(self.tree):
                    self.tree.clear()
            except (RuntimeError, AttributeError):
                pass  # Widget already deleted
            return
        
        self.current_data = data.copy()
        
        # Update ticker combo with safety checks
        if not data.empty and 'ticker' in data.columns:
            tickers = sorted(data['ticker'].unique())
            try:
                if self.ticker_combo and not is_widget_deleted(self.ticker_combo):
                    self.ticker_combo.clear()
                    self.ticker_combo.addItems([''] + tickers)
            except (RuntimeError, AttributeError):
                pass  # Widget already deleted
        
        # Update tree view
        self.update_tree_view()
        
    def update_tree_view(self):
        """Update tree view with selected ticker data - with widget safety"""
        # Clear existing items with safety check
        try:
            if hasattr(self, 'tree') and self.tree and not is_widget_deleted(self.tree):
                self.tree.clear()
            else:
                return  # Tree widget not available
        except (RuntimeError, AttributeError):
            return  # Tree widget already deleted
        
        # Get selected ticker with safety check
        ticker = ""
        try:
            if self.ticker_combo and not is_widget_deleted(self.ticker_combo):
                ticker = self.ticker_combo.currentText()
        except (RuntimeError, AttributeError):
            pass  # Combo box not available
            
        if not ticker or self.current_data.empty:
            try:
                if hasattr(self, 'status_label') and self.status_label and not is_widget_deleted(self.status_label):
                    self.status_label.setText("Select a stock to view data...")
            except (RuntimeError, AttributeError):
                pass
            return
        
        # Filter data by ticker
        ticker_data = self.current_data[self.current_data['ticker'] == ticker].copy()
        if ticker_data.empty:
            return
            
        # Sort by date (newest first)
        ticker_data = ticker_data.sort_values('date', ascending=False)
        
        # Determine how many records to show
        show_all = self.show_all_var.isChecked() if self.show_all_var else False
        if show_all:
            display_data = ticker_data
            limit_text = "all"
        else:
            display_data = ticker_data.head(2000)
            limit_text = "latest 2000"
        
        # Add items to tree
        for _, row in display_data.iterrows():
            item = QTreeWidgetItem()
            
            try:
                # Date
                date_str = row['date'].strftime('%Y-%m-%d') if pd.notna(row['date']) else ''
                item.setText(0, date_str)
                
                # OHLC prices
                for i, col in enumerate(['open', 'high', 'low', 'close'], 1):
                    if pd.notna(row[col]):
                        item.setText(i, f"₹{float(row[col]):.2f}")
                    else:
                        item.setText(i, '')
                
                # Volume
                if pd.notna(row['volume']):
                    vol = int(float(row['volume']))
                    if vol >= 10000000:
                        vol_str = f"{vol/10000000:.1f}Cr"
                    elif vol >= 100000:
                        vol_str = f"{vol/100000:.1f}L"
                    else:
                        vol_str = f"{vol:,}"
                    item.setText(5, vol_str)
                else:
                    item.setText(5, '')
                
                # Set alignment
                for i in range(1, 6):
                    item.setTextAlignment(i, Qt.AlignRight | Qt.AlignVCenter)
                
                self.tree.addTopLevelItem(item)
                
            except Exception as e:
                print(f"Error adding item: {e}")
                continue
        
        # Update status
        date_range = f"{ticker_data['date'].min().date()} to {ticker_data['date'].max().date()}"
        self.status_label.setText(
            f"{ticker}: {len(ticker_data):,} total records ({date_range}) - showing {limit_text}"
        )
    
    def on_ticker_changed(self, ticker):
        """Handle ticker selection change - with safety checks"""
        try:
            self.update_tree_view()
            if ticker and ticker.strip():
                self.selection_changed.emit(ticker)
        except (RuntimeError, AttributeError):
            pass  # Widget already deleted
    
    def on_show_all_changed(self):
        """Handle show all checkbox change"""
        self.update_tree_view()
        
    def on_selection_changed(self):
        """Handle tree item selection"""
        pass
