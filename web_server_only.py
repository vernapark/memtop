"""
Simple Web Server for Render.com
Serves video streaming website with admin panel
NO Telegram bot integration
"""
import os
import json
import secrets
import string
import sys
from datetime import datetime
from aiohttp import web
import logging

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

# Configuration
PORT = int(os.getenv('PORT', 10000))
HOST = '0.0.0.0'
KEY_STORAGE_FILE = "key_storage.json"
ACCESS_CODES_FILE = "access_codes.json"

# ============================================================================
# FILE INITIALIZATION
# ============================================================================

def initialize_files():
    """Initialize storage files if they don't exist"""
    try:
        if not os.path.exists(KEY_STORAGE_FILE):
            initial_data = {"current_key": "", "created_at": "", "created_by": ""}
            with open(KEY_STORAGE_FILE, 'w') as f:
                json.dump(initial_data, f, indent=2)
            logger.info(f"✅ Created {KEY_STORAGE_FILE}")
        
        if not os.path.exists(ACCESS_CODES_FILE):
            initial_data = {"access_codes": []}
            with open(ACCESS_CODES_FILE, 'w') as f:
                json.dump(initial_data, f, indent=2)
            logger.info(f"✅ Created {ACCESS_CODES_FILE}")
    except Exception as e:
        logger.error(f"❌ Failed to initialize files: {e}")
        raise

# ============================================================================
# STORAGE FUNCTIONS
# ============================================================================

def generate_key(length=32):
    """Generate a secure random key"""
    characters = string.ascii_letters + string.digits
    return ''.join(secrets.choice(characters) for _ in range(length))

def load_key_storage():
    """Load current key from storage"""
    if os.path.exists(KEY_STORAGE_FILE):
        try:
            with open(KEY_STORAGE_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading key storage: {e}")
    return {"current_key": "", "created_at": "", "created_by": ""}

def save_key_storage(data):
    """Save key to storage"""
    with open(KEY_STORAGE_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def load_access_codes():
    """Load access codes from storage"""
    if os.path.exists(ACCESS_CODES_FILE):
        try:
            with open(ACCESS_CODES_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading access codes: {e}")
    return {"access_codes": []}

def save_access_codes(data):
    """Save access codes to storage"""
    with open(ACCESS_CODES_FILE, 'w') as f:
        json.dump(data, f, indent=2)

# ============================================================================
# WEB SERVER HANDLERS
# ============================================================================

async def serve_file(request):
    """Serve static files"""
    try:
        path = request.path
        
        if path == '/':
            path = '/index.html'
        
        if path == '/parking55009hvSweJimbs5hhinbd56y':
            path = '/parking55009hvSweJimbs5hhinbd56y.html'
            logger.info(f"[ADMIN] Access from {request.remote}")
        
        file_path = path.lstrip('/')
        
        if '..' in file_path:
            return web.Response(status=403, text="Forbidden")
        
        if not os.path.exists(file_path):
            logger.warning(f"File not found: {file_path}")
            return web.Response(status=404, text="Not Found")
        
        content_type = 'text/html'
        if file_path.endswith('.css'):
            content_type = 'text/css'
        elif file_path.endswith('.js'):
            content_type = 'application/javascript'
        elif file_path.endswith('.json'):
            content_type = 'application/json'
        elif file_path.endswith('.png'):
            content_type = 'image/png'
        elif file_path.endswith('.jpg') or file_path.endswith('.jpeg'):
            content_type = 'image/jpeg'
        elif file_path.endswith('.gif'):
            content_type = 'image/gif'
        elif file_path.endswith('.svg'):
            content_type = 'image/svg+xml'
        elif file_path.endswith('.mp4'):
            content_type = 'video/mp4'
        
        with open(file_path, 'rb') as f:
            content = f.read()
        
        return web.Response(body=content, content_type=content_type)
    
    except Exception as e:
        logger.error(f"Error serving file {request.path}: {e}")
        return web.Response(status=500, text="Internal Server Error")

async def health_check(request):
    """Health check endpoint for Render"""
    return web.Response(text="OK - Web Server Running", status=200)

# ============================================================================
# MAIN APPLICATION
# ============================================================================

async def main():
    """Start the web server"""
    try:
        print("=" * 70, flush=True)
        print("🚀 Starting Web Server (NO Telegram Bot)", flush=True)
        print("=" * 70, flush=True)
        print(f"Python version: {sys.version}", flush=True)
        print(f"PORT: {PORT}", flush=True)
        print(f"HOST: {HOST}", flush=True)
        print("=" * 70, flush=True)
        
        # Initialize storage files
        logger.info("Initializing storage files...")
        initialize_files()
        logger.info("✅ Storage files initialized")
        
        # Create web application
        logger.info("Creating web application...")
        app = web.Application()
        
        # Add routes
        app.router.add_get("/health", health_check)
        app.router.add_route('*', "/{path:.*}", serve_file)
        
        logger.info("📍 Routes registered:")
        logger.info(f"   GET /health -> health_check")
        logger.info(f"   * /{{path:.*}} -> serve_file")
        
        # Start web server
        logger.info(f"Starting web server on {HOST}:{PORT}...")
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, HOST, PORT)
        await site.start()
        
        print("=" * 70, flush=True)
        print("✅ Web Server is running!", flush=True)
        print(f"🌐 Website: http://{HOST}:{PORT}", flush=True)
        print("=" * 70, flush=True)
        logger.info("✅ Web server operational")
        
        # Keep running
        import asyncio
        logger.info("Entering main event loop...")
        await asyncio.Event().wait()
        
    except Exception as e:
        logger.error(f"❌ FATAL ERROR in main(): {e}", exc_info=True)
        print(f"\n❌ FATAL ERROR: {e}", file=sys.stderr, flush=True)
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    try:
        import asyncio
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Shutting down gracefully...")
    except Exception as e:
        print(f"\n❌ FATAL ERROR: {e}", file=sys.stderr, flush=True)
        import traceback
        traceback.print_exc()
        sys.exit(1)
