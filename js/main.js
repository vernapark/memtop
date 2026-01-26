// Premium Video Streaming - YouTube Style with Mobile Fix
// THUMBNAIL FIX: Better thumbnail handling from Cloudinary

const categoryIcons = {
    '18+': 'ðŸ”ž',
    'adult': 'ðŸ”ž',
    'entertainment': 'ðŸŽ¬',
    'education': 'ðŸ“š',
    'music': 'ðŸŽµ',
    'sports': 'âš½',
    'news': 'ðŸ“°',
    'technology': 'ðŸ’»',
    'default': 'ðŸ“º'
};

let allVideos = [];
let currentFilter = 'all';

document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    loadVideos();
    setupSearchFunctionality();
    setupCategoryFilters();
    setupModalEventListeners();
}

// Load videos from Cloudinary
async function loadVideos() {
    try {
        showLoading();
        
        const response = await fetch('/api/videos');
        const data = await response.json();
        allVideos = data.videos || [];
        
        console.log('âœ… Loaded videos from cloud:', allVideos.length);
        
        // Debug: Log first video to see thumbnail structure
        if (allVideos.length > 0) {
            console.log('ðŸ“Š Sample video data:', allVideos[0]);
            console.log('ðŸ–¼ï¸ Thumbnail field:', allVideos[0].thumbnail);
        }
        
        if (allVideos.length === 0) {
            showEmptyState();
            return;
        }
        
        displayVideos(allVideos);
        
    } catch (error) {
        console.error('âŒ Error loading videos:', error);
        showErrorState();
    }
}

