#!/usr/bin/env python3
"""
Telegram Bot - USING TELEBOT LIBRARY INSTEAD
python-telegram-bot is broken - using pyTelegramBotAPI which actually works
"""
import os
import json
import secrets
import string
import sys
from datetime import datetime
import logging
import time

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

def main():
    print("=" * 70)
    print("Starting Telegram Bot - USING TELEBOT")
    print("=" * 70)
    print(f"Bot Token: {BOT_TOKEN[:20]}...")
    print(f"Authorized Chat ID: {AUTHORIZED_CHAT_ID}")
    print("=" * 70)
    
    try:
        import telebot
        
        bot = telebot.TeleBot(BOT_TOKEN)
        
        @bot.message_handler(commands=['start'])
        def handle_start(message):
            if message.chat.id != AUTHORIZED_CHAT_ID:
                bot.reply_to(message, "Unauthorized access.")
                return
            
            text = (
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
            bot.reply_to(message, text)
        
        @bot.message_handler(commands=['help'])
        def handle_help(message):
            if message.chat.id != AUTHORIZED_CHAT_ID:
                bot.reply_to(message, "Unauthorized access.")
                return
            
            text = (
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
            bot.reply_to(message, text)
        
        @bot.message_handler(commands=['createkey'])
        def handle_createkey(message):
            if message.chat.id != AUTHORIZED_CHAT_ID:
                bot.reply_to(message, "Unauthorized access.")
                return
            
            new_key = generate_key()
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            username = message.from_user.username or "Unknown"
            
            key_data = {
                "current_key": new_key,
                "created_at": timestamp,
                "created_by": username
            }
            save_key_storage(key_data)
            
            text = f"New Admin Key Generated!\n\nKey: {new_key}\n\nCreated: {timestamp}\nBy: @{username}\n\nKeep this key secure!"
            bot.reply_to(message, text)
        
        @bot.message_handler(commands=['currentkey'])
        def handle_currentkey(message):
            if message.chat.id != AUTHORIZED_CHAT_ID:
                bot.reply_to(message, "Unauthorized access.")
                return
            
            key_data = load_key_storage()
            
            if not key_data.get('current_key'):
                bot.reply_to(message, "No admin key exists yet.\nUse /createkey to generate one.")
                return
            
            text = f"Current Admin Key\n\nKey: {key_data['current_key']}\n\nCreated: {key_data.get('created_at', 'Unknown')}\nBy: @{key_data.get('created_by', 'Unknown')}"
            bot.reply_to(message, text)
        
        @bot.message_handler(commands=['generatecode'])
        def handle_generatecode(message):
            if message.chat.id != AUTHORIZED_CHAT_ID:
                bot.reply_to(message, "Unauthorized access.")
                return
            
            new_code = generate_key(16)
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            codes_data = load_access_codes()
            codes_data['access_codes'].append(new_code)
            save_access_codes(codes_data)
            
            text = f"User Access Code Generated!\n\nCode: {new_code}\n\nCreated: {timestamp}\nTotal Active Codes: {len(codes_data['access_codes'])}\n\nShare this code with users."
            bot.reply_to(message, text)
        
        @bot.message_handler(commands=['listcodes'])
        def handle_listcodes(message):
            if message.chat.id != AUTHORIZED_CHAT_ID:
                bot.reply_to(message, "Unauthorized access.")
                return
            
            codes_data = load_access_codes()
            codes = codes_data.get('access_codes', [])
            
            if not codes:
                bot.reply_to(message, "No active access codes.\nUse /generatecode to create one.")
                return
            
            text = f"Active Access Codes ({len(codes)})\n\n"
            for i, code in enumerate(codes, 1):
                text += f"{i}. {code}\n"
            
            text += f"\nTotal: {len(codes)} code(s)"
            bot.reply_to(message, text)
        
        @bot.message_handler(commands=['revokecode'])
        def handle_revokecode(message):
            if message.chat.id != AUTHORIZED_CHAT_ID:
                bot.reply_to(message, "Unauthorized access.")
                return
            
            parts = message.text.split()
            if len(parts) < 2:
                bot.reply_to(message, "Usage: /revokecode <code>\n\nExample:\n/revokecode abc123xyz456")
                return
            
            code_to_revoke = parts[1]
            
            codes_data = load_access_codes()
            codes = codes_data.get('access_codes', [])
            
            if code_to_revoke in codes:
                codes.remove(code_to_revoke)
                codes_data['access_codes'] = codes
                save_access_codes(codes_data)
                
                bot.reply_to(message, f"Access code revoked!\n\nRemoved: {code_to_revoke}\nRemaining Codes: {len(codes)}")
            else:
                bot.reply_to(message, f"Code not found: {code_to_revoke}")
        
        logger.info("Bot commands registered")
        logger.info("Starting polling...")
        
        # Start polling with infinity_polling (better than polling for long-running bots)
        bot.infinity_polling()
        
    except Exception as e:
        logger.error(f"FATAL ERROR: {e}", exc_info=True)
        sys.exit(1)

if __name__ == '__main__':
    main()
