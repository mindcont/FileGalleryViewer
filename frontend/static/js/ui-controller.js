/**
 * UI Controller for File Gallery Viewer
 * Manages user interface state and interactions
 */
class UIController {
    constructor(apiClient) {
        this.apiClient = apiClient;
        this.fileGallery = document.getElementById('fileGallery');
        this.loadingIndicator = document.getElementById('loadingIndicator');
        this.errorAlert = document.getElementById('errorAlert');
        this.errorMessage = document.getElementById('errorMessage');
        this.emptyState = document.getElementById('emptyState');
        this.refreshBtn = document.getElementById('refreshBtn');
        
        // Image preview state
        this.currentImageIndex = -1;
        this.imageElements = [];
        
        // Lazy loading observer
        this.lazyLoadObserver = null;
        
        this.initializeEventListeners();
        this.initializeLazyLoading();
        this.initializeImagePreview();
    }

    /**
     * Initialize event listeners
     */
    initializeEventListeners() {
        this.refreshBtn.addEventListener('click', () => {
            this.loadFiles();
        });
    }

    /**
     * Initialize lazy loading for images
     */
    initializeLazyLoading() {
        if ('IntersectionObserver' in window) {
            this.lazyLoadObserver = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        const src = img.getAttribute('data-src');
                        if (src) {
                            img.src = src;
                            img.removeAttribute('data-src');
                            this.lazyLoadObserver.unobserve(img);
                        }
                    }
                });
            }, {
                rootMargin: '50px'
            });
        }
    }

    /**
     * Initialize image preview modal
     */
    initializeImagePreview() {
        // Create modal HTML
        const modalHTML = `
            <div class="modal fade" id="imagePreviewModal" tabindex="-1" aria-hidden="true">
                <div class="modal-dialog modal-xl modal-dialog-centered">
                    <div class="modal-content bg-dark">
                        <div class="modal-header border-0">
                            <h5 class="modal-title text-white" id="imagePreviewTitle"></h5>
                            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="关闭"></button>
                        </div>
                        <div class="modal-body text-center p-0">
                            <img id="previewImage" class="img-fluid" alt="预览图片" style="max-height: 80vh;">
                        </div>
                        <div class="modal-footer border-0 justify-content-between">
                            <button type="button" class="btn btn-outline-light" id="prevImageBtn">
                                <i class="bi bi-chevron-left"></i> 上一张
                            </button>
                            <span class="text-white" id="imageCounter"></span>
                            <button type="button" class="btn btn-outline-light" id="nextImageBtn">
                                下一张 <i class="bi bi-chevron-right"></i>
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Append modal to body
        document.body.insertAdjacentHTML('beforeend', modalHTML);
        
        // Get modal elements
        this.previewModal = new bootstrap.Modal(document.getElementById('imagePreviewModal'));
        this.previewImage = document.getElementById('previewImage');
        this.previewTitle = document.getElementById('imagePreviewTitle');
        this.imageCounter = document.getElementById('imageCounter');
        this.prevImageBtn = document.getElementById('prevImageBtn');
        this.nextImageBtn = document.getElementById('nextImageBtn');
        
        // Add navigation event listeners
        this.prevImageBtn.addEventListener('click', () => this.showPreviousImage());
        this.nextImageBtn.addEventListener('click', () => this.showNextImage());
        
        // Add keyboard navigation
        document.addEventListener('keydown', (e) => {
            const modalElement = document.getElementById('imagePreviewModal');
            if (modalElement.classList.contains('show')) {
                if (e.key === 'ArrowLeft') {
                    this.showPreviousImage();
                } else if (e.key === 'ArrowRight') {
                    this.showNextImage();
                } else if (e.key === 'Escape') {
                    this.previewModal.hide();
                }
            }
        });
    }

    /**
     * Load files from API and render them
     */
    async loadFiles() {
        try {
            this.showLoading();
            this.hideError();
            this.hideEmptyState();

            const response = await this.apiClient.getFiles();
            
            if (response.files && response.files.length > 0) {
                this.renderImageCards(response.files);
            } else {
                this.showEmptyState();
            }
        } catch (error) {
            console.error('Error loading files:', error);
            this.showError('加载文件列表失败，请检查后端服务是否正常运行');
        } finally {
            this.hideLoading();
        }
    }

    /**
     * Render image cards in the gallery
     * @param {Array} files - Array of file data
     */
    renderImageCards(files) {
        this.fileGallery.innerHTML = '';
        this.imageElements = [];
        
        files.forEach((fileData, index) => {
            const cardElement = this.createImageCard(fileData, index);
            this.fileGallery.appendChild(cardElement);
        });
    }

    /**
     * Create an image card element
     * @param {Object} fileData - File data object
     * @param {number} index - Index of the image in the gallery
     * @returns {HTMLElement} Card element
     */
    createImageCard(fileData, index) {
        const col = document.createElement('div');
        col.className = 'col-md-4 col-lg-3 mb-4';

        // Use thumbnail for gallery view, full image for preview
        const thumbnailUrl = this.apiClient.getThumbnailUrl(fileData.png_file.name);
        const imageUrl = this.apiClient.getImageUrl(fileData.png_file.name);
        const downloadUrl = fileData.has_csv ? 
            this.apiClient.getDownloadUrl(fileData.csv_file.name) : null;

        col.innerHTML = `
            <div class="card h-100 shadow-sm">
                <div class="position-relative image-card-container" style="cursor: pointer;">
                    <img ${this.lazyLoadObserver ? `data-src="${thumbnailUrl}"` : `src="${thumbnailUrl}"`}
                         class="card-img-top lazy-image" 
                         alt="${fileData.png_file.name}"
                         data-index="${index}"
                         data-filename="${fileData.png_file.name}"
                         onerror="this.parentElement.innerHTML='<div class=\\"image-placeholder\\"><i class=\\"bi bi-image\\" style=\\"font-size: 2rem;\\"></i></div>'">
                    ${fileData.has_csv ? 
                        '<span class="badge bg-success status-badge"><i class="bi bi-check-circle"></i></span>' :
                        '<span class="badge bg-warning status-badge"><i class="bi bi-exclamation-circle"></i></span>'
                    }
                    <div class="image-overlay">
                        <i class="bi bi-zoom-in"></i>
                    </div>
                </div>
                <div class="card-body">
                    <h6 class="card-title">${fileData.png_file.name}</h6>
                    <div class="file-info">
                        <small class="text-muted">
                            <i class="bi bi-file-earmark-image"></i>
                            ${this.formatFileSize(fileData.png_file.size)}
                        </small>
                    </div>
                    <div class="d-grid">
                        ${fileData.has_csv ? 
                            `<a href="${downloadUrl}" 
                               class="btn btn-primary btn-sm btn-download" 
                               download="${fileData.csv_file.name}">
                                <i class="bi bi-download"></i> 下载CSV
                             </a>` :
                            `<button class="btn btn-secondary btn-sm btn-download" disabled>
                                <i class="bi bi-x-circle"></i> 无数据文件
                             </button>`
                        }
                    </div>
                </div>
            </div>
        `;

        // Get the image element and set up lazy loading
        const imgElement = col.querySelector('.lazy-image');
        if (this.lazyLoadObserver && imgElement) {
            this.lazyLoadObserver.observe(imgElement);
        }
        
        // Store full image URL for preview (not thumbnail)
        this.imageElements.push({
            url: imageUrl,
            filename: fileData.png_file.name
        });
        
        // Add click event for image preview
        const imageContainer = col.querySelector('.image-card-container');
        imageContainer.addEventListener('click', () => {
            this.showImagePreview(index);
        });

        return col;
    }

    /**
     * Format file size for display
     * @param {number} bytes - File size in bytes
     * @returns {string} Formatted file size
     */
    formatFileSize(bytes) {
        if (bytes === 0) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
    }

    /**
     * Show loading indicator
     */
    showLoading() {
        this.loadingIndicator.classList.remove('d-none');
        this.fileGallery.innerHTML = '';
        this.refreshBtn.disabled = true;
    }

    /**
     * Hide loading indicator
     */
    hideLoading() {
        this.loadingIndicator.classList.add('d-none');
        this.refreshBtn.disabled = false;
    }

    /**
     * Show error message
     * @param {string} message - Error message to display
     */
    showError(message) {
        this.errorMessage.textContent = message;
        this.errorAlert.classList.remove('d-none');
    }

    /**
     * Hide error message
     */
    hideError() {
        this.errorAlert.classList.add('d-none');
    }

    /**
     * Show empty state
     */
    showEmptyState() {
        this.emptyState.classList.remove('d-none');
        this.fileGallery.innerHTML = '';
    }

    /**
     * Hide empty state
     */
    hideEmptyState() {
        this.emptyState.classList.add('d-none');
    }

    /**
     * Show image preview modal
     * @param {number} index - Index of the image to preview
     */
    showImagePreview(index) {
        if (index < 0 || index >= this.imageElements.length) return;
        
        this.currentImageIndex = index;
        const imageData = this.imageElements[index];
        
        this.previewImage.src = imageData.url;
        this.previewTitle.textContent = imageData.filename;
        this.updateImageCounter();
        this.updateNavigationButtons();
        
        this.previewModal.show();
    }

    /**
     * Show previous image in preview
     */
    showPreviousImage() {
        if (this.currentImageIndex > 0) {
            this.showImagePreview(this.currentImageIndex - 1);
        }
    }

    /**
     * Show next image in preview
     */
    showNextImage() {
        if (this.currentImageIndex < this.imageElements.length - 1) {
            this.showImagePreview(this.currentImageIndex + 1);
        }
    }

    /**
     * Update image counter display
     */
    updateImageCounter() {
        this.imageCounter.textContent = `${this.currentImageIndex + 1} / ${this.imageElements.length}`;
    }

    /**
     * Update navigation button states
     */
    updateNavigationButtons() {
        this.prevImageBtn.disabled = this.currentImageIndex === 0;
        this.nextImageBtn.disabled = this.currentImageIndex === this.imageElements.length - 1;
    }
}