// Display videos in grid
function displayVideos(videos) {
    const container = document.getElementById('videosContainer');
    
    if (!container) return;
    
    if (videos.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <h3>No videos found</h3>
                <p>Try adjusting your search or filter</p>
            </div>
        `;
        return;
    }
    
    container.innerHTML = videos.map(video => createVideoCard(video)).join('');
    
    // Add click listeners with ROBUST touch handling for mobile scroll fix
    setTimeout(() => {
        document.querySelectorAll('.video-card').forEach((card, index) => {
            let touchStartY = 0;
            let touchStartX = 0;
            let touchStartTime = 0;
            let isScrolling = false;
            let hasMoved = false;
            
            // Track touch start
            card.addEventListener('touchstart', (e) => {
                touchStartY = e.touches[0].clientY;
                touchStartX = e.touches[0].clientX;
                touchStartTime = Date.now();
                isScrolling = false;
                hasMoved = false;
            }, { passive: true });
            
            // Track touch move - detect scrolling with lower threshold
            card.addEventListener('touchmove', (e) => {
                const touchY = e.touches[0].clientY;
                const touchX = e.touches[0].clientX;
                const deltaY = Math.abs(touchY - touchStartY);
                const deltaX = Math.abs(touchX - touchStartX);
                
                // If user moved more than 5px (reduced from 10px), it's definitely scrolling
                if (deltaY > 5 || deltaX > 5) {
                    isScrolling = true;
                    hasMoved = true;
                }
            }, { passive: true });
            
            // Handle touch end - ONLY open video if NOT scrolling
            card.addEventListener('touchend', (e) => {
                const touchDuration = Date.now() - touchStartTime;
                
                // Only open video if:
                // 1. User did NOT scroll (no movement detected)
                // 2. Touch was quick (less than 300ms - reduced from 500ms)
                // 3. Not currently scrolling
                if (!isScrolling && !hasMoved && touchDuration < 300) {
                    e.preventDefault();
                    e.stopPropagation();
                    openVideoModal(videos[index]);
                }
                // Otherwise, let the scroll happen naturally
            }, { passive: false });
            
            // Desktop click (non-touch devices)
            card.addEventListener('click', (e) => {
                // Only handle if not a touch device or touch already handled
                if (!e.defaultPrevented && e.pointerType !== 'touch') {
                    e.preventDefault();
                    e.stopPropagation();
                    openVideoModal(videos[index]);
                }
            });
        });
        
        // Load video durations
        loadVideoDurations();
    }, 0);
}

// Create video card HTML - FIXED THUMBNAIL HANDLING
function createVideoCard(video) {
    // Enhanced thumbnail detection
    let thumbnailSrc = '';
    
    // Try multiple possible thumbnail sources
    if (video.thumbnail && video.thumbnail.trim() !== '') {
        thumbnailSrc = video.thumbnail;
        console.log('âœ… Using video.thumbnail:', thumbnailSrc);
    } else if (video.thumbnailUrl && video.thumbnailUrl.trim() !== '') {
        thumbnailSrc = video.thumbnailUrl;
        console.log('âœ… Using video.thumbnailUrl:', thumbnailSrc);
    } else if (video.videoUrl) {
        // Generate thumbnail from video URL (Cloudinary can do this)
        thumbnailSrc = generateCloudinaryThumbnail(video.videoUrl);
        console.log('âš™ï¸ Generated thumbnail from video URL:', thumbnailSrc);
    } else {
        thumbnailSrc = generateDefaultThumbnail();
        console.log('âš ï¸ Using default thumbnail for:', video.title);
    }
    
    const categoryIcon = categoryIcons[video.category?.toLowerCase()] || categoryIcons['default'];
    
    return `
        <div class="video-card" data-video-id="${video.id}">
            <div class="video-thumbnail-wrapper">
                <img 
                    src="${thumbnailSrc}" 
                    alt="${escapeHtml(video.title)}" 
                    class="video-thumbnail"
                    onerror="console.error('Thumbnail failed:', this.src); this.src='${generateDefaultThumbnail()}'; this.onerror=null;"
                    loading="lazy"
                    crossorigin="anonymous"
                >
                <span class="video-duration" data-video-url="${video.videoUrl}">...</span>
                <span class="video-category-badge">${categoryIcon} ${escapeHtml(video.category || 'Video')}</span>
            </div>
            <div class="video-info">
                <div class="video-avatar">${categoryIcon}</div>
                <div class="video-details">
                    <h3 class="video-title">${escapeHtml(video.title)}</h3>
                    <div class="video-metadata">
                        <span>${escapeHtml(video.category || 'General')}</span>
                        <span>${formatDate(video.uploadDate)}</span>
                    </div>
                </div>
            </div>
        </div>
    `;
}

// Generate thumbnail from Cloudinary video URL
function generateCloudinaryThumbnail(videoUrl) {
    try {
        // Cloudinary URLs can be converted to thumbnails
        // e.g., video.mp4 -> video.jpg at a specific time
        if (videoUrl.includes('cloudinary.com')) {
            // Replace the video extension with jpg and add transformation for thumbnail
            let thumbUrl = videoUrl.replace(/\.(mp4|mov|avi|mkv|webm)$/i, '.jpg');
            
            // Add video thumbnail transformation if not already present
            if (!thumbUrl.includes('so_')) {
                // Insert transformation parameter to get frame at 2 seconds
                thumbUrl = thumbUrl.replace('/upload/', '/upload/so_2.0,f_jpg,q_auto/');
            }
            
            console.log('ðŸŽ¬ Cloudinary thumbnail generated:', thumbUrl);
            return thumbUrl;
        }
    } catch (e) {
        console.error('Error generating Cloudinary thumbnail:', e);
    }
    
    return generateDefaultThumbnail();
}

// Load video durations asynchronously
function loadVideoDurations() {
    document.querySelectorAll('.video-duration').forEach(element => {
        const videoUrl = element.getAttribute('data-video-url');
        if (videoUrl) {
            loadSingleDuration(videoUrl, element);
        }
    });
}

function loadSingleDuration(videoUrl, element) {
    const video = document.createElement('video');
    video.preload = 'metadata';
    video.crossOrigin = 'anonymous';
    
    video.addEventListener('loadedmetadata', function() {
        const duration = video.duration;
        const formatted = formatDuration(duration);
        element.textContent = formatted;
    });
    
    video.addEventListener('error', function() {
        element.textContent = '--:--';
    });
    
    video.src = videoUrl;
}

// Format duration (seconds to mm:ss)
function formatDuration(seconds) {
    if (!seconds || isNaN(seconds)) return '--:--';
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs < 10 ? '0' : ''}${secs}`;
}

// Format date
function formatDate(dateString) {
    if (!dateString) return 'Recently';
    
    try {
        const date = new Date(dateString);
        const now = new Date();
        const diffTime = Math.abs(now - date);
        const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));
        
        if (diffDays === 0) return 'Today';
        if (diffDays === 1) return 'Yesterday';
        if (diffDays < 7) return `${diffDays} days ago`;
        if (diffDays < 30) return `${Math.floor(diffDays / 7)} weeks ago`;
        if (diffDays < 365) return `${Math.floor(diffDays / 30)} months ago`;
        return `${Math.floor(diffDays / 365)} years ago`;
    } catch {
        return 'Recently';
    }
}

