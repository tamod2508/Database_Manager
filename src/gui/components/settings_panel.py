"""
Simple settings panel
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox

from ...config.settings import config
from ...utils.logger import get_logger

logger = get_logger(__name__)

class SettingsPanel:
    """Simple settings panel"""
    
    def __init__(self, parent):
        self.parent = parent
        self.frame = ctk.CTkScrollableFrame(parent)
        self.setup_ui()
        
    def setup_ui(self):
        """Setup simple settings UI"""
        
        # Title
        title_label = ctk.CTkLabel(
            self.frame,
            text="Settings",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(padx=20, pady=20)
        
        # Database info
        info_frame = ctk.CTkFrame(self.frame)
        info_frame.pack(padx=20, pady=20, fill="x")
        
        ctk.CTkLabel(info_frame, text="Database Information", 
                    font=ctk.CTkFont(size=14, weight="bold")).pack(pady=10)
        
        info_text = f"""Database Path: {config.DB_PATH}
Data Directory: {config.DATA_DIR}
Companies CSV: {config.COMPANIES_CSV}
Chunk Size: {config.CHUNK_SIZE}
Max Workers: {config.MAX_WORKERS}"""
        
        info_label = ctk.CTkLabel(info_frame, text=info_text, justify="left")
        info_label.pack(padx=20, pady=10)
        
        # Simple controls
        controls_frame = ctk.CTkFrame(self.frame)
        controls_frame.pack(padx=20, pady=20, fill="x")
        
        ctk.CTkLabel(controls_frame, text="Quick Actions", 
                    font=ctk.CTkFont(size=14, weight="bold")).pack(pady=10)
        
        # Info button
        info_button = ctk.CTkButton(
            controls_frame,
            text="Show System Info",
            command=self.show_system_info,
            height=40
        )
        info_button.pack(pady=10, padx=20, fill="x")
        
    def show_system_info(self):
        """Show system information"""
        try:
            from ...core.apple_silicon_optimizer import optimizer
            system_info = optimizer.get_system_info()
            
            info_text = f"""System Information:

Architecture: {system_info['architecture']}
CPU Cores: {system_info['cpu_count']}
Memory: {system_info['memory_gb']} GB
macOS Version: {system_info['macos_version']}
Optimal Workers: {system_info['optimal_workers']}
Performance Cores: {system_info['performance_cores']}"""
            
            messagebox.showinfo("System Information", info_text)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to get system info: {e}")
