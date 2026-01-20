#!/usr/bin/env python3
"""
Production Web Server for Video Streaming Website
Optimized for Render.com deployment
"""
import http.server
import socketserver
import os
import json
from urllib.parse import unquote

# Get port from environment (Render.com provides this)
PORT = int(os.getenv('PORT', 10000))
HOST = os.getenv('HOST', '0.0.0.0')

class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def translate_path(self, path):
        """Translate path to handle custom routes"""
        # Remove query string
        path = path.split('?', 1)[0]
        path = path.split('#', 1)[0]
        
        # Special handling for admin route
        if path == '/parking55009hvSweJimbs5hhinbd56y':
            path = '/parking55009hvSweJimbs5hhinbd56y.html'
            print(f"[ADMIN] Access from {self.address_string()}")
        
        # Call parent's translate_path with the modified path
        return super().translate_path(path)
    
    def end_headers(self):
        # Add security headers
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('X-Frame-Options', 'DENY')
        self.send_header('X-XSS-Protection', '1; mode=block')
        super().end_headers()
    
    def log_message(self, format, *args):
        # Custom logging
        print(f"[WEB] {self.address_string()} - {format % args}")

# Change to script directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

print("=" * 60)
print(f"🌐 Video Streaming Website Server")
print(f"📍 Host: {HOST}")
print(f"🔌 Port: {PORT}")
print(f"🌍 Environment: {'Production (Render.com)' if os.getenv('RENDER') else 'Development'}")
print("=" * 60)

# Enable reuse address for quick restarts
socketserver.TCPServer.allow_reuse_address = True

# Start server
with socketserver.TCPServer((HOST, PORT), CustomHandler) as httpd:
    print(f"✅ Server running on http://{HOST}:{PORT}")
    print("🔐 Admin: /parking55009hvSweJimbs5hhinbd56y")
    print("=" * 60)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n⛔ Server stopped.")
