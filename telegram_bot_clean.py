#!/usr/bin/env python3
"""
Clean Telegram Bot Implementation
Manages admin keys and user access codes
Uses polling (NOT webhook) for maximum reliability
"""
import os
import json
import secrets
import string
import sys
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import logging

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

# Configuration
BOT_TOKEN = os.getenv("BOT_TOKEN", "8567043675:AAHB7CmPOfsWIHluLLk9hDF-8FBcN4LtOMM")
AUTHORIZED_CHAT_ID = int(os.getenv("AUTHORIZED_CHAT_ID", "2103408372"))
KEY_STORAGE_FILE = "key_storage.json"
ACCESS_CODES_FILE = "access_codes.json"

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
# BOT COMMANDS
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
        "1. Use `/createkey` to generate new key\n"
        "2. Copy the generated key\n"
        "3. Paste it in the admin panel\n\n"
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
# MAIN APPLICATION
# ============================================================================

def main():
    """Start the bot with polling"""
    print("=" * 70)
    print("🤖 Starting Telegram Bot (POLLING MODE)")
    print("=" * 70)
    print(f"Bot Token: {BOT_TOKEN[:20]}...")
    print(f"Authorized Chat ID: {AUTHORIZED_CHAT_ID}")
    print("=" * 70)
    
    try:
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
        
        logger.info("✅ Bot commands registered")
        logger.info("🚀 Starting polling...")
        
        # Start polling
        application.run_polling(allowed_updates=Update.ALL_TYPES)
        
    except Exception as e:
        logger.error(f"❌ FATAL ERROR: {e}", exc_info=True)
        sys.exit(1)

if __name__ == '__main__':
    main()
