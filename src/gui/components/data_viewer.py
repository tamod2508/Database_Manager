"""
Data viewing component - UNLIMITED VERSION
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
import pandas as pd
import logging
from typing import Optional

from ...utils.logger import get_logger
from ...core.database_manager import db_manager

logger = get_logger(__name__)

class DataViewer:
    """Unlimited data viewer component"""
    
    def __init__(self, parent):
        self.parent = parent
        self.current_data = pd.DataFrame()
        self.frame = ctk.CTkFrame(parent)
        self.setup_ui()
        
    def setup_ui(self):
        """Setup unlimited data UI"""
        
        # Controls frame
        controls_frame = ctk.CTkFrame(self.frame)
        controls_frame.pack(fill="x", padx=10, pady=10)
        
        # Ticker selection
        ctk.CTkLabel(controls_frame, text="Ticker:").pack(side="left", padx=10)
        
        self.ticker_var = tk.StringVar()
        self.ticker_combo = ctk.CTkComboBox(
            controls_frame,
            variable=self.ticker_var,
            command=self.on_ticker_change,
            width=150
        )
        self.ticker_combo.pack(side="left", padx=10)
        
        # Show all data checkbox
        self.show_all_var = tk.BooleanVar(value=False)
        self.show_all_check = ctk.CTkCheckBox(
            controls_frame,
            text="Show all data (may be slow)",
            variable=self.show_all_var,
            command=self.on_show_all_change
        )
        self.show_all_check.pack(side="left", padx=20)
        
        # Info label
        self.info_label = ctk.CTkLabel(controls_frame, text="Select a ticker to view data")
        self.info_label.pack(side="left", padx=20)
        
        # Table frame
        table_frame = ctk.CTkFrame(self.frame)
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create treeview
        columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=20)
        
        # Configure columns
        for col in columns:
            self.tree.heading(col, text=col)
            if col == 'Date':
                self.tree.column(col, width=100, anchor='center')
            elif col == 'Volume':
                self.tree.column(col, width=120, anchor='e')
            else:
                self.tree.column(col, width=80, anchor='e')
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack layout
        self.tree.pack(side="left", fill="both", expand=True)
        v_scrollbar.pack(side="right", fill="y")
        
    def update_data(self, data: pd.DataFrame):
        """Update the displayed data"""
        try:
            self.current_data = data
            
            # Update ticker combo
            if not data.empty:
                tickers = sorted(data['ticker'].unique())
                self.ticker_combo.configure(values=tickers)
                
                if tickers and not self.ticker_var.get():
                    self.ticker_var.set(tickers[0])
                    
                self.info_label.configure(text=f"Loaded {len(tickers)} tickers, {len(data):,} total records")
            
            # Update table
            self.update_table_view()
            
            logger.info(f"Data viewer updated with {len(data)} records")
            
        except Exception as e:
            logger.error(f"Failed to update data viewer: {e}")
    
    def update_table_view(self):
        """Update table view with current data - UNLIMITED VERSION"""
        try:
            # Clear existing data
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Filter data by selected ticker
            ticker = self.ticker_var.get()
            if not ticker or self.current_data.empty:
                return
            
            ticker_data = self.current_data[self.current_data['ticker'] == ticker].copy()
            ticker_data = ticker_data.sort_values('date', ascending=False)
            
            # Determine how many records to show
            show_all = self.show_all_var.get()
            if show_all:
                display_data = ticker_data  # Show ALL data
                limit_text = "all"
            else:
                display_data = ticker_data.head(2000)  # Show recent 2000
                limit_text = "latest 2000"
            
            # Add data to tree
            record_count = 0
            for _, row in display_data.iterrows():
                values = [
                    row['date'].strftime('%Y-%m-%d') if pd.notna(row['date']) else '',
                    f"{row['open']:.2f}" if pd.notna(row['open']) else '',
                    f"{row['high']:.2f}" if pd.notna(row['high']) else '',
                    f"{row['low']:.2f}" if pd.notna(row['low']) else '',
                    f"{row['close']:.2f}" if pd.notna(row['close']) else '',
                    f"{int(row['volume']):,}" if pd.notna(row['volume']) else ''
                ]
                self.tree.insert('', 'end', values=values)
                record_count += 1
                
                # Progress indicator for large datasets
                if record_count % 1000 == 0:
                    self.info_label.configure(text=f"Loading {ticker}: {record_count:,} records...")
                    self.frame.update_idletasks()
            
            # Final info update
            date_range = f"{ticker_data['date'].min().date()} to {ticker_data['date'].max().date()}"
            self.info_label.configure(
                text=f"{ticker}: {len(ticker_data):,} total records ({date_range}) - showing {limit_text}"
            )
                
        except Exception as e:
            logger.error(f"Failed to update table view: {e}")
            self.info_label.configure(text=f"Error loading data: {e}")
    
    def on_ticker_change(self, value):
        """Handle ticker selection change"""
        self.update_table_view()
    
    def on_show_all_change(self):
        """Handle show all data checkbox change"""
        self.update_table_view()
    
    def on_view_change(self, value):
        """Handle view type change - not used in this version"""
        pass
