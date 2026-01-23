#!/usr/bin/env python3
"""
🛡️ BULLETPROOF COMBINED SERVER WITH MULTI-CLOUDINARY SUPPORT + FULL TELEGRAM BOT
- Supports multiple Cloudinary accounts for increased storage
- Full Telegram bot with all commands (createkey, generatecode, etc.)
- Videos stored permanently in Cloudinary
- Metadata stored in Cloudinary (using context/tags)
"""
import os
import json
import secrets
import string
import sys
import random
from datetime import datetime
from aiohttp import web
import logging

# Visitor tracking imports
from visitor_tracking import (
    visitor_connect,
    visitor_heartbeat,
    visitor_disconnect,
    get_active_visitors
)

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
CLOUDINARY_ACCOUNTS_FILE = "cloudinary_accounts.json"

# ============================================================================
# MULTI-CLOUDINARY ACCOUNT MANAGEMENT
# ============================================================================

def load_cloudinary_accounts():
    """Load Cloudinary accounts - supports multiple OR single account"""
    accounts = []
    
    # Try loading from JSON file first (multi-account)
    if os.path.exists(CLOUDINARY_ACCOUNTS_FILE):
        try:
            with open(CLOUDINARY_ACCOUNTS_FILE, 'r') as f:
                data = json.load(f)
                accounts = data.get('accounts', [])
                if accounts:
                    logger.info(f"✅ Loaded {len(accounts)} Cloudinary accounts from {CLOUDINARY_ACCOUNTS_FILE}")
                    return accounts
        except Exception as e:
            logger.warning(f"Could not load {CLOUDINARY_ACCOUNTS_FILE}: {e}")
    
    # Fallback: Load from environment variables (single account - existing setup)
    cloud_name = os.getenv('CLOUDINARY_CLOUD_NAME')
    api_key = os.getenv('CLOUDINARY_API_KEY')
    api_secret = os.getenv('CLOUDINARY_API_SECRET')
    
    if cloud_name and api_key and api_secret:
        logger.info("✅ Using single Cloudinary account from environment variables")
        return [{
            "name": "Primary Account",
            "cloud_name": cloud_name,
            "api_key": api_key,
            "api_secret": api_secret,
            "active": True
        }]
    
    return []

def get_active_accounts():
    """Get only active Cloudinary accounts"""
    accounts = load_cloudinary_accounts()
    active = [acc for acc in accounts if acc.get('active', True)]
    return active

def select_account_for_upload():
    """Select a Cloudinary account for upload (random for load balancing)"""
    accounts = get_active_accounts()
    
    if not accounts:
        raise Exception("No active Cloudinary accounts available")
    
    selected = random.choice(accounts)
    logger.info(f"📤 Selected account: {selected.get('name', 'Unnamed')} for upload")
    return selected


def generate_cloudinary_thumbnail(public_id, cloud_name):
    """Generate Cloudinary thumbnail URL for video"""
    thumbnail_url = f"https://res.cloudinary.com/{cloud_name}/video/upload/so_1.0,w_640,h_360,c_fill,q_auto,f_jpg/{public_id}.jpg"
    logger.info(f"??? Generated thumbnail: {thumbnail_url}")
    return thumbnail_url

def configure_cloudinary(account):
    """Configure Cloudinary with specific account credentials"""
    import cloudinary
    cloudinary.config(
        cloud_name=account['cloud_name'],
        api_key=account['api_key'],
        api_secret=account['api_secret']
    )
    return account

