"""
Database management with Apple Silicon optimizations - TIMEZONE FIX
Sqlite does not handle timezones well , so we have to remove the timezones and only use date
"""

import sqlite3
import pandas as pd
from sqlalchemy import create_engine, text
from typing import Optional, List, Dict, Any
import logging
from pathlib import Path

from ..config.settings import config
from .apple_silicon_optimizer import optimizer
from ..utils.logger import get_logger

logger = get_logger(__name__)

class DatabaseManager:
    """Optimized database manager for stock data"""
    
    def __init__(self):
        self.db_path = config.DB_PATH
        self.engine = None
        self.is_initialized = False #Tracks whether database has been set up, Prevent duplicate initialization,Ensure database is ready before operations
        self.optimal_settings = optimizer.get_optimal_settings()
        
    def initialize(self):
        """Initialize database with optimizations"""
        try:
            self.engine = create_engine(
                config.db_url,
                echo=False, #False: Don't print SQL statements to console
                pool_pre_ping=True, #Test connections before use, Prevents "database is locked" errors
                pool_recycle=3600 #Recycle connections every 3600 seconds (1 hour), prevents connection timeout issues
            )
            
            self._apply_sqlite_optimizations()
            self._create_tables()
            
            self.is_initialized = True
            logger.info("Database initialized successfully")
            
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            raise
    
    def _apply_sqlite_optimizations(self):
        """Apply SQLite optimizations"""
        optimization_queries = [
            "PRAGMA journal_mode = WAL", #Sets SQLite to WAL (Write-Ahead Logging) mode for better concurrency, faster writes and better crash recovery
            "PRAGMA synchronous = NORMAL",
            f"PRAGMA cache_size = {self.optimal_settings['cache_size']}",
            "PRAGMA optimize" #Runs SQLite's automatic optimization,Updates statistics, reorganizes indexes
        ]
        
        try:
            with self.engine.connect() as conn:
                for query in optimization_queries:
                    conn.execute(text(query)) #text(query): SQLAlchemy wrapper for raw SQL
                    conn.commit()
                logger.info("SQLite optimizations applied")
        except Exception as e:
            logger.warning(f"Could not apply all optimizations: {e}")
    
    def _create_tables(self):
        """Create database tables"""
        create_table_query = '''
        CREATE TABLE IF NOT EXISTS stock_data (
            ticker TEXT NOT NULL,
            date DATE NOT NULL,
            open REAL,
            high REAL,
            low REAL,
            close REAL,
            volume INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (ticker, date)
        );
        '''
        
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_ticker_date ON stock_data(ticker, date);",
            "CREATE INDEX IF NOT EXISTS idx_date ON stock_data(date);",
            "CREATE INDEX IF NOT EXISTS idx_ticker ON stock_data(ticker);"
        ]
        
        try:
            with self.engine.connect() as conn:
                conn.execute(text(create_table_query))
                for index_query in indexes:
                    conn.execute(text(index_query))
                conn.commit()
                logger.info("Database tables and indexes created")
        except Exception as e:
            logger.error(f"Table creation failed: {e}")
            raise
    
    def insert_dataframe_chunked(self, df: pd.DataFrame) -> bool:
        """Insert DataFrame with proper timezone handling"""
        if not self.is_initialized:
            self.initialize()
            
        if df.empty:
            logger.warning("Attempted to insert empty DataFrame")
            return False
        
        try:
            # TIMEZONE FIX: Convert timezone-aware dates to naive dates
            df_copy = df.copy()
            
            if 'date' in df_copy.columns:
                # Convert to datetime and remove timezone info
                df_copy['date'] = pd.to_datetime(df_copy['date'])
                if df_copy['date'].dt.tz is not None:
                    df_copy['date'] = df_copy['date'].dt.tz_localize(None)
                # Convert to string format for database
                df_copy['date'] = df_copy['date'].dt.strftime('%Y-%m-%d')
            
            chunk_size = 10000
            total_rows = len(df_copy)
            inserted_count = 0
            
            logger.info(f"Inserting {total_rows} rows in chunks of {chunk_size}")
            
            with self.engine.connect() as conn:
                for i in range(0, total_rows, chunk_size):
                    chunk = df_copy.iloc[i:i+chunk_size]
                    
                    for _, row in chunk.iterrows():
                        try:
                            insert_query = text("""
                                INSERT OR REPLACE INTO stock_data 
                                (ticker, date, open, high, low, close, volume) 
                                VALUES (:ticker, :date, :open, :high, :low, :close, :volume)
                            """)
                            
                            conn.execute(insert_query, {
                                'ticker': str(row['ticker']),
                                'date': str(row['date']),
                                'open': float(row['open']) if pd.notna(row['open']) else None,
                                'high': float(row['high']) if pd.notna(row['high']) else None,
                                'low': float(row['low']) if pd.notna(row['low']) else None,
                                'close': float(row['close']) if pd.notna(row['close']) else None,
                                'volume': int(row['volume']) if pd.notna(row['volume']) else None
                            })
                            inserted_count += 1
                            
                        except Exception as e:
                            logger.debug(f"Skipped row: {e}")
                    
                    conn.commit()
                    if (i // chunk_size + 1) % 10 == 0:
                        logger.info(f"Processed {i + len(chunk)} / {total_rows} rows")
            
            logger.info(f"Successfully inserted {inserted_count} rows")
            return inserted_count > 0
            
        except Exception as e:
            logger.error(f"Data insertion failed: {e}")
            return False
        

    def get_stock_data(self, ticker: Optional[str] = None) -> pd.DataFrame:
        """Retrieve stock data"""
        if not self.is_initialized:
            self.initialize()
            
        try:
            query = "SELECT * FROM stock_data"
            params = {}
            
            if ticker:
                query += " WHERE ticker = :ticker"
                params["ticker"] = ticker
                
            query += " ORDER BY ticker, date"
            
            with self.engine.connect() as conn:
                df = pd.read_sql(text(query), conn, params=params)
                
            if not df.empty and 'date' in df.columns:
                df["date"] = pd.to_datetime(df["date"])
            
            return df
            
        except Exception as e:
            logger.error(f"Data retrieval failed: {e}")
            return pd.DataFrame()
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        if not self.is_initialized:
            self.initialize()
            
        try:
            with self.engine.connect() as conn:
                stats_query = text("""
                    SELECT 
                        COUNT(*) as total_records,
                        COUNT(DISTINCT ticker) as unique_tickers,
                        MIN(date) as earliest_date,
                        MAX(date) as latest_date
                    FROM stock_data
                """)
                
                result = conn.execute(stats_query).fetchone()
                db_size_mb = self.db_path.stat().st_size / (1024 * 1024) if self.db_path.exists() else 0
                
                return {
                    'total_records': result[0] if result and result[0] else 0,
                    'unique_tickers': result[1] if result and result[1] else 0,
                    'earliest_date': result[2] if result else None,
                    'latest_date': result[3] if result else None,
                    'database_size_mb': round(db_size_mb, 2),
                    'database_path': str(self.db_path)
                }
                
        except Exception as e:
            logger.error(f"Stats retrieval failed: {e}")
            return {'total_records': 0, 'unique_tickers': 0, 'database_size_mb': 0}

# Global instance
db_manager = DatabaseManager()
