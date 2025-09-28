"""
Application configuration settings
This file will create the paths and directories used in the app also it will detect what OS we are on currently and optimize accordingly
"""

import os
from pathlib import Path
from dataclasses import dataclass
from typing import Optional
import subprocess
from datetime import datetime

@dataclass
class AppConfig:
    """Main application configuration"""
    
    # Paths
    BASE_DIR: Path = Path(__file__).parent.parent.parent
    DATA_DIR: Path = BASE_DIR / "data"
    DB_DIR: Path = DATA_DIR / "db" 
    LOGS_DIR: Path = BASE_DIR / "logs"
    
    # Database
    DB_NAME: str = "historical_data.db"  
    DB_PATH: Path = DB_DIR / DB_NAME
    
    # Data source
    COMPANIES_CSV: Path = DATA_DIR / "stock_list.csv"  
    START_DATE: str = "2010-01-01"
    END_DATE: str = datetime.now().strftime('%Y-%m-%d')  # Dynamic end date - TODAY
    
    # Update settings  
    UPDATE_SCHEDULE_WEEKDAY: int = 0  # Sunday
    UPDATE_SCHEDULE_HOUR: int = 9
    UPDATE_SCHEDULE_MINUTE: int = 0
    
    # Performance
    CHUNK_SIZE: int = 500 #yfinance has a rate limit of 500-1000 stocks this avoids failure for larger requests, also helps in RAM optimization, different then the chunk_size in database manager
    MAX_WORKERS: Optional[int] = None
    
    # GUI settings
    WINDOW_WIDTH: int = 1200
    WINDOW_HEIGHT: int = 800
    THEME: str = "dark"
    
    def __post_init__(self):
        """Initialize computed values and create directories"""
        
        # Create directories
        for directory in [self.DATA_DIR, self.DB_DIR, self.LOGS_DIR]:
            directory.mkdir(parents=True, exist_ok=True)
            
        # Detect hardware and set optimal worker count
        self.is_apple_silicon = self._detect_apple_silicon()
        self.cpu_count = os.cpu_count() or 4
        
        if self.MAX_WORKERS is None:
            if self.is_apple_silicon:
                self.MAX_WORKERS = min(self.cpu_count * 2, 12)
            else:
                self.MAX_WORKERS = min(self.cpu_count, 8)
    
    def _detect_apple_silicon(self) -> bool:
        """Detect if running on Apple Silicon"""
        try:
            result = subprocess.run(['uname', '-m'], 
                                  capture_output=True, text=True)
            return result.stdout.strip() == 'arm64'
        except:
            return False
    
    @property
    def db_url(self) -> str:
        """SQLAlchemy database URL"""
        return f"sqlite:///{self.DB_PATH}"

# Global config instance
config = AppConfig()