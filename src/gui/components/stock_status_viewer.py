"""
Stock-wise status viewer component for GUI
Shows data availability status for each company
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
import pandas as pd

from ...utils.logger import get_logger
from ...core.database_manager import db_manager

logger = get_logger(__name__)

class StockStatusViewer:
    """Component to display stock-wise data availability status"""
    
    def __init__(self, parent):
        self.parent = parent
        self.frame = ctk.CTkFrame(parent)
        self.status_data = pd.DataFrame()
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the status viewer UI"""
        
        # Title and controls
        header_frame = ctk.CTkFrame(self.frame)
        header_frame.pack(fill="x", padx=10, pady=10)
        
        title_label = ctk.CTkLabel(
            header_frame,
            text="Stock-wise Data Status",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title_label.pack(side="left", padx=10)
        
        # Refresh button
        refresh_btn = ctk.CTkButton(
            header_frame,
            text="Refresh Status",
            command=self.refresh_status,
            height=32,
            width=120
        )
        refresh_btn.pack(side="right", padx=10)
        
        # Summary frame
        summary_frame = ctk.CTkFrame(self.frame)
        summary_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        self.summary_label = ctk.CTkLabel(
            summary_frame,
            text="Loading status...",
            font=ctk.CTkFont(size=12)
        )
        self.summary_label.pack(padx=10, pady=10)
        
        # Table frame with scrollbar
        table_frame = ctk.CTkFrame(self.frame)
        table_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Create Treeview with columns
        columns = ('Symbol', 'Status', 'Records', 'Earliest Date', 'Latest Date', 'Date Range')
        self.tree = ttk.Treeview(
            table_frame, 
            columns=columns, 
            show='headings',
            height=20
        )
        
        # Configure columns
        self.tree.heading('Symbol', text='Symbol')
        self.tree.heading('Status', text='Status')
        self.tree.heading('Records', text='Total Records')
        self.tree.heading('Earliest Date', text='Earliest Date')
        self.tree.heading('Latest Date', text='Latest Date')
        self.tree.heading('Date Range', text='Days of Data')
        
        self.tree.column('Symbol', width=100, anchor='center')
        self.tree.column('Status', width=80, anchor='center')
        self.tree.column('Records', width=100, anchor='center')
        self.tree.column('Earliest Date', width=120, anchor='center')
        self.tree.column('Latest Date', width=120, anchor='center')
        self.tree.column('Date Range', width=100, anchor='center')
        
        # Configure tags for status colors
        self.tree.tag_configure('available', background='#E8F5E9', foreground='#2E7D32')  
        self.tree.tag_configure('missing', background='#FFEBEE', foreground='#C62828')
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack layout
        self.tree.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
        
        # Filter frame
        filter_frame = ctk.CTkFrame(self.frame)
        filter_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        ctk.CTkLabel(filter_frame, text="Filter:").pack(side="left", padx=10)
        
        self.filter_var = tk.StringVar(value="all")
        
        ctk.CTkRadioButton(
            filter_frame,
            text="All",
            variable=self.filter_var,
            value="all",
            command=self.apply_filter
        ).pack(side="left", padx=5)
        
        ctk.CTkRadioButton(
            filter_frame,
            text="Data Available",
            variable=self.filter_var,
            value="available",
            command=self.apply_filter
        ).pack(side="left", padx=5)
        
        ctk.CTkRadioButton(
            filter_frame,
            text="Missing Data",
            variable=self.filter_var,
            value="missing",
            command=self.apply_filter
        ).pack(side="left", padx=5)
    
    def refresh_status(self):
        """Refresh status data from database"""
        try:
            logger.info("Refreshing stock status data...")
            
            # Get list of all symbols from CSV
            from ...config.settings import config
            symbols_df = pd.read_csv(config.COMPANIES_CSV)
            all_symbols = symbols_df['Symbol'].tolist()
            
            # Get database stats per symbol
            status_list = []
            
            for symbol in all_symbols:
                stock_data = db_manager.get_stock_data(ticker=symbol)
                
                if not stock_data.empty:
                    earliest = stock_data['date'].min()
                    latest = stock_data['date'].max()
                    record_count = len(stock_data)
                    days_range = (latest - earliest).days
                    
                    status_list.append({
                        'symbol': symbol,
                        'has_data': True,
                        'record_count': record_count,
                        'earliest_date': earliest.strftime('%Y-%m-%d'),
                        'latest_date': latest.strftime('%Y-%m-%d'),
                        'days_range': days_range
                    })
                else:
                    status_list.append({
                        'symbol': symbol,
                        'has_data': False,
                        'record_count': 0,
                        'earliest_date': 'N/A',
                        'latest_date': 'N/A',
                        'days_range': 0
                    })
            
            self.status_data = pd.DataFrame(status_list)
            self.update_display()
            
            logger.info(f"Status refreshed for {len(all_symbols)} symbols")
            
        except Exception as e:
            logger.error(f"Failed to refresh status: {e}")
            self.summary_label.configure(text=f"Error: {e}")
    
    def update_display(self):
        """Update the display with current status data"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        if self.status_data.empty:
            self.summary_label.configure(text="No data available")
            return
        
        # Calculate summary
        total_symbols = len(self.status_data)
        symbols_with_data = len(self.status_data[self.status_data['has_data']])
        symbols_missing = total_symbols - symbols_with_data
        
        # Update summary
        summary_text = (
            f"Total Symbols: {total_symbols} | "
            f"Data Available: {symbols_with_data} | "
            f"Missing Data: {symbols_missing}"
        )
        self.summary_label.configure(text=summary_text)
        
        # Apply current filter
        self.apply_filter()
    
    def apply_filter(self):
        """Apply the selected filter to the display"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        if self.status_data.empty:
            return
        
        filter_value = self.filter_var.get()
        
        # Filter data based on selection
        if filter_value == "available":
            filtered_data = self.status_data[self.status_data['has_data']]
        elif filter_value == "missing":
            filtered_data = self.status_data[~self.status_data['has_data']]
        else:  # all
            filtered_data = self.status_data
        
        # Populate tree
        for _, row in filtered_data.iterrows():
            status_icon = "✓" if row['has_data'] else "✗"
            tag = 'available' if row['has_data'] else 'missing'
            
            values = (
                row['symbol'],
                status_icon,
                f"{row['record_count']:,}" if row['record_count'] > 0 else "-",
                row['earliest_date'],
                row['latest_date'],
                str(row['days_range']) if row['days_range'] > 0 else "-"
            )
            
            self.tree.insert('', 'end', values=values, tags=(tag,))
    
    def load_initial_data(self):
        """Load initial status data"""
        self.refresh_status()