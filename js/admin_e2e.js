/**
 * Admin Panel E2E Encryption Integration
 * Handles encrypted video upload with progress tracking
 */

class AdminE2EUploader {
    constructor() {
        this.encryption = new VideoEncryption();
        this.keyManager = new KeyManager();
        this.metadataStripper = new MetadataStripper();
        this.uploadInProgress = false;
    }

    /**
     * Initialize E2E uploader
     */
    async init() {
        await this.keyManager.initDB();
        this.setupEventListeners();
        this.showE2EStatus();
    }

    /**
     * Setup event listeners for upload form
     */
    setupEventListeners() {
        const uploadForm = document.getElementById('uploadForm');
        if (uploadForm) {
            uploadForm.addEventListener('submit', (e) => this.handleEncryptedUpload(e));
        }

        // Add E2E toggle option
        this.addE2EToggle();
    }

    /**
     * Add E2E encryption toggle to admin panel
     */
    addE2EToggle() {
        const uploadSection = document.querySelector('.upload-section');
        if (!uploadSection) return;

        const e2eToggleHTML = `
            <div class="e2e-controls" style="margin: 20px 0; padding: 15px; background: #f0f9ff; border-radius: 8px; border: 2px solid #3b82f6;">
                <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 10px;">
                    <input type="checkbox" id="e2eEnabled" checked style="width: 20px; height: 20px; cursor: pointer;">
                    <label for="e2eEnabled" style="font-weight: bold; cursor: pointer; font-size: 16px;">
                        🔒 Enable End-to-End Encryption
                    </label>
                </div>
                <div style="font-size: 13px; color: #1e40af; margin-left: 30px;">
                    <p style="margin: 5px 0;">✅ Videos encrypted in your browser before upload</p>
                    <p style="margin: 5px 0;">✅ Server cannot see video content</p>
                    <p style="margin: 5px 0;">✅ Metadata automatically stripped</p>
                    <p style="margin: 5px 0;">✅ Only you can decrypt videos</p>
                </div>
                <div id="e2eStatus" style="margin-top: 10px; font-size: 12px; color: #059669;">
                    🟢 E2E Encryption: Ready
                </div>
            </div>
        `;

        uploadSection.insertAdjacentHTML('afterbegin', e2eToggleHTML);
    }

    /**
     * Show E2E encryption status
     */
    showE2EStatus() {
        const statusEl = document.getElementById('e2eStatus');
        if (statusEl) {
            const supported = this.encryption && this.metadataStripper.isSupported();
            if (supported) {
                statusEl.innerHTML = '🟢 E2E Encryption: Active & Ready';
                statusEl.style.color = '#059669';
            } else {
                statusEl.innerHTML = '🔴 E2E Encryption: Not Supported (HTTPS required)';
                statusEl.style.color = '#dc2626';
            }
        }
    }

    /**
     * Handle encrypted video upload
     */
    async handleEncryptedUpload(event) {
        event.preventDefault();

        if (this.uploadInProgress) {
            alert('Upload already in progress!');
            return;
        }

        const e2eEnabled = document.getElementById('e2eEnabled')?.checked ?? true;
        const fileInput = document.querySelector('input[type="file"]');
        const videoFile = fileInput?.files[0];

        if (!videoFile) {
            alert('Please select a video file!');
            return;
        }

        // Check if E2E is enabled
        if (!e2eEnabled) {
            // Fallback to regular upload
            return this.regularUpload(event);
        }

        try {
            this.uploadInProgress = true;
            await this.processAndUploadEncrypted(videoFile);
        } catch (error) {
            console.error('Upload error:', error);
            this.showError(error.message);
        } finally {
            this.uploadInProgress = false;
        }
    }

    /**
     * Process and upload encrypted video
     */
    async processAndUploadEncrypted(videoFile) {
        const progressModal = this.createProgressModal();
        
        try {
            // Step 1: Strip metadata
            this.updateProgress(progressModal, 10, '🧹 Stripping metadata...');
            const { cleanFile, report } = await this.metadataStripper.stripMetadata(
                videoFile,
                (progress, status) => this.updateProgress(progressModal, 10 + progress * 0.2, status)
            );

            console.log('Metadata stripping report:', report);

            // Step 2: Generate encryption key
            this.updateProgress(progressModal, 30, '🔑 Generating encryption key...');
            const encryptionKey = await this.encryption.generateKey();

            // Step 3: Encrypt video
            this.updateProgress(progressModal, 40, '🔒 Encrypting video...');
            const { encryptedData, iv, metadata } = await this.encryption.encryptVideo(
                cleanFile,
                encryptionKey,
                (progress, status) => this.updateProgress(progressModal, 40 + progress * 0.3, status)
            );

            // Step 4: Upload encrypted video
            this.updateProgress(progressModal, 70, '⬆️ Uploading encrypted video...');
            const videoId = await this.uploadToServer(encryptedData, metadata, (progress) => {
                this.updateProgress(progressModal, 70 + progress * 0.2, `Uploading: ${progress}%`);
            });

            // Step 5: Store encryption key locally
            this.updateProgress(progressModal, 90, '💾 Storing encryption key...');
            await this.keyManager.storeKey(videoId, encryptionKey, iv, {
                ...metadata,
                metadataReport: report
            });

            // Step 6: Complete
            this.updateProgress(progressModal, 100, '✅ Upload complete!');

            setTimeout(() => {
                this.closeProgressModal(progressModal);
                this.showSuccess(videoId);
                this.refreshVideoList();
            }, 1500);

        } catch (error) {
            this.closeProgressModal(progressModal);
            throw error;
        }
    }

