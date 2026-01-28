/**
 * E2E Video Encryption Module
 * Uses AES-256-GCM encryption via Web Crypto API
 * Zero-knowledge architecture - server never sees decryption keys
 */

class VideoEncryption {
    constructor() {
        this.algorithm = 'AES-GCM';
        this.keyLength = 256;
        this.ivLength = 12; // 96 bits for GCM
        this.tagLength = 128; // 128 bits for authentication
    }

    /**
     * Generate a secure encryption key
     * @returns {Promise<CryptoKey>}
     */
    async generateKey() {
        return await crypto.subtle.generateKey(
            {
                name: this.algorithm,
                length: this.keyLength
            },
            true, // extractable
            ['encrypt', 'decrypt']
        );
    }

    /**
     * Generate a random IV (Initialization Vector)
     * @returns {Uint8Array}
     */
    generateIV() {
        return crypto.getRandomValues(new Uint8Array(this.ivLength));
    }

    /**
     * Encrypt video file
     * @param {File} videoFile - Original video file
     * @param {CryptoKey} key - Encryption key
     * @param {Function} progressCallback - Progress callback (0-100)
     * @returns {Promise<{encryptedData: Blob, iv: Uint8Array, metadata: Object}>}
     */
    async encryptVideo(videoFile, key, progressCallback = null) {
        try {
            // Generate IV
            const iv = this.generateIV();
            
            // Read file as ArrayBuffer
            progressCallback && progressCallback(10, 'Reading video file...');
            const fileBuffer = await this.readFileAsArrayBuffer(videoFile);
            
            // Encrypt the data
            progressCallback && progressCallback(30, 'Encrypting video...');
            const encryptedBuffer = await crypto.subtle.encrypt(
                {
                    name: this.algorithm,
                    iv: iv,
                    tagLength: this.tagLength
                },
                key,
                fileBuffer
            );

            progressCallback && progressCallback(80, 'Finalizing encryption...');

            // Create metadata
            const metadata = {
                originalName: videoFile.name,
                originalSize: videoFile.size,
                originalType: videoFile.type,
                encryptedSize: encryptedBuffer.byteLength,
                timestamp: Date.now(),
                algorithm: this.algorithm,
                keyLength: this.keyLength
            };

            // Convert to Blob for upload
            const encryptedBlob = new Blob([encryptedBuffer], { type: 'application/octet-stream' });

            progressCallback && progressCallback(100, 'Encryption complete!');

            return {
                encryptedData: encryptedBlob,
                iv: iv,
                metadata: metadata
            };

        } catch (error) {
            console.error('Encryption error:', error);
            throw new Error(`Encryption failed: ${error.message}`);
        }
    }

    /**
     * Decrypt video data
     * @param {ArrayBuffer} encryptedData - Encrypted video data
     * @param {CryptoKey} key - Decryption key
     * @param {Uint8Array} iv - Initialization vector
     * @param {Function} progressCallback - Progress callback
     * @returns {Promise<ArrayBuffer>}
     */
    async decryptVideo(encryptedData, key, iv, progressCallback = null) {
        try {
            progressCallback && progressCallback(20, 'Decrypting video...');

            const decryptedBuffer = await crypto.subtle.decrypt(
                {
                    name: this.algorithm,
                    iv: iv,
                    tagLength: this.tagLength
                },
                key,
                encryptedData
            );

            progressCallback && progressCallback(100, 'Decryption complete!');

            return decryptedBuffer;

        } catch (error) {
            console.error('Decryption error:', error);
            throw new Error(`Decryption failed: ${error.message}`);
        }
    }

    /**
     * Export encryption key to raw format
     * @param {CryptoKey} key
     * @returns {Promise<ArrayBuffer>}
     */
    async exportKey(key) {
        return await crypto.subtle.exportKey('raw', key);
    }

