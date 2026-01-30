"""
🛡️ ADVANCED DDOS PROTECTION
Proof-of-work challenges, adaptive throttling, distributed rate limiting
"""
import time
import hashlib
import secrets
import asyncio
from collections import defaultdict, deque
from aiohttp import web
import json

class ProofOfWork:
    """Challenge-response system using proof-of-work"""
    
    def __init__(self, difficulty: int = 4):
        self.difficulty = difficulty  # Number of leading zeros required
        self.challenges = {}  # Store active challenges
        self.challenge_timeout = 300  # 5 minutes
    
    def generate_challenge(self, client_id: str) -> dict:
        """Generate proof-of-work challenge"""
        nonce = secrets.token_hex(16)
        timestamp = int(time.time())
        
        challenge_data = {
            'nonce': nonce,
            'timestamp': timestamp,
            'difficulty': self.difficulty,
            'client_id': client_id
        }
        
        # Store challenge
        challenge_key = hashlib.sha256(f"{client_id}{nonce}".encode()).hexdigest()
        self.challenges[challenge_key] = challenge_data
        
        return {
            'challenge': nonce,
            'difficulty': self.difficulty,
            'timestamp': timestamp
        }
    
    def verify_solution(self, client_id: str, nonce: str, solution: int) -> bool:
        """Verify proof-of-work solution"""
        challenge_key = hashlib.sha256(f"{client_id}{nonce}".encode()).hexdigest()
        
        if challenge_key not in self.challenges:
            return False
        
        challenge = self.challenges[challenge_key]
        
        # Check timeout
        if time.time() - challenge['timestamp'] > self.challenge_timeout:
            del self.challenges[challenge_key]
            return False
        
        # Verify solution
        test_string = f"{nonce}{solution}".encode()
        hash_result = hashlib.sha256(test_string).hexdigest()
        
        # Check if hash has required leading zeros
        required_prefix = '0' * self.difficulty
        is_valid = hash_result.startswith(required_prefix)
        
        if is_valid:
            del self.challenges[challenge_key]
        
        return is_valid
    
    async def cleanup_old_challenges(self):
        """Remove expired challenges"""
        while True:
            await asyncio.sleep(60)  # Every minute
            now = time.time()
            
            for key in list(self.challenges.keys()):
                if now - self.challenges[key]['timestamp'] > self.challenge_timeout:
                    del self.challenges[key]