# Validate Cloudinary config at startup
def validate_cloudinary_config():
    """Validate that at least one Cloudinary account is configured"""
    accounts = load_cloudinary_accounts()
    active_accounts = get_active_accounts()
    
    if not accounts:
        logger.error("=" * 70)
        logger.error("❌ CRITICAL ERROR: NO CLOUDINARY ACCOUNTS CONFIGURED!")
        logger.error("=" * 70)
        logger.error("You need to configure at least one Cloudinary account.")
        logger.error("")
        logger.error("OPTION 1: Use environment variables (single account):")
        logger.error("  - CLOUDINARY_CLOUD_NAME")
        logger.error("  - CLOUDINARY_API_KEY")
        logger.error("  - CLOUDINARY_API_SECRET")
        logger.error("")
        logger.error("OPTION 2: Create cloudinary_accounts.json (multiple accounts):")
        logger.error('  {"accounts": [{"name": "Account 1", "cloud_name": "xxx", ...}]}')
        logger.error("=" * 70)
        return False
    
    if not active_accounts:
        logger.error("=" * 70)
        logger.error("❌ ERROR: NO ACTIVE CLOUDINARY ACCOUNTS!")
        logger.error("=" * 70)
        logger.error(f"Found {len(accounts)} account(s) but none are active.")
        logger.error("Set 'active': true for at least one account.")
        logger.error("=" * 70)
        return False
    
    logger.info(f"✅ Cloudinary configured with {len(active_accounts)} active account(s)")
    for acc in active_accounts:
        logger.info(f"   - {acc.get('name', 'Unnamed')}: {acc['cloud_name']}")
    
    return True

CLOUDINARY_ENABLED = validate_cloudinary_config()

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
# TELEGRAM BOT HANDLERS (FULL IMPLEMENTATION)
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
                "🤖 Admin Key Manager Bot\n\n"
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
                "📚 Complete Help Guide\n\n"
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
            
            response = f"🔑 New Admin Key Generated!\n\nKey: {new_key}\n\nCreated: {timestamp}\nBy: @{username}\n\n🔒 Keep this key secure!"
            await send_message(chat_id, response)
        
        elif text == '/currentkey':
            key_data = load_key_storage()
            
            if not key_data.get('current_key'):
                await send_message(chat_id, "❌ No admin key exists yet.\nUse /createkey to generate one.")
            else:
                response = f"🔑 Current Admin Key\n\nKey: {key_data['current_key']}\n\nCreated: {key_data.get('created_at', 'Unknown')}\nBy: @{key_data.get('created_by', 'Unknown')}"
                await send_message(chat_id, response)
        
        elif text == '/generatecode':
            new_code = generate_key(16)
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            codes_data = load_access_codes()
            codes_data['access_codes'].append(new_code)
            save_access_codes(codes_data)
            
            response = f"🎟️ User Access Code Generated!\n\nCode: {new_code}\n\nCreated: {timestamp}\nTotal Active Codes: {len(codes_data['access_codes'])}\n\n📤 Share this code with users."
            await send_message(chat_id, response)
        
        elif text == '/listcodes':
            codes_data = load_access_codes()
            codes = codes_data.get('access_codes', [])
            
            if not codes:
                await send_message(chat_id, "❌ No active access codes.\nUse /generatecode to create one.")
            else:
                response = f"🎟️ Active Access Codes ({len(codes)})\n\n"
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
                    
                    await send_message(chat_id, f"✅ Access code revoked!\n\nRemoved: {code_to_revoke}\nRemaining Codes: {len(codes)}")
                else:
                    await send_message(chat_id, f"❌ Code not found: {code_to_revoke}")
        
        return web.Response(text="OK")
        
    except Exception as e:
        logger.error(f"Telegram webhook error: {e}", exc_info=True)
        return web.Response(status=500)

# ============================================================================
# CLOUDINARY VIDEO HANDLERS (WITH MULTI-ACCOUNT SUPPORT)
# ============================================================================