// Generate default thumbnail
function generateDefaultThumbnail() {
    return 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="320" height="180"%3E%3Crect fill="%230f0f0f" width="320" height="180"/%3E%3Ctext fill="%23aaaaaa" font-size="24" font-family="Arial" x="50%25" y="50%25" text-anchor="middle" dy=".3em"%3EðŸ“¹%3C/text%3E%3C/svg%3E';
}

// Escape HTML to prevent XSS
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text || '';
    return div.innerHTML;
}

// ===================================
// VIDEO MODAL (MOBILE-OPTIMIZED)
// ===================================

function openVideoModal(video) {
    console.log('ðŸŽ¬ Opening video:', video.title);
    
    const modal = document.getElementById('videoModal');
    const videoElement = document.getElementById('modalVideo');
    const titleElement = document.getElementById('videoTitle');
    const descElement = document.getElementById('videoDescription');
    
    if (!modal || !videoElement) {
        console.error('âŒ Modal elements not found');
        return;
    }
    
    // Set video source
    videoElement.src = video.videoUrl;
    
    // Set video details
    if (titleElement) titleElement.textContent = video.title || 'Untitled';
    if (descElement) descElement.textContent = video.description || 'No description available';
    
    // Show modal
    modal.classList.add('active');
    document.body.style.overflow = 'hidden';
    
    // CRITICAL FIX FOR MOBILE: Play video after a short delay
    setTimeout(() => {
        videoElement.load();
        
        // Try to autoplay (works on most mobile browsers now)
        const playPromise = videoElement.play();
        
        if (playPromise !== undefined) {
            playPromise
                .then(() => {
                    console.log('âœ… Video playing');
                })
                .catch(error => {
                    console.log('âš ï¸ Autoplay prevented, user must tap play:', error);
                    // This is normal on some mobile browsers - user will tap play button
                });
        }
    }, 100);
    
    // Mobile-specific: Prevent scroll behind modal
    if (isMobileDevice()) {
        document.body.style.position = 'fixed';
        document.body.style.width = '100%';
        document.body.style.top = `-${window.scrollY}px`;
    }
}

function closeVideoModal() {
    console.log('ðŸšª Closing video modal');
    
    const modal = document.getElementById('videoModal');
    const videoElement = document.getElementById('modalVideo');
    
    if (!modal || !videoElement) return;
    
    // Pause and clear video
    videoElement.pause();
    videoElement.src = '';
    
    // Hide modal
    modal.classList.remove('active');
    
    // Restore body scroll
    if (isMobileDevice()) {
        const scrollY = document.body.style.top;
        document.body.style.position = '';
        document.body.style.width = '';
        document.body.style.top = '';
        window.scrollTo(0, parseInt(scrollY || '0') * -1);
    } else {
        document.body.style.overflow = '';
    }
}

