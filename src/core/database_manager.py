"""
Database management with Apple Silicon optimizations - TIMEZONE FIX
Sqlite does not handle timezones well , so we have to remove the timezones and only use date
"""

import pandas as pd
from sqlalchemy import create_engine, text
from typing import Optional, Dict,List,  Any

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
            is_missing BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (ticker, date)
        );
        '''

        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_ticker_date ON stock_data(ticker, date);",
            "CREATE INDEX IF NOT EXISTS idx_date ON stock_data(date);",
            "CREATE INDEX IF NOT EXISTS idx_ticker ON stock_data(ticker);",
            "CREATE INDEX IF NOT EXISTS idx_stock_data_missing ON stock_data(ticker, is_missing);"
        ]

        try:
            with self.engine.connect() as conn:
                # Create table
                conn.execute(text(create_table_query))

                # Create each index separately (IMPORTANT: one at a time!)
                for index_query in indexes:
                    conn.execute(text(index_query))

                conn.commit()
                logger.info("Database tables and indexes created")
        except Exception as e:
            logger.error(f"Table creation failed: {e}")
            raise
    def insert_dataframe_chunked(self, df: pd.DataFrame, is_missing: bool = False) -> bool:
        """
        Insert DataFrame with proper timezone handling and is_missing flag

        Args:
            df: DataFrame to insert
            is_missing: Flag indicating if this is missing data (default: False for real data)

        Returns:
            bool: True if successful, False otherwise
        """
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

            # Add is_missing flag
            df_copy['is_missing'] = is_missing

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
                                (ticker, date, open, high, low, close, volume, is_missing)
                                VALUES (:ticker, :date, :open, :high, :low, :close, :volume, :is_missing)
                            """)

                            conn.execute(insert_query, {
                                'ticker': str(row['ticker']),
                                'date': str(row['date']),
                                'open': float(row['open']) if pd.notna(row['open']) else None,
                                'high': float(row['high']) if pd.notna(row['high']) else None,
                                'low': float(row['low']) if pd.notna(row['low']) else None,
                                'close': float(row['close']) if pd.notna(row['close']) else None,
                                'volume': int(row['volume']) if pd.notna(row['volume']) else None,
                                'is_missing': bool(row['is_missing'])
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

    def get_latest_dates(self, tickers: Optional[List[str]] = None) -> Dict[str, Optional[str]]:
        """Get the latest date for each ticker in the database"""
        if not self.is_initialized:
            self.initialize()

        try:
            with self.engine.connect() as conn:
                if tickers:
                    # Create proper parameter binding for SQLAlchemy
                    placeholders = ','.join([f':ticker{i}' for i in range(len(tickers))])
                    query = text(f"""
                        SELECT ticker, MAX(date) as latest_date
                        FROM stock_data
                        WHERE ticker IN ({placeholders})
                        GROUP BY ticker
                    """)

                    params = {f'ticker{i}': ticker for i, ticker in enumerate(tickers)}
                    result = conn.execute(query, params).fetchall()

                    # Initialize with all requested tickers
                    latest_dates = {ticker: None for ticker in tickers}
                else:
                    # Get all tickers
                    query = text("""
                        SELECT ticker, MAX(date) as latest_date
                        FROM stock_data
                        GROUP BY ticker
                    """)
                    result = conn.execute(query).fetchall()
                    latest_dates = {}

                # Populate results
                for ticker, latest_date in result:
                    latest_dates[ticker] = latest_date

                return latest_dates

        except Exception as e:
            logger.error(f"Failed to get latest dates: {e}")
            return {ticker: None for ticker in (tickers or [])}
    def get_stock_data_stats(self, ticker: Optional[str] = None) -> pd.DataFrame:
        """
        Get data completeness statistics per stock

        Args:
            ticker: Optional ticker symbol to get stats for specific stock
                    If None, returns stats for all stocks

        Returns:
            DataFrame with columns:
            - ticker: Stock symbol
            - first_date: Earliest date in data
            - last_date: Latest date in data
            - total_records: Total number of records
            - real_records: Number of real data records (is_missing=FALSE)
            - missing_records: Number of missing data records (is_missing=TRUE)
        """
        if not self.is_initialized:
            self.initialize()

        try:
            query = """
                SELECT
                    ticker,
                    MIN(date) as first_date,
                    MAX(date) as last_date,
                    COUNT(*) as total_records,
                    SUM(CASE WHEN is_missing = FALSE THEN 1 ELSE 0 END) as real_records,
                    SUM(CASE WHEN is_missing = TRUE THEN 1 ELSE 0 END) as missing_records
                FROM stock_data
            """

            params = {}
            if ticker:
                query += " WHERE ticker = :ticker"
                params["ticker"] = ticker

            query += " GROUP BY ticker ORDER BY ticker"

            with self.engine.connect() as conn:
                df = pd.read_sql(text(query), conn, params=params)

            if not df.empty:
                # Convert date strings to datetime
                df['first_date'] = pd.to_datetime(df['first_date'])
                df['last_date'] = pd.to_datetime(df['last_date'])

                # Calculate completeness percentage (approximate)
                # Assumes ~252 trading days per year
                def calculate_completeness(row):
                    years = (row['last_date'] - row['first_date']).days / 365.25
                    expected = years * 252  # Approximate trading days
                    if expected > 0:
                        completeness = (row['real_records'] / expected) * 100
                        return min(completeness, 100.0)  # Cap at 100%
                    return 100.0

                df['completeness_pct'] = df.apply(calculate_completeness, axis=1)

            return df

        except Exception as e:
            logger.error(f"Failed to get stock data stats: {e}")
            return pd.DataFrame()

    def get_data_completeness_summary(self) -> Dict[str, Any]:
        """
        Get overall data completeness summary across all stocks

        Returns:
            Dictionary with:
            - total_stocks: Total number of unique tickers
            - stocks_with_data: Number of stocks with any data
            - total_records: Total number of all records
            - real_records: Total number of real data records
            - missing_records: Total number of missing data records
            - date_range: Tuple of (earliest_date, latest_date) across all stocks
            - avg_completeness: Average completeness percentage
        """
        if not self.is_initialized:
            self.initialize()

        try:
            with self.engine.connect() as conn:
                # Get overall stats
                stats_query = text("""
                    SELECT
                        COUNT(DISTINCT ticker) as total_stocks,
                        COUNT(*) as total_records,
                        SUM(CASE WHEN is_missing = FALSE THEN 1 ELSE 0 END) as real_records,
                        SUM(CASE WHEN is_missing = TRUE THEN 1 ELSE 0 END) as missing_records,
                        MIN(date) as earliest_date,
                        MAX(date) as latest_date
                    FROM stock_data
                """)

                result = conn.execute(stats_query).fetchone()

                if result:
                    # Get per-stock stats to calculate average completeness
                    stock_stats = self.get_stock_data_stats()
                    avg_completeness = stock_stats['completeness_pct'].mean() if not stock_stats.empty else 0.0

                    return {
                        'total_stocks': result[0] or 0,
                        'stocks_with_data': result[0] or 0,
                        'total_records': result[1] or 0,
                        'real_records': result[2] or 0,
                        'missing_records': result[3] or 0,
                        'date_range': (result[4], result[5]) if result[4] and result[5] else (None, None),
                        'avg_completeness': round(avg_completeness, 2)
                    }

                return {
                    'total_stocks': 0,
                    'stocks_with_data': 0,
                    'total_records': 0,
                    'real_records': 0,
                    'missing_records': 0,
                    'date_range': (None, None),
                    'avg_completeness': 0.0
                }

        except Exception as e:
            logger.error(f"Failed to get completeness summary: {e}")
            return {
                'total_stocks': 0,
                'stocks_with_data': 0,
                'total_records': 0,
                'real_records': 0,
                'missing_records': 0,
                'date_range': (None, None),
                'avg_completeness': 0.0
            }

    def get_stocks_with_incomplete_data(self, threshold_pct: float = 95.0) -> pd.DataFrame:
        """
        Get stocks with data completeness below threshold

        Args:
            threshold_pct: Minimum completeness percentage (default: 95.0)

        Returns:
            DataFrame with stocks below threshold, sorted by completeness
        """
        if not self.is_initialized:
            self.initialize()

        try:
            all_stats = self.get_stock_data_stats()

            if all_stats.empty:
                return pd.DataFrame()

            # Filter by threshold
            incomplete = all_stats[all_stats['completeness_pct'] < threshold_pct]

            # Sort by completeness (worst first)
            incomplete = incomplete.sort_values('completeness_pct')

            return incomplete

        except Exception as e:
            logger.error(f"Failed to get incomplete stocks: {e}")
            return pd.DataFrame()

    def count_records_by_missing_flag(self, ticker: Optional[str] = None) -> Dict[str, int]:
        """
        Count records by is_missing flag

        Args:
            ticker: Optional ticker to count for specific stock

        Returns:
            Dictionary with:
            - total: Total records
            - real: Records with is_missing=FALSE
            - missing: Records with is_missing=TRUE
        """
        if not self.is_initialized:
            self.initialize()

        try:
            query = """
                SELECT
                    COUNT(*) as total,
                    SUM(CASE WHEN is_missing = FALSE THEN 1 ELSE 0 END) as real,
                    SUM(CASE WHEN is_missing = TRUE THEN 1 ELSE 0 END) as missing
                FROM stock_data
            """

            params = {}
            if ticker:
                query += " WHERE ticker = :ticker"
                params["ticker"] = ticker

            with self.engine.connect() as conn:
                result = conn.execute(text(query), params).fetchone()

                return {
                    'total': result[0] or 0,
                    'real': result[1] or 0,
                    'missing': result[2] or 0
                }

        except Exception as e:
            logger.error(f"Failed to count records: {e}")
            return {'total': 0, 'real': 0, 'missing': 0}

# Global instance
db_manager = DatabaseManager()
