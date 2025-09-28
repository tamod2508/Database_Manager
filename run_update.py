#!/usr/bin/env python3
"""
Standalone update script for LaunchAgent - with timestamp saving
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def save_last_update_time(update_time=None):
    """Save the last update time to file - same as status panel"""
    try:
        app_dir = Path(__file__).parent
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
            
        print(f"Saved last update time: {update_time}")
        
    except Exception as e:
        print(f"Could not save last update time: {e}")

def main():
    try:
        from src.core.database_manager import db_manager
        from src.core.data_fetcher import data_fetcher
        from src.menubar.notifications import NotificationManager
        
        # Initialize
        db_manager.initialize()
        notification_manager = NotificationManager()
        
        # Send start notification
        notification_manager.show_notification(
            "Scheduled Update Started",
            "Weekly stock data update beginning...",
            sound=False
        )
        
        # Perform update
        success, result = data_fetcher.fetch_all_stocks_concurrent()
        
        if success:
            # SAVE UPDATE TIME WHEN SUCCESSFUL
            save_last_update_time()
            
            message = f"Updated {result.get('successful_fetches', 0)} stocks"
            notification_manager.show_notification(
                "Update Complete",
                message,
                sound=True
            )
            print(f"SUCCESS: {message}")
        else:
            error_msg = result.get('error', 'Unknown error')
            notification_manager.show_notification(
                "Update Failed",
                f"Error: {error_msg}",
                sound=True
            )
            print(f"ERROR: {error_msg}")
            sys.exit(1)
            
    except Exception as e:
        print(f"FATAL ERROR: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
