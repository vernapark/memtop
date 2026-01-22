// Admin JavaScript - BULLETPROOF VERSION
// Fixed: Robust thumbnail generation with multiple fallbacks

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

// BULLETPROOF THUMBNAIL GENERATION
function generateThumbnailFromVideo(videoFile) {
    return new Promise((resolve, reject) => {
        const video = document.createElement('video');
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        
        let hasResolved = false;
        let seekAttempts = 0;
        const maxSeekAttempts = 3;
        const timeoutDuration = 10000; // 10 seconds
        
        // Timeout fallback - generate blank thumbnail
        const timeoutId = setTimeout(() => {
            if (!hasResolved) {
                console.warn('Thumbnail generation timeout - creating blank thumbnail');
                hasResolved = true;
                cleanup();
                resolve(createBlankThumbnail());
            }
        }, timeoutDuration);
        
        function cleanup() {
            clearTimeout(timeoutId);
            try {
                video.pause();
                video.src = '';
                video.load();
                URL.revokeObjectURL(video.src);
            } catch (e) {
                console.warn('Cleanup warning:', e);
            }
        }
        
        function trySeekToTime(time) {
            seekAttempts++;
            console.log(`Attempting thumbnail at ${time}s (attempt ${seekAttempts}/${maxSeekAttempts})`);
            
            try {
                video.currentTime = time;
            } catch (e) {
                console.error('Seek error:', e);
                if (seekAttempts >= maxSeekAttempts && !hasResolved) {
                    hasResolved = true;
                    cleanup();
                    resolve(createBlankThumbnail());
                }
            }
        }
        
        video.preload = 'metadata';
        video.muted = true;
        video.playsInline = true;
        video.crossOrigin = 'anonymous';
        
        // Handle successful metadata load
        video.onloadedmetadata = function() {
            console.log('Video metadata loaded:', {
                duration: video.duration,
                width: video.videoWidth,
                height: video.videoHeight
            });
            
            if (!video.duration || video.duration === Infinity || isNaN(video.duration)) {
                console.warn('Invalid video duration, trying to load first frame');
                trySeekToTime(0);
            } else {
                // Try multiple seek positions
                const seekTime = Math.min(2, video.duration * 0.1);
                trySeekToTime(seekTime);
            }
        };
        
        // Handle successful seek
        video.onseeked = function() {
            if (hasResolved) return;
            
            console.log('Video seeked successfully');
            
            try {
                // Set canvas size (handle 0 dimensions)
                const width = video.videoWidth || 1280;
                const height = video.videoHeight || 720;
                canvas.width = width;
                canvas.height = height;
                
                // Draw video frame (or blank if video is black)
                ctx.fillStyle = '#000000';
                ctx.fillRect(0, 0, canvas.width, canvas.height);
                
                if (video.videoWidth > 0 && video.videoHeight > 0) {
                    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
                } else {
                    console.warn('Video has no dimensions, creating blank thumbnail');
                }
                
                // Add text overlay for blank videos
                ctx.fillStyle = '#ffffff';
                ctx.font = '48px Arial';
                ctx.textAlign = 'center';
                ctx.textBaseline = 'middle';
                ctx.fillText('🎬', canvas.width / 2, canvas.height / 2);
                
                // Convert to blob
                canvas.toBlob((blob) => {
                    if (blob && !hasResolved) {
                        hasResolved = true;
                        cleanup();
                        console.log('Thumbnail generated successfully');
                        resolve(blob);
                    } else if (!hasResolved) {
                        // Try another seek position
                        if (seekAttempts < maxSeekAttempts && video.duration > 0) {
                            const nextTime = Math.min(video.duration * 0.5, 5);
                            trySeekToTime(nextTime);
                        } else {
                            hasResolved = true;
                            cleanup();
                            resolve(createBlankThumbnail());
                        }
                    }
                }, 'image/jpeg', 0.8);
                
            } catch (e) {
                console.error('Canvas error:', e);
                if (!hasResolved) {
                    hasResolved = true;
                    cleanup();
                    resolve(createBlankThumbnail());
                }
            }
        };
        
        // Handle video errors
        video.onerror = function(e) {
            console.error('Video load error:', e, video.error);
            if (!hasResolved) {
                hasResolved = true;
                cleanup();
                // Don't reject - use blank thumbnail as fallback
                resolve(createBlankThumbnail());
            }
        };
        
        // Handle loadeddata event as additional trigger
        video.onloadeddata = function() {
            console.log('Video data loaded');
        };
        
        // Start loading video
        try {
            const videoURL = URL.createObjectURL(videoFile);
            video.src = videoURL;
            video.load();
        } catch (e) {
            console.error('Error creating object URL:', e);
            if (!hasResolved) {
                hasResolved = true;
                cleanup();
                resolve(createBlankThumbnail());
            }
        }
    });
}

