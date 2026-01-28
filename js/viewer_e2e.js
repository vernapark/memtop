/**
 * Viewer E2E Decryption Module
 * Handles encrypted video playback with client-side decryption
 */

class VideoViewer {
    constructor() {
        this.encryption = new VideoEncryption();
        this.keyManager = new KeyManager();
        this.currentVideoId = null;
        this.currentBlobURL = null;
    }

    /**
     * Initialize video viewer
     */
    async init() {
        await this.keyManager.initDB();
        this.setupVideoInterceptor();
        console.log('✅ E2E Video Viewer initialized');
    }

    /**
     * Setup video interceptor to handle encrypted videos
     */
    setupVideoInterceptor() {
        // Intercept video play attempts
        document.addEventListener('click', async (e) => {
            const videoCard = e.target.closest('.video-card');
            if (videoCard) {
                const videoId = videoCard.dataset.videoId;
                const encrypted = videoCard.dataset.encrypted === 'true';
                
                if (encrypted) {
                    e.preventDefault();
                    e.stopPropagation();
                    await this.playEncryptedVideo(videoId);
                }
            }
        });
    }

    /**
     * Play encrypted video
     */
    async playEncryptedVideo(videoId) {
        try {
            this.showLoadingModal('🔓 Decrypting video...');

            // Step 1: Retrieve encryption key
            this.updateLoadingModal('🔑 Retrieving encryption key...');
            const { key, iv, metadata } = await this.keyManager.retrieveKey(videoId);

            // Step 2: Fetch encrypted video data
            this.updateLoadingModal('📥 Downloading encrypted video...');
            const encryptedData = await this.fetchEncryptedVideo(videoId);

            // Step 3: Decrypt video
            this.updateLoadingModal('🔓 Decrypting video...');
            const decryptedData = await this.encryption.decryptVideo(
                encryptedData,
                key,
                iv,
                (progress, status) => this.updateLoadingModal(status)
            );

            // Step 4: Create video URL and play
            this.updateLoadingModal('▶️ Starting playback...');
            const videoURL = this.encryption.createVideoURL(decryptedData, metadata.originalType);

            this.closeLoadingModal();
            this.showVideoPlayer(videoURL, metadata);

            this.currentVideoId = videoId;
            this.currentBlobURL = videoURL;

        } catch (error) {
            this.closeLoadingModal();
            this.showError(error.message);
            console.error('Playback error:', error);
        }
    }

    /**
     * Fetch encrypted video from server
     */
    async fetchEncryptedVideo(videoId) {
        const response = await fetch(`/api/video/${videoId}?encrypted=true`);
        
        if (!response.ok) {
            throw new Error('Failed to fetch encrypted video');
        }

        return await response.arrayBuffer();
    }

