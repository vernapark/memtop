// Visitor Tracking for Homepage
(function() {
    'use strict';
    
    // Generate unique session ID for this visit
    let sessionId = localStorage.getItem('visitor_session_id');
    if (!sessionId) {
        sessionId = generateSessionId();
        localStorage.setItem('visitor_session_id', sessionId);
    }
    
    let heartbeatInterval = null;
    let isTracking = false;
    
    function generateSessionId() {
        return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }
    
    function getCurrentPage() {
        return window.location.pathname || '/';
    }
    
    async function connectVisitor() {
        if (isTracking) return;
        
        try {
            const response = await fetch('/api/visitor/connect', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    sessionId: sessionId,
                    page: getCurrentPage()
                })
            });
            
            if (response.ok) {
                console.log('📊 Visitor tracking: Connected');
                isTracking = true;
                startHeartbeat();
            }
        } catch (error) {
            console.error('Visitor tracking error:', error);
        }
    }
    
    async function sendHeartbeat() {
        if (!isTracking) return;
        
        try {
            await fetch('/api/visitor/heartbeat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    sessionId: sessionId,
                    page: getCurrentPage()
                })
            });
        } catch (error) {
            console.error('Heartbeat error:', error);
        }
    }
    
    async function disconnectVisitor() {
        if (!isTracking) return;
        
        try {
            // Use sendBeacon for reliable disconnect (works even when page is closing)
            const data = JSON.stringify({
                sessionId: sessionId
            });
            
            navigator.sendBeacon('/api/visitor/disconnect', new Blob([data], {
                type: 'application/json'
            }));
            
            isTracking = false;
            stopHeartbeat();
        } catch (error) {
            console.error('Disconnect error:', error);
        }
    }
    
    function startHeartbeat() {
        // Send heartbeat every 15 seconds
        heartbeatInterval = setInterval(sendHeartbeat, 15000);
    }
    
    function stopHeartbeat() {
        if (heartbeatInterval) {
            clearInterval(heartbeatInterval);
            heartbeatInterval = null;
        }
    }
    
    // Initialize on page load
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', connectVisitor);
    } else {
        connectVisitor();
    }
    
    // Disconnect when page unloads
    window.addEventListener('beforeunload', disconnectVisitor);
    window.addEventListener('pagehide', disconnectVisitor);
    
    // Handle visibility change (tab switching)
    document.addEventListener('visibilitychange', function() {
        if (document.hidden) {
            stopHeartbeat();
        } else {
            if (isTracking) {
                sendHeartbeat();
                startHeartbeat();
            }
        }
    });
})();
