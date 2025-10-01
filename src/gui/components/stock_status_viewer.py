"""
Stock-wise status viewer component for GUI - Enhanced with Missing Days
Shows data availability status for each company including missing days count
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

        # Create Treeview with columns (ADDED: Completeness and Missing Days)
        columns = ('Symbol', 'Status', 'Records', 'Earliest Date', 'Latest Date', 'Date Range', 'Completeness', 'Missing Days')
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
        self.tree.heading('Date Range', text='Expeted days')
        self.tree.heading('Completeness', text='Completeness %')
        self.tree.heading('Missing Days', text='Missing Days')

        self.tree.column('Symbol', width=100, anchor='center')
        self.tree.column('Status', width=80, anchor='center')
        self.tree.column('Records', width=100, anchor='center')
        self.tree.column('Earliest Date', width=120, anchor='center')
        self.tree.column('Latest Date', width=120, anchor='center')
        self.tree.column('Date Range', width=100, anchor='center')
        self.tree.column('Completeness', width=110, anchor='center')
        self.tree.column('Missing Days', width=110, anchor='center')

        # Add tooltip/info for Missing Days column
        # Create info button next to the header
        info_text = (
            "ℹ️ About 'Missing Days':\n\n"
            "This shows the approximate number of trading days missing from the expected date range.\n\n"
            "Calculated as: (Years × 252 trading days) - (Actual records)\n\n"
            "Why data might be <100%:\n"
            "• Market holidays (~10-12 days/year)\n"
            "• Stock listing mid-year\n"
            "• yfinance data gaps\n"
            "• Trading suspensions\n\n"
            "These are NOT actual rows in the database - they're date gaps that don't exist.\n\n"
            "97%+ completeness is considered excellent."
        )

        # Store tooltip text for potential hover implementation
        self.missing_days_tooltip = info_text

        # Configure tags for status colors
        self.tree.tag_configure('complete', background='#E8F5E9', foreground='#2E7D32')  # Green
        self.tree.tag_configure('good', background='#FFF9C4', foreground='#F57C00')      # Yellow
        self.tree.tag_configure('incomplete', background='#FFEBEE', foreground='#C62828') # Red

        # Info button for Missing Days explanation
        missing_days_info_btn = ctk.CTkButton(
            header_frame,
            text="ℹ️ About Missing Days",
            command=self.show_missing_days_info,
            height=32,
            width=160,
            fg_color="gray40",
            hover_color="gray30"
        )
        missing_days_info_btn.pack(side="right", padx=5)

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
            text="Complete (≥97%)",
            variable=self.filter_var,
            value="complete",
            command=self.apply_filter
        ).pack(side="left", padx=5)

        ctk.CTkRadioButton(
            filter_frame,
            text="Incomplete (<97%)",
            variable=self.filter_var,
            value="incomplete",
            command=self.apply_filter
        ).pack(side="left", padx=5)

    def refresh_status(self):
        """Refresh status data from database using new stats methods"""
        try:
            logger.info("Refreshing stock status data with completeness stats...")

            # Get comprehensive stats from database
            stats_df = db_manager.get_stock_data_stats()

            if stats_df.empty:
                self.summary_label.configure(text="No data available")
                logger.info("No data found in database")
                return

            # Convert to format expected by display
            status_list = []

            for _, row in stats_df.iterrows():
                # Calculate missing days (approximate)
                years = (row['last_date'] - row['first_date']).days / 365.25
                expected_days = int(years * 252)  # ~252 trading days/year
                actual_days = row['total_records']
                missing_days = max(0, expected_days - actual_days)

                completeness = row['completeness_pct']

                status_list.append({
                    'symbol': row['ticker'],
                    'has_data': True,
                    'record_count': row['total_records'],
                    'earliest_date': row['first_date'].strftime('%Y-%m-%d'),
                    'latest_date': row['last_date'].strftime('%Y-%m-%d'),
                    'days_range': expected_days,
                    'completeness_pct': completeness,
                    'missing_days': missing_days
                })

            self.status_data = pd.DataFrame(status_list)
            self.update_display()

            logger.info(f"Status refreshed for {len(stats_df)} symbols")

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
        complete_stocks = len(self.status_data[self.status_data['completeness_pct'] >= 97])
        good_stocks = len(self.status_data[(self.status_data['completeness_pct'] >= 90) &
                                           (self.status_data['completeness_pct'] < 97)])
        incomplete_stocks = len(self.status_data[self.status_data['completeness_pct'] < 90])

        avg_completeness = self.status_data['completeness_pct'].mean()
        total_missing = self.status_data['missing_days'].sum()

        # Update summary
        summary_text = (
            f"Total Symbols: {total_symbols} | "
            f"Complete (≥97%): {complete_stocks} | "
            f"Good (90-96%): {good_stocks} | "
            f"Incomplete (<90%): {incomplete_stocks} | "
            f"Avg Completeness: {avg_completeness:.1f}% | "
            f"Total Missing Days: {total_missing:,}"
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
        if filter_value == "complete":
            filtered_data = self.status_data[self.status_data['completeness_pct'] >= 97]
        elif filter_value == "incomplete":
            filtered_data = self.status_data[self.status_data['completeness_pct'] < 97]
        else:  # all
            filtered_data = self.status_data

        # Populate tree
        for _, row in filtered_data.iterrows():
            completeness = row['completeness_pct']

            # Determine status icon and tag (adjusted for market holidays)
            # 97%+ is considered complete (accounts for ~10-12 market holidays per year)
            if completeness >= 97:
                status_icon = "✓"
                tag = 'complete'
            elif completeness >= 90:
                status_icon = "⚠"
                tag = 'good'
            else:
                status_icon = "✗"
                tag = 'incomplete'

            values = (
                row['symbol'],
                status_icon,
                f"{row['record_count']:,}" if row['record_count'] > 0 else "-",
                row['earliest_date'],
                row['latest_date'],
                str(row['days_range']) if row['days_range'] > 0 else "-",
                f"{completeness:.1f}%",
                f"{row['missing_days']:,}" if row['missing_days'] > 0 else "0"
            )

            self.tree.insert('', 'end', values=values, tags=(tag,))

    def load_initial_data(self):
        """Load initial status data"""
        self.refresh_status()

    def show_missing_days_info(self):
        """Show information about Missing Days column"""
        from tkinter import messagebox

        info_text = (
            "ℹ️  Understanding 'Missing Days'\n\n"
            "This column shows approximate trading days missing from the expected range.\n\n"
            "📊 Calculation:\n"
            "Missing Days = (Years × 252) - (Actual records)\n"
            "• 252 = Average trading days per year\n"
            "• Years = Date range of stock data\n\n"
            "⚠️  Important:\n"
            "These are NOT actual rows in the database!\n"
            "They represent date gaps where yfinance has no data.\n\n"
            "🔍 Common reasons for <100% completeness:\n"
            "• Market holidays (~10-12 days/year in India)\n"
            "• Stock listed mid-year\n"
            "• yfinance data quality gaps\n"
            "• Trading suspensions (corporate actions)\n"
            "• IPO/listing date calculations\n\n"
            "✅ What's considered good:\n"
            "• ≥97% = Complete (accounts for holidays)\n"
            "• 90-96% = Good (minor gaps)\n"
            "• <90% = May need attention\n\n"
            "This is normal and expected - most stocks will be 97-100%!"
        )

        messagebox.showinfo("About Missing Days", info_text)

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