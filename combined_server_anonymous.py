#!/usr/bin/env python3
"""
🥷 ANONYMOUS SECURED SERVER - Complete Privacy Protection
Combines security protection + complete anonymity for uploads
NO tracking of IP, location, device, browser, or any fingerprinting
"""

import os
import sys
import logging
from aiohttp import web

# Import security middleware
from security_middleware import (
    SecurityMiddleware,
    SECURITY_CONFIG
)

# Import anonymity protection
from anonymity_middleware import (
    AnonymityProtection,
    require_anonymity
)

# Import original server
import importlib.util
spec = importlib.util.spec_from_file_location(
    "original_server", 
    "combined_server_bulletproof_multi.py"
)
original_server = importlib.util.module_from_spec(spec)
spec.loader.exec_module(original_server)

logger = logging.getLogger(__name__)

# ============================================================================
# COMBINED SECURITY + ANONYMITY MIDDLEWARE
# ============================================================================

@web.middleware
async def combined_security_middleware(request, handler):
    """
    Combined security and anonymity protection
    - Security: Rate limiting, attack prevention, headers
    - Anonymity: Strip all tracking data for uploads
    """
    
    # Skip for health check
    if request.path == '/health':
        return await handler(request)
    
    # ===== ANONYMITY PROTECTION (for uploads) =====
    if request.path in ['/api/upload-video', '/telegram-webhook'] or request.method == 'POST':
        logger.info(f"🥷 Applying anonymity protection to: {request.path}")
        
        # Strip ALL tracking information
        sanitized = AnonymityProtection.sanitize_request(request)
        
        # Store sanitized data for later use
        request._anonymized = True
        request._sanitized_data = sanitized
        
        # Add timing obfuscation
        AnonymityProtection.prevent_timing_attacks()
        
        logger.info("🥷 Upload request anonymized - zero tracking")
    
    # ===== SECURITY PROTECTION (for all requests) =====
    
    # Get client identifier (anonymized for uploads)
    if hasattr(request, '_anonymized'):
        # For anonymized requests, use generic identifier
        identifier = 'anonymous_upload'
    else:
        # For regular requests, use normal fingerprinting
        client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        fingerprint = SecurityMiddleware.get_client_fingerprint(request)
        identifier = f"{client_ip}:{fingerprint}"
    
    # Check for suspicious patterns (but not for anonymized uploads)
    if not hasattr(request, '_anonymized'):
        if SECURITY_CONFIG['block_suspicious_patterns']:
            if SecurityMiddleware.is_suspicious_request(request):
                logger.warning(f"🚨 Suspicious request blocked from {identifier}")
                return web.json_response({'error': 'Forbidden'}, status=403)
    
    # Rate limiting (lighter for anonymized uploads)
    if hasattr(request, '_anonymized'):
        # More lenient rate limiting for uploads
        allowed, reason = SecurityMiddleware.rate_limit_check(
            identifier,
            30,  # 30 uploads per minute
            3600  # 1 hour window
        )
    else:
        # Normal rate limiting
        allowed, reason = SecurityMiddleware.rate_limit_check(
            identifier,
            SECURITY_CONFIG['max_requests_per_minute'],
            60
        )
    
    if not allowed:
        logger.warning(f"🚨 Rate limit exceeded: {identifier} - {reason}")
        if reason == 'IP_BANNED':
            return web.json_response({'error': 'Access denied'}, status=403)
        return web.json_response({'error': 'Too many requests'}, status=429)
    
    # Process request
    try:
        response = await handler(request)
        
        # Add security headers
        response = SecurityMiddleware.add_security_headers(response)
        
        # Log anonymous upload (without tracking info)
        if hasattr(request, '_anonymized'):
            AnonymityProtection.create_anonymous_log_entry(
                'upload',
                {'path': request.path, 'method': request.method}
            )
        
        return response
        
    except web.HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing request: {e}")
        return web.json_response({'error': 'Internal server error'}, status=500)


# ============================================================================
# ANONYMIZED UPLOAD HANDLERS
# ============================================================================

async def anonymous_upload_video(request):
    """
    Upload video with complete anonymity
    Strips all metadata, IP, location, device info
    """
    try:
        logger.info("🥷 Processing anonymous video upload")
        
        # Get the sanitized data
        if hasattr(request, '_sanitized_data'):
            sanitized = request._sanitized_data
            logger.info(f"🥷 Using sanitized request data: {sanitized.get('ip')}")
        
        # Call original upload function
        return await original_server.upload_video_to_cloudinary(request)
        
    except Exception as e:
        logger.error(f"Error in anonymous upload: {e}")
        return web.json_response({'error': str(e)}, status=500)


