// Storage Manager using IndexedDB for unlimited video storage
// This replaces localStorage to handle large video files

const DB_NAME = 'VideoStreamDB';
const DB_VERSION = 1;
const STORE_NAME = 'videos';

class VideoStorage {
    constructor() {
        this.db = null;
    }

    // Initialize IndexedDB
    async init() {
        return new Promise((resolve, reject) => {
            const request = indexedDB.open(DB_NAME, DB_VERSION);

            request.onerror = () => {
                console.error('Database failed to open');
                reject(request.error);
            };

            request.onsuccess = () => {
                this.db = request.result;
                console.log('Database opened successfully');
                resolve();
            };

            request.onupgradeneeded = (e) => {
                const db = e.target.result;
                
                if (!db.objectStoreNames.contains(STORE_NAME)) {
                    const objectStore = db.createObjectStore(STORE_NAME, { keyPath: 'id' });
                    objectStore.createIndex('category', 'category', { unique: false });
                    objectStore.createIndex('uploadDate', 'uploadDate', { unique: false });
                    console.log('Object store created');
                }
            };
        });
    }

    // Add a video
    async addVideo(video) {
        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction([STORE_NAME], 'readwrite');
            const objectStore = transaction.objectStore(STORE_NAME);
            const request = objectStore.add(video);

            request.onsuccess = () => {
                console.log('Video added successfully:', video.id);
                resolve(video.id);
            };

            request.onerror = () => {
                console.error('Error adding video:', request.error);
                reject(request.error);
            };
        });
    }

    // Get all videos
    async getAllVideos() {
        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction([STORE_NAME], 'readonly');
            const objectStore = transaction.objectStore(STORE_NAME);
            const request = objectStore.getAll();

            request.onsuccess = () => {
                resolve(request.result || []);
            };

            request.onerror = () => {
                console.error('Error getting videos:', request.error);
                reject(request.error);
            };
        });
    }

    // Get video by ID
    async getVideo(id) {
        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction([STORE_NAME], 'readonly');
            const objectStore = transaction.objectStore(STORE_NAME);
            const request = objectStore.get(id);

            request.onsuccess = () => {
                resolve(request.result);
            };

            request.onerror = () => {
                reject(request.error);
            };
        });
    }

    // Delete a video
    async deleteVideo(id) {
        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction([STORE_NAME], 'readwrite');
            const objectStore = transaction.objectStore(STORE_NAME);
            const request = objectStore.delete(id);

            request.onsuccess = () => {
                console.log('Video deleted:', id);
                resolve();
            };

            request.onerror = () => {
                console.error('Error deleting video:', request.error);
                reject(request.error);
            };
        });
    }

    // Get storage estimate
    async getStorageEstimate() {
        if (navigator.storage && navigator.storage.estimate) {
            const estimate = await navigator.storage.estimate();
            const usage = (estimate.usage / 1024 / 1024).toFixed(2);
            const quota = (estimate.quota / 1024 / 1024).toFixed(2);
            console.log(`Storage: ${usage}MB used of ${quota}MB available`);
            return { usage, quota, usagePercent: (estimate.usage / estimate.quota * 100).toFixed(2) };
        }
        return null;
    }
}

// Export for use in other scripts
const videoStorage = new VideoStorage();
