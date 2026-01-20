#!/usr/bin/env python3
"""
Telegram Bot with Webhook Support for Render.com
Manages admin keys and user access codes
"""
import os
import json
import secrets
import string
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from aiohttp import web
import logging

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Configuration from environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN", "8567043675:AAHB7CmPOfsWIHluLLk9hDF-8FBcN4LtOMM")
AUTHORIZED_CHAT_ID = int(os.getenv("AUTHORIZED_CHAT_ID", "2103408372"))
KEY_STORAGE_FILE = os.getenv("KEY_STORAGE_FILE", "key_storage.json")
ACCESS_CODES_FILE = "access_codes.json"

# Webhook configuration
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "https://memtop.onrender.com")
WEBHOOK_PATH = "/telegram-webhook"
WEBHOOK_PORT = int(os.getenv("PORT", 10000))

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
        except:
            pass
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
        except:
            pass
    return {"access_codes": []}

def save_access_codes(data):
    """Save access codes to storage"""
    with open(ACCESS_CODES_FILE, 'w') as f:
        json.dump(data, f, indent=2)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    chat_id = update.effective_chat.id
    
    if chat_id != AUTHORIZED_CHAT_ID:
        await update.message.reply_text(
            "❌ Unauthorized access.\n"
            "This bot is private and only accessible to authorized users."
        )
        return
    
    message = (
        "🔐 *Admin Key Manager Bot*\n\n"
        "Welcome! This bot manages access for your video streaming website.\n\n"
        "*Admin Commands:*\n"
        "/start - Show this welcome message\n"
        "/help - Get detailed instructions\n"
        "/createkey - Generate admin access key\n"
        "/currentkey - View current admin key\n\n"
        "*User Access Commands:*\n"
        "/generatecode - Generate user access code\n"
        "/listcodes - View all active access codes\n"
        "/revokecode - Remove an access code\n\n"
        "⚠️ *Security Note:*\n"
        "Creating a new admin key will invalidate the old one."
    )
    
    await update.message.reply_text(message, parse_mode='Markdown')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    chat_id = update.effective_chat.id
    
    if chat_id != AUTHORIZED_CHAT_ID:
        await update.message.reply_text("❌ Unauthorized access.")
        return
    
    message = (
        "📖 *How to Use This Bot*\n\n"
        "*For Admin Panel Access:*\n"
        "1. Use `/createkey` to generate admin access key\n"
        "2. Copy the key\n"
        "3. Login at: /parking55009hvSweJimbs5hhinbd56y\n\n"
        "*For User Homepage Access:*\n"
        "1. Use `/generatecode` to create user access code\n"
        "2. Share the code with users\n"
        "3. Users enter code on homepage to access videos\n"
        "4. Use `/listcodes` to see all active codes\n"
        "5. Use `/revokecode` to disable a code\n\n"
        "*Important Notes:*\n"
        "• Admin keys are for dashboard access only\n"
        "• Access codes are for homepage video viewing\n"
        "• Each access code is unique\n"
        "• You can generate multiple access codes\n"
        "• Codes remain valid until revoked"
    )
    
    await update.message.reply_text(message, parse_mode='Markdown')

