#!/usr/bin/env python3
"""
COMBINED: Web Server + Telegram Bot
Everything runs in one process, sharing the same storage files
"""
import os
import json
import secrets
import string
import sys
from datetime import datetime
from aiohttp import web
import logging

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

# Configuration
PORT = int(os.getenv('PORT', 10000))
HOST = '0.0.0.0'
BOT_TOKEN = os.getenv("BOT_TOKEN", "8567043675:AAHB7CmPOfsWIHluLLk9hDF-8FBcN4LtOMM")
AUTHORIZED_CHAT_ID = int(os.getenv("AUTHORIZED_CHAT_ID", "2103408372"))
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "")
KEY_STORAGE_FILE = "key_storage.json"
ACCESS_CODES_FILE = "access_codes.json"

# ============================================================================
# STORAGE FUNCTIONS (SHARED BY BOT AND WEBSITE)
# ============================================================================

def initialize_files():
    """Initialize storage files if they don't exist"""
    if not os.path.exists(KEY_STORAGE_FILE):
        initial_data = {"current_key": "", "created_at": "", "created_by": ""}
        with open(KEY_STORAGE_FILE, 'w') as f:
            json.dump(initial_data, f, indent=2)
        logger.info(f"Created {KEY_STORAGE_FILE}")
    
    if not os.path.exists(ACCESS_CODES_FILE):
        initial_data = {"access_codes": []}
        with open(ACCESS_CODES_FILE, 'w') as f:
            json.dump(initial_data, f, indent=2)
        logger.info(f"Created {ACCESS_CODES_FILE}")

def generate_key(length=32):
    characters = string.ascii_letters + string.digits
    return ''.join(secrets.choice(characters) for _ in range(length))

