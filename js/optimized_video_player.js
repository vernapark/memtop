// ===================================
// OPTIMIZED VIDEO PLAYER
// MacBook zoom + Super fast loading + No buffering
// ===================================

class OptimizedVideoPlayer {
    constructor() {
        this.currentVideo = null;
        this.videoElement = null;
        this.modal = null;
        this.isLoading = false;
        this.retryCount = 0;
        this.maxRetries = 3;
        this.connectionSpeed = 'fast'; // fast, medium, slow
        this.bufferCheckInterval = null;
        
        this.init();
    }
    
    init() {
        this.modal = document.getElementById('videoModal');
        this.videoElement = document.getElementById('modalVideo');
        
        if (!this.modal || !this.videoElement) {
            console.error('❌ Modal or video element not found');
            return;
        }
        
        // Detect connection speed
        this.detectConnectionSpeed();
        
        // Setup error handling
        this.setupErrorHandling();
        
        // Setup video event listeners
        this.setupVideoEventListeners();
        
        console.log('✅ Optimized video player initialized');
        console.log('📶 Connection speed:', this.connectionSpeed);
    }
    
    // ===================================
    // CONNECTION SPEED DETECTION
    // ===================================
    
    detectConnectionSpeed() {
        if ('connection' in navigator) {
            const connection = navigator.connection || navigator.mozConnection || navigator.webkitConnection;
            
            if (connection) {
                const effectiveType = connection.effectiveType;
                const downlink = connection.downlink; // Mbps
                
                console.log('📊 Network info:', { effectiveType, downlink });
                
                // Classify speed
                if (effectiveType === '4g' && downlink > 5) {
                    this.connectionSpeed = 'fast';
                } else if (effectiveType === '3g' || downlink > 1.5) {
                    this.connectionSpeed = 'medium';
                } else {
                    this.connectionSpeed = 'slow';
                }
                
                // Listen for connection changes
                connection.addEventListener('change', () => {
                    this.detectConnectionSpeed();
                    console.log('📶 Connection changed:', this.connectionSpeed);
                });
            }
        }
    }
    
    // ===================================
    // OPEN VIDEO WITH MACBOOK ZOOM
    // ===================================
    
    async openVideo(video, clickedElement = null) {
        try {
            console.log('🎬 Opening video:', video.title);
            
            this.currentVideo = video;
            this.retryCount = 0;
            
            // Get click position for zoom origin
            const originPoint = this.getClickOrigin(clickedElement);
            
            // Prepare modal
            this.prepareModal(video);
            
            // Show modal with MacBook zoom animation
            await this.showModalWithZoom(originPoint);
            
            // Load and play video
            await this.loadVideoOptimized(video.videoUrl);
            
        } catch (error) {
            console.error('❌ Error opening video:', error);
            this.showError('Failed to open video. Please try again.');
        }
    }
    
    getClickOrigin(element) {
        if (!element) {
            return { x: window.innerWidth / 2, y: window.innerHeight / 2 };
        }
        
        const rect = element.getBoundingClientRect();
        return {
            x: rect.left + rect.width / 2,
            y: rect.top + rect.height / 2
        };
    }
    
    prepareModal(video) {
        // Set video info
        const modalTitle = document.getElementById('modalTitle');
        const modalDescription = document.getElementById('modalDescription');
        const modalCategory = document.getElementById('modalCategory');
        
        if (modalTitle) modalTitle.textContent = video.title;
        if (modalDescription) modalDescription.textContent = video.description || 'No description available';
        if (modalCategory) modalCategory.textContent = video.category || 'General';
        
        // Reset video element
        this.videoElement.src = '';
        this.videoElement.load();
        
        // Show loading indicator
        this.showLoading();
    }
    
    async showModalWithZoom(origin) {
        return new Promise((resolve) => {
            // Set transform origin based on click position
            this.modal.style.transformOrigin = `${origin.x}px ${origin.y}px`;
            
            // Show modal
            this.modal.style.display = 'flex';
            this.modal.classList.add('active');
            
            // Prevent body scroll
            document.body.classList.add('modal-open');
            
            // Wait for animation to complete
            setTimeout(resolve, 500);
        });
    }
    
    // ===================================
    // OPTIMIZED VIDEO LOADING
    // ===================================
    
