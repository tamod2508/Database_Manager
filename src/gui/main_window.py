"""
Main GUI application window - Fixed Refresh Functionality and Progress Tracking
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import pandas as pd
import threading
from typing import Dict

from ..config.settings import config
from ..core.database_manager import db_manager
from ..core.data_fetcher import data_fetcher
from ..utils.logger import get_logger
from .components.data_viewer import DataViewer
from .components.status_panel import StatusPanel
from .components.settings_panel import SettingsPanel
from .components.stock_status_viewer import StockStatusViewer

logger = get_logger(__name__, "GUI.log")

class MainWindow:
    """Main application window"""

    def __init__(self):
        # Set appearance mode and theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Initialize database
        try:
            db_manager.initialize()
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            messagebox.showerror("Database Error", f"Failed to initialize database: {e}")

        # Create main window
        self.root = ctk.CTk()
        self.root.title("Data Manager")
        self.root.geometry(f"{config.WINDOW_WIDTH}x{config.WINDOW_HEIGHT}")
        self.root.minsize(800, 600)

        # Configure grid weights
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

        # Initialize state variables
        self.current_data = pd.DataFrame()
        self.is_updating = False

        self.setup_ui()

        logger.info("Main window initialized")

    def setup_ui(self):
        """Setup the user interface"""

        # Left sidebar
        self.sidebar = ctk.CTkFrame(self.root, width=250, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(5, weight=1)

        # App title
        title_label = ctk.CTkLabel(
            self.sidebar,
            text="Data Manager",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.grid(row=0, column=0, padx=20, pady=(20, 10))


        # Update plan button (shows what will be updated)
        self.plan_button = ctk.CTkButton(
            self.sidebar,
            text="Check Update Plan",
            command=self.show_update_plan,
            height=35,
            fg_color="gray60",
            hover_color="gray50"
        )
        self.plan_button.grid(row=1, column=0, padx=20, pady=5, sticky="ew")

        # Incremental update button (primary)
        self.update_button = ctk.CTkButton(
            self.sidebar,
            text="Update Data",
            command=self.start_incremental_update,
            height=40,
            fg_color="green",
            hover_color="darkgreen"
        )
        self.update_button.grid(row=2, column=0, padx=20, pady=10, sticky="ew")

        # Full refresh button (secondary - more dangerous)
        self.full_refresh_button = ctk.CTkButton(
            self.sidebar,
            text="Full Refresh",
            command=self.start_full_refresh,
            height=35,
            fg_color="orange",
            hover_color="darkorange"
        )
        self.full_refresh_button.grid(row=3, column=0, padx=20, pady=5, sticky="ew")

        # Refresh view button
        self.refresh_button = ctk.CTkButton(
            self.sidebar,
            text="Refresh View",
            command=self.refresh_data,
            height=35
        )
        self.refresh_button.grid(row=4, column=0, padx=20, pady=10, sticky="ew")

        # Status panel
        self.status_panel = StatusPanel(self.sidebar)
        self.status_panel.frame.grid(row=5, column=0, padx=20, pady=20, sticky="nsew")

        # Main content area
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)

        # Use CTk tabview instead of ttk notebook
        self.tabview = ctk.CTkTabview(self.main_frame)
        self.tabview.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        # Add tabs
        status_tab = self.tabview.add("Stock-wise Status")
        data_tab = self.tabview.add("Data Viewer")
        settings_tab = self.tabview.add("Settings")

        # Create components in tabs
        self.settings_panel = SettingsPanel(settings_tab)
        self.settings_panel.frame.pack(fill="both", expand=True)

        self.data_viewer = DataViewer(data_tab)
        self.data_viewer.frame.pack(fill="both", expand=True)

        self.stock_status_viewer = StockStatusViewer(status_tab)
        self.stock_status_viewer.frame.pack(fill="both", expand=True)

        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ctk.CTkProgressBar(self.main_frame, variable=self.progress_var)
        self.progress_bar.grid(row=1, column=0, sticky="ew", padx=10, pady=(10, 5))
        self.progress_bar.set(0)

        # Status label
        self.status_var = tk.StringVar(value="Ready - Click 'Refresh View' to load existing data or 'Update Data' to fetch latest")
        self.status_label = ctk.CTkLabel(self.main_frame, textvariable=self.status_var)
        self.status_label.grid(row=2, column=0, padx=10, pady=(0, 10))

        # Load initial data
        self.root.after(1000, self.refresh_data)  # Load data after UI is fully initialized

    def refresh_data(self):
        """Refresh the data display from database"""
        try:
            self.status_var.set("Loading data from database...")
            self.root.update_idletasks()

            # Get data from database
            self.current_data = db_manager.get_stock_data()

            if not self.current_data.empty:
                # Update data viewer
                self.data_viewer.update_data(self.current_data)

                self.stock_status_viewer.refresh_status()

                # Update status
                unique_tickers = len(self.current_data['ticker'].unique())
                total_records = len(self.current_data)
                latest_date = self.current_data['date'].max().strftime('%Y-%m-%d') if not self.current_data.empty else 'N/A'

                self.status_var.set(f"Loaded {total_records:,} records from {unique_tickers} tickers (latest: {latest_date})")

                logger.info(f"Data refreshed: {total_records} records, {unique_tickers} tickers")
            else:
                self.status_var.set("No data available - Click 'Update Data' to fetch stock data")
                logger.info("No data found in database")

            # Update status panel
            try:
                stats = db_manager.get_database_stats()
                self.status_panel.update_status(stats)
            except Exception as e:
                logger.warning(f"Could not update status panel: {e}")

        except Exception as e:
            logger.error(f"Data refresh failed: {e}")
            self.status_var.set(f"Error loading data: {str(e)}")
            messagebox.showerror("Refresh Error", f"Failed to refresh data:\n{str(e)}")

    def _start_update_thread(self, incremental=True):
        """Start update in background thread"""
        self.is_updating = True

        # Update UI state
        self.update_button.configure(state="disabled")
        self.full_refresh_button.configure(state="disabled")
        self.refresh_button.configure(state="disabled")
        self.plan_button.configure(state="disabled")

        if incremental:
            self.update_button.configure(text="Updating...")
            self.status_var.set("Starting incremental update...")
        else:
            self.full_refresh_button.configure(text="Refreshing...")
            self.status_var.set("Starting full refresh...")

        self.progress_var.set(0)

        # Run in thread
        thread = threading.Thread(
            target=self._run_update,
            args=(incremental,),
            daemon=True
        )
        thread.start()


    def _run_update(self, incremental=True):
        """Run update with specified mode"""
        try:
            if incremental:
                success, result = data_fetcher.update_stock_data(
                    update_callback=self._update_progress
                )
            else:
                success, result = data_fetcher.refresh_all_data(
                    update_callback=self._update_progress
                )

            self.root.after(0, self._update_complete, success, result, incremental)

        except Exception as e:
            logger.error(f"Update failed: {e}")
            self.root.after(0, self._update_complete, False, {"error": str(e)}, incremental)


    def _update_progress(self, progress: float, symbol: str,
                        successful: int, failed: int):
        """Update progress callback - Enhanced to show database insertion phase"""
        def update_ui():
            # Fetching is 0-90% of progress, insertion is 90-100%
            fetch_progress = progress * 0.9
            self.progress_var.set(fetch_progress)
            self.status_var.set(f"Fetching {symbol}... ({successful} success, {failed} failed)")

        self.root.after(0, update_ui)

    def _update_complete(self, success: bool, result: Dict, incremental: bool):
        """Handle update completion - Fixed to show popup"""
        self.is_updating = False

        # Show database insertion progress
        def show_insertion_progress():
            self.status_var.set("Inserting data into database...")
            self.progress_var.set(0.95)
            self.root.update_idletasks()

        self.root.after(0, show_insertion_progress)

        # Small delay to show insertion message
        import time
        time.sleep(0.5)

        # Restore UI state
        self.update_button.configure(state="normal", text="Update Data")
        self.full_refresh_button.configure(state="normal", text="Full Refresh")
        self.refresh_button.configure(state="normal")
        self.plan_button.configure(state="normal")

        self.progress_var.set(1.0 if success else 0)

        if success:
            mode = "incremental update" if incremental else "full refresh"
            total_records = result.get('total_records', 0)
            successful_fetches = result.get('successful_fetches', 0)
            skipped_fetches = result.get('skipped_fetches', 0)
            duration = result.get('duration_seconds', 0)

            # Different messages based on mode and results
            if total_records == 0:
                # No new data
                self.status_var.set("All data is up to date - no new records fetched")
                message_text = "No new data was available to fetch.\n\nAll symbols are up to date!"
                title = "No Updates Needed"
            else:
                self.status_var.set(f"{mode.title()} complete: {total_records:,} records in {duration:.1f}s")

                # BUILD THE POPUP MESSAGE
                message_text = f"✅ {mode.title()} completed successfully!\n\n"
                message_text += f"📊 Successfully updated: {successful_fetches} symbols\n"
                message_text += f"📥 New records added: {total_records:,}\n"
                if skipped_fetches > 0:
                    message_text += f"✓ Symbols already up to date: {skipped_fetches}\n"
                message_text += f"⏱️  Duration: {duration:.1f} seconds\n"

                # Add performance metrics
                records_per_sec = result.get('records_per_second', 0)
                if records_per_sec > 0:
                    message_text += f"⚡ Performance: {records_per_sec:.0f} records/second"

                title = "Update Complete"

            # Mark data as updated in status panel
            self.status_panel.mark_data_updated()

            # SHOW THE POPUP
            messagebox.showinfo(title, message_text)

            # Automatically refresh the display after successful update
            if total_records > 0:
                self.refresh_data()
        else:
            error_msg = result.get('error', 'Unknown error')
            mode = "incremental update" if incremental else "full refresh"
            self.status_var.set(f"{mode.title()} failed: {error_msg}")
            messagebox.showerror("Update Failed", f"Error during {mode}:\n\n{error_msg}")

    def run(self):
        """Start the application"""
        logger.info("Starting main application")
        self.root.mainloop()

    def show_update_plan(self):
        """Show what will be updated before actually updating"""
        try:
            self.status_var.set("Analyzing update requirements...")
            self.root.update_idletasks()

            # Get update plan
            plan = data_fetcher.get_update_plan()

            # Format plan information
            total_symbols = plan['total_symbols']
            need_full = len(plan['symbols_needing_full_fetch'])
            need_update = len(plan['symbols_needing_update'])
            up_to_date = len(plan['symbols_up_to_date'])

            if need_full == 0 and need_update == 0:
                plan_text = f"✅ All {total_symbols} symbols are up to date!\n\nNo updates needed."
                title = "No Updates Required"
            else:
                plan_text = f"Update Plan for {total_symbols} symbols:\n\n"

                if need_full > 0:
                    plan_text += f"📥 {need_full} symbols need FULL data fetch\n"
                    plan_text += "   (No existing data)\n\n"

                if need_update > 0:
                    plan_text += f"🔄 {need_update} symbols need INCREMENTAL update\n"
                    plan_text += "   (Recent data only)\n\n"

                if up_to_date > 0:
                    plan_text += f"✅ {up_to_date} symbols are already up to date\n\n"

                plan_text += "Click 'Update Data' for incremental update\n"
                plan_text += "or 'Full Refresh' to re-fetch everything."

                title = "Update Plan"

            self.status_var.set("Update plan ready - see popup for details")
            messagebox.showinfo(title, plan_text)

        except Exception as e:
            logger.error(f"Failed to get update plan: {e}")
            self.status_var.set(f"Error getting update plan: {e}")
            messagebox.showerror("Error", f"Failed to analyze update plan:\n{str(e)}")

    def start_incremental_update(self):
        """Start incremental data update (only new data)"""
        if self.is_updating:
            messagebox.showinfo("Update in Progress", "Data update is already running")
            return

        try:
            # Get update plan first
            plan = data_fetcher.get_update_plan()

            need_full = len(plan['symbols_needing_full_fetch'])
            need_update = len(plan['symbols_needing_update'])
            up_to_date = len(plan['symbols_up_to_date'])

            if need_full == 0 and need_update == 0:
                messagebox.showinfo("No Updates Needed", "All data is up to date!")
                return

            # Show update summary
            message = "Incremental Update Summary:\n\n"
            if need_full > 0:
                message += f"• {need_full} symbols need full data fetch\n"
            if need_update > 0:
                message += f"• {need_update} symbols need recent data update\n"
            if up_to_date > 0:
                message += f"• {up_to_date} symbols are already up to date\n"
            message += "\nThis will only fetch missing data, saving time and API calls.\n\nContinue?"

            result = messagebox.askyesno("Incremental Update", message)
            if result:
                self._start_update_thread(incremental=True)

        except Exception as e:
            logger.error(f"Failed to start incremental update: {e}")
            messagebox.showerror("Error", f"Failed to start update:\n{str(e)}")

    def start_full_refresh(self):
        """Start full data refresh (all data from scratch)"""
        if self.is_updating:
            messagebox.showinfo("Update in Progress", "Data update is already running")
            return

        # Strong warning for full refresh
        result = messagebox.askyesno(
            "⚠️ Full Refresh Warning",
            "FULL REFRESH will fetch ALL data from the start date.\n\n"
            "This will:\n"
            "• Take significantly longer\n"
            "• Use many more API calls\n"
            "• Re-fetch data you already have\n\n"
            "Only use this if:\n"
            "• You want to rebuild the entire database\n"
            "• You suspect data corruption\n"
            "• You changed the date range settings\n\n"
            "Continue?"
        )

        if result:
            # Double confirmation
            confirm = messagebox.askyesno(
                "Final Confirmation",
                "Are you absolutely sure you want to fetch ALL data from scratch?\n\n"
                "This cannot be undone."
            )
            if confirm:
                self._start_update_thread(incremental=False)

def main():
    """Main entry point"""
    try:
        app = MainWindow()
        app.run()
    except Exception as e:
        logger.error(f"Application startup failed: {e}")
        messagebox.showerror("Startup Error", f"Failed to start application:\n{str(e)}")

if __name__ == "__main__":
    main()