async def upload_video_to_cloudinary(request):
    """Upload video to Cloudinary with multi-account support"""
    
    if not CLOUDINARY_ENABLED:
        return web.json_response({
            "error": "Cloudinary not configured",
            "details": "Configure Cloudinary accounts to enable video uploads"
        }, status=503)
    
    try:
        import cloudinary
        import cloudinary.uploader
        
        # Select account for upload
        account = select_account_for_upload()
        configure_cloudinary(account)
        
        reader = await request.multipart()
        video_file = None
        thumbnail_file = None
        video_data = {}
        
        async for field in reader:
            if field.name == 'videoFile':
                video_file = await field.read()
            elif field.name == 'thumbnail':
                thumbnail_file = await field.read()
            else:
                value = await field.text()
                video_data[field.name] = value
        
        if not video_file:
            return web.json_response({"error": "No video file provided"}, status=400)
        
        logger.info(f"📤 Uploading to {account.get('name')}: {video_data.get('videoTitle', 'Untitled')}")
        
        # Upload thumbnail if provided
        thumbnail_url = None
        if thumbnail_file:
            thumbnail_result = cloudinary.uploader.upload(
                thumbnail_file,
                folder="video_streaming_site/thumbnails",
                resource_type="image"
            )
            thumbnail_url = thumbnail_result['secure_url']
        
        # Upload video
        video_result = cloudinary.uploader.upload(
            video_file,
            resource_type="video",
            folder="video_streaming_site/videos",
            context={
                "title": video_data.get('videoTitle', 'Untitled'),
                "description": video_data.get('videoDescription', ''),
                "category": video_data.get('videoCategory', 'General'),
                "uploadDate": datetime.now().isoformat(),
                "cloudinary_account": account.get('name', 'Unknown'),
                "cloudinary_cloud_name": account['cloud_name']
            }
        )
        
        video_metadata = {
            "id": video_result['public_id'],
            "title": video_data.get('videoTitle', 'Untitled'),
            "description": video_data.get('videoDescription', ''),
            "category": video_data.get('videoCategory', 'General'),
            "videoUrl": video_result['secure_url'],
            "thumbnail": thumbnail_url or generate_cloudinary_thumbnail(video_result['public_id'], account['cloud_name']),
            "uploadDate": datetime.now().isoformat(),
            "duration": video_result.get('duration', 0),
            "cloudinary_id": video_result['public_id'],
            "cloudinary_account": account.get('name', 'Unknown'),
            "cloudinary_cloud_name": account['cloud_name']
        }
        
        logger.info(f"✅ Video uploaded to {account.get('name')}: {video_metadata['id']}")
        
        return web.json_response({
            "success": True,
            "message": f"Video uploaded to {account.get('name')}",
            "video": video_metadata
        })
        
    except Exception as e:
        logger.error(f"❌ Upload error: {e}", exc_info=True)
        return web.json_response({"error": str(e)}, status=500)

async def get_videos_from_cloudinary(request):
    """Get all videos from all Cloudinary accounts"""
    
    if not CLOUDINARY_ENABLED:
        return web.json_response({"videos": []})
    
    try:
        import cloudinary
        import cloudinary.api
        
        all_videos = []
        accounts = get_active_accounts()
        account_stats = {}
        
        # Get videos from each account
        for account in accounts:
            try:
                configure_cloudinary(account)
                
                result = cloudinary.api.resources(
                    resource_type="video",
                    type="upload",
                    prefix="video_streaming_site/videos",
                    max_results=500,
                    context=True
                )
                
                account_name = account.get('name', 'Unknown')
                account_videos = 0
                
                for resource in result.get('resources', []):
                    context = resource.get('context', {}).get('custom', {})
                    
                    video_metadata = {
                        "id": resource['public_id'],
                        "title": context.get('title', 'Untitled'),
                        "description": context.get('description', ''),
                        "category": context.get('category', 'General'),
                        "videoUrl": resource['secure_url'],
                        "thumbnail": generate_cloudinary_thumbnail(resource['public_id'], account['cloud_name']),
                        "uploadDate": context.get('uploadDate', resource.get('created_at', '')),
                        "duration": resource.get('duration', 0),
                        "cloudinary_id": resource['public_id'],
                        "cloudinary_account": context.get('cloudinary_account', account_name),
                        "cloudinary_cloud_name": account['cloud_name']
                    }
                    
                    all_videos.append(video_metadata)
                    account_videos += 1
                
                account_stats[account_name] = account_videos
                logger.info(f"✅ Loaded {account_videos} videos from {account_name}")
                
            except Exception as e:
                logger.error(f"❌ Error loading from {account.get('name')}: {e}")
        
        # Sort by upload date (newest first)
        all_videos.sort(key=lambda x: x.get('uploadDate', ''), reverse=True)
        
        response_data = {
            "videos": all_videos,
            "statistics": {
                "total_videos": len(all_videos),
                "total_accounts": len(accounts),
                "videos_per_account": account_stats
            }
        }
        
        return web.json_response(response_data)
        
    except Exception as e:
        logger.error(f"❌ Error getting videos: {e}", exc_info=True)
        return web.json_response({"error": str(e)}, status=500)

