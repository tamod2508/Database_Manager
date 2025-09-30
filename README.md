
# Database Manager

A macOS application for stock data management with intelligent incremental updates, menu bar integration, and Apple Silicon optimization.

## Overview

Database Manager is a comprehensive stock data management application designed specifically for macOS. It provides efficient stock data monitoring through an intuitive GUI interface and a convenient menu bar application with Apple Silicon performance optimizations.

### Key Features

* **Intelligent Incremental Updates** : Only fetches missing data, dramatically reducing API calls and update time
* **Dual Interface** : Full-featured GUI application and lightweight menu bar monitoring
* **Apple Silicon Optimized** : Enhanced performance on M-series chips
* **Stock-wise Status Monitoring** : Visual tracking of data availability per symbol
* **Visual Feedback** : Animated menu bar icons showing operation status
* **Data Management** : SQLite database with performance optimizations and bulk operations
* **Native Integration** : macOS notifications and system integration

## System Requirements

* macOS 10.14 or later
* Python 3.9 or higher
* 500MB free disk space (for data storage)
* Internet connection (for data updates)

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/tamod2508/Database_Manager.git
cd Database_Manager
```

### 2. Set Up Python Environment

```bash
# Create virtual environment
python3 -m venv data_env

# Activate environment
source data_env/bin/activate

# Install dependencies
pip install -r setup/requirements.txt
```

### 3. Create Startup Aliases (Optional)

For convenient access, add these aliases to your shell profile:

```bash
# Add to ~/.zshrc or ~/.bash_profile
echo 'alias db_gui="cd ~/Desktop/Database_Manager && source data_env/bin/activate && python3 run_gui.py"' >> ~/.zshrc
echo 'alias db_menu="cd ~/Desktop/Database_Manager && source data_env/bin/activate && python3 run_menubar.py &"' >> ~/.zshrc

# Reload shell configuration
source ~/.zshrc
```

## Usage

### GUI Application

Launch the main graphical interface:

```bash
cd Database_Manager
source data_env/bin/activate
python3 run_gui.py

# Or use the alias (if configured):
db_gui
```

The GUI provides:

#### Main Tabs:

* **Data Viewer** : Browse and filter historical stock data with sortable tables
* **Stock-wise Status** : Monitor data availability for each symbol with visual indicators
* Color-coded status (green for available, red for missing)
* Date range display per stock
* Bulk delete functionality with safety confirmations
* **Settings** : Application configuration and system information

#### Update Options:

* **Check Update Plan** : Preview what data will be fetched before updating
* **Update Data** : Intelligent incremental update (default) - only fetches missing data
* **Full Refresh** : Complete data rebuild from scratch (use sparingly)
* **Refresh View** : Reload data display from database

### Menu Bar Application

Launch the menu bar monitoring component:

```bash
cd Database_Manager
source data_env/bin/activate
python3 run_menubar.py

