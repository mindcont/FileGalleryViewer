# File Gallery Viewer Backend
# Main application entry point

import os
import logging
from flask import Flask, jsonify
from flask_cors import CORS
from services.file_service import FileService
from routes.api import register_routes

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Configure CORS to allow frontend access
CORS(app, origins="*")

# Get data directory from environment variable or use default
DATA_DIR = os.environ.get('DATA_DIR', os.path.join(os.path.dirname(__file__), '..', 'data'))
logger.info(f"Data directory: {DATA_DIR}")


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    logger.warning(f"404 error: {error}")
    return jsonify({
        'error': 'Resource not found',
        'message': str(error)
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"500 error: {error}")
    return jsonify({
        'error': 'Internal server error',
        'message': 'An unexpected error occurred'
    }), 500


@app.errorhandler(403)
def forbidden(error):
    """Handle 403 errors"""
    logger.warning(f"403 error: {error}")
    return jsonify({
        'error': 'Forbidden',
        'message': 'Access to this resource is forbidden'
    }), 403


@app.errorhandler(400)
def bad_request(error):
    """Handle 400 errors"""
    logger.warning(f"400 error: {error}")
    return jsonify({
        'error': 'Bad request',
        'message': str(error)
    }), 400


@app.route('/')
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "File Gallery Viewer Backend is running",
        "data_dir": DATA_DIR
    })


# Create data directory if it doesn't exist
os.makedirs(DATA_DIR, exist_ok=True)

# Initialize FileService
try:
    file_service = FileService(DATA_DIR)
    logger.info(f"FileService initialized with directory: {DATA_DIR}")
except Exception as e:
    logger.error(f"Failed to initialize FileService: {e}")
    exit(1)

# Register API routes
register_routes(app, file_service, DATA_DIR)

if __name__ == '__main__':
    logger.info("Starting File Gallery Viewer Backend...")
    app.run(debug=True, host='0.0.0.0', port=9000)