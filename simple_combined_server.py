"""
Simple Combined Web Server + Telegram Bot for Render.com
Runs both the video streaming website and telegram bot in one process
WITHOUT Cloudinary dependency to ensure it always starts
FIXED VERSION with better error handling and logging
"""
import os
import json
import secrets
import string
import sys
import traceback
from datetime import datetime
from aiohttp import web
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Setup logging with more detail
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    stream=sys.stdout,
    force=True
)
logger = logging.getLogger(__name__)

# Configuration
PORT = int(os.getenv('PORT', 10000))
HOST = '0.0.0.0'
BOT_TOKEN = os.getenv("BOT_TOKEN", "8567043675:AAHB7CmPOfsWIHluLLk9hDF-8FBcN4LtOMM")
AUTHORIZED_CHAT_ID = int(os.getenv("AUTHORIZED_CHAT_ID", "2103408372"))
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "https://memtop-video-streaming.onrender.com")
WEBHOOK_PATH = "/telegram-webhook"
KEY_STORAGE_FILE = "key_storage.json"
ACCESS_CODES_FILE = "access_codes.json"

# Store application globally
telegram_app = None

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
# TELEGRAM BOT COMMANDS
# ============================================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    chat_id = update.effective_chat.id
    
    if chat_id != AUTHORIZED_CHAT_ID:
        await update.message.reply_text("❌ Unauthorized access.")
        return
    
    message = (
        "👑 *Admin Key Manager Bot*\n\n"
        "🔐 *Admin Key Commands:*\n"
        "/createkey - Generate new admin access key\n"
        "/currentkey - View current admin key\n\n"
        "🎫 *User Access Code Commands:*\n"
        "/generatecode - Generate user access code\n"
        "/listcodes - View all active access codes\n"
        "/revokecode - Remove an access code\n\n"
        "/help - Show detailed help"
    )
    await update.message.reply_text(message, parse_mode='Markdown')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    chat_id = update.effective_chat.id
    
    if chat_id != AUTHORIZED_CHAT_ID:
        await update.message.reply_text("❌ Unauthorized access.")
        return
    
    message = (
        "📚 *Complete Help Guide*\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "🔐 *ADMIN KEY MANAGEMENT*\n\n"
        "*What is the Admin Key?*\n"
        "The admin key is used to access the admin panel at:\n"
        "`/parking55009hvSweJimbs5hhinbd56y`\n\n"
        "*How to use:*\n"
        "1. Use `/generatecode` to create user access code\n"
        "2. Copy the generated code\n"
        "3. Share it with users\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "🎫 *USER ACCESS CODES*\n\n"
        "*What are Access Codes?*\n"
        "Access codes allow users to enter the website.\n\n"
        "*Features:*\n"
        "• Each access code is unique\n"
        "• You can generate multiple access codes\n"
        "• Codes can be revoked anytime\n"
        "• All codes are stored securely\n\n"
        "*Commands:*\n"
        "• `/generatecode` - Create new access code\n"
        "• `/listcodes` - See all active codes\n"
        "• `/revokecode <code>` - Delete a code\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "Need more help? Just ask! 😊"
    )
    await update.message.reply_text(message, parse_mode='Markdown')

