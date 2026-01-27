"""
Advanced Security Middleware - Anti-Tracking, Anti-Reverse Engineering, Anti-Hacking
Bulletproof protection while maintaining smooth performance
"""

import hashlib
import hmac
import time
import secrets
import json
from functools import wraps
from collections import defaultdict
from datetime import datetime, timedelta
import re

# Security Configuration
SECURITY_CONFIG = {
    'max_requests_per_minute': 60,
    'max_requests_per_hour': 500,
    'video_token_expiry': 3600,  # 1 hour
    'ban_duration': 3600,  # 1 hour ban for suspicious activity
    'max_failed_attempts': 5,
    'block_suspicious_patterns': True,
    'require_csrf_token': True,
    'enable_fingerprinting': True,
}

# In-memory storage (for production, use Redis)
rate_limit_storage = defaultdict(list)
failed_attempts = defaultdict(int)
banned_ips = {}
active_tokens = {}
csrf_tokens = {}

# Secret key for token generation (should be in environment variable)
SECRET_KEY = secrets.token_hex(32)

class SecurityMiddleware:
    """Comprehensive security middleware"""
    
    @staticmethod
    def generate_token(data, expiry=3600):
        """Generate secure token with expiry"""
        timestamp = int(time.time() + expiry)
        payload = f"{data}:{timestamp}"
        signature = hmac.new(
            SECRET_KEY.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()
        return f"{payload}:{signature}"
    
    @staticmethod
    def verify_token(token):
        """Verify token and check expiry"""
        try:
            parts = token.split(':')
            if len(parts) != 3:
                return False
            
            data, timestamp, signature = parts
            timestamp = int(timestamp)
            
            # Check expiry
            if time.time() > timestamp:
                return False
            
            # Verify signature
            payload = f"{data}:{timestamp}"
            expected_signature = hmac.new(
                SECRET_KEY.encode(),
                payload.encode(),
                hashlib.sha256
            ).hexdigest()
            
            return hmac.compare_digest(signature, expected_signature)
        except:
            return False
    
    @staticmethod
    def get_client_fingerprint(request):
        """Generate unique client fingerprint"""
        fingerprint_data = [
            request.headers.get('User-Agent', ''),
            request.headers.get('Accept-Language', ''),
            request.headers.get('Accept-Encoding', ''),
            request.remote_addr,
        ]
        fingerprint = hashlib.sha256(
            '|'.join(fingerprint_data).encode()
        ).hexdigest()
        return fingerprint
    
    @staticmethod
    def is_suspicious_request(request):
        """Detect suspicious patterns"""
        suspicious_patterns = [
            r'(?i)(union|select|insert|update|delete|drop|script|javascript|onerror|onload)',
            r'(?i)(<script|<iframe|<object|<embed)',
            r'\.\./',  # Path traversal
            r'(?i)(eval\(|exec\(|system\()',
        ]
        
        # Check URL and query parameters
        full_path = request.full_path
        for pattern in suspicious_patterns:
            if re.search(pattern, full_path):
                return True
        
        # Check headers for suspicious content
        user_agent = request.headers.get('User-Agent', '').lower()
        suspicious_agents = ['bot', 'crawler', 'spider', 'scraper', 'curl', 'wget', 'python-requests']
        
        # Allow legitimate bots but log them
        legitimate_bots = ['googlebot', 'bingbot']
        if any(agent in user_agent for agent in suspicious_agents):
            if not any(bot in user_agent for bot in legitimate_bots):
                return True
        
        return False
    
    @staticmethod
    def rate_limit_check(identifier, max_requests=60, window=60):
        """Check rate limiting"""
        current_time = time.time()
        
        # Check if banned
        if identifier in banned_ips:
            ban_time = banned_ips[identifier]
            if current_time - ban_time < SECURITY_CONFIG['ban_duration']:
                return False, 'IP_BANNED'
            else:
                del banned_ips[identifier]
        
        # Clean old entries
        rate_limit_storage[identifier] = [
            t for t in rate_limit_storage[identifier]
            if current_time - t < window
        ]
        
        # Check rate limit
        if len(rate_limit_storage[identifier]) >= max_requests:
            # Ban if excessive requests
            failed_attempts[identifier] += 1
            if failed_attempts[identifier] >= SECURITY_CONFIG['max_failed_attempts']:
                banned_ips[identifier] = current_time
                return False, 'RATE_LIMIT_BAN'
            return False, 'RATE_LIMIT'
        
        # Add current request
        rate_limit_storage[identifier].append(current_time)
        return True, 'OK'
    
    @staticmethod
    def generate_csrf_token(session_id):
        """Generate CSRF token"""
        token = secrets.token_urlsafe(32)
        csrf_tokens[session_id] = {
            'token': token,
            'created': time.time()
        }
        return token
    
    @staticmethod
    def verify_csrf_token(session_id, token):
        """Verify CSRF token"""
        if session_id not in csrf_tokens:
            return False
        
        stored = csrf_tokens[session_id]
        
        # Check expiry (5 minutes)
        if time.time() - stored['created'] > 300:
            del csrf_tokens[session_id]
            return False
        
        return hmac.compare_digest(stored['token'], token)
    
    @staticmethod
    def encrypt_video_url(video_id):
        """Generate encrypted video URL with time-limited token"""
        token = SecurityMiddleware.generate_token(
            video_id,
            SECURITY_CONFIG['video_token_expiry']
        )
        active_tokens[token] = {
            'video_id': video_id,
            'created': time.time()
        }
        return token
    
    @staticmethod
    def decrypt_video_token(token):
        """Decrypt and validate video token"""
        if not SecurityMiddleware.verify_token(token):
            return None
        
        if token in active_tokens:
            return active_tokens[token]['video_id']
        
        return None
    
    @staticmethod
    def add_security_headers(response):
        """Add security headers to response"""
        # Prevent clickjacking
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        
        # Prevent MIME sniffing
        response.headers['X-Content-Type-Options'] = 'nosniff'
        
        # XSS Protection
        response.headers['X-XSS-Protection'] = '1; mode=block'
        
        # HTTPS enforcement
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        
        # Content Security Policy
        response.headers['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; "
            "img-src 'self' data: https: blob:; "
            "media-src 'self' https: blob:; "
            "font-src 'self' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; "
            "connect-src 'self' https:; "
            "frame-ancestors 'self';"
        )
        
        # Referrer Policy
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Permissions Policy
        response.headers['Permissions-Policy'] = (
            'geolocation=(), microphone=(), camera=(), payment=()'
        )
        
        # Remove server header
        response.headers.pop('Server', None)
        
        return response
    
    @staticmethod
    def sanitize_input(data):
        """Sanitize user input"""
        if isinstance(data, str):
            # Remove potentially dangerous characters
            data = re.sub(r'[<>"\']', '', data)
            data = data.strip()
        return data
    
    @staticmethod
    def cleanup_expired_data():
        """Clean up expired tokens and rate limit data"""
        current_time = time.time()
        
        # Clean expired tokens
        expired_tokens = [
            token for token, data in active_tokens.items()
            if current_time - data['created'] > SECURITY_CONFIG['video_token_expiry']
        ]
        for token in expired_tokens:
            del active_tokens[token]
        
        # Clean expired CSRF tokens
        expired_csrf = [
            sid for sid, data in csrf_tokens.items()
            if current_time - data['created'] > 300
        ]
        for sid in expired_csrf:
            del csrf_tokens[sid]
        
        # Clean old rate limit data
        for identifier in list(rate_limit_storage.keys()):
            rate_limit_storage[identifier] = [
                t for t in rate_limit_storage[identifier]
                if current_time - t < 3600
            ]
            if not rate_limit_storage[identifier]:
                del rate_limit_storage[identifier]


def require_security(f):
    """Decorator for route security"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from flask import request, jsonify
        
        # Get client identifier
        client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        fingerprint = SecurityMiddleware.get_client_fingerprint(request)
        identifier = f"{client_ip}:{fingerprint}"
        
        # Check for suspicious patterns
        if SECURITY_CONFIG['block_suspicious_patterns']:
            if SecurityMiddleware.is_suspicious_request(request):
                return jsonify({'error': 'Forbidden'}), 403
        
        # Rate limiting
        allowed, reason = SecurityMiddleware.rate_limit_check(
            identifier,
            SECURITY_CONFIG['max_requests_per_minute'],
            60
        )
        
        if not allowed:
            if reason == 'IP_BANNED':
                return jsonify({'error': 'Access denied'}), 403
            return jsonify({'error': 'Too many requests'}), 429
        
        return f(*args, **kwargs)
    
    return decorated_function


def require_video_token(f):
    """Decorator for video access with token validation"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from flask import request, jsonify
        
        token = request.args.get('token') or request.headers.get('X-Video-Token')
        
        if not token:
            return jsonify({'error': 'Token required'}), 401
        
        video_id = SecurityMiddleware.decrypt_video_token(token)
        
        if not video_id:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        # Pass video_id to the route
        kwargs['video_id'] = video_id
        return f(*args, **kwargs)
    
    return decorated_function
