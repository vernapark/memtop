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

// Check if user is logged in with the key-based authentication
function checkAuth() {
    const isAuthenticated = sessionStorage.getItem('adminAuthenticated');
    const authKey = sessionStorage.getItem('authKey');
    const currentPage = window.location.pathname;
    
    if (currentPage.includes('dashboard.html') && (!isAuthenticated || !authKey)) {
        // Redirect to secret admin login
        window.location.href = '../parking55009hvSweJimbs5hhinbd56y.html';
    }
}

// Initialize based on page
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
    const thumbnailFileInput = document.getElementById('thumbnailFile');
    
    if (uploadForm) {
        uploadForm.addEventListener('submit', handleVideoUpload);
        loadAdminVideos();
        
        // Initialize drag and drop ONLY for video zone
        initDragAndDrop();
        
        // Initialize paste functionality for thumbnails (ONLY paste, no drag/drop/click)
        initPasteSupport();
        
        // Update file name displays when files are selected
        if (videoFileInput) {
            videoFileInput.addEventListener('change', function() {
                const fileName = this.files[0] ? this.files[0].name : 'None';
                document.getElementById('selectedFileName').textContent = fileName;
            });
        }
        
        if (thumbnailFileInput) {
            thumbnailFileInput.addEventListener('change', function() {
                const fileName = this.files[0] ? this.files[0].name : 'None';
                document.getElementById('selectedThumbnailName').textContent = fileName;
            });
        }
        
        // Show storage info
        showStorageInfo();
    }
    
    if (logoutBtn) {
        logoutBtn.addEventListener('click', handleLogout);
    }
});

// Initialize paste support for thumbnail images - ONLY PASTE, NO DRAG/DROP
function initPasteSupport() {
    const thumbnailDropZone = document.getElementById('thumbnailDropZone');
    const thumbnailFileInput = document.getElementById('thumbnailFile');
    
    if (!thumbnailDropZone || !thumbnailFileInput) return;
    
    // Make the zone focusable
    thumbnailDropZone.setAttribute('tabindex', '0');
    thumbnailDropZone.style.outline = 'none';
    thumbnailDropZone.style.cursor = 'text';
    
    // Update the zone to show paste-only instruction
    thumbnailDropZone.innerHTML = `
        <div class="drop-zone-icon">📋</div>
        <div class="drop-zone-text">Paste Thumbnail Here</div>
        <div class="drop-zone-hint">Click here, then press Ctrl+V</div>
    `;
    
    // Add visual indication when focused
    thumbnailDropZone.addEventListener('focus', function() {
        this.style.boxShadow = '0 0 0 3px rgba(62, 166, 255, 0.5)';
        this.style.borderColor = '#3ea6ff';
    });
    
    thumbnailDropZone.addEventListener('blur', function() {
        this.style.boxShadow = 'none';
        this.style.borderColor = '#5d5d5d';
    });
    
    // REMOVE click to browse functionality - do nothing on click
    thumbnailDropZone.addEventListener('click', function(e) {
        e.stopPropagation();
        // Just focus the zone, don't open file picker
        this.focus();
    });
    
    // Add paste event listener ONLY to the thumbnail drop zone
    thumbnailDropZone.addEventListener('paste', function(e) {
        e.preventDefault();
        e.stopPropagation();
        
        // Get clipboard data
        const clipboardData = e.clipboardData || window.clipboardData;
        const items = clipboardData.items;
        
        if (!items) {
            showPasteNotification('⚠️ No clipboard data found', 'warning');
            return;
        }
        
        // Look for image in clipboard
        let foundImage = false;
        for (let i = 0; i < items.length; i++) {
            if (items[i].type.indexOf('image') !== -1) {
                foundImage = true;
                const blob = items[i].getAsFile();
                if (blob) {
                    // Create a File object from the blob
                    const fileName = `pasted-thumbnail-${Date.now()}.png`;
                    const file = new File([blob], fileName, { type: blob.type });
                    
                    // Set the file to the input
                    const dataTransfer = new DataTransfer();
                    dataTransfer.items.add(file);
                    thumbnailFileInput.files = dataTransfer.files;
                    
                    // Update file name display
                    document.getElementById('selectedThumbnailName').textContent = fileName;
                    
                    // Update drop zone UI to show success
                    thumbnailDropZone.innerHTML = `
                        <div class="drop-zone-icon">✅</div>
                        <div class="drop-zone-text" style="color: #7fff7f;">Image Pasted!</div>
                        <div class="drop-zone-hint">${fileName}</div>
                    `;
                    
                    console.log('Thumbnail pasted successfully:', fileName);
                    
                    // Show success notification
                    showPasteNotification('✅ Thumbnail pasted successfully!', 'success');
                }
                break;
            }
        }
        
        if (!foundImage) {
            showPasteNotification('⚠️ No image found in clipboard. Copy an image first!', 'warning');
        }
    });
    
    // Prevent drag and drop on thumbnail zone
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        thumbnailDropZone.addEventListener(eventName, function(e) {
            e.preventDefault();
            e.stopPropagation();
        }, false);
    });
}