async def create_key(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /createkey command"""
    chat_id = update.effective_chat.id
    
    if chat_id != AUTHORIZED_CHAT_ID:
        await update.message.reply_text("❌ Unauthorized access.")
        return
    
    new_key = generate_key()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    username = update.effective_user.username or "Unknown"
    
    key_data = {
        "current_key": new_key,
        "created_at": timestamp,
        "created_by": username
    }
    save_key_storage(key_data)
    
    message = (
        "✅ *New Admin Key Generated!*\n\n"
        f"🔑 `{new_key}`\n\n"
        f"🕒 Created: {timestamp}\n"
        f"👤 By: @{username}\n\n"
        "*How to use:*\n"
        "1. Copy the key above\n"
        "2. Go to: `/parking55009hvSweJimbs5hhinbd56y`\n"
        "3. Paste the key to access admin panel\n\n"
        "⚠️ Keep this key secure!"
    )
    await update.message.reply_text(message, parse_mode='Markdown')

async def current_key(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /currentkey command"""
    chat_id = update.effective_chat.id
    
    if chat_id != AUTHORIZED_CHAT_ID:
        await update.message.reply_text("❌ Unauthorized access.")
        return
    
    key_data = load_key_storage()
    
    if not key_data.get('current_key'):
        await update.message.reply_text(
            "ℹ️ No admin key exists yet.\n\n"
            "Use /createkey to generate one.",
            parse_mode='Markdown'
        )
        return
    
    message = (
        "🔐 *Current Admin Key*\n\n"
        f"🔑 `{key_data['current_key']}`\n\n"
        f"🕒 Created: {key_data.get('created_at', 'Unknown')}\n"
        f"👤 By: @{key_data.get('created_by', 'Unknown')}\n\n"
        "Use /createkey to generate a new key."
    )
    await update.message.reply_text(message, parse_mode='Markdown')

async def generate_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /generatecode command"""
    chat_id = update.effective_chat.id
    
    if chat_id != AUTHORIZED_CHAT_ID:
        await update.message.reply_text("❌ Unauthorized access.")
        return
    
    new_code = generate_key(16)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    codes_data = load_access_codes()
    codes_data['access_codes'].append(new_code)
    save_access_codes(codes_data)
    
    message = (
        "✅ *User Access Code Generated!*\n\n"
        f"🎫 `{new_code}`\n\n"
        f"🕒 Created: {timestamp}\n"
        f"📊 Total Active Codes: {len(codes_data['access_codes'])}\n\n"
        "*How to use:*\n"
        "1. Copy the code above\n"
        "2. Share with users who need access\n"
        "3. Users enter this code on the website\n\n"
        "💡 Use /listcodes to see all codes\n"
        "💡 Use /revokecode to remove a code"
    )
    await update.message.reply_text(message, parse_mode='Markdown')

async def list_codes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /listcodes command"""
    chat_id = update.effective_chat.id
    
    if chat_id != AUTHORIZED_CHAT_ID:
        await update.message.reply_text("❌ Unauthorized access.")
        return
    
    codes_data = load_access_codes()
    codes = codes_data.get('access_codes', [])
    
    if not codes:
        await update.message.reply_text(
            "ℹ️ No active access codes.\n\n"
            "Use /generatecode to create the first code."
        )
        return
    
    message = f"🎫 *Active Access Codes* ({len(codes)})\n\n"
    for i, code in enumerate(codes, 1):
        message += f"{i}. `{code}`\n"
    
    message += f"\n💡 Total: {len(codes)} code(s)\n"
    message += "💡 Use /revokecode <code> to remove"
    
    await update.message.reply_text(message, parse_mode='Markdown')

async def revoke_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /revokecode command"""
    chat_id = update.effective_chat.id
    
    if chat_id != AUTHORIZED_CHAT_ID:
        await update.message.reply_text("❌ Unauthorized access.")
        return
    
    if not context.args:
        await update.message.reply_text(
            "⚠️ *Usage:* `/revokecode <code>`\n\n"
            "*Example:*\n"
            "`/revokecode abc123xyz456`\n\n"
            "Use /listcodes to see all codes.",
            parse_mode='Markdown'
        )
        return
    
    code_to_revoke = context.args[0]
    
    codes_data = load_access_codes()
    codes = codes_data.get('access_codes', [])
    
    if code_to_revoke in codes:
        codes.remove(code_to_revoke)
        codes_data['access_codes'] = codes
        save_access_codes(codes_data)
        
        await update.message.reply_text(
            f"✅ Access code revoked!\n\n"
            f"🗑️ Removed: `{code_to_revoke}`\n"
            f"📊 Remaining Codes: {len(codes)}\n\n"
            "This code will no longer grant access to the website.",
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            f"❌ Code not found: `{code_to_revoke}`\n\n"
            "Use /listcodes to see all active codes.",
            parse_mode='Markdown'
        )

# ============================================================================
# WEB SERVER HANDLERS
# ============================================================================

async def webhook_handler(request):
    """Handle Telegram webhook updates"""
    global telegram_app
    
    if request.method != 'POST':
        logger.warning(f"Webhook received non-POST request: {request.method}")
        return web.Response(status=405, text="Method Not Allowed")
    
    try:
        logger.info(f"📨 Received webhook request from {request.remote}")
        data = await request.json()
        logger.info(f"📦 Webhook data: {json.dumps(data, indent=2)}")
        
        update = Update.de_json(data, telegram_app.bot)
        await telegram_app.update_queue.put(update)
        
        logger.info("✅ Update queued successfully")
        return web.Response(status=200, text="OK")
    except Exception as e:
        logger.error(f"❌ Webhook error: {e}", exc_info=True)
        return web.Response(status=500, text="Internal Server Error")

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
    return web.Response(text="OK - Bot & Web Server Running", status=200)

# ============================================================================
# MAIN APPLICATION
# ============================================================================

async def main():
    """Start the combined server"""
    global telegram_app
    
    try:
        print("=" * 70, flush=True)
        print("🚀 Starting Combined Web Server + Telegram Bot", flush=True)
        print("=" * 70, flush=True)
        print(f"Python version: {sys.version}", flush=True)
        print(f"PORT: {PORT}", flush=True)
        print(f"HOST: {HOST}", flush=True)
        print(f"WEBHOOK_URL: {WEBHOOK_URL}", flush=True)
        print("=" * 70, flush=True)
        
        # Initialize storage files
        logger.info("Initializing storage files...")
        initialize_files()
        logger.info("✅ Storage files initialized")
        
        # Create Telegram bot application
        logger.info("Creating Telegram bot application...")
        telegram_app = (
            Application.builder()
            .token(BOT_TOKEN)
            .updater(None)  # Required for manual webhook handling
            .build()
        )
        logger.info("✅ Telegram bot application created")
        
        # Register bot commands
        logger.info("Registering bot commands...")
        telegram_app.add_handler(CommandHandler("start", start))
        telegram_app.add_handler(CommandHandler("help", help_command))
        telegram_app.add_handler(CommandHandler("createkey", create_key))
        telegram_app.add_handler(CommandHandler("currentkey", current_key))
        telegram_app.add_handler(CommandHandler("generatecode", generate_code))
        telegram_app.add_handler(CommandHandler("listcodes", list_codes))
        telegram_app.add_handler(CommandHandler("revokecode", revoke_code))
        logger.info("✅ Bot commands registered")
        
        # Initialize bot
        logger.info("Initializing bot...")
        await telegram_app.initialize()
        logger.info("✅ Bot initialized")
        
        logger.info("Starting bot...")
        await telegram_app.start()
        logger.info("✅ Bot started")
        
        # Set webhook
        webhook_url = f"{WEBHOOK_URL}{WEBHOOK_PATH}"
        logger.info(f"Setting webhook to: {webhook_url}")
        await telegram_app.bot.set_webhook(url=webhook_url)
        logger.info(f"✅ Webhook set to: {webhook_url}")
        
        # Create web application
        logger.info("Creating web application...")
        app = web.Application()
        
        # Add routes
        app.router.add_route('*', WEBHOOK_PATH, webhook_handler)
        app.router.add_get("/health", health_check)
        app.router.add_route('*', "/{path:.*}", serve_file)
        
        logger.info("📍 Routes registered:")
        logger.info(f"   * {WEBHOOK_PATH} -> webhook_handler")
        logger.info(f"   GET /health -> health_check")
        logger.info(f"   * /{{path:.*}} -> serve_file")
        
        # Start web server
        logger.info(f"Starting web server on {HOST}:{PORT}...")
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, HOST, PORT)
        await site.start()
        
        print("=" * 70, flush=True)
        print("✅ Server is running!", flush=True)
        print(f"🌐 Website: {WEBHOOK_URL}", flush=True)
        print(f"🤖 Telegram Bot: Active with webhook", flush=True)
        print("=" * 70, flush=True)
        logger.info("✅ All systems operational")
        
        # Keep running
        import asyncio
        logger.info("Entering main event loop...")
        await asyncio.Event().wait()
        
    except Exception as e:
        logger.error(f"❌ FATAL ERROR in main(): {e}", exc_info=True)
        print(f"\n❌ FATAL ERROR: {e}", file=sys.stderr, flush=True)
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
        traceback.print_exc()
        sys.exit(1)
