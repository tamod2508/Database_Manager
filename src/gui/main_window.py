"""
Main GUI application window - Fixed Refresh Functionality
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import threading
from typing import Optional, Dict, Any
import logging

from ..config.settings import config
from ..core.database_manager import db_manager
from ..core.data_fetcher import data_fetcher
from ..core.apple_silicon_optimizer import optimizer
from ..utils.logger import get_logger
from .components.data_viewer import DataViewer
from .components.status_panel import StatusPanel
from .components.settings_panel import SettingsPanel

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
        self.sidebar.grid_rowconfigure(4, weight=1)
        
        # App title
        title_label = ctk.CTkLabel(
            self.sidebar, 
            text="Data Manager",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        
        # Control buttons
        self.update_button = ctk.CTkButton(
            self.sidebar,
            text="Update Data",
            command=self.start_update,
            height=40
        )
        self.update_button.grid(row=2, column=0, padx=20, pady=10, sticky="ew")
        
        self.refresh_button = ctk.CTkButton(
            self.sidebar,
            text="Refresh View",
            command=self.refresh_data,
            height=40
        )
        self.refresh_button.grid(row=3, column=0, padx=20, pady=10, sticky="ew")
        
        # Status panel
        self.status_panel = StatusPanel(self.sidebar)
        self.status_panel.frame.grid(row=4, column=0, padx=20, pady=20, sticky="nsew")
        
        # Main content area
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)
        
        # Use CTk tabview instead of ttk notebook
        self.tabview = ctk.CTkTabview(self.main_frame)
        self.tabview.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        # Add tabs
        data_tab = self.tabview.add("Data Viewer")
        settings_tab = self.tabview.add("Settings")
        
        # Create components in tabs
        self.data_viewer = DataViewer(data_tab)
        self.data_viewer.frame.pack(fill="both", expand=True)
        
        self.settings_panel = SettingsPanel(settings_tab)
        self.settings_panel.frame.pack(fill="both", expand=True)
        
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
    
    def start_update(self):
        """Start data update in background thread"""
        if self.is_updating:
            messagebox.showinfo("Update in Progress", "Data update is already running")
            return
            
        # Confirm update
        result = messagebox.askyesno(
            "Update Data",
            "This will fetch the latest stock data from Yahoo Finance.\n\n"
            "Continue?"
        )
        
        if not result:
            return
            
        self.is_updating = True
        self.update_button.configure(state="disabled", text="Updating...")
        self.refresh_button.configure(state="disabled")
        self.progress_var.set(0)
        self.status_var.set("Starting data update...")
        
        # Run update in separate thread
        thread = threading.Thread(target=self._run_update, daemon=True)
        thread.start()
    
    def _run_update(self):
        """Run full data update"""
        try:
            success, result = data_fetcher.fetch_all_stocks_concurrent(
                update_callback=self._update_progress
            )
            
            # Update UI on main thread
            self.root.after(0, self._update_complete, success, result)
            
        except Exception as e:
            logger.error(f"Update failed: {e}")
            self.root.after(0, self._update_complete, False, {"error": str(e)})
    
    def _update_progress(self, progress: float, symbol: str, 
                        successful: int, failed: int):
        """Update progress callback"""
        def update_ui():
            self.progress_var.set(progress)
            self.status_var.set(f"Processing {symbol}... ({successful} success, {failed} failed)")
        
        self.root.after(0, update_ui)
    
    def _update_complete(self, success: bool, result: Dict):
        """Handle update completion"""
        self.is_updating = False
        self.update_button.configure(state="normal", text="Update Data")
        self.refresh_button.configure(state="normal")
        self.progress_var.set(1.0 if success else 0)
        
        if success:
            total_records = result.get('total_records', 0)
            successful_fetches = result.get('successful_fetches', 0)
            duration = result.get('duration_seconds', 0)
            
            self.status_var.set(f"Update complete: {total_records:,} records in {duration:.1f}s")
            
            # NEW: Mark data as updated in status panel
            self.status_panel.mark_data_updated()
            
            messagebox.showinfo(
                "Update Complete", 
                f"Successfully updated {successful_fetches} stocks\n"
                f"Total records: {total_records:,}\n"
                f"Duration: {duration:.1f} seconds"
            )
            
            # Automatically refresh the display after successful update
            self.refresh_data()
        else:
            error_msg = result.get('error', 'Unknown error')
            self.status_var.set(f"Update failed: {error_msg}")
            messagebox.showerror("Update Failed", f"Error: {error_msg}")
    
    def run(self):
        """Start the application"""
        logger.info("Starting main application")
        self.root.mainloop()

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