"""
Optimized stock data fetching with robust timezone handling
Data Flow:

1.)Load symbols from CSV
2.)Submit parallel tasks to thread pool
3.)Process completed tasks as they finish
4.)Combine all data into single DataFrame
5.)Store in database using chunked insertion
6.)Return comprehensive results
"""

import pandas as pd
import yfinance as yf
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Optional, Tuple
import time
import logging
from datetime import datetime

from ..config.settings import config
from .apple_silicon_optimizer import optimizer
from ..utils.logger import get_logger

logger = get_logger(__name__)

class DataFetcher:
    """Optimized data fetcher for stocks"""
    
    def __init__(self):
        self.companies_file = config.COMPANIES_CSV
        self.start_date = config.START_DATE
        self.end_date = config.END_DATE
        self.max_workers = config.MAX_WORKERS
        
        # Configure environment for optimal performance
        optimizer.configure_environment()
        
    def get_stock_symbols(self) -> List[str]:
        """Load stock symbols from CSV"""
        
        try:
            if not self.companies_file.exists():
                logger.error(f"Companies file not found: {self.companies_file}")
                return []
                
            df = pd.read_csv(self.companies_file)
            
            if 'Symbol' not in df.columns:
                logger.error("CSV must contain 'Symbol' column")
                return []
                
            symbols = [f"{symbol}.NS" for symbol in df['Symbol'].tolist()]
            logger.info(f"Successfully loaded {len(symbols)} symbols from CSV")
            return symbols
            
        except Exception as e:
            logger.error(f"Failed to load symbols from CSV: {e}")
            return []
    
    def fetch_single_stock(self, symbol: str, 
                          start_date: Optional[str] = None,
                          end_date: Optional[str] = None) -> Optional[pd.DataFrame]:
        """Fetch data for a single stock symbol with timezone handling"""
        
        start = start_date or self.start_date
        end = end_date or self.end_date
        
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(start=start, end=end, auto_adjust=True) #auto_adjust=True: Automatically adjust for stock splits/dividends
            
            if data.empty:
                logger.warning(f"No data available for {symbol}")
                return None
                
            # Reset index to make Date a column
            data = data.reset_index() #Default behavior: yfinance returns data with Date as index,After reset_index: Date becomes a normal column named 'Date',Why needed: Easier to work with Date as a column
            
            # TIMEZONE FIX: Handle timezone-aware dates from yfinance
            if 'Date' in data.columns:
                # Convert to pandas datetime and remove timezone
                data['Date'] = pd.to_datetime(data['Date'])
                if hasattr(data['Date'].dtype, 'tz') and data['Date'].dtype.tz is not None:
                    data['Date'] = data['Date'].dt.tz_localize(None) #.dt.tz_localize(None): Pandas method to remove timezone, Result: "Naive" datetime (no timezone info)
                elif data['Date'].dt.tz is not None:
                    data['Date'] = data['Date'].dt.tz_localize(None)
            
            # Add ticker column
            data['ticker'] = symbol.replace('.NS', '')
            
            # Rename columns to match database schema
            data = data.rename(columns={
                'Date': 'date',
                'Open': 'open',
                'High': 'high', 
                'Low': 'low',
                'Close': 'close',
                'Volume': 'volume'
            })
            
            # Select only required columns and ensure proper data types
            required_columns = ['ticker', 'date', 'open', 'high', 'low', 'close', 'volume']
            data = data[required_columns].copy()
            
            # Ensure numeric columns are properly typed
            numeric_cols = ['open', 'high', 'low', 'close', 'volume']
            for col in numeric_cols:
                data[col] = pd.to_numeric(data[col], errors='coerce') #errors='coerce': Convert invalid values to NaN instead of erroring
            
            logger.debug(f"Successfully fetched {len(data)} records for {symbol}")
            return data
            
        except Exception as e:
            logger.error(f"Failed to fetch data for {symbol}: {e}")
            return None
    
    def fetch_all_stocks_concurrent(self, 
                                  symbols: Optional[List[str]] = None,
                                  update_callback: Optional[callable] = None) -> Tuple[bool, Dict]:
        """Fetch all stocks using concurrent processing"""
        
        if symbols is None: #Logic: If no symbols provided, load them from CSV
            symbols = self.get_stock_symbols()
            
        if not symbols: #Check if we have any symbols to process
            logger.error("No symbols available for fetching")
            return False, {"error": "No symbols to fetch"}
            
        logger.info(f"Starting concurrent fetch for {len(symbols)} symbols")
        start_time = time.time()
        
        successful_fetches = 0
        failed_fetches = 0
        all_data = [] #Store DataFrames from each successful fetch
        
        # Use ThreadPoolExecutor with optimal worker count, submit all 500 stocks to the threadpool so they can process in parallel
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_symbol = {
                executor.submit(self.fetch_single_stock, symbol): symbol 
                for symbol in symbols
            }
            
            # Process completed tasks
            for future in as_completed(future_to_symbol): #Iterate through tasks as they complete,  Tasks can complete in any order
                symbol = future_to_symbol[future] # Look up which symbol this completed task represents, Example: If future completed, this might return "RELIANCE.NS"
                
                try:
                    data = future.result()
                    
                    if data is not None and not data.empty:
                        all_data.append(data)
                        successful_fetches += 1
                        logger.info(f"Successfully fetched {symbol}: {len(data)} records")
                    else:
                        failed_fetches += 1
                        logger.warning(f"No data retrieved for {symbol}")
                        
                except Exception as e:
                    failed_fetches += 1
                    logger.error(f"Error processing {symbol}: {e}")
                
                # Call update callback if provided
                if update_callback:
                    progress = (successful_fetches + failed_fetches) / len(symbols)
                    update_callback(progress, symbol, successful_fetches, failed_fetches)
        
        # Combine all data with additional timezone safety
        if all_data: #Check if we have any successful data to process
            try:
                combined_data = pd.concat(all_data, ignore_index=True) #Combine all individual stock DataFrames into one large DataFrame,ignore_index=True: Create new sequential index instead of preserving original indexes
                
                # SAFETY CHECK: Remove timezone if present (pandas concat can sometimes reintroduce timezones)
                # We check this again when we are inserting to dataframe therefore this is redundant
                #if 'date' in combined_data.columns and combined_data['date'].dt.tz is not None:
                #   combined_data['date'] = combined_data['date'].dt.tz_localize(None)
                #    logger.debug("Removed timezone from combined data (safety check)")
                
                # Import database manager here to avoid circular import
                from .database_manager import db_manager
                
                # Store in database
                logger.info(f"Inserting {len(combined_data)} records into database...")
                success = db_manager.insert_dataframe_chunked(combined_data)
                
                end_time = time.time()
                duration = end_time - start_time
                
                result = {
                    "success": success,
                    "total_symbols": len(symbols),
                    "successful_fetches": successful_fetches,
                    "failed_fetches": failed_fetches,
                    "total_records": len(combined_data),
                    "duration_seconds": round(duration, 2),
                    "records_per_second": round(len(combined_data) / duration, 2)
                }
                
                if success:
                    logger.info(f"Fetch operation completed successfully: {successful_fetches}/{len(symbols)} stocks processed")
                    logger.info(f"Performance: {duration:.2f}s duration, {result['records_per_second']:.2f} records/s")
                else:
                    logger.error("Database insertion failed after successful data fetch")
                
                return success, result
                
            except Exception as e:
                logger.error(f"Error combining or inserting data: {e}")
                return False, {"error": f"Data processing failed: {e}"}
        else:
            logger.error(f"No data fetched successfully from {len(symbols)} symbols")
            return False, {
                "error": "No data fetched successfully",
                "failed_fetches": failed_fetches
            }

# Global data fetcher instance
data_fetcher = DataFetcher()
