// Admin JavaScript - Multiple Upload with Auto-Generated Titles
console.log('🚀 Admin Multi-Upload Module Loaded');

// Selected files array
let selectedFiles = [];

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
    
    // Generate 7-8 words
    const wordCount = Math.random() < 0.5 ? 7 : 8;
    const titleParts = [];
    
    for (let i = 0; i < wordCount; i++) {
        // Mix words and numbers (60% words, 40% numbers)
        if (Math.random() < 0.6) {
            const randomWord = words[Math.floor(Math.random() * words.length)];
            titleParts.push(randomWord);
        } else {
            const randomNumber = numbers[Math.floor(Math.random() * numbers.length)];
            titleParts.push(randomNumber);
        }
    }
    
    return titleParts.join(' ');
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    console.log('🎬 Admin Panel Initialized - Multi-Upload Mode');
    
    const videoDropZone = document.getElementById('videoDropZone');
    const videoFileInput = document.getElementById('videoFile');
    const uploadForm = document.getElementById('uploadForm');
    const selectedFilesContainer = document.getElementById('selectedFilesContainer');
    const selectedFilesList = document.getElementById('selectedFilesList');
    const fileCount = document.getElementById('fileCount');
    const uploadBtn = document.getElementById('uploadBtn');
    const uploadProgressContainer = document.getElementById('uploadProgressContainer');
    const uploadProgressList = document.getElementById('uploadProgressList');
    
    // Make drop zone clickable
    videoDropZone.addEventListener('click', () => {
        videoFileInput.click();
    });
    
    // Drag and drop handlers
    videoDropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        videoDropZone.classList.add('drag-over');
    });
    
    videoDropZone.addEventListener('dragleave', () => {
        videoDropZone.classList.remove('drag-over');
    });
    
    videoDropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        videoDropZone.classList.remove('drag-over');
        
        const files = Array.from(e.dataTransfer.files).filter(file => file.type.startsWith('video/'));
        if (files.length > 0) {
            addFiles(files);
        }
    });
    
    // File input change handler
    videoFileInput.addEventListener('change', (e) => {
        const files = Array.from(e.target.files);
        if (files.length > 0) {
            addFiles(files);
        }
    });
    
    // Add files to selection
    function addFiles(files) {
        selectedFiles = [...selectedFiles, ...files];
        updateSelectedFilesList();
        console.log(`📁 ${files.length} file(s) added. Total: ${selectedFiles.length}`);
    }
    
    // Update selected files display
    function updateSelectedFilesList() {
        if (selectedFiles.length === 0) {
            selectedFilesContainer.style.display = 'none';
            return;
        }
        
        selectedFilesContainer.style.display = 'block';
        fileCount.textContent = selectedFiles.length;
        
        selectedFilesList.innerHTML = selectedFiles.map((file, index) => `
            <div class="file-item">
                <span class="file-item-name">📹 ${file.name} (${formatFileSize(file.size)})</span>
                <button type="button" class="file-item-remove" onclick="removeFile(${index})">Remove</button>
            </div>
        `).join('');
    }
    
    // Remove file from selection
    window.removeFile = function(index) {
        selectedFiles.splice(index, 1);
        updateSelectedFilesList();
        console.log(`🗑️ File removed. Remaining: ${selectedFiles.length}`);
    };
    
    // Format file size
    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
    }
    
    // Upload form submission
    uploadForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        if (selectedFiles.length === 0) {
            showStatus('⚠️ Please select at least one video file', 'error');
            return;
        }
        
        const category = document.getElementById('videoCategory').value;
        
        if (!category) {
            showStatus('⚠️ Please select a category', 'error');
            return;
        }
        
        // Disable upload button during upload
        uploadBtn.disabled = true;
        uploadBtn.textContent = `Uploading ${selectedFiles.length} video(s)...`;
        
        // Show progress container
        uploadProgressContainer.style.display = 'block';
        uploadProgressList.innerHTML = '';
        
        console.log(`🚀 Starting parallel upload of ${selectedFiles.length} videos`);
        
        // Upload all files in parallel for maximum speed
        const uploadPromises = selectedFiles.map((file, index) => 
            uploadSingleVideo(file, category, index)
        );
        
        try {
            const results = await Promise.all(uploadPromises);
            const successCount = results.filter(r => r.success).length;
            const failCount = results.length - successCount;
            
            if (failCount === 0) {
                showStatus(`✅ All ${successCount} videos uploaded successfully!`, 'success');
            } else {
                showStatus(`⚠️ ${successCount} succeeded, ${failCount} failed`, 'warning');
            }
            
            // Clear selection
            selectedFiles = [];
            updateSelectedFilesList();
            videoFileInput.value = '';
            
            // Reload video list
            setTimeout(() => {
                loadVideos();
            }, 1000);
            
        } catch (error) {
            console.error('Upload error:', error);
            showStatus('❌ Upload failed: ' + error.message, 'error');
        } finally {
            uploadBtn.disabled = false;
            uploadBtn.textContent = 'Upload All Videos';
        }
    });
    
    // Upload single video with optimizations
    async function uploadSingleVideo(file, category, index) {
        const generatedTitle = generateAlphanumericTitle();
        const progressItem = createProgressItem(file.name, index);
        
        console.log(`📤 Uploading: ${file.name} → Title: "${generatedTitle}"`);
        
        try {
            // Create thumbnail from video
            updateProgress(index, 10, 'Generating thumbnail...');
            const thumbnail = await generateThumbnail(file);
            
            // Upload to Cloudinary with optimizations
            updateProgress(index, 30, 'Uploading video...');
            const videoUrl = await uploadToCloudinary(file, 'video', (progress) => {
                updateProgress(index, 30 + (progress * 0.5), `Uploading: ${Math.round(progress)}%`);
            });
            
            updateProgress(index, 80, 'Uploading thumbnail...');
            const thumbnailUrl = await uploadToCloudinary(thumbnail, 'image', (progress) => {
                updateProgress(index, 80 + (progress * 0.15), `Thumbnail: ${Math.round(progress)}%`);
            });
            
            // Save to storage
            updateProgress(index, 95, 'Saving...');
            await saveVideoToStorage({
                title: generatedTitle,
                description: `Auto-uploaded video - ${generatedTitle}`,
                videoUrl: videoUrl,
                thumbnailUrl: thumbnailUrl,
                category: category,
                uploadDate: new Date().toISOString()
            });
            
            updateProgress(index, 100, '✅ Complete');
            console.log(`✅ Upload complete: ${generatedTitle}`);
            
            return { success: true, title: generatedTitle };
            
        } catch (error) {
            console.error(`❌ Upload failed for ${file.name}:`, error);
            updateProgress(index, 100, '❌ Failed: ' + error.message);
            return { success: false, error: error.message };
        }
    }
    
    // Create progress item UI
    function createProgressItem(filename, index) {
        const progressHtml = `
            <div class="upload-progress-item" id="progress-${index}">
                <div class="progress-header">
                    <span class="progress-filename">${filename}</span>
                    <span class="progress-status" id="status-${index}">Starting...</span>
                </div>
                <div class="progress-bar-bg">
                    <div class="progress-bar-fill" id="bar-${index}" style="width: 0%"></div>
                </div>
            </div>
        `;
        uploadProgressList.insertAdjacentHTML('beforeend', progressHtml);
    }
    
    // Update progress
    function updateProgress(index, percent, status) {
        const bar = document.getElementById(`bar-${index}`);
        const statusEl = document.getElementById(`status-${index}`);
        
        if (bar) bar.style.width = `${percent}%`;
        if (statusEl) statusEl.textContent = status;
    }
    
    // Generate thumbnail from video
    function generateThumbnail(videoFile) {
        return new Promise((resolve, reject) => {
            const video = document.createElement('video');
            const canvas = document.createElement('canvas');
            const ctx = canvas.getContext('2d');
            
            video.preload = 'metadata';
            video.muted = true;
            
            video.addEventListener('loadedmetadata', () => {
                video.currentTime = Math.min(2, video.duration / 4); // Seek to 2s or 25% of video
            });
            
            video.addEventListener('seeked', () => {
                canvas.width = video.videoWidth;
                canvas.height = video.videoHeight;
                ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
                
                canvas.toBlob((blob) => {
                    if (blob) {
                        const thumbnailFile = new File([blob], 'thumbnail.jpg', { type: 'image/jpeg' });
                        resolve(thumbnailFile);
                    } else {
                        reject(new Error('Failed to generate thumbnail'));
                    }
                }, 'image/jpeg', 0.85);
            });
            
            video.addEventListener('error', (e) => {
                reject(new Error('Failed to load video for thumbnail'));
            });
            
            video.src = URL.createObjectURL(videoFile);
        });
    }
    
    // Upload to Cloudinary with optimizations
    async function uploadToCloudinary(file, resourceType, progressCallback) {
        return new Promise((resolve, reject) => {
            // Simulate Cloudinary upload (replace with actual implementation)
            // In production, this should use Cloudinary's upload API
            
            const formData = new FormData();
            formData.append('file', file);
            formData.append('upload_preset', 'your_upload_preset'); // Replace with actual preset
            formData.append('resource_type', resourceType);
            
            // Optimization parameters for maximum speed and quality
            if (resourceType === 'video') {
                formData.append('quality', 'auto:best');
                formData.append('fetch_format', 'auto');
                formData.append('chunk_size', '20000000'); // 20MB chunks for faster upload
            }
            
            const xhr = new XMLHttpRequest();
            
            // Track upload progress
            xhr.upload.addEventListener('progress', (e) => {
                if (e.lengthComputable && progressCallback) {
                    const progress = (e.loaded / e.total) * 100;
                    progressCallback(progress);
                }
            });
            
            xhr.addEventListener('load', () => {
                if (xhr.status === 200) {
                    const response = JSON.parse(xhr.responseText);
                    resolve(response.secure_url || response.url);
                } else {
                    reject(new Error(`Upload failed: ${xhr.statusText}`));
                }
            });
            
            xhr.addEventListener('error', () => {
                reject(new Error('Network error during upload'));
            });
            
            xhr.addEventListener('timeout', () => {
                reject(new Error('Upload timeout'));
            });
            
            // For now, simulate upload since we don't have Cloudinary credentials in browser
            // In production, replace with actual Cloudinary endpoint
            simulateCloudinaryUpload(file, resourceType, progressCallback)
                .then(resolve)
                .catch(reject);
        });
    }
    
    // Simulate Cloudinary upload (temporary for testing)
    function simulateCloudinaryUpload(file, resourceType, progressCallback) {
        return new Promise((resolve, reject) => {
            // Simulate upload with progress
            let progress = 0;
            const interval = setInterval(() => {
                progress += Math.random() * 20;
                if (progress > 100) progress = 100;
                
                if (progressCallback) {
                    progressCallback(progress);
                }
                
                if (progress >= 100) {
                    clearInterval(interval);
                    
                    // Create object URL for local storage
                    const url = URL.createObjectURL(file);
                    resolve(url);
                }
            }, 200);
        });
    }
    
    // Save video to storage
    async function saveVideoToStorage(videoData) {
        try {
            // Get existing videos
            const videos = await getAllVideos();
            
            // Add new video
            videoData.id = Date.now().toString();
            videos.push(videoData);
            
            // Save to localStorage
            localStorage.setItem('videos', JSON.stringify(videos));
            
            console.log('💾 Video saved to storage:', videoData.title);
        } catch (error) {
            console.error('Storage error:', error);
            throw error;
        }
    }
    
    // Get all videos from storage
    async function getAllVideos() {
        try {
            const videosJson = localStorage.getItem('videos');
            return videosJson ? JSON.parse(videosJson) : [];
        } catch (error) {
            console.error('Error loading videos:', error);
            return [];
        }
    }
    
    // Show status message
    function showStatus(message, type = 'info') {
        const statusDiv = document.getElementById('uploadStatus');
        statusDiv.textContent = message;
        statusDiv.className = 'status-message ' + type;
        statusDiv.style.display = 'block';
        
        if (type === 'success' || type === 'error') {
            setTimeout(() => {
                statusDiv.style.display = 'none';
            }, 5000);
        }
    }
    
    // Load and display videos
    async function loadVideos() {
        const videoList = document.getElementById('adminVideoList');
        const videos = await getAllVideos();
        
        if (videos.length === 0) {
            videoList.innerHTML = '<p style="color: #777; text-align: center; padding: 40px;">No videos uploaded yet.</p>';
            return;
        }
        
        videoList.innerHTML = videos.map(video => `
            <div class="video-item" data-id="${video.id}">
                <img src="${video.thumbnailUrl}" alt="${video.title}" class="video-thumbnail">
                <div class="video-info">
                    <h3>${video.title}</h3>
                    <p>${video.description || 'No description'}</p>
                    <span class="video-category">${video.category}</span>
                </div>
                <div class="video-actions">
                    <button onclick="deleteVideo('${video.id}')" class="btn-delete">Delete</button>
                </div>
            </div>
        `).join('');
    }
    
    // Delete video
    window.deleteVideo = async function(videoId) {
        if (!confirm('Are you sure you want to delete this video?')) {
            return;
        }
        
        try {
            const videos = await getAllVideos();
            const filteredVideos = videos.filter(v => v.id !== videoId);
            localStorage.setItem('videos', JSON.stringify(filteredVideos));
            
            showStatus('✅ Video deleted successfully', 'success');
            loadVideos();
        } catch (error) {
            console.error('Delete error:', error);
            showStatus('❌ Failed to delete video', 'error');
        }
    };
    
    // Logout handler
    document.getElementById('logoutBtn')?.addEventListener('click', (e) => {
        e.preventDefault();
        if (confirm('Are you sure you want to logout?')) {
            localStorage.removeItem('adminLoggedIn');
            window.location.href = 'login.html';
        }
    });
    
    // Initial load
    loadVideos();
});
