// Live Visitors Display for Admin Panel
(function() {
    'use strict';
    
    const REFRESH_INTERVAL = 5000; // Refresh every 5 seconds
    let refreshTimer = null;
    
    function formatDuration(seconds) {
        if (seconds < 60) return `${seconds}s`;
        const minutes = Math.floor(seconds / 60);
        if (minutes < 60) return `${minutes}m`;
        const hours = Math.floor(minutes / 60);
        const mins = minutes % 60;
        return `${hours}h ${mins}m`;
    }
    
    function createVisitorCard(visitor) {
        const card = document.createElement('div');
        card.style.cssText = `
            background: #2a2a2a;
            border-left: 3px solid #3ea6ff;
            padding: 10px;
            margin-bottom: 8px;
            border-radius: 4px;
            transition: all 0.3s;
        `;
        
        card.innerHTML = `
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px;">
                <div style="display: flex; align-items: center; gap: 8px;">
                    <span style="font-size: 20px;">${visitor.flag}</span>
                    <span style="color: #fff; font-weight: 600; font-size: 13px;">${visitor.country}</span>
                </div>
                <span style="background: #0a0a0a; color: #3ea6ff; padding: 2px 6px; border-radius: 4px; font-size: 10px;">
                    ${formatDuration(visitor.duration)}
                </span>
            </div>
            <div style="color: #aaa; font-size: 11px; font-family: monospace; margin-bottom: 3px;">
                ${visitor.ip}
            </div>
            <div style="color: #777; font-size: 10px;">
                📄 ${visitor.page}
            </div>
        `;
        
        // Hover effect
        card.addEventListener('mouseenter', () => {
            card.style.background = '#333';
            card.style.borderLeftColor = '#4db2ff';
        });
        
        card.addEventListener('mouseleave', () => {
            card.style.background = '#2a2a2a';
            card.style.borderLeftColor = '#3ea6ff';
        });
        
        return card;
    }
    
    async function loadVisitors() {
        try {
            const response = await fetch('/api/visitors/active');
            
            if (!response.ok) {
                throw new Error('Failed to fetch visitors');
            }
            
            const data = await response.json();
            const visitors = data.visitors || [];
            
            // Update count
            const countElement = document.getElementById('visitorCount');
            if (countElement) {
                countElement.textContent = visitors.length;
                countElement.style.animation = 'pulse 0.5s';
                setTimeout(() => countElement.style.animation = '', 500);
            }
            
            // Update list
            const listElement = document.getElementById('visitorsList');
            if (!listElement) return;
            
            if (visitors.length === 0) {
                listElement.innerHTML = `
                    <div style="text-align: center; color: #777; padding: 20px;">
                        <div style="font-size: 40px; margin-bottom: 10px;">👻</div>
                        <div>No active visitors</div>
                    </div>
                `;
                return;
            }
            
            // Clear and rebuild list
            listElement.innerHTML = '';
            
            visitors.forEach(visitor => {
                listElement.appendChild(createVisitorCard(visitor));
            });
            
        } catch (error) {
            console.error('Error loading visitors:', error);
            const listElement = document.getElementById('visitorsList');
            if (listElement) {
                listElement.innerHTML = `
                    <div style="text-align: center; color: #ff4444; padding: 20px;">
                        <div style="font-size: 30px; margin-bottom: 10px;">⚠️</div>
                        <div>Error loading visitors</div>
                    </div>
                `;
            }
        }
    }
    
    function startAutoRefresh() {
        // Initial load
        loadVisitors();
        
        // Auto-refresh
        refreshTimer = setInterval(loadVisitors, REFRESH_INTERVAL);
    }
    
    function stopAutoRefresh() {
        if (refreshTimer) {
            clearInterval(refreshTimer);
            refreshTimer = null;
        }
    }
    
    // Add pulse animation
    const style = document.createElement('style');
    style.textContent = `
        @keyframes pulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.1); }
        }
        
        #liveVisitorsWidget::-webkit-scrollbar {
            width: 6px;
        }
        
        #liveVisitorsWidget::-webkit-scrollbar-track {
            background: #0a0a0a;
            border-radius: 3px;
        }
        
        #liveVisitorsWidget::-webkit-scrollbar-thumb {
            background: #3ea6ff;
            border-radius: 3px;
        }
        
        #liveVisitorsWidget::-webkit-scrollbar-thumb:hover {
            background: #4db2ff;
        }
    `;
    document.head.appendChild(style);
    
    // Initialize on page load
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', startAutoRefresh);
    } else {
        startAutoRefresh();
    }
    
    // Stop refresh when page unloads
    window.addEventListener('beforeunload', stopAutoRefresh);
    
    // Pause refresh when tab is hidden
    document.addEventListener('visibilitychange', () => {
        if (document.hidden) {
            stopAutoRefresh();
        } else {
            startAutoRefresh();
        }
    });
    
    console.log('🟢 Live Visitors Widget: Initialized');
})();