    /**
     * Import encryption key from raw format
     * @param {ArrayBuffer} keyData
     * @returns {Promise<CryptoKey>}
     */
    async importKey(keyData) {
        return await crypto.subtle.importKey(
            'raw',
            keyData,
            {
                name: this.algorithm,
                length: this.keyLength
            },
            true,
            ['encrypt', 'decrypt']
        );
    }

    /**
     * Convert ArrayBuffer to Base64
     * @param {ArrayBuffer} buffer
     * @returns {string}
     */
    arrayBufferToBase64(buffer) {
        const bytes = new Uint8Array(buffer);
        let binary = '';
        for (let i = 0; i < bytes.byteLength; i++) {
            binary += String.fromCharCode(bytes[i]);
        }
        return btoa(binary);
    }

    /**
     * Convert Base64 to ArrayBuffer
     * @param {string} base64
     * @returns {ArrayBuffer}
     */
    base64ToArrayBuffer(base64) {
        const binary = atob(base64);
        const bytes = new Uint8Array(binary.length);
        for (let i = 0; i < binary.length; i++) {
            bytes[i] = binary.charCodeAt(i);
        }
        return bytes.buffer;
    }

    /**
     * Read file as ArrayBuffer
     * @param {File} file
     * @returns {Promise<ArrayBuffer>}
     */
    readFileAsArrayBuffer(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = () => resolve(reader.result);
            reader.onerror = reject;
            reader.readAsArrayBuffer(file);
        });
    }

    /**
     * Create encrypted video blob URL for streaming
     * @param {ArrayBuffer} decryptedData
     * @param {string} mimeType
     * @returns {string}
     */
    createVideoURL(decryptedData, mimeType = 'video/mp4') {
        const blob = new Blob([decryptedData], { type: mimeType });
        return URL.createObjectURL(blob);
    }

    /**
     * Revoke video URL to free memory
     * @param {string} url
     */
    revokeVideoURL(url) {
        URL.revokeObjectURL(url);
    }
}

/**
 * Secure Key Management System
 * Stores encryption keys securely in IndexedDB
 */
class KeyManager {
    constructor() {
        this.dbName = 'memtop_e2e_keys';
        this.storeName = 'encryption_keys';
        this.db = null;
    }

    /**
     * Initialize IndexedDB
     * @returns {Promise<IDBDatabase>}
     */
    async initDB() {
        if (this.db) return this.db;

        return new Promise((resolve, reject) => {
            const request = indexedDB.open(this.dbName, 1);

            request.onerror = () => reject(request.error);
            request.onsuccess = () => {
                this.db = request.result;
                resolve(this.db);
            };

            request.onupgradeneeded = (event) => {
                const db = event.target.result;
                if (!db.objectStoreNames.contains(this.storeName)) {
                    const objectStore = db.createObjectStore(this.storeName, { keyPath: 'videoId' });
                    objectStore.createIndex('timestamp', 'timestamp', { unique: false });
                }
            };
        });
    }

    /**
     * Store encryption key for a video
     * @param {string} videoId - Unique video identifier
     * @param {CryptoKey} key - Encryption key
     * @param {Uint8Array} iv - Initialization vector
     * @param {Object} metadata - Video metadata
     * @returns {Promise<void>}
     */
    async storeKey(videoId, key, iv, metadata = {}) {
        const db = await this.initDB();
        const encryption = new VideoEncryption();

        // Export key to raw format
        const keyData = await encryption.exportKey(key);

        const keyRecord = {
            videoId: videoId,
            keyData: encryption.arrayBufferToBase64(keyData),
            iv: encryption.arrayBufferToBase64(iv.buffer),
            metadata: metadata,
            timestamp: Date.now()
        };

        return new Promise((resolve, reject) => {
            const transaction = db.transaction([this.storeName], 'readwrite');
            const store = transaction.objectStore(this.storeName);
            const request = store.put(keyRecord);

            request.onsuccess = () => resolve();
            request.onerror = () => reject(request.error);
        });
    }

