"""
Compact data table widget with simple text arrow dropdowns
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QComboBox, 
    QLabel, QCheckBox, QTreeWidget, QTreeWidgetItem
)
from PySide6.QtCore import Qt, Signal, QTimer
import pandas as pd

class DataTable(QWidget):
    """Compact data table with simplified styling"""
    
    selection_changed = Signal(str)
    filter_controls_needed = Signal(object)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_data = pd.DataFrame()
        self.ticker_combo = None
        self.show_all_var = None
        self.tree = None
        self.status_label = None
        self.filter_widget = None
        self.is_initializing = False
        
        # Use timer to delay initialization
        QTimer.singleShot(100, self.delayed_setup)
        
    def delayed_setup(self):
        """Delayed setup to ensure parent widget is ready"""
        if not self.is_initializing:
            self.is_initializing = True
            self.setup_ui()
        
    def setup_ui(self):
        """Setup compact table UI"""
        try:
            layout = QVBoxLayout(self)
            layout.setContentsMargins(8, 8, 8, 8)
            layout.setSpacing(8)
            
            # Create compact filter controls
            self.create_filter_controls()
            
            # Tree widget
            self.setup_tree(layout)
            
            # Info label
            self.setup_info(layout)
            
        except Exception as e:
            print(f"Error in setup_ui: {e}")
        
    def create_filter_controls(self):
        """Create compact filter controls"""
        try:
            self.filter_widget = QWidget()
            filter_layout = QHBoxLayout(self.filter_widget)
            filter_layout.setContentsMargins(16, 12, 16, 12)
            filter_layout.setSpacing(16)
            
            # Compact stock label
            ticker_label = QLabel("Stock:")
            ticker_label.setStyleSheet("""
                QLabel {
                    font-weight: 700; 
                    color: #ffffff; 
                    font-size: 13px;
                    min-width: 45px;
                }
            """)
            filter_layout.addWidget(ticker_label)
            
            # Compact combo box with simple arrow
            self.ticker_combo = QComboBox(self.filter_widget)
            self.ticker_combo.setMinimumWidth(150)
            self.ticker_combo.setMaximumWidth(200)
            self.ticker_combo.setStyleSheet("""
                QComboBox {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                               stop:0 #3a4558, stop:1 #2d3441);
                    border: 1px solid #4a5468;
                    border-radius: 6px;
                    padding: 6px 20px 6px 10px;
                    color: #ffffff;
                    font-weight: 600;
                    font-size: 12px;
                    min-height: 16px;
                }
                QComboBox:hover {
                    border-color: #0466c8;
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                               stop:0 #4a5468, stop:1 #3a4558);
                }
                QComboBox:focus {
                    border-color: #0466c8;
                    outline: none;
                }
                QComboBox::drop-down {
                    subcontrol-origin: padding;
                    subcontrol-position: top right;
                    width: 16px;
                    border: none;
                    padding-right: 2px;
                }
                QComboBox::down-arrow {
                    width: 12px;
                    height: 12px;
                    background: none;
                    border: none;
                }
                QComboBox::down-arrow:after {
                    content: "▼";
                    color: #ffffff;
                    font-size: 8px;
                }
                QComboBox QAbstractItemView {
                    background-color: #2d3441;
                    color: #ffffff;
                    selection-background-color: #0466c8;
                    border: 1px solid #4a5468;
                    border-radius: 4px;
                    outline: none;
                }
                QComboBox QAbstractItemView::item {
                    padding: 6px 10px;
                    border-bottom: 1px solid #3a4558;
                    min-height: 20px;
                }
                QComboBox QAbstractItemView::item:hover {
                    background-color: #3a4558;
                }
            """)
            
            try:
                self.ticker_combo.currentTextChanged.connect(self.on_ticker_changed)
            except Exception as e:
                print(f"Error connecting ticker combo signal: {e}")
                
            filter_layout.addWidget(self.ticker_combo)
            
            # Compact checkbox
            self.show_all_var = QCheckBox("Show all", self.filter_widget)
            self.show_all_var.setStyleSheet("""
                QCheckBox {
                    color: #ffffff;
                    font-weight: 600;
                    font-size: 12px;
                    spacing: 6px;
                }
                QCheckBox::indicator {
                    width: 14px;
                    height: 14px;
                    border-radius: 3px;
                    border: 2px solid #4a5468;
                    background-color: #2d3441;
                }
                QCheckBox::indicator:hover {
                    border-color: #0466c8;
                    background-color: #3a4558;
                }
                QCheckBox::indicator:checked {
                    background-color: #0466c8;
                    border-color: #0466c8;
                }
            """)
            
            try:
                self.show_all_var.stateChanged.connect(self.on_show_all_changed)
            except Exception as e:
                print(f"Error connecting checkbox signal: {e}")
                
            filter_layout.addWidget(self.show_all_var)
            
            # Add stretch to push everything to the left
            filter_layout.addStretch()
            
            # Emit filter widget
            try:
                self.filter_controls_needed.emit(self.filter_widget)
                print("✅ Compact filter controls created")
            except Exception as e:
                print(f"Error emitting filter controls: {e}")
                
        except Exception as e:
            print(f"Error creating filter controls: {e}")
        
    def setup_tree(self, layout):
        """Setup tree widget with equal column widths"""
        try:
            columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
            self.tree = QTreeWidget(self)
            self.tree.setHeaderLabels(columns)
            self.tree.setRootIsDecorated(False)
            self.tree.setAlternatingRowColors(True)
            self.tree.setSortingEnabled(True)
            
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
                    padding: 8px 4px;
                    border-bottom: 1px solid #2d3441;
                    height: 24px;
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
                    padding: 10px 8px;
                    font-weight: 700;
                    color: #ffffff;
                    font-size: 13px;
                }
                QHeaderView::section:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                               stop:0 #4a5468, stop:1 #3a4558);
                }
            """)
            
            # Set equal column widths
            column_width = 130
            for i in range(6):
                self.tree.setColumnWidth(i, column_width)
            
            # Set header to stretch last section
            header = self.tree.header()
            header.setStretchLastSection(True)
            
            layout.addWidget(self.tree)
            
        except Exception as e:
            print(f"Error setting up tree: {e}")
        
    def setup_info(self, layout):
        """Setup info panel"""
        try:
            self.status_label = QLabel("Select a stock to view data...", self)
            self.status_label.setStyleSheet("""
                QLabel {
                    color: #979dac;
                    font-size: 11px;
                    font-weight: 500;
                    padding: 8px;
                    background-color: transparent;
                }
            """)
            layout.addWidget(self.status_label)
        except Exception as e:
            print(f"Error setting up info: {e}")
    
    def is_widget_valid(self, widget):
        """Check if widget is valid"""
        if widget is None:
            return False
        try:
            widget.isVisible()
            return True
        except (RuntimeError, AttributeError):
            return False
    
    def safe_clear_combo(self):
        """Safely clear combo box"""
        try:
            if self.is_widget_valid(self.ticker_combo):
                self.ticker_combo.clear()
                return True
        except Exception as e:
            print(f"Error clearing combo: {e}")
        return False
    
    def safe_add_items(self, items):
        """Safely add items to combo box"""
        try:
            if self.is_widget_valid(self.ticker_combo):
                self.ticker_combo.addItems(items)
                return True
        except Exception as e:
            print(f"Error adding items: {e}")
        return False
    
    def update_data(self, data):
        """Update table with new data"""
        try:
            if data is None or data.empty:
                self.current_data = pd.DataFrame()
                self.safe_clear_combo()
                if self.is_widget_valid(self.tree):
                    self.tree.clear()
                return
            
            self.current_data = data.copy()
            
            # Update ticker combo
            if 'ticker' in data.columns:
                tickers = sorted(data['ticker'].unique())
                if self.safe_clear_combo():
                    self.safe_add_items([''] + tickers)
                    print(f"✅ Updated combo with {len(tickers)} tickers")
            
            self.update_tree_view()
            
        except Exception as e:
            print(f"Error in update_data: {e}")
        
    def update_tree_view(self):
        """Update tree view with improved formatting"""
        try:
            if not self.is_widget_valid(self.tree):
                return
                
            self.tree.clear()
            
            if not self.is_widget_valid(self.ticker_combo):
                return
                
            ticker = self.ticker_combo.currentText()
            if not ticker or self.current_data.empty:
                if self.is_widget_valid(self.status_label):
                    self.status_label.setText("Select a stock to view data...")
                return
            
            # Filter and display data
            ticker_data = self.current_data[self.current_data['ticker'] == ticker].copy()
            if ticker_data.empty:
                return
                
            ticker_data = ticker_data.sort_values('date', ascending=False)
            
            # Show data
            show_all = False
            if self.is_widget_valid(self.show_all_var):
                show_all = self.show_all_var.isChecked()
                
            display_data = ticker_data if show_all else ticker_data.head(2000)
            
            # Add items to tree with better formatting
            for _, row in display_data.iterrows():
                try:
                    item = QTreeWidgetItem()
                    
                    # Date - shorter format
                    date_str = row['date'].strftime('%d-%m-%y') if pd.notna(row['date']) else ''
                    item.setText(0, date_str)
                    
                    # Prices - compact format
                    for i, col in enumerate(['open', 'high', 'low', 'close'], 1):
                        if pd.notna(row[col]):
                            price = float(row[col])
                            if price >= 1000:
                                item.setText(i, f"₹{price:.0f}")
                            else:
                                item.setText(i, f"₹{price:.2f}")
                        else:
                            item.setText(i, '-')
                    
                    # Volume - compact format
                    if pd.notna(row['volume']):
                        vol = int(float(row['volume']))
                        if vol >= 10000000:
                            vol_str = f"{vol/10000000:.1f}Cr"
                        elif vol >= 100000:
                            vol_str = f"{vol/100000:.0f}L"
                        elif vol >= 1000:
                            vol_str = f"{vol/1000:.0f}K"
                        else:
                            vol_str = f"{vol}"
                        item.setText(5, vol_str)
                    else:
                        item.setText(5, '-')
                    
                    # Align numbers right, date center
                    item.setTextAlignment(0, Qt.AlignCenter)
                    for i in range(1, 6):
                        item.setTextAlignment(i, Qt.AlignRight | Qt.AlignVCenter)
                    
                    self.tree.addTopLevelItem(item)
                    
                except Exception as e:
                    print(f"Error adding tree item: {e}")
                    continue
            
            # Update status
            if self.is_widget_valid(self.status_label):
                total = len(ticker_data)
                showing = len(display_data)
                limit_text = "all" if show_all else f"latest {showing:,}"
                self.status_label.setText(f"{ticker}: {total:,} total records - showing {limit_text}")
                
        except Exception as e:
            print(f"Error in update_tree_view: {e}")
    
    def on_ticker_changed(self, ticker):
        """Handle ticker change"""
        try:
            self.update_tree_view()
            if ticker and ticker.strip():
                self.selection_changed.emit(ticker)
        except Exception as e:
            print(f"Error in ticker changed: {e}")
    
    def on_show_all_changed(self):
        """Handle show all change"""
        try:
            self.update_tree_view()
        except Exception as e:
            print(f"Error in show all changed: {e}")
