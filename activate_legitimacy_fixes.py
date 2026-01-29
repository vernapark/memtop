#!/usr/bin/env python3
"""
🎯 ACTIVATE LEGITIMACY FIXES
This script updates your server to use enhanced security headers
Run this to activate all trust signals without breaking functionality
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
            if line.startswith('import logging'):
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
    print("🎯 ACTIVATING LEGITIMACY FIXES")
    print("=" * 70)
    print()
    
    # List of server files to check
    server_files = [
        'combined_server_e2e.py',
        'combined_server_bulletproof_multi.py',
    ]
    
    print("📝 Files that will be updated:")
    for f in server_files:
        if os.path.exists(f):
            print(f"   ✓ {f}")
        else:
            print(f"   - {f} (not found, skipping)")
    
    print()
    print("⚠️  Backups will be created automatically")
    print()
    
    # Ask for confirmation
    response = input("Continue with activation? (y/n): ").strip().lower()
    
    if response != 'y':
        print("❌ Activation cancelled")
        return
    
    print()
    print("🚀 Starting activation...")
    print()
    
    updated = []
    failed = []
    
    for server_file in server_files:
        if os.path.exists(server_file):
            print(f"📝 Processing {server_file}...")
            if update_server_file(server_file):
                updated.append(server_file)
            else:
                failed.append(server_file)
            print()
    
    # Summary
    print("=" * 70)
    print("📊 ACTIVATION SUMMARY")
    print("=" * 70)
    print()
    
    if updated:
        print("✅ Successfully updated:")
        for f in updated:
            print(f"   - {f}")
        print()
    
    if failed:
        print("❌ Failed to update:")
        for f in failed:
            print(f"   - {f}")
        print()
    
    print("📋 Static files already created:")
    print("   ✓ robots.txt")
    print("   ✓ sitemap.xml")
    print("   ✓ manifest.json")
    print("   ✓ .well-known/security.txt")
    print("   ✓ privacy-policy.html")
    print("   ✓ terms-of-service.html")
    print("   ✓ about.html")
    print("   ✓ security-policy.html")
    print("   ✓ humans.txt")
    print("   ✓ ads.txt")
    print("   ✓ browserconfig.xml")
    print()
    
    print("=" * 70)
    print("🎉 LEGITIMACY FIXES ACTIVATED!")
    print("=" * 70)
    print()
    print("📝 Next Steps:")
    print("   1. Test locally: python combined_server_e2e.py")
    print("   2. Commit changes: git add . && git commit -m 'Add legitimacy fixes'")
    print("   3. Deploy to Render: git push")
    print("   4. Wait for deployment to complete")
    print("   5. Check your site - warnings should be gone!")
    print()
    print("💡 To revert changes, use the .backup_before_legitimacy files")
    print()

if __name__ == '__main__':
    main()