    /**
     * Retrieve encryption key for a video
     * @param {string} videoId
     * @returns {Promise<{key: CryptoKey, iv: Uint8Array, metadata: Object}>}
     */
    async retrieveKey(videoId) {
        const db = await this.initDB();
        const encryption = new VideoEncryption();

        return new Promise((resolve, reject) => {
            const transaction = db.transaction([this.storeName], 'readonly');
            const store = transaction.objectStore(this.storeName);
            const request = store.get(videoId);

            request.onsuccess = async () => {
                const result = request.result;
                if (!result) {
                    reject(new Error('Encryption key not found'));
                    return;
                }

                try {
                    // Import key from raw format
                    const keyData = encryption.base64ToArrayBuffer(result.keyData);
                    const key = await encryption.importKey(keyData);
                    const iv = new Uint8Array(encryption.base64ToArrayBuffer(result.iv));

                    resolve({
                        key: key,
                        iv: iv,
                        metadata: result.metadata
                    });
                } catch (error) {
                    reject(error);
                }
            };

            request.onerror = () => reject(request.error);
        });
    }

    /**
     * Delete encryption key for a video
     * @param {string} videoId
     * @returns {Promise<void>}
     */
    async deleteKey(videoId) {
        const db = await this.initDB();

        return new Promise((resolve, reject) => {
            const transaction = db.transaction([this.storeName], 'readwrite');
            const store = transaction.objectStore(this.storeName);
            const request = store.delete(videoId);

            request.onsuccess = () => resolve();
            request.onerror = () => reject(request.error);
        });
    }

    /**
     * Get all stored video IDs
     * @returns {Promise<string[]>}
     */
    async getAllVideoIds() {
        const db = await this.initDB();

        return new Promise((resolve, reject) => {
            const transaction = db.transaction([this.storeName], 'readonly');
            const store = transaction.objectStore(this.storeName);
            const request = store.getAllKeys();

            request.onsuccess = () => resolve(request.result);
            request.onerror = () => reject(request.error);
        });
    }

    /**
     * Export all keys as JSON (for backup)
     * @returns {Promise<string>}
     */
    async exportAllKeys() {
        const db = await this.initDB();

        return new Promise((resolve, reject) => {
            const transaction = db.transaction([this.storeName], 'readonly');
            const store = transaction.objectStore(this.storeName);
            const request = store.getAll();

            request.onsuccess = () => {
                const keys = request.result;
                const exportData = {
                    version: 1,
                    exportDate: new Date().toISOString(),
                    keys: keys
                };
                resolve(JSON.stringify(exportData, null, 2));
            };

            request.onerror = () => reject(request.error);
        });
    }

    /**
     * Import keys from JSON backup
     * @param {string} jsonData
     * @returns {Promise<number>} Number of keys imported
     */
    async importKeys(jsonData) {
        const db = await this.initDB();
        const data = JSON.parse(jsonData);

        if (!data.keys || !Array.isArray(data.keys)) {
            throw new Error('Invalid backup format');
        }

        return new Promise((resolve, reject) => {
            const transaction = db.transaction([this.storeName], 'readwrite');
            const store = transaction.objectStore(this.storeName);

            let imported = 0;
            data.keys.forEach(keyRecord => {
                store.put(keyRecord);
                imported++;
            });

            transaction.oncomplete = () => resolve(imported);
            transaction.onerror = () => reject(transaction.error);
        });
    }

    /**
     * Clear all stored keys (use with caution!)
     * @returns {Promise<void>}
     */
    async clearAllKeys() {
        const db = await this.initDB();

        return new Promise((resolve, reject) => {
            const transaction = db.transaction([this.storeName], 'readwrite');
            const store = transaction.objectStore(this.storeName);
            const request = store.clear();

            request.onsuccess = () => resolve();
            request.onerror = () => reject(request.error);
        });
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { VideoEncryption, KeyManager };
}