def load_key_storage():
    if os.path.exists(KEY_STORAGE_FILE):
        try:
            with open(KEY_STORAGE_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error: {e}")
    return {"current_key": "", "created_at": "", "created_by": ""}

def save_key_storage(data):
    with open(KEY_STORAGE_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def load_access_codes():
    if os.path.exists(ACCESS_CODES_FILE):
        try:
            with open(ACCESS_CODES_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error: {e}")
    return {"access_codes": []}

def save_access_codes(data):
    with open(ACCESS_CODES_FILE, 'w') as f:
        json.dump(data, f, indent=2)

# ============================================================================
# TELEGRAM BOT HANDLERS
# ============================================================================

async def send_message(chat_id, text):
    """Send message to Telegram"""
    import aiohttp
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": chat_id, "text": text}
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=data) as resp:
            return await resp.json()

async def handle_telegram_webhook(request):
    """Handle incoming Telegram webhook"""
    try:
        update = await request.json()
        logger.info(f"Telegram update: {update.get('message', {}).get('text', 'N/A')}")
        
        if 'message' not in update:
            return web.Response(text="OK")
        
        message = update['message']
        chat_id = message['chat']['id']
        text = message.get('text', '')
        username = message['from'].get('username', 'Unknown')
        
        if chat_id != AUTHORIZED_CHAT_ID:
            await send_message(chat_id, "Unauthorized access.")
            return web.Response(text="OK")
        
        # Handle commands
        if text == '/start':
            response = (
                "Admin Key Manager Bot\n\n"
                "Admin Key Commands:\n"
                "/createkey - Generate new admin access key\n"
                "/currentkey - View current admin key\n\n"
                "User Access Code Commands:\n"
                "/generatecode - Generate user access code\n"
                "/listcodes - View all active access codes\n"
                "/revokecode - Remove an access code\n\n"
                "/help - Show detailed help"
            )
            await send_message(chat_id, response)
        
        elif text == '/help':
            response = (
                "Complete Help Guide\n\n"
                "The admin key is used to access the admin panel.\n"
                "Access codes allow users to enter the website.\n\n"
                "Commands:\n"
                "/createkey - Generate admin key\n"
                "/currentkey - View current key\n"
                "/generatecode - Create access code\n"
                "/listcodes - See all codes\n"
                "/revokecode <code> - Delete a code"
            )
            await send_message(chat_id, response)
        
        elif text == '/createkey':
            new_key = generate_key()
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            key_data = {
                "current_key": new_key,
                "created_at": timestamp,
                "created_by": username
            }
            save_key_storage(key_data)
            
            response = f"New Admin Key Generated!\n\nKey: {new_key}\n\nCreated: {timestamp}\nBy: @{username}\n\nKeep this key secure!"
            await send_message(chat_id, response)
        
        elif text == '/currentkey':
            key_data = load_key_storage()
            
            if not key_data.get('current_key'):
                await send_message(chat_id, "No admin key exists yet.\nUse /createkey to generate one.")
            else:
                response = f"Current Admin Key\n\nKey: {key_data['current_key']}\n\nCreated: {key_data.get('created_at', 'Unknown')}\nBy: @{key_data.get('created_by', 'Unknown')}"
                await send_message(chat_id, response)
        
        elif text == '/generatecode':
            new_code = generate_key(16)
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            codes_data = load_access_codes()
            codes_data['access_codes'].append(new_code)
            save_access_codes(codes_data)
            
            response = f"User Access Code Generated!\n\nCode: {new_code}\n\nCreated: {timestamp}\nTotal Active Codes: {len(codes_data['access_codes'])}\n\nShare this code with users."
            await send_message(chat_id, response)
        
        elif text == '/listcodes':
            codes_data = load_access_codes()
            codes = codes_data.get('access_codes', [])
            
            if not codes:
                await send_message(chat_id, "No active access codes.\nUse /generatecode to create one.")
            else:
                response = f"Active Access Codes ({len(codes)})\n\n"
                for i, code in enumerate(codes, 1):
                    response += f"{i}. {code}\n"
                response += f"\nTotal: {len(codes)} code(s)"
                await send_message(chat_id, response)
        
        elif text.startswith('/revokecode'):
            parts = text.split()
            if len(parts) < 2:
                await send_message(chat_id, "Usage: /revokecode <code>\n\nExample:\n/revokecode abc123xyz456")
            else:
                code_to_revoke = parts[1]
                
                codes_data = load_access_codes()
                codes = codes_data.get('access_codes', [])
                
                if code_to_revoke in codes:
                    codes.remove(code_to_revoke)
                    codes_data['access_codes'] = codes
                    save_access_codes(codes_data)
                    
                    await send_message(chat_id, f"Access code revoked!\n\nRemoved: {code_to_revoke}\nRemaining Codes: {len(codes)}")
                else:
                    await send_message(chat_id, f"Code not found: {code_to_revoke}")
        
        return web.Response(text="OK")
        
    except Exception as e:
        logger.error(f"Telegram webhook error: {e}", exc_info=True)
        return web.Response(status=500)

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
        elif file_path.endswith('.mp4'):
            content_type = 'video/mp4'
        
        with open(file_path, 'rb') as f:
            content = f.read()
        
        return web.Response(body=content, content_type=content_type)
    
    except Exception as e:
        logger.error(f"Error serving file {request.path}: {e}")
        return web.Response(status=500, text="Internal Server Error")

async def health_check(request):
    """Health check endpoint"""
    return web.Response(text="OK - Website & Bot Running")

# ============================================================================
# STARTUP
# ============================================================================

async def set_telegram_webhook():
    """Set Telegram webhook on startup"""
    if not WEBHOOK_URL:
        logger.warning("WEBHOOK_URL not set - bot will not work!")
        return
    
    import aiohttp
    webhook_url = f"{WEBHOOK_URL}/telegram-webhook"
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook"
    data = {"url": webhook_url}
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=data) as resp:
            result = await resp.json()
            if result.get('ok'):
                logger.info(f"Telegram webhook set to: {webhook_url}")
            else:
                logger.error(f"Failed to set webhook: {result}")

async def startup(app):
    """Run on startup"""
    initialize_files()
    await set_telegram_webhook()

def main():
    print("=" * 70)
    print("COMBINED SERVER: Website + Telegram Bot")
    print("=" * 70)
    print(f"Port: {PORT}")
    print(f"Webhook URL: {WEBHOOK_URL}")
    print("=" * 70)
    
    app = web.Application()
    
    # Bot webhook
    app.router.add_post('/telegram-webhook', handle_telegram_webhook)
    
    # Website routes
    app.router.add_get("/health", health_check)
    app.router.add_route('*', "/{path:.*}", serve_file)
    
    app.on_startup.append(startup)
    
    logger.info("Starting combined server...")
    web.run_app(app, host=HOST, port=PORT)

if __name__ == '__main__':
    main()
