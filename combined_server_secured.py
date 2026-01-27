#!/usr/bin/env python3
"""
🔒 SECURED VERSION - Anti-Tracking, Anti-Reverse Engineering Protection
Wraps the existing bulletproof server with advanced security features
"""

import os
import sys
import importlib.util
from functools import wraps
from aiohttp import web
import logging

# Import security middleware
from security_middleware import (
    SecurityMiddleware,
    require_security,
    require_video_token,
    SECURITY_CONFIG
)

# Import the original server
spec = importlib.util.spec_from_file_location(
    "original_server", 
    "combined_server_bulletproof_multi.py"
)
original_server = importlib.util.module_from_spec(spec)
spec.loader.exec_module(original_server)

logger = logging.getLogger(__name__)

# ============================================================================
# SECURITY WRAPPER MIDDLEWARE
# ============================================================================

@web.middleware
async def security_middleware(request, handler):
    """Apply security checks to all requests"""
    
    # Skip security for health check
    if request.path == '/health':
        return await handler(request)
    
    # Get client identifier
    client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    fingerprint = SecurityMiddleware.get_client_fingerprint(request)
    identifier = f"{client_ip}:{fingerprint}"
    
    # Check for suspicious patterns
    if SECURITY_CONFIG['block_suspicious_patterns']:
        if SecurityMiddleware.is_suspicious_request(request):
            logger.warning(f"🚨 Suspicious request blocked from {client_ip}")
            return web.json_response({'error': 'Forbidden'}, status=403)
    
    # Rate limiting
    allowed, reason = SecurityMiddleware.rate_limit_check(
        identifier,
        SECURITY_CONFIG['max_requests_per_minute'],
        60
    )
    
    if not allowed:
        logger.warning(f"🚨 Rate limit exceeded: {identifier} - {reason}")
        if reason == 'IP_BANNED':
            return web.json_response({'error': 'Access denied'}, status=403)
        return web.json_response({'error': 'Too many requests. Please slow down.'}, status=429)
    
    # Process request
    try:
        response = await handler(request)
        
        # Add security headers
        response = SecurityMiddleware.add_security_headers(response)
        
        return response
        
    except web.HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing request: {e}")
        return web.json_response({'error': 'Internal server error'}, status=500)


# ============================================================================
# SECURED VIDEO API ENDPOINTS
# ============================================================================

async def get_video_token(request):
    """Generate secure token for video access"""
    try:
        data = await request.json()
        video_id = data.get('video_id')
        
        if not video_id:
            return web.json_response({'error': 'video_id required'}, status=400)
        
        # Generate encrypted token
        token = SecurityMiddleware.encrypt_video_url(video_id)
        
        return web.json_response({
            'success': True,
            'token': token,
            'expires_in': SECURITY_CONFIG['video_token_expiry']
        })
        
    except Exception as e:
        logger.error(f"Error generating token: {e}")
        return web.json_response({'error': str(e)}, status=500)


async def get_secured_video_url(request):
    """Get video URL with valid token"""
    try:
        token = request.query.get('token')
        
        if not token:
            return web.json_response({'error': 'Token required'}, status=401)
        
        video_id = SecurityMiddleware.decrypt_video_token(token)
        
        if not video_id:
            return web.json_response({'error': 'Invalid or expired token'}, status=401)
        
        # Get video from original function
        # For now, return success - integration with cloudinary needed
        return web.json_response({
            'success': True,
            'video_id': video_id,
            'message': 'Token valid'
        })
        
    except Exception as e:
        logger.error(f"Error validating token: {e}")
        return web.json_response({'error': str(e)}, status=500)


async def security_violation_handler(request):
    """Handle security violation reports from client"""
    try:
        data = await request.json()
        violation_type = data.get('type', 'unknown')
        timestamp = data.get('timestamp', '')
        fingerprint = data.get('fingerprint', '')
        
        client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        
        logger.warning(f"🚨 Security Violation - Type: {violation_type}, IP: {client_ip}, Fingerprint: {fingerprint}")
        
        # Could add to ban list or take other actions
        
        return web.json_response({'received': True})
        
    except Exception as e:
        logger.error(f"Error handling violation: {e}")
        return web.json_response({'error': str(e)}, status=500)


