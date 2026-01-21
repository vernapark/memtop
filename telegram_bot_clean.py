#!/usr/bin/env python3
"""
Telegram Bot - RAW API VERSION
Uses python-telegram-bot v13 which is stable and works with all Python versions
"""
import os
import json
import secrets
import string
import sys
import time
from datetime import datetime
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

def handle_start(chat_id, bot):
    if chat_id != AUTHORIZED_CHAT_ID:
        bot.send_message(chat_id=chat_id, text="Unauthorized access.")
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
    bot.send_message(chat_id=chat_id, text=message)

def handle_help(chat_id, bot):
    if chat_id != AUTHORIZED_CHAT_ID:
        bot.send_message(chat_id=chat_id, text="Unauthorized access.")
        return
    
    message = (
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
    bot.send_message(chat_id=chat_id, text=message)

def handle_createkey(chat_id, username, bot):
    if chat_id != AUTHORIZED_CHAT_ID:
        bot.send_message(chat_id=chat_id, text="Unauthorized access.")
        return
    
    new_key = generate_key()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    key_data = {
        "current_key": new_key,
        "created_at": timestamp,
        "created_by": username or "Unknown"
    }
    save_key_storage(key_data)
    
    message = f"New Admin Key Generated!\n\nKey: {new_key}\n\nCreated: {timestamp}\nBy: @{username}\n\nKeep this key secure!"
    bot.send_message(chat_id=chat_id, text=message)

def handle_currentkey(chat_id, bot):
    if chat_id != AUTHORIZED_CHAT_ID:
        bot.send_message(chat_id=chat_id, text="Unauthorized access.")
        return
    
    key_data = load_key_storage()
    
    if not key_data.get('current_key'):
        bot.send_message(chat_id=chat_id, text="No admin key exists yet.\nUse /createkey to generate one.")
        return
    
    message = f"Current Admin Key\n\nKey: {key_data['current_key']}\n\nCreated: {key_data.get('created_at', 'Unknown')}\nBy: @{key_data.get('created_by', 'Unknown')}"
    bot.send_message(chat_id=chat_id, text=message)

def handle_generatecode(chat_id, bot):
    if chat_id != AUTHORIZED_CHAT_ID:
        bot.send_message(chat_id=chat_id, text="Unauthorized access.")
        return
    
    new_code = generate_key(16)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    codes_data = load_access_codes()
    codes_data['access_codes'].append(new_code)
    save_access_codes(codes_data)
    
    message = f"User Access Code Generated!\n\nCode: {new_code}\n\nCreated: {timestamp}\nTotal Active Codes: {len(codes_data['access_codes'])}\n\nShare this code with users."
    bot.send_message(chat_id=chat_id, text=message)

def handle_listcodes(chat_id, bot):
    if chat_id != AUTHORIZED_CHAT_ID:
        bot.send_message(chat_id=chat_id, text="Unauthorized access.")
        return
    
    codes_data = load_access_codes()
    codes = codes_data.get('access_codes', [])
    
    if not codes:
        bot.send_message(chat_id=chat_id, text="No active access codes.\nUse /generatecode to create one.")
        return
    
    message = f"Active Access Codes ({len(codes)})\n\n"
    for i, code in enumerate(codes, 1):
        message += f"{i}. {code}\n"
    
    message += f"\nTotal: {len(codes)} code(s)"
    bot.send_message(chat_id=chat_id, text=message)

def handle_revokecode(chat_id, text, bot):
    if chat_id != AUTHORIZED_CHAT_ID:
        bot.send_message(chat_id=chat_id, text="Unauthorized access.")
        return
    
    parts = text.split()
    if len(parts) < 2:
        bot.send_message(chat_id=chat_id, text="Usage: /revokecode <code>\n\nExample:\n/revokecode abc123xyz456")
        return
    
    code_to_revoke = parts[1]
    
    codes_data = load_access_codes()
    codes = codes_data.get('access_codes', [])
    
    if code_to_revoke in codes:
        codes.remove(code_to_revoke)
        codes_data['access_codes'] = codes
        save_access_codes(codes_data)
        
        bot.send_message(chat_id=chat_id, text=f"Access code revoked!\n\nRemoved: {code_to_revoke}\nRemaining Codes: {len(codes)}")
    else:
        bot.send_message(chat_id=chat_id, text=f"Code not found: {code_to_revoke}")

def main():
    print("=" * 70)
    print("Starting Telegram Bot - v13 STABLE VERSION")
    print("=" * 70)
    print(f"Bot Token: {BOT_TOKEN[:20]}...")
    print(f"Authorized Chat ID: {AUTHORIZED_CHAT_ID}")
    print("=" * 70)
    
    try:
        from telegram.ext import Updater, CommandHandler
        
        # Create updater with v13 API (which works!)
        updater = Updater(token=BOT_TOKEN, use_context=True)
        dispatcher = updater.dispatcher
        
        # Register handlers
        dispatcher.add_handler(CommandHandler("start", lambda update, context: handle_start(update.effective_chat.id, context.bot)))
        dispatcher.add_handler(CommandHandler("help", lambda update, context: handle_help(update.effective_chat.id, context.bot)))
        dispatcher.add_handler(CommandHandler("createkey", lambda update, context: handle_createkey(update.effective_chat.id, update.effective_user.username, context.bot)))
        dispatcher.add_handler(CommandHandler("currentkey", lambda update, context: handle_currentkey(update.effective_chat.id, context.bot)))
        dispatcher.add_handler(CommandHandler("generatecode", lambda update, context: handle_generatecode(update.effective_chat.id, context.bot)))
        dispatcher.add_handler(CommandHandler("listcodes", lambda update, context: handle_listcodes(update.effective_chat.id, context.bot)))
        dispatcher.add_handler(CommandHandler("revokecode", lambda update, context: handle_revokecode(update.effective_chat.id, update.message.text, context.bot)))
        
        logger.info("Bot commands registered")
        logger.info("Starting polling...")
        
        # Start polling
        updater.start_polling()
        logger.info("Bot is running!")
        
        # Keep running
        updater.idle()
        
    except Exception as e:
        logger.error(f"FATAL ERROR: {e}", exc_info=True)
        sys.exit(1)

if __name__ == '__main__':
    main()