class AdaptiveRateLimiter:
    """Intelligent rate limiting that adapts to traffic patterns"""
    
    def __init__(self):
        self.rate_data = defaultdict(lambda: {
            'requests': deque(maxlen=1000),
            'normal_rate': 60,  # Baseline requests per minute
            'current_limit': 60,
            'burst_count': 0,
            'last_burst': 0,
            'whitelist': False
        })
        
        # Global traffic monitoring
        self.global_requests = deque(maxlen=10000)
        self.under_attack = False
        self.attack_threshold = 1000  # Global requests per minute
    
    def check_rate_limit(self, ip: str) -> tuple[bool, int]:
        """
        Check if IP exceeds rate limit
        Returns: (is_allowed, wait_time)
        """
        data = self.rate_data[ip]
        now = time.time()
        
        # Clean old requests
        while data['requests'] and now - data['requests'][0] > 60:
            data['requests'].popleft()
        
        # Add current request
        data['requests'].append(now)
        
        current_rate = len(data['requests'])
        
        # Check if whitelisted
        if data['whitelist']:
            return True, 0
        
        # Adaptive limit calculation
        if current_rate > data['normal_rate'] * 2:
            # Burst detected
            data['burst_count'] += 1
            data['last_burst'] = now
            
            if data['burst_count'] > 3:
                # Tighten limits
                data['current_limit'] = max(10, data['current_limit'] // 2)
        else:
            # Gradually relax limits if behavior improves
            if now - data['last_burst'] > 300:  # 5 minutes of good behavior
                data['current_limit'] = min(data['normal_rate'], data['current_limit'] + 5)
                data['burst_count'] = max(0, data['burst_count'] - 1)
        
        # Check global attack mode
        if self.under_attack:
            data['current_limit'] = max(5, data['current_limit'] // 2)
        
        # Apply limit
        if current_rate > data['current_limit']:
            wait_time = 60 - (now - data['requests'][0])
            return False, int(wait_time)
        
        return True, 0
    
    def update_global_traffic(self):
        """Monitor global traffic for DDoS detection"""
        now = time.time()
        self.global_requests.append(now)
        
        # Clean old requests
        while self.global_requests and now - self.global_requests[0] > 60:
            self.global_requests.popleft()
        
        # Detect DDoS
        global_rate = len(self.global_requests)
        if global_rate > self.attack_threshold:
            self.under_attack = True
        elif global_rate < self.attack_threshold * 0.5:
            self.under_attack = False
    
    def whitelist_ip(self, ip: str):
        """Whitelist trusted IP"""
        self.rate_data[ip]['whitelist'] = True

class DistributedRateLimiter:
    """Coordinate rate limiting across distributed instances"""
    
    def __init__(self):
        self.shared_state = {}  # In production, use Redis/Memcached
        self.local_cache = defaultdict(lambda: {'count': 0, 'timestamp': time.time()})
    
    async def check_distributed_limit(self, key: str, limit: int, window: int = 60) -> bool:
        """
        Check rate limit across distributed system
        key: identifier (IP, user ID, etc.)
        limit: max requests per window
        window: time window in seconds
        """
        now = time.time()
        cache = self.local_cache[key]
        
        # Reset if window expired
        if now - cache['timestamp'] > window:
            cache['count'] = 0
            cache['timestamp'] = now
        
        cache['count'] += 1
        
        # In production, sync with Redis:
        # redis.incr(f"rate:{key}")
        # redis.expire(f"rate:{key}", window)
        
        return cache['count'] <= limit

# Global instances
proof_of_work = ProofOfWork(difficulty=4)
adaptive_limiter = AdaptiveRateLimiter()
distributed_limiter = DistributedRateLimiter()

@web.middleware
async def ddos_protection_middleware(request, handler):
    """Comprehensive DDoS protection"""
    
    ip = request.headers.get('X-Forwarded-For', request.remote).split(',')[0].strip()
    
    # 1. Update global traffic monitoring
    adaptive_limiter.update_global_traffic()
    
    # 2. Check adaptive rate limit
    is_allowed, wait_time = adaptive_limiter.check_rate_limit(ip)
    
    if not is_allowed:
        # 3. Issue proof-of-work challenge for rate-limited clients
        if request.headers.get('X-PoW-Solution'):
            # Client attempted to solve challenge
            nonce = request.headers.get('X-PoW-Nonce')
            solution = int(request.headers.get('X-PoW-Solution', 0))
            
            if proof_of_work.verify_solution(ip, nonce, solution):
                # Valid solution - allow request
                adaptive_limiter.whitelist_ip(ip)
            else:
                return web.Response(
                    text='Invalid proof-of-work solution',
                    status=403
                )
        else:
            # Issue new challenge
            challenge = proof_of_work.generate_challenge(ip)
            return web.Response(
                text=json.dumps({
                    'error': 'Rate limit exceeded',
                    'challenge': challenge,
                    'message': 'Solve proof-of-work challenge to continue'
                }),
                status=429,
                headers={'Retry-After': str(wait_time)}
            )
    
    # 4. Check distributed rate limit
    if not await distributed_limiter.check_distributed_limit(f"global:{ip}", 100):
        return web.Response(text='Global rate limit exceeded', status=429)
    
    # 5. Request allowed - proceed
    response = await handler(request)
    
    # Add rate limit headers
    response.headers['X-RateLimit-Limit'] = str(adaptive_limiter.rate_data[ip]['current_limit'])
    response.headers['X-RateLimit-Remaining'] = str(
        max(0, adaptive_limiter.rate_data[ip]['current_limit'] - len(adaptive_limiter.rate_data[ip]['requests']))
    )
    
    return response

@web.middleware
async def connection_throttling_middleware(request, handler):
    """Throttle connection speed for suspicious clients"""
    
    # Check if client needs throttling (from threat detection)
    threat_score = request.get('threat_score', 0)
    
    if threat_score > 50:
        # Add artificial delay for suspicious clients
        delay = (threat_score - 50) / 10  # 0-5 seconds
        await asyncio.sleep(min(delay, 5))
    
    return await handler(request)
