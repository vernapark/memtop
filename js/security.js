/**
 * Client-Side Security Protection
 * Anti-debugging, Anti-DevTools, Anti-Reverse Engineering
 */

(function() {
    'use strict';
    
    // Configuration
    const SECURITY_CONFIG = {
        enableAntiDebug: true,
        enableAntiDevTools: true,
        enableAntiCopy: true,
        enableContextMenuBlock: false, // Set to false for better UX
        checkInterval: 1000,
        maxDebuggerHits: 3
    };
    
    let debuggerHitCount = 0;
    let devToolsOpen = false;
    
    // ==================== Anti-Debugging ====================
    
    /**
     * Detect debugger and prevent debugging
     */
    function antiDebugger() {
        if (!SECURITY_CONFIG.enableAntiDebug) return;
        
        // Method 1: Infinite debugger loop
        setInterval(function() {
            debugger;
        }, 100);
        
        // Method 2: Time-based detection
        const start = performance.now();
        debugger;
        const end = performance.now();
        
        if (end - start > 100) {
            debuggerHitCount++;
            if (debuggerHitCount >= SECURITY_CONFIG.maxDebuggerHits) {
                handleSecurityViolation('debugger_detected');
            }
        }
    }
    
    /**
     * Detect DevTools using various methods
     */
    function detectDevTools() {
        if (!SECURITY_CONFIG.enableAntiDevTools) return;
        
        // Method 1: Check window size difference
        const widthThreshold = window.outerWidth - window.innerWidth > 160;
        const heightThreshold = window.outerHeight - window.innerHeight > 160;
        
        if (widthThreshold || heightThreshold) {
            if (!devToolsOpen) {
                devToolsOpen = true;
                handleSecurityViolation('devtools_detected');
            }
        } else {
            devToolsOpen = false;
        }
        
        // Method 2: Check console
        let checkStatus = false;
        const element = new Image();
        Object.defineProperty(element, 'id', {
            get: function() {
                checkStatus = true;
                handleSecurityViolation('console_detected');
            }
        });
        
        console.log(element);
        
        // Method 3: toString detection
        const devtools = /./;
        devtools.toString = function() {
            handleSecurityViolation('devtools_toString');
        };
        
        console.log('%c', devtools);
    }
    
    /**
     * Prevent console access
     */
    function disableConsole() {
        if (!SECURITY_CONFIG.enableAntiDebug) return;
        
        // Disable common console methods
        const methods = [
            'log', 'debug', 'info', 'warn', 'error', 'table', 
            'clear', 'trace', 'assert', 'count', 'dir', 'dirxml'
        ];
        
        methods.forEach(method => {
            if (console[method]) {
                console[method] = function() {
                    // Silent override
                };
            }
        });
    }
    
    /**
     * Detect and prevent right-click inspection
     */
    function preventContextMenu() {
        if (!SECURITY_CONFIG.enableContextMenuBlock) return;
        
        document.addEventListener('contextmenu', function(e) {
            e.preventDefault();
            return false;
        });
    }
    
    /**
     * Prevent keyboard shortcuts for DevTools
     */
    function preventDevToolsShortcuts() {
        document.addEventListener('keydown', function(e) {
            // F12
            if (e.keyCode === 123) {
                e.preventDefault();
                return false;
            }
            
            // Ctrl+Shift+I, Ctrl+Shift+J, Ctrl+Shift+C
            if (e.ctrlKey && e.shiftKey && (e.keyCode === 73 || e.keyCode === 74 || e.keyCode === 67)) {
                e.preventDefault();
                return false;
            }
            
            // Ctrl+U (view source)
            if (e.ctrlKey && e.keyCode === 85) {
                e.preventDefault();
                return false;
            }
            
            // Ctrl+S (save page)
            if (e.ctrlKey && e.keyCode === 83) {
                e.preventDefault();
                return false;
            }
        });
    }
    
    /**
     * Prevent text selection and copying
     */
    function preventCopy() {
        if (!SECURITY_CONFIG.enableAntiCopy) return;
        
        document.addEventListener('copy', function(e) {
            e.preventDefault();
            return false;
        });
        
        document.addEventListener('cut', function(e) {
            e.preventDefault();
            return false;
        });
        
        // Disable text selection on videos
        const style = document.createElement('style');
        style.textContent = `
            video {
                -webkit-user-select: none;
                -moz-user-select: none;
                -ms-user-select: none;
                user-select: none;
                pointer-events: auto;
            }
        `;
        document.head.appendChild(style);
    }
    
    /**
     * Obfuscate video URLs
     */
    function obfuscateVideoUrls() {
        // Override video src attribute
        const originalSetAttribute = HTMLVideoElement.prototype.setAttribute;
        HTMLVideoElement.prototype.setAttribute = function(name, value) {
            if (name === 'src') {
                // Store encrypted URL
                this.dataset.secureUrl = btoa(value);
                return;
            }
            return originalSetAttribute.call(this, name, value);
        };
    }
    
    /**
     * Detect and prevent video download attempts
     */
    function preventVideoDownload() {
        // Disable drag and drop on videos
        document.addEventListener('dragstart', function(e) {
            if (e.target.tagName === 'VIDEO') {
                e.preventDefault();
                return false;
            }
        });
        
        // Monitor network requests
        if (window.PerformanceObserver) {
            const observer = new PerformanceObserver((list) => {
                for (const entry of list.getEntries()) {
                    if (entry.initiatorType === 'video' || entry.initiatorType === 'xmlhttprequest') {
                        // Log suspicious activity
                        console.warn('Video access detected');
                    }
                }
            });
            observer.observe({ entryTypes: ['resource'] });
        }
    }
    
    /**
     * Generate client fingerprint
     */
    function generateFingerprint() {
        const data = [
            navigator.userAgent,
            navigator.language,
            navigator.platform,
            screen.width + 'x' + screen.height,
            screen.colorDepth,
            new Date().getTimezoneOffset(),
            !!window.localStorage,
            !!window.sessionStorage
        ].join('|');
        
        return btoa(data);
    }
    
    /**
     * Add fingerprint to all requests
     */
    function addFingerprintToRequests() {
        const fingerprint = generateFingerprint();
        
        // Override fetch
        const originalFetch = window.fetch;
        window.fetch = function(...args) {
            if (args[1]) {
                args[1].headers = args[1].headers || {};
                args[1].headers['X-Client-Fingerprint'] = fingerprint;
            } else {
                args[1] = { headers: { 'X-Client-Fingerprint': fingerprint } };
            }
            return originalFetch.apply(this, args);
        };
        
        // Override XMLHttpRequest
        const originalOpen = XMLHttpRequest.prototype.open;
        const originalSend = XMLHttpRequest.prototype.send;
        
        XMLHttpRequest.prototype.open = function(method, url, ...rest) {
            this._url = url;
            return originalOpen.apply(this, [method, url, ...rest]);
        };
        
        XMLHttpRequest.prototype.send = function(...args) {
            this.setRequestHeader('X-Client-Fingerprint', fingerprint);
            return originalSend.apply(this, args);
        };
    }
    
    /**
     * Handle security violations
     */
    function handleSecurityViolation(type) {
        console.warn('Security violation detected:', type);
        
        // Send alert to server
        fetch('/api/security/violation', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                type: type,
                timestamp: Date.now(),
                fingerprint: generateFingerprint()
            })
        }).catch(() => {});
        
        // Optional: Redirect or show warning
        // window.location.href = '/security-warning.html';
    }
    
    /**
     * Detect automated tools and bots
     */
    function detectAutomation() {
        // Check for common automation indicators
        const automation = {
            webdriver: navigator.webdriver,
            phantom: window._phantom || window.callPhantom,
            nightmare: window.__nightmare,
            selenium: window.document.documentElement.getAttribute('selenium') || 
                     window.document.documentElement.getAttribute('webdriver') ||
                     window.document.documentElement.getAttribute('driver')
        };
        
        if (Object.values(automation).some(v => v)) {
            handleSecurityViolation('automation_detected');
        }
    }
    
    /**
     * Initialize all security measures
     */
    function initSecurity() {
        // Start protection
        if (SECURITY_CONFIG.enableAntiDebug) {
            antiDebugger();
            disableConsole();
        }
        
        if (SECURITY_CONFIG.enableAntiDevTools) {
            setInterval(detectDevTools, SECURITY_CONFIG.checkInterval);
        }
        
        preventContextMenu();
        preventDevToolsShortcuts();
        preventCopy();
        obfuscateVideoUrls();
        preventVideoDownload();
        addFingerprintToRequests();
        detectAutomation();
        
        console.log('🔒 Security measures activated');
    }
    
    // Initialize on DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initSecurity);
    } else {
        initSecurity();
    }
    
    // Make some functions globally accessible if needed
    window._security = {
        generateFingerprint: generateFingerprint,
        handleViolation: handleSecurityViolation
    };
    
})();