// Show paste notification
function showPasteNotification(message, type = 'success') {
    const colors = {
        success: 'linear-gradient(135deg, #4CAF50, #45a049)',
        warning: 'linear-gradient(135deg, #ff9800, #f57c00)',
        error: 'linear-gradient(135deg, #f44336, #d32f2f)'
    };
    
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${colors[type]};
        color: white;
        padding: 15px 25px;
        border-radius: 8px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
        z-index: 10000;
        font-size: 14px;
        font-weight: 500;
        animation: slideIn 0.3s ease;
    `;
    notification.textContent = message;
    document.body.appendChild(notification);
    
    // Remove after 3 seconds
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Add CSS animations for notifications
if (!document.getElementById('pasteAnimations')) {
    const style = document.createElement('style');
    style.id = 'pasteAnimations';
    style.textContent = `
        @keyframes slideIn {
            from {
                transform: translateX(400px);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }
        @keyframes slideOut {
            from {
                transform: translateX(0);
                opacity: 1;
            }
            to {
                transform: translateX(400px);
                opacity: 0;
            }
        }
    `;
    document.head.appendChild(style);
}

// Show storage information
async function showStorageInfo() {
    const estimate = await videoStorage.getStorageEstimate();
    if (estimate) {
        console.log(`Storage: ${estimate.usage}MB / ${estimate.quota}MB (${estimate.usagePercent}%)`);
    }
}

// Initialize drag and drop functionality - ONLY FOR VIDEO
function initDragAndDrop() {
    const videoDropZone = document.getElementById('videoDropZone');
    const videoFileInput = document.getElementById('videoFile');
    
    if (!videoDropZone) return;
    
    // Setup video drop zone ONLY
    setupDropZone(videoDropZone, videoFileInput, 'video', {
        defaultIcon: '🎬',
        defaultText: 'Drag & Drop Video Here',
        defaultHint: 'or click to browse',
        successIcon: '✅',
        successText: 'Video Added',
        fileNameDisplay: 'selectedFileName'
    });
}

// Setup a drop zone with specific configuration
function setupDropZone(dropZone, fileInput, fileType, config) {
    // Prevent default drag behaviors
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
    });
    
    // Highlight drop zone when item is dragged over it
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
        
        // Find appropriate file type
        let targetFile = null;
        Array.from(files).forEach(file => {
            if (fileType === 'video' && file.type.startsWith('video/')) {
                targetFile = file;
            } else if (fileType === 'image' && file.type.startsWith('image/')) {
                targetFile = file;
            }
        });
        
        if (targetFile) {
            // Set the file to the input
            const dataTransfer = new DataTransfer();
            dataTransfer.items.add(targetFile);
            fileInput.files = dataTransfer.files;
            document.getElementById(config.fileNameDisplay).textContent = targetFile.name;
            
            // Update drop zone UI
            dropZone.innerHTML = `
                <div class="drop-zone-icon">${config.successIcon}</div>
                <div class="drop-zone-text" style="color: #7fff7f;">${config.successText}</div>
                <div class="drop-zone-hint">${targetFile.name.substring(0, 30)}${targetFile.name.length > 30 ? '...' : ''}</div>
            `;
        } else {
            alert(`Please drop a ${fileType} file.`);
        }
    }, false);
    
    // Make drop zone clickable to open file picker
    dropZone.addEventListener('click', () => {
        fileInput.click();
    });
}

// Prevent default drag behaviors
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

// Handle video upload
function handleVideoUpload(e) {
    e.preventDefault();
    
    if (!storageReady) {
        alert('Storage not ready. Please refresh the page.');
        return;
    }
    
    const title = document.getElementById('videoTitle').value;
    const description = document.getElementById('videoDescription').value;
    const category = document.getElementById('videoCategory').value;
    const videoFile = document.getElementById('videoFile').files[0];
    const thumbnailFile = document.getElementById('thumbnailFile').files[0];
    const statusMessage = document.getElementById('uploadStatus');
    
    if (!videoFile) {
        showStatus(statusMessage, 'Please select a video file', 'error');
        return;
    }
    
    // Show file size info
    const sizeMB = (videoFile.size / 1024 / 1024).toFixed(2);
    console.log(`Uploading video: ${videoFile.name} (${sizeMB}MB)`);
    
    // Set upload in progress
    uploadInProgress = true;
    
    // Disable submit button
    const submitBtn = e.target.querySelector('button[type="submit"]');
    submitBtn.disabled = true;
    submitBtn.textContent = 'Uploading...';
    
    // Show loading status
    showStatus(statusMessage, `⏳ Processing ${sizeMB}MB video... Please wait.`, 'success');
    
    // Read video file
    const videoReader = new FileReader();
    
    videoReader.onerror = function() {
        uploadInProgress = false;
        submitBtn.disabled = false;
        submitBtn.textContent = 'Upload Video';
        showStatus(statusMessage, '❌ Error reading video file', 'error');
    };
    
    videoReader.onload = function(e) {
        const videoUrl = e.target.result;
        
        // Read thumbnail if provided
        if (thumbnailFile) {
            const thumbnailReader = new FileReader();
            
            thumbnailReader.onerror = function() {
                uploadInProgress = false;
                submitBtn.disabled = false;
                submitBtn.textContent = 'Upload Video';
                showStatus(statusMessage, '❌ Error reading thumbnail', 'error');
            };
            
            thumbnailReader.onload = function(e) {
                const thumbnailUrl = e.target.result;
                saveVideo(title, description, category, videoUrl, thumbnailUrl, statusMessage, submitBtn);
            };
            
            thumbnailReader.readAsDataURL(thumbnailFile);
        } else {
            saveVideo(title, description, category, videoUrl, null, statusMessage, submitBtn);
        }
    };
    
    videoReader.readAsDataURL(videoFile);
}

// Save video using IndexedDB
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
        
        // Save to IndexedDB (no size limit!)
        await videoStorage.addVideo(newVideo);
        console.log('Video saved successfully:', newVideo.id);
        
        // Show storage info
        await showStorageInfo();
        
        uploadInProgress = false;
        submitBtn.disabled = false;
        submitBtn.textContent = 'Upload Video';
        
        showStatus(statusMessage, '✅ Video uploaded successfully!', 'success');
        
        // Reset form and reload videos
        document.getElementById('uploadForm').reset();
        document.getElementById('selectedFileName').textContent = 'None';
        document.getElementById('selectedThumbnailName').textContent = 'None';
        
        // Reset drop zones
        resetDropZones();
        
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
        showStatus(statusMessage, '❌ Upload failed: ' + error.message, 'error');
    }
}

// Reset drop zones to default state
function resetDropZones() {
    const videoDropZone = document.getElementById('videoDropZone');
    const thumbnailDropZone = document.getElementById('thumbnailDropZone');
    
    if (videoDropZone) {
        videoDropZone.innerHTML = `
            <div class="drop-zone-icon">🎬</div>
            <div class="drop-zone-text">Drag & Drop Video Here</div>
            <div class="drop-zone-hint">or click to browse</div>
        `;
    }
    
    if (thumbnailDropZone) {
        thumbnailDropZone.innerHTML = `
            <div class="drop-zone-icon">📋</div>
            <div class="drop-zone-text">Paste Thumbnail Here</div>
            <div class="drop-zone-hint">Click here, then press Ctrl+V</div>
        `;
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

// Preview video in modal
async function previewVideo(videoId) {
    try {
        const video = await videoStorage.getVideo(videoId);
        if (video) {
            const modal = document.createElement('div');
            modal.style.cssText = 'position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.95); z-index: 9999; display: flex; align-items: center; justify-content: center;';
            modal.innerHTML = `
                <div style="max-width: 90%; max-height: 90%; position: relative;">
                    <button onclick="this.parentElement.parentElement.remove()" style="position: absolute; top: 10px; right: 10px; background: rgba(0,0,0,0.8); color: white; border: 2px solid #fff; border-radius: 50%; width: 40px; height: 40px; font-size: 24px; cursor: pointer; z-index: 10000;">✕</button>
                    <video controls autoplay style="max-width: 100%; max-height: 90vh; border-radius: 8px;">
                        <source src="${video.videoUrl}" type="video/mp4">
                    </video>
                    <div style="color: white; margin-top: 10px; text-align: center;">
                        <h3>${video.title}</h3>
                        <p>${video.description || ''}</p>
                    </div>
                </div>
            `;
            document.body.appendChild(modal);
            modal.onclick = (e) => { if (e.target === modal) modal.remove(); };
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to preview video');
    }
}