async def create_key(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /createkey command"""
    chat_id = update.effective_chat.id
    
    if chat_id != AUTHORIZED_CHAT_ID:
        await update.message.reply_text("❌ Unauthorized access.")
        return
    
    # Generate new key
    new_key = generate_key(32)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Load current storage
    storage = load_key_storage()
    old_key_exists = bool(storage.get("current_key"))
    
    # Save new key
    storage = {
        "current_key": new_key,
        "created_at": timestamp,
        "created_by": "Telegram Bot"
    }
    save_key_storage(storage)
    
    # Send response
    message = (
        "✅ *New Admin Access Key Generated!*\n\n"
        f"🔑 `{new_key}`\n\n"
        f"🕒 Created: {timestamp}\n\n"
    )
    
    if old_key_exists:
        message += "⚠️ *Previous admin key has been invalidated.*\n\n"
    
    message += (
        "*Next Steps:*\n"
        "1. Copy the key above\n"
        "2. Go to admin panel\n"
        "3. Paste and login\n\n"
        "💡 Use /currentkey anytime to view this key again."
    )
    
    await update.message.reply_text(message, parse_mode='Markdown')

async def current_key(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /currentkey command"""
    chat_id = update.effective_chat.id
    
    if chat_id != AUTHORIZED_CHAT_ID:
        await update.message.reply_text("❌ Unauthorized access.")
        return
    
    storage = load_key_storage()
    
    if not storage.get("current_key"):
        await update.message.reply_text(
            "ℹ️ No active admin key found.\n\n"
            "Use /createkey to generate your first access key."
        )
        return
    
    message = (
        "🔑 *Current Admin Access Key*\n\n"
        f"`{storage['current_key']}`\n\n"
        f"🕒 Created: {storage.get('created_at', 'Unknown')}\n\n"
        "💡 Use /createkey to generate a new one."
    )
    
    await update.message.reply_text(message, parse_mode='Markdown')

async def generate_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /generatecode command - Generate user access code"""
    chat_id = update.effective_chat.id
    
    if chat_id != AUTHORIZED_CHAT_ID:
        await update.message.reply_text("❌ Unauthorized access.")
        return
    
    # Generate new access code
    new_code = generate_key(16)  # Shorter code for users
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Load and update access codes
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
        "3. Users enter this code on the homepage\n"
        "4. Code grants access to view all videos\n\n"
        "💡 Use /listcodes to see all active codes\n"
        "🗑️ Use /revokecode to disable a specific code"
    )
    
    await update.message.reply_text(message, parse_mode='Markdown')

async def list_codes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /listcodes command - List all active access codes"""
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
    
    message = f"📋 *Active Access Codes* ({len(codes)})\n\n"
    for i, code in enumerate(codes, 1):
        message += f"{i}. `{code}`\n"
    
    message += "\n💡 Use /revokecode <code> to disable a code"
    
    await update.message.reply_text(message, parse_mode='Markdown')

async def revoke_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /revokecode command - Remove an access code"""
    chat_id = update.effective_chat.id
    
    if chat_id != AUTHORIZED_CHAT_ID:
        await update.message.reply_text("❌ Unauthorized access.")
        return
    
    # Get the code to revoke from command args
    if not context.args:
        await update.message.reply_text(
            "❌ Please provide a code to revoke.\n\n"
            "Usage: /revokecode <code>\n"
            "Example: /revokecode abc123xyz\n\n"
            "Use /listcodes to see all active codes."
        )
        return
    
    code_to_revoke = context.args[0]
    
    # Load and update access codes
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

async def health_check(request):
    """Health check endpoint"""
    return web.Response(text="Bot is running!")

async def main():
    """Start the bot with webhook"""
    print("=" * 60)
    print("🤖 Admin Key Manager Bot Starting (Webhook Mode)...")
    print(f"📱 Authorized Chat ID: {AUTHORIZED_CHAT_ID}")
    print(f"💾 Admin Key Storage: {KEY_STORAGE_FILE}")
    print(f"🎫 Access Codes Storage: {ACCESS_CODES_FILE}")
    print(f"🌐 Webhook URL: {WEBHOOK_URL}{WEBHOOK_PATH}")
    print(f"🔌 Port: {WEBHOOK_PORT}")
    print("=" * 60)
    
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("createkey", create_key))
    application.add_handler(CommandHandler("currentkey", current_key))
    application.add_handler(CommandHandler("generatecode", generate_code))
    application.add_handler(CommandHandler("listcodes", list_codes))
    application.add_handler(CommandHandler("revokecode", revoke_code))
    
    # Initialize application
    await application.initialize()
    await application.start()
    
    # Set webhook
    webhook_url = f"{WEBHOOK_URL}{WEBHOOK_PATH}"
    await application.bot.set_webhook(url=webhook_url)
    logger.info(f"Webhook set to: {webhook_url}")
    
    # Create web app for webhook
    app = web.Application()
    app.router.add_post(WEBHOOK_PATH, lambda req: application.update_queue.put(
        Update.de_json(data=await req.json(), bot=application.bot)
    ) or web.Response())
    app.router.add_get("/health", health_check)
    app.router.add_get("/", health_check)
    
    # Start web server
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', WEBHOOK_PORT)
    await site.start()
    
    print("✅ Bot is now running 24/7 with webhook!")
    print("💬 Send /start to your bot to begin")
    print("=" * 60)
    
    # Keep running
    import asyncio
    await asyncio.Event().wait()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
