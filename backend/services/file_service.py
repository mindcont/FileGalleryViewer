"""
File Service Module
Handles scanning local directories and matching PNG/CSV files
"""

import os
import time
import hashlib
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Dict
from dataclasses import dataclass, asdict
from PIL import Image
import io


@dataclass
class FileInfo:
    """Information about a file"""
    name: str
    path: str
    size: int
    last_modified: str
    file_type: str  # 'png' or 'csv'
    
    def to_dict(self):
        return asdict(self)


@dataclass
class FileMatch:
    """Matched PNG and CSV file pair"""
    png_file: FileInfo
    csv_file: Optional[FileInfo]
    has_csv: bool
    
    def to_dict(self):
        return {
            'png_file': self.png_file.to_dict(),
            'csv_file': self.csv_file.to_dict() if self.csv_file else None,
            'has_csv': self.has_csv
        }


class FileService:
    """Service for scanning and managing local files"""
    
    def __init__(self, directory_path: str, cache_ttl: int = 300):
        """
        Initialize FileService with a directory path
        
        Args:
            directory_path: Path to the directory to scan
            cache_ttl: Cache time-to-live in seconds (default: 300 = 5 minutes)
        """
        self.directory_path = Path(directory_path)
        if not self.directory_path.exists():
            raise ValueError(f"Directory does not exist: {directory_path}")
        if not self.directory_path.is_dir():
            raise ValueError(f"Path is not a directory: {directory_path}")
        
        # Cache configuration
        self.cache_ttl = cache_ttl
        self._cache: Optional[List[FileMatch]] = None
        self._cache_timestamp: float = 0
        self._directory_hash: Optional[str] = None
        
        # Thumbnail cache directory
        self.thumbnail_dir = self.directory_path / '.thumbnails'
        self.thumbnail_dir.mkdir(exist_ok=True)
    
    def _get_file_info(self, file_path: Path, file_type: str) -> FileInfo:
        """
        Extract file information
        
        Args:
            file_path: Path to the file
            file_type: Type of file ('png' or 'csv')
            
        Returns:
            FileInfo object with file details
        """
        stat = file_path.stat()
        return FileInfo(
            name=file_path.name,
            path=str(file_path),
            size=stat.st_size,
            last_modified=datetime.fromtimestamp(stat.st_mtime).isoformat(),
            file_type=file_type
        )
    
    def _scan_png_files(self) -> List[FileInfo]:
        """
        Scan directory for PNG files
        
        Returns:
            List of FileInfo objects for PNG files
        """
        png_files = []
        seen_files = set()
        
        # Scan for both lowercase and uppercase extensions
        for pattern in ['*.png', '*.PNG']:
            for file_path in self.directory_path.glob(pattern):
                if file_path.is_file():
                    # Use resolved path to avoid duplicates on case-insensitive filesystems
                    resolved_path = str(file_path.resolve())
                    if resolved_path not in seen_files:
                        seen_files.add(resolved_path)
                        png_files.append(self._get_file_info(file_path, 'png'))
        
        return png_files
    
    def _scan_csv_files(self) -> List[FileInfo]:
        """
        Scan directory for CSV files
        
        Returns:
            List of FileInfo objects for CSV files
        """
        csv_files = []
        seen_files = set()
        
        # Scan for both lowercase and uppercase extensions
        for pattern in ['*.csv', '*.CSV']:
            for file_path in self.directory_path.glob(pattern):
                if file_path.is_file():
                    # Use resolved path to avoid duplicates on case-insensitive filesystems
                    resolved_path = str(file_path.resolve())
                    if resolved_path not in seen_files:
                        seen_files.add(resolved_path)
                        csv_files.append(self._get_file_info(file_path, 'csv'))
        
        return csv_files
    
    def _match_png_to_csv(self, png_filename: str) -> str:
        """
        Get the expected CSV filename for a PNG file
        
        Args:
            png_filename: Name of the PNG file
            
        Returns:
            Expected CSV filename
        """
        base_name = png_filename.replace('.png', '').replace('.PNG', '')
        return base_name + '.csv'
    
    def match_files(self, png_files: List[FileInfo], csv_files: List[FileInfo]) -> List[FileMatch]:
        """
        Match PNG files with their corresponding CSV files
        
        Args:
            png_files: List of PNG FileInfo objects
            csv_files: List of CSV FileInfo objects
            
        Returns:
            List of FileMatch objects
        """
        # Create a dictionary for quick CSV lookup
        csv_dict = {csv_file.name.lower(): csv_file for csv_file in csv_files}
        
        matches = []
        for png_file in png_files:
            expected_csv_name = self._match_png_to_csv(png_file.name)
            csv_file = csv_dict.get(expected_csv_name.lower())
            
            matches.append(FileMatch(
                png_file=png_file,
                csv_file=csv_file,
                has_csv=csv_file is not None
            ))
        
        return matches
    
    def _get_directory_hash(self) -> str:
        """
        Calculate a hash of the directory state based on file modification times
        
        Returns:
            Hash string representing current directory state
        """
        file_states = []
        for file_path in sorted(self.directory_path.glob('*')):
            if file_path.is_file() and (file_path.suffix.lower() in ['.png', '.csv']):
                stat = file_path.stat()
                file_states.append(f"{file_path.name}:{stat.st_mtime}:{stat.st_size}")
        
        state_string = '|'.join(file_states)
        return hashlib.md5(state_string.encode()).hexdigest()
    
    def _is_cache_valid(self) -> bool:
        """
        Check if the cache is still valid
        
        Returns:
            True if cache is valid, False otherwise
        """
        if self._cache is None:
            return False
        
        # Check if cache has expired
        current_time = time.time()
        if current_time - self._cache_timestamp > self.cache_ttl:
            return False
        
        # Check if directory has changed
        current_hash = self._get_directory_hash()
        if current_hash != self._directory_hash:
            return False
        
        return True
    
    def invalidate_cache(self):
        """Manually invalidate the cache"""
        self._cache = None
        self._cache_timestamp = 0
        self._directory_hash = None
    
    def scan_files(self, use_cache: bool = True) -> List[FileMatch]:
        """
        Scan directory and match PNG files with CSV files
        
        Args:
            use_cache: Whether to use cached results (default: True)
        
        Returns:
            List of FileMatch objects with matched files
        """
        # Return cached results if valid
        if use_cache and self._is_cache_valid():
            return self._cache
        
        # Perform fresh scan
        png_files = self._scan_png_files()
        csv_files = self._scan_csv_files()
        matches = self.match_files(png_files, csv_files)
        
        # Update cache
        self._cache = matches
        self._cache_timestamp = time.time()
        self._directory_hash = self._get_directory_hash()
        
        return matches
    
    def generate_thumbnail(self, image_path: Path, max_size: tuple = (400, 400)) -> Optional[bytes]:
        """
        Generate a thumbnail for an image
        
        Args:
            image_path: Path to the image file
            max_size: Maximum dimensions for the thumbnail (width, height)
        
        Returns:
            Thumbnail image as bytes, or None if generation fails
        """
        try:
            # Check if thumbnail already exists
            thumbnail_name = f"{image_path.stem}_thumb.jpg"
            thumbnail_path = self.thumbnail_dir / thumbnail_name
            
            # Check if thumbnail is up-to-date
            if thumbnail_path.exists():
                image_mtime = image_path.stat().st_mtime
                thumb_mtime = thumbnail_path.stat().st_mtime
                if thumb_mtime >= image_mtime:
                    # Return cached thumbnail
                    return thumbnail_path.read_bytes()
            
            # Generate new thumbnail
            with Image.open(image_path) as img:
                # Convert RGBA to RGB if necessary
                if img.mode in ('RGBA', 'LA', 'P'):
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
                    img = background
                
                # Create thumbnail
                img.thumbnail(max_size, Image.Resampling.LANCZOS)
                
                # Save to bytes
                output = io.BytesIO()
                img.save(output, format='JPEG', quality=85, optimize=True)
                thumbnail_bytes = output.getvalue()
                
                # Cache thumbnail to disk
                thumbnail_path.write_bytes(thumbnail_bytes)
                
                return thumbnail_bytes
        
        except Exception as e:
            print(f"Error generating thumbnail for {image_path}: {e}")
            return None
    
    def get_cache_stats(self) -> Dict:
        """
        Get cache statistics
        
        Returns:
            Dictionary with cache statistics
        """
        return {
            'is_cached': self._cache is not None,
            'cache_age': time.time() - self._cache_timestamp if self._cache else None,
            'cache_ttl': self.cache_ttl,
            'cached_items': len(self._cache) if self._cache else 0,
            'thumbnail_count': len(list(self.thumbnail_dir.glob('*_thumb.jpg')))
        }
