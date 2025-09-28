"""
Menu bar application using rumps - Enhanced with Visual Feedback
"""


import rumps
import subprocess
import threading
import time
from datetime import datetime

from ..config.settings import config
from ..core.database_manager import db_manager
from ..core.data_fetcher import data_fetcher
from ..utils.logger import get_logger
from .notifications import NotificationManager

logger = get_logger(__name__, "menubar.log")

class NiftyMenuBarApp(rumps.App):
    """Menu bar application for stock monitoring with visual feedback"""
    
    def __init__(self):
        super(NiftyMenuBarApp, self).__init__(
            name="Database Manager",
            title="📊",
            quit_button=None
        )

        # Hide from dock
        rumps.App.hide_dock_icon = True
        
        self.notification_manager = NotificationManager()
        self.is_updating = False
        self.last_status_check = None
        
        # Animation state for visual feedback
        self.is_animating = False
        self.animation_thread = None
        self.base_icon = "📊"
        self.animation_frames = ["📊🔄", "📊⏳", "📊🔃", "📊⌛"]
        self.current_frame = 0
        
        # Initialize database
        try:
            db_manager.initialize()
            logger.info("Database initialized for menu bar app")
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
        
        # Setup menu
        self.setup_menu()
        
        # Start status monitoring
        self.start_status_monitoring()
        
        logger.info("Menu bar app initialized")
    
    def start_animation(self, operation_name="Working"):
        """Start the spinning animation"""
        if self.is_animating:
            return
            
        self.is_animating = True
        self.current_frame = 0
        
        def animate():
            while self.is_animating:
                if self.is_animating:  # Double check
                    self.title = self.animation_frames[self.current_frame]
                    self.current_frame = (self.current_frame + 1) % len(self.animation_frames)
                time.sleep(0.5)  # Change frame every 500ms
        
        self.animation_thread = threading.Thread(target=animate, daemon=True)
        self.animation_thread.start()
        
        # Update status to show what's happening
        if hasattr(self, 'status_item'):
            self.status_item.title = f"🔄 {operation_name}..."
    
    def stop_animation(self):
        """Stop the spinning animation"""
        self.is_animating = False
        if self.animation_thread:
            self.animation_thread = None
        # Restore base icon
        self.title = "📊"
    
    def set_loading_state(self, message="Loading"):
        """Set the menu bar to loading state"""
        self.start_animation(message)
    
    def clear_loading_state(self):
        """Clear the loading state"""
        self.stop_animation()
        # Update status immediately
        threading.Thread(target=self.update_status, daemon=True).start()
    
    def setup_menu(self):
        """Setup the menu bar menu"""
        
        # Status item (will be updated dynamically)
        self.status_item = rumps.MenuItem("🔄 Checking status...")
        self.menu.add(self.status_item)
        
        # Separator
        self.menu.add(rumps.separator)
        
        # Actions
        self.menu.add(rumps.MenuItem("📊 Open GUI", callback=self.open_gui))
        self.menu.add(rumps.MenuItem("🔄 Update Data", callback=self.update_data))
        self.menu.add(rumps.MenuItem("📈 Quick Stats", callback=self.show_stats))
        
        # Separator
        self.menu.add(rumps.separator)
        
        # Settings
        self.menu.add(rumps.MenuItem("⚙️ Preferences", callback=self.open_preferences))
        self.menu.add(rumps.MenuItem("📋 View Logs", callback=self.view_logs))
        
        # Separator
        self.menu.add(rumps.separator)
        
        # Help & About
        self.menu.add(rumps.MenuItem("ℹ️ About", callback=self.show_about))
        self.menu.add(rumps.MenuItem("❌ Quit", callback=self.quit_app))
    
    def start_status_monitoring(self):
        """Start background status monitoring"""
        def monitor():
            while True:
                try:
                    if not self.is_animating:  # Don't update status during animations
                        self.update_status()
                    time.sleep(60)  # Check every minute
                except Exception as e:
                    logger.error(f"Status monitoring error: {e}")
                    time.sleep(60)
        
        monitor_thread = threading.Thread(target=monitor, daemon=True)
        monitor_thread.start()
    
    def update_status(self):
        """Update menu bar status - FIXED VERSION"""
        try:
            stats = db_manager.get_database_stats()
            
            if not stats or stats.get('total_records', 0) == 0:
                self.title = "📊❌"
                self.status_item.title = "❌ No data available"
                return
            
            # Get record counts
            unique_tickers = stats.get('unique_tickers', 0)
            latest_date = stats.get('latest_date', '')
            
            # Check if we have recent data by looking at latest_date
            if latest_date:
                try:
                    # Parse the latest date (format: YYYY-MM-DD)
                    latest_dt = datetime.strptime(latest_date, '%Y-%m-%d')
                    days_old = (datetime.now() - latest_dt).days
                    
                    # Determine status based on data age
                    if days_old <= 3:
                        self.title = "📊✅"
                        status_text = f"✅ Current data ({unique_tickers} tickers, latest: {latest_date})"
                    elif days_old <= 7:
                        self.title = "📊✅"
                        status_text = f"✅ Recent data ({unique_tickers} tickers, {days_old}d old)"
                    elif days_old <= 14:
                        self.title = "📊⚠️"
                        status_text = f"⚠️ Getting old ({unique_tickers} tickers, {days_old}d old)"
                    else:
                        self.title = "📊❌"
                        status_text = f"❌ Stale data ({unique_tickers} tickers, {days_old}d old)"
                        
                except Exception as e:
                    logger.warning(f"Date parsing failed: {e}")
                    # Fallback - we have data, show green
                    self.title = "📊✅"
                    status_text = f"✅ Data available ({unique_tickers} tickers)"
            else:
                # No date info but we have data
                self.title = "📊✅"
                status_text = f"✅ Data available ({unique_tickers} tickers)"
            
            self.status_item.title = status_text
            self.last_status_check = datetime.now()
            
        except Exception as e:
            logger.error(f"Status update failed: {e}")
            self.title = "📊❌"
            self.status_item.title = "❌ Status check failed"
    
    @rumps.clicked("📊 Open GUI")
    def open_gui(self, _):
        """Open the main GUI application"""
        try:
            # Show loading state
            self.set_loading_state("Opening GUI")
            
            import os
            import subprocess
            from pathlib import Path
            
            # Get the correct paths
            app_dir = Path(__file__).parent.parent.parent
            gui_script = app_dir / "run_gui.py"
            python_exe = app_dir / "data_env" / "bin" / "python3"
            
            if not gui_script.exists():
                self.clear_loading_state()
                rumps.alert("GUI Not Found", f"Could not find GUI script at {gui_script}")
                logger.error(f"GUI script not found at {gui_script}")
                return
            
            if not python_exe.exists():
                # Fallback to system python
                python_exe = "python3"
            
            # Launch GUI in background
            env = os.environ.copy()
            env['TK_SILENCE_DEPRECATION'] = '1'
            
            process = subprocess.Popen(
                [str(python_exe), str(gui_script)],
                cwd=str(app_dir),
                env=env,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
                start_new_session=True
            )
            
            logger.info(f"GUI application launched with PID {process.pid}")
            
            # Clear loading state after delay
            def clear_after_delay():
                time.sleep(2)
                self.clear_loading_state()
            threading.Thread(target=clear_after_delay, daemon=True).start()
            
        except FileNotFoundError as e:
            error_msg = f"File not found: {e}"
            logger.error(error_msg)
            self.clear_loading_state()
            rumps.alert("Launch Error", error_msg)
        except Exception as e:
            error_msg = f"Failed to open GUI: {e}"
            logger.error(error_msg)
            self.clear_loading_state()
            rumps.alert("Error", error_msg)
    
    @rumps.clicked("🔄 Update Data")
    def update_data(self, _):
        """Start data update"""
        if self.is_updating:
            rumps.alert("Update in Progress", "Data update is already running")
            return
        
        # Confirm update
        response = rumps.alert(
            title="Update Data",
            message="This will fetch the latest stock data. Continue?",
            ok="Update",
            cancel="Cancel"
        )
        
        if response == 1:  # OK clicked
            self.start_update_background()
    
    def start_update_background(self):
        """Start update in background thread with visual feedback"""
        def update():
            try:
                self.is_updating = True
                
                # Start visual feedback
                self.set_loading_state("Updating Data")
                
                logger.info("Starting data update from menu bar")
                
                # Show start notification
                self.notification_manager.show_notification(
                    "Data Update Started",
                    "Fetching latest stock data...",
                    sound=False
                )
                
                # Perform update
                success, result = data_fetcher.fetch_all_stocks_concurrent()
                
                if success:
                    message = f"Updated {result.get('successful_fetches', 0)} stocks"
                    logger.info(f"Update completed successfully: {message}")
                    
                    # SAVE UPDATE TIME TO SYNC WITH GUI
                    self.save_last_update_time()
                    
                    self.notification_manager.show_notification(
                        "Update Complete ✅",
                        message,
                        sound=True
                    )
                else:
                    error_msg = result.get('error', 'Unknown error')
                    logger.error(f"Update failed: {error_msg}")
                    
                    self.notification_manager.show_notification(
                        "Update Failed ❌",
                        f"Error: {error_msg}",
                        sound=True
    )
                
                # Stop animation and update status
                self.clear_loading_state()
                
            except Exception as e:
                logger.error(f"Update error: {e}")
                self.clear_loading_state()
                self.notification_manager.show_notification(
                    "Update Error ❌",
                    f"Unexpected error: {e}",
                    sound=True
                )
            finally:
                self.is_updating = False
        
        update_thread = threading.Thread(target=update, daemon=True)
        update_thread.start()
    
    @rumps.clicked("📈 Quick Stats")
    def show_stats(self, _):
        """Show quick database statistics"""
        try:
            # Show loading
            self.set_loading_state("Loading Stats")
            
            stats = db_manager.get_database_stats()
            
            # Clear loading
            self.clear_loading_state()
            
            if not stats:
                rumps.alert("No Data", "No database statistics available")
                return
            
            stats_text = f"""Total Records: {stats.get('total_records', 0):,}
Unique Tickers: {stats.get('unique_tickers', 0)}
Date Range: {stats.get('earliest_date', 'N/A')} to {stats.get('latest_date', 'N/A')}
Last Updated: {stats.get('last_updated', 'Never')[:10] if stats.get('last_updated') else 'Never'}
Database Size: {stats.get('database_size_mb', 0):.1f} MB"""
            
            rumps.alert("Database Statistics", stats_text)
            
        except Exception as e:
            logger.error(f"Stats display failed: {e}")
            self.clear_loading_state()
            rumps.alert("Error", f"Failed to get statistics: {e}")
    
    @rumps.clicked("⚙️ Preferences")
    def open_preferences(self, _):
        """Open preferences (launch GUI to settings tab)"""
        try:
            # For now, just open the main GUI
            self.open_gui(_)
            
        except Exception as e:
            logger.error(f"Failed to open preferences: {e}")
            rumps.alert("Error", f"Failed to open preferences: {e}")
    
    @rumps.clicked("📋 View Logs")
    def view_logs(self, _):
        """Open log directory in Finder"""
        try:
            subprocess.Popen(["open", str(config.LOGS_DIR)])
            
        except Exception as e:
            logger.error(f"Failed to open logs: {e}")
            rumps.alert("Error", f"Failed to open logs: {e}")
    
    @rumps.clicked("ℹ️ About")
    def show_about(self, _):
        """Show about information"""
        about_text = f"""Database Manager v1.0

A high-performance stock data management application optimized for Apple Silicon Macs.

Features:
- Automated weekly data updates
- Menu bar monitoring with visual feedback
- Apple Silicon optimizations
- Real-time data visualization

Database: {config.DB_PATH}
Logs: {config.LOGS_DIR}"""
        
        rumps.alert("About Database Manager", about_text)
    
    @rumps.clicked("❌ Quit")
    def quit_app(self, _):
        """Quit the application"""
        if self.is_updating:
            response = rumps.alert(
                title="Update in Progress",
                message="Data update is running. Quit anyway?",
                ok="Quit",
                cancel="Cancel"
            )
            if response != 1:  # Cancel clicked
                return
        
        # Stop any running animations
        self.is_animating = False
        
        logger.info("Menu bar app quitting")
        rumps.quit_application()

    def save_last_update_time(self, update_time=None):
        """Save the last update time to file"""
        try:
            import os
            import json
            from datetime import datetime
            from pathlib import Path
            
            # Get the app directory (same path as status panel)
            app_dir = Path(__file__).parent.parent.parent
            status_file = app_dir / 'data' / 'last_update.json'
            
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
                
            logger.info(f"Menu bar: Saved last update time: {update_time}")
            
        except Exception as e:
            logger.error(f"Menu bar: Could not save last update time: {e}")


def main():
    """Main entry point for menu bar app"""
    try:
        app = NiftyMenuBarApp()
        app.run()
    except KeyboardInterrupt:
        logger.info("Menu bar app interrupted")
    except Exception as e:
        logger.error(f"Menu bar app error: {e}")

if __name__ == "__main__":
    main()
