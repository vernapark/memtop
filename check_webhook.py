#!/usr/bin/env python3
"""Check and delete webhook to fix 409 conflict"""
import requests
import sys

BOT_TOKEN = "8567043675:AAHB7CmPOfsWIHluLLk9hDF-8FBcN4LtOMM"
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

print("=" * 70)
print("Checking Telegram Bot Webhook Status")
print("=" * 70)

# Check current webhook
print("\n1. Checking current webhook...")
response = requests.get(f"{API_URL}/getWebhookInfo")
data = response.json()

if data.get('ok'):
    webhook_info = data['result']
    webhook_url = webhook_info.get('url', '')
    
    print(f"Webhook URL: {webhook_url if webhook_url else 'NOT SET'}")
    print(f"Pending updates: {webhook_info.get('pending_update_count', 0)}")
    print(f"Last error: {webhook_info.get('last_error_message', 'None')}")
    
    if webhook_url:
        print("\n⚠️ WEBHOOK IS SET! This conflicts with polling.")
        print("\n2. Deleting webhook...")
        
        # Delete webhook
        delete_response = requests.post(f"{API_URL}/deleteWebhook")
        delete_data = delete_response.json()
        
        if delete_data.get('ok'):
            print("✅ Webhook deleted successfully!")
            print("\n3. Verifying deletion...")
            
            # Verify
            verify_response = requests.get(f"{API_URL}/getWebhookInfo")
            verify_data = verify_response.json()
            
            if verify_data.get('ok'):
                new_url = verify_data['result'].get('url', '')
                if not new_url:
                    print("✅ Confirmed: No webhook set")
                    print("\nNow your polling bot should work!")
                else:
                    print(f"❌ Webhook still exists: {new_url}")
        else:
            print(f"❌ Failed to delete webhook: {delete_data}")
    else:
        print("\n✅ No webhook set - polling should work!")
        print("\nThe 409 error might be from:")
        print("- Multiple Render deployments running at same time")
        print("- Render restarting the service (creating 2 instances briefly)")
        
else:
    print(f"❌ Error checking webhook: {data}")

print("\n" + "=" * 70)
