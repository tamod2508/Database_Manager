"""
Professional stock status page with optimized layout - FIXED
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTreeWidget, QTreeWidgetItem, QFrame, QRadioButton,
    QButtonGroup, QMessageBox, QProgressDialog
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QBrush, QColor
import pandas as pd
from datetime import datetime

from ...core.database_manager import db_manager
from ...config.settings import config
from ...utils.logger import get_logger

logger = get_logger(__name__)

class StockStatusPage(QWidget):
    """Stock-wise data availability status page with optimized layout"""

    # Signal for status updates
    status_updated = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.status_data = pd.DataFrame()
        self.current_filter = "all"
        self.tree = None  # Initialize tree first to prevent AttributeError
        self.is_loading = False  # Prevent double loading
        self.has_loaded = False  # Track if already loaded
        self.setup_ui()

    def setup_ui(self):
        """Setup the optimized status page UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        # Compact summary section
        self.create_ultra_compact_summary(layout)

        # Filter section
        self.create_filters(layout)

        # Status table (takes most space)
        self.create_status_table(layout)

        # Bottom action bar
        self.create_bottom_actions(layout)

    def create_ultra_compact_summary(self, layout):
        """Create ultra compact summary statistics section"""
        summary_frame = QFrame()
        summary_frame.setFixedHeight(60)
        summary_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                           stop:0 #2d3441, stop:1 #252832);
                border: 2px solid #4a5468;
                border-radius: 10px;
            }
        """)

        summary_layout = QHBoxLayout(summary_frame)
        summary_layout.setContentsMargins(16, 8, 16, 8)
        summary_layout.setSpacing(20)

        # Total symbols - single compact box
        total_container = self.create_single_stat_box("Total", "0", "#0466c8")
        summary_layout.addWidget(total_container)

        # Separator
        sep1 = QFrame()
        sep1.setFrameShape(QFrame.VLine)
        sep1.setStyleSheet("QFrame { background-color: #4a5468; max-width: 1px; }")
        summary_layout.addWidget(sep1)

        # Available - single compact box
        available_container = self.create_single_stat_box("Available", "0", "#28a745")
        summary_layout.addWidget(available_container)

        # Separator
        sep2 = QFrame()
        sep2.setFrameShape(QFrame.VLine)
        sep2.setStyleSheet("QFrame { background-color: #4a5468; max-width: 1px; }")
        summary_layout.addWidget(sep2)

        # Missing - single compact box
        missing_container = self.create_single_stat_box("Missing", "0", "#dc3545")
        summary_layout.addWidget(missing_container)

        summary_layout.addStretch()

        layout.addWidget(summary_frame)

    def create_single_stat_box(self, title, value, color):
        """Create a single compact stat box (title: value in one box)"""
        # Outer container with border
        outer = QFrame()
        outer.setFixedWidth(130)
        outer.setStyleSheet("""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                           stop:0 #3a4558, stop:1 #2d3441);
                border: 1px solid #4a5468;
                border-radius: 6px;
                padding: 2px;
            }}
        """)

        # Inner layout
        inner_layout = QVBoxLayout(outer)
        inner_layout.setContentsMargins(10, 6, 10, 6)
        inner_layout.setSpacing(2)

        # Title label (small, gray)
        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                color: #979dac;
                font-size: 10px;
                font-weight: 500;
                text-transform: uppercase;
                background: transparent;
                border: none;
            }
        """)

        # Value label (medium sized, colored)
        value_label = QLabel(value)
        value_label.setObjectName(f"{title}_value")
        value_label.setAlignment(Qt.AlignCenter)
        value_label.setStyleSheet(f"""
            QLabel {{
                color: {color};
                font-size: 12px;
                font-weight: 500;
                background: transparent;
                border: none;
            }}
        """)

        inner_layout.addWidget(title_label)
        inner_layout.addWidget(value_label)

        return outer

    def create_filters(self, layout):
        """Create compact filter radio buttons"""
        filter_frame = QFrame()
        filter_frame.setStyleSheet("""
            QFrame {
                background: transparent;
                border: none;
                padding: 4px 0;
            }
        """)

        filter_layout = QHBoxLayout(filter_frame)
        filter_layout.setContentsMargins(4, 0, 4, 0)
        filter_layout.setSpacing(16)

        filter_label = QLabel("Filter:")
        filter_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-weight: 600;
                font-size: 13px;
            }
        """)
        filter_layout.addWidget(filter_label)

        # Radio button group
        self.filter_group = QButtonGroup()

        # All stocks
        self.all_radio = self.create_filter_radio("All", "all")
        self.all_radio.setChecked(True)
        filter_layout.addWidget(self.all_radio)

        # Data available
        self.available_radio = self.create_filter_radio("Available ✓", "available")
        filter_layout.addWidget(self.available_radio)

        # Missing data
        self.missing_radio = self.create_filter_radio("Missing ✗", "missing")
        filter_layout.addWidget(self.missing_radio)

        filter_layout.addStretch()

        layout.addWidget(filter_frame)

    def create_filter_radio(self, text, value):
        """Create a styled radio button for filtering"""
        radio = QRadioButton(text)
        radio.setProperty("filter_value", value)
        radio.setStyleSheet("""
            QRadioButton {
                color: #ffffff;
                font-size: 13px;
                font-weight: 500;
                spacing: 8px;
            }
            QRadioButton::indicator {
                width: 16px;
                height: 16px;
                border-radius: 8px;
                border: 2px solid #4a5468;
                background-color: #2d3441;
            }
            QRadioButton::indicator:hover {
                border-color: #0466c8;
                background-color: #3a4558;
            }
            QRadioButton::indicator:checked {
                background-color: #0466c8;
                border-color: #0466c8;
            }
            QRadioButton::indicator:checked:after {
                width: 6px;
                height: 6px;
                border-radius: 3px;
                background-color: #ffffff;
            }
        """)
        radio.toggled.connect(lambda checked, v=value: self.on_filter_changed(v) if checked else None)
        self.filter_group.addButton(radio)
        return radio

    def create_status_table(self, layout):
        """Create the status table widget (maximized space)"""
        # Table widget
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels([
            'Symbol', 'Status', 'Records', 'Earliest Date',
            'Latest Date', 'Date Range'
        ])
        self.tree.setRootIsDecorated(False)
        self.tree.setAlternatingRowColors(True)
        self.tree.setSortingEnabled(True)
        self.tree.setSelectionMode(QTreeWidget.ExtendedSelection)

        # Style the table
        self.tree.setStyleSheet("""
            QTreeWidget {
                background-color: #141720;
                alternate-background-color: #1a1d22;
                color: #ffffff;
                border: 2px solid #4a5468;
                border-radius: 12px;
                font-size: 12px;
                gridline-color: #3a4558;
            }
            QTreeWidget::item {
                padding: 10px 6px;
                border-bottom: 1px solid #2d3441;
                height: 28px;
            }
            QTreeWidget::item:selected {
                background-color: #0466c8;
                color: #ffffff;
            }
            QTreeWidget::item:hover {
                background-color: #3a4558;
            }
            QHeaderView::section {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                           stop:0 #3a4558, stop:1 #2d3441);
                border: 1px solid #4a5468;
                padding: 12px 8px;
                font-weight: 700;
                color: #ffffff;
                font-size: 13px;
            }
            QHeaderView::section:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                           stop:0 #4a5468, stop:1 #3a4558);
            }
        """)

        # Set column widths
        self.tree.setColumnWidth(0, 120)  # Symbol
        self.tree.setColumnWidth(1, 80)   # Status
        self.tree.setColumnWidth(2, 100)  # Records
        self.tree.setColumnWidth(3, 120)  # Earliest
        self.tree.setColumnWidth(4, 120)  # Latest
        self.tree.setColumnWidth(5, 100)  # Range

        layout.addWidget(self.tree)

    def create_bottom_actions(self, layout):
        """Create bottom action bar with buttons - FIXED TEXT CUTOFF"""
        action_frame = QFrame()
        action_frame.setFixedHeight(70)  # Increased height for buttons
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

        # Status label
        self.status_label = QLabel("Select stocks from the table above")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #979dac;
                font-size: 11px;
                font-weight: 500;
            }
        """)
        action_layout.addWidget(self.status_label)

        action_layout.addStretch()

        # Refresh button - FIXED SIZE
        self.refresh_btn = QPushButton("🔄 Refresh")
        self.refresh_btn.setProperty("class", "info")
        self.refresh_btn.setFixedHeight(120)
        self.refresh_btn.setFixedWidth(120)
        self.refresh_btn.clicked.connect(self.refresh_status)
        action_layout.addWidget(self.refresh_btn)

        # Delete selected button - FIXED SIZE
        self.delete_btn = QPushButton("🗑️ Delete")
        self.delete_btn.setProperty("class", "secondary")
        self.delete_btn.setFixedHeight(120)
        self.delete_btn.setFixedWidth(120)
        self.delete_btn.clicked.connect(self.delete_selected_stocks)
        action_layout.addWidget(self.delete_btn)

        layout.addWidget(action_frame)

    def refresh_status(self):
        """Refresh status data from database - PREVENTS DOUBLE LOADING"""
        # Prevent double loading
        if self.is_loading:
            logger.info("Status refresh already in progress, skipping...")
            return

        try:
            self.is_loading = True
            self.has_loaded = True
            self.status_label.setText("🔄 Refreshing status data...")
            self.refresh_btn.setEnabled(False)

            logger.info("Refreshing stock status data...")

            # Get list of all symbols from CSV
            symbols_df = pd.read_csv(config.COMPANIES_CSV)
            all_symbols = symbols_df['Symbol'].tolist()

            # Get database stats per symbol
            status_list = []

            # Create progress dialog for large datasets
            if len(all_symbols) > 100:
                progress = QProgressDialog(
                    "Analyzing stock data availability...",
                    "Cancel",
                    0,
                    len(all_symbols),
                    self
                )
                progress.setWindowModality(Qt.WindowModal)
                progress.setWindowTitle("Loading Status")
                progress.setStyleSheet("""
                    QProgressDialog {
                        background-color: #1a1d22;
                        border: 2px solid #4a5468;
                        border-radius: 8px;
                    }
                    QProgressBar {
                        border: 2px solid #4a5468;
                        border-radius: 5px;
                        text-align: center;
                        background-color: #2d3441;
                        color: #ffffff;
                    }
                    QProgressBar::chunk {
                        background-color: #0466c8;
                        border-radius: 3px;
                    }
                """)
                progress.show()
            else:
                progress = None

            for idx, symbol in enumerate(all_symbols):
                if progress:
                    progress.setValue(idx)
                    if progress.wasCanceled():
                        break

                stock_data = db_manager.get_stock_data(ticker=symbol)

                if not stock_data.empty:
                    earliest = stock_data['date'].min()
                    latest = stock_data['date'].max()
                    record_count = len(stock_data)
                    days_range = (latest - earliest).days

                    status_list.append({
                        'symbol': symbol,
                        'has_data': True,
                        'record_count': record_count,
                        'earliest_date': earliest.strftime('%Y-%m-%d'),
                        'latest_date': latest.strftime('%Y-%m-%d'),
                        'days_range': days_range
                    })
                else:
                    status_list.append({
                        'symbol': symbol,
                        'has_data': False,
                        'record_count': 0,
                        'earliest_date': 'N/A',
                        'latest_date': 'N/A',
                        'days_range': 0
                    })

            if progress:
                progress.setValue(len(all_symbols))

            self.status_data = pd.DataFrame(status_list)
            self.update_display()

            self.status_label.setText(f"✅ Status refreshed for {len(all_symbols)} symbols")
            logger.info(f"Status refreshed for {len(all_symbols)} symbols")

        except Exception as e:
            logger.error(f"Failed to refresh status: {e}")
            self.status_label.setText(f"❌ Error: {e}")
            QMessageBox.critical(self, "Refresh Error", f"Failed to refresh status:\n\n{str(e)}")
        finally:
            self.refresh_btn.setEnabled(True)
            self.is_loading = False

    def update_display(self):
        """Update the display with current status data"""
        if self.status_data.empty:
            self.status_label.setText("No data available")
            return

        # Calculate summary
        total_symbols = len(self.status_data)
        symbols_with_data = len(self.status_data[self.status_data['has_data']])
        symbols_missing = total_symbols - symbols_with_data

        # Update summary labels
        self.update_stat_value("Total", str(total_symbols))
        self.update_stat_value("Available", str(symbols_with_data))
        self.update_stat_value("Missing", str(symbols_missing))

        # Apply current filter
        self.apply_filter()

    def update_stat_value(self, title, value):
        """Update a statistic value label"""
        label = self.findChild(QLabel, f"{title}_value")
        if label:
            label.setText(value)

    def on_filter_changed(self, filter_value):
        """Handle filter change"""
        self.current_filter = filter_value
        if self.tree:  # Only apply if tree exists
            self.apply_filter()

    def apply_filter(self):
        """Apply the selected filter to the display"""
        # Check if tree exists
        if not self.tree:
            return

        # Clear existing items
        self.tree.clear()

        if self.status_data.empty:
            return

        # Filter data based on selection
        if self.current_filter == "available":
            filtered_data = self.status_data[self.status_data['has_data']]
        elif self.current_filter == "missing":
            filtered_data = self.status_data[~self.status_data['has_data']]
        else:  # all
            filtered_data = self.status_data

        # Populate tree
        for _, row in filtered_data.iterrows():
            item = QTreeWidgetItem()

            # Symbol
            item.setText(0, row['symbol'])

            # Status icon
            status_icon = "✓" if row['has_data'] else "✗"
            item.setText(1, status_icon)

            # Records
            records_text = f"{row['record_count']:,}" if row['record_count'] > 0 else "-"
            item.setText(2, records_text)

            # Dates
            item.setText(3, row['earliest_date'])
            item.setText(4, row['latest_date'])

            # Days range
            days_text = str(row['days_range']) if row['days_range'] > 0 else "-"
            item.setText(5, days_text)

            # Color coding
            if row['has_data']:
                # Green for available
                for col in range(6):
                    item.setForeground(col, QBrush(QColor("#28a745")))
            else:
                # Red for missing
                for col in range(6):
                    item.setForeground(col, QBrush(QColor("#dc3545")))

            # Center align status and symbol
            item.setTextAlignment(0, Qt.AlignCenter)
            item.setTextAlignment(1, Qt.AlignCenter)
            item.setTextAlignment(2, Qt.AlignRight | Qt.AlignVCenter)
            item.setTextAlignment(3, Qt.AlignCenter)
            item.setTextAlignment(4, Qt.AlignCenter)
            item.setTextAlignment(5, Qt.AlignCenter)

            self.tree.addTopLevelItem(item)

        # Update status label
        self.status_label.setText(f"Showing {len(filtered_data)} of {len(self.status_data)} stocks")

    def delete_selected_stocks(self):
        """Delete data for selected stocks from database"""
        # Get selected items
        selected_items = self.tree.selectedItems()

        if not selected_items:
            QMessageBox.warning(
                self,
                "No Selection",
                "Please select one or more stocks from the list to delete."
            )
            return

        # Collect symbols and their record counts
        stocks_to_delete = []
        total_records = 0

        for item in selected_items:
            symbol = item.text(0)
            records_text = item.text(2)

            if records_text != "-":
                record_count = int(records_text.replace(",", ""))
                stocks_to_delete.append({
                    'symbol': symbol,
                    'records': record_count
                })
                total_records += record_count

        if not stocks_to_delete:
            QMessageBox.information(
                self,
                "No Data",
                "Selected stocks have no data to delete."
            )
            return

        # Build confirmation message
        stock_count = len(stocks_to_delete)
        if stock_count == 1:
            confirm_msg = f"Are you sure you want to delete ALL data for {stocks_to_delete[0]['symbol']}?\n\n"
            confirm_msg += f"This will permanently remove {total_records:,} records.\n\n"
        else:
            confirm_msg = f"Are you sure you want to delete data for {stock_count} stocks?\n\n"
            confirm_msg += f"Total records to delete: {total_records:,}\n\n"
            confirm_msg += "Stocks:\n"
            for stock in stocks_to_delete[:5]:
                confirm_msg += f"  • {stock['symbol']}: {stock['records']:,} records\n"
            if stock_count > 5:
                confirm_msg += f"  ... and {stock_count - 5} more\n\n"

        confirm_msg += "This action cannot be undone!"

        # Confirmation dialog
        reply = QMessageBox.question(
            self,
            "Confirm Deletion",
            confirm_msg,
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply != QMessageBox.Yes:
            return

        # Double confirmation for safety
        final_reply = QMessageBox.warning(
            self,
            "Final Confirmation",
            f"Last chance!\n\nDelete {total_records:,} records for {stock_count} stock(s)?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if final_reply != QMessageBox.Yes:
            self.status_label.setText("Deletion cancelled")
            return

        # Perform deletion
        deleted_count = 0
        failed_stocks = []

        try:
            if not db_manager.is_initialized:
                db_manager.initialize()

            with db_manager.engine.connect() as conn:
                from sqlalchemy import text

                for stock in stocks_to_delete:
                    symbol = stock['symbol']
                    try:
                        logger.info(f"Deleting data for {symbol} ({stock['records']} records)")

                        delete_query = text("DELETE FROM stock_data WHERE ticker = :ticker")
                        result = conn.execute(delete_query, {'ticker': symbol})
                        deleted_count += result.rowcount

                    except Exception as e:
                        logger.error(f"Failed to delete {symbol}: {e}")
                        failed_stocks.append(symbol)

                conn.commit()

            # Show results
            if failed_stocks:
                QMessageBox.warning(
                    self,
                    "Partial Success",
                    f"Deleted {deleted_count:,} records.\n\n"
                    f"Failed to delete: {', '.join(failed_stocks)}"
                )
            else:
                logger.info(f"Successfully deleted {deleted_count} records for {stock_count} stocks")
                QMessageBox.information(
                    self,
                    "Deletion Complete",
                    f"Successfully deleted {deleted_count:,} records for {stock_count} stock(s)"
                )

            # Refresh the status display
            self.refresh_status()

        except Exception as e:
            logger.error(f"Failed to delete data: {e}")
            QMessageBox.critical(
                self,
                "Deletion Failed",
                f"Failed to delete data:\n\n{str(e)}"
            )
