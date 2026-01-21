// Admin JavaScript for Video Streaming Site

// Track if upload is in progress
let uploadInProgress = false;

// Initialize storage on page load
let storageReady = false;

// Warn before leaving page during upload
window.addEventListener('beforeunload', function(e) {
    if (uploadInProgress) {
        e.preventDefault();
        e.returnValue = 'Upload in progress! Are you sure you want to leave?';
        return e.returnValue;
    }
});

// Check if user is logged in
function checkAuth() {
    const isAuthenticated = sessionStorage.getItem('adminAuthenticated');
    const authKey = sessionStorage.getItem('authKey');
    const currentPage = window.location.pathname;
    
    if (currentPage.includes('dashboard.html') && (!isAuthenticated || !authKey)) {
        window.location.href = '../parking55009hvSweJimbs5hhinbd56y.html';
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', async function() {
    checkAuth();
    
    // Initialize IndexedDB storage
    try {
        await videoStorage.init();
        storageReady = true;
        console.log('Storage initialized successfully');
    } catch (error) {
        console.error('Failed to initialize storage:', error);
        alert('Failed to initialize storage. Please refresh the page.');
        return;
    }
    
    const uploadForm = document.getElementById('uploadForm');
    const logoutBtn = document.getElementById('logoutBtn');
    const videoFileInput = document.getElementById('videoFile');
    
    if (uploadForm) {
        uploadForm.addEventListener('submit', handleVideoUpload);
        loadAdminVideos();
        
        // Initialize drag and drop for video only
        initDragAndDrop();
        
        // Update file name display when file is selected
        if (videoFileInput) {
            videoFileInput.addEventListener('change', function() {
                const fileName = this.files[0] ? this.files[0].name : 'None';
                document.getElementById('selectedFileName').textContent = fileName;
            });
        }
        
        // Show storage info
        showStorageInfo();
    }
    
    if (logoutBtn) {
        logoutBtn.addEventListener('click', handleLogout);
    }
});

// Show storage information
async function showStorageInfo() {
    const estimate = await videoStorage.getStorageEstimate();
    if (estimate) {
        console.log(`Storage: ${estimate.usage}MB / ${estimate.quota}MB (${estimate.usagePercent}%)`);
    }
}

// Initialize drag and drop for video
function initDragAndDrop() {
    const videoDropZone = document.getElementById('videoDropZone');
    const videoFileInput = document.getElementById('videoFile');
    
    if (!videoDropZone) return;
    
    setupDropZone(videoDropZone, videoFileInput);
}

// Setup drop zone
function setupDropZone(dropZone, fileInput) {
    // Prevent default drag behaviors
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
    });
    
    // Highlight drop zone
    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => {
            dropZone.classList.add('drag-over');
        }, false);
    });
    
    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, () => {
            dropZone.classList.remove('drag-over');
        }, false);
    });
    
    // Handle dropped files
    dropZone.addEventListener('drop', (e) => {
        const dt = e.dataTransfer;
        const files = dt.files;
        
        if (files.length === 0) return;
        
        // Find video file
        let targetFile = null;
        Array.from(files).forEach(file => {
            if (file.type.startsWith('video/')) {
                targetFile = file;
            }
        });
        
        if (targetFile) {
            const dataTransfer = new DataTransfer();
            dataTransfer.items.add(targetFile);
            fileInput.files = dataTransfer.files;
            document.getElementById('selectedFileName').textContent = targetFile.name;
            
            dropZone.innerHTML = `
                <div class="drop-zone-icon">âœ…</div>
                <div class="drop-zone-text" style="color: #7fff7f;">Video Added</div>
                <div class="drop-zone-hint">${targetFile.name.substring(0, 30)}${targetFile.name.length > 30 ? '...' : ''}</div>
            `;
        } else {
            alert('Please drop a video file.');
        }
    }, false);
    
    // Click to open file picker
    dropZone.addEventListener('click', () => {
        fileInput.click();
    });
}

function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

// Handle logout
function handleLogout(e) {
    e.preventDefault();
    
    if (uploadInProgress) {
        if (!confirm('Upload is in progress. Are you sure you want to logout?')) {
            return;
        }
    }
    
    sessionStorage.removeItem('adminAuthenticated');
    sessionStorage.removeItem('authKey');
    window.location.href = '../parking55009hvSweJimbs5hhinbd56y.html';
}

// Generate thumbnail from video
function generateThumbnailFromVideo(videoFile) {
    return new Promise((resolve, reject) => {
        const video = document.createElement('video');
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        
        video.preload = 'metadata';
        video.muted = true;
        video.playsInline = true;
        
        video.onloadedmetadata = function() {
            // Seek to 2 seconds or 10% of video duration
            const seekTime = Math.min(2, video.duration * 0.1);
            video.currentTime = seekTime;
        };
        
        video.onseeked = function() {
            // Set canvas size to video dimensions
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            
            // Draw video frame to canvas
            ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
            
            // Convert canvas to data URL
            const thumbnailDataUrl = canvas.toDataURL('image/jpeg', 0.8);
            
            // Clean up
            video.src = '';
            
            resolve(thumbnailDataUrl);
        };
        
        video.onerror = function() {
            reject(new Error('Failed to load video for thumbnail generation'));
        };
        
        // Load video
        video.src = URL.createObjectURL(videoFile);
    });
}

