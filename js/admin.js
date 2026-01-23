// Admin JavaScript - Multiple Upload with Cloudinary API Integration
console.log('🚀 Admin Multi-Upload with Cloudinary - LOADED');

// Selected files array
let selectedFiles = [];
let isUploading = false;

// Generate random alphanumeric title (7-8 words)
function generateAlphanumericTitle() {
    const words = [
        'Alpha', 'Beta', 'Gamma', 'Delta', 'Sigma', 'Omega', 'Zeta', 'Theta',
        'Prime', 'Ultra', 'Super', 'Mega', 'Hyper', 'Turbo', 'Nitro', 'Blaze',
        'Storm', 'Flash', 'Bolt', 'Nova', 'Cosmic', 'Stellar', 'Lunar', 'Solar',
        'Phoenix', 'Dragon', 'Tiger', 'Eagle', 'Hawk', 'Wolf', 'Bear', 'Lion',
        'Crystal', 'Diamond', 'Ruby', 'Jade', 'Pearl', 'Gold', 'Silver', 'Platinum',
        'Fire', 'Ice', 'Water', 'Earth', 'Wind', 'Thunder', 'Lightning', 'Shadow',
        'Mystic', 'Magic', 'Power', 'Force', 'Energy', 'Spirit', 'Soul', 'Mind',
        'Cyber', 'Digital', 'Virtual', 'Quantum', 'Neural', 'Fusion', 'Matrix', 'Nexus',
        'Royal', 'Epic', 'Legend', 'Hero', 'Champion', 'Master', 'Elite', 'Supreme',
        'Neon', 'Laser', 'Pulse', 'Wave', 'Echo', 'Vortex', 'Infinity', 'Zenith'
    ];
    
    const numbers = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0', 
                     '10', '20', '30', '50', '99', '100', '777', '888', '999'];
    
    const wordCount = Math.random() < 0.5 ? 7 : 8;
    const titleParts = [];
    
    for (let i = 0; i < wordCount; i++) {
        if (Math.random() < 0.6) {
            titleParts.push(words[Math.floor(Math.random() * words.length)]);
        } else {
            titleParts.push(numbers[Math.floor(Math.random() * numbers.length)]);
        }
    }
    
    return titleParts.join(' ');
}

