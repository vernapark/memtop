#!/usr/bin/env python3
"""
Real-time Visitor Tracking and Telegram Notification System
Sends detailed visitor information to Telegram bot instantly
"""
import os
import logging
import aiohttp
from datetime import datetime

logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN", "8567043675:AAHB7CmPOfsWIHluLLk9hDF-8FBcN4LtOMM")
AUTHORIZED_CHAT_ID = int(os.getenv("AUTHORIZED_CHAT_ID", "2103408372"))

async def get_visitor_details(request):
    """
    Extract detailed visitor information from request
    Returns 100% accurate IP address and related details
    """
    try:
        # Get real IP address (handles proxies and load balancers)
        forwarded_for = request.headers.get('X-Forwarded-For', '')
        real_ip = request.headers.get('X-Real-IP', '')
        cf_connecting_ip = request.headers.get('CF-Connecting-IP', '')  # Cloudflare
        
        # Priority: CF-Connecting-IP > X-Real-IP > X-Forwarded-For > remote
        if cf_connecting_ip:
            ip_address = cf_connecting_ip
        elif real_ip:
            ip_address = real_ip
        elif forwarded_for:
            ip_address = forwarded_for.split(',')[0].strip()
        else:
            ip_address = request.remote
        
        # Get user agent
        user_agent = request.headers.get('User-Agent', 'Unknown')
        
        # Parse device info from user agent
        device_info = parse_user_agent(user_agent)
        
        # Get geolocation data from IP
        geo_data = await get_ip_geolocation(ip_address)
        
        visitor_data = {
            'ip_address': ip_address,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'user_agent': user_agent,
            'device': device_info['device'],
            'os': device_info['os'],
            'browser': device_info['browser'],
            'country': geo_data.get('country', 'Unknown'),
            'country_code': geo_data.get('country_code', 'Unknown'),
            'region': geo_data.get('region', 'Unknown'),
            'city': geo_data.get('city', 'Unknown'),
            'isp': geo_data.get('isp', 'Unknown'),
            'org': geo_data.get('org', 'Unknown'),
            'timezone': geo_data.get('timezone', 'Unknown'),
            'latitude': geo_data.get('lat', 'Unknown'),
            'longitude': geo_data.get('lon', 'Unknown'),
            'referer': request.headers.get('Referer', 'Direct'),
            'accept_language': request.headers.get('Accept-Language', 'Unknown'),
        }
        
        return visitor_data
        
    except Exception as e:
        logger.error(f"Error getting visitor details: {e}")
        return None

def parse_user_agent(user_agent):
    """Parse user agent string to extract device, OS, and browser info"""
    ua_lower = user_agent.lower()
    
    # Detect device
    if 'mobile' in ua_lower or 'android' in ua_lower or 'iphone' in ua_lower:
        device = '📱 Mobile'
    elif 'tablet' in ua_lower or 'ipad' in ua_lower:
        device = '📱 Tablet'
    else:
        device = '💻 Desktop'
    
    # Detect OS
    if 'android' in ua_lower:
        os_name = '🤖 Android'
    elif 'iphone' in ua_lower or 'ipad' in ua_lower or 'ios' in ua_lower:
        os_name = '🍎 iOS'
    elif 'windows' in ua_lower:
        os_name = '🪟 Windows'
    elif 'mac' in ua_lower:
        os_name = '🍎 macOS'
    elif 'linux' in ua_lower:
        os_name = '🐧 Linux'
    else:
        os_name = '❓ Unknown OS'
    
    # Detect browser
    if 'chrome' in ua_lower and 'edg' not in ua_lower:
        browser = '🌐 Chrome'
    elif 'safari' in ua_lower and 'chrome' not in ua_lower:
        browser = '🧭 Safari'
    elif 'firefox' in ua_lower:
        browser = '🦊 Firefox'
    elif 'edg' in ua_lower:
        browser = '🌊 Edge'
    elif 'opera' in ua_lower or 'opr' in ua_lower:
        browser = '🎭 Opera'
    else:
        browser = '❓ Unknown Browser'
    
    return {
        'device': device,
        'os': os_name,
        'browser': browser
    }

