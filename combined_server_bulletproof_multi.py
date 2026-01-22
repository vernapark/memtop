#!/usr/bin/env python3
"""
🛡️ BULLETPROOF COMBINED SERVER WITH MULTI-CLOUDINARY SUPPORT
- Supports multiple Cloudinary accounts for increased storage
- Backward compatible with single account setup
- Falls back to environment variables if no JSON file
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
# BULLETPROOF CLOUDINARY VIDEO HANDLERS (WITH MULTI-ACCOUNT SUPPORT)
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
            "thumbnail": thumbnail_url or video_result.get('thumbnail_url', ''),
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
                        "thumbnail": context.get('thumbnail', resource.get('thumbnail_url', '')),
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
        
        # Get video info to find thumbnail
        try:
            resource = cloudinary.api.resource(video_id, resource_type="video", context=True)
            context = resource.get('context', {}).get('custom', {})
            thumbnail_url = context.get('thumbnail', '')
            
            # Delete thumbnail if it's on Cloudinary
            if thumbnail_url and 'cloudinary.com' in thumbnail_url:
                try:
                    thumb_parts = thumbnail_url.split('/')
                    if len(thumb_parts) > 2:
                        thumb_public_id = '/'.join(thumb_parts[-2:]).split('.')[0]
                        cloudinary.uploader.destroy(thumb_public_id, resource_type="image")
                        logger.info(f"🗑️ Deleted thumbnail: {thumb_public_id}")
                except Exception as e:
                    logger.warning(f"Could not delete thumbnail: {e}")
        except Exception as e:
            logger.warning(f"Could not get video info: {e}")
        
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
# [REST OF YOUR EXISTING CODE - Telegram bot, key management, etc.]
# ============================================================================

def generate_key(length=32):
    characters = string.ascii_letters + string.digits
    return ''.join(secrets.choice(characters) for _ in range(length))

def load_key_storage():
    if os.path.exists(KEY_STORAGE_FILE):
        try:
            with open(KEY_STORAGE_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    return {"current_key": "", "created_at": "", "created_by": ""}

def save_key_storage(data):
    with open(KEY_STORAGE_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def load_access_codes():
    if os.path.exists(ACCESS_CODES_FILE):
        try:
            with open(ACCESS_CODES_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    return {"access_codes": []}

def save_access_codes(data):
    with open(ACCESS_CODES_FILE, 'w') as f:
        json.dump(data, f, indent=2)

# [... Keep all your existing telegram bot handlers ...]

async def handle_telegram_webhook(request):
    """Handle Telegram webhook"""
    try:
        from telegram import Update
        from telegram.ext import Application
        
        update_data = await request.json()
        logger.info(f"📨 Telegram webhook received")
        
        # Here you would process the telegram update
        # This is simplified - use your existing implementation
        
        return web.Response(text="OK")
    except Exception as e:
        logger.error(f"Telegram webhook error: {e}")
        return web.Response(status=500)

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
            return web.Response(status=404, text="Not Found")
        
        content_type = 'text/html'
        if file_path.endswith('.css'):
            content_type = 'text/css'
        elif file_path.endswith('.js'):
            content_type = 'application/javascript'
        elif file_path.endswith('.json'):
            content_type = 'application/json'
        
        with open(file_path, 'rb') as f:
            content = f.read()
        
        return web.Response(body=content, content_type=content_type)
        
    except Exception as e:
        logger.error(f"Error serving file: {e}")
        return web.Response(status=500, text="Internal Server Error")

async def health_check(request):
    """Health check endpoint"""
    accounts = get_active_accounts()
    status = "healthy" if CLOUDINARY_ENABLED else "cloudinary_not_configured"
    
    return web.json_response({
        "status": status,
        "cloudinary_accounts": len(accounts),
        "active_accounts": len(accounts)
    })

async def startup(app):
    """Startup tasks"""
    logger.info("=" * 70)
    logger.info("🚀 BULLETPROOF SERVER WITH MULTI-CLOUDINARY")
    logger.info("=" * 70)
    
    if CLOUDINARY_ENABLED:
        accounts = get_active_accounts()
        logger.info(f"✅ {len(accounts)} Cloudinary account(s) active")
        logger.info("✅ Videos stored permanently in cloud")
        logger.info("✅ Automatic load balancing across accounts")
        logger.info("✅ Survives all deployments and restarts")
    else:
        logger.warning("⚠️ CLOUDINARY NOT CONFIGURED")
        logger.warning("⚠️ VIDEO UPLOADS DISABLED")
    
    logger.info("=" * 70)

def main():
    print("=" * 70)
    print("🛡️ BULLETPROOF SERVER + MULTI-CLOUDINARY")
    print("=" * 70)
    print(f"Port: {PORT}")
    print(f"Webhook URL: {WEBHOOK_URL}")
    
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
    
    app = web.Application(client_max_size=1024**3)
    
    # Bot webhook
    app.router.add_post('/telegram-webhook', handle_telegram_webhook)
    
    # Cloudinary video API routes
    app.router.add_post('/api/upload-video', upload_video_to_cloudinary)
    app.router.add_get('/api/videos', get_videos_from_cloudinary)
    app.router.add_post('/api/delete-video', delete_video_from_cloudinary)
    
    # Account management
    app.router.add_get('/api/cloudinary-accounts', get_accounts_info)
    
    # Website routes
    app.router.add_get("/health", health_check)
    app.router.add_route('*', "/{path:.*}", serve_file)
    
    app.on_startup.append(startup)
    
    logger.info("🚀 Starting bulletproof server with multi-cloudinary...")
    web.run_app(app, host=HOST, port=PORT)

if __name__ == '__main__':
    main()
