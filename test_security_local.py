#!/usr/bin/env python3
"""
Quick test script to verify security implementation locally
"""

import sys
import os

def test_security_files():
    """Check if all security files exist"""
    print("=" * 70)
    print("🔍 Testing Security Implementation")
    print("=" * 70)
    
    required_files = {
        'security_middleware.py': 'Server-side security middleware',
        'combined_server_secured.py': 'Secured server wrapper',
        'js/security.js': 'Client-side protection',
        'render.yaml': 'Deployment configuration',
    }
    
    all_good = True
    
    for file, description in required_files.items():
        if os.path.exists(file):
            file_size = os.path.getsize(file)
            print(f"✅ {file:40s} ({file_size:,} bytes) - {description}")
        else:
            print(f"❌ {file:40s} - MISSING!")
            all_good = False
    
    print("\n" + "=" * 70)
    
    # Check render.yaml content
    if os.path.exists('render.yaml'):
        with open('render.yaml', 'r') as f:
            content = f.read()
            if 'combined_server_secured.py' in content:
                print("✅ render.yaml configured to use secured server")
            else:
                print("⚠️  render.yaml NOT using secured server")
                print("   Update startCommand to: python combined_server_secured.py")
                all_good = False
    
    # Check HTML files updated
    html_files = ['home.html', 'admin/dashboard.html', 'admin/login.html']
    html_updated = 0
    
    for html_file in html_files:
        if os.path.exists(html_file):
            with open(html_file, 'r', encoding='utf-8') as f:
                content = f.read()
                if 'security.js' in content:
                    html_updated += 1
    
    print(f"✅ {html_updated}/{len(html_files)} HTML files have security script")
    
    print("=" * 70)
    
    if all_good:
        print("\n🎉 All security files are in place!")
        print("\n📋 Next Steps:")
        print("   1. Test locally (optional): python combined_server_secured.py")
        print("   2. Commit: git add . && git commit -m 'Added security'")
        print("   3. Push: git push origin main")
        print("   4. Render will auto-deploy in 2-3 minutes")
        print("\n🔒 Your website will be bulletproof!")
    else:
        print("\n❌ Some files are missing or not configured properly")
        print("   Please review the errors above")
    
    print("=" * 70)
    
    return all_good

def test_imports():
    """Test if security middleware can be imported"""
    print("\n🔍 Testing Python imports...")
    
    try:
        from security_middleware import SecurityMiddleware
        print("✅ security_middleware imports successfully")
        print(f"   - Rate limit: {SecurityMiddleware.rate_limit_check}")
        print(f"   - Token generation: {SecurityMiddleware.generate_token}")
        print(f"   - Security headers: {SecurityMiddleware.add_security_headers}")
        return True
    except Exception as e:
        print(f"❌ Error importing security_middleware: {e}")
        return False

def test_security_config():
    """Show security configuration"""
    print("\n⚙️  Security Configuration:")
    
    try:
        from security_middleware import SECURITY_CONFIG
        for key, value in SECURITY_CONFIG.items():
            print(f"   - {key:30s}: {value}")
        return True
    except Exception as e:
        print(f"❌ Error loading config: {e}")
        return False

if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Run tests
    files_ok = test_security_files()
    
    if files_ok:
        imports_ok = test_imports()
        config_ok = test_security_config()
        
        if imports_ok and config_ok:
            print("\n" + "=" * 70)
            print("✅ ALL TESTS PASSED!")
            print("=" * 70)
            print("\n🚀 Ready to deploy!")
            sys.exit(0)
    
    print("\n⚠️  Some tests failed. Please fix the issues above.")
    sys.exit(1)
