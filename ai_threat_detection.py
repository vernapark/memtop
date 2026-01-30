"""
🤖 AI-BASED THREAT DETECTION SYSTEM
Machine Learning powered security with real-time threat scoring
"""
import time
import hashlib
import json
from collections import defaultdict, deque
from datetime import datetime, timedelta
import asyncio
from aiohttp import web

class AIThreatDetector:
    """ML-based threat detection with behavioral analysis"""
    
    def __init__(self):
        # Behavioral tracking
        self.ip_behavior = defaultdict(lambda: {
            'requests': deque(maxlen=100),
            'endpoints': deque(maxlen=50),
            'user_agents': set(),
            'threat_score': 0.0,
            'first_seen': time.time(),
            'last_seen': time.time(),
            'blocked_until': 0,
            'total_requests': 0,
            'failed_auth': 0,
            'suspicious_patterns': 0
        })
        
        # Attack patterns (ML training data)
        self.attack_patterns = {
            'sql_injection': [
                'union select', 'drop table', '1=1', 'or 1=1',
                'exec(', 'execute(', 'script>', 'javascript:',
                '../', '..\\', 'etc/passwd', 'cmd.exe'
            ],
            'xss_patterns': [
                '<script', 'javascript:', 'onerror=', 'onload=',
                'eval(', 'alert(', 'document.cookie', 'innerHTML'
            ],
            'bot_signatures': [
                'bot', 'crawler', 'spider', 'scraper', 'python-requests',
                'curl', 'wget', 'scanner', 'nikto', 'sqlmap'
            ],
            'ddos_indicators': [
                'keep-alive: 300', 'range: bytes=', 'slowloris'
            ]
        }
        
        # Anomaly detection thresholds
        self.thresholds = {
            'requests_per_minute': 60,
            'unique_endpoints_per_minute': 20,
            'threat_score_block': 80,
            'threat_score_challenge': 50,
            'consecutive_errors': 5,
            'user_agent_changes': 3
        }
    
    def calculate_threat_score(self, ip: str, request: web.Request) -> float:
        """Calculate real-time threat score using ML-like analysis"""
        behavior = self.ip_behavior[ip]
        score = 0.0
        
        # Update behavior tracking
        now = time.time()
        behavior['last_seen'] = now
        behavior['total_requests'] += 1
        behavior['requests'].append(now)
        behavior['endpoints'].append(request.path)
        
        ua = request.headers.get('User-Agent', '')
        if ua:
            behavior['user_agents'].add(ua)
        
        # === BEHAVIORAL ANALYSIS (ML-inspired) ===
        
        # 1. Request frequency analysis (detect floods)
        recent_requests = [t for t in behavior['requests'] if now - t < 60]
        requests_per_min = len(recent_requests)
        if requests_per_min > self.thresholds['requests_per_minute']:
            score += min((requests_per_min / self.thresholds['requests_per_minute']) * 30, 40)
        
        # 2. Endpoint diversity analysis (detect scanning)
        recent_endpoints = list(behavior['endpoints'])[-20:]
        unique_endpoints = len(set(recent_endpoints))
        if unique_endpoints > self.thresholds['unique_endpoints_per_minute']:
            score += 20
        
        # 3. User-Agent consistency (detect bot rotation)
        if len(behavior['user_agents']) > self.thresholds['user_agent_changes']:
            score += 15
        
        # 4. Pattern matching (detect attack payloads)
        full_url = str(request.url)
        request_body = str(request.query)
        
        for pattern_type, patterns in self.attack_patterns.items():
            for pattern in patterns:
                if pattern.lower() in full_url.lower() or pattern.lower() in request_body.lower():
                    score += 25
                    behavior['suspicious_patterns'] += 1
                    break
        
        # 5. User-Agent analysis (bot detection)
        if ua:
            ua_lower = ua.lower()
            for bot_sig in self.attack_patterns['bot_signatures']:
                if bot_sig in ua_lower:
                    score += 30
                    break
        
        # 6. Time-based anomaly detection
        if behavior['total_requests'] > 10:
            # Check if request pattern is too regular (bot-like)
            if len(recent_requests) >= 10:
                intervals = [recent_requests[i] - recent_requests[i-1] 
                           for i in range(1, min(10, len(recent_requests)))]
                avg_interval = sum(intervals) / len(intervals)
                variance = sum((x - avg_interval) ** 2 for x in intervals) / len(intervals)
                
                # Too regular = bot (variance close to 0)
                if variance < 0.1:
                    score += 20
        
        # 7. HTTP method anomalies
        if request.method not in ['GET', 'POST']:
            score += 10
        
        # 8. Missing common headers (suspicious)
        expected_headers = ['User-Agent', 'Accept', 'Accept-Language']
        missing = sum(1 for h in expected_headers if h not in request.headers)
        score += missing * 10
        
        # 9. Referrer analysis
        referer = request.headers.get('Referer', '')
        if referer and 'sixy54u9329u4e35-936854r84k30djfrk93w9s9' not in referer:
            # External referrer on internal pages = suspicious
            if request.path.startswith('/admin') or request.path.startswith('/api'):
                score += 15
        
        # 10. Failed authentication tracking
        if behavior['failed_auth'] > self.thresholds['consecutive_errors']:
            score += behavior['failed_auth'] * 5
        
        # Update stored threat score
        behavior['threat_score'] = min(score, 100)
        
        return behavior['threat_score']
    
    def is_blocked(self, ip: str) -> bool:
        """Check if IP is currently blocked"""
        behavior = self.ip_behavior[ip]
        if behavior['blocked_until'] > time.time():
            return True
        return False
    
    def block_ip(self, ip: str, duration: int = 3600):
        """Block IP for specified duration (default 1 hour)"""
        self.ip_behavior[ip]['blocked_until'] = time.time() + duration
    
    def record_failed_auth(self, ip: str):
        """Record failed authentication attempt"""
        self.ip_behavior[ip]['failed_auth'] += 1
    
    def get_action(self, threat_score: float) -> str:
        """Determine action based on threat score"""
        if threat_score >= self.thresholds['threat_score_block']:
            return 'block'
        elif threat_score >= self.thresholds['threat_score_challenge']:
            return 'challenge'
        else:
            return 'allow'
    
    async def cleanup_old_data(self):
        """Periodic cleanup of old tracking data"""
        while True:
            await asyncio.sleep(3600)  # Every hour
            now = time.time()
            
            # Remove data older than 24 hours
            for ip in list(self.ip_behavior.keys()):
                behavior = self.ip_behavior[ip]
                if now - behavior['last_seen'] > 86400:  # 24 hours
                    del self.ip_behavior[ip]

# Global detector instance
threat_detector = AIThreatDetector()

@web.middleware
async def ai_threat_detection_middleware(request, handler):
    """AI-powered threat detection middleware"""
    # Get client IP
    ip = request.headers.get('X-Forwarded-For', request.remote).split(',')[0].strip()
    
    # Check if IP is blocked
    if threat_detector.is_blocked(ip):
        return web.Response(text='Access Denied', status=403)
    
    # Calculate threat score
    threat_score = threat_detector.calculate_threat_score(ip, request)
    action = threat_detector.get_action(threat_score)
    
    if action == 'block':
        threat_detector.block_ip(ip, duration=3600)
        return web.Response(text='Too many suspicious requests', status=429)
    
    elif action == 'challenge':
        # Challenge suspicious requests (implemented in proof-of-work module)
        request['needs_challenge'] = True
    
    # Allow request but track it
    request['threat_score'] = threat_score
    response = await handler(request)
    
    # Add security headers
    response.headers['X-Threat-Score'] = str(int(threat_score))
    
    return response
