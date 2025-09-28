"""
Apple Silicon specific optimizations
"""

import os
import psutil
import subprocess
from typing import Dict, Any
from ..config.settings import config

class AppleSiliconOptimizer:
    """Hardware-specific optimizations for Apple Silicon"""
    
    def __init__(self):
        self.is_apple_silicon = config.is_apple_silicon
        self.cpu_count = config.cpu_count
        self.memory_gb = psutil.virtual_memory().total / (1024**3) # Identifies how much RAM is availabe in the system
        
    def get_optimal_settings(self) -> Dict[str, Any]:
        """Get optimal settings based on hardware"""
        
        base_settings = {
            'max_workers': config.MAX_WORKERS,
            'chunk_size': config.CHUNK_SIZE,
            'memory_limit_mb': int(self.memory_gb * 0.6 * 1024),  # 60% of RAM
        }
        
        if self.is_apple_silicon:
            # Apple Silicon optimizations
            apple_settings = {
                'use_high_performance_cores': True,
                'memory_mapping_size': 268435456,  # 256MB
                'cache_size': 20000,  # Larger cache for M-series,Value: 20000 pages (each page ≈ 4KB, so ≈ 80MB cache),Reasoning: Apple Silicon's memory hierarchy benefits from larger caches
                'temp_store': 'MEMORY', #Store temporary SQLite data in RAM
                'mmap_threshold': 64 * 1024,  # 64KB, Files larger than 64KB will use memory mapping
            }
            base_settings.update(apple_settings) #Merges apple_settings into base_settings
        else:
            # Intel Mac settings, more conservative than apple
            intel_settings = {
                'use_high_performance_cores': False,
                'memory_mapping_size': 134217728,  # 128MB
                'cache_size': 10000,
                'temp_store': 'DEFAULT', # Use disk for temp storage (safer on Intel)
                'mmap_threshold': 128 * 1024,  # 128KB
            }
            base_settings.update(intel_settings)
            
        return base_settings
    
    def configure_environment(self):
        """Set environment variables for optimal performance"""
        
        if self.is_apple_silicon:
            # Optimize for Apple Silicon
            os.environ['OPENBLAS_NUM_THREADS'] = str(self.cpu_count) #Controls OpenBLAS library threading
            os.environ['MKL_NUM_THREADS'] = str(self.cpu_count) #Controls Intel Math Kernel Library threading
            os.environ['VECLIB_MAXIMUM_THREADS'] = str(self.cpu_count) #Controls Apple's vector library threading
            os.environ['NUMEXPR_NUM_THREADS'] = str(self.cpu_count) #Controls NumExpr library threading
            
            # Use Accelerate framework
            os.environ['BLAS'] = 'Accelerate' #Tell math libraries to use Apple's optimized BLAS, BLAS: Basic Linear Algebra Subprograms, Accelerate: Apple's highly optimized math library for M-series chips
            os.environ['LAPACK'] = 'Accelerate' #Tell math libraries to use Apple's optimized LAPACK, LAPACK: Linear Algebra Package (more advanced than BLAS)
        
    def get_system_info(self) -> Dict[str, Any]:
        """Get detailed system information"""
        
        try:
            # Get macOS version
            #Runs the shell command sw_vers -productVersion
            #sw_vers: macOS command that shows system version
            #-productVersion: Flag to get just the version number
            #capture_output=True: Capture the command output
            #text=True: Return output as string (not bytes)
            
            macos_version = subprocess.run(['sw_vers', '-productVersion'], 
                                         capture_output=True, text=True)
            macos_version = macos_version.stdout.strip() #.stdout: Standard output from the command
        except:
            macos_version = "Unknown"
            
        return {
            'architecture': 'Apple Silicon' if self.is_apple_silicon else 'Intel',
            'cpu_count': self.cpu_count,
            'memory_gb': round(self.memory_gb, 2),
            'macos_version': macos_version,
            'optimal_workers': config.MAX_WORKERS,
            'performance_cores': self.is_apple_silicon
        }

# Global optimizer instance
optimizer = AppleSiliconOptimizer()