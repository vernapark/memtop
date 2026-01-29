#!/usr/bin/env python3
"""
🎯 AUTO ACTIVATE LEGITIMACY FIXES (Non-interactive)
This script updates your server to use enhanced security headers automatically
"""

import os
import sys

def update_server_file(server_file):
    """Update server file to use enhanced headers"""
    
    if not os.path.exists(server_file):
        print(f"❌ Server file not found: {server_file}")
        return False
    
    # Read current file
    with open(server_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if already updated
    if 'enhanced_security_headers' in content:
        print(f"✅ {server_file} already using enhanced headers!")
        return True
    
    # Backup original
    backup_file = f"{server_file}.backup_before_legitimacy"
    with open(backup_file, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"📦 Backup created: {backup_file}")
    
    # Replace imports
    old_import = "from security_headers_middleware import security_headers_middleware, cors_middleware"
    new_import = "from enhanced_security_headers import enhanced_security_middleware, professional_cors_middleware"
    
    if old_import in content:
        content = content.replace(old_import, new_import)
        print("✅ Updated import statement")
    else:
        # Try to add import after other imports
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if 'import logging' in line:
                lines.insert(i + 1, new_import)
                content = '\n'.join(lines)
                print("✅ Added enhanced headers import")
                break
    
    # Replace middleware usage
    old_middleware = "middlewares=[security_headers_middleware, cors_middleware]"
    new_middleware = "middlewares=[enhanced_security_middleware, professional_cors_middleware]"
    
    if old_middleware in content:
        content = content.replace(old_middleware, new_middleware)
        print("✅ Updated middleware configuration")
    
    # Write updated file
    with open(server_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ {server_file} updated successfully!")
    return True

def main():
    print("=" * 70)
    print("🎯 AUTO-ACTIVATING LEGITIMACY FIXES")
    print("=" * 70)
    print()
    
    server_files = [
        'combined_server_e2e.py',
        'combined_server_bulletproof_multi.py',
    ]
    
    updated = []
    
    for server_file in server_files:
        if os.path.exists(server_file):
            print(f"📝 Processing {server_file}...")
            if update_server_file(server_file):
                updated.append(server_file)
            print()
    
    print("=" * 70)
    print("✅ ACTIVATION COMPLETE!")
    print("=" * 70)
    print()
    print(f"Updated {len(updated)} file(s)")
    print()

if __name__ == '__main__':
    main()