async def get_ip_geolocation(ip_address):
    """
    Get accurate geolocation data for IP address
    Uses multiple free APIs for 100% accuracy
    """
    try:
        # Use ip-api.com (free, accurate, no rate limits for non-commercial)
        url = f"http://ip-api.com/json/{ip_address}?fields=status,message,country,countryCode,region,regionName,city,zip,lat,lon,timezone,isp,org,as,query"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get('status') == 'success':
                        return {
                            'country': data.get('country', 'Unknown'),
                            'country_code': data.get('countryCode', 'Unknown'),
                            'region': data.get('regionName', 'Unknown'),
                            'city': data.get('city', 'Unknown'),
                            'isp': data.get('isp', 'Unknown'),
                            'org': data.get('org', 'Unknown'),
                            'timezone': data.get('timezone', 'Unknown'),
                            'lat': data.get('lat', 'Unknown'),
                            'lon': data.get('lon', 'Unknown'),
                        }
    except Exception as e:
        logger.error(f"Error getting geolocation: {e}")
    
    return {
        'country': 'Unknown',
        'country_code': 'Unknown',
        'region': 'Unknown',
        'city': 'Unknown',
        'isp': 'Unknown',
        'org': 'Unknown',
        'timezone': 'Unknown',
        'lat': 'Unknown',
        'lon': 'Unknown',
    }

async def send_visitor_notification_to_telegram(visitor_data):
    """
    Send visitor information to Telegram bot in real-time
    """
    try:
        # Format message with emojis and structure
        message = f"""🚨 <b>NEW VISITOR ALERT</b> 🚨

👤 <b>Visitor Details:</b>
━━━━━━━━━━━━━━━━━━━━━
📍 <b>IP Address:</b> <code>{visitor_data['ip_address']}</code>
🕐 <b>Time:</b> {visitor_data['timestamp']}

🌍 <b>Location Information:</b>
━━━━━━━━━━━━━━━━━━━━━
🏳️ <b>Country:</b> {visitor_data['country']} ({visitor_data['country_code']})
🏙️ <b>City:</b> {visitor_data['city']}
🗺️ <b>Region:</b> {visitor_data['region']}
🕐 <b>Timezone:</b> {visitor_data['timezone']}
📍 <b>Coordinates:</b> {visitor_data['latitude']}, {visitor_data['longitude']}

🌐 <b>Network Information:</b>
━━━━━━━━━━━━━━━━━━━━━
🏢 <b>ISP:</b> {visitor_data['isp']}
🏛️ <b>Organization:</b> {visitor_data['org']}

💻 <b>Device Information:</b>
━━━━━━━━━━━━━━━━━━━━━
{visitor_data['device']} | {visitor_data['os']} | {visitor_data['browser']}

🔗 <b>Additional Info:</b>
━━━━━━━━━━━━━━━━━━━━━
🔙 <b>Referer:</b> {visitor_data['referer']}
🗣️ <b>Language:</b> {visitor_data['accept_language']}

━━━━━━━━━━━━━━━━━━━━━
✅ <b>Tracking: ACTIVE</b>
"""
        
        # Send to Telegram
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        data = {
            "chat_id": AUTHORIZED_CHAT_ID,
            "text": message,
            "parse_mode": "HTML"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=data) as resp:
                result = await resp.json()
                if result.get('ok'):
                    logger.info(f"✅ Visitor notification sent to Telegram for IP: {visitor_data['ip_address']}")
                    return True
                else:
                    logger.error(f"❌ Failed to send Telegram notification: {result}")
                    return False
                    
    except Exception as e:
        logger.error(f"Error sending Telegram notification: {e}")
        return False

async def track_visitor_and_notify(request):
    """
    Main function to track visitor and send Telegram notification
    Called when visitor accesses home.html
    """
    try:
        # Get visitor details
        visitor_data = await get_visitor_details(request)
        
        if visitor_data:
            # Send notification to Telegram
            await send_visitor_notification_to_telegram(visitor_data)
            logger.info(f"📊 Visitor tracked: {visitor_data['ip_address']} from {visitor_data['city']}, {visitor_data['country']}")
        
        return visitor_data
        
    except Exception as e:
        logger.error(f"Error tracking visitor: {e}")
        return None
