"""
Professional settings page with system information and configuration
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QGroupBox, QScrollArea, QGridLayout, QLineEdit,
    QSpinBox, QMessageBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
import os
from pathlib import Path

from ...config.settings import config
from ...core.apple_silicon_optimizer import optimizer
from ...utils.logger import get_logger

logger = get_logger(__name__)

class SettingsPage(QWidget):
    """Settings and system information page"""
    
    # Signals
    settings_changed = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the settings page UI"""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(12)
        
        # Create scroll area for settings
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
        """)
        
        # Container widget for scroll area
        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(4, 4, 4, 4)
        container_layout.setSpacing(16)
        
        # System Information Section
        self.create_system_info_section(container_layout)
        
        # Database Settings Section
        self.create_database_section(container_layout)
        
        # Performance Settings Section
        self.create_performance_section(container_layout)
        
        # Data Settings Section
        self.create_data_settings_section(container_layout)
        
        # Path Information Section
        self.create_paths_section(container_layout)
        
        # Action Buttons
        self.create_action_buttons(container_layout)
        
        container_layout.addStretch()
        
        # Set container to scroll area
        scroll.setWidget(container)
        main_layout.addWidget(scroll)
        
    def create_system_info_section(self, layout):
        """Create system information section"""
        group = QGroupBox("💻 System Information")
        group.setStyleSheet(self.get_groupbox_style())
        
        group_layout = QGridLayout(group)
        group_layout.setSpacing(12)
        group_layout.setContentsMargins(20, 24, 20, 20)
        
        # Get system info
        try:
            sys_info = optimizer.get_system_info()
            
            # Architecture
            self.add_info_row(group_layout, 0, "Architecture:", 
                            sys_info.get('architecture', 'Unknown'))
            
            # CPU Cores
            self.add_info_row(group_layout, 1, "CPU Cores:", 
                            str(sys_info.get('cpu_count', 'Unknown')))
            
            # Memory
            self.add_info_row(group_layout, 2, "Memory:", 
                            f"{sys_info.get('memory_gb', 0):.1f} GB")
            
            # macOS Version
            self.add_info_row(group_layout, 3, "macOS Version:", 
                            sys_info.get('macos_version', 'Unknown'))
            
            # Optimal Workers
            self.add_info_row(group_layout, 4, "Optimal Workers:", 
                            str(sys_info.get('optimal_workers', 'Unknown')))
            
            # Performance Cores
            perf_cores = "Yes" if sys_info.get('performance_cores') else "No"
            self.add_info_row(group_layout, 5, "High Performance Mode:", perf_cores)
            
        except Exception as e:
            logger.error(f"Failed to get system info: {e}")
            error_label = QLabel(f"Error loading system info: {e}")
            error_label.setStyleSheet("color: #dc3545;")
            group_layout.addWidget(error_label, 0, 0, 1, 2)
        
        layout.addWidget(group)
        
    def create_database_section(self, layout):
        """Create database information section"""
        group = QGroupBox("🗄️ Database Information")
        group.setStyleSheet(self.get_groupbox_style())
        
        group_layout = QGridLayout(group)
        group_layout.setSpacing(12)
        group_layout.setContentsMargins(20, 24, 20, 20)
        
        # Database Name
        self.add_info_row(group_layout, 0, "Database Name:", config.DB_NAME)
        
        # Database Path
        db_path_short = str(config.DB_PATH).replace(str(config.BASE_DIR), "~")
        self.add_info_row(group_layout, 1, "Database Path:", db_path_short)
        
        # Database Size
        try:
            if config.DB_PATH.exists():
                size_mb = config.DB_PATH.stat().st_size / (1024 * 1024)
                self.add_info_row(group_layout, 2, "Database Size:", f"{size_mb:.2f} MB")
            else:
                self.add_info_row(group_layout, 3, "Database Size:", "Not created yet")
        except Exception as e:
            self.add_info_row(group_layout, 2, "Database Size:", f"Error: {e}")
        
        # Open database location button
        open_db_btn = QPushButton("📂 Open Database Location")
        open_db_btn.setProperty("class", "info")
        open_db_btn.setFixedHeight(36)
        open_db_btn.clicked.connect(self.open_database_location)
        group_layout.addWidget(open_db_btn, 3, 0, 1, 2)
        
        layout.addWidget(group)
        
    def create_performance_section(self, layout):
        """Create performance settings section"""
        group = QGroupBox("⚡ Performance Settings")
        group.setStyleSheet(self.get_groupbox_style())
        
        group_layout = QGridLayout(group)
        group_layout.setSpacing(12)
        group_layout.setContentsMargins(20, 24, 20, 20)
        
        # Max Workers (read-only display)
        self.add_info_row(group_layout, 0, "Max Workers:", str(config.MAX_WORKERS))
        
        # Chunk Size
        self.add_info_row(group_layout, 1, "Chunk Size:", str(config.CHUNK_SIZE))
        
        # Cache Size
        optimal_settings = optimizer.get_optimal_settings()
        cache_mb = optimal_settings.get('cache_size', 0) * 4 / 1024  # Convert pages to MB
        self.add_info_row(group_layout, 2, "Cache Size:", f"~{cache_mb:.0f} MB")
        
        # Memory Mapping
        mmap_mb = optimal_settings.get('memory_mapping_size', 0) / (1024 * 1024)
        self.add_info_row(group_layout, 3, "Memory Mapping:", f"{mmap_mb:.0f} MB")
        
        # Temp Storage
        temp_store = optimal_settings.get('temp_store', 'DEFAULT')
        self.add_info_row(group_layout, 4, "Temp Storage:", temp_store)
        
        layout.addWidget(group)
        
    def create_data_settings_section(self, layout):
        """Create data settings section"""
        group = QGroupBox("📊 Data Settings")
        group.setStyleSheet(self.get_groupbox_style())
        
        group_layout = QGridLayout(group)
        group_layout.setSpacing(12)
        group_layout.setContentsMargins(20, 24, 20, 20)
        
        # Companies CSV
        csv_path_short = str(config.COMPANIES_CSV).replace(str(config.BASE_DIR), "~")
        self.add_info_row(group_layout, 0, "Stock List CSV:", csv_path_short)
        
        # Start Date
        self.add_info_row(group_layout, 1, "Data Start Date:", config.START_DATE)
        
        # End Date (dynamic)
        self.add_info_row(group_layout, 2, "Data End Date:", config.END_DATE)
        
        # Stock count
        try:
            import pandas as pd
            if config.COMPANIES_CSV.exists():
                df = pd.read_csv(config.COMPANIES_CSV)
                stock_count = len(df)
                self.add_info_row(group_layout, 3, "Total Stocks:", str(stock_count))
            else:
                self.add_info_row(group_layout, 3, "Total Stocks:", "CSV not found")
        except Exception as e:
            self.add_info_row(group_layout, 3, "Total Stocks:", f"Error: {e}")
        
        layout.addWidget(group)
        
    def create_paths_section(self, layout):
        """Create paths information section"""
        group = QGroupBox("📁 Application Paths")
        group.setStyleSheet(self.get_groupbox_style())
        
        group_layout = QGridLayout(group)
        group_layout.setSpacing(12)
        group_layout.setContentsMargins(20, 24, 20, 20)
        
        # Base Directory
        base_short = str(config.BASE_DIR).replace(str(Path.home()), "~")
        self.add_info_row(group_layout, 0, "Base Directory:", base_short)
        
        # Data Directory
        data_short = str(config.DATA_DIR).replace(str(config.BASE_DIR), "~")
        self.add_info_row(group_layout, 1, "Data Directory:", data_short)
        
        # Logs Directory
        logs_short = str(config.LOGS_DIR).replace(str(config.BASE_DIR), "~")
        self.add_info_row(group_layout, 2, "Logs Directory:", logs_short)
        
        # Buttons row
        button_layout = QHBoxLayout()
        button_layout.setSpacing(8)
        
        # Open data directory
        open_data_btn = QPushButton("📂 Open Data")
        open_data_btn.setProperty("class", "info")
        open_data_btn.setFixedHeight(36)
        open_data_btn.clicked.connect(lambda: self.open_directory(config.DATA_DIR))
        button_layout.addWidget(open_data_btn)
        
        # Open logs directory
        open_logs_btn = QPushButton("📋 Open Logs")
        open_logs_btn.setProperty("class", "info")
        open_logs_btn.setFixedHeight(36)
        open_logs_btn.clicked.connect(lambda: self.open_directory(config.LOGS_DIR))
        button_layout.addWidget(open_logs_btn)
        
        group_layout.addLayout(button_layout, 3, 0, 1, 2)
        
        layout.addWidget(group)
        
    def create_action_buttons(self, layout):
        """Create action buttons section"""
        action_frame = QFrame()
        action_frame.setFixedHeight(56)
        action_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                           stop:0 #2d3441, stop:1 #252832);
                border: 2px solid #4a5468;
                border-radius: 10px;
            }
        """)
        
        action_layout = QHBoxLayout(action_frame)
        action_layout.setContentsMargins(16, 10, 16, 10)
        action_layout.setSpacing(12)
        
        # Info label
        info_label = QLabel("System and application configuration")
        info_label.setStyleSheet("""
            QLabel {
                color: #979dac;
                font-size: 11px;
                font-weight: 500;
            }
        """)
        action_layout.addWidget(info_label)
        
        action_layout.addStretch()
        
        # Refresh button
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.setProperty("class", "info")
        refresh_btn.setFixedHeight(40)
        refresh_btn.setFixedWidth(100)
        refresh_btn.clicked.connect(self.refresh_settings)
        action_layout.addWidget(refresh_btn)
        
        # Export settings button
        export_btn = QPushButton("📤 Export")
        export_btn.setProperty("class", "neutral")
        export_btn.setFixedHeight(40)
        export_btn.setFixedWidth(100)
        export_btn.clicked.connect(self.export_settings)
        action_layout.addWidget(export_btn)
        
        layout.addWidget(action_frame)
        
    def add_info_row(self, layout, row, label_text, value_text):
        """Add an information row to the grid layout"""
        # Label
        label = QLabel(label_text)
        label.setStyleSheet("""
            QLabel {
                color: #979dac;
                font-size: 12px;
                font-weight: 600;
            }
        """)
        layout.addWidget(label, row, 0, Qt.AlignLeft | Qt.AlignVCenter)
        
        # Value
        value = QLabel(str(value_text))
        value.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 12px;
                font-weight: 500;
                font-family: 'Monaco', 'Courier New', monospace;
            }
        """)
        value.setTextInteractionFlags(Qt.TextSelectableByMouse)
        layout.addWidget(value, row, 1, Qt.AlignLeft | Qt.AlignVCenter)
        
    def get_groupbox_style(self):
        """Get the standard group box style"""
        return """
            QGroupBox {
                font-weight: 700;
                font-size: 14px;
                border: 2px solid #4a5468;
                border-radius: 12px;
                margin-top: 16px;
                padding-top: 8px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                           stop:0 #2d3441, stop:1 #252832);
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 16px;
                padding: 8px 16px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                           stop:0 #0570d8, stop:1 #0466c8);
                border-radius: 8px;
                color: #ffffff;
                font-weight: 700;
                font-size: 13px;
            }
        """
        
    def open_database_location(self):
        """Open database directory in Finder"""
        self.open_directory(config.DB_DIR)
        
    def open_directory(self, path):
        """Open a directory in Finder"""
        try:
            import subprocess
            subprocess.Popen(['open', str(path)])
            logger.info(f"Opened directory: {path}")
        except Exception as e:
            logger.error(f"Failed to open directory: {e}")
            QMessageBox.warning(
                self,
                "Open Failed",
                f"Could not open directory:\n{path}\n\nError: {e}"
            )
            
    def refresh_settings(self):
        """Refresh all settings information"""
        try:
            # Close and recreate the page
            parent = self.parent()
            if parent:
                # Store current page
                self.__init__(parent)
                logger.info("Settings page refreshed")
                
                QMessageBox.information(
                    self,
                    "Refreshed",
                    "Settings information has been refreshed"
                )
        except Exception as e:
            logger.error(f"Failed to refresh settings: {e}")
            QMessageBox.warning(
                self,
                "Refresh Failed",
                f"Could not refresh settings:\n\n{e}"
            )
            
    def export_settings(self):
        """Export settings to a text file"""
        try:
            import json
            from datetime import datetime
            
            # Gather all settings
            settings_dict = {
                'export_time': datetime.now().isoformat(),
                'system': {
                    'architecture': optimizer.get_system_info().get('architecture'),
                    'cpu_cores': optimizer.get_system_info().get('cpu_count'),
                    'memory_gb': optimizer.get_system_info().get('memory_gb'),
                    'macos_version': optimizer.get_system_info().get('macos_version'),
                },
                'database': {
                    'name': config.DB_NAME,
                    'path': str(config.DB_PATH),
                },
                'performance': {
                    'max_workers': config.MAX_WORKERS,
                    'chunk_size': config.CHUNK_SIZE,
                },
                'data': {
                    'start_date': config.START_DATE,
                    'end_date': config.END_DATE,
                    'companies_csv': str(config.COMPANIES_CSV),
                },
                'paths': {
                    'base_dir': str(config.BASE_DIR),
                    'data_dir': str(config.DATA_DIR),
                    'logs_dir': str(config.LOGS_DIR),
                }
            }
            
            # Export to file
            export_path = config.DATA_DIR / f"settings_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(export_path, 'w') as f:
                json.dump(settings_dict, f, indent=2)
            
            logger.info(f"Settings exported to: {export_path}")
            
            QMessageBox.information(
                self,
                "Export Complete",
                f"Settings exported successfully to:\n\n{export_path}"
            )
            
        except Exception as e:
            logger.error(f"Failed to export settings: {e}")
            QMessageBox.warning(
                self,
                "Export Failed",
                f"Could not export settings:\n\n{e}"
            )