// Handle video upload
async function handleVideoUpload(e) {
    e.preventDefault();
    
    if (!storageReady) {
        alert('Storage not ready. Please refresh the page.');
        return;
    }
    
    const title = document.getElementById('videoTitle').value;
    const description = document.getElementById('videoDescription').value;
    const category = document.getElementById('videoCategory').value;
    const videoFile = document.getElementById('videoFile').files[0];
    const statusMessage = document.getElementById('uploadStatus');
    
    if (!videoFile) {
        showStatus(statusMessage, 'Please select a video file', 'error');
        return;
    }
    
    const sizeMB = (videoFile.size / 1024 / 1024).toFixed(2);
    console.log(`Uploading video: ${videoFile.name} (${sizeMB}MB)`);
    
    uploadInProgress = true;
    
    const submitBtn = e.target.querySelector('button[type="submit"]');
    submitBtn.disabled = true;
    submitBtn.textContent = 'Processing...';
    
    showStatus(statusMessage, `â³ Generating thumbnail and processing ${sizeMB}MB video...`, 'success');
    
    try {
        // Generate thumbnail from video
        const thumbnailUrl = await generateThumbnailFromVideo(videoFile);
        console.log('Thumbnail generated successfully');
        
        showStatus(statusMessage, `â³ Uploading video...`, 'success');
        
        // Read video file
        const videoReader = new FileReader();
        
        videoReader.onload = function(e) {
            const videoUrl = e.target.result;
            saveVideo(title, description, category, videoUrl, thumbnailUrl, statusMessage, submitBtn);
        };
        
        videoReader.onerror = function() {
            uploadInProgress = false;
            submitBtn.disabled = false;
            submitBtn.textContent = 'Upload Video';
            showStatus(statusMessage, 'âŒ Error reading video file', 'error');
        };
        
        videoReader.readAsDataURL(videoFile);
        
    } catch (error) {
        console.error('Thumbnail generation error:', error);
        uploadInProgress = false;
        submitBtn.disabled = false;
        submitBtn.textContent = 'Upload Video';
        showStatus(statusMessage, 'âŒ Failed to generate thumbnail: ' + error.message, 'error');
    }
}

// Save video
async function saveVideo(title, description, category, videoUrl, thumbnailUrl, statusMessage, submitBtn) {
    try {
        const newVideo = {
            id: Date.now().toString(),
            title: title,
            description: description,
            category: category,
            videoUrl: videoUrl,
            thumbnail: thumbnailUrl,
            uploadDate: new Date().toISOString()
        };
        
        await videoStorage.addVideo(newVideo);
        console.log('Video saved successfully:', newVideo.id);
        
        await showStorageInfo();
        
        uploadInProgress = false;
        submitBtn.disabled = false;
        submitBtn.textContent = 'Upload Video';
        
        showStatus(statusMessage, 'âœ… Video uploaded successfully with auto-generated thumbnail!', 'success');
        
        // Reset form
        document.getElementById('uploadForm').reset();
        document.getElementById('selectedFileName').textContent = 'None';
        
        // Reset drop zone
        const videoDropZone = document.getElementById('videoDropZone');
        if (videoDropZone) {
            videoDropZone.innerHTML = `
                <div class="drop-zone-icon">ðŸŽ¬</div>
                <div class="drop-zone-text">Drag & Drop Video Here</div>
                <div class="drop-zone-hint">Thumbnail will be auto-generated from video</div>
            `;
        }
        
        setTimeout(() => {
            loadAdminVideos();
            statusMessage.textContent = '';
            statusMessage.className = 'status-message';
        }, 2000);
        
    } catch (error) {
        console.error('Upload error:', error);
        uploadInProgress = false;
        submitBtn.disabled = false;
        submitBtn.textContent = 'Upload Video';
        showStatus(statusMessage, 'âŒ Upload failed: ' + error.message, 'error');
    }
}

// Load videos in admin panel
async function loadAdminVideos() {
    if (!storageReady) return;
    
    try {
        const videos = await videoStorage.getAllVideos();
        const videoList = document.getElementById('adminVideoList');
        
        if (!videoList) return;
        
        if (videos.length === 0) {
            videoList.innerHTML = `
                <div class="empty-state">
                    <h3>No videos uploaded yet</h3>
                    <p>Upload your first video using the form above</p>
                </div>
            `;
            return;
        }
        
        videoList.innerHTML = videos.map(video => `
            <div class="admin-video-item">
                <div class="video-item-info">
                    <h4>${video.title}</h4>
                    <p><strong>Category:</strong> ${video.category}</p>
                    <p>${video.description || 'No description'}</p>
                    <p><small>Uploaded: ${new Date(video.uploadDate).toLocaleDateString()}</small></p>
                </div>
                <button class="btn-danger" onclick="deleteVideo('${video.id}')">Delete</button>
            </div>
        `).join('');
    } catch (error) {
        console.error('Error loading videos:', error);
    }
}

// Delete video
async function deleteVideo(videoId) {
    if (!confirm('Are you sure you want to delete this video?')) {
        return;
    }
    
    try {
        await videoStorage.deleteVideo(videoId);
        loadAdminVideos();
    } catch (error) {
        console.error('Error deleting video:', error);
        alert('Failed to delete video');
    }
}

// Show status message
function showStatus(element, message, type) {
    element.textContent = message;
    element.className = `status-message ${type}`;
}

