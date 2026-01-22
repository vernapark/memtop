"""
Live Visitor Tracking System
Tracks real IP addresses with geolocation (country + flag)
"""
import time
import asyncio
import logging
from aiohttp import web

logger = logging.getLogger(__name__)

# In-memory storage for active visitors
active_visitors = {}
visitor_lock = asyncio.Lock()

async def get_visitor_ip(request):
    """Get real IP address from request, handling proxies"""
    # Check for forwarded IP (behind proxy/load balancer)
    forwarded = request.headers.get('X-Forwarded-For')
    if forwarded:
        return forwarded.split(',')[0].strip()
    
    real_ip = request.headers.get('X-Real-IP')
    if real_ip:
        return real_ip
    
    # Fallback to direct connection IP
    peername = request.transport.get_extra_info('peername')
    if peername:
        return peername[0]
    
    return 'Unknown'

async def get_geo_location(ip):
    """Get country info from IP using ip-api.com (free, no API key needed)"""
    if ip in ['127.0.0.1', 'localhost', 'Unknown', '::1']:
        return {
            'country': 'Local',
            'countryCode': 'XX',
            'flag': '🏠'
        }
    
    try:
        import aiohttp
        async with aiohttp.ClientSession() as session:
            url = f'http://ip-api.com/json/{ip}?fields=status,country,countryCode'
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=3)) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if data.get('status') == 'success':
                        country_code = data.get('countryCode', 'XX')
                        # Convert country code to flag emoji
                        flag = ''.join(chr(127397 + ord(c)) for c in country_code.upper())
                        return {
                            'country': data.get('country', 'Unknown'),
                            'countryCode': country_code,
                            'flag': flag
                        }
    except Exception as e:
        logger.error(f'Geolocation error for {ip}: {e}')
    
    return {
        'country': 'Unknown',
        'countryCode': 'XX',
        'flag': '🌐'
    }

async def visitor_connect(request):
    """Register a new visitor"""
    try:
        ip = await get_visitor_ip(request)
        data = await request.json()
        session_id = data.get('sessionId')
        page = data.get('page', '/')
        
        if not session_id:
            return web.json_response({'error': 'sessionId required'}, status=400)
        
        # Get geolocation
        geo = await get_geo_location(ip)
        
        async with visitor_lock:
            visitor_id = f'{ip}_{session_id}'
            active_visitors[visitor_id] = {
                'ip': ip,
                'sessionId': session_id,
                'country': geo['country'],
                'countryCode': geo['countryCode'],
                'flag': geo['flag'],
                'page': page,
                'connectedAt': time.time(),
                'lastSeen': time.time()
            }
        
        logger.info(f'🟢 Visitor connected: {ip} ({geo["country"]}) - Session: {session_id[:8]}...')
        
        return web.json_response({'success': True, 'visitorId': visitor_id})
    
    except Exception as e:
        logger.error(f'Error in visitor_connect: {e}', exc_info=True)
        return web.json_response({'error': str(e)}, status=500)

async def visitor_heartbeat(request):
    """Update visitor last seen timestamp"""
    try:
        data = await request.json()
        session_id = data.get('sessionId')
        page = data.get('page', '/')
        
        if not session_id:
            return web.json_response({'error': 'sessionId required'}, status=400)
        
        ip = await get_visitor_ip(request)
        visitor_id = f'{ip}_{session_id}'
        
        async with visitor_lock:
            if visitor_id in active_visitors:
                active_visitors[visitor_id]['lastSeen'] = time.time()
                active_visitors[visitor_id]['page'] = page
            else:
                # Visitor not found, re-register
                geo = await get_geo_location(ip)
                active_visitors[visitor_id] = {
                    'ip': ip,
                    'sessionId': session_id,
                    'country': geo['country'],
                    'countryCode': geo['countryCode'],
                    'flag': geo['flag'],
                    'page': page,
                    'connectedAt': time.time(),
                    'lastSeen': time.time()
                }
        
        return web.json_response({'success': True})
    
    except Exception as e:
        logger.error(f'Error in visitor_heartbeat: {e}')
        return web.json_response({'error': str(e)}, status=500)

async def visitor_disconnect(request):
    """Remove visitor when they leave"""
    try:
        data = await request.json()
        session_id = data.get('sessionId')
        
        if not session_id:
            return web.json_response({'error': 'sessionId required'}, status=400)
        
        ip = await get_visitor_ip(request)
        visitor_id = f'{ip}_{session_id}'
        
        async with visitor_lock:
            if visitor_id in active_visitors:
                visitor = active_visitors[visitor_id]
                logger.info(f'🔴 Visitor disconnected: {ip} ({visitor["country"]})')
                del active_visitors[visitor_id]
        
        return web.json_response({'success': True})
    
    except Exception as e:
        logger.error(f'Error in visitor_disconnect: {e}')
        return web.json_response({'error': str(e)}, status=500)

async def get_active_visitors(request):
    """Get list of all active visitors (admin only)"""
    try:
        current_time = time.time()
        timeout = 30  # Consider visitor inactive after 30 seconds
        
        async with visitor_lock:
            # Clean up stale visitors
            stale = [vid for vid, v in active_visitors.items() 
                    if current_time - v['lastSeen'] > timeout]
            
            for vid in stale:
                logger.info(f'⏱️ Removing stale visitor: {active_visitors[vid]["ip"]}')
                del active_visitors[vid]
            
            # Return active visitors list
            visitors_list = []
            for visitor_id, visitor in active_visitors.items():
                visitors_list.append({
                    'ip': visitor['ip'],
                    'country': visitor['country'],
                    'countryCode': visitor['countryCode'],
                    'flag': visitor['flag'],
                    'page': visitor['page'],
                    'duration': int(current_time - visitor['connectedAt']),
                    'lastSeen': int(current_time - visitor['lastSeen'])
                })
        
        return web.json_response({
            'visitors': visitors_list,
            'total': len(visitors_list)
        })
    
    except Exception as e:
        logger.error(f'Error in get_active_visitors: {e}', exc_info=True)
        return web.json_response({'error': str(e)}, status=500)
