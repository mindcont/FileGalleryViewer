/**
 * API Client for File Gallery Viewer
 * Handles communication with the backend API
 */
class APIClient {
    constructor(baseUrl = 'http://localhost:9000') {
        this.baseUrl = baseUrl;
    }

    /**
     * Get list of files from the backend
     * @returns {Promise<Object>} File list response
     */
    async getFiles() {
        try {
            const response = await fetch(`${this.baseUrl}/api/files`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error('Error fetching files:', error);
            throw error;
        }
    }

    /**
     * Get image URL for a given filename
     * @param {string} filename - PNG filename
     * @returns {string} Image URL
     */
    getImageUrl(filename) {
        return `${this.baseUrl}/api/image/${encodeURIComponent(filename)}`;
    }

    /**
     * Get thumbnail URL for a given filename
     * @param {string} filename - PNG filename
     * @returns {string} Thumbnail URL
     */
    getThumbnailUrl(filename) {
        return `${this.baseUrl}/api/thumbnail/${encodeURIComponent(filename)}`;
    }

    /**
     * Get download URL for a CSV file
     * @param {string} filename - CSV filename
     * @returns {string} Download URL
     */
    getDownloadUrl(filename) {
        return `${this.baseUrl}/api/download/${encodeURIComponent(filename)}`;
    }

    /**
     * Get cache statistics
     * @returns {Promise<Object>} Cache statistics
     */
    async getCacheStats() {
        try {
            const response = await fetch(`${this.baseUrl}/api/cache/stats`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error('Error fetching cache stats:', error);
            throw error;
        }
    }

    /**
     * Invalidate backend cache
     * @returns {Promise<Object>} Response message
     */
    async invalidateCache() {
        try {
            const response = await fetch(`${this.baseUrl}/api/cache/invalidate`, {
                method: 'POST'
            });
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error('Error invalidating cache:', error);
            throw error;
        }
    }

    /**
     * Check if the backend is available
     * @returns {Promise<boolean>} Backend availability status
     */
    async checkHealth() {
        try {
            const response = await fetch(`${this.baseUrl}/`);
            return response.ok;
        } catch (error) {
            console.error('Backend health check failed:', error);
            return false;
        }
    }
}