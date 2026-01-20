// Main JavaScript for Video Streaming Site

// Storage ready flag
let storageReady = false;

// Initialize the application
document.addEventListener('DOMContentLoaded', async function() {
    // Initialize IndexedDB storage
    try {
        await videoStorage.init();
        storageReady = true;
        console.log('Storage initialized on home page');
        loadVideos();
    } catch (error) {
        console.error('Failed to initialize storage:', error);
        document.getElementById('videoCategories').innerHTML = `
            <div class="empty-state">
                <h3>Storage Error</h3>
                <p>Failed to load videos. Please refresh the page.</p>
            </div>
        `;
    }
});

// Load and display videos by category
async function loadVideos() {
    if (!storageReady) return;
    
    try {
        const videos = await videoStorage.getAllVideos();
        const categoriesContainer = document.getElementById('videoCategories');
        
        if (!categoriesContainer) return;
        
        console.log('Total videos loaded:', videos.length);
        
        if (videos.length === 0) {
            categoriesContainer.innerHTML = `
                <div class="empty-state">
                    <h3>No videos available yet</h3>
                    <p>Check back soon for new content!</p>
                </div>
            `;
            return;
        }
        
        // Group videos by category
        const videosByCategory = {};
        videos.forEach(video => {
            if (!videosByCategory[video.category]) {
                videosByCategory[video.category] = [];
            }
            videosByCategory[video.category].push(video);
        });
        
        // Display videos by category
        categoriesContainer.innerHTML = '';
        for (const [category, categoryVideos] of Object.entries(videosByCategory)) {
            const categorySection = createCategorySection(category, categoryVideos);
            categoriesContainer.appendChild(categorySection);
        }
        
        console.log(`Loaded ${videos.length} videos in ${Object.keys(videosByCategory).length} categories`);
    } catch (error) {
        console.error('Error loading videos:', error);
        document.getElementById('videoCategories').innerHTML = `
            <div class="empty-state">
                <h3>Error Loading Videos</h3>
                <p>Please refresh the page or contact support.</p>
            </div>
        `;
    }
}

// Create a category section with videos
function createCategorySection(category, videos) {
    const section = document.createElement('div');
    section.className = 'category-section';
    
    const categoryTitle = category.charAt(0).toUpperCase() + category.slice(1);
    
    section.innerHTML = `
        <h3>${categoryTitle}</h3>
        <div class="video-grid">
            ${videos.map(video => createVideoCard(video)).join('')}
        </div>
    `;
    
    // Add click listeners to video cards
    setTimeout(() => {
        section.querySelectorAll('.video-card').forEach((card, index) => {
            card.addEventListener('click', () => openVideoModal(videos[index]));
        });
    }, 0);
    
    return section;
}

// Create a video card HTML - YouTube Style
function createVideoCard(video) {
    const thumbnailSrc = video.thumbnail || 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="320" height="180"%3E%3Crect fill="%230f0f0f" width="320" height="180"/%3E%3Ctext fill="%23aaaaaa" font-size="20" font-family="Arial" x="50%25" y="50%25" text-anchor="middle" dy=".3em"%3E📹 Video%3C/text%3E%3C/svg%3E';
    
    return `
        <div class="video-card" data-video-id="${video.id}">
            <div class="video-thumbnail-container">
                <img src="${thumbnailSrc}" alt="${video.title}" class="video-thumbnail" onerror="this.src='data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 width=%22320%22 height=%22180%22%3E%3Crect fill=%22%230f0f0f%22 width=%22320%22 height=%22180%22/%3E%3Ctext fill=%22%23aaaaaa%22 font-size=%2220%22 font-family=%22Arial%22 x=%2250%25%22 y=%2250%25%22 text-anchor=%22middle%22 dy=%22.3em%22%3E📹 Video%3C/text%3E%3C/svg%3E'">
                <span class="video-duration">10:24</span>
            </div>
            <div class="video-info">
                <div>
                    <h4>${video.title}</h4>
                    <p>${video.description || 'No description available'}</p>
                    <span class="video-category">${video.category}</span>
                </div>
            </div>
        </div>
    `;
}

