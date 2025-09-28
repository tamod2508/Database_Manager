"""
macOS notification manager
"""

import subprocess
import logging
from typing import Optional

from ..utils.logger import get_logger

logger = get_logger(__name__)

class NotificationManager:
    """Manager for macOS notifications"""
    
    def __init__(self):
        self.app_name = "Database Manager"
        
    def show_notification(self, title: str, message: str, 
                         sound: bool = True, subtitle: Optional[str] = None):
        """Show macOS notification using osascript"""
        
        try:
            # Build AppleScript command
            script_parts = [
                'display notification',
                f'"{message}"',
                f'with title "{title}"'
            ]
            
            if subtitle:
                script_parts.append(f'subtitle "{subtitle}"')
                
            if sound:
                script_parts.append('sound name "Glass"')
            
            script = ' '.join(script_parts)
            
            # Execute AppleScript
            result = subprocess.run([
                'osascript', '-e', script
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.debug(f"Notification sent: {title}")
            else:
                logger.warning(f"Notification failed: {result.stderr}")
                
        except Exception as e:
            logger.error(f"Failed to send notification: {e}")
    
    def show_update_progress(self, completed: int, total: int, current_symbol: str):
        """Show update progress notification"""
        
        progress_percent = int((completed / total) * 100) if total > 0 else 0
        
        self.show_notification(
            title="Data Update Progress",
            message=f"{progress_percent}% complete - Processing {current_symbol}",
            sound=False
        )