    /**
     * Show video player with decrypted content
     */
    showVideoPlayer(videoURL, metadata) {
        // Create modal player
        const modal = document.createElement('div');
        modal.className = 'e2e-video-player-modal';
        modal.innerHTML = `
            <div class="e2e-video-player-content">
                <div class="e2e-player-header">
                    <h3>🔒 Secure Playback</h3>
                    <button class="e2e-close-btn" onclick="window.videoViewer.closePlayer()">✕</button>
                </div>
                <video controls autoplay class="e2e-video-element">
                    <source src="${videoURL}" type="${metadata.originalType}">
                    Your browser does not support the video tag.
                </video>
                <div class="e2e-player-info">
                    <p>🔐 This video is decrypted locally in your browser</p>
                    <p>📊 Original size: ${this.formatFileSize(metadata.originalSize)}</p>
                </div>
            </div>
        `;

        // Add styles
        this.addPlayerStyles();

        document.body.appendChild(modal);

        // Cleanup on close
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                this.closePlayer();
            }
        });

        // Cleanup when video ends
        const video = modal.querySelector('video');
        video.addEventListener('ended', () => {
            setTimeout(() => this.closePlayer(), 2000);
        });
    }

    /**
     * Close video player and cleanup
     */
    closePlayer() {
        const modal = document.querySelector('.e2e-video-player-modal');
        if (modal) {
            modal.remove();
        }

        // Revoke blob URL to free memory
        if (this.currentBlobURL) {
            this.encryption.revokeVideoURL(this.currentBlobURL);
            this.currentBlobURL = null;
        }

        this.currentVideoId = null;
    }

    /**
     * Show loading modal
     */
    showLoadingModal(message) {
        let modal = document.querySelector('.e2e-loading-modal');
        
        if (!modal) {
            modal = document.createElement('div');
            modal.className = 'e2e-loading-modal';
            modal.innerHTML = `
                <div class="e2e-loading-content">
                    <div class="e2e-spinner"></div>
                    <p class="e2e-loading-message">${message}</p>
                </div>
            `;
            document.body.appendChild(modal);
        } else {
            this.updateLoadingModal(message);
        }
    }

    /**
     * Update loading modal message
     */
    updateLoadingModal(message) {
        const messageEl = document.querySelector('.e2e-loading-message');
        if (messageEl) {
            messageEl.textContent = message;
        }
    }

    /**
     * Close loading modal
     */
    closeLoadingModal() {
        const modal = document.querySelector('.e2e-loading-modal');
        if (modal) {
            modal.remove();
        }
    }

    /**
     * Show error message
     */
    showError(message) {
        const errorModal = document.createElement('div');
        errorModal.className = 'e2e-error-modal';
        errorModal.innerHTML = `
            <div class="e2e-error-content">
                <h3>❌ Playback Error</h3>
                <p>${message}</p>
                <p style="font-size: 12px; color: #666; margin-top: 10px;">
                    This video may require the encryption key to be present in your browser.
                </p>
                <button onclick="this.closest('.e2e-error-modal').remove()">Close</button>
            </div>
        `;

        document.body.appendChild(errorModal);

        setTimeout(() => errorModal.remove(), 5000);
    }

    /**
     * Add player styles
     */
    addPlayerStyles() {
        if (document.getElementById('e2e-player-styles')) return;

        const style = document.createElement('style');
        style.id = 'e2e-player-styles';
        style.textContent = `
            .e2e-video-player-modal {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.95);
                display: flex;
                align-items: center;
                justify-content: center;
                z-index: 10000;
                animation: fadeIn 0.3s ease;
            }

            .e2e-video-player-content {
                background: #1f2937;
                border-radius: 12px;
                max-width: 90%;
                max-height: 90%;
                width: 1000px;
                overflow: hidden;
            }

            .e2e-player-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 15px 20px;
                background: #111827;
                color: white;
            }

            .e2e-player-header h3 {
                margin: 0;
                font-size: 18px;
            }

            .e2e-close-btn {
                background: none;
                border: none;
                color: white;
                font-size: 24px;
                cursor: pointer;
                padding: 5px 10px;
                transition: transform 0.2s;
            }

            .e2e-close-btn:hover {
                transform: scale(1.2);
            }

            .e2e-video-element {
                width: 100%;
                max-height: 70vh;
                display: block;
            }

            .e2e-player-info {
                padding: 15px 20px;
                background: #111827;
                color: #9ca3af;
                font-size: 13px;
            }

            .e2e-player-info p {
                margin: 5px 0;
            }

            .e2e-loading-modal {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.9);
                display: flex;
                align-items: center;
                justify-content: center;
                z-index: 10001;
            }

            .e2e-loading-content {
                text-align: center;
                color: white;
            }

            .e2e-spinner {
                border: 4px solid rgba(255, 255, 255, 0.3);
                border-top: 4px solid white;
                border-radius: 50%;
                width: 50px;
                height: 50px;
                animation: spin 1s linear infinite;
                margin: 0 auto 20px;
            }

            .e2e-loading-message {
                font-size: 16px;
                margin: 0;
            }

            .e2e-error-modal {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.8);
                display: flex;
                align-items: center;
                justify-content: center;
                z-index: 10002;
            }

            .e2e-error-content {
                background: white;
                padding: 30px;
                border-radius: 12px;
                max-width: 500px;
                text-align: center;
            }

            .e2e-error-content h3 {
                margin-top: 0;
                color: #dc2626;
            }

            .e2e-error-content button {
                background: #3b82f6;
                color: white;
                border: none;
                padding: 10px 30px;
                border-radius: 6px;
                cursor: pointer;
                font-size: 14px;
                margin-top: 15px;
            }

            @keyframes fadeIn {
                from { opacity: 0; }
                to { opacity: 1; }
            }

            @keyframes spin {
                to { transform: rotate(360deg); }
            }
        `;

        document.head.appendChild(style);
    }

    /**
     * Format file size for display
     */
    formatFileSize(bytes) {
        if (bytes < 1024) return bytes + ' B';
        if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB';
        if (bytes < 1024 * 1024 * 1024) return (bytes / (1024 * 1024)).toFixed(2) + ' MB';
        return (bytes / (1024 * 1024 * 1024)).toFixed(2) + ' GB';
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', async () => {
    const viewer = new VideoViewer();
    await viewer.init();
    
    // Make available globally
    window.videoViewer = viewer;
    
    console.log('✅ E2E Video Viewer ready');
});
