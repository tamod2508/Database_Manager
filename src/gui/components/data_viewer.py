"""
Data viewing component - Enhanced with Missing Data Toggle
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
import pandas as pd

from ...utils.logger import get_logger

logger = get_logger(__name__)

class DataViewer:
    """Data viewer component with missing data toggle"""

    def __init__(self, parent):
        self.parent = parent
        self.current_data = pd.DataFrame()
        self.frame = ctk.CTkFrame(parent)
        self.setup_ui()

    def setup_ui(self):
        """Setup data viewer UI with missing data toggle"""

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

        # NEW: Show only missing data checkbox
        self.show_missing_var = tk.BooleanVar(value=False)
        self.show_missing_check = ctk.CTkCheckBox(
            controls_frame,
            text="Show only missing data (is_missing=TRUE)",
            variable=self.show_missing_var,
            command=self.on_show_missing_change,
            fg_color="red",
            hover_color="darkred"
        )
        self.show_missing_check.pack(side="left", padx=20)

        # Info label
        self.info_label = ctk.CTkLabel(controls_frame, text="Select a ticker to view data")
        self.info_label.pack(side="left", padx=20)

        # Table frame
        table_frame = ctk.CTkFrame(self.frame)
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Create treeview
        columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Missing']
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=20)

        # Configure columns
        for col in columns:
            self.tree.heading(col, text=col)
            if col == 'Date':
                self.tree.column(col, width=100, anchor='center')
            elif col == 'Volume':
                self.tree.column(col, width=120, anchor='e')
            elif col == 'Missing':
                self.tree.column(col, width=80, anchor='center')
            else:
                self.tree.column(col, width=80, anchor='e')

        # Configure tags for missing data highlighting
        self.tree.tag_configure('missing', background='#FFEBEE', foreground='#C62828')  # Light red
        self.tree.tag_configure('real', background='#E8F5E9', foreground='#2E7D32')     # Light green

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
        """Update table view with current data and filters"""
        try:
            # Clear existing data
            for item in self.tree.get_children():
                self.tree.delete(item)

            # Filter data by selected ticker
            ticker = self.ticker_var.get()
            if not ticker or self.current_data.empty:
                return

            ticker_data = self.current_data[self.current_data['ticker'] == ticker].copy()

            # Apply missing data filter
            show_missing_only = self.show_missing_var.get()
            if show_missing_only:
                # Filter to show only missing data (is_missing=TRUE)
                if 'is_missing' in ticker_data.columns:
                    ticker_data = ticker_data[ticker_data['is_missing']]
                else:
                    # Column doesn't exist yet, show nothing
                    self.info_label.configure(text=f"{ticker}: No is_missing column found. Run database migration.")
                    return

            ticker_data = ticker_data.sort_values('date', ascending=False)

            # Determine how many records to show
            show_all = self.show_all_var.get()
            if show_all:
                display_data = ticker_data
                limit_text = "all"
            else:
                display_data = ticker_data.head(2000)
                limit_text = "latest 2000"

            # Add data to tree
            record_count = 0
            missing_count = 0
            real_count = 0

            for _, row in display_data.iterrows():
                # Check if this is missing data
                is_missing = row.get('is_missing', False)
                tag = 'missing' if is_missing else 'real'

                if is_missing:
                    missing_count += 1
                    missing_icon = "✗"
                else:
                    real_count += 1
                    missing_icon = "✓"

                values = [
                    row['date'].strftime('%Y-%m-%d') if pd.notna(row['date']) else '',
                    f"{row['open']:.2f}" if pd.notna(row['open']) else 'NULL',
                    f"{row['high']:.2f}" if pd.notna(row['high']) else 'NULL',
                    f"{row['low']:.2f}" if pd.notna(row['low']) else 'NULL',
                    f"{row['close']:.2f}" if pd.notna(row['close']) else 'NULL',
                    f"{int(row['volume']):,}" if pd.notna(row['volume']) else 'NULL',
                    missing_icon
                ]
                self.tree.insert('', 'end', values=values, tags=(tag,))
                record_count += 1

                # Progress indicator for large datasets
                if record_count % 1000 == 0:
                    self.info_label.configure(text=f"Loading {ticker}: {record_count:,} records...")
                    self.frame.update_idletasks()

            # Final info update
            date_range = f"{ticker_data['date'].min().date()} to {ticker_data['date'].max().date()}"

            if show_missing_only:
                self.info_label.configure(
                    text=f"{ticker}: Showing {missing_count:,} missing records ({date_range}) - {limit_text}"
                )
            else:
                total_in_ticker = len(ticker_data)
                self.info_label.configure(
                    text=f"{ticker}: {total_in_ticker:,} total records ({date_range}) - showing {limit_text} | Real: {real_count:,} | Missing: {missing_count:,}"
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

    def on_show_missing_change(self):
        """Handle show missing data checkbox change"""
        # If showing missing only, explain what this means
        if self.show_missing_var.get():
            logger.info("Filtering to show only rows with is_missing=TRUE")
        self.update_table_view()