"""
Security Headers Middleware - Fixes "Dangerous Site" Browser Warnings
Adds comprehensive security headers to prevent browser security warnings
"""
from aiohttp import web

@web.middleware
async def security_headers_middleware(request, handler):
    """Add comprehensive security headers to all responses"""
    response = await handler(request)
    
    # Prevent MIME type sniffing attacks
    response.headers['X-Content-Type-Options'] = 'nosniff'
    
    # Prevent clickjacking attacks
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    
    # Enable XSS protection
    response.headers['X-XSS-Protection'] = '1; mode=block'
    
    # Control referrer information
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    
    # Content Security Policy - CRITICAL for preventing "dangerous site" warnings
    # This tells browsers what content sources are allowed
    csp_directives = [
        "default-src 'self'",
        "script-src 'self' 'unsafe-inline' 'unsafe-eval'",  # Allow inline scripts (needed for current code)
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
        "font-src 'self' https://fonts.gstatic.com data:",
        "img-src 'self' data: blob: https:",
        "media-src 'self' blob: https: data:",
        "connect-src 'self' https: wss:",
        "frame-ancestors 'self'",
        "base-uri 'self'",
        "form-action 'self'",
        "object-src 'none'",
        "upgrade-insecure-requests"  # Upgrade HTTP to HTTPS automatically
    ]
    response.headers['Content-Security-Policy'] = "; ".join(csp_directives)
    
    # Strict Transport Security - Only for HTTPS
    if request.scheme == 'https':
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains; preload'
    
    # Permissions Policy - Restrict dangerous browser features
    permissions = [
        "camera=()",
        "microphone=()",
        "geolocation=()",
        "payment=()",
        "usb=()",
        "magnetometer=()",
        "gyroscope=()",
        "accelerometer=()",
        "interest-cohort=()"  # Disable FLoC tracking
    ]
    response.headers['Permissions-Policy'] = ", ".join(permissions)
    
    # Cross-Origin policies
    response.headers['Cross-Origin-Embedder-Policy'] = 'require-corp'
    response.headers['Cross-Origin-Opener-Policy'] = 'same-origin'
    response.headers['Cross-Origin-Resource-Policy'] = 'same-origin'
    
    return response

@web.middleware
async def cors_middleware(request, handler):
    """Handle CORS for API requests"""
    if request.method == 'OPTIONS':
        response = web.Response()
    else:
        response = await handler(request)
    
    # Allow same-origin requests
    response.headers['Access-Control-Allow-Origin'] = request.headers.get('Origin', '*')
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    response.headers['Access-Control-Max-Age'] = '3600'
    
    return response