// Open video player modal - Ultra-Realistic 4DX Style
function openVideoModal(video) {
    // Create modal if it doesn't exist
    let modal = document.getElementById('videoModal');
    if (!modal) {
        modal = document.createElement('div');
        modal.id = 'videoModal';
        modal.className = 'video-modal';
        modal.innerHTML = `
            <div class="video-modal-content">
                <button class="close-modal" onclick="closeVideoModal()">✕</button>
                <div class="quality-badge">4K ULTRA HD</div>
                <video id="modalVideo" controls autoplay controlsList="nodownload noremoteplayback" disablePictureInPicture disableRemotePlayback oncontextmenu="return false;">
                    <source src="" type="video/mp4">
                    Your browser does not support the video tag.
                </video>
            </div>
        `;
        document.body.appendChild(modal);
    }
    
    // Set video source and show modal
    const videoElement = document.getElementById('modalVideo');
    videoElement.src = video.videoUrl;
    modal.classList.add('active');
    
    // Prevent body scroll
    document.body.style.overflow = 'hidden';
    
    // Remove download button after video loads
    videoElement.addEventListener('loadedmetadata', function() {
        removeDownloadButton();
    });
    
    // Close modal on background click
    modal.onclick = function(e) {
        if (e.target === modal) {
            closeVideoModal();
        }
    };
}

// Close video player modal
function closeVideoModal() {
    const modal = document.getElementById('videoModal');
    const videoElement = document.getElementById('modalVideo');
    
    if (modal && videoElement) {
        modal.classList.remove('active');
        videoElement.pause();
        videoElement.src = '';
        document.body.style.overflow = '';
    }
}

// Aggressive download button removal
function removeDownloadButton() {
    const video = document.getElementById('modalVideo');
    if (video) {
        // Remove download attribute
        video.removeAttribute('download');
        
        // Set controlsList again
        video.setAttribute('controlsList', 'nodownload noremoteplayback');
    }
}

// Close modal with Escape key
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        closeVideoModal();
    }
});

// Additional download protection
document.addEventListener('contextmenu', function(e) {
    if (e.target.tagName === 'VIDEO') {
        e.preventDefault();
        return false;
    }
});

// Prevent keyboard shortcuts for download
document.addEventListener('keydown', function(e) {
    // Prevent Ctrl+S (Save)
    if ((e.ctrlKey || e.metaKey) && e.key === 's') {
        e.preventDefault();
        return false;
    }
});

// Disable drag and drop on videos
document.addEventListener('dragstart', function(e) {
    if (e.target.tagName === 'VIDEO') {
        e.preventDefault();
        return false;
    }
});



// Video Quality Management
let currentQuality = 'auto';
let availableQualities = ['auto', '1080p', '720p', '480p', '360p'];

