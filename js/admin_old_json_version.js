// Admin JavaScript - CLOUDINARY VERSION
// All features preserved, now uploads to cloud storage

let uploadInProgress = false;

window.addEventListener('beforeunload', function(e) {
    if (uploadInProgress) {
        e.preventDefault();
        e.returnValue = 'Upload in progress! Are you sure you want to leave?';
        return e.returnValue;
    }
});

function checkAuth() {
    const isAuthenticated = sessionStorage.getItem('adminAuthenticated');
    const authKey = sessionStorage.getItem('authKey');
    const currentPage = window.location.pathname;
    
    if (currentPage.includes('dashboard.html') && (!isAuthenticated || !authKey)) {
        window.location.href = '../parking55009hvSweJimbs5hhinbd56y.html';
    }
}

document.addEventListener('DOMContentLoaded', function() {
    checkAuth();
    
    const uploadForm = document.getElementById('uploadForm');
    const logoutBtn = document.getElementById('logoutBtn');
    const videoFileInput = document.getElementById('videoFile');
    
    if (uploadForm) {
        uploadForm.addEventListener('submit', handleVideoUpload);
        loadAdminVideos();
        initDragAndDrop();
        
        if (videoFileInput) {
            videoFileInput.addEventListener('change', function() {
                const fileName = this.files[0] ? this.files[0].name : 'None';
                document.getElementById('selectedFileName').textContent = fileName;
            });
        }
    }
    
    if (logoutBtn) {
        logoutBtn.addEventListener('click', handleLogout);
    }
});

function initDragAndDrop() {
    const videoDropZone = document.getElementById('videoDropZone');
    const videoFileInput = document.getElementById('videoFile');
    
    if (!videoDropZone) return;
    
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        videoDropZone.addEventListener(eventName, preventDefaults, false);
    });
    
    ['dragenter', 'dragover'].forEach(eventName => {
        videoDropZone.addEventListener(eventName, () => {
            videoDropZone.classList.add('drag-over');
        }, false);
    });
    
    ['dragleave', 'drop'].forEach(eventName => {
        videoDropZone.addEventListener(eventName, () => {
            videoDropZone.classList.remove('drag-over');
        }, false);
    });
    
    videoDropZone.addEventListener('drop', (e) => {
        const files = e.dataTransfer.files;
        if (files.length === 0) return;
        
        let targetFile = null;
        Array.from(files).forEach(file => {
            if (file.type.startsWith('video/')) {
                targetFile = file;
            }
        });
        
        if (targetFile) {
            const dataTransfer = new DataTransfer();
            dataTransfer.items.add(targetFile);
            videoFileInput.files = dataTransfer.files;
            document.getElementById('selectedFileName').textContent = targetFile.name;
            
            videoDropZone.innerHTML = `
                <div class="drop-zone-icon">✅</div>
                <div class="drop-zone-text" style="color: #7fff7f;">Video Added</div>
                <div class="drop-zone-hint">${targetFile.name.substring(0, 30)}</div>
            `;
        } else {
            alert('Please drop a video file.');
        }
    }, false);
    
    videoDropZone.addEventListener('click', () => {
        videoFileInput.click();
    });
}

function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

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

function generateThumbnailFromVideo(videoFile) {
    return new Promise((resolve, reject) => {
        const video = document.createElement('video');
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        
        video.preload = 'metadata';
        video.muted = true;
        video.playsInline = true;
        
        video.onloadedmetadata = function() {
            const seekTime = Math.min(2, video.duration * 0.1);
            video.currentTime = seekTime;
        };
        
        video.onseeked = function() {
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
            const thumbnailDataUrl = canvas.toDataURL('image/jpeg', 0.8);
            video.src = '';
            resolve(thumbnailDataUrl);
        };
        
        video.onerror = function() {
            reject(new Error('Failed to load video for thumbnail generation'));
        };
        
        video.src = URL.createObjectURL(videoFile);
    });
}

async function handleVideoUpload(e) {
    e.preventDefault();
    
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
    console.log(`Uploading video to cloud: ${videoFile.name} (${sizeMB}MB)`);
    
    uploadInProgress = true;
    const submitBtn = e.target.querySelector('button[type="submit"]');
    submitBtn.disabled = true;
    submitBtn.textContent = 'Processing...';
    
    showStatus(statusMessage, '⏳ Generating thumbnail...', 'success');
    
    try {
        const thumbnailData = await generateThumbnailFromVideo(videoFile);
        showStatus(statusMessage, `⏳ Uploading ${sizeMB}MB to cloud...`, 'success');
        
        const videoReader = new FileReader();
        videoReader.onload = async function(e) {
            try {
                const response = await fetch('/api/upload-video', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        videoData: e.target.result,
                        thumbnailData: thumbnailData,
                        title: title,
                        description: description,
                        category: category
                    })
                });
                
                const result = await response.json();
                
                if (result.success) {
                    showStatus(statusMessage, '✅ Video uploaded to cloud successfully!', 'success');
                    document.getElementById('uploadForm').reset();
                    document.getElementById('selectedFileName').textContent = 'None';
                    
                    const videoDropZone = document.getElementById('videoDropZone');
                    if (videoDropZone) {
                        videoDropZone.innerHTML = `
                            <div class="drop-zone-icon">🎬</div>
                            <div class="drop-zone-text">Drag & Drop Video Here</div>
                            <div class="drop-zone-hint">Thumbnail will be auto-generated from video</div>
                        `;
                    }
                    
                    setTimeout(() => {
                        loadAdminVideos();
                        statusMessage.textContent = '';
                        statusMessage.className = 'status-message';
                    }, 2000);
                } else {
                    throw new Error(result.error || 'Upload failed');
                }
            } catch (error) {
                console.error('Upload error:', error);
                showStatus(statusMessage, '❌ Upload failed: ' + error.message, 'error');
            } finally {
                uploadInProgress = false;
                submitBtn.disabled = false;
                submitBtn.textContent = 'Upload Video';
            }
        };
        
        videoReader.onerror = function() {
            uploadInProgress = false;
            submitBtn.disabled = false;
            submitBtn.textContent = 'Upload Video';
            showStatus(statusMessage, '❌ Error reading video file', 'error');
        };
        
        videoReader.readAsDataURL(videoFile);
        
    } catch (error) {
        console.error('Error:', error);
        uploadInProgress = false;
        submitBtn.disabled = false;
        submitBtn.textContent = 'Upload Video';
        showStatus(statusMessage, '❌ Failed: ' + error.message, 'error');
    }
}

async function loadAdminVideos() {
    try {
        const response = await fetch('/api/videos');
        const data = await response.json();
        const videos = data.videos || [];
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

async function deleteVideo(videoId) {
    if (!confirm('Are you sure you want to delete this video?')) {
        return;
    }
    
    try {
        const response = await fetch('/api/delete-video', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ id: videoId })
        });
        
        const result = await response.json();
        
        if (result.success) {
            loadAdminVideos();
        } else {
            alert('Failed to delete video: ' + result.error);
        }
    } catch (error) {
        console.error('Error deleting video:', error);
        alert('Failed to delete video');
    }
}

function showStatus(element, message, type) {
    element.textContent = message;
    element.className = `status-message ${type}`;
}
