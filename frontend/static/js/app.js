/**
 * Main Application Entry Point
 * Initializes the File Gallery Viewer application
 */

// Application state
let apiClient;
let uiController;

/**
 * Initialize the application
 */
function initializeApp() {
    // Create API client instance
    apiClient = new APIClient();
    
    // Create UI controller instance
    uiController = new UIController(apiClient);
    
    // Check backend health and load initial data
    checkBackendAndLoadFiles();
    
    console.log('File Gallery Viewer initialized successfully');
}

/**
 * Check backend health and load files
 */
async function checkBackendAndLoadFiles() {
    try {
        const isHealthy = await apiClient.checkHealth();
        
        if (isHealthy) {
            // Backend is available, load files
            await uiController.loadFiles();
        } else {
            // Backend is not available
            uiController.showError('无法连接到后端服务，请确保后端服务正在运行');
        }
    } catch (error) {
        console.error('Error during initialization:', error);
        uiController.showError('应用初始化失败，请刷新页面重试');
    }
}

/**
 * Handle application errors
 * @param {Error} error - Error object
 */
function handleAppError(error) {
    console.error('Application error:', error);
    if (uiController) {
        uiController.showError('应用发生错误，请刷新页面重试');
    }
}

// Global error handler
window.addEventListener('error', (event) => {
    handleAppError(event.error);
});

// Unhandled promise rejection handler
window.addEventListener('unhandledrejection', (event) => {
    handleAppError(event.reason);
});

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', initializeApp);