# ============================================================================
# CLEANUP TASK
# ============================================================================

async def cleanup_task(app):
    """Background task to clean up expired data"""
    import asyncio
    
    while True:
        try:
            await asyncio.sleep(300)  # Run every 5 minutes
            SecurityMiddleware.cleanup_expired_data()
            logger.info("🧹 Cleaned up expired security data")
        except Exception as e:
            logger.error(f"Cleanup error: {e}")


async def start_cleanup_task(app):
    """Start cleanup background task"""
    app['cleanup_task'] = app.loop.create_task(cleanup_task(app))


async def cleanup_background_tasks(app):
    """Stop cleanup task on shutdown"""
    app['cleanup_task'].cancel()
    await app['cleanup_task']


# ============================================================================
# MAIN FUNCTION WITH SECURITY
# ============================================================================

def main():
    print("=" * 80)
    print("🔒 BULLETPROOF SECURED SERVER")
    print("   - Anti-Tracking Protection")
    print("   - Anti-Reverse Engineering")
    print("   - Rate Limiting & DDoS Protection")
    print("   - Encrypted Video URLs")
    print("   - Security Headers")
    print("=" * 80)
    
    # Create app with security middleware
    app = web.Application(
        client_max_size=1024**3,
        middlewares=[security_middleware]
    )
    
    # Add all original routes from the base server
    # Bot webhook
    app.router.add_post('/telegram-webhook', original_server.handle_telegram_webhook)
    
    # Cloudinary video API routes
    app.router.add_post('/api/upload-video', original_server.upload_video_to_cloudinary)
    app.router.add_get('/api/videos', original_server.get_videos_from_cloudinary)
    app.router.add_post('/api/delete-video', original_server.delete_video_from_cloudinary)
    
    # Account management
    app.router.add_get('/api/cloudinary-accounts', original_server.get_accounts_info)
    
    # Visitor tracking API routes
    app.router.add_post('/api/visitor/connect', original_server.visitor_connect)
    app.router.add_post('/api/visitor/heartbeat', original_server.visitor_heartbeat)
    app.router.add_post('/api/visitor/disconnect', original_server.visitor_disconnect)
    app.router.add_get('/api/visitors/active', original_server.get_active_visitors)
    
    # APK download routes
    app.router.add_get('/api/get-app-info', original_server.get_app_info)
    app.router.add_get('/download-app', original_server.download_app)
    app.router.add_post('/api/upload-apk', original_server.upload_apk)
    
    # NEW SECURITY ROUTES
    app.router.add_post('/api/security/get-token', get_video_token)
    app.router.add_get('/api/security/video', get_secured_video_url)
    app.router.add_post('/api/security/violation', security_violation_handler)
    
    # Website routes (must be last)
    app.router.add_get("/health", original_server.health_check)
    app.router.add_route('*', "/{path:.*}", original_server.serve_file)
    
    # Startup tasks
    app.on_startup.append(original_server.startup)
    app.on_startup.append(start_cleanup_task)
    app.on_cleanup.append(cleanup_background_tasks)
    
    PORT = int(os.getenv('PORT', 10000))
    HOST = '0.0.0.0'
    
    print(f"🚀 Starting secured server on {HOST}:{PORT}")
    print("=" * 80)
    
    logger.info("🔒 Security features enabled:")
    logger.info(f"   - Rate limiting: {SECURITY_CONFIG['max_requests_per_minute']}/min")
    logger.info(f"   - Video token expiry: {SECURITY_CONFIG['video_token_expiry']}s")
    logger.info(f"   - Ban duration: {SECURITY_CONFIG['ban_duration']}s")
    logger.info("   - Suspicious pattern blocking: ✅")
    logger.info("   - Security headers: ✅")
    
    web.run_app(app, host=HOST, port=PORT)


if __name__ == '__main__':
    main()
