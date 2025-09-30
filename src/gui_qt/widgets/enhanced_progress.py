"""
Enhanced progress indicators with multiple styles
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QMovie

class LoadingSpinner(QWidget):
    """Animated loading spinner"""
    
    def __init__(self, message="Loading...", parent=None):
        super().__init__(parent)
        self.setup_ui(message)
        
    def setup_ui(self, message):
        """Setup spinner UI"""
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(16)
        
        # Animated dots label (simple text-based spinner)
        self.spinner_label = QLabel("⏳")
        self.spinner_label.setStyleSheet("""
            QLabel {
                font-size: 48px;
                color: #0466c8;
            }
        """)
        self.spinner_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.spinner_label)
        
        # Message label
        self.message_label = QLabel(message)
        self.message_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: 600;
                color: #ffffff;
            }
        """)
        self.message_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.message_label)
        
        # Animate spinner
        self.spinner_frames = ["⏳", "⌛", "⏳", "⌛"]
        self.current_frame = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.animate)
        self.timer.start(500)
        
    def animate(self):
        """Animate the spinner"""
        self.current_frame = (self.current_frame + 1) % len(self.spinner_frames)
        self.spinner_label.setText(self.spinner_frames[self.current_frame])
        
    def set_message(self, message):
        """Update the message"""
        self.message_label.setText(message)
        
    def stop(self):
        """Stop the animation"""
        self.timer.stop()


class DetailedProgressWidget(QWidget):
    """Detailed progress widget with status information"""
    
    cancelled = Signal()
    
    def __init__(self, title="Processing", parent=None):
        super().__init__(parent)
        self.setup_ui(title)
        
    def setup_ui(self, title):
        """Setup progress widget UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)
        
        # Title
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: 700;
                color: #ffffff;
            }
        """)
        layout.addWidget(title_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #4a5468;
                border-radius: 8px;
                text-align: center;
                background-color: #2d3441;
                color: #ffffff;
                font-weight: 600;
                height: 28px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                           stop:0 #0570d8, stop:1 #0466c8);
                border-radius: 6px;
            }
        """)
        layout.addWidget(self.progress_bar)
        
        # Status label
        self.status_label = QLabel("Initializing...")
        self.status_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #979dac;
            }
        """)
        layout.addWidget(self.status_label)
        
        # Details label (smaller text for extra info)
        self.details_label = QLabel("")
        self.details_label.setStyleSheet("""
            QLabel {
                font-size: 11px;
                color: #7d8597;
                font-family: 'Monaco', 'Courier New', monospace;
            }
        """)
        layout.addWidget(self.details_label)
        
    def set_progress(self, value, status="", details=""):
        """Update progress value and status"""
        self.progress_bar.setValue(int(value))
        if status:
            self.status_label.setText(status)
        if details:
            self.details_label.setText(details)
            
    def set_indeterminate(self):
        """Set progress bar to indeterminate mode"""
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(0)
        
    def set_determinate(self, maximum=100):
        """Set progress bar to determinate mode"""
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(maximum)


class InlineProgressIndicator(QWidget):
    """Small inline progress indicator for status bars"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        """Setup inline indicator"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        # Small spinner
        self.spinner_label = QLabel("●")
        self.spinner_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #0466c8;
            }
        """)
        layout.addWidget(self.spinner_label)
        
        # Message
        self.message_label = QLabel("Loading...")
        self.message_label.setStyleSheet("""
            QLabel {
                font-size: 11px;
                color: #979dac;
            }
        """)
        layout.addWidget(self.message_label)
        
        # Animate
        self.colors = ["#0466c8", "#0570d8", "#1f85fa", "#4ba3fb"]
        self.current_color = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.animate)
        self.timer.start(300)
        
    def animate(self):
        """Animate the indicator"""
        self.current_color = (self.current_color + 1) % len(self.colors)
        self.spinner_label.setStyleSheet(f"""
            QLabel {{
                font-size: 12px;
                color: {self.colors[self.current_color]};
            }}
        """)
        
    def set_message(self, message):
        """Update message"""
        self.message_label.setText(message)
        
    def stop(self):
        """Stop animation and show completion"""
        self.timer.stop()
        self.spinner_label.setText("✓")
        self.spinner_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #28a745;
            }
        """)