    /**
     * Upload encrypted video to server
     */
    async uploadToServer(encryptedBlob, metadata, progressCallback) {
        const formData = new FormData();
        
        // Create anonymous filename
        const anonymousFilename = `encrypted_${Date.now()}_${Math.random().toString(36).substring(7)}.enc`;
        
        formData.append('video', encryptedBlob, anonymousFilename);
        formData.append('encrypted', 'true');
        formData.append('metadata', JSON.stringify(metadata));

        const title = document.getElementById('videoTitle')?.value || 'Encrypted Video';
        const description = document.getElementById('videoDescription')?.value || '';
        
        formData.append('title', title);
        formData.append('description', description);

        return new Promise((resolve, reject) => {
            const xhr = new XMLHttpRequest();

            xhr.upload.addEventListener('progress', (e) => {
                if (e.lengthComputable) {
                    const percentComplete = (e.loaded / e.total) * 100;
                    progressCallback(Math.round(percentComplete));
                }
            });

            xhr.addEventListener('load', () => {
                if (xhr.status === 200) {
                    try {
                        const response = JSON.parse(xhr.responseText);
                        resolve(response.video_id || response.id);
                    } catch (e) {
                        reject(new Error('Invalid server response'));
                    }
                } else {
                    reject(new Error(`Upload failed: ${xhr.statusText}`));
                }
            });

            xhr.addEventListener('error', () => reject(new Error('Network error')));
            xhr.addEventListener('abort', () => reject(new Error('Upload cancelled')));

            xhr.open('POST', '/api/upload');
            xhr.send(formData);
        });
    }

    /**
     * Create progress modal
     */
    createProgressModal() {
        const modal = document.createElement('div');
        modal.className = 'e2e-progress-modal';
        modal.innerHTML = `
            <div class="e2e-progress-content">
                <h3>🔒 Secure Upload in Progress</h3>
                <div class="e2e-progress-bar-container">
                    <div class="e2e-progress-bar" style="width: 0%"></div>
                </div>
                <p class="e2e-progress-status">Initializing...</p>
                <p class="e2e-progress-percent">0%</p>
            </div>
        `;

        // Add styles
        const style = document.createElement('style');
        style.textContent = `
            .e2e-progress-modal {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.8);
                display: flex;
                align-items: center;
                justify-content: center;
                z-index: 10000;
            }
            .e2e-progress-content {
                background: white;
                padding: 30px;
                border-radius: 12px;
                max-width: 500px;
                width: 90%;
                text-align: center;
            }
            .e2e-progress-bar-container {
                width: 100%;
                height: 30px;
                background: #e5e7eb;
                border-radius: 15px;
                overflow: hidden;
                margin: 20px 0;
            }
            .e2e-progress-bar {
                height: 100%;
                background: linear-gradient(90deg, #3b82f6, #8b5cf6);
                transition: width 0.3s ease;
            }
            .e2e-progress-status {
                font-size: 14px;
                color: #6b7280;
                margin: 10px 0;
            }
            .e2e-progress-percent {
                font-size: 24px;
                font-weight: bold;
                color: #3b82f6;
            }
        `;

        document.head.appendChild(style);
        document.body.appendChild(modal);

        return modal;
    }

    /**
     * Update progress modal
     */
    updateProgress(modal, percent, status) {
        const progressBar = modal.querySelector('.e2e-progress-bar');
        const statusEl = modal.querySelector('.e2e-progress-status');
        const percentEl = modal.querySelector('.e2e-progress-percent');

        if (progressBar) progressBar.style.width = `${percent}%`;
        if (statusEl) statusEl.textContent = status;
        if (percentEl) percentEl.textContent = `${Math.round(percent)}%`;
    }

    /**
     * Close progress modal
     */
    closeProgressModal(modal) {
        modal.remove();
    }

    /**
     * Show success message
     */
    showSuccess(videoId) {
        alert(`✅ Video uploaded successfully!\n\n🔒 Video ID: ${videoId}\n\n⚠️ Important: Your encryption key is stored locally in your browser. If you clear browser data, you will lose access to this video!`);
    }

    /**
     * Show error message
     */
    showError(message) {
        alert(`❌ Upload failed!\n\n${message}`);
    }

    /**
     * Refresh video list
     */
    refreshVideoList() {
        // Trigger video list refresh (implementation depends on existing code)
        if (window.loadVideos) {
            window.loadVideos();
        } else {
            location.reload();
        }
    }

    /**
     * Regular upload (fallback when E2E disabled)
     */
    async regularUpload(event) {
        console.log('E2E disabled, using regular upload');
        // Let the form submit normally or call existing upload function
        return true;
    }

    /**
     * Export encryption keys (backup)
     */
    async exportKeys() {
        try {
            const keysJSON = await this.keyManager.exportAllKeys();
            const blob = new Blob([keysJSON], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            
            const a = document.createElement('a');
            a.href = url;
            a.download = `memtop_keys_backup_${Date.now()}.json`;
            a.click();
            
            URL.revokeObjectURL(url);
            alert('✅ Encryption keys exported successfully!\n\n⚠️ Keep this file safe! You need it to decrypt your videos.');
        } catch (error) {
            alert(`❌ Export failed: ${error.message}`);
        }
    }

    /**
     * Import encryption keys (restore)
     */
    async importKeys(file) {
        try {
            const text = await file.text();
            const count = await this.keyManager.importKeys(text);
            alert(`✅ Successfully imported ${count} encryption keys!`);
            this.refreshVideoList();
        } catch (error) {
            alert(`❌ Import failed: ${error.message}`);
        }
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', async () => {
    if (window.location.pathname.includes('admin') || window.location.pathname.includes('dashboard')) {
        const uploader = new AdminE2EUploader();
        await uploader.init();
        
        // Make available globally for backup/restore functions
        window.adminE2EUploader = uploader;
        
        console.log('✅ E2E Encryption enabled for admin panel');
    }
});
