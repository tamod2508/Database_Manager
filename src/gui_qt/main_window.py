"""
Main PySide6 application window - Full integration with existing core systems
"""

import sys
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QSplitter, QTabWidget, QGroupBox, QPushButton, 
    QLabel, QTextEdit, QStatusBar, QMessageBox, 
    QApplication
)
from PySide6.QtCore import (
    Qt, QThread, Signal, QTimer
)
from PySide6.QtGui import QFont
import pandas as pd
import threading
from typing import Dict

from ..config.settings import config
from ..core.database_manager import db_manager
from ..core.data_fetcher import data_fetcher
from ..utils.logger import get_logger
from .pages.stock_status_page import StockStatusPage
from .pages.data_viewer_page import DataViewerPage
from .pages.settings_page import SettingsPage
from .dialogs.progress_dialog import ProgressDialog
from .dialogs.update_plan_dialog import UpdatePlanDialog

logger = get_logger(__name__, "GUI.log")

class UpdateWorker(QThread):
    """Background worker for data updates"""
    # Fix: Use Signal instead of pyqtSignal
    progress_update = Signal(float, str, int, int)  # progress, symbol, successful, failed
    update_complete = Signal(bool, dict)  # success, result
    
    def __init__(self, incremental=True):
        super().__init__()
        self.incremental = incremental
        
    def run(self):
        """Run update in background thread"""
        try:
            if self.incremental:
                success, result = data_fetcher.update_stock_data(
                    update_callback=self._update_progress
                )
            else:
                success, result = data_fetcher.refresh_all_data(
                    update_callback=self._update_progress
                )
            
            self.update_complete.emit(success, result)
            
        except Exception as e:
            logger.error(f"Update failed: {e}")
            self.update_complete.emit(False, {"error": str(e)})
    
    def _update_progress(self, progress: float, symbol: str, successful: int, failed: int):
        """Update progress callback"""
        self.progress_update.emit(progress, symbol, successful, failed)