// Enhanced openVideoModal with quality selector
const originalOpenModal = openVideoModal;
openVideoModal = function(video) {
    // Create modal if it doesn't exist
    let modal = document.getElementById('videoModal');
    if (!modal) {
        modal = document.createElement('div');
        modal.id = 'videoModal';
        modal.className = 'video-modal';
        modal.innerHTML = `
            <div class="video-modal-content">
                <button class="close-modal" onclick="closeVideoModal()">✕</button>
                <div class="quality-badge">4K ULTRA HD</div>
                <div class="quality-loading">Changing quality...</div>
                <video id="modalVideo" controls autoplay controlsList="nodownload noremoteplayback" disablePictureInPicture disableRemotePlayback oncontextmenu="return false;">
                    <source src="" type="video/mp4">
                    Your browser does not support the video tag.
                </video>
                <div class="quality-selector">
                    <button class="quality-btn" onclick="toggleQualityMenu()">
                        <span id="currentQualityText">Auto</span>
                        <span>⚙️</span>
                    </button>
                    <div class="quality-menu" id="qualityMenu">
                        <div class="quality-option active" onclick="changeQuality('auto', this)">
                            <div class="quality-label">
                                <span class="quality-resolution">Auto</span>
                                <span class="quality-bitrate">Best available</span>
                            </div>
                        </div>
                        <div class="quality-option" onclick="changeQuality('1080p', this)">
                            <div class="quality-label">
                                <span class="quality-resolution">1080p</span>
                                <span class="quality-bitrate">Full HD</span>
                            </div>
                        </div>
                        <div class="quality-option" onclick="changeQuality('720p', this)">
                            <div class="quality-label">
                                <span class="quality-resolution">720p</span>
                                <span class="quality-bitrate">HD</span>
                            </div>
                        </div>
                        <div class="quality-option" onclick="changeQuality('480p', this)">
                            <div class="quality-label">
                                <span class="quality-resolution">480p</span>
                                <span class="quality-bitrate">SD</span>
                            </div>
                        </div>
                        <div class="quality-option" onclick="changeQuality('360p', this)">
                            <div class="quality-label">
                                <span class="quality-resolution">360p</span>
                                <span class="quality-bitrate">Low</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        document.body.appendChild(modal);
    }
    
    // Set video source and show modal
    const videoElement = document.getElementById('modalVideo');
    videoElement.src = video.videoUrl;
    modal.classList.add('active');
    
    // Store current video for quality changes
    window.currentVideo = video;
    
    // Prevent body scroll
    document.body.style.overflow = 'hidden';
    
    // Remove download button after video loads
    videoElement.addEventListener('loadedmetadata', function() {
        removeDownloadButton();
        console.log('Video loaded. Available quality: Auto (original)');
    });
    
    // Close modal on background click
    modal.onclick = function(e) {
        if (e.target === modal) {
            closeVideoModal();
        }
    };
};

// Replace the function reference
openVideoModal = originalOpenModal;

// Toggle quality menu
function toggleQualityMenu() {
    const menu = document.getElementById('qualityMenu');
    if (menu) {
        menu.classList.toggle('active');
    }
}

// Change video quality
function changeQuality(quality, element) {
    const videoElement = document.getElementById('modalVideo');
    const currentQualityText = document.getElementById('currentQualityText');
    const qualityLoading = document.querySelector('.quality-loading');
    const qualityMenu = document.getElementById('qualityMenu');
    
    if (!videoElement || !window.currentVideo) return;
    
    // Save current time and play state
    const currentTime = videoElement.currentTime;
    const wasPlaying = !videoElement.paused;
    
    // Show loading
    if (qualityLoading) {
        qualityLoading.classList.add('active');
    }
    
    // Update active state
    document.querySelectorAll('.quality-option').forEach(opt => {
        opt.classList.remove('active');
    });
    if (element) {
        element.classList.add('active');
    }
    
    // Update current quality display
    if (currentQualityText) {
        currentQualityText.textContent = quality.toUpperCase();
    }
    
    // Close menu
    if (qualityMenu) {
        qualityMenu.classList.remove('active');
    }
    
    // Simulate quality change (in production, you'd have different URLs for each quality)
    // For now, we're using the same video source
    setTimeout(() => {
        videoElement.currentTime = currentTime;
        if (wasPlaying) {
            videoElement.play();
        }
        
        // Hide loading
        if (qualityLoading) {
            qualityLoading.classList.remove('active');
        }
        
        console.log(`Quality changed to: ${quality}`);
        
        // Update quality badge
        const qualityBadge = document.querySelector('.quality-badge');
        if (qualityBadge) {
            const badgeText = quality === 'auto' ? '4K ULTRA HD' : 
                            quality === '1080p' ? 'FULL HD 1080P' :
                            quality === '720p' ? 'HD 720P' :
                            quality === '480p' ? 'SD 480P' : 'SD 360P';
            qualityBadge.textContent = badgeText;
        }
    }, 500);
    
    currentQuality = quality;
}

// Close quality menu when clicking outside
document.addEventListener('click', function(e) {
    const qualitySelector = document.querySelector('.quality-selector');
    const qualityMenu = document.getElementById('qualityMenu');
    
    if (qualitySelector && qualityMenu && !qualitySelector.contains(e.target)) {
        qualityMenu.classList.remove('active');
    }
});





// Enhanced openVideoModal with preview initialization







// Accurate Video Preview on Scrubber Hover
let previewCanvas = null;
let previewContext = null;
let previewContainer = null;
let previewVideo = null;
let hiddenPreviewVideo = null;
let isPreviewReady = false;
let rafId = null;
let isSeeking = false;

// Initialize video preview when modal opens
function initializeVideoPreview() {
    const modalVideo = document.getElementById('modalVideo');
    const modalContent = document.querySelector('.video-modal-content');
    
    if (!modalVideo || !modalContent) return;
    
    previewVideo = modalVideo;
    
    // Create preview container if it doesn't exist
    if (!previewContainer) {
        previewContainer = document.createElement('div');
        previewContainer.className = 'video-preview-container';
        previewContainer.innerHTML = `
            <div class="video-preview-thumbnail">
                <canvas id="previewCanvas"></canvas>
                <div class="video-preview-time">0:00</div>
            </div>
            <div class="video-preview-arrow"></div>
        `;
        modalContent.appendChild(previewContainer);
        
        previewCanvas = document.getElementById('previewCanvas');
        previewContext = previewCanvas.getContext('2d', { alpha: false, willReadFrequently: true });
        previewCanvas.width = 160;
        previewCanvas.height = 90;
    }
    
    // Create hidden video element for seeking preview
    if (!hiddenPreviewVideo) {
        hiddenPreviewVideo = document.createElement('video');
        hiddenPreviewVideo.style.display = 'none';
        hiddenPreviewVideo.src = modalVideo.src;
        hiddenPreviewVideo.muted = true;
        hiddenPreviewVideo.preload = 'auto';
        modalContent.appendChild(hiddenPreviewVideo);
        
        // Wait for hidden video to load
        hiddenPreviewVideo.addEventListener('loadeddata', () => {
            isPreviewReady = true;
            console.log('Preview video ready for seeking');
        });
    }
    
    // Add optimized mouse move listener
    modalVideo.addEventListener('mousemove', throttledVideoHover);
    modalVideo.addEventListener('mouseleave', hidePreview);
    modalContent.addEventListener('mousemove', throttledVideoHover);
}

// Throttled hover handler using requestAnimationFrame
function throttledVideoHover(e) {
    // Use requestAnimationFrame for smooth 60fps updates
    if (rafId) {
        cancelAnimationFrame(rafId);
    }
    
    rafId = requestAnimationFrame(() => {
        handleVideoHoverOptimized(e);
    });
}

// Optimized hover handler
function handleVideoHoverOptimized(e) {
    const modalVideo = document.getElementById('modalVideo');
    if (!modalVideo || modalVideo.duration === 0 || !isPreviewReady) return;
    
    const rect = modalVideo.getBoundingClientRect();
    const mouseX = e.clientX - rect.left;
    const mouseY = e.clientY - rect.top;
    
    // Show preview when hovering near bottom (controls area)
    const controlsHeight = 80;
    if (mouseY < rect.height - controlsHeight) {
        hidePreview();
        return;
    }
    
    // Calculate time based on mouse position
    const percentage = Math.max(0, Math.min(1, mouseX / rect.width));
    const previewTime = percentage * modalVideo.duration;
    
    // Show preview immediately
    showVideoPreviewAtTime(previewTime, e.clientX);
}

// Show video preview at specific time
function showVideoPreviewAtTime(time, xPosition) {
    if (!previewContainer || !previewCanvas || !previewContext || !hiddenPreviewVideo) return;
    
    // Show container immediately
    previewContainer.classList.add('active');
    previewContainer.style.left = xPosition + 'px';
    
    // Update timestamp immediately
    const timeDisplay = previewContainer.querySelector('.video-preview-time');
    if (timeDisplay) {
        timeDisplay.textContent = formatTime(time);
    }
    
    // Seek hidden video to preview time and capture frame
    if (!isSeeking && Math.abs(hiddenPreviewVideo.currentTime - time) > 0.5) {
        isSeeking = true;
        hiddenPreviewVideo.currentTime = time;
        
        // Wait for seek to complete
        hiddenPreviewVideo.addEventListener('seeked', function captureFrame() {
            try {
                previewContext.drawImage(hiddenPreviewVideo, 0, 0, previewCanvas.width, previewCanvas.height);
                isSeeking = false;
            } catch (error) {
                console.log('Preview draw error:', error);
                isSeeking = false;
            }
            hiddenPreviewVideo.removeEventListener('seeked', captureFrame);
        }, { once: true });
    }
}

// Hide preview
function hidePreview() {
    if (previewContainer) {
        previewContainer.classList.remove('active');
    }
    if (rafId) {
        cancelAnimationFrame(rafId);
        rafId = null;
    }
    isSeeking = false;
}

// Format time (seconds to MM:SS)
function formatTime(seconds) {
    if (isNaN(seconds)) return '0:00';
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return mins + ':' + (secs < 10 ? '0' : '') + secs;
}

// Enhanced openVideoModal with preview initialization
const originalOpenVideoModalPreview = openVideoModal;
openVideoModal = function(video) {
    originalOpenVideoModalPreview(video);
    
    // Initialize preview after video loads
    const modalVideo = document.getElementById('modalVideo');
    if (modalVideo) {
        modalVideo.addEventListener('loadeddata', () => {
            setTimeout(() => {
                initializeVideoPreview();
            }, 100);
        }, { once: true });
    }
};