    async loadVideoOptimized(videoUrl) {
        try {
            this.isLoading = true;
            this.showLoading();
            
            console.log('📥 Loading video...', { url: videoUrl, speed: this.connectionSpeed });
            
            // Optimize based on connection speed
            const optimizedUrl = this.getOptimizedUrl(videoUrl);
            
            // Preload video metadata
            this.videoElement.preload = 'metadata';
            
            // Set optimal buffer size
            this.setOptimalBuffer();
            
            // Load video source
            this.videoElement.src = optimizedUrl;
            
            // Progressive loading
            await this.progressiveLoad();
            
            // Start buffer monitoring
            this.startBufferMonitoring();
            
            // Auto-play
            await this.playVideo();
            
            this.isLoading = false;
            this.hideLoading();
            
            console.log('✅ Video loaded and playing');
            
        } catch (error) {
            console.error('❌ Video loading error:', error);
            this.handleLoadError(error);
        }
    }
    
    getOptimizedUrl(videoUrl) {
        // For Cloudinary videos, we can add quality transformations
        if (videoUrl.includes('cloudinary.com')) {
            const baseUrl = videoUrl.split('/upload/')[0] + '/upload/';
            const videoPath = videoUrl.split('/upload/')[1];
            
            // Quality settings based on connection
            let quality = 'q_auto:best';
            if (this.connectionSpeed === 'medium') {
                quality = 'q_auto:good';
            } else if (this.connectionSpeed === 'slow') {
                quality = 'q_auto:low';
            }
            
            // Add optimizations
            const optimizations = [
                quality,
                'f_auto', // Auto format
                'vc_auto', // Auto video codec
                'br_500k' // Bitrate cap for smooth streaming
            ].join(',');
            
            return `${baseUrl}${optimizations}/${videoPath}`;
        }
        
        return videoUrl;
    }
    
    setOptimalBuffer() {
        // Adjust buffer based on connection
        if (this.connectionSpeed === 'slow') {
            this.videoElement.preload = 'auto'; // Aggressive buffering for slow connections
        } else {
            this.videoElement.preload = 'metadata'; // Smart buffering for fast connections
        }
    }
    
    async progressiveLoad() {
        return new Promise((resolve, reject) => {
            const timeout = setTimeout(() => {
                reject(new Error('Video loading timeout'));
            }, 15000); // 15 second timeout
            
            const onCanPlay = () => {
                clearTimeout(timeout);
                this.videoElement.removeEventListener('canplay', onCanPlay);
                this.videoElement.removeEventListener('error', onError);
                resolve();
            };
            
            const onError = (e) => {
                clearTimeout(timeout);
                this.videoElement.removeEventListener('canplay', onCanPlay);
                this.videoElement.removeEventListener('error', onError);
                reject(e);
            };
            
            this.videoElement.addEventListener('canplay', onCanPlay);
            this.videoElement.addEventListener('error', onError);
            this.videoElement.load();
        });
    }
    
    async playVideo() {
        try {
            await this.videoElement.play();
            console.log('▶️ Video playing');
        } catch (error) {
            console.error('❌ Play error:', error);
            // Retry on mobile autoplay issues
            if (error.name === 'NotAllowedError') {
                console.log('⚠️ Autoplay blocked, waiting for user interaction');
            } else {
                throw error;
            }
        }
    }
    
    // ===================================
    // BUFFER MONITORING
    // ===================================
    
    startBufferMonitoring() {
        this.stopBufferMonitoring();
        
        this.bufferCheckInterval = setInterval(() => {
            if (!this.videoElement) return;
            
            const buffered = this.videoElement.buffered;
            const currentTime = this.videoElement.currentTime;
            
            if (buffered.length > 0) {
                const bufferedEnd = buffered.end(buffered.length - 1);
                const bufferAhead = bufferedEnd - currentTime;
                
                // Show buffering if less than 2 seconds ahead
                if (bufferAhead < 2 && !this.videoElement.paused) {
                    this.showBuffering();
                } else {
                    this.hideBuffering();
                }
                
                // Log buffer status
                if (window.DEBUG) {
                    console.log('📊 Buffer:', { currentTime, bufferedEnd, bufferAhead });
                }
            }
        }, 500);
    }
    
    stopBufferMonitoring() {
        if (this.bufferCheckInterval) {
            clearInterval(this.bufferCheckInterval);
            this.bufferCheckInterval = null;
        }
    }
    
    // ===================================
    // ERROR HANDLING
    // ===================================
    
