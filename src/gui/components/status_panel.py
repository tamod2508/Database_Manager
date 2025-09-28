"""
Simple status monitoring panel - Fixed Last Updated Tracking
"""

import customtkinter as ctk
import tkinter as tk
from typing import Dict, Any
from datetime import datetime
import os
import json

from ...utils.logger import get_logger
from ...core.database_manager import db_manager

logger = get_logger(__name__)

class StatusPanel:
    """Simple status panel with persistent last update tracking"""
    
    def __init__(self, parent):
        self.parent = parent
        self.frame = ctk.CTkFrame(parent)
        
        # Path for storing last update info
        self.app_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        self.status_file = os.path.join(self.app_dir, 'data', 'last_update.json')
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup simple status UI"""
        
        # Title
        title_label = ctk.CTkLabel(
            self.frame,
            text="System Status",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title_label.pack(padx=10, pady=(10, 20))
        
        # Status text
        self.status_text = ctk.CTkTextbox(self.frame, height=200, width=200)
        self.status_text.pack(padx=10, pady=10, fill="both", expand=True)
        
        # Refresh button
        refresh_button = ctk.CTkButton(
            self.frame,
            text="Refresh",
            command=self.refresh_status,
            height=30
        )
        refresh_button.pack(padx=10, pady=10, fill="x")
        
        # Initial status
        self.refresh_status()
    
    def get_last_update_time(self):
        """Get the last update time from file - DATE ONLY"""
        try:
            if os.path.exists(self.status_file):
                with open(self.status_file, 'r') as f:
                    data = json.load(f)
                    full_timestamp = data.get('last_update', 'Never')
                    
                    # Extract only the date part (YYYY-MM-DD)
                    if full_timestamp != 'Never' and len(full_timestamp) >= 10:
                        return full_timestamp[:16]  # Get first 10 characters (date part)
                    return full_timestamp
            return 'Never'
        except Exception as e:
            logger.warning(f"Could not read last update time: {e}")
            return 'Never'
    
    def save_last_update_time(self, update_time=None):
        """Save the last update time to file"""
        try:
            # Ensure data directory exists
            os.makedirs(os.path.dirname(self.status_file), exist_ok=True)
            
            if update_time is None:
                update_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            data = {
                'last_update': update_time,
                'timestamp': datetime.now().isoformat()
            }
            
            with open(self.status_file, 'w') as f:
                json.dump(data, f, indent=2)
                
            logger.info(f"Saved last update time: {update_time}")
            
        except Exception as e:
            logger.error(f"Could not save last update time: {e}")
    
    def update_status(self, stats: Dict[str, Any]):
        """Update status display"""
        try:
            # Get the persistent last update time
            last_updated = self.get_last_update_time()
            
            # Determine connection status based on data availability
            total_records = stats.get('total_records', 0)
            connection_active = total_records > 0  # If we have data, connection is working
            
            status_text = f"""Database Status:

Records: {total_records:,}
Tickers: {stats.get('unique_tickers', 0)}
Size: {stats.get('database_size_mb', 0):.1f} MB

Date Range:
{stats.get('earliest_date', 'N/A')} to
{stats.get('latest_date', 'N/A')}

Last Update Date:
{last_updated[:10]}
Last Update Time:
{last_updated[11:16]}

Connection: {'✅ Active' if connection_active else '❌ Inactive'}
"""
            
            self.status_text.delete("1.0", "end")
            self.status_text.insert("1.0", status_text)
            
        except Exception as e:
            logger.error(f"Failed to update status: {e}")
    
    def refresh_status(self):
        """Refresh status from database"""
        try:
            stats = db_manager.get_database_stats()
            self.update_status(stats)
        except Exception as e:
            logger.error(f"Failed to refresh status: {e}")
            self.status_text.delete("1.0", "end")
            self.status_text.insert("1.0", f"Error getting status:\n{e}")
    
    def mark_data_updated(self):
        """Call this method when data is successfully updated"""
        self.save_last_update_time()
        self.refresh_status()  # Refresh display to show new update time