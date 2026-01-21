#!/usr/bin/env python3
"""
Clean Telegram Bot Implementation - FIXED for python-telegram-bot 20.7
"""
import os
import json
import secrets
import string
import sys
import asyncio
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import logging

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN", "8567043675:AAHB7CmPOfsWIHluLLk9hDF-8FBcN4LtOMM")
AUTHORIZED_CHAT_ID = int(os.getenv("AUTHORIZED_CHAT_ID", "2103408372"))
KEY_STORAGE_FILE = "key_storage.json"
ACCESS_CODES_FILE = "access_codes.json"

def generate_key(length=32):
    characters = string.ascii_letters + string.digits
    return ''.join(secrets.choice(characters) for _ in range(length))

def load_key_storage():
    if os.path.exists(KEY_STORAGE_FILE):
        try:
            with open(KEY_STORAGE_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading key storage: {e}")
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
            logger.error(f"Error loading access codes: {e}")
    return {"access_codes": []}

def save_access_codes(data):
    with open(ACCESS_CODES_FILE, 'w') as f:
        json.dump(data, f, indent=2)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if chat_id != AUTHORIZED_CHAT_ID:
        await update.message.reply_text("Unauthorized access.")
        return
    
    message = (
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
    await update.message.reply_text(message)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if chat_id != AUTHORIZED_CHAT_ID:
        await update.message.reply_text("Unauthorized access.")
        return
    
    message = (
        "Complete Help Guide\n\n"
        "ADMIN KEY MANAGEMENT\n\n"
        "What is the Admin Key?\n"
        "The admin key is used to access the admin panel.\n\n"
        "How to use:\n"
        "1. Use /createkey to generate new key\n"
        "2. Copy the generated key\n"
        "3. Paste it in the admin panel\n\n"
        "USER ACCESS CODES\n\n"
        "Access codes allow users to enter the website.\n\n"
        "Features:\n"
        "- Each access code is unique\n"
        "- You can generate multiple access codes\n"
        "- Codes can be revoked anytime\n"
        "- All codes are stored securely\n\n"
        "Commands:\n"
        "/generatecode - Create new access code\n"
        "/listcodes - See all active codes\n"
        "/revokecode <code> - Delete a code"
    )
    await update.message.reply_text(message)

async def create_key(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if chat_id != AUTHORIZED_CHAT_ID:
        await update.message.reply_text("Unauthorized access.")
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
        f"New Admin Key Generated!\n\n"
        f"Key: {new_key}\n\n"
        f"Created: {timestamp}\n"
        f"By: @{username}\n\n"
        f"Keep this key secure!"
    )
    await update.message.reply_text(message)

async def current_key(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if chat_id != AUTHORIZED_CHAT_ID:
        await update.message.reply_text("Unauthorized access.")
        return
    
    key_data = load_key_storage()
    
    if not key_data.get('current_key'):
        await update.message.reply_text("No admin key exists yet.\nUse /createkey to generate one.")
        return
    
    message = (
        f"Current Admin Key\n\n"
        f"Key: {key_data['current_key']}\n\n"
        f"Created: {key_data.get('created_at', 'Unknown')}\n"
        f"By: @{key_data.get('created_by', 'Unknown')}"
    )
    await update.message.reply_text(message)

async def generate_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if chat_id != AUTHORIZED_CHAT_ID:
        await update.message.reply_text("Unauthorized access.")
        return
    
    new_code = generate_key(16)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    codes_data = load_access_codes()
    codes_data['access_codes'].append(new_code)
    save_access_codes(codes_data)
    
    message = (
        f"User Access Code Generated!\n\n"
        f"Code: {new_code}\n\n"
        f"Created: {timestamp}\n"
        f"Total Active Codes: {len(codes_data['access_codes'])}\n\n"
        f"Share this code with users who need access."
    )
    await update.message.reply_text(message)

async def list_codes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if chat_id != AUTHORIZED_CHAT_ID:
        await update.message.reply_text("Unauthorized access.")
        return
    
    codes_data = load_access_codes()
    codes = codes_data.get('access_codes', [])
    
    if not codes:
        await update.message.reply_text("No active access codes.\nUse /generatecode to create one.")
        return
    
    message = f"Active Access Codes ({len(codes)})\n\n"
    for i, code in enumerate(codes, 1):
        message += f"{i}. {code}\n"
    
    message += f"\nTotal: {len(codes)} code(s)"
    await update.message.reply_text(message)

async def revoke_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if chat_id != AUTHORIZED_CHAT_ID:
        await update.message.reply_text("Unauthorized access.")
        return
    
    if not context.args:
        await update.message.reply_text("Usage: /revokecode <code>\n\nExample:\n/revokecode abc123xyz456")
        return
    
    code_to_revoke = context.args[0]
    
    codes_data = load_access_codes()
    codes = codes_data.get('access_codes', [])
    
    if code_to_revoke in codes:
        codes.remove(code_to_revoke)
        codes_data['access_codes'] = codes
        save_access_codes(codes_data)
        
        await update.message.reply_text(
            f"Access code revoked!\n\n"
            f"Removed: {code_to_revoke}\n"
            f"Remaining Codes: {len(codes)}"
        )
    else:
        await update.message.reply_text(f"Code not found: {code_to_revoke}")

async def main():
    print("=" * 70)
    print("Starting Telegram Bot (POLLING MODE)")
    print("=" * 70)
    print(f"Bot Token: {BOT_TOKEN[:20]}...")
    print(f"Authorized Chat ID: {AUTHORIZED_CHAT_ID}")
    print("=" * 70)
    
    try:
        application = Application.builder().token(BOT_TOKEN).build()
        
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("createkey", create_key))
        application.add_handler(CommandHandler("currentkey", current_key))
        application.add_handler(CommandHandler("generatecode", generate_code))
        application.add_handler(CommandHandler("listcodes", list_codes))
        application.add_handler(CommandHandler("revokecode", revoke_code))
        
        logger.info("Bot commands registered")
        
        await application.initialize()
        await application.start()
        logger.info("Application started")
        
        await application.updater.start_polling(
            poll_interval=1.0,
            timeout=10,
            bootstrap_retries=-1,
            read_timeout=2,
            allowed_updates=Update.ALL_TYPES
        )
        logger.info("Polling started successfully")
        
        await asyncio.Event().wait()
        
    except Exception as e:
        logger.error(f"FATAL ERROR: {e}", exc_info=True)
        sys.exit(1)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nShutting down gracefully...")
    except Exception as e:
        print(f"\nFATAL ERROR: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