async def delete_video_from_cloudinary(request):
    """Delete video from correct Cloudinary account"""
    
    if not CLOUDINARY_ENABLED:
        return web.json_response({"error": "Cloudinary not configured"}, status=503)
    
    try:
        import cloudinary
        import cloudinary.uploader
        import cloudinary.api
        
        data = await request.json()
        video_id = data.get('id')
        cloud_name = data.get('cloudinary_cloud_name')
        
        if not video_id:
            return web.json_response({"error": "No video ID provided"}, status=400)
        
        # Find and configure the correct account
        accounts = load_cloudinary_accounts()
        account = None
        
        if cloud_name:
            account = next((acc for acc in accounts if acc['cloud_name'] == cloud_name), None)
        
        if not account:
            # Fallback to first active account
            active = get_active_accounts()
            if active:
                account = active[0]
                logger.warning(f"⚠️ Cloud name not found, using {account.get('name')}")
        
        if not account:
            return web.json_response({"error": "No account found for deletion"}, status=404)
        
        configure_cloudinary(account)
        
        # Delete video
        cloudinary.uploader.destroy(video_id, resource_type="video")
        
        logger.info(f"✅ Video deleted from {account.get('name')}: {video_id}")
        
        return web.json_response({
            "success": True,
            "message": f"Video deleted from {account.get('name')}"
        })
        
    except Exception as e:
        logger.error(f"❌ Delete error: {e}", exc_info=True)
        return web.json_response({"error": str(e)}, status=500)

# ============================================================================
# ACCOUNT MANAGEMENT API
# ============================================================================

async def get_accounts_info(request):
    """Get information about all configured accounts"""
    try:
        accounts = load_cloudinary_accounts()
        active = get_active_accounts()
        
        safe_accounts = []
        for acc in accounts:
            safe_accounts.append({
                "name": acc.get('name', 'Unnamed'),
                "cloud_name": acc['cloud_name'],
                "active": acc.get('active', True)
            })
        
        return web.json_response({
            "accounts": safe_accounts,
            "total_accounts": len(accounts),
            "active_accounts": len(active)
        })
        
    except Exception as e:
        logger.error(f"Error getting accounts info: {e}")
        return web.json_response({"error": str(e)}, status=500)

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

async def get_app_info(request):
    `"`"`"Get APK file information for download`"`"`"
    try:
        apk_file = 'app.apk'
        
        if os.path.exists(apk_file):
            file_size = os.path.getsize(apk_file)
            return web.json_response({
                'apkUrl': '/download-app',
                'filename': 'PremiumApp.apk',
                'size': file_size,
                'available': True
            })
        else:
            return web.json_response({
                'available': False,
                'message': 'App not available'
            })
    except Exception as e:
        logger.error(f"Error getting app info: {e}")
        return web.json_response({'available': False, 'error': str(e)}, status=500)

async def download_app(request):
    `"`"`"Serve APK file for download`"`"`"
    try:
        apk_file = 'app.apk'
        
        if not os.path.exists(apk_file):
            return web.Response(status=404, text='App not found')
        
        with open(apk_file, 'rb') as f:
            content = f.read()
        
        return web.Response(
            body=content,
            content_type='application/vnd.android.package-archive',
            headers={
                'Content-Disposition': 'attachment; filename="PremiumApp.apk"'
            }
        )
    except Exception as e:
        logger.error(f"Error downloading app: {e}")
        return web.Response(status=500, text='Download failed')
