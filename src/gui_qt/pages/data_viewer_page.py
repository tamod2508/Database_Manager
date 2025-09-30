"""
Enhanced data viewer page - filters at top, chart and table below
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QSplitter, QFrame, QHBoxLayout, QLabel
from PySide6.QtCore import Qt
from ..widgets.data_table_simple import DataTable
from ..widgets.stock_chart import StockChart

class DataViewerPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_data = None
        self.filter_widget = None
        self.setup_ui()
        
    def setup_ui(self):
        """Setup layout with filters at top"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)
        
        # Create filter frame at top
        self.filter_frame = QFrame()
        self.filter_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                           stop:0 #3a4558, stop:1 #2d3441);
                border: 2px solid #4a5468;
                border-radius: 12px;
                margin: 2px 4px 8px 4px;
            }
        """)
        self.filter_frame.setFixedHeight(80)
        
        # Create layout for filter frame
        self.filter_layout = QHBoxLayout(self.filter_frame)
        self.filter_layout.setContentsMargins(12, 8, 12, 8)
        
        # Add placeholder text initially
        placeholder_label = QLabel("Loading stock filters...")
        placeholder_label.setStyleSheet("color: #979dac; font-size: 12px;")
        self.filter_layout.addWidget(placeholder_label)
        
        layout.addWidget(self.filter_frame)
        
        # Create splitter for chart and table
        splitter = QSplitter(Qt.Vertical)
        splitter.setStyleSheet("""
            QSplitter::handle {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                           stop:0 #4a5468, stop:1 #3a4558);
                border-radius: 3px;
                margin: 1px;
                height: 6px;
            }
            QSplitter::handle:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                           stop:0 #0570d8, stop:1 #0466c8);
            }
        """)
        
        # Create chart and table
        self.stock_chart = StockChart()
        self.data_table = DataTable()
        
        # Connect signals
        self.data_table.selection_changed.connect(self.on_stock_selected)
        self.data_table.filter_controls_needed.connect(self.add_filter_controls)
        
        # Add to splitter
        splitter.addWidget(self.stock_chart)
        splitter.addWidget(self.data_table)
        
        # Set proportions - chart dominates
        splitter.setSizes([700, 150])
        splitter.setStretchFactor(0, 4)
        splitter.setStretchFactor(1, 1)
        
        layout.addWidget(splitter)
        
    def add_filter_controls(self, filter_widget):
        """Add filter controls to the top frame"""
        # Clear existing content
        for i in reversed(range(self.filter_layout.count())):
            child = self.filter_layout.itemAt(i).widget()
            if child:
                child.setParent(None)
        
        # Add the new filter widget
        self.filter_widget = filter_widget
        self.filter_layout.addWidget(filter_widget)
        
        print("✅ Filter controls added to top of page")
        
    def update_data(self, data):
        """Update both table and chart with new data"""
        self.current_data = data
        
        try:
            if hasattr(self, 'data_table') and self.data_table:
                self.data_table.update_data(data)
                print(f"✅ Data updated: {len(data) if data is not None else 0} records")
        except Exception as e:
            print(f"Warning: Could not update data table: {e}")
        
    def on_stock_selected(self, ticker):
        """Handle stock selection"""
        if not ticker or self.current_data is None or self.current_data.empty:
            return
            
        try:
            ticker_data = self.current_data[self.current_data['ticker'] == ticker].copy()
            
            if not ticker_data.empty and hasattr(self, 'stock_chart'):
                self.stock_chart.update_chart(ticker_data, ticker)
                print(f"Updated chart for: {ticker} ({len(ticker_data)} records)")
            else:
                print(f"No data found for ticker: {ticker}")
        except Exception as e:
            print(f"Warning: Could not update chart: {e}")
