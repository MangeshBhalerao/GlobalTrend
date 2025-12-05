import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Any, Dict
from src.config import settings


class CacheManager:
    """Manages caching of API responses to local JSON files."""
    
    def __init__(self, cache_dir: Optional[Path] = None, expiry_seconds: Optional[int] = None):
        """
        Initialize cache manager.
        
        Args:
            cache_dir: Directory to store cache files
            expiry_seconds: Time in seconds before cache expires
        """
        self.cache_dir = cache_dir or settings.cache_path
        self.expiry_seconds = expiry_seconds or settings.cache_expiry_seconds
        
        # Create cache directory if it doesn't exist
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_cache_file_path(self, key: str) -> Path:
        """Get the file path for a cache key."""
        # Sanitize key for filename
        safe_key = key.replace("/", "_").replace(":", "_").replace("?", "_").replace("&", "_")
        return self.cache_dir / f"{safe_key}.json"
    
    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve data from cache if it exists and is not expired.
        
        Args:
            key: Cache key
            
        Returns:
            Cached data if valid, None otherwise
        """
        cache_file = self._get_cache_file_path(key)
        
        if not cache_file.exists():
            return None
        
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            # Check if cache has expired
            cached_at = datetime.fromisoformat(cache_data['cached_at'])
            if datetime.now() - cached_at > timedelta(seconds=self.expiry_seconds):
                # Cache expired, remove file
                cache_file.unlink()
                return None
            
            return {
                'data': cache_data['data'],
                'cached': True,
                'cached_at': cached_at
            }
        
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            # Invalid cache file, remove it
            cache_file.unlink(missing_ok=True)
            return None
    
    def set(self, key: str, data: Any) -> None:
        """
        Store data in cache.
        
        Args:
            key: Cache key
            data: Data to cache
        """
        cache_file = self._get_cache_file_path(key)
        
        cache_data = {
            'data': data,
            'cached_at': datetime.now().isoformat()
        }
        
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            # If caching fails, log but don't crash
            print(f"Warning: Failed to cache data: {e}")
    
    def clear(self) -> int:
        """
        Clear all cache files.
        
        Returns:
            Number of files deleted
        """
        count = 0
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                cache_file.unlink()
                count += 1
            except Exception:
                pass
        
        return count
    
    def clear_expired(self) -> int:
        """
        Clear only expired cache files.
        
        Returns:
            Number of expired files deleted
        """
        count = 0
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                
                cached_at = datetime.fromisoformat(cache_data['cached_at'])
                if datetime.now() - cached_at > timedelta(seconds=self.expiry_seconds):
                    cache_file.unlink()
                    count += 1
            except Exception:
                # If we can't read the file, remove it
                cache_file.unlink(missing_ok=True)
                count += 1
        
        return count
