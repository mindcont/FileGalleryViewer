"""
API Routes for File Gallery Viewer
Provides endpoints for file listing, image serving, and CSV downloads
"""

import os
import logging
from pathlib import Path
from flask import Blueprint, jsonify, send_file, abort
from werkzeug.utils import secure_filename

logger = logging.getLogger(__name__)

api_bp = Blueprint('api', __name__, url_prefix='/api')


def validate_filename(filename: str, data_dir: str) -> Path:
    """
    Validate filename and prevent directory traversal attacks
    
    Args:
        filename: The filename to validate
        data_dir: The base data directory
        
    Returns:
        Validated Path object
        
    Raises:
        ValueError: If filename is invalid or contains path traversal attempts
    """
    if not filename:
        raise ValueError("Filename cannot be empty")
    
    # Use secure_filename to sanitize the filename
    safe_filename = secure_filename(filename)
    
    if not safe_filename:
        raise ValueError("Invalid filename")
    
    # Construct the full path
    data_path = Path(data_dir).resolve()
    file_path = (data_path / safe_filename).resolve()
    
    # Ensure the file path is within the data directory (prevent directory traversal)
    if not str(file_path).startswith(str(data_path)):
        raise ValueError("Invalid file path - directory traversal detected")
    
    return file_path




















def register_routes(app, file_service, data_dir):
    """
    Register all API routes with the Flask app
    
    Args:
        app: Flask application instance
        file_service: FileService instance
        data_dir: Base data directory path
    """
    
    @api_bp.route('/files', methods=['GET'])
    def get_files():
        try:
            logger.info("Scanning files...")
            matches = file_service.scan_files()
            files_data = [match.to_dict() for match in matches]
            response = {'files': files_data, 'total_count': len(files_data)}
            logger.info(f"Found {len(files_data)} PNG files")
            return jsonify(response), 200
        except Exception as e:
            logger.error(f"Error scanning files: {e}")
            return jsonify({'error': 'Failed to scan files', 'message': str(e)}), 500
    
    @api_bp.route('/image/<filename>', methods=['GET'])
    def get_image(filename):
        try:
            file_path = validate_filename(filename, data_dir)
            if not file_path.exists():
                abort(404, description=f"Image not found: {filename}")
            if not filename.lower().endswith('.png'):
                abort(400, description="Only PNG files are allowed")
            return send_file(file_path, mimetype='image/png')
        except ValueError as e:
            abort(403, description=str(e))
        except Exception as e:
            logger.error(f"Error serving image {filename}: {e}")
            abort(500, description="Failed to serve image")
    
    @api_bp.route('/thumbnail/<filename>', methods=['GET'])
    def get_thumbnail(filename):
        try:
            file_path = validate_filename(filename, data_dir)
            if not file_path.exists():
                abort(404, description=f"Image not found: {filename}")
            if not filename.lower().endswith('.png'):
                abort(400, description="Only PNG files are allowed")
            
            # Generate thumbnail
            thumbnail_bytes = file_service.generate_thumbnail(file_path)
            if thumbnail_bytes is None:
                abort(500, description="Failed to generate thumbnail")
            
            from flask import Response
            return Response(thumbnail_bytes, mimetype='image/jpeg')
        except ValueError as e:
            abort(403, description=str(e))
        except Exception as e:
            logger.error(f"Error serving thumbnail {filename}: {e}")
            abort(500, description="Failed to serve thumbnail")
    
    @api_bp.route('/download/<filename>', methods=['GET'])
    def download_csv(filename):
        try:
            file_path = validate_filename(filename, data_dir)
            if not file_path.exists():
                abort(404, description=f"CSV file not found: {filename}")
            if not filename.lower().endswith('.csv'):
                abort(400, description="Only CSV files are allowed")
            return send_file(file_path, mimetype='text/csv', as_attachment=True, download_name=filename)
        except ValueError as e:
            abort(403, description=str(e))
        except Exception as e:
            logger.error(f"Error serving CSV {filename}: {e}")
            abort(500, description="Failed to serve CSV file")
    
    app.register_blueprint(api_bp)
    logger.info("API routes registered")
