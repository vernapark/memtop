"""
🍯 HONEYPOT & DECOY ENDPOINTS
Trap attackers with fake admin panels, APIs, and vulnerabilities
"""
import secrets
import time
import json
from collections import defaultdict
from aiohttp import web
import asyncio

class HoneypotSystem:
    """Advanced honeypot system to detect and trap attackers"""
    
    def __init__(self):
        # Track attackers who hit honeypots
        self.trapped_ips = defaultdict(lambda: {
            'hits': 0,
            'first_seen': time.time(),
            'endpoints_hit': set(),
            'is_attacker': False,
            'banned': False
        })
        
        # Fake vulnerability patterns
        self.fake_vulns = {
            'sql_injection': '/api/users?id=1 OR 1=1',
            'path_traversal': '/api/file?path=../../etc/passwd',
            'command_injection': '/api/exec?cmd=whoami',
            'xxe': '/api/xml/parse',
            'ssrf': '/api/fetch?url=http://localhost',
            'lfi': '/api/include?file=../../../../etc/shadow'
        }
        
        # Decoy data to feed attackers
        self.decoy_data = {
            'fake_users': [
                {'id': 1, 'username': 'admin', 'email': 'admin@example.com', 'role': 'superadmin'},
                {'id': 2, 'username': 'testuser', 'email': 'test@example.com', 'role': 'user'},
                {'id': 3, 'username': 'developer', 'email': 'dev@example.com', 'role': 'developer'}
            ],
            'fake_api_keys': [
                secrets.token_hex(32),
                secrets.token_hex(32),
                secrets.token_hex(32)
            ],
            'fake_database_creds': {
                'host': '192.168.1.100',
                'username': 'db_admin',
                'password': 'P@ssw0rd123',
                'database': 'production_db'
            }
        }
    
    def mark_as_attacker(self, ip: str):
        """Mark IP as confirmed attacker"""
        self.trapped_ips[ip]['is_attacker'] = True
        self.trapped_ips[ip]['banned'] = True
    
    def is_trapped(self, ip: str) -> bool:
        """Check if IP has been trapped"""
        return self.trapped_ips[ip]['banned']
    
    def record_honeypot_hit(self, ip: str, endpoint: str):
        """Record when IP hits honeypot"""
        data = self.trapped_ips[ip]
        data['hits'] += 1
        data['endpoints_hit'].add(endpoint)
        
        # Auto-ban after multiple honeypot hits
        if data['hits'] >= 3:
            self.mark_as_attacker(ip)

# Global honeypot instance
honeypot = HoneypotSystem()

# ============================================================================
# FAKE ADMIN PANELS (Traps for attackers)
# ============================================================================