class MainWindow(QMainWindow):
    """Main application window with full core integration"""
    
    def __init__(self):
        super().__init__()
        self.current_data = pd.DataFrame()
        self.is_updating = False
        self.update_worker = None
        self.progress_dialog = None
        
        # Initialize database (same as your existing GUI)
        try:
            db_manager.initialize()
            logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            QMessageBox.critical(self, "Database Error", 
                               f"Failed to initialize database: {e}")
        
        self.setup_ui()
        self.load_initial_data()
        
        logger.info("PySide6 main window initialized")
        
    def setup_ui(self):
        """Setup the professional user interface"""
        self.setWindowTitle("Database Manager")
        self.setGeometry(100, 100, config.WINDOW_WIDTH, config.WINDOW_HEIGHT)
        self.setMinimumSize(800, 600)
        
        # Create central widget with splitter
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Create splitter for sidebar and main content
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)
        
        # Setup components
        self.setup_sidebar(splitter)
        self.setup_main_content(splitter)
        
        # Set splitter proportions (sidebar smaller)
        splitter.setSizes([280, 920])
        splitter.setChildrenCollapsible(False)  # Prevent collapsing
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready - Click 'Refresh View' to load existing data or 'Update Data' to fetch latest")
        
    def setup_sidebar(self, parent):
        """Setup left sidebar with controls and status"""
        sidebar = QWidget()
        sidebar.setMaximumWidth(320)
        sidebar.setMinimumWidth(260)
        sidebar.setProperty("class", "sidebar")
        
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)
        
        # Title
        title = QLabel("Database Manager")
        title.setAlignment(Qt.AlignCenter)
        title.setProperty("class", "sidebar-title")
        layout.addWidget(title)
        
        # Update controls group
        self.setup_update_controls(layout)
        
        # Status display (integrated from your existing status panel)
        self.setup_status_display(layout)
        
        layout.addStretch()
        parent.addWidget(sidebar)
        
    def setup_update_controls(self, layout):
        """Setup update control buttons"""
        controls_group = QGroupBox("Data Controls")

        
        controls_layout = QVBoxLayout(controls_group)
        controls_layout.setSpacing(10)
        
        # Check Update Plan button
        self.plan_btn = QPushButton("📋 Check Update Plan")
        self.plan_btn.setProperty("class", "neutral")
        self.plan_btn.clicked.connect(self.show_update_plan)
        controls_layout.addWidget(self.plan_btn)
        
        # Incremental Update button (primary)
        self.update_btn = QPushButton("🔄 Update Data")
        self.update_btn.setProperty("class", "primary")
        self.update_btn.clicked.connect(self.start_incremental_update)
        controls_layout.addWidget(self.update_btn)
        
        # Full Refresh button (secondary)
        self.refresh_btn = QPushButton("🔄 Full Refresh")
        self.refresh_btn.setProperty("class", "secondary")
        self.refresh_btn.clicked.connect(self.start_full_refresh)
        controls_layout.addWidget(self.refresh_btn)
        
        # Refresh View button
        self.view_refresh_btn = QPushButton("📊 Refresh View")
        self.view_refresh_btn.setProperty("class", "info")
        self.view_refresh_btn.clicked.connect(self.refresh_data)
        controls_layout.addWidget(self.view_refresh_btn)
        
        layout.addWidget(controls_group)
        
    def setup_status_display(self, layout):
        """Setup status display (integrated from your existing status_panel.py)"""
        status_group = QGroupBox("System Status")

        
        status_layout = QVBoxLayout(status_group)
        
        # Status text display (rich HTML like your existing status panel)
        self.status_display = QTextEdit()
        self.status_display.setMaximumHeight(200)
        self.status_display.setReadOnly(True)

        status_layout.addWidget(self.status_display)
        
        layout.addWidget(status_group)
        
    def setup_main_content(self, parent):
        """Setup main content area with tabs"""
        # Create tab widget
        self.tab_widget = QTabWidget()

        
        # Create pages (will implement these next)
        self.stock_status_page = StockStatusPage()
        self.data_viewer_page = DataViewerPage() 
        self.settings_page = SettingsPage()
        
        # Add tabs
        self.tab_widget.addTab(self.stock_status_page, "📈 Stock Status")
        self.tab_widget.addTab(self.data_viewer_page, "📊 Data Viewer")
        self.tab_widget.addTab(self.settings_page, "⚙️ Settings")
        
        parent.addWidget(self.tab_widget)
        
    def load_initial_data(self):
        """Load initial data after UI is ready"""
        # Use QTimer for delayed loading (same pattern as your existing GUI)
        QTimer.singleShot(1000, self.refresh_data)
        
    def refresh_data(self):
        """Refresh data from database (same logic as your existing GUI)"""
        try:
            self.status_bar.showMessage("Loading data from database...")
            QApplication.processEvents()  # Update UI immediately
            
            # Get data from database (same as your existing implementation)
            self.current_data = db_manager.get_stock_data()
            
            if not self.current_data.empty:
                # Update data viewer
                self.data_viewer_page.update_data(self.current_data)
                
                # Update stock status page
                self.stock_status_page.refresh_status()
                
                # Update status display
                unique_tickers = len(self.current_data['ticker'].unique())
                total_records = len(self.current_data)
                latest_date = self.current_data['date'].max().strftime('%Y-%m-%d') if not self.current_data.empty else 'N/A'
                
                self.status_bar.showMessage(
                    f"Loaded {total_records:,} records from {unique_tickers} tickers (latest: {latest_date})"
                )
                
                logger.info(f"Data refreshed: {total_records} records, {unique_tickers} tickers")
            else:
                self.status_bar.showMessage("No data available - Click 'Update Data' to fetch stock data")
                logger.info("No data found in database")
            
            # Update status display (same as your existing status panel)
            self.update_status_display()
            
        except Exception as e:
            logger.error(f"Data refresh failed: {e}")
            self.status_bar.showMessage(f"Error loading data: {str(e)}")
            QMessageBox.critical(self, "Refresh Error", f"Failed to refresh data:\n{str(e)}")
    
    def update_status_display(self):
        """Update status display (integrated from your status_panel.py)"""
        try:
            # Get database stats (same as your existing implementation)
            stats = db_manager.get_database_stats()
            
            # Get last update time (same logic as your status panel)
            last_updated = self.get_last_update_time()
            
            # Format status with HTML (enhanced from your existing status panel)
            status_html = f"""
            <div style="color: #ffffff; font-family: 'Courier New', monospace;">
                <h3 style="color: #3daee9; margin-bottom: 10px;">📊 Database Status</h3>
                
                <p><span style="color: #28a745;">●</span> <b>Records:</b> {stats.get('total_records', 0):,}</p>
                <p><span style="color: #28a745;">●</span> <b>Tickers:</b> {stats.get('unique_tickers', 0)}</p>
                <p><span style="color: #28a745;">●</span> <b>Size:</b> {stats.get('database_size_mb', 0):.1f} MB</p>
                
                <h4 style="color: #3daee9; margin-top: 15px;">📅 Date Range:</h4>
                <p>{stats.get('earliest_date', 'N/A')} to<br>{stats.get('latest_date', 'N/A')}</p>
                
                <h4 style="color: #3daee9; margin-top: 15px;">🕒 Last Update:</h4>
                <p><b>Date:</b> {last_updated[:10] if last_updated != 'Never' else 'Never'}</p>
                <p><b>Time:</b> {last_updated[11:16] if len(last_updated) > 11 else 'N/A'}</p>
                
                <p style="margin-top: 15px;">
                    <span style="color: #28a745;">✅</span> <b>Status:</b> 
                    {'Active' if stats.get('total_records', 0) > 0 else 'Inactive'}
                </p>
            </div>
            """
            
            self.status_display.setHtml(status_html)
            
        except Exception as e:
            logger.error(f"Failed to update status display: {e}")
            self.status_display.setPlainText(f"Error getting status: {e}")
    
    def get_last_update_time(self):
        """Get last update time (simplified working version)"""
        try:
            import os
            import json
            from pathlib import Path
            
            # Simple working path - directly from project root
            status_file = Path('data/last_update.json')
            
            if status_file.exists():
                with open(status_file, 'r') as f:
                    data = json.load(f)
                    full_timestamp = data.get('last_update', 'Never')
                    
                    if full_timestamp != 'Never' and len(full_timestamp) >= 10:
                        return full_timestamp[:16]  # Date + time
                    return full_timestamp
            return 'Never'
        except Exception as e:
            logger.warning(f"Could not read last update time: {e}")
            return 'Never' 
        except Exception as e:
            logger.warning(f"Could not read last update time: {e}")
            return 'Never'
    
    def save_last_update_time(self, update_time=None):
        """Save last update time (simplified working version)"""
        try:
            import os
            import json
            from datetime import datetime
            from pathlib import Path
            
            # Simple working path - directly from project root
            status_file = Path('data/last_update.json')
            
            # Ensure data directory exists
            os.makedirs(status_file.parent, exist_ok=True)
            
            if update_time is None:
                update_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            data = {
                'last_update': update_time,
                'timestamp': datetime.now().isoformat()
            }
            
            with open(status_file, 'w') as f:
                json.dump(data, f, indent=2)
                
            logger.info(f"Saved last update time: {update_time}")
            
        except Exception as e:
            logger.error(f"Could not save last update time: {e}")
            logger.error(f"Tried path: {status_file if 'status_file' in locals() else 'unknown'}")
    
    def show_update_plan(self):
        """Show update plan (same logic as your existing GUI)"""
        try:
            self.status_bar.showMessage("Analyzing update requirements...")
            QApplication.processEvents()
            
            # Get update plan (same as your existing implementation)
            plan = data_fetcher.get_update_plan()
            
            # Show in dialog instead of message box
            dialog = UpdatePlanDialog(plan, self)
            dialog.exec()
            
            self.status_bar.showMessage("Update plan ready - see dialog for details")
            
        except Exception as e:
            logger.error(f"Failed to get update plan: {e}")
            self.status_bar.showMessage(f"Error getting update plan: {e}")
            QMessageBox.critical(self, "Error", f"Failed to analyze update plan:\n{str(e)}")
    
    def start_incremental_update(self):
        """Start incremental update (same logic as your existing GUI)"""
        if self.is_updating:
            QMessageBox.information(self, "Update in Progress", "Data update is already running")
            return
        
        try:
            # Get update plan first (same as your existing implementation)
            plan = data_fetcher.get_update_plan()
            
            need_full = len(plan['symbols_needing_full_fetch'])
            need_update = len(plan['symbols_needing_update'])
            up_to_date = len(plan['symbols_up_to_date'])
            
            if need_full == 0 and need_update == 0:
                QMessageBox.information(self, "No Updates Needed", "All data is up to date!")
                return
            
            # Show update summary (same as your existing GUI)
            message = "Incremental Update Summary:\n\n"
            if need_full > 0:
                message += f"• {need_full} symbols need full data fetch\n"
            if need_update > 0:
                message += f"• {need_update} symbols need recent data update\n"
            if up_to_date > 0:
                message += f"• {up_to_date} symbols are already up to date\n"
            message += "\nThis will only fetch missing data, saving time and API calls.\n\nContinue?"
            
            result = QMessageBox.question(self, "Incremental Update", message)
            if result == QMessageBox.Yes:
                self._start_update_thread(incremental=True)
                
        except Exception as e:
            logger.error(f"Failed to start incremental update: {e}")
            QMessageBox.critical(self, "Error", f"Failed to start update:\n{str(e)}")
    
    def start_full_refresh(self):
        """Start full refresh (same logic as your existing GUI)"""
        if self.is_updating:
            QMessageBox.information(self, "Update in Progress", "Data update is already running")
            return
        
        # Strong warning (same as your existing GUI)
        result = QMessageBox.warning(
            self, "⚠️ Full Refresh Warning",
            "FULL REFRESH will fetch ALL data from the start date.\n\n"
            "This will:\n"
            "• Take significantly longer\n"
            "• Use many more API calls\n"
            "• Re-fetch data you already have\n\n"
            "Only use this if:\n"
            "• You want to rebuild the entire database\n"
            "• You suspect data corruption\n"
            "• You changed the date range settings\n\n"
            "Continue with FULL REFRESH?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if result == QMessageBox.Yes:
            # Double confirmation
            confirm = QMessageBox.question(
                self, "Final Confirmation",
                "Are you absolutely sure you want to fetch ALL data from scratch?\n\n"
                "This cannot be undone and will take much longer.",
                QMessageBox.Yes | QMessageBox.No
            )
            if confirm == QMessageBox.Yes:
                self._start_update_thread(incremental=False)
    
    def _start_update_thread(self, incremental=True):
        """Start update in background thread (enhanced from your existing GUI)"""
        self.is_updating = True
        
        # Update UI state
        self.update_btn.setEnabled(False)
        self.refresh_btn.setEnabled(False)
        self.view_refresh_btn.setEnabled(False)
        self.plan_btn.setEnabled(False)
        
        mode_text = "Updating..." if incremental else "Refreshing..."
        if incremental:
            self.update_btn.setText(f"🔄 {mode_text}")
        else:
            self.refresh_btn.setText(f"🔄 {mode_text}")
        
        # Create and show progress dialog
        self.progress_dialog = ProgressDialog(incremental, self)
        self.progress_dialog.show()
        
        # Create and start worker thread
        self.update_worker = UpdateWorker(incremental)
        self.update_worker.progress_update.connect(self.progress_dialog.update_progress)
        self.update_worker.update_complete.connect(self._update_complete)
        self.update_worker.start()
    
    def _update_complete(self, success: bool, result: Dict):
        """Handle update completion (same logic as your existing GUI)"""
        self.is_updating = False
        
        # Close progress dialog
        if self.progress_dialog:
            self.progress_dialog.close()
            self.progress_dialog = None
        
        # Restore UI state
        self.update_btn.setEnabled(True)
        self.refresh_btn.setEnabled(True)
        self.view_refresh_btn.setEnabled(True)
        self.plan_btn.setEnabled(True)
        
        self.update_btn.setText("🔄 Update Data")
        self.refresh_btn.setText("🔄 Full Refresh")
        
        if success:
            mode = result.get('mode', 'update')
            total_records = result.get('total_records', 0)
            successful_fetches = result.get('successful_fetches', 0)
            skipped_fetches = result.get('skipped_fetches', 0)
            duration = result.get('duration_seconds', 0)
            
            # Different messages based on results (same as your existing GUI)
            if total_records == 0:
                self.status_bar.showMessage("All data is up to date - no new records fetched")
                message_text = "No new data was available to fetch.\n\nAll symbols are up to date!"
                title = "No Updates Needed"
            else:
                self.status_bar.showMessage(f"{mode.title()} complete: {total_records:,} records in {duration:.1f}s")
                
                message_text = f"{mode.title()} completed successfully!\n\n"
                message_text += f"Successfully updated: {successful_fetches} symbols\n"
                message_text += f"New records added: {total_records:,}\n"
                if skipped_fetches > 0:
                    message_text += f"Symbols already up to date: {skipped_fetches}\n"
                message_text += f"Duration: {duration:.1f} seconds"
                title = "Update Complete"
            
            # Save update time (same as your existing GUI)
            self.save_last_update_time()
            
            QMessageBox.information(self, title, message_text)
            
            # Automatically refresh display after successful update
            if total_records > 0:
                self.refresh_data()
        else:
            error_msg = result.get('error', 'Unknown error')
            mode = result.get('mode', 'update')
            self.status_bar.showMessage(f"{mode.title()} failed: {error_msg}")
            QMessageBox.critical(self, "Update Failed", f"Error during {mode}:\n\n{error_msg}")
    
    def closeEvent(self, event):
        """Handle application close"""
        if self.is_updating:
            result = QMessageBox.question(
                self, "Update in Progress",
                "Data update is running. Close anyway?",
                QMessageBox.Yes | QMessageBox.No
            )
            if result != QMessageBox.Yes:
                event.ignore()
                return
        
        logger.info("PySide6 GUI closing")
        event.accept()