// Generate thumbnail from video
function generateThumbnailFromVideo(videoFile) {
    return new Promise((resolve, reject) => {
        const video = document.createElement('video');
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        
        let hasResolved = false;
        const timeoutDuration = 10000;
        
        const timeoutId = setTimeout(() => {
            if (!hasResolved) {
                console.warn('Thumbnail timeout - creating blank thumbnail');
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
                URL.revokeObjectURL(video.src);
            } catch (e) {}
        }
        
        video.preload = 'metadata';
        video.muted = true;
        video.playsInline = true;
        
        video.onloadedmetadata = function() {
            const seekTime = Math.min(2, video.duration * 0.1);
            try {
                video.currentTime = seekTime;
            } catch (e) {
                if (!hasResolved) {
                    hasResolved = true;
                    cleanup();
                    resolve(createBlankThumbnail());
                }
            }
        };
        
        video.onseeked = function() {
            if (hasResolved) return;
            
            try {
                const width = video.videoWidth || 1280;
                const height = video.videoHeight || 720;
                canvas.width = width;
                canvas.height = height;
                
                ctx.fillStyle = '#000000';
                ctx.fillRect(0, 0, canvas.width, canvas.height);
                
                if (video.videoWidth > 0 && video.videoHeight > 0) {
                    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
                }
                
                canvas.toBlob((blob) => {
                    if (blob && !hasResolved) {
                        hasResolved = true;
                        cleanup();
                        resolve(blob);
                    } else if (!hasResolved) {
                        hasResolved = true;
                        cleanup();
                        resolve(createBlankThumbnail());
                    }
                }, 'image/jpeg', 0.8);
                
            } catch (e) {
                if (!hasResolved) {
                    hasResolved = true;
                    cleanup();
                    resolve(createBlankThumbnail());
                }
            }
        };
        
        video.onerror = function() {
            if (!hasResolved) {
                hasResolved = true;
                cleanup();
                resolve(createBlankThumbnail());
            }
        };
        
        try {
            video.src = URL.createObjectURL(videoFile);
            video.load();
        } catch (e) {
            if (!hasResolved) {
                hasResolved = true;
                cleanup();
                resolve(createBlankThumbnail());
            }
        }
    });
}

function createBlankThumbnail() {
    const canvas = document.createElement('canvas');
    canvas.width = 1280;
    canvas.height = 720;
    const ctx = canvas.getContext('2d');
    
    ctx.fillStyle = '#000000';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = '#ffffff';
    ctx.font = 'bold 120px Arial';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText('🎬', canvas.width / 2, canvas.height / 2);
    
    return new Promise((resolve) => {
        canvas.toBlob((blob) => {
            resolve(blob || new Blob([''], { type: 'image/jpeg' }));
        }, 'image/jpeg', 0.8);
    });
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    console.log('🎬 Admin Panel Initialized - Multi-Upload with Cloudinary');
    
    const videoDropZone = document.getElementById('videoDropZone');
    const videoFileInput = document.getElementById('videoFile');
    const uploadForm = document.getElementById('uploadForm');
    const selectedFilesContainer = document.getElementById('selectedFilesContainer');
    const selectedFilesList = document.getElementById('selectedFilesList');
    const fileCount = document.getElementById('fileCount');
    const uploadBtn = document.getElementById('uploadBtn');
    const uploadProgressContainer = document.getElementById('uploadProgressContainer');
    const uploadProgressList = document.getElementById('uploadProgressList');
    
    if (videoDropZone) {
        videoDropZone.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            if (videoFileInput) videoFileInput.click();
        });
        
        videoDropZone.style.cursor = 'pointer';
        
        videoDropZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            e.stopPropagation();
            videoDropZone.classList.add('drag-over');
        });
        
        videoDropZone.addEventListener('dragleave', (e) => {
            e.preventDefault();
            e.stopPropagation();
            videoDropZone.classList.remove('drag-over');
        });
        
        videoDropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            e.stopPropagation();
            videoDropZone.classList.remove('drag-over');
            
            const files = Array.from(e.dataTransfer.files).filter(file => file.type.startsWith('video/'));
            if (files.length > 0) {
                addFiles(files);
            }
        });
    }
    
    if (videoFileInput) {
        videoFileInput.addEventListener('change', (e) => {
            const files = Array.from(e.target.files);
            if (files.length > 0) addFiles(files);
        });
    }
    
    function addFiles(files) {
        const videoFiles = files.filter(file => file.type.startsWith('video/'));
        if (videoFiles.length === 0) {
            showStatus('⚠️ No valid video files selected', 'error');
            return;
        }
        
        selectedFiles = [...selectedFiles, ...videoFiles];
        updateSelectedFilesList();
        showStatus(`✅ ${videoFiles.length} video(s) added`, 'success');
    }
    
    function updateSelectedFilesList() {
        if (selectedFiles.length === 0) {
            if (selectedFilesContainer) selectedFilesContainer.style.display = 'none';
            return;
        }
        
        if (selectedFilesContainer) selectedFilesContainer.style.display = 'block';
        if (fileCount) fileCount.textContent = selectedFiles.length;
        
        if (selectedFilesList) {
            selectedFilesList.innerHTML = selectedFiles.map((file, index) => `
                <div class="file-item">
                    <span class="file-item-name">📹 ${file.name} (${formatFileSize(file.size)})</span>
                    <button type="button" class="file-item-remove" onclick="removeFile(${index})">Remove</button>
                </div>
            `).join('');
        }
    }
    
    window.removeFile = function(index) {
        selectedFiles.splice(index, 1);
        updateSelectedFilesList();
    };
    
    function formatFileSize(bytes) {
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
    }
    
    if (uploadForm) {
        uploadForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            e.stopPropagation();
            
            if (isUploading) {
                showStatus('⚠️ Upload already in progress', 'warning');
                return;
            }
            
            if (selectedFiles.length === 0) {
                showStatus('⚠️ Please select at least one video file', 'error');
                return;
            }
            
            const category = document.getElementById('videoCategory').value;
            if (!category) {
                showStatus('⚠️ Please select a category', 'error');
                return;
            }
            
            isUploading = true;
            if (uploadBtn) {
                uploadBtn.disabled = true;
                uploadBtn.textContent = `Uploading ${selectedFiles.length} video(s)...`;
            }
            
            if (uploadProgressContainer) uploadProgressContainer.style.display = 'block';
            if (uploadProgressList) uploadProgressList.innerHTML = '';
            
            console.log(`🚀 Starting parallel upload of ${selectedFiles.length} videos to Cloudinary`);
            showStatus(`🚀 Uploading ${selectedFiles.length} video(s) to Cloudinary...`, 'info');
            
            const uploadPromises = selectedFiles.map((file, index) => 
                uploadSingleVideoToCloudinary(file, category, index)
            );
            
            try {
                const results = await Promise.all(uploadPromises);
                const successCount = results.filter(r => r.success).length;
                const failCount = results.length - successCount;
                
                if (failCount === 0) {
                    showStatus(`✅ All ${successCount} videos uploaded to Cloudinary!`, 'success');
                } else {
                    showStatus(`⚠️ ${successCount} succeeded, ${failCount} failed`, 'warning');
                }
                
                selectedFiles = [];
                updateSelectedFilesList();
                if (videoFileInput) videoFileInput.value = '';
                
                setTimeout(() => loadVideos(), 1000);
                
            } catch (error) {
                console.error('Upload error:', error);
                showStatus('❌ Upload failed: ' + error.message, 'error');
            } finally {
                isUploading = false;
                if (uploadBtn) {
                    uploadBtn.disabled = false;
                    uploadBtn.textContent = 'Upload All Videos';
                }
            }
        });
    }
    
    async function uploadSingleVideoToCloudinary(file, category, index) {
        const generatedTitle = generateAlphanumericTitle();
        createProgressItem(file.name, index);
        
        console.log(`📤 Uploading to Cloudinary: ${file.name} → "${generatedTitle}"`);
        
        try {
            updateProgress(index, 10, 'Generating thumbnail...');
            const thumbnailBlob = await generateThumbnailFromVideo(file);
            
            updateProgress(index, 30, 'Uploading to Cloudinary...');
            
            // Create FormData for multipart upload
            const formData = new FormData();
            formData.append('videoFile', file);
            formData.append('thumbnail', thumbnailBlob, 'thumbnail.jpg');
            formData.append('videoTitle', generatedTitle);
            formData.append('videoDescription', `Auto-uploaded - ${generatedTitle}`);
            formData.append('videoCategory', category);
            
            const response = await fetch('/api/upload-video', {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            
            if (result.success) {
                updateProgress(index, 100, '✅ Complete');
                console.log(`✅ Cloudinary upload complete: ${generatedTitle}`);
                return { success: true, title: generatedTitle };
            } else {
                throw new Error(result.error || 'Upload failed');
            }
            
        } catch (error) {
            console.error(`❌ Upload failed for ${file.name}:`, error);
            updateProgress(index, 100, '❌ Failed: ' + error.message);
            return { success: false, error: error.message };
        }
    }
    
    function createProgressItem(filename, index) {
        if (!uploadProgressList) return;
        
        uploadProgressList.insertAdjacentHTML('beforeend', `
            <div class="upload-progress-item" id="progress-${index}">
                <div class="progress-header">
                    <span class="progress-filename">${filename}</span>
                    <span class="progress-status" id="status-${index}">Starting...</span>
                </div>
                <div class="progress-bar-bg">
                    <div class="progress-bar-fill" id="bar-${index}" style="width: 0%"></div>
                </div>
            </div>
        `);
    }
    
    function updateProgress(index, percent, status) {
        const bar = document.getElementById(`bar-${index}`);
        const statusEl = document.getElementById(`status-${index}`);
        
        if (bar) bar.style.width = `${Math.min(100, Math.max(0, percent))}%`;
        if (statusEl) statusEl.textContent = status;
    }
    
    function showStatus(message, type = 'info') {
        const statusDiv = document.getElementById('uploadStatus');
        if (!statusDiv) return;
        
        statusDiv.textContent = message;
        statusDiv.className = 'status-message ' + type;
        statusDiv.style.display = 'block';
        
        console.log(`[${type.toUpperCase()}] ${message}`);
        
        if (type === 'success' || type === 'error') {
            setTimeout(() => statusDiv.style.display = 'none', 5000);
        }
    }
    
    async function loadVideos() {
        const videoList = document.getElementById('adminVideoList');
        if (!videoList) return;
        
        try {
            const response = await fetch('/api/videos');
            const data = await response.json();
            const videos = data.videos || [];
            
            if (videos.length === 0) {
                videoList.innerHTML = '<p style="color: #777; text-align: center; padding: 40px;">No videos uploaded yet.</p>';
                return;
            }
            
            videoList.innerHTML = videos.map(video => `
                <div class="video-item" data-id="${video.id}">
                    <img src="${video.thumbnail || video.thumbnailUrl}" alt="${video.title}" class="video-thumbnail">
                    <div class="video-info">
                        <h3>${video.title}</h3>
                        <p>${video.description || 'No description'}</p>
                        <span class="video-category">${video.category}</span>
                        ${video.cloudinary_account ? `<small>Storage: ${video.cloudinary_account}</small>` : ''}
                    </div>
                    <div class="video-actions">
                        <button onclick="deleteVideo('${video.id}', '${video.cloudinary_cloud_name || ''}')" class="btn-delete">Delete</button>
                    </div>
                </div>
            `).join('');
        } catch (error) {
            console.error('Error loading videos:', error);
        }
    }
    
    window.deleteVideo = async function(videoId, cloudName = '') {
        if (!confirm('Are you sure you want to delete this video?')) return;
        
        try {
            const response = await fetch('/api/delete-video', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ id: videoId, cloudinary_cloud_name: cloudName })
            });
            
            const result = await response.json();
            if (result.success) {
                showStatus('✅ Video deleted', 'success');
                
    // App Upload Management
    const appUploadForm = document.getElementById('appUploadForm');
    if (appUploadForm) {
        appUploadForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const appFile = document.getElementById('appFile').files[0];
            const appVersion = document.getElementById('appVersion').value;
            const appDescription = document.getElementById('appDescription').value;
            
            if (!appFile) {
                showAppStatus('?? Please select an APK file', 'error');
                return;
            }
            
            const appUploadBtn = document.getElementById('appUploadBtn');
            appUploadBtn.disabled = true;
            appUploadBtn.textContent = 'Uploading...';
            
            try {
                const formData = new FormData();
                formData.append('appFile', appFile);
                formData.append('version', appVersion);
                formData.append('description', appDescription);
                
                const response = await fetch('/api/upload-app', {
                    method: 'POST',
                    body: formData
                });
                
                const result = await response.json();
                
                if (result.success) {
                    showAppStatus('? App uploaded successfully!', 'success');
                    document.getElementById('appFile').value = '';
                    document.getElementById('appVersion').value = '';
                    document.getElementById('appDescription').value = '';
                    loadCurrentApp();
                } else {
                    showAppStatus('? Upload failed: ' + result.error, 'error');
                }
            } catch (error) {
                showAppStatus('? Upload error: ' + error.message, 'error');
            } finally {
                appUploadBtn.disabled = false;
                appUploadBtn.textContent = 'Upload App';
            }
        });
    }
    
    function showAppStatus(message, type) {
        const statusDiv = document.getElementById('appUploadStatus');
        if (!statusDiv) return;
        
        statusDiv.textContent = message;
        statusDiv.className = 'status-message ' + type;
        statusDiv.style.display = 'block';
        
        if (type === 'success' || type === 'error') {
            setTimeout(() => statusDiv.style.display = 'none', 5000);
        }
    }
    
    async function loadCurrentApp() {
        try {
            const response = await fetch('/api/app-info');
            const data = await response.json();
            
            if (data.success && data.app) {
                document.getElementById('currentAppVersion').textContent = data.app.version;
                document.getElementById('currentAppSize').textContent = formatFileSize(data.app.size);
                document.getElementById('currentAppDate').textContent = new Date(data.app.uploadDate).toLocaleString();
                document.getElementById('currentAppDesc').textContent = data.app.description || 'No description';
                document.getElementById('currentAppInfo').style.display = 'block';
            }
        } catch (error) {
            console.error('Error loading app info:', error);
        }
    }
    
    window.deleteApp = async function() {
        if (!confirm('Are you sure you want to delete the app?')) return;
        
        try {
            const response = await fetch('/api/delete-app', {
                method: 'POST'
            });
            
            const result = await response.json();
            
            if (result.success) {
                showAppStatus('? App deleted', 'success');
                document.getElementById('currentAppInfo').style.display = 'none';
            } else {
                showAppStatus('? Delete failed', 'error');
            }
        } catch (error) {
            showAppStatus('? Error: ' + error.message, 'error');
        }
    };
    
    loadCurrentApp();
    
    loadVideos();
            } else {
                showStatus('❌ Delete failed: ' + result.error, 'error');
            }
        } catch (error) {
            console.error('Delete error:', error);
            showStatus('❌ Failed to delete video', 'error');
        }
    };
    
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', (e) => {
            e.preventDefault();
            if (confirm('Are you sure you want to logout?')) {
                localStorage.removeItem('adminLoggedIn');
                window.location.href = 'login.html';
            }
        });
    }
    
    
    // App Upload Management
    const appUploadForm = document.getElementById('appUploadForm');
    if (appUploadForm) {
        appUploadForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const appFile = document.getElementById('appFile').files[0];
            const appVersion = document.getElementById('appVersion').value;
            const appDescription = document.getElementById('appDescription').value;
            
            if (!appFile) {
                showAppStatus('?? Please select an APK file', 'error');
                return;
            }
            
            const appUploadBtn = document.getElementById('appUploadBtn');
            appUploadBtn.disabled = true;
            appUploadBtn.textContent = 'Uploading...';
            
            try {
                const formData = new FormData();
                formData.append('appFile', appFile);
                formData.append('version', appVersion);
                formData.append('description', appDescription);
                
                const response = await fetch('/api/upload-app', {
                    method: 'POST',
                    body: formData
                });
                
                const result = await response.json();
                
                if (result.success) {
                    showAppStatus('? App uploaded successfully!', 'success');
                    document.getElementById('appFile').value = '';
                    document.getElementById('appVersion').value = '';
                    document.getElementById('appDescription').value = '';
                    loadCurrentApp();
                } else {
                    showAppStatus('? Upload failed: ' + result.error, 'error');
                }
            } catch (error) {
                showAppStatus('? Upload error: ' + error.message, 'error');
            } finally {
                appUploadBtn.disabled = false;
                appUploadBtn.textContent = 'Upload App';
            }
        });
    }
    
    function showAppStatus(message, type) {
        const statusDiv = document.getElementById('appUploadStatus');
        if (!statusDiv) return;
        
        statusDiv.textContent = message;
        statusDiv.className = 'status-message ' + type;
        statusDiv.style.display = 'block';
        
        if (type === 'success' || type === 'error') {
            setTimeout(() => statusDiv.style.display = 'none', 5000);
        }
    }
    
    async function loadCurrentApp() {
        try {
            const response = await fetch('/api/app-info');
            const data = await response.json();
            
            if (data.success && data.app) {
                document.getElementById('currentAppVersion').textContent = data.app.version;
                document.getElementById('currentAppSize').textContent = formatFileSize(data.app.size);
                document.getElementById('currentAppDate').textContent = new Date(data.app.uploadDate).toLocaleString();
                document.getElementById('currentAppDesc').textContent = data.app.description || 'No description';
                document.getElementById('currentAppInfo').style.display = 'block';
            }
        } catch (error) {
            console.error('Error loading app info:', error);
        }
    }
    
    window.deleteApp = async function() {
        if (!confirm('Are you sure you want to delete the app?')) return;
        
        try {
            const response = await fetch('/api/delete-app', {
                method: 'POST'
            });
            
            const result = await response.json();
            
            if (result.success) {
                showAppStatus('? App deleted', 'success');
                document.getElementById('currentAppInfo').style.display = 'none';
            } else {
                showAppStatus('? Delete failed', 'error');
            }
        } catch (error) {
            showAppStatus('? Error: ' + error.message, 'error');
        }
    };
    
    loadCurrentApp();
    
    loadVideos();
    console.log('✅ Admin Panel Ready - Cloudinary Integration Active');
});