# Or use the alias (if configured):
db_menu
```

The menu bar app provides:

* **Update Options** :
* Incremental Update (default): Fast, efficient updates
* Check Update Plan: Preview before updating
* Full Refresh: Complete database rebuild
* **Quick Stats** : View database statistics at a glance
* **Visual status indicators** : Animated icons during operations
* **One-click data updates** : Background operation with notifications
* **System integration** : Native macOS notifications and status updates

### Manual Data Update

```bash
python3 run_update.py
```

## Incremental Update System

The application intelligently manages data updates to minimize API calls and update time:

### How It Works:

1. **Analysis Phase** : Checks database for latest date per symbol
2. **Smart Planning** :

* Symbols with no data: Full fetch from START_DATE
* Symbols with old data: Fetch only missing dates
* Symbols up-to-date: Skip entirely

1. **Efficient Fetching** : Only processes symbols that need updates
2. **Weekend Handling** : Automatically skips non-trading days

### Performance Benefits:

* **90%+ reduction** in API calls for daily updates
* **Much faster** update times (seconds vs minutes)
* **Respectful** of Yahoo Finance rate limits
* **Transparent** : Shows exactly what will be updated before fetching

### Example Update Scenarios:

**Daily Update (Monday morning):**

* Checks 500 symbols
* Finds 500 need Friday's data
* Fetches only 1 day per symbol
* Completes in ~30 seconds

**After a week:**

* Checks 500 symbols
* Some up-to-date, some need 5 days
* Fetches only missing days
* Much faster than full refresh

**Database Rebuild:**

* Use "Full Refresh" option
* Fetches complete history for all symbols
* Takes longer but rebuilds from scratch

## Module Documentation

### Core Modules

#### `src/core/database_manager.py`

* **Purpose** : SQLite database operations and management
* **Features** :
* Optimized database connections with WAL mode
* Chunked data insertion for large datasets
* Latest date queries for incremental updates
* Database statistics and health monitoring
* Apple Silicon performance optimizations
* Individual stock data deletion

#### `src/core/data_fetcher.py`

* **Purpose** : Intelligent stock data acquisition from Yahoo Finance
* **Features** :
* Incremental update planning and execution
* Concurrent data fetching using ThreadPoolExecutor
* Custom date range calculation per symbol
* Rate limiting and error handling
* Progress tracking for update operations
* Symbol validation and CSV processing
* Weekend and non-trading day handling

#### `src/core/apple_silicon_optimizer.py`

* **Purpose** : Hardware-specific optimizations
* **Features** :
* CPU architecture detection
* Optimal worker count calculation
* Memory allocation optimization
* Performance tuning for M-series chips

### GUI Components

#### `src/gui/main_window.py`

* **Purpose** : Primary application interface
* **Features** :
* CustomTkinter-based modern UI
* Three-tab interface (Data Viewer, Stock-wise Status, Settings)
* Multiple update options with clear distinctions
* Progress tracking for operations
* Status monitoring integration
* Automatic data refresh after updates

#### `src/gui/components/`

* **data_viewer.py** : Stock data display with filtering and sorting
* **stock_status_viewer.py** : Per-symbol data availability monitoring
* Visual status indicators (✓/✗)
* Date range display
* Filter options (all/available/missing)
* Multi-select bulk deletion
* Color-coded rows for easy scanning
* **status_panel.py** : System status monitoring and database health
* **settings_panel.py** : Application configuration interface

### Menu Bar Integration

#### `src/menubar/menu_app.py`

* **Purpose** : macOS menu bar application using rumps
* **Features** :
* Animated status indicators during operations
* Submenu with update options (Incremental/Full Refresh)
* Update plan preview
* Background operation monitoring
* Native macOS integration
* Persistent update time tracking

#### `src/menubar/notifications.py`

* **Purpose** : macOS notification system integration
* **Features** :
* Update completion notifications
* Error alerting
* Progress updates for long operations
* System-native notification display

### Configuration and Utilities

#### `src/config/settings.py`

* **Purpose** : Application configuration management
* **Features** :
* Database and file path configuration
* Dynamic end date calculation (avoids incomplete data)
* Performance settings
* Application metadata
* Hardware detection

#### `src/utils/logger.py`

* **Purpose** : Comprehensive logging system
* **Features** :
* Component-specific log files
* Visual indicators for different log levels (✓ ✗ ⚠️ ℹ️)
* Rotating log files with size management
* Console and file output
* Debug mode support

## File Structure

```
Database_Manager/
├── src/
│   ├── config/          # Configuration management
│   ├── core/            # Core functionality (database, data fetching)
│   ├── gui/             # GUI components and interface
│   │   └── components/  # Reusable UI components
│   ├── menubar/         # Menu bar application
│   └── utils/           # Utilities and logging
├── data/
│   ├── db/              # SQLite database files (excluded from Git)
│   ├── stock_list.csv   # Stock symbols list (excluded from Git)
│   └── last_update.json # Last update timestamp (excluded from Git)
├── logs/                # Application logs (excluded from Git)
├── data_env/            # Python virtual environment
├── setup/               # Installation and requirements
├── run_gui.py           # GUI application launcher
├── run_menubar.py       # Menu bar application launcher
└── run_update.py        # Manual update script
```

## Configuration Files

### Data Files

* `data/stock_list.csv` - List of stock symbols to track
* `data/db/historical_data.db` - SQLite database with stock data
* `data/last_update.json` - Persistent update time tracking

### Log Files

* `logs/database_manager.log` - General application logs
* `logs/menubar.log` - Menu bar specific logs
* `logs/GUI.log` - GUI application logs

## Best Practices

### Daily Usage

1. Use** ****Update Data** (incremental) for daily updates
2. Run updates in the evening after market close (after 8 PM IST)
3. Check** ****Stock-wise Status** tab to verify data coverage
4. Use** ****Check Update Plan** if unsure what will be updated

### When to Use Full Refresh

Only use** ****Full Refresh** when:

* Rebuilding the entire database from scratch
* Suspecting data corruption
* Changing date range settings
* Adding many new symbols

### Data Management

* Use** ****Stock-wise Status** tab to identify missing data
* Delete individual stocks before re-fetching if data seems corrupted
* Multi-select for bulk operations
* Regular backups recommended for production use

## Troubleshooting

### Common Issues

**"No data available" errors for all stocks**

This usually means you're trying to fetch today's data before it's published:

```bash
# Wait until evening (after 8 PM IST) or check your END_DATE in settings.py
# Should be set to yesterday: (datetime.now() - timedelta(days=1))
```

**Menu bar app not starting**

```bash
cd ~/Desktop/Database_Manager
source data_env/bin/activate
python3 run_menubar.py
```

**Import errors**

```bash
source data_env/bin/activate
pip install -r setup/requirements.txt
```

**Database connection issues**

```bash
# Check database integrity
ls -la data/db/
# Restart application
```

**Incremental update not working**

1. Fully restart the application (quit and relaunch)
2. Check logs for error messages
3. Try "Full Refresh" to rebuild database
4. Verify CSV file has no blank rows

### Quick Start Commands

```bash
# Start GUI application
cd ~/Desktop/Database_Manager && source data_env/bin/activate && python3 run_gui.py

# Start menu bar application
cd ~/Desktop/Database_Manager && source data_env/bin/activate && python3 run_menubar.py

# Manual data update
cd ~/Desktop/Database_Manager && source data_env/bin/activate && python3 run_update.py
```

### Log Analysis

Check application logs for detailed error information:

```bash
tail -f ~/Desktop/Database_Manager/logs/database_manager.log
tail -f ~/Desktop/Database_Manager/logs/menubar.log
tail -f ~/Desktop/Database_Manager/logs/GUI.log
```

## Performance Optimization

### Apple Silicon Benefits

* 2x faster data processing on M-series chips
* Optimized memory allocation
* Concurrent processing with hardware-appropriate thread counts
* Larger cache sizes for database operations

### Database Optimizations

* SQLite WAL mode for improved concurrent access
* Memory mapping for faster I/O operations
* Chunked data insertion for large datasets
* Optimized indexes for quick queries

### Incremental Update Efficiency

* Smart date range calculation per symbol
* Skips symbols already up-to-date
* Parallel fetching with optimal thread counts
* Weekend and holiday handling

## Technical Details

### Date Handling

* All dates stored without timezone (naive datetime)
* Automatic conversion from yfinance's timezone-aware data
* Dynamic END_DATE to avoid incomplete daily data
* Weekend-aware update planning

### Database Schema

```sql
CREATE TABLE stock_data (
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
```

### Update Algorithm

1. Load all symbols from CSV
2. Query database for latest date per symbol
3. Calculate date ranges:
   * No data: fetch from START_DATE
   * Has data: fetch from (latest_date + 1 day)
   * Within 3 days of END_DATE: mark as current
4. Submit parallel fetch tasks with custom ranges
5. Combine results and insert to database
6. Update status and notify user

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly on macOS
5. Submit a pull request

## License

This project is licensed under the MIT License. See LICENSE file for details.

## Version History

* **v1.1** - Intelligent Incremental Updates
  * Incremental update system (90%+ efficiency improvement)
  * Stock-wise status monitoring tab
  * Bulk delete functionality
  * Update plan preview
  * Weekend and non-trading day handling
  * Enhanced menu bar with update options
  * Improved error handling and logging
* **v1.0.0** - Initial release
  * Stock data management
  * Menu bar integration
  * Automated updates
  * Apple Silicon optimization

## Roadmap

### Future Enhancements

* Quarterly financial statement integration
* Advanced charting and technical indicators
* Custom stock screeners
* Export functionality
* Email/notification alerts for specific conditions

## Support

For issues, questions, or contributions, please visit the GitHub repository or check the application logs for detailed error information.
