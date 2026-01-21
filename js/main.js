// Main JavaScript - CLOUDINARY VERSION
// Loads videos from cloud storage

const categoryIcons = {
    '18+': 'https://media.istockphoto.com/id/1432243860/vector/eighteen-or-older-persons-adult-content-18-plus-only-rating.jpg?s=612x612&w=0&k=20&c=XCAaLoMGXteF9CVzXdwqzGArsafVRS5-SWZapLrki8k=',
    'adult': 'https://media.istockphoto.com/id/1432243860/vector/eighteen-or-older-persons-adult-content-18-plus-only-rating.jpg?s=612x612&w=0&k=20&c=XCAaLoMGXteF9CVzXdwqzGArsafVRS5-SWZapLrki8k=',
    'entertainment': '🎬',
    'education': '📚',
    'music': '🎵',
    'sports': '⚽',
    'news': '📰',
    'technology': '💻',
    'default': '📺'
};

document.addEventListener('DOMContentLoaded', function() {
    loadVideos();
});

function getCategoryIcon(category) {
    const categoryLower = category.toLowerCase();
    const icon = categoryIcons[categoryLower] || categoryIcons['default'];
    
    if (icon.startsWith('http')) {
        return `<img src="${icon}" alt="${category}" class="category-icon-img">`;
    }
    return `<span class="category-icon-emoji">${icon}</span>`;
}

async function loadVideos() {
    try {
        const response = await fetch('/api/videos');
        const data = await response.json();
        const videos = data.videos || [];
        const categoriesContainer = document.getElementById('videoCategories');
        
        if (!categoriesContainer) return;
        
        console.log('Total videos loaded from cloud:', videos.length);
        
        if (videos.length === 0) {
            categoriesContainer.innerHTML = `
                <div class="empty-state">
                    <h3>No videos available yet</h3>
                    <p>Check back soon for new content!</p>
                </div>
            `;
            return;
        }
        
        const videosByCategory = {};
        videos.forEach(video => {
            if (!videosByCategory[video.category]) {
                videosByCategory[video.category] = [];
            }
            videosByCategory[video.category].push(video);
        });
        
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

function createCategorySection(category, videos) {
    const section = document.createElement('div');
    section.className = 'category-section';
    
    section.innerHTML = `
        <div class="video-grid">
            ${videos.map(video => createVideoCard(video)).join('')}
        </div>
    `;
    
    setTimeout(() => {
        section.querySelectorAll('.video-card').forEach((card, index) => {
            card.addEventListener('click', () => openVideoModal(videos[index]));
        });
        
        section.querySelectorAll('.video-duration').forEach((durationSpan) => {
            const videoUrl = durationSpan.getAttribute('data-video-url');
            if (videoUrl) {
                loadVideoDuration(videoUrl, durationSpan);
            }
        });
    }, 0);
    
    return section;
}

function createVideoCard(video) {
    const thumbnailSrc = video.thumbnail || 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="320" height="180"%3E%3Crect fill="%230f0f0f" width="320" height="180"/%3E%3Ctext fill="%23aaaaaa" font-size="20" font-family="Arial" x="50%25" y="50%25" text-anchor="middle" dy=".3em"%3E📹 Video%3C/text%3E%3C/svg%3E';
    
    const categoryIcon = getCategoryIcon(video.category);
    
    return `
        <div class="video-card" data-video-id="${video.id}">
            <div class="video-thumbnail-container">
                <img src="${thumbnailSrc}" alt="${video.title}" class="video-thumbnail" onerror="this.src='data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 width=%22320%22 height=%22180%22%3E%3Crect fill=%22%230f0f0f%22 width=%22320%22 height=%22180%22/%3E%3Ctext fill=%22%23aaaaaa%22 font-size=%2220%22 font-family=%22Arial%22 x=%2250%25%22 y=%2250%25%22 text-anchor=%22middle%22 dy=%22.3em%22%3E📹 Video%3C/text%3E%3C/svg%3E'">
                <div class="video-category-badge-circle">
                    ${categoryIcon}
                </div>
                <span class="video-duration" data-video-url="${video.videoUrl}">...</span>
            </div>
            <div class="video-info">
                <div>
                    <h4>${video.title}</h4>
                    <p>${video.description || 'No description available'}</p>
                </div>
            </div>
        </div>
    `;
}

function loadVideoDuration(videoUrl, durationElement) {
    const video = document.createElement('video');
    video.preload = 'metadata';
    
    video.addEventListener('loadedmetadata', function() {
        const duration = video.duration;
        const minutes = Math.floor(duration / 60);
        const seconds = Math.floor(duration % 60);
        const formattedDuration = `${minutes}:${seconds < 10 ? '0' : ''}${seconds}`;
        durationElement.textContent = formattedDuration;
    });
    
    video.addEventListener('error', function() {
        durationElement.textContent = '--:--';
    });
    
    video.src = videoUrl;
}

function openVideoModal(video) {
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
    
    const videoElement = document.getElementById('modalVideo');
    videoElement.src = video.videoUrl;
    modal.classList.add('active');
    
    document.body.style.overflow = 'hidden';
    
    modal.onclick = function(e) {
        if (e.target === modal) {
            closeVideoModal();
        }
    };
}

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

document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        closeVideoModal();
    }
});

document.addEventListener('contextmenu', function(e) {
    if (e.target.tagName === 'VIDEO') {
        e.preventDefault();
        return false;
    }
});

document.addEventListener('keydown', function(e) {
    if ((e.ctrlKey || e.metaKey) && e.key === 's') {
        e.preventDefault();
        return false;
    }
});

document.addEventListener('dragstart', function(e) {
    if (e.target.tagName === 'VIDEO') {
        e.preventDefault();
        return false;
    }
});
