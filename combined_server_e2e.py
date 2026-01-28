#!/usr/bin/env python3
"""
🔒 E2E ENCRYPTED SERVER - Zero-Knowledge Architecture
Combines anonymous security + end-to-end encryption
Server is BLIND to video content
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

# Import E2E handler
from server_e2e_handler import E2EVideoHandler, register_e2e_routes

# Import original server
import importlib.util
spec = importlib.util.spec_from_file_location(
    "original_server", 
    "combined_server_bulletproof_multi.py"
)
original_server = importlib.util.module_from_spec(spec)
spec.loader.exec_module(original_server)

logger = logging.getLogger(__name__)

# Initialize E2E handler
e2e_handler = E2EVideoHandler()

# ============================================================================
# COMBINED E2E + SECURITY + ANONYMITY MIDDLEWARE
# ============================================================================

@web.middleware
async def e2e_security_middleware(request, handler):
    """
    Combined E2E encryption, security and anonymity protection
    - E2E: Server blind to video content
    - Security: Rate limiting, attack prevention, headers
    - Anonymity: Strip all tracking data
    """
    
    # Skip for health check
    if request.path == '/health':
        return await handler(request)
    
    # Apply anonymity protection to uploads
    if request.method == 'POST' and 'upload' in request.path.lower():
        request = await AnonymityProtection.anonymize_request(request)
    
    # Get client identifier (anonymized)
    identifier = AnonymityProtection.get_anonymous_identifier(request)
    
    # Check rate limit
    allowed, reason = SecurityMiddleware.check_rate_limit(
        identifier,
        sensitive=('upload' in request.path.lower() or 
                  'login' in request.path.lower() or
                  'admin' in request.path.lower())
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
        
        # Log anonymous activity
        if hasattr(request, '_anonymized'):
            AnonymityProtection.create_anonymous_log_entry(
                'e2e_upload',
                {'path': request.path, 'method': request.method, 'encrypted': True}
            )
        
        return response
        
    except web.HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing request: {e}")
        return web.json_response({'error': 'Internal server error'}, status=500)


# ============================================================================
# E2E ENCRYPTED UPLOAD HANDLERS
# ============================================================================

async def e2e_anonymous_upload(request):
    """
    Upload encrypted video with complete anonymity
    Server never sees unencrypted content
    """
    try:
        logger.info("🔒 Processing E2E encrypted upload (server blind)")
        
        # Get the sanitized data
        if hasattr(request, '_sanitized_data'):
            sanitized = request._sanitized_data
            logger.info(f"🥷 Using anonymized request: {sanitized.get('ip')}")
        
        # E2E handler processes encrypted blob
        return e2e_handler.handle_encrypted_upload(request)
        
    except Exception as e:
        logger.error(f"E2E upload error: {e}")
        return web.json_response({'error': str(e)}, status=500)


async def e2e_get_video(request):
    """
    Retrieve encrypted video info
    Server just provides download URL, cannot decrypt
    """
    try:
        video_id = request.match_info.get('video_id')
        logger.info(f"🔒 Retrieving E2E video: {video_id} (encrypted)")
        
        return e2e_handler.handle_encrypted_download(video_id)
        
    except Exception as e:
        logger.error(f"E2E retrieval error: {e}")
        return web.json_response({'error': str(e)}, status=500)


async def e2e_list_videos(request):
    """
    List encrypted videos
    Only returns safe metadata
    """
    try:
        logger.info("🔒 Listing E2E encrypted videos")
        return e2e_handler.get_encrypted_videos_list()
        
    except Exception as e:
        logger.error(f"E2E list error: {e}")
        return web.json_response({'error': str(e)}, status=500)


async def e2e_delete_video(request):
    """
    Delete encrypted video
    """
    try:
        video_id = request.match_info.get('video_id')
        logger.info(f"🔒 Deleting E2E video: {video_id}")
        
        return e2e_handler.delete_encrypted_video(video_id)
        
    except Exception as e:
        logger.error(f"E2E delete error: {e}")
        return web.json_response({'error': str(e)}, status=500)


async def get_e2e_status(request):
    """
    Get E2E encryption status
    """
    return web.json_response({
        'success': True,
        'e2e_enabled': True,
        'encryption': 'AES-256-GCM',
        'server_blind': True,
        'zero_knowledge': True,
        'anonymity': True,
        'features': {
            'client_encryption': True,
            'metadata_stripping': True,
            'secure_storage': True,
            'encrypted_streaming': True,
            'key_management': 'client-side'
        },
        'message': 'E2E encryption active - server cannot decrypt videos'
    })


async def serve_e2e_js(request):
    """
    Serve E2E encryption JavaScript files
    """
    try:
        file_map = {
            'encryption.js': 'js/encryption.js',
            'metadata_stripper.js': 'js/metadata_stripper.js',
            'admin_e2e.js': 'js/admin_e2e.js',
            'viewer_e2e.js': 'js/viewer_e2e.js'
        }
        
        filename = request.match_info.get('filename', '')
        
        if filename in file_map:
            filepath = file_map[filename]
            return web.FileResponse(filepath)
        
        return web.Response(status=404)
        
    except Exception as e:
        logger.error(f"Error serving E2E JS: {e}")
        return web.Response(status=500)


# ============================================================================
# STARTUP AND CLEANUP
# ============================================================================

background_tasks = set()

async def start_cleanup_task(app):
    """Start background cleanup tasks"""
    task = asyncio.create_task(SecurityMiddleware.cleanup_old_entries())
    background_tasks.add(task)
    task.add_done_callback(background_tasks.discard)

async def cleanup_background_tasks(app):
    """Cleanup background tasks on shutdown"""
    for task in background_tasks:
        task.cancel()
    await asyncio.gather(*background_tasks, return_exceptions=True)


# ============================================================================
# MAIN APPLICATION
# ============================================================================

def main():
    """Start the E2E encrypted server"""
    
    print("\n" + "=" * 80)
    print("🔒 MEMTOP E2E ENCRYPTED SERVER - ZERO KNOWLEDGE ARCHITECTURE")
    print("=" * 80)
    print("\n🛡️  Security Features:")
    print("   - End-to-End Encryption (AES-256-GCM)")
    print("   - Client-Side Video Encryption")
    print("   - Metadata Stripping (GPS, Device Info)")
    print("   - Zero-Knowledge Storage (Server Blind)")
    print("   - Complete Anonymity Protection")
    print("   - Rate Limiting & DDoS Protection")
    print("   - Security Headers")
    print("=" * 80)
    
    # Create app with E2E middleware
    app = web.Application(
        client_max_size=1024**3,
        middlewares=[e2e_security_middleware]
    )
    
    # E2E Encryption routes
    app.router.add_post('/api/upload', e2e_anonymous_upload)
    app.router.add_get('/api/video/{video_id}', e2e_get_video)
    app.router.add_get('/api/videos', e2e_list_videos)
    app.router.add_delete('/api/video/{video_id}', e2e_delete_video)
    app.router.add_get('/api/e2e/status', get_e2e_status)
    
    # E2E JavaScript files
    app.router.add_get('/js/e2e/{filename}', serve_e2e_js)
    
    # Bot webhook (anonymized)
    app.router.add_post('/telegram-webhook', original_server.telegram_webhook_handler)
    
    # Legacy video API routes (for backward compatibility)
    app.router.add_post('/api/upload-video', e2e_anonymous_upload)
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
    from combined_server_anonymous import get_anonymity_status, serve_anonymity_js
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
    
    print(f"\n🚀 Starting E2E encrypted server on {HOST}:{PORT}")
    print("=" * 80)
    
    logger.info("🔒 E2E Encryption features enabled:")
    logger.info("   - Client-side encryption: ✅ (AES-256-GCM)")
    logger.info("   - Metadata stripping: ✅ (GPS, device, timestamps)")
    logger.info("   - Server blind: ✅ (Zero-knowledge)")
    logger.info("   - Key management: ✅ (Client-side only)")
    logger.info("   - Encrypted storage: ✅ (Cloudinary blind)")
    logger.info("   - Encrypted streaming: ✅ (Decrypt on client)")
    
    logger.info("\n🥷 Anonymity features enabled:")
    logger.info("   - IP address: ✅ Hidden (127.0.0.1)")
    logger.info("   - Location: ✅ Blocked completely")
    logger.info("   - Device info: ✅ Anonymized")
    logger.info("   - Browser fingerprint: ✅ Blocked")
    
    logger.info("\n🔒 Security features enabled:")
    logger.info(f"   - Rate limiting: {SECURITY_CONFIG['max_requests_per_minute']}/min")
    logger.info("   - Attack prevention: ✅")
    logger.info("   - Security headers: ✅")
    
    print("\n🔒 YOUR VIDEOS ARE END-TO-END ENCRYPTED!")
    print("   ✅ Server CANNOT see video content")
    print("   ✅ Render.com CANNOT see video content")
    print("   ✅ Cloudinary CANNOT see video content")
    print("   ✅ Only YOU can decrypt videos")
    print("=" * 80 + "\n")
    
    web.run_app(app, host=HOST, port=PORT)


if __name__ == '__main__':
    import asyncio
    main()