// Setup modal event listeners
function setupModalEventListeners() {
    const modal = document.getElementById('videoModal');
    const overlay = modal?.querySelector('.video-modal-overlay');
    
    // Close on overlay click (but not on video click)
    if (overlay) {
        overlay.addEventListener('click', (e) => {
            e.stopPropagation();
            closeVideoModal();
        });
    }
    
    // Close on Escape key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            closeVideoModal();
        }
    });
    
    // Prevent video context menu
    document.addEventListener('contextmenu', (e) => {
        if (e.target.tagName === 'VIDEO') {
            e.preventDefault();
            return false;
        }
    });
}

// Detect mobile device
function isMobileDevice() {
    return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) 
        || window.innerWidth <= 768;
}

// ===================================
// SEARCH FUNCTIONALITY
// ===================================

function setupSearchFunctionality() {
    const searchInput = document.getElementById('searchInput');
    
    if (!searchInput) return;
    
    let searchTimeout;
    searchInput.addEventListener('input', (e) => {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => {
            const query = e.target.value.toLowerCase().trim();
            filterVideos(query);
        }, 300);
    });
}

function filterVideos(query) {
    let filtered = allVideos;
    
    // Apply category filter
    if (currentFilter !== 'all') {
        filtered = filtered.filter(video => 
            video.category?.toLowerCase() === currentFilter
        );
    }
    
    // Apply search query
    if (query) {
        filtered = filtered.filter(video => 
            video.title?.toLowerCase().includes(query) ||
            video.description?.toLowerCase().includes(query) ||
            video.category?.toLowerCase().includes(query)
        );
    }
    
    displayVideos(filtered);
}

// ===================================
// CATEGORY FILTERS
// ===================================

function setupCategoryFilters() {
    const chips = document.querySelectorAll('.chip');
    
    chips.forEach(chip => {
        chip.addEventListener('click', () => {
            // Update active state
            chips.forEach(c => c.classList.remove('active'));
            chip.classList.add('active');
            
            // Update filter
            currentFilter = chip.getAttribute('data-category');
            
            // Filter videos
            const searchQuery = document.getElementById('searchInput')?.value || '';
            filterVideos(searchQuery.toLowerCase().trim());
        });
    });
}

// ===================================
// LOADING & ERROR STATES
// ===================================

function showLoading() {
    const container = document.getElementById('videosContainer');
    if (!container) return;
    
    container.innerHTML = `
        <div class="loading-spinner">
            <div class="spinner"></div>
        </div>
    `;
}

function showEmptyState() {
    const container = document.getElementById('videosContainer');
    if (!container) return;
    
    container.innerHTML = `
        <div class="empty-state">
            <h3>No videos available yet</h3>
            <p>Check back soon for new content!</p>
        </div>
    `;
}

function showErrorState() {
    const container = document.getElementById('videosContainer');
    if (!container) return;
    
    container.innerHTML = `
        <div class="empty-state">
            <h3>Error Loading Videos</h3>
            <p>Please refresh the page or contact support.</p>
        </div>
    `;
}

// ===================================
// VIDEO PROTECTION
// ===================================

// Prevent video download attempts
document.addEventListener('keydown', function(e) {
    // Prevent Ctrl+S / Cmd+S
    if ((e.ctrlKey || e.metaKey) && e.key === 's') {
        e.preventDefault();
        return false;
    }
});

// Prevent video drag
document.addEventListener('dragstart', function(e) {
    if (e.target.tagName === 'VIDEO') {
        e.preventDefault();
        return false;
    }
});

// ===================================
// MOBILE OPTIMIZATIONS
// ===================================

// Touch handling is managed per video card for better scroll detection

// Handle orientation change
window.addEventListener('orientationchange', function() {
    setTimeout(() => {
        // Adjust modal if open
        const modal = document.getElementById('videoModal');
        if (modal && modal.classList.contains('active')) {
            const video = document.getElementById('modalVideo');
            if (video) {
                video.style.height = 'auto';
            }
        }
    }, 100);
});

// Console log for debugging
console.log('ðŸŽ¬ Premium Video Streaming Initialized (Thumbnail Fix)');
console.log('ðŸ“± Mobile Device:', isMobileDevice());
console.log('ðŸŒ User Agent:', navigator.userAgent);