async def health_check(request):
    """Health check endpoint"""
    accounts = get_active_accounts()
    status = "OK - Multi-Cloudinary + Telegram Bot Active"
    
    return web.Response(text=f"{status} ({len(accounts)} accounts)")

# ============================================================================
# STARTUP
# ============================================================================

async def set_telegram_webhook():
    """Set Telegram webhook on startup"""
    if not WEBHOOK_URL:
        logger.warning("⚠️ WEBHOOK_URL not set - bot will not work!")
        return
    
    import aiohttp
    webhook_url = f"{WEBHOOK_URL}/telegram-webhook"
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook"
    data = {"url": webhook_url}
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=data) as resp:
            result = await resp.json()
            if result.get('ok'):
                logger.info(f"✅ Telegram webhook set to: {webhook_url}")
            else:
                logger.error(f"❌ Failed to set webhook: {result}")

async def startup(app):
    """Run on startup"""
    initialize_files()
    await set_telegram_webhook()
    logger.info("=" * 70)
    logger.info("🛡️ BULLETPROOF SERVER + MULTI-CLOUDINARY + TELEGRAM BOT")
    logger.info("=" * 70)
    
    if CLOUDINARY_ENABLED:
        accounts = get_active_accounts()
        logger.info(f"✅ {len(accounts)} Cloudinary account(s) active")
        for acc in accounts:
            logger.info(f"   - {acc.get('name')}: {acc['cloud_name']}")
        logger.info("✅ Videos stored permanently in cloud")
        logger.info("✅ Automatic load balancing across accounts")
    else:
        logger.warning("⚠️ CLOUDINARY NOT CONFIGURED")
        logger.warning("⚠️ VIDEO UPLOADS DISABLED")
    
    logger.info("✅ Telegram bot: @pluseight_bot (webhook mode)")
    logger.info("=" * 70)

def main():
    print("=" * 70)
    print("🛡️ BULLETPROOF SERVER + MULTI-CLOUDINARY + TELEGRAM BOT")
    print("=" * 70)
    print(f"Port: {PORT}")
    print(f"Webhook URL: {WEBHOOK_URL}")
    print(f"Bot: @pluseight_bot")
    
    if CLOUDINARY_ENABLED:
        accounts = get_active_accounts()
        print(f"Cloudinary: ✅ {len(accounts)} account(s) configured")
        for acc in accounts:
            print(f"  - {acc.get('name')}: {acc['cloud_name']}")
        print("Video Storage: ✅ PERMANENT (multi-account)")
    else:
        print("Cloudinary: ❌ NOT CONFIGURED")
        print("Video Storage: ❌ DISABLED")
    
    print("=" * 70)
    
    app = web.Application(client_max_size=1024**3)  # 1GB max upload size
    
    # Bot webhook
    app.router.add_post('/telegram-webhook', handle_telegram_webhook)
    
    # Cloudinary video API routes
    app.router.add_post('/api/upload-video', upload_video_to_cloudinary)
    app.router.add_get('/api/videos', get_videos_from_cloudinary)
    app.router.add_post('/api/delete-video', delete_video_from_cloudinary)
    
    # Account management
    app.router.add_get('/api/cloudinary-accounts', get_accounts_info)

    # Visitor tracking API routes
    app.router.add_post('/api/visitor/connect', visitor_connect)
    app.router.add_post('/api/visitor/heartbeat', visitor_heartbeat)
    app.router.add_post('/api/visitor/disconnect', visitor_disconnect)
    app.router.add_get('/api/visitors/active', get_active_visitors)
    
    # APK download routes
    app.router.add_get('/api/get-app-info', get_app_info)
    app.router.add_get('/download-app', download_app)
        # Website routes
    app.router.add_get("/health", health_check)
    app.router.add_route('*', "/{path:.*}", serve_file)
    
    app.on_startup.append(startup)
    
    logger.info("🚀 Starting bulletproof server with multi-cloudinary and telegram bot...")
    web.run_app(app, host=HOST, port=PORT)

if __name__ == '__main__':
    main()


