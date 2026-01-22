"""
Test Script for Multi-Cloudinary Account Setup
Verifies all accounts are configured correctly
"""
import json
import os
import sys

def test_accounts():
    """Test all Cloudinary accounts configuration"""
    
    print("=" * 70)
    print("🧪 Testing Multi-Cloudinary Account Setup")
    print("=" * 70)
    
    # Check if cloudinary is installed
    try:
        import cloudinary
        import cloudinary.api
        print("✅ Cloudinary library installed")
    except ImportError:
        print("❌ Cloudinary library not installed")
        print("   Run: pip install cloudinary")
        return False
    
    # Check for accounts file
    accounts_file = "cloudinary_accounts.json"
    if not os.path.exists(accounts_file):
        print(f"❌ File not found: {accounts_file}")
        print("   Create this file with your Cloudinary account credentials")
        return False
    
    print(f"✅ Found {accounts_file}")
    
    # Load accounts
    try:
        with open(accounts_file, 'r') as f:
            data = json.load(f)
            accounts = data.get('accounts', [])
    except Exception as e:
        print(f"❌ Error reading {accounts_file}: {e}")
        return False
    
    if not accounts:
        print("❌ No accounts found in file")
        return False
    
    print(f"✅ Found {len(accounts)} account(s) in configuration")
    print()
    
    # Test each account
    active_count = 0
    working_count = 0
    
    for i, account in enumerate(accounts, 1):
        name = account.get('name', f'Account {i}')
        cloud_name = account.get('cloud_name', '')
        api_key = account.get('api_key', '')
        api_secret = account.get('api_secret', '')
        is_active = account.get('active', True)
        
        print(f"📋 Account {i}: {name}")
        print(f"   Cloud Name: {cloud_name}")
        print(f"   API Key: {api_key[:4]}****{api_key[-4:] if len(api_key) > 8 else '****'}")
        print(f"   Status: {'🟢 Active' if is_active else '🔴 Inactive'}")
        
        if is_active:
            active_count += 1
        
        # Validate credentials exist
        if not cloud_name or not api_key or not api_secret:
            print("   ❌ Missing credentials")
            print()
            continue
        
        # Test connection
        if is_active:
            try:
                cloudinary.config(
                    cloud_name=cloud_name,
                    api_key=api_key,
                    api_secret=api_secret
                )
                
                # Try to get account usage
                result = cloudinary.api.usage()
                
                # Calculate storage info
                used_gb = result.get('storage', {}).get('usage', 0) / (1024**3)
                limit_gb = result.get('storage', {}).get('limit', 0) / (1024**3)
                
                bandwidth_used_gb = result.get('bandwidth', {}).get('usage', 0) / (1024**3)
                bandwidth_limit_gb = result.get('bandwidth', {}).get('limit', 0) / (1024**3)
                
                print(f"   ✅ Connection successful!")
                print(f"   📊 Storage: {used_gb:.2f} GB / {limit_gb:.2f} GB")
                print(f"   📡 Bandwidth: {bandwidth_used_gb:.2f} GB / {bandwidth_limit_gb:.2f} GB (this month)")
                
                # Calculate available space
                available_gb = limit_gb - used_gb
                print(f"   💾 Available: {available_gb:.2f} GB")
                
                working_count += 1
                
            except Exception as e:
                print(f"   ❌ Connection failed: {str(e)[:100]}")
        
        print()
    
    # Summary
    print("=" * 70)
    print("📊 Summary")
    print("=" * 70)
    print(f"Total Accounts: {len(accounts)}")
    print(f"Active Accounts: {active_count}")
    print(f"Working Accounts: {working_count}")
    
    if working_count == 0:
        print()
        print("❌ No working accounts found!")
        print("   Please check your credentials in cloudinary_accounts.json")
        return False
    elif working_count < active_count:
        print()
        print(f"⚠️  Warning: {active_count - working_count} active account(s) failed to connect")
        print("   Check credentials for failed accounts")
    else:
        print()
        print("✅ All active accounts are working correctly!")
    
    print("=" * 70)
    return working_count > 0


def main():
    """Main function"""
    success = test_accounts()
    
    if success:
        print()
        print("🎉 Setup looks good! You're ready to use multi-Cloudinary!")
        print()
        print("Next steps:")
        print("1. Update your server to use multi_cloudinary_setup.py")
        print("2. Deploy to Render.com")
        print("3. Upload videos and watch them distribute across accounts")
        sys.exit(0)
    else:
        print()
        print("❌ Please fix the issues above before deploying")
        sys.exit(1)


if __name__ == '__main__':
    main()
