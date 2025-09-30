"""
Data viewing component - with working search box and autocomplete
Replace in: src/gui/components/data_viewer.py
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
import pandas as pd

from ...utils.logger import get_logger

logger = get_logger(__name__)

class DataViewer:
    """Data viewer component with search functionality"""

    def __init__(self, parent):
        self.parent = parent
        self.current_data = pd.DataFrame()
        self.all_tickers = []
        self.filtered_tickers = []
        self.frame = ctk.CTkFrame(parent)
        self.suggestions_window = None
        self.setup_ui()

    def setup_ui(self):
        """Setup data viewer UI with search box"""

        # Controls frame
        controls_frame = ctk.CTkFrame(self.frame)
        controls_frame.pack(fill="x", padx=10, pady=10)

        # Search label with icon
        ctk.CTkLabel(controls_frame, text="🔍 Search Ticker:",
                    font=ctk.CTkFont(size=13, weight="bold")).pack(side="left", padx=(10, 5))

        # Search entry box
        self.ticker_search = ctk.CTkEntry(
            controls_frame,
            placeholder_text="Type ticker symbol (e.g., RELIANCE, TCS, INFY)",
            width=300,
            height=32
        )
        self.ticker_search.pack(side="left", padx=5)

        # Bind search events
        self.ticker_search.bind('<KeyRelease>', self.on_search_changed)
        self.ticker_search.bind('<Return>', self.on_search_enter)
        self.ticker_search.bind('<Down>', self.focus_suggestions)
        self.ticker_search.bind('<FocusOut>', self.delayed_hide_suggestions)

        # Clear button
        clear_btn = ctk.CTkButton(
            controls_frame,
            text="✕ Clear",
            command=self.clear_search,
            width=70,
            height=32,
            fg_color="gray40",
            hover_color="gray30"
        )
        clear_btn.pack(side="left", padx=5)

        # Show all data checkbox
        self.show_all_var = tk.BooleanVar(value=False)
        self.show_all_check = ctk.CTkCheckBox(
            controls_frame,
            text="Show all records",
            variable=self.show_all_var,
            command=self.on_show_all_change
        )
        self.show_all_check.pack(side="left", padx=15)

        # Info label
        self.info_label = ctk.CTkLabel(controls_frame, text="Type to search for a ticker",
                                       font=ctk.CTkFont(size=11))
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

    def on_search_changed(self, event=None):
        """Handle search text changes - show suggestions"""
        search_text = self.ticker_search.get().strip().upper()

        if not search_text:
            self.hide_suggestions()
            self.info_label.configure(text="Type to search for a ticker")
            return

        # Filter tickers based on search text
        self.filtered_tickers = [
            ticker for ticker in self.all_tickers
            if search_text in ticker
        ]

        if self.filtered_tickers:
            self.show_suggestions(self.filtered_tickers[:10])  # Show max 10 suggestions

            # Update info with matches count
            if len(self.filtered_tickers) == 1:
                self.info_label.configure(text="1 matching ticker")
            else:
                self.info_label.configure(text=f"{len(self.filtered_tickers)} matching tickers")
        else:
            self.hide_suggestions()
            self.info_label.configure(text="No matching tickers found")

    def show_suggestions(self, suggestions):
        """Show autocomplete suggestions in a toplevel window"""
        # Destroy existing suggestions window
        if self.suggestions_window:
            self.suggestions_window.destroy()

        # Create new toplevel window for suggestions
        self.suggestions_window = tk.Toplevel(self.frame)
        self.suggestions_window.wm_overrideredirect(True)  # Remove window decorations

        # Position below the search entry
        x = self.ticker_search.winfo_rootx()
        y = self.ticker_search.winfo_rooty() + self.ticker_search.winfo_height()
        width = self.ticker_search.winfo_width()

        self.suggestions_window.geometry(f"{width}x150+{x}+{y}")

        # Create listbox in suggestions window
        suggestions_frame = tk.Frame(self.suggestions_window, bg="#2b2b2b", bd=1, relief="solid")
        suggestions_frame.pack(fill="both", expand=True)

        self.suggestions_listbox = tk.Listbox(
            suggestions_frame,
            bg="#2b2b2b",
            fg="white",
            selectbackground="#1f538d",
            font=("Arial", 11),
            relief="flat",
            borderwidth=0,
            highlightthickness=0
        )
        self.suggestions_listbox.pack(fill="both", expand=True, padx=1, pady=1)

        # Add scrollbar
        scrollbar = tk.Scrollbar(suggestions_frame, orient="vertical")
        scrollbar.pack(side="right", fill="y")
        self.suggestions_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.suggestions_listbox.yview)

        # Populate with suggestions
        for ticker in suggestions:
            self.suggestions_listbox.insert(tk.END, ticker)

        # Bind events
        self.suggestions_listbox.bind('<<ListboxSelect>>', self.on_suggestion_select)
        self.suggestions_listbox.bind('<Return>', self.on_suggestion_select)
        self.suggestions_listbox.bind('<Escape>', lambda e: self.hide_suggestions())
        self.suggestions_listbox.bind('<FocusOut>', self.delayed_hide_suggestions)

        # Select first item by default
        if suggestions:
            self.suggestions_listbox.selection_set(0)
            self.suggestions_listbox.activate(0)

    def hide_suggestions(self):
        """Hide autocomplete suggestions"""
        if self.suggestions_window:
            self.suggestions_window.destroy()
            self.suggestions_window = None

    def delayed_hide_suggestions(self, event=None):
        """Hide suggestions after a short delay (allows clicking on suggestions)"""
        self.frame.after(200, self.hide_suggestions)

    def focus_suggestions(self, event=None):
        """Move focus to suggestions listbox"""
        if self.suggestions_window and self.suggestions_listbox:
            self.suggestions_listbox.focus_set()
            return "break"

    def on_search_enter(self, event=None):
        """Handle Enter key - select first suggestion or exact match"""
        search_text = self.ticker_search.get().strip().upper()

        if not search_text:
            return

        # Check for exact match first
        if search_text in self.all_tickers:
            self.select_ticker(search_text)
            self.hide_suggestions()
        elif self.filtered_tickers:
            # Select first suggestion
            self.select_ticker(self.filtered_tickers[0])
            self.ticker_search.delete(0, tk.END)
            self.ticker_search.insert(0, self.filtered_tickers[0])
            self.hide_suggestions()

        return "break"

    def on_suggestion_select(self, event=None):
        """Handle suggestion selection from listbox"""
        if not self.suggestions_listbox:
            return

        selection = self.suggestions_listbox.curselection()
        if selection:
            ticker = self.suggestions_listbox.get(selection[0])
            self.ticker_search.delete(0, tk.END)
            self.ticker_search.insert(0, ticker)
            self.select_ticker(ticker)
            self.hide_suggestions()
            self.ticker_search.focus_set()  # Return focus to search box

    def select_ticker(self, ticker):
        """Display data for selected ticker"""
        if ticker and not self.current_data.empty:
            self.update_table_view(ticker)

    def clear_search(self):
        """Clear search box and table"""
        self.ticker_search.delete(0, tk.END)
        self.hide_suggestions()
        self.tree.delete(*self.tree.get_children())
        self.info_label.configure(text="Type to search for a ticker")
        self.ticker_search.focus_set()

    def update_data(self, data: pd.DataFrame):
        """Update the displayed data"""
        try:
            self.current_data = data

            # Update ticker list
            if not data.empty:
                self.all_tickers = sorted(data['ticker'].unique().tolist())
                self.info_label.configure(
                    text=f"Loaded {len(self.all_tickers)} tickers, {len(data):,} total records"
                )
                logger.info(f"Data viewer updated with {len(data)} records, {len(self.all_tickers)} tickers")
            else:
                self.info_label.configure(text="No data available")

        except Exception as e:
            logger.error(f"Failed to update data viewer: {e}")
            self.info_label.configure(text=f"Error: {e}")

    def update_table_view(self, ticker=None):
        """Update table view with current data"""
        try:
            # Clear existing data
            for item in self.tree.get_children():
                self.tree.delete(item)

            # Get ticker from search box if not provided
            if ticker is None:
                ticker = self.ticker_search.get().strip().upper()

            if not ticker or self.current_data.empty:
                return

            ticker_data = self.current_data[self.current_data['ticker'] == ticker].copy()
            if ticker_data.empty:
                self.info_label.configure(text=f"No data found for {ticker}")
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
                text=f"{len(ticker_data):,} total records ({date_range}) - showing {limit_text}"
            )

        except Exception as e:
            logger.error(f"Failed to update table view: {e}")
            self.info_label.configure(text=f"Error loading data: {e}")

    def on_show_all_change(self):
        """Handle show all data checkbox change"""
        ticker = self.ticker_search.get().strip().upper()
        if ticker:
            self.update_table_view(ticker)