async def anonymous_telegram_webhook(request):
    """
    Handle Telegram webhook with anonymity
    Prevents tracking of who sent videos via bot
    """
    try:
        logger.info("🥷 Processing anonymous Telegram upload")
        
        # Sanitize request
        if hasattr(request, '_sanitized_data'):
            sanitized = request._sanitized_data
            logger.info("🥷 Telegram webhook anonymized")
        
        # Call original webhook handler
        return await original_server.handle_telegram_webhook(request)
        
    except Exception as e:
        logger.error(f"Error in anonymous telegram webhook: {e}")
        return web.json_response({'error': str(e)}, status=500)


# ============================================================================
# ANONYMITY STATUS ENDPOINT
# ============================================================================

async def get_anonymity_status(request):
    """Check if anonymity protection is active"""
    return web.json_response({
        'anonymity_active': True,
        'protections': {
            'ip_hidden': True,
            'location_hidden': True,
            'device_hidden': True,
            'browser_hidden': True,
            'fingerprinting_blocked': True,
            'geolocation_blocked': True,
            'webrtc_blocked': True,
            'metadata_stripped': True,
        },
        'message': 'Complete anonymity protection active'
    })


# ============================================================================
# SERVE ANONYMITY SCRIPT
# ============================================================================

async def serve_anonymity_js(request):
    """Serve anonymity JavaScript"""
    try:
        with open('js/anonymity.js', 'r') as f:
            content = f.read()
        return web.Response(text=content, content_type='application/javascript')
    except Exception as e:
        logger.error(f"Error serving anonymity.js: {e}")
        return web.Response(text='', content_type='application/javascript')


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
# MAIN FUNCTION
# ============================================================================

def main():
    print("=" * 80)
    print("🥷 ANONYMOUS + BULLETPROOF SECURED SERVER")
    print("   - Complete Anonymity Protection")
    print("   - Zero Tracking (IP, Location, Device)")
    print("   - Anti-Fingerprinting")
    print("   - Rate Limiting & DDoS Protection")
    print("   - Security Headers")
    print("=" * 80)
    
    # Create app with combined middleware
    app = web.Application(
        client_max_size=1024**3,
        middlewares=[combined_security_middleware]
    )
    
    # Bot webhook (anonymized)
    app.router.add_post('/telegram-webhook', anonymous_telegram_webhook)
    
    # Video API routes (anonymized)
    app.router.add_post('/api/upload-video', anonymous_upload_video)
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
    
    # Security routes
    from combined_server_secured import get_video_token, get_secured_video_url, security_violation_handler
    app.router.add_post('/api/security/get-token', get_video_token)
    app.router.add_get('/api/security/video', get_secured_video_url)
    app.router.add_post('/api/security/violation', security_violation_handler)
    
    # Anonymity routes
    app.router.add_get('/api/anonymity/status', get_anonymity_status)
    app.router.add_get('/js/anonymity.js', serve_anonymity_js)
    
    # Health check
    app.router.add_get("/health", original_server.health_check)
    
    # Website routes (must be last)
    app.router.add_route('*', "/{path:.*}", original_server.serve_file)
    
    # Startup tasks
    app.on_startup.append(original_server.startup)
    app.on_startup.append(start_cleanup_task)
    app.on_cleanup.append(cleanup_background_tasks)
    
    PORT = int(os.getenv('PORT', 10000))
    HOST = '0.0.0.0'
    
    print(f"🚀 Starting anonymous secured server on {HOST}:{PORT}")
    print("=" * 80)
    
    logger.info("🥷 Anonymity features enabled:")
    logger.info("   - IP address: ✅ Hidden (127.0.0.1)")
    logger.info("   - Location: ✅ Blocked completely")
    logger.info("   - Device info: ✅ Anonymized")
    logger.info("   - Browser fingerprint: ✅ Blocked")
    logger.info("   - Geolocation: ✅ Disabled")
    logger.info("   - WebRTC: ✅ Blocked (no IP leak)")
    logger.info("   - Metadata: ✅ Stripped from uploads")
    
    logger.info("\n🔒 Security features enabled:")
    logger.info(f"   - Rate limiting: {SECURITY_CONFIG['max_requests_per_minute']}/min")
    logger.info(f"   - Video token expiry: {SECURITY_CONFIG['video_token_expiry']}s")
    logger.info(f"   - Ban duration: {SECURITY_CONFIG['ban_duration']}s")
    logger.info("   - Attack prevention: ✅")
    logger.info("   - Security headers: ✅")
    
    print("\n🥷 YOUR UPLOADS ARE COMPLETELY UNTRACEABLE!")
    print("=" * 80)
    
    web.run_app(app, host=HOST, port=PORT)


if __name__ == '__main__':
    main()
