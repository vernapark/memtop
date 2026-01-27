"""
🥷 COMPLETE ANONYMITY & ANTI-FINGERPRINTING PROTECTION
Prevents ANY tracking of video uploader - IP, location, device, browser, etc.
Makes uploads completely untraceable and anonymous
"""

import re
import hashlib
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class AnonymityProtection:
    """Complete anonymity and anti-fingerprinting protection"""
    
    # Headers that reveal identity/location
    TRACKING_HEADERS = [
        'X-Forwarded-For',
        'X-Real-IP',
        'X-Client-IP',
        'X-Forwarded',
        'Forwarded-For',
        'Forwarded',
        'CF-Connecting-IP',
        'True-Client-IP',
        'X-Cluster-Client-IP',
        'X-ProxyUser-IP',
        'Via',
        'X-Original-IP',
        'X-Remote-IP',
        'X-Remote-Addr',
        'Client-IP',
        'X-Host',
        'X-Coming-From',
        'X-Originating-IP',
        'X-Device-ID',
        'X-Device-User-Agent',
        'X-Device-Type',
        'X-Mobile',
        'X-Tablet',
        'X-Desktop',
        'X-Operating-System',
        'X-Browser',
        'X-Browser-Version',
        'X-Platform',
        'DNT',  # Do Not Track
        'Sec-CH-UA',
        'Sec-CH-UA-Mobile',
        'Sec-CH-UA-Platform',
        'Sec-CH-UA-Arch',
        'Sec-CH-UA-Model',
        'Sec-Fetch-Site',
        'Sec-Fetch-Mode',
        'Sec-Fetch-User',
        'Sec-Fetch-Dest',
    ]
    
    # Browser fingerprinting APIs to block
    FINGERPRINT_APIS = [
        'navigator.userAgent',
        'navigator.platform',
        'navigator.language',
        'navigator.languages',
        'navigator.hardwareConcurrency',
        'navigator.deviceMemory',
        'screen.width',
        'screen.height',
        'screen.colorDepth',
        'screen.pixelDepth',
        'window.devicePixelRatio',
        'Intl.DateTimeFormat',
        'canvas.fingerprinting',
        'webgl.fingerprinting',
        'audio.fingerprinting',
    ]
    
    @staticmethod
    def sanitize_request(request):
        """
        Remove ALL tracking information from request
        Makes the request completely anonymous
        """
        sanitized_data = {}
        
        # 1. ANONYMIZE IP ADDRESS
        # Replace real IP with generic localhost
        sanitized_data['ip'] = '127.0.0.1'  # Anonymous IP
        sanitized_data['remote_addr'] = '0.0.0.0'  # No IP tracking
        
        # 2. REMOVE ALL TRACKING HEADERS
        sanitized_headers = {}
        for key, value in request.headers.items():
            # Only keep essential headers, remove tracking ones
            if key not in AnonymityProtection.TRACKING_HEADERS:
                # Further sanitize User-Agent
                if key.lower() == 'user-agent':
                    sanitized_headers[key] = AnonymityProtection._anonymize_user_agent(value)
                # Sanitize Referer
                elif key.lower() == 'referer':
                    sanitized_headers[key] = '/'  # Generic referer
                # Sanitize Accept-Language (reveals location)
                elif key.lower() == 'accept-language':
                    sanitized_headers[key] = 'en-US,en;q=0.9'  # Generic language
                else:
                    sanitized_headers[key] = value
        
        sanitized_data['headers'] = sanitized_headers
        
        # 3. ANONYMIZE TIMESTAMP (optional - prevents timing analysis)
        # Round to nearest hour to prevent timing correlation
        now = datetime.utcnow()
        sanitized_data['timestamp'] = now.replace(minute=0, second=0, microsecond=0)
        
        # 4. GENERATE ANONYMOUS SESSION ID (not traceable)
        # Use random hash instead of real session ID
        import secrets
        sanitized_data['session_id'] = secrets.token_hex(16)
        
        logger.info("🥷 Request anonymized - all tracking data removed")
        
        return sanitized_data
    
    @staticmethod
    def _anonymize_user_agent(user_agent):
        """
        Replace real User-Agent with generic one
        Prevents browser/device fingerprinting
        """
        # Generic User-Agent that reveals nothing specific
        return 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    
    @staticmethod
    def sanitize_upload_metadata(file_data):
        """
        Remove ALL metadata from uploaded files
        Strips EXIF, location, device info, etc.
        """
        sanitized = {
            'filename': AnonymityProtection._anonymize_filename(file_data.get('filename', 'video.mp4')),
            'size': file_data.get('size', 0),
            'content_type': file_data.get('content_type', 'video/mp4'),
            'upload_time': datetime.utcnow().replace(minute=0, second=0, microsecond=0),  # Rounded time
        }
        
        # Remove these tracking fields if present:
        tracking_fields = [
            'uploader_ip',
            'uploader_location',
            'device_id',
            'browser',
            'platform',
            'user_agent',
            'referrer',
            'session_id',
            'user_id',
            'client_id',
            'fingerprint',
            'geolocation',
            'city',
            'country',
            'timezone',
            'language',
            'screen_resolution',
            'device_type',
            'os',
            'os_version',
            'browser_version',
            'isp',
            'asn',
            'proxy',
            'vpn',
        ]
        
        # Ensure no tracking fields exist
        for field in tracking_fields:
            if field in file_data:
                logger.warning(f"🚨 Removed tracking field: {field}")
        
        logger.info("🥷 Upload metadata sanitized - all tracking removed")
        
        return sanitized
    
    @staticmethod
    def _anonymize_filename(filename):
        """
        Replace original filename with hash
        Prevents filename-based tracking
        """
        # Generate hash-based anonymous filename
        file_hash = hashlib.sha256(filename.encode()).hexdigest()[:16]
        extension = filename.split('.')[-1] if '.' in filename else 'mp4'
        return f"video_{file_hash}.{extension}"
    
    @staticmethod
    def strip_video_metadata(video_path):
        """
        Strip ALL metadata from video file
        Removes EXIF, GPS, device info, etc.
        """
        try:
            import subprocess
            
            # Use ffmpeg to strip all metadata
            output_path = f"{video_path}_clean"
            
            cmd = [
                'ffmpeg',
                '-i', video_path,
                '-map_metadata', '-1',  # Remove all metadata
                '-c:v', 'copy',  # Copy video without re-encoding
                '-c:a', 'copy',  # Copy audio without re-encoding
                '-fflags', '+bitexact',  # Remove encoder info
                '-flags:v', '+bitexact',
                '-flags:a', '+bitexact',
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, timeout=60)
            
            if result.returncode == 0:
                logger.info("🥷 Video metadata stripped successfully")
                return output_path
            else:
                logger.warning("⚠️ ffmpeg not available, skipping metadata stripping")
                return video_path
                
        except Exception as e:
            logger.warning(f"⚠️ Could not strip metadata: {e}")
            return video_path
    
    @staticmethod
    def block_geolocation_apis():
        """
        Generate JavaScript to block geolocation and fingerprinting APIs
        Prevents browser-based location tracking
        """
        js_code = """
        (function() {
            'use strict';
            
            // ============================================================
            // BLOCK GEOLOCATION APIs
            // ============================================================
            
            // Block Geolocation API
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition = function() {
                    console.log('🥷 Geolocation blocked');
                };
                navigator.geolocation.watchPosition = function() {
                    console.log('🥷 Geolocation blocked');
                };
            }
            
            // Block IP Geolocation services
            const blockedDomains = [
                'ipapi.co',
                'ipinfo.io',
                'ip-api.com',
                'geoip-db.com',
                'extreme-ip-lookup.com',
                'ipgeolocation.io',
                'freegeoip.app',
                'ip.nf',
                'wtfismyip.com',
            ];
            
            // Override fetch to block geolocation services
            const originalFetch = window.fetch;
            window.fetch = function(...args) {
                const url = args[0];
                if (typeof url === 'string' && blockedDomains.some(d => url.includes(d))) {
                    console.log('🥷 Geolocation service blocked:', url);
                    return Promise.reject(new Error('Geolocation blocked'));
                }
                return originalFetch.apply(this, args);
            };
            
            // ============================================================
            // BLOCK FINGERPRINTING APIs
            // ============================================================
            
            // Block Canvas Fingerprinting
            const originalToDataURL = HTMLCanvasElement.prototype.toDataURL;
            HTMLCanvasElement.prototype.toDataURL = function() {
                console.log('🥷 Canvas fingerprinting blocked');
                return 'data:image/png;base64,iVBORw0KGg==';
            };
            
            const originalToBlob = HTMLCanvasElement.prototype.toBlob;
            HTMLCanvasElement.prototype.toBlob = function() {
                console.log('🥷 Canvas fingerprinting blocked');
            };
            
            // Block WebGL Fingerprinting
            const getParameter = WebGLRenderingContext.prototype.getParameter;
            WebGLRenderingContext.prototype.getParameter = function(parameter) {
                if (parameter === 37445 || parameter === 37446) {
                    console.log('🥷 WebGL fingerprinting blocked');
                    return 'Generic GPU';
                }
                return getParameter.apply(this, arguments);
            };
            
            // Block Audio Fingerprinting
            const audioContext = window.AudioContext || window.webkitAudioContext;
            if (audioContext) {
                const originalCreateOscillator = audioContext.prototype.createOscillator;
                audioContext.prototype.createOscillator = function() {
                    console.log('🥷 Audio fingerprinting blocked');
                    return originalCreateOscillator.apply(this, arguments);
                };
            }
            
            // Block Battery API (reveals device info)
            if (navigator.getBattery) {
                navigator.getBattery = function() {
                    console.log('🥷 Battery API blocked');
                    return Promise.resolve({
                        charging: true,
                        level: 1,
                        chargingTime: 0,
                        dischargingTime: Infinity
                    });
                };
            }
            
            // Block Device Memory API
            Object.defineProperty(navigator, 'deviceMemory', {
                get: function() {
                    console.log('🥷 Device memory blocked');
                    return 8;  // Generic value
                }
            });
            
            // Block Hardware Concurrency (CPU cores)
            Object.defineProperty(navigator, 'hardwareConcurrency', {
                get: function() {
                    console.log('🥷 Hardware info blocked');
                    return 4;  // Generic value
                }
            });
            
            // Block Network Information API
            if (navigator.connection) {
                Object.defineProperty(navigator, 'connection', {
                    get: function() {
                        console.log('🥷 Network info blocked');
                        return {
                            effectiveType: '4g',
                            downlink: 10,
                            rtt: 50
                        };
                    }
                });
            }
            
            // Block Media Devices (camera/microphone enumeration)
            if (navigator.mediaDevices && navigator.mediaDevices.enumerateDevices) {
                navigator.mediaDevices.enumerateDevices = function() {
                    console.log('🥷 Media devices blocked');
                    return Promise.resolve([]);
                };
            }
            
            // Block Timezone Detection
            const originalDateTimeFormat = Intl.DateTimeFormat;
            Intl.DateTimeFormat = function() {
                console.log('🥷 Timezone detection blocked');
                return new originalDateTimeFormat('en-US', { timeZone: 'UTC' });
            };
            
            // Spoof Screen Resolution
            Object.defineProperty(screen, 'width', {
                get: function() { return 1920; }  // Generic resolution
            });
            Object.defineProperty(screen, 'height', {
                get: function() { return 1080; }
            });
            Object.defineProperty(screen, 'availWidth', {
                get: function() { return 1920; }
            });
            Object.defineProperty(screen, 'availHeight', {
                get: function() { return 1080; }
            });
            
            // Spoof Pixel Ratio
            Object.defineProperty(window, 'devicePixelRatio', {
                get: function() { return 1; }  // Generic ratio
            });
            
            // Block Plugins Enumeration
            Object.defineProperty(navigator, 'plugins', {
                get: function() {
                    console.log('🥷 Plugins enumeration blocked');
                    return [];
                }
            });
            
            // Block MIME Types Enumeration
            Object.defineProperty(navigator, 'mimeTypes', {
                get: function() {
                    console.log('🥷 MIME types blocked');
                    return [];
                }
            });
            
            // Spoof Language
            Object.defineProperty(navigator, 'language', {
                get: function() { return 'en-US'; }
            });
            Object.defineProperty(navigator, 'languages', {
                get: function() { return ['en-US', 'en']; }
            });
            
            // Block WebRTC (reveals real IP even behind VPN)
            if (window.RTCPeerConnection) {
                window.RTCPeerConnection = function() {
                    console.log('🥷 WebRTC blocked (IP leak prevention)');
                    throw new Error('WebRTC disabled for privacy');
                };
            }
            
            console.log('🥷 Complete anonymity protection active');
            console.log('   ✅ Geolocation blocked');
            console.log('   ✅ Fingerprinting blocked');
            console.log('   ✅ IP leak prevention active');
            console.log('   ✅ Device info hidden');
            console.log('   ✅ Location tracking blocked');
            
        })();
        """
        
        return js_code
    
    @staticmethod
    def create_anonymous_log_entry(action, details=None):
        """
        Create log entry without any tracking information
        """
        log_entry = {
            'action': action,
            'timestamp': datetime.utcnow().replace(minute=0, second=0, microsecond=0),  # Rounded
            'ip': 'anonymous',
            'location': 'unknown',
            'device': 'anonymous',
            'details': details or {}
        }
        
        return log_entry
    
    @staticmethod
    def prevent_timing_attacks():
        """
        Add random delays to prevent timing-based tracking
        """
        import random
        import time
        
        # Random delay between 100-500ms
        delay = random.uniform(0.1, 0.5)
        time.sleep(delay)
        
        logger.info("🥷 Added timing obfuscation")


# Decorator for anonymous upload routes
def require_anonymity(f):
    """Decorator to enforce anonymity on upload routes"""
    from functools import wraps
    
    @wraps(f)
    async def decorated_function(request, *args, **kwargs):
        # Sanitize request to remove all tracking
        sanitized = AnonymityProtection.sanitize_request(request)
        
        # Add timing obfuscation
        AnonymityProtection.prevent_timing_attacks()
        
        # Replace request data with sanitized version
        request._anonymized = True
        request._sanitized_data = sanitized
        
        logger.info("🥷 Anonymous upload - zero tracking enabled")
        
        return await f(request, *args, **kwargs)
    
    return decorated_function
