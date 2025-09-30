"""
Interactive stock chart widget with simple dropdown arrows
"""

import sys
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QComboBox, QLabel
from PySide6.QtCore import Qt
import pandas as pd
import numpy as np

try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
    from matplotlib.figure import Figure
    from matplotlib.dates import DateFormatter
    import matplotlib.dates as mdates
    from datetime import datetime, timedelta
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    print("Matplotlib not available. Chart functionality will be limited.")
    MATPLOTLIB_AVAILABLE = False

class CompactNavigationToolbar(NavigationToolbar):
    """Custom compact navigation toolbar"""
    
    def __init__(self, canvas, parent):
        super().__init__(canvas, parent)
        
        # Remove text labels and make buttons smaller
        for action in self.actions():
            if action.text():
                action.setText("")
        
        # Set smaller icon size
        self.setIconSize(self.iconSize() * 0.5)
        
        # Remove some buttons we don't need
        unwanted = ['Subplots', 'Customize']
        for action in self.actions():
            if action.toolTip() in unwanted:
                self.removeAction(action)

class StockChart(QWidget):
    """Interactive stock chart with simple dropdowns"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_data = pd.DataFrame()
        self.current_ticker = ""
        self.chart_type = "candlestick"
        
        if MATPLOTLIB_AVAILABLE:
            self.setup_ui()
        else:
            self.setup_fallback_ui()
    
    def setup_ui(self):
        """Setup chart UI with compact toolbar"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)
        
        # Chart controls
        self.setup_chart_controls(layout)
        
        # Create horizontal layout for chart and toolbar
        chart_layout = QHBoxLayout()
        chart_layout.setSpacing(8)
        
        # Create matplotlib figure and canvas
        self.figure = Figure(figsize=(14, 7), facecolor='#1a1d22')
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setStyleSheet("background-color: #1a1d22; border: 2px solid #4a5468; border-radius: 8px;")
        
        # Create compact navigation toolbar
        self.toolbar = CompactNavigationToolbar(self.canvas, self)
        self.toolbar.setOrientation(Qt.Vertical)
        self.toolbar.setStyleSheet("""
            QToolBar {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                           stop:0 #3a4558, stop:1 #2d3441);
                border: 1px solid #4a5468;
                border-radius: 4px;
                spacing: 1px;
                padding: 2px;
                max-width: 28px;
            }
            QToolBar QToolButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                           stop:0 #4a5468, stop:1 #3a4558);
                border: 1px solid #5a6478;
                border-radius: 2px;
                padding: 2px;
                margin: 1px;
                color: #ffffff;
                max-width: 20px;
                max-height: 20px;
                min-width: 20px;
                min-height: 20px;
            }
            QToolBar QToolButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                           stop:0 #0570d8, stop:1 #0466c8);
            }
            QToolBar QToolButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                           stop:0 #0352a0, stop:1 #0466c8);
            }
        """)
        
        # Create subplot
        self.ax = self.figure.add_subplot(111, facecolor='#1a1d22')
        
        # Style the plot
        self.style_plot()
        
        # Add canvas and toolbar to horizontal layout
        chart_layout.addWidget(self.canvas)
        chart_layout.addWidget(self.toolbar)
        
        layout.addLayout(chart_layout)
        
        # Show empty chart initially
        self.show_empty_chart()
        
    def setup_fallback_ui(self):
        """Setup fallback UI when matplotlib is not available"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        
        fallback_label = QLabel("Chart Widget\n\nMatplotlib not installed.\nRun: pip install matplotlib")
        fallback_label.setAlignment(Qt.AlignCenter)
        fallback_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                color: #979dac;
                background-color: #2d3441;
                border: 2px solid #4a5468;
                border-radius: 12px;
                padding: 40px;
            }
        """)
        layout.addWidget(fallback_label)
    
    def setup_chart_controls(self, layout):
        """Setup compact chart controls"""
        controls_frame = QWidget()
        controls_layout = QHBoxLayout(controls_frame)
        controls_layout.setContentsMargins(0, 0, 0, 0)
        controls_layout.setSpacing(12)
        
        # Chart type selector
        type_label = QLabel("Chart:")
        type_label.setStyleSheet("color: #ffffff; font-weight: 600; font-size: 12px;")
        controls_layout.addWidget(type_label)
        
        self.chart_type_combo = QComboBox()
        self.chart_type_combo.addItems(["Candlestick", "Line", "Area"])
        self.chart_type_combo.setMinimumWidth(120)
        self.chart_type_combo.setMaximumWidth(140)
        self.chart_type_combo.setStyleSheet("""
            QComboBox {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                           stop:0 #3a4558, stop:1 #2d3441);
                border: 1px solid #4a5468;
                border-radius: 6px;
                padding: 8px 20px 8px 10px;
                color: #ffffff;
                font-weight: 600;
                font-size: 12px;
                min-height: 18px;
            }
            QComboBox:hover {
                border-color: #0466c8;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                           stop:0 #4a5468, stop:1 #3a4558);
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 18px;
                border: none;
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
                min-height: 18px;
            }
            QComboBox QAbstractItemView::item:hover {
                background-color: #3a4558;
            }
        """)
        self.chart_type_combo.currentTextChanged.connect(self.on_chart_type_changed)
        controls_layout.addWidget(self.chart_type_combo)
        
        # Time period selector
        period_label = QLabel("Period:")
        period_label.setStyleSheet("color: #ffffff; font-weight: 600; font-size: 12px;")
        controls_layout.addWidget(period_label)
        
        self.period_combo = QComboBox()
        self.period_combo.addItems(["1M", "3M", "6M", "1Y", "2Y", "All"])
        self.period_combo.setCurrentText("1Y")
        self.period_combo.setMinimumWidth(70)
        self.period_combo.setMaximumWidth(80)
        self.period_combo.setStyleSheet("""
            QComboBox {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                           stop:0 #3a4558, stop:1 #2d3441);
                border: 1px solid #4a5468;
                border-radius: 6px;
                padding: 8px 18px 8px 10px;
                color: #ffffff;
                font-weight: 600;
                font-size: 12px;
                min-height: 18px;
            }
            QComboBox:hover {
                border-color: #0466c8;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                           stop:0 #4a5468, stop:1 #3a4558);
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 16px;
                border: none;
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
                min-height: 18px;
            }
            QComboBox QAbstractItemView::item:hover {
                background-color: #3a4558;
            }
        """)
        self.period_combo.currentTextChanged.connect(self.on_period_changed)
        controls_layout.addWidget(self.period_combo)
        
        controls_layout.addStretch()
        
        # Current ticker label
        self.ticker_label = QLabel("Select a ticker from table")
        self.ticker_label.setStyleSheet("""
            QLabel {
                color: #979dac;
                font-size: 11px;
                font-weight: 500;
            }
        """)
        controls_layout.addWidget(self.ticker_label)
        
        layout.addWidget(controls_frame)
    
    def style_plot(self):
        """Apply dark theme styling to matplotlib plot"""
        # Set background colors
        self.ax.set_facecolor('#1a1d22')
        self.figure.patch.set_facecolor('#1a1d22')
        
        # Style axes
        self.ax.spines['bottom'].set_color('#4a5468')
        self.ax.spines['top'].set_color('#4a5468')
        self.ax.spines['left'].set_color('#4a5468')
        self.ax.spines['right'].set_color('#4a5468')
        
        # Style ticks and labels
        self.ax.tick_params(colors='#ffffff', which='both')
        self.ax.xaxis.label.set_color('#ffffff')
        self.ax.yaxis.label.set_color('#ffffff')
        
        # Grid
        self.ax.grid(True, alpha=0.3, color='#4a5468')
        
        # Use tight layout
        self.figure.tight_layout(pad=1.0)
        
    def show_empty_chart(self):
        """Show empty chart with message"""
        self.ax.clear()
        self.style_plot()
        
        self.ax.text(0.5, 0.5, 'Select a ticker to view chart', 
                    transform=self.ax.transAxes, 
                    ha='center', va='center', 
                    fontsize=16, color='#979dac')
        
        self.ax.set_xlim(0, 1)
        self.ax.set_ylim(0, 1)
        self.canvas.draw()
    
    def update_chart(self, data, ticker):
        """Update chart with new data"""
        if not MATPLOTLIB_AVAILABLE:
            return
            
        self.current_data = data
        self.current_ticker = ticker
        
        if data is None or data.empty or not ticker:
            self.show_empty_chart()
            self.ticker_label.setText("Select a ticker from table")
            return
        
        # Validate required columns
        required_cols = ['date', 'open', 'high', 'low', 'close']
        missing_cols = [col for col in required_cols if col not in data.columns]
        if missing_cols:
            self.show_error_chart(f"Missing columns: {', '.join(missing_cols)}")
            return
        
        # Filter data for selected period
        filtered_data = self.filter_data_by_period(data)
        
        if filtered_data.empty:
            self.show_empty_chart()
            self.ticker_label.setText(f"{ticker} - No data for selected period")
            return
        
        # Update ticker label
        date_range = f"{filtered_data['date'].min().strftime('%b %y')} to {filtered_data['date'].max().strftime('%b %y')}"
        self.ticker_label.setText(f"{ticker} • {len(filtered_data)} records • {date_range}")
        
        # Plot based on chart type
        chart_type = self.chart_type_combo.currentText().lower()
        
        try:
            if chart_type == "candlestick":
                self.plot_candlestick(filtered_data, ticker)
            elif chart_type == "line":
                self.plot_line(filtered_data, ticker)
            elif chart_type == "area":
                self.plot_area(filtered_data, ticker)
        except Exception as e:
            print(f"Chart plotting error: {e}")
            self.show_error_chart(f"Error plotting {ticker}")
    
    def filter_data_by_period(self, data):
        """Filter data based on selected time period"""
        if data.empty:
            return data
            
        period = self.period_combo.currentText()
        end_date = data['date'].max()
        
        if period == "All":
            return data
        elif period == "1M":
            start_date = end_date - timedelta(days=30)
        elif period == "3M":
            start_date = end_date - timedelta(days=90)
        elif period == "6M":
            start_date = end_date - timedelta(days=180)
        elif period == "1Y":
            start_date = end_date - timedelta(days=365)
        elif period == "2Y":
            start_date = end_date - timedelta(days=730)
        else:
            return data
            
        return data[data['date'] >= start_date]
    
    def format_dates_smartly(self, data):
        """Format x-axis dates without problematic locator_params"""
        if data.empty:
            return
            
        # Calculate time span
        time_span = (data['date'].max() - data['date'].min()).days
        
        if time_span <= 30:  # 1 month or less
            self.ax.xaxis.set_major_formatter(DateFormatter('%d %b'))
            self.ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
        elif time_span <= 90:  # 3 months or less
            self.ax.xaxis.set_major_formatter(DateFormatter('%d %b'))
            self.ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=2))
        elif time_span <= 365:  # 1 year or less
            self.ax.xaxis.set_major_formatter(DateFormatter('%b %y'))
            self.ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
        elif time_span <= 1095:  # 3 years or less
            self.ax.xaxis.set_major_formatter(DateFormatter('%Y'))
            self.ax.xaxis.set_major_locator(mdates.YearLocator())
        else:  # More than 3 years - show only years with wider spacing
            self.ax.xaxis.set_major_formatter(DateFormatter('%Y'))
            if time_span > 36500:  # More than 100 years
                self.ax.xaxis.set_major_locator(mdates.YearLocator(base=10))
            elif time_span > 18250:  # More than 50 years
                self.ax.xaxis.set_major_locator(mdates.YearLocator(base=5))
            elif time_span > 7300:  # More than 20 years
                self.ax.xaxis.set_major_locator(mdates.YearLocator(base=2))
            else:
                self.ax.xaxis.set_major_locator(mdates.YearLocator())
        
        # Manually limit ticks if too many
        max_ticks = 8
        locs = self.ax.get_xticks()
        if len(locs) > max_ticks:
            step = len(locs) // max_ticks
            self.ax.set_xticks(locs[::step])
    
    def plot_candlestick(self, data, ticker):
        """Plot candlestick chart"""
        self.ax.clear()
        self.style_plot()
        
        # Sort by date
        data = data.sort_values('date')
        
        # Sample data for performance
        if len(data) > 1000:
            step = len(data) // 1000
            data = data.iloc[::step]
        
        # Create candlestick-like plot
        for _, row in data.iterrows():
            date = row['date']
            open_price = row['open']
            high_price = row['high']
            low_price = row['low']
            close_price = row['close']
            
            # Skip if any price is NaN
            if pd.isna(open_price) or pd.isna(high_price) or pd.isna(low_price) or pd.isna(close_price):
                continue
            
            # Color: green if close > open, red otherwise
            color = '#28a745' if close_price >= open_price else '#dc3545'
            
            # Draw high-low line
            self.ax.plot([date, date], [low_price, high_price], color=color, linewidth=1, alpha=0.8)
            
            # Draw body
            body_height = abs(close_price - open_price)
            if body_height > 0:
                self.ax.plot([date, date], [min(open_price, close_price), max(open_price, close_price)], 
                           color=color, linewidth=3, alpha=0.9, solid_capstyle='butt')
        
        # Format dates
        self.format_dates_smartly(data)
        
        # Rotate x-axis labels
        plt.setp(self.ax.xaxis.get_majorticklabels(), rotation=45, ha='right', fontsize=9)
        
        # Labels
        self.ax.set_title(f'{ticker} - Candlestick Chart', color='#ffffff', fontsize=11, pad=10)
        self.ax.set_ylabel('Price (₹)', color='#ffffff')
        
        # Format y-axis
        self.ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'₹{x:.0f}'))
        
        self.figure.tight_layout(pad=1.0)
        self.canvas.draw()
    
    def plot_line(self, data, ticker):
        """Plot line chart"""
        self.ax.clear()
        self.style_plot()
        
        data = data.sort_values('date')
        
        # Sample data for performance
        if len(data) > 2000:
            step = len(data) // 2000
            data = data.iloc[::step]
        
        # Plot close price line
        self.ax.plot(data['date'], data['close'], color='#0466c8', linewidth=2, alpha=0.9)
        
        # Fill area under curve
        self.ax.fill_between(data['date'], data['close'], alpha=0.2, color='#0466c8')
        
        # Format dates
        self.format_dates_smartly(data)
        plt.setp(self.ax.xaxis.get_majorticklabels(), rotation=45, ha='right', fontsize=9)
        
        # Labels
        self.ax.set_title(f'{ticker} - Close Price', color='#ffffff', fontsize=11, pad=10)
        self.ax.set_ylabel('Price (₹)', color='#ffffff')
        
        # Format y-axis
        self.ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'₹{x:.0f}'))
        
        self.figure.tight_layout(pad=1.0)
        self.canvas.draw()
    
    def plot_area(self, data, ticker):
        """Plot area chart"""
        self.ax.clear()
        self.style_plot()
        
        data = data.sort_values('date')
        
        # Sample data for performance
        if len(data) > 2000:
            step = len(data) // 2000
            data = data.iloc[::step]
        
        # Plot area chart
        self.ax.fill_between(data['date'], data['close'], alpha=0.6, color='#28a745')
        self.ax.plot(data['date'], data['close'], color='#ffffff', linewidth=1, alpha=0.8)
        
        # Format dates
        self.format_dates_smartly(data)
        plt.setp(self.ax.xaxis.get_majorticklabels(), rotation=45, ha='right', fontsize=9)
        
        # Labels
        self.ax.set_title(f'{ticker} - Area Chart', color='#ffffff', fontsize=11, pad=10)
        self.ax.set_ylabel('Price (₹)', color='#ffffff')
        
        # Format y-axis
        self.ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'₹{x:.0f}'))
        
        self.figure.tight_layout(pad=1.0)
        self.canvas.draw()
    
    def show_error_chart(self, message):
        """Show error message in chart"""
        self.ax.clear()
        self.style_plot()
        
        self.ax.text(0.5, 0.5, f'Error: {message}', 
                    transform=self.ax.transAxes, 
                    ha='center', va='center', 
                    fontsize=14, color='#dc3545')
        
        self.canvas.draw()
    
    def on_chart_type_changed(self, chart_type):
        """Handle chart type change"""
        if self.current_data is not None and not self.current_data.empty:
            self.update_chart(self.current_data, self.current_ticker)
    
    def on_period_changed(self, period):
        """Handle time period change"""
        if self.current_data is not None and not self.current_data.empty:
            self.update_chart(self.current_data, self.current_ticker)
