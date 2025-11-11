# Development Configuration for File Gallery Viewer

import os

class DevelopmentConfig:
    """Development environment configuration"""
    
    # Flask settings
    DEBUG = True
    TESTING = False
    
    # Data directory
    DATA_DIR = os.environ.get('DATA_DIR', os.path.join(os.path.dirname(__file__), '..', 'data'))
    
    # Server settings
    HOST = '0.0.0.0'
    PORT = int(os.environ.get('PORT', 9000))
    
    # CORS settings - Allow all origins in development
    CORS_ORIGINS = '*'
    
    # Logging
    LOG_LEVEL = 'DEBUG'
    
    # Security - Not critical in development
    SECRET_KEY = 'dev-secret-key'
    
    # File handling
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100MB max file size
    ALLOWED_EXTENSIONS = {'png', 'PNG'}
    CSV_EXTENSIONS = {'csv', 'CSV'}
    
    # Cache settings - Shorter timeout for development
    CACHE_TIMEOUT = 60  # 1 minute