    setupErrorHandling() {
        // Global error handler
        window.addEventListener('error', (e) => {
            console.error('🔴 Global error:', e);
        });
        
        // Unhandled promise rejections
        window.addEventListener('unhandledrejection', (e) => {
            console.error('🔴 Unhandled rejection:', e.reason);
        });
    }
    
    setupVideoEventListeners() {
        if (!this.videoElement) return;
        
        // Loading states
        this.videoElement.addEventListener('loadstart', () => {
            console.log('📥 Video load started');
            this.showLoading();
        });
        
        this.videoElement.addEventListener('loadedmetadata', () => {
            console.log('📊 Metadata loaded');
        });
        
        this.videoElement.addEventListener('canplay', () => {
            console.log('✅ Can play');
            this.hideLoading();
        });
        
        this.videoElement.addEventListener('playing', () => {
            console.log('▶️ Playing');
            this.hideLoading();
            this.hideBuffering();
        });
        
        this.videoElement.addEventListener('waiting', () => {
            console.log('⏳ Waiting/buffering');
            this.showBuffering();
        });
        
        this.videoElement.addEventListener('stalled', () => {
            console.log('⚠️ Stalled');
            this.showBuffering();
        });
        
        // Error handling
        this.videoElement.addEventListener('error', (e) => {
            console.error('❌ Video error:', e);
            this.handleVideoError();
        });
        
        // Ended
        this.videoElement.addEventListener('ended', () => {
            console.log('✅ Video ended');
        });
    }
    
    handleLoadError(error) {
        this.isLoading = false;
        this.hideLoading();
        
        if (this.retryCount < this.maxRetries) {
            this.retryCount++;
            console.log(`🔄 Retrying... (${this.retryCount}/${this.maxRetries})`);
            
            setTimeout(() => {
                this.loadVideoOptimized(this.currentVideo.videoUrl);
            }, 1000 * this.retryCount);
        } else {
            this.showError('Failed to load video after multiple attempts. Please check your connection.');
        }
    }
    
    handleVideoError() {
        const error = this.videoElement.error;
        let message = 'Video playback error';
        
        if (error) {
            switch (error.code) {
                case 1: message = 'Video loading aborted'; break;
                case 2: message = 'Network error'; break;
                case 3: message = 'Video decode error'; break;
                case 4: message = 'Video format not supported'; break;
            }
        }
        
        console.error('🔴 Video error:', message);
        this.handleLoadError(new Error(message));
    }
    
    // ===================================
    // CLOSE VIDEO
    // ===================================
    
    closeVideo() {
        console.log('❌ Closing video');
        
        // Stop buffer monitoring
        this.stopBufferMonitoring();
        
        // Add closing animation
        this.modal.classList.add('closing');
        
        setTimeout(() => {
            // Stop video
            if (this.videoElement) {
                this.videoElement.pause();
                this.videoElement.src = '';
                this.videoElement.load();
            }
            
            // Hide modal
            this.modal.style.display = 'none';
            this.modal.classList.remove('active', 'closing');
            
            // Restore body scroll
            document.body.classList.remove('modal-open');
            
            // Hide all indicators
            this.hideLoading();
            this.hideBuffering();
            this.hideError();
            
            this.currentVideo = null;
        }, 300);
    }
    
    // ===================================
    // UI INDICATORS
    // ===================================
    
    showLoading() {
        const loader = document.querySelector('.video-loading');
        if (loader) loader.classList.add('active');
    }
    
    hideLoading() {
        const loader = document.querySelector('.video-loading');
        if (loader) loader.classList.remove('active');
    }
    
    showBuffering() {
        const buffering = document.querySelector('.video-buffering');
        if (buffering) buffering.classList.add('active');
    }
    
    hideBuffering() {
        const buffering = document.querySelector('.video-buffering');
        if (buffering) buffering.classList.remove('active');
    }
    
    showError(message) {
        const errorEl = document.querySelector('.video-error');
        if (errorEl) {
            errorEl.textContent = message;
            errorEl.classList.add('active');
        }
        
        this.hideLoading();
        this.hideBuffering();
    }
    
    hideError() {
        const errorEl = document.querySelector('.video-error');
        if (errorEl) errorEl.classList.remove('active');
    }
}

// ===================================
// INITIALIZE
// ===================================

let videoPlayer = null;

document.addEventListener('DOMContentLoaded', function() {
    videoPlayer = new OptimizedVideoPlayer();
    console.log('🎬 Video player ready');
});

// Export for use in main.js
window.OptimizedVideoPlayer = OptimizedVideoPlayer;
window.videoPlayer = videoPlayer;