// Create blank thumbnail as fallback
function createBlankThumbnail() {
    console.log('Creating blank thumbnail');
    const canvas = document.createElement('canvas');
    canvas.width = 1280;
    canvas.height = 720;
    const ctx = canvas.getContext('2d');
    
    // Black background
    ctx.fillStyle = '#000000';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    // Add icon
    ctx.fillStyle = '#ffffff';
    ctx.font = 'bold 120px Arial';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText('🎬', canvas.width / 2, canvas.height / 2);
    
    // Add text
    ctx.font = '36px Arial';
    ctx.fillText('Video Thumbnail', canvas.width / 2, canvas.height / 2 + 100);
    
    return new Promise((resolve) => {
        canvas.toBlob((blob) => {
            resolve(blob || new Blob([''], { type: 'image/jpeg' }));
        }, 'image/jpeg', 0.8);
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
    
    showStatus(statusMessage, '⏳ Generating thumbnail (this may take a moment)...', 'success');
    
    try {
        // Generate thumbnail with bulletproof fallback
        const thumbnailBlob = await generateThumbnailFromVideo(videoFile);
        console.log('Thumbnail blob size:', thumbnailBlob.size);
        
        showStatus(statusMessage, `⏳ Uploading ${sizeMB}MB to cloud...`, 'success');
        
        // Use FormData for multipart/form-data
        const formData = new FormData();
        formData.append('videoFile', videoFile);
        formData.append('thumbnail', thumbnailBlob, 'thumbnail.jpg');
        formData.append('videoTitle', title);
        formData.append('videoDescription', description);
        formData.append('videoCategory', category);
        
        const response = await fetch('/api/upload-video', {
            method: 'POST',
            body: formData
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
        
        // Show statistics if available
        if (data.statistics) {
            const stats = data.statistics;
            const statsHtml = `
                <div style="background: #1a1a1a; padding: 16px; border-radius: 8px; margin-bottom: 20px; border: 1px solid #3f3f3f;">
                    <h3 style="margin: 0 0 12px 0; color: #3ea6ff;">📊 Storage Statistics</h3>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 12px;">
                        <div>
                            <div style="color: #aaa; font-size: 0.9rem;">Total Videos</div>
                            <div style="font-size: 1.5rem; font-weight: 600; color: #fff;">${stats.total_videos}</div>
                        </div>
                        <div>
                            <div style="color: #aaa; font-size: 0.9rem;">Active Accounts</div>
                            <div style="font-size: 1.5rem; font-weight: 600; color: #7fff7f;">${stats.active_accounts} / ${stats.total_accounts}</div>
                        </div>
                        ${Object.entries(stats.videos_per_account || {}).map(([account, count]) => `
                            <div>
                                <div style="color: #aaa; font-size: 0.9rem;">${account}</div>
                                <div style="font-size: 1.5rem; font-weight: 600; color: #3ea6ff;">${count} videos</div>
                            </div>
                        `).join('')}
                    </div>
                </div>
            `;
            videoList.innerHTML = statsHtml;
        }
        
        videoList.innerHTML += videos.map(video => `
            <div class="admin-video-item">
                <div class="video-item-info">
                    <h4>${video.title}</h4>
                    <p><strong>Category:</strong> ${video.category}</p>
                    ${video.cloudinary_account ? `<p><strong>Storage:</strong> ${video.cloudinary_account}</p>` : ''}
                    <p>${video.description || 'No description'}</p>
                    <p><small>Uploaded: ${new Date(video.uploadDate).toLocaleDateString()}</small></p>
                </div>
                <button class="btn-danger" onclick="deleteVideo('${video.id}', '${video.cloudinary_cloud_name || ''}')">Delete</button>
            </div>
        `).join('');
    } catch (error) {
        console.error('Error loading videos:', error);
    }
}

async function deleteVideo(videoId, cloudName = '') {
    if (!confirm('Are you sure you want to delete this video?')) {
        return;
    }
    
    try {
        const response = await fetch('/api/delete-video', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ 
                id: videoId,
                cloudinary_cloud_name: cloudName 
            })
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
