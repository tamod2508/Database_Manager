"""
Stock-wise status viewer component - OPTIMIZED VERSION
Replace in: src/gui/components/stock_status_viewer.py
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
import pandas as pd

from ...utils.logger import get_logger
from ...core.database_manager import db_manager

logger = get_logger(__name__)

class StockStatusViewer:
    """Optimized component to display stock-wise data availability status"""

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

        # Delete button
        delete_btn = ctk.CTkButton(
            header_frame,
            text="Delete Selected",
            command=self.delete_selected_stock,
            height=32,
            width=120,
            fg_color="red",
            hover_color="darkred"
        )
        delete_btn.pack(side="right", padx=5)

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
            height=20,
            selectmode='extended'
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
        """Refresh status data from database - OPTIMIZED VERSION"""
        try:
            logger.info("Refreshing stock status data...")
            self.summary_label.configure(text="Loading... please wait")
            self.frame.update_idletasks()

            # Get list of all symbols from CSV
            from ...config.settings import config
            symbols_df = pd.read_csv(config.COMPANIES_CSV)
            all_symbols = symbols_df['Symbol'].tolist()

            # OPTIMIZATION 1: Get all data in ONE query instead of 2000 queries
            logger.info(f"Fetching data for {len(all_symbols)} symbols in bulk...")
            all_data = db_manager.get_stock_data()  # Get ALL data at once

            if all_data.empty:
                # No data in database at all
                status_list = []
                for symbol in all_symbols:
                    status_list.append({
                        'symbol': symbol,
                        'has_data': False,
                        'record_count': 0,
                        'earliest_date': 'N/A',
                        'latest_date': 'N/A',
                        'days_range': 0
                    })
            else:
                # OPTIMIZATION 2: Use pandas groupby for fast aggregation
                logger.info("Analyzing data by symbol...")

                # Group by ticker and calculate stats in one go
                stats = all_data.groupby('ticker').agg({
                    'date': ['min', 'max', 'count']
                }).reset_index()

                # Flatten column names
                stats.columns = ['ticker', 'earliest_date', 'latest_date', 'record_count']

                # Calculate days range
                stats['days_range'] = (stats['latest_date'] - stats['earliest_date']).dt.days

                # Convert dates to strings
                stats['earliest_date'] = stats['earliest_date'].dt.strftime('%Y-%m-%d')
                stats['latest_date'] = stats['latest_date'].dt.strftime('%Y-%m-%d')

                # Create a set of tickers with data for fast lookup
                tickers_with_data = set(stats['ticker'].tolist())

                # Build status list
                status_list = []
                for symbol in all_symbols:
                    if symbol in tickers_with_data:
                        # Get stats for this symbol
                        symbol_stats = stats[stats['ticker'] == symbol].iloc[0]
                        status_list.append({
                            'symbol': symbol,
                            'has_data': True,
                            'record_count': int(symbol_stats['record_count']),
                            'earliest_date': symbol_stats['earliest_date'],
                            'latest_date': symbol_stats['latest_date'],
                            'days_range': int(symbol_stats['days_range'])
                        })
                    else:
                        # No data for this symbol
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

    def delete_selected_stock(self):
        """Delete data for the selected stock(s) from database"""
        from tkinter import messagebox

        # Get selected items
        selections = self.tree.selection()

        if not selections:
            messagebox.showwarning(
                "No Selection",
                "Please select one or more stocks from the list to delete."
            )
            return

        # Collect symbols and their record counts
        stocks_to_delete = []
        total_records = 0

        for selection in selections:
            item = self.tree.item(selection)
            symbol = item['values'][0]

            stock_data = db_manager.get_stock_data(ticker=symbol)

            if not stock_data.empty:
                record_count = len(stock_data)
                stocks_to_delete.append({
                    'symbol': symbol,
                    'records': record_count
                })
                total_records += record_count

        if not stocks_to_delete:
            messagebox.showinfo(
                "No Data",
                "Selected stocks have no data to delete."
            )
            return

        # Build confirmation message
        stock_count = len(stocks_to_delete)
        if stock_count == 1:
            confirm_msg = f"Are you sure you want to delete ALL data for {stocks_to_delete[0]['symbol']}?\n\n"
            confirm_msg += f"This will permanently remove {total_records:,} records.\n\n"
        else:
            confirm_msg = f"Are you sure you want to delete data for {stock_count} stocks?\n\n"
            confirm_msg += f"Total records to delete: {total_records:,}\n\n"
            confirm_msg += "Stocks:\n"
            for stock in stocks_to_delete[:5]:
                confirm_msg += f"  • {stock['symbol']}: {stock['records']:,} records\n"
            if stock_count > 5:
                confirm_msg += f"  ... and {stock_count - 5} more\n\n"

        confirm_msg += "This action cannot be undone!"

        # Confirmation dialog
        confirm = messagebox.askyesno(
            "Confirm Deletion",
            confirm_msg
        )

        if not confirm:
            return

        # Double confirmation for safety
        final_confirm = messagebox.askyesno(
            "Final Confirmation",
            f"Last chance!\n\n"
            f"Delete {total_records:,} records for {stock_count} stock(s)?",
            icon='warning'
        )

        if not final_confirm:
            messagebox.showinfo("Cancelled", "Deletion cancelled.")
            return

        # Perform deletion
        deleted_count = 0
        failed_stocks = []

        try:
            if not db_manager.is_initialized:
                db_manager.initialize()

            with db_manager.engine.connect() as conn:
                from sqlalchemy import text

                for stock in stocks_to_delete:
                    symbol = stock['symbol']
                    try:
                        logger.info(f"Deleting data for {symbol} ({stock['records']} records)")

                        delete_query = text("DELETE FROM stock_data WHERE ticker = :ticker")
                        result = conn.execute(delete_query, {'ticker': symbol})
                        deleted_count += result.rowcount

                    except Exception as e:
                        logger.error(f"Failed to delete {symbol}: {e}")
                        failed_stocks.append(symbol)

                conn.commit()

            # Show results
            if failed_stocks:
                messagebox.showwarning(
                    "Partial Success",
                    f"Deleted {deleted_count:,} records.\n\n"
                    f"Failed to delete: {', '.join(failed_stocks)}"
                )
            else:
                logger.info(f"Successfully deleted {deleted_count} records for {stock_count} stocks")
                messagebox.showinfo(
                    "Deletion Complete",
                    f"Successfully deleted {deleted_count:,} records for {stock_count} stock(s)"
                )

            # Refresh the status display
            self.refresh_status()

        except Exception as e:
            logger.error(f"Failed to delete data: {e}")
            messagebox.showerror(
                "Deletion Failed",
                f"Failed to delete data:\n\n{str(e)}"
            )