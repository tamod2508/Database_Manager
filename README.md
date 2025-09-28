# Database Manager

A macOS application for stock data managementmenu bar integration, and Apple Silicon optimization.

## Overview

Database Manager is a comprehensive stock data management application designed specifically for macOS. It provides real-time stock data monitoring through an intuitive GUI interface and a convenient menu bar application and Apple Silicon performance optimizations.

### Key Features

- **Dual Interface**: Full-featured GUI application and lightweight menu bar monitoring
- **Apple Silicon Optimized**: Enhanced performance on M-series chips
- **Visual Feedback**: Animated menu bar icons showing operation status
- **Data Management**: SQLite database with performance optimizations
- **Native Integration**: macOS notifications, auto-startup, and system integration

## System Requirements

- macOS 10.14 or later
- Python 3.9 or higher
- 500MB free disk space (for data storage)
- Internet connection (for data updates)

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

- Data viewer with sortable tables
- Status monitoring panel
- Manual update controls
- Settings management

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

- Quick access to key functions
- Visual status indicators
- One-click data updates
- System integration

Launch manually when needed.

### Manual Data Update

```bash
python3 run_update.py
```

## Module Documentation

### Core Modules

#### `src/core/database_manager.py`

- **Purpose**: SQLite database operations and management
- **Features**:
  - Optimized database connections with WAL mode
  - Chunked data insertion for large datasets
  - Database statistics and health monitoring
  - Apple Silicon performance optimizations

#### `src/core/data_fetcher.py`

- **Purpose**: Stock data acquisition from Yahoo Finance
- **Features**:
  - Concurrent data fetching using ThreadPoolExecutor
  - Rate limiting and error handling
  - Progress tracking for update operations
  - Symbol validation and processing

#### `src/core/apple_silicon_optimizer.py`

- **Purpose**: Hardware-specific optimizations
- **Features**:
  - CPU architecture detection
  - Optimal worker count calculation
  - Memory allocation optimization
  - Performance tuning for M-series chips

### GUI Components

#### `src/gui/main_window.py`

- **Purpose**: Primary application interface
- **Features**:
  - CustomTkinter-based modern UI
  - Tabbed interface with data viewer and settings
  - Progress tracking for operations
  - Status monitoring integration

#### `src/gui/components/`

- **data_viewer.py**: Stock data display with filtering and sorting
- **status_panel.py**: System status monitoring and database health
- **settings_panel.py**: Application configuration interface

### Menu Bar Integration

#### `src/menubar/menu_app.py`

- **Purpose**: macOS menu bar application using rumps
- **Features**:
  - Animated status indicators during operations
  - Quick access menu with all major functions
  - Background operation monitoring
  - Native macOS integration

#### `src/menubar/notifications.py`

- **Purpose**: macOS notification system integration
- **Features**:
  - Update completion notifications
  - Error alerting
  - System-native notification display

### Configuration and Utilities

#### `src/config/settings.py`

- **Purpose**: Application configuration management
- **Features**:
  - Database and file path configuration
  - Performance settings
  - Application metadata

#### `src/utils/logger.py`

- **Purpose**: Comprehensive logging system
- **Features**:
  - Component-specific log files
  - Visual indicators for different log levels
  - Rotating log files with size management
  - Console and file output

## Automated Operations

The application includes manual data management capabilities and convenient launcher scripts for regular use.

## File Structure

```
Database_Manager/
├── src/
│   ├── config/          # Configuration management
│   ├── core/            # Core functionality (database, data fetching)
│   ├── gui/             # GUI components and interface
│   ├── menubar/         # Menu bar application
│   └── utils/           # Utilities and logging
├── data/
│   ├── db/              # SQLite database files (excluded from Git)
│   └── stock_list.csv   # Stock symbols list (excluded from Git)
├── logs/                # Application logs (excluded from Git)
├── data_env/            # Python virtual environment
├── setup/               # Installation and requirements
├── run_gui.py           # GUI application launcher
├── run_menubar.py       # Menu bar application launcher
└── run_update.py        # Manual update script
```

## Configuration Files

### Log Files

- `Database_Manager/logs/database_manager.log` - General application logs
- `Database_Manager/logs/menubar.log` - Menu bar specific logs
- `Database_Manager/logs/GUI.log` - GUI application logs

## Troubleshooting

### Common Issues

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
```

## Performance Optimization

### Apple Silicon Benefits

- 2x faster data processing on M-series chips
- Optimized memory allocation
- Concurrent processing with hardware-appropriate thread counts

### Database Optimizations

- SQLite WAL mode for improved concurrent access
- Memory mapping for faster I/O operations
- Chunked data insertion for large datasets

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly on macOS
5. Submit a pull request

## License

This project is licensed under the MIT License. See LICENSE file for details.

## Version History

- **v1.0.0** - Initial release with core functionality
  - Stock data management
  - Menu bar integration
  - Automated updates
  - Apple Silicon optimization
