#!/usr/bin/env python3
"""
🛡️ ULTIMATE BULLETPROOF SERVER with PostgreSQL Database
- Videos stored in Cloudinary (permanent cloud storage)
- Metadata stored in PostgreSQL DATABASE (permanent, survives all deployments)
- No local files = No data loss EVER
- Works on Render's free tier (PostgreSQL + Cloudinary both free)
"""
import os
import json
import secrets
import string
import sys
from datetime import datetime
from aiohttp import web
import logging
import asyncpg
from typing import Optional

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

# Configuration
PORT = int(os.getenv('PORT', 10000))
HOST = '0.0.0.0'
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
AUTHORIZED_CHAT_ID = int(os.getenv("AUTHORIZED_CHAT_ID", "0"))
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "")

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "")

# Cloudinary config
CLOUDINARY_CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME", "")
CLOUDINARY_API_KEY = os.getenv("CLOUDINARY_API_KEY", "")
CLOUDINARY_API_SECRET = os.getenv("CLOUDINARY_API_SECRET", "")

# Global database connection pool
db_pool: Optional[asyncpg.Pool] = None

# ============================================================================
# DATABASE SETUP
# ============================================================================

async def init_database():
    """Initialize PostgreSQL database and create tables"""
    global db_pool
    
    if not DATABASE_URL:
        logger.error("=" * 70)
        logger.error("❌ DATABASE_URL not set!")
        logger.error("Videos will NOT persist across deployments!")
        logger.error("Add a PostgreSQL database in Render dashboard")
        logger.error("=" * 70)
        return False
    
    try:
        # Create connection pool
        db_pool = await asyncpg.create_pool(DATABASE_URL, min_size=1, max_size=10)
        logger.info("✅ Connected to PostgreSQL database")
        
        # Create videos table
        async with db_pool.acquire() as conn:
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS videos (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    description TEXT,
                    category TEXT NOT NULL,
                    video_url TEXT NOT NULL,
                    thumbnail_url TEXT NOT NULL,
                    upload_date TIMESTAMP NOT NULL DEFAULT NOW(),
                    duration REAL,
                    cloudinary_id TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            ''')
            
            # Create access keys table
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS admin_keys (
                    id SERIAL PRIMARY KEY,
                    key_value TEXT NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    created_by TEXT
                )
            ''')
            
            # Create access codes table
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS access_codes (
                    id SERIAL PRIMARY KEY,
                    code TEXT UNIQUE NOT NULL,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            ''')
            
            logger.info("✅ Database tables ready")
        
        return True
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        return False

# ============================================================================
# VIDEO CRUD OPERATIONS (Database + Cloudinary)
# ============================================================================

async def save_video_to_db(video_data: dict):
    """Save video metadata to PostgreSQL database"""
    async with db_pool.acquire() as conn:
        await conn.execute('''
            INSERT INTO videos (id, title, description, category, video_url, thumbnail_url, upload_date, duration, cloudinary_id)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
            ON CONFLICT (id) DO UPDATE SET
                title = EXCLUDED.title,
                description = EXCLUDED.description,
                category = EXCLUDED.category,
                video_url = EXCLUDED.video_url,
                thumbnail_url = EXCLUDED.thumbnail_url
        ''', 
            video_data['id'],
            video_data['title'],
            video_data['description'],
            video_data['category'],
            video_data['videoUrl'],
            video_data['thumbnail'],
            datetime.fromisoformat(video_data['uploadDate']),
            video_data.get('duration', 0),
            video_data['cloudinary_id']
        )

async def get_videos_from_db():
    """Fetch all videos from PostgreSQL database"""
    async with db_pool.acquire() as conn:
        rows = await conn.fetch('SELECT * FROM videos ORDER BY upload_date DESC')
        videos = []
        for row in rows:
            videos.append({
                'id': row['id'],
                'title': row['title'],
                'description': row['description'],
                'category': row['category'],
                'videoUrl': row['video_url'],
                'thumbnail': row['thumbnail_url'],
                'uploadDate': row['upload_date'].isoformat(),
                'duration': row['duration'],
                'cloudinary_id': row['cloudinary_id']
            })
        return videos

async def delete_video_from_db(video_id: str):
    """Delete video metadata from PostgreSQL database"""
    async with db_pool.acquire() as conn:
        await conn.execute('DELETE FROM videos WHERE id = $1', video_id)

# ============================================================================
# CLOUDINARY VIDEO HANDLERS
# ============================================================================

async def upload_video_to_cloudinary(request):
    """Upload video to Cloudinary + save metadata to database"""
    
    if not CLOUDINARY_CLOUD_NAME or not CLOUDINARY_API_KEY or not CLOUDINARY_API_SECRET:
        return web.json_response({
            "error": "Cloudinary not configured. Set CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET in Render"
        }, status=503)
    
    if not db_pool:
        return web.json_response({
            "error": "Database not configured. Add PostgreSQL database in Render"
        }, status=503)
    
    try:
        import cloudinary
        import cloudinary.uploader
        
        cloudinary.config(
            cloud_name=CLOUDINARY_CLOUD_NAME,
            api_key=CLOUDINARY_API_KEY,
            api_secret=CLOUDINARY_API_SECRET
        )
        
        data = await request.json()
        video_data = data.get('videoData')
        thumbnail_data = data.get('thumbnailData')
        title = data.get('title', 'Untitled')
        description = data.get('description', '')
        category = data.get('category', 'uncategorized')
        
        logger.info(f"🎬 Uploading video: {title}")
        
        # Upload thumbnail
        thumbnail_result = cloudinary.uploader.upload(
            thumbnail_data,
            resource_type="image",
            folder="memtop_videos/thumbnails",
            public_id=f"thumb_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        )
        
        logger.info(f"✅ Thumbnail uploaded")
        
        # Upload video
        video_result = cloudinary.uploader.upload(
            video_data,
            resource_type="video",
            folder="memtop_videos/videos",
            public_id=f"video_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        )
        
        logger.info(f"✅ Video uploaded to Cloudinary")
        
        # Save metadata to DATABASE
        video_metadata = {
            "id": video_result['public_id'],
            "title": title,
            "description": description,
            "category": category,
            "videoUrl": video_result['secure_url'],
            "thumbnail": thumbnail_result['secure_url'],
            "uploadDate": datetime.now().isoformat(),
            "duration": video_result.get('duration', 0),
            "cloudinary_id": video_result['public_id']
        }
        
        await save_video_to_db(video_metadata)
        logger.info(f"✅ Video metadata saved to DATABASE")
        
        return web.json_response({
            "success": True,
            "message": "Video uploaded to permanent storage (Cloudinary + Database)",
            "video": video_metadata
        })
        
    except Exception as e:
        logger.error(f"❌ Upload error: {e}", exc_info=True)
        return web.json_response({"error": str(e)}, status=500)

async def get_videos_handler(request):
    """Fetch all videos from DATABASE"""
    
    if not db_pool:
        return web.json_response({"videos": []})
    
    try:
        videos = await get_videos_from_db()
        logger.info(f"📥 Fetched {len(videos)} videos from DATABASE")
        return web.json_response({"videos": videos})
    except Exception as e:
        logger.error(f"❌ Error fetching videos: {e}", exc_info=True)
        return web.json_response({"videos": []})

async def delete_video_handler(request):
    """Delete video from Cloudinary + DATABASE"""
    
    if not CLOUDINARY_CLOUD_NAME or not db_pool:
        return web.json_response({"error": "Service not available"}, status=503)
    
    try:
        import cloudinary
        import cloudinary.uploader
        
        cloudinary.config(
            cloud_name=CLOUDINARY_CLOUD_NAME,
            api_key=CLOUDINARY_API_KEY,
            api_secret=CLOUDINARY_API_SECRET
        )
        
        data = await request.json()
        video_id = data.get('id')
        
        if not video_id:
            return web.json_response({"error": "No video ID"}, status=400)
        
        logger.info(f"🗑️ Deleting video: {video_id}")
        
        # Delete from Cloudinary
        try:
            cloudinary.uploader.destroy(video_id, resource_type="video")
            logger.info(f"✅ Deleted from Cloudinary")
        except Exception as e:
            logger.warning(f"⚠️ Cloudinary delete failed: {e}")
        
        # Delete from database
        await delete_video_from_db(video_id)
        logger.info(f"✅ Deleted from DATABASE")
        
        return web.json_response({
            "success": True,
            "message": "Video deleted from permanent storage"
        })
        
    except Exception as e:
        logger.error(f"❌ Delete error: {e}", exc_info=True)
        return web.json_response({"error": str(e)}, status=500)

# ============================================================================
# ADMIN KEY & ACCESS CODE FUNCTIONS (Database)
# ============================================================================

async def get_current_admin_key():
    """Get the most recent admin key from database"""
    async with db_pool.acquire() as conn:
        row = await conn.fetchrow('SELECT key_value, created_at, created_by FROM admin_keys ORDER BY id DESC LIMIT 1')
        if row:
            return {
                'current_key': row['key_value'],
                'created_at': row['created_at'].strftime("%Y-%m-%d %H:%M:%S"),
                'created_by': row['created_by']
            }
        return None

async def save_admin_key(key: str, created_by: str):
    """Save new admin key to database"""
    async with db_pool.acquire() as conn:
        await conn.execute(
            'INSERT INTO admin_keys (key_value, created_at, created_by) VALUES ($1, $2, $3)',
            key, datetime.now(), created_by
        )

async def get_access_codes():
    """Get all access codes from database"""
    async with db_pool.acquire() as conn:
        rows = await conn.fetch('SELECT code FROM access_codes ORDER BY created_at DESC')
        return [row['code'] for row in rows]

async def add_access_code(code: str):
    """Add access code to database"""
    async with db_pool.acquire() as conn:
        await conn.execute('INSERT INTO access_codes (code) VALUES ($1)', code)

async def remove_access_code(code: str):
    """Remove access code from database"""
    async with db_pool.acquire() as conn:
        result = await conn.execute('DELETE FROM access_codes WHERE code = $1', code)
        return result != 'DELETE 0'

# ============================================================================
# TELEGRAM BOT HANDLERS
# ============================================================================

def generate_key(length=32):
    characters = string.ascii_letters + string.digits
    return ''.join(secrets.choice(characters) for _ in range(length))

async def send_message(chat_id, text):
    """Send message to Telegram"""
    import aiohttp
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": chat_id, "text": text}
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=data) as resp:
            return await resp.json()

async def handle_telegram_webhook(request):
    """Handle Telegram bot commands"""
    try:
        update = await request.json()
        
        if 'message' not in update:
            return web.Response(text="OK")
        
        message = update['message']
        chat_id = message['chat']['id']
        text = message.get('text', '')
        username = message['from'].get('username', 'Unknown')
        
        if AUTHORIZED_CHAT_ID and chat_id != AUTHORIZED_CHAT_ID:
            await send_message(chat_id, "Unauthorized access.")
            return web.Response(text="OK")
        
        if not db_pool:
            await send_message(chat_id, "❌ Database not configured")
            return web.Response(text="OK")
        
        # Handle commands
        if text == '/start':
            response = (
                "🤖 Admin Bot - Database Version\n\n"
                "Commands:\n"
                "/createkey - Generate admin key\n"
                "/currentkey - View current key\n"
                "/generatecode - Create access code\n"
                "/listcodes - View all codes\n"
                "/revokecode <code> - Remove code"
            )
            await send_message(chat_id, response)
        
        elif text == '/createkey':
            new_key = generate_key()
            await save_admin_key(new_key, username)
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            response = f"🔑 New Admin Key\n\nKey: {new_key}\n\nCreated: {timestamp}\nBy: @{username}"
            await send_message(chat_id, response)
        
        elif text == '/currentkey':
            key_data = await get_current_admin_key()
            if not key_data:
                await send_message(chat_id, "❌ No admin key exists.\nUse /createkey")
            else:
                response = f"🔑 Current Admin Key\n\nKey: {key_data['current_key']}\n\nCreated: {key_data['created_at']}\nBy: @{key_data['created_by']}"
                await send_message(chat_id, response)
        
        elif text == '/generatecode':
            new_code = generate_key(16)
            await add_access_code(new_code)
            codes = await get_access_codes()
            response = f"🎟️ Access Code Generated\n\nCode: {new_code}\n\nTotal Active: {len(codes)}"
            await send_message(chat_id, response)
        
        elif text == '/listcodes':
            codes = await get_access_codes()
            if not codes:
                await send_message(chat_id, "❌ No access codes.\nUse /generatecode")
            else:
                response = f"🎟️ Active Codes ({len(codes)})\n\n"
                for i, code in enumerate(codes, 1):
                    response += f"{i}. {code}\n"
                await send_message(chat_id, response)
        
        elif text.startswith('/revokecode'):
            parts = text.split()
            if len(parts) < 2:
                await send_message(chat_id, "Usage: /revokecode <code>")
            else:
                code = parts[1]
                success = await remove_access_code(code)
                if success:
                    codes = await get_access_codes()
                    await send_message(chat_id, f"✅ Code revoked\nRemaining: {len(codes)}")
                else:
                    await send_message(chat_id, f"❌ Code not found")
        
        return web.Response(text="OK")
        
    except Exception as e:
        logger.error(f"Telegram error: {e}", exc_info=True)
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
        
        file_path = path.lstrip('/')
        
        if '..' in file_path or not os.path.exists(file_path):
            return web.Response(status=404, text="Not Found")
        
        content_types = {
            '.html': 'text/html',
            '.css': 'text/css',
            '.js': 'application/javascript',
            '.json': 'application/json',
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.mp4': 'video/mp4'
        }
        
        ext = os.path.splitext(file_path)[1]
        content_type = content_types.get(ext, 'application/octet-stream')
        
        with open(file_path, 'rb') as f:
            return web.Response(body=f.read(), content_type=content_type)
    
    except Exception as e:
        logger.error(f"Error serving {request.path}: {e}")
        return web.Response(status=500)

async def health_check(request):
    """Health check"""
    db_status = "✅" if db_pool else "❌"
    cloudinary_status = "✅" if CLOUDINARY_CLOUD_NAME else "❌"
    return web.Response(text=f"OK - DB:{db_status} Cloudinary:{cloudinary_status}")

# ============================================================================
# STARTUP
# ============================================================================

async def set_telegram_webhook():
    """Set webhook"""
    if not WEBHOOK_URL or not BOT_TOKEN:
        return
    
    import aiohttp
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook"
    data = {"url": f"{WEBHOOK_URL}/telegram-webhook"}
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=data) as resp:
            result = await resp.json()
            if result.get('ok'):
                logger.info(f"✅ Webhook set")

async def startup(app):
    """Startup"""
    db_ok = await init_database()
    await set_telegram_webhook()
    
    logger.info("=" * 70)
    logger.info("🛡️ ULTIMATE BULLETPROOF SERVER")
    logger.info(f"Database: {'✅ Connected' if db_ok else '❌ Not configured'}")
    logger.info(f"Cloudinary: {'✅ Ready' if CLOUDINARY_CLOUD_NAME else '❌ Not configured'}")
    logger.info("=" * 70)

async def cleanup(app):
    """Cleanup on shutdown"""
    if db_pool:
        await db_pool.close()
        logger.info("✅ Database connections closed")

def main():
    print("=" * 70)
    print("🛡️ ULTIMATE BULLETPROOF SERVER with DATABASE")
    print("=" * 70)
    print(f"Port: {PORT}")
    print(f"Database: {'✅' if DATABASE_URL else '❌ NOT SET'}")
    print(f"Cloudinary: {'✅' if CLOUDINARY_CLOUD_NAME else '❌ NOT SET'}")
    print("=" * 70)
    
    app = web.Application(client_max_size=1024**3)
    
    # Routes
    app.router.add_post('/telegram-webhook', handle_telegram_webhook)
    app.router.add_post('/api/upload-video', upload_video_to_cloudinary)
    app.router.add_get('/api/videos', get_videos_handler)
    app.router.add_post('/api/delete-video', delete_video_handler)
    app.router.add_get("/health", health_check)
    app.router.add_route('*', "/{path:.*}", serve_file)
    
    app.on_startup.append(startup)
    app.on_cleanup.append(cleanup)
    
    web.run_app(app, host=HOST, port=PORT)

if __name__ == '__main__':
    main()