async def fake_admin_login(request):
    """Fake admin login page to trap attackers"""
    ip = request.headers.get('X-Forwarded-For', request.remote).split(',')[0].strip()
    honeypot.record_honeypot_hit(ip, '/admin/login')
    
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Admin Login</title>
        <style>
            body { font-family: Arial; background: #f0f0f0; }
            .login-box { width: 300px; margin: 100px auto; background: white; padding: 30px; border-radius: 5px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            input { width: 100%; padding: 10px; margin: 10px 0; border: 1px solid #ddd; border-radius: 3px; }
            button { width: 100%; padding: 10px; background: #007bff; color: white; border: none; border-radius: 3px; cursor: pointer; }
        </style>
    </head>
    <body>
        <div class="login-box">
            <h2>Admin Panel</h2>
            <form method="POST" action="/admin/authenticate">
                <input type="text" name="username" placeholder="Username" required>
                <input type="password" name="password" placeholder="Password" required>
                <button type="submit">Login</button>
            </form>
        </div>
    </body>
    </html>
    """
    return web.Response(text=html, content_type='text/html')

async def fake_admin_auth(request):
    """Fake authentication endpoint"""
    ip = request.headers.get('X-Forwarded-For', request.remote).split(',')[0].strip()
    honeypot.record_honeypot_hit(ip, '/admin/authenticate')
    
    # Mark as attacker trying to break in
    honeypot.mark_as_attacker(ip)
    
    # Return fake error
    return web.Response(
        text=json.dumps({'error': 'Invalid credentials'}),
        content_type='application/json',
        status=401
    )

# ============================================================================
# FAKE API ENDPOINTS (Decoys)
# ============================================================================

async def fake_api_users(request):
    """Fake users API endpoint"""
    ip = request.headers.get('X-Forwarded-For', request.remote).split(',')[0].strip()
    honeypot.record_honeypot_hit(ip, '/api/users')
    
    # Return fake user data
    return web.Response(
        text=json.dumps({
            'users': honeypot.decoy_data['fake_users'],
            'total': len(honeypot.decoy_data['fake_users'])
        }),
        content_type='application/json'
    )

async def fake_api_config(request):
    """Fake config API that reveals 'sensitive' data"""
    ip = request.headers.get('X-Forwarded-For', request.remote).split(',')[0].strip()
    honeypot.record_honeypot_hit(ip, '/api/config')
    honeypot.mark_as_attacker(ip)  # Anyone accessing this is definitely an attacker
    
    # Return fake sensitive config
    return web.Response(
        text=json.dumps({
            'database': honeypot.decoy_data['fake_database_creds'],
            'api_keys': honeypot.decoy_data['fake_api_keys'],
            'secret_key': secrets.token_hex(32),
            'debug_mode': True
        }),
        content_type='application/json'
    )

async def fake_api_debug(request):
    """Fake debug endpoint"""
    ip = request.headers.get('X-Forwarded-For', request.remote).split(',')[0].strip()
    honeypot.record_honeypot_hit(ip, '/api/debug')
    honeypot.mark_as_attacker(ip)
    
    return web.Response(
        text=json.dumps({
            'php_info': 'PHP Version 8.1.0',
            'server_info': 'Apache/2.4.52 (Ubuntu)',
            'loaded_modules': ['mod_ssl', 'mod_rewrite', 'mod_php'],
            'environment': dict(request.headers)
        }),
        content_type='application/json'
    )

# ============================================================================
# FAKE VULNERABILITIES (Intentional honeypots)
# ============================================================================

async def fake_sql_injection_vuln(request):
    """Fake SQL injection vulnerability"""
    ip = request.headers.get('X-Forwarded-For', request.remote).split(',')[0].strip()
    honeypot.record_honeypot_hit(ip, '/api/search')
    
    query = request.query.get('q', '')
    
    # Detect SQL injection attempts
    sql_keywords = ['union', 'select', 'drop', 'insert', 'update', 'delete', '1=1', 'or 1=1']
    if any(keyword in query.lower() for keyword in sql_keywords):
        honeypot.mark_as_attacker(ip)
        
        # Return fake SQL error to make attacker think it worked
        return web.Response(
            text=json.dumps({
                'error': 'SQL Error: You have an error in your SQL syntax',
                'query': f'SELECT * FROM users WHERE name = \'{query}\'',
                'hint': 'near \'\' at line 1'
            }),
            content_type='application/json',
            status=500
        )
    
    return web.Response(text=json.dumps({'results': []}), content_type='application/json')

async def fake_path_traversal_vuln(request):
    """Fake path traversal vulnerability"""
    ip = request.headers.get('X-Forwarded-For', request.remote).split(',')[0].strip()
    honeypot.record_honeypot_hit(ip, '/api/file')
    
    filepath = request.query.get('path', '')
    
    # Detect path traversal attempts
    if '../' in filepath or '..\\' in filepath or 'etc/passwd' in filepath:
        honeypot.mark_as_attacker(ip)
        
        # Return fake file content
        return web.Response(
            text='root:x:0:0:root:/root:/bin/bash\nadmin:x:1000:1000:admin:/home/admin:/bin/bash',
            content_type='text/plain'
        )
    
    return web.Response(text='File not found', status=404)

# ============================================================================
# FAKE EXPOSED FILES (Common attacker targets)
# ============================================================================

async def fake_env_file(request):
    """Fake .env file exposure"""
    ip = request.headers.get('X-Forwarded-For', request.remote).split(',')[0].strip()
    honeypot.record_honeypot_hit(ip, '/.env')
    honeypot.mark_as_attacker(ip)
    
    fake_env = """
DB_HOST=192.168.1.100
DB_USER=admin
DB_PASSWORD=SuperSecret123!
DB_NAME=production_db

API_KEY=sk_live_51234567890abcdef
API_SECRET=whsec_1234567890abcdef

AWS_ACCESS_KEY=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY

STRIPE_KEY=sk_live_abcdefghijklmnop
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
"""
    return web.Response(text=fake_env, content_type='text/plain')

async def fake_phpinfo(request):
    """Fake phpinfo.php"""
    ip = request.headers.get('X-Forwarded-For', request.remote).split(',')[0].strip()
    honeypot.record_honeypot_hit(ip, '/phpinfo.php')
    honeypot.mark_as_attacker(ip)
    
    return web.Response(
        text='<html><body><h1>PHP Version 8.1.0</h1><p>System: Linux Ubuntu 20.04</p></body></html>',
        content_type='text/html'
    )

async def fake_git_config(request):
    """Fake .git/config exposure"""
    ip = request.headers.get('X-Forwarded-For', request.remote).split(',')[0].strip()
    honeypot.record_honeypot_hit(ip, '/.git/config')
    honeypot.mark_as_attacker(ip)
    
    fake_git = """
[core]
    repositoryformatversion = 0
    filemode = true
[remote "origin"]
    url = git@github.com:company/secret-project.git
    fetch = +refs/heads/*:refs/remotes/origin/*
[user]
    email = admin@company.com
    name = Admin User
"""
    return web.Response(text=fake_git, content_type='text/plain')

# ============================================================================
# HONEYPOT MIDDLEWARE
# ============================================================================

@web.middleware
async def honeypot_middleware(request, handler):
    """Check if IP is trapped in honeypot"""
    ip = request.headers.get('X-Forwarded-For', request.remote).split(',')[0].strip()
    
    # Block trapped attackers
    if honeypot.is_trapped(ip):
        # Send them to infinite redirect loop
        return web.Response(
            text='<html><head><meta http-equiv="refresh" content="0;url=/admin/login"></head></html>',
            content_type='text/html'
        )
    
    return await handler(request)

def setup_honeypot_routes(app):
    """Setup all honeypot routes"""
    # Fake admin panels
    app.router.add_get('/admin', fake_admin_login)
    app.router.add_get('/admin/login', fake_admin_login)
    app.router.add_post('/admin/authenticate', fake_admin_auth)
    app.router.add_get('/administrator', fake_admin_login)
    app.router.add_get('/wp-admin', fake_admin_login)
    app.router.add_get('/phpmyadmin', fake_admin_login)
    
    # Fake API endpoints
    app.router.add_get('/api/users', fake_api_users)
    app.router.add_get('/api/config', fake_api_config)
    app.router.add_get('/api/debug', fake_api_debug)
    app.router.add_get('/api/search', fake_sql_injection_vuln)
    app.router.add_get('/api/file', fake_path_traversal_vuln)
    
    # Fake exposed files
    app.router.add_get('/.env', fake_env_file)
    app.router.add_get('/phpinfo.php', fake_phpinfo)
    app.router.add_get('/.git/config', fake_git_config)
    app.router.add_get('/.git/HEAD', fake_git_config)
    app.router.add_get('/backup.sql', fake_env_file)
    app.router.add_get('/database.sql', fake_env_file)
