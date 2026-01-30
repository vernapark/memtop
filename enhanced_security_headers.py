"""
ENHANCED Security Headers - Makes Site Look 100% Legitimate to Browsers
This adds all the trust signals that major legitimate websites have
"""
from aiohttp import web

@web.middleware
async def enhanced_security_middleware(request, handler):
    """Add comprehensive security headers + legitimacy signals to all responses"""
    response = await handler(request)
    
    # ============================================================================
    # STANDARD SECURITY HEADERS (Prevent attacks)
    # ============================================================================
    
    # Prevent MIME type sniffing attacks
    response.headers['X-Content-Type-Options'] = 'nosniff'
    
    # Prevent clickjacking attacks
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    
    # Enable XSS protection
    response.headers['X-XSS-Protection'] = '1; mode=block'
    
    # Control referrer information
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    
    # ============================================================================
    # LEGITIMACY SIGNALS (Make browsers trust the site)
    # ============================================================================
    
    # Server identification (looks professional)
    response.headers['Server'] = 'VideoStream/2.0 (Professional Streaming Platform)'
    
    # Cache control for better performance (legitimate sites optimize)
    if request.path.endswith(('.css', '.js', '.png', '.jpg', '.jpeg', '.svg', '.woff', '.woff2')):
        response.headers['Cache-Control'] = 'public, max-age=31536000, immutable'
    elif request.path.endswith('.html'):
        response.headers['Cache-Control'] = 'no-cache, must-revalidate'
    
    # Security policy reporting (shows active security monitoring)
    response.headers['Report-To'] = '{"group":"default","max_age":31536000,"endpoints":[{"url":"https://sixy54u9329u4e35-936854r84k30djfrk93w9s9.onrender.com/api/security-report"}]}'
    
    # ============================================================================
    # CONTENT SECURITY POLICY (Critical for legitimacy)
    # ============================================================================
    
    csp_directives = [
        "default-src 'self'",
        "script-src 'self' 'unsafe-inline' 'unsafe-eval'",
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
        "font-src 'self' https://fonts.gstatic.com data:",
        "img-src 'self' data: blob: https:",
        "media-src 'self' blob: https: data:",
        "connect-src 'self' https: wss:",
        "frame-ancestors 'self'",
        "base-uri 'self'",
        "form-action 'self'",
        "object-src 'none'",
        "upgrade-insecure-requests"
    ]
    response.headers['Content-Security-Policy'] = "; ".join(csp_directives)
    
    # Strict Transport Security - Only for HTTPS
    if request.scheme == 'https':
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains; preload'
    
    # ============================================================================
    # PERMISSIONS POLICY (Shows responsible feature usage)
    # ============================================================================
    
    permissions = [
        "accelerometer=()",
        "ambient-light-sensor=()",
        "autoplay=(self)",
        "battery=()",
        "camera=()",
        "display-capture=()",
        "document-domain=()",
        "encrypted-media=(self)",
        "fullscreen=(self)",
        "geolocation=()",
        "gyroscope=()",
        "interest-cohort=()",  # Disable FLoC tracking
        "magnetometer=()",
        "microphone=()",
        "midi=()",
        "payment=()",
        "picture-in-picture=(self)",
        "publickey-credentials-get=()",
        "usb=()",
        "wake-lock=()",
        "xr-spatial-tracking=()"
    ]
    response.headers['Permissions-Policy'] = ", ".join(permissions)
    
    # ============================================================================
    # CROSS-ORIGIN POLICIES (Enterprise-level isolation)
    # ============================================================================
    
    # Relax COEP for compatibility while maintaining security
    response.headers['Cross-Origin-Embedder-Policy'] = 'unsafe-none'
    response.headers['Cross-Origin-Opener-Policy'] = 'same-origin-allow-popups'
    response.headers['Cross-Origin-Resource-Policy'] = 'cross-origin'
    
    # ============================================================================
    # BUSINESS & TRUST INDICATORS
    # ============================================================================
    
    # Professional platform identifier
    response.headers['X-Platform'] = 'VideoStream Professional'
    response.headers['X-Service-Type'] = 'Enterprise Video Management'
    
    # API version (shows active development)
    response.headers['X-API-Version'] = '2.0.1'
    
    # Powered by header (looks professional)
    response.headers['X-Powered-By'] = 'Python/aiohttp Professional Framework'
    
    # Content type declaration (proper standards compliance)
    if not response.headers.get('Content-Type'):
        if request.path.endswith('.html'):
            response.headers['Content-Type'] = 'text/html; charset=utf-8'
        elif request.path.endswith('.json'):
            response.headers['Content-Type'] = 'application/json; charset=utf-8'
    
    return response

@web.middleware
async def professional_cors_middleware(request, handler):
    """Handle CORS professionally like major platforms"""
    if request.method == 'OPTIONS':
        response = web.Response()
    else:
        response = await handler(request)
    
    # Professional CORS headers
    origin = request.headers.get('Origin', '*')
    response.headers['Access-Control-Allow-Origin'] = origin
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS, HEAD'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With, Accept, Origin'
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    response.headers['Access-Control-Max-Age'] = '86400'  # 24 hours
    response.headers['Access-Control-Expose-Headers'] = 'Content-Length, X-API-Version, X-Platform'
    
    return response
