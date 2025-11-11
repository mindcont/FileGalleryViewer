# Production Configuration for File Gallery Viewer

import os

class ProductionConfig:
    """Production environment configuration"""
    
    # Flask settings
    DEBUG = False
    TESTING = False
    
    # Data directory
    DATA_DIR = os.environ.get('DATA_DIR', '/app/data')
    
    # Server settings
    HOST = '0.0.0.0'
    PORT = int(os.environ.get('PORT', 9000))
    
    # CORS settings
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*').split(',')
    
    # Logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    
    # Security
    SECRET_KEY = os.environ.get('SECRET_KEY', 'change-this-in-production')
    
    # File handling
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100MB max file size
    ALLOWED_EXTENSIONS = {'png', 'PNG'}
    CSV_EXTENSIONS = {'csv', 'CSV'}
    
    # Cache settings
    CACHE_TIMEOUT = int(os.environ.get('CACHE_TIMEOUT', 300))  # 5 minutes
    
    # Performance
    GUNICORN_WORKERS = int(os.environ.get('GUNICORN_WORKERS', 4))
    GUNICORN_TIMEOUT = int(os.environ.get('GUNICORN_TIMEOUT', 120))
