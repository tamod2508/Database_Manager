#!/usr/bin/env python3
"""
Debug script to check last update time path resolution
"""

import os
import json
from pathlib import Path
from datetime import datetime

print("🔍 Debugging Last Update Time...")
print("=" * 40)

# Method 1: Check if the JSON file exists and what it contains
print("1. Checking JSON file directly:")
json_path_direct = Path("data/last_update.json")
print(f"   Direct path: {json_path_direct.absolute()}")
print(f"   Exists: {json_path_direct.exists()}")

if json_path_direct.exists():
    try:
        with open(json_path_direct, 'r') as f:
            data = json.load(f)
        print(f"   Content: {data}")
    except Exception as e:
        print(f"   Error reading: {e}")

# Method 2: Check the path resolution used in main_window.py
print("\n2. Checking path resolution from GUI perspective:")
# Simulate the path resolution from main_window.py
current_file = Path(__file__)  # This script location
print(f"   Current file: {current_file}")

# This mimics the path resolution in main_window.py
# Path(__file__).parent.parent.parent.parent from gui_qt/main_window.py
app_dir_from_gui = current_file.parent / "src" / "gui_qt" / "main_window.py"
print(f"   Simulated GUI file: {app_dir_from_gui}")

# The actual resolution that should happen
gui_file_parent = Path("src/gui_qt/main_window.py").parent.parent.parent.parent
status_file_gui = gui_file_parent / 'data' / 'last_update.json'
print(f"   GUI resolved path: {status_file_gui.absolute()}")
print(f"   GUI path exists: {status_file_gui.exists()}")

# Method 3: Check what your existing tkinter GUI uses
print("\n3. Checking existing status panel logic:")
try:
    import sys
    sys.path.insert(0, "src")
    
    # Try to read using the same logic as your existing status_panel.py
    app_dir = Path(__file__).parent
    status_file = app_dir / 'data' / 'last_update.json'
    print(f"   Status panel path: {status_file.absolute()}")
    print(f"   Status panel exists: {status_file.exists()}")
    
    if status_file.exists():
        with open(status_file, 'r') as f:
            data = json.load(f)
        print(f"   Status panel content: {data}")
        
        # Test the extraction logic
        full_timestamp = data.get('last_update', 'Never')
        if full_timestamp != 'Never' and len(full_timestamp) >= 10:
            result = full_timestamp[:16]
            print(f"   Extracted time: '{result}'")
        else:
            print(f"   Full timestamp: '{full_timestamp}'")
            print(f"   Length: {len(full_timestamp)}")
    
except Exception as e:
    print(f"   Error: {e}")

# Method 4: Create a test file if none exists
print("\n4. Testing file creation:")
test_status_file = Path("data/last_update.json")
if not test_status_file.exists():
    print("   Creating test file...")
    os.makedirs(test_status_file.parent, exist_ok=True)
    
    test_data = {
        'last_update': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'timestamp': datetime.now().isoformat()
    }
    
    with open(test_status_file, 'w') as f:
        json.dump(test_data, f, indent=2)
    
    print(f"   Created: {test_status_file.absolute()}")
    print(f"   Content: {test_data}")

print("\n" + "=" * 40)
print("✅ Debug complete!")
