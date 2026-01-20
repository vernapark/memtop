#!/usr/bin/env python3
"""
Initialization script for first deployment
Ensures key_storage.json exists
"""
import os
import json

KEY_FILE = "key_storage.json"

def init_storage():
    """Initialize key storage if it doesn't exist"""
    if not os.path.exists(KEY_FILE):
        print(f"🔧 Initializing {KEY_FILE}...")
        initial_data = {
            "current_key": "",
            "created_at": "",
            "created_by": ""
        }
        with open(KEY_FILE, 'w') as f:
            json.dump(initial_data, f, indent=2)
        print(f"✅ Created {KEY_FILE}")
    else:
        print(f"✅ {KEY_FILE} already exists")

if __name__ == "__main__":
    init_storage()
