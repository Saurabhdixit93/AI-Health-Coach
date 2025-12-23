"""
Redis caching service for session management and frequently accessed data.
"""
import redis
import json
from typing import Optional, Any
from ..config import settings


class CacheService:
    """Redis cache service for improved performance."""
    
    def __init__(self):
        self.redis_client = redis.from_url(
            settings.REDIS_URL,
            decode_responses=True
        )
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        try:
            value = self.redis_client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            print(f"Cache get error: {e}")
            return None
    
    def set(self, key: str, value: Any, expiry: int = 3600) -> bool:
        """
        Set value in cache with expiry time.
        
        Args:
            key: Cache key
            value: Value to cache (will be JSON serialized)
            expiry: Expiry time in seconds (default 1 hour)
        """
        try:
            self.redis_client.setex(
                key,
                expiry,
                json.dumps(value)
            )
            return True
        except Exception as e:
            print(f"Cache set error: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete key from cache."""
        try:
            self.redis_client.delete(key)
            return True
        except Exception as e:
            print(f"Cache delete error: {e}")
            return False
    
    def set_typing_indicator(self, user_id: str, is_typing: bool) -> bool:
        """
        Set typing indicator status for a user.
        
        Args:
            user_id: User ID
            is_typing: Whether AI is typing
        """
        key = f"typing:{user_id}"
        if is_typing:
            return self.set(key, {"is_typing": True}, expiry=30)
        else:
            return self.delete(key)
    
    def get_typing_indicator(self, user_id: str) -> bool:
        """Get typing indicator status for a user."""
        key = f"typing:{user_id}"
        result = self.get(key)
        return result.get("is_typing", False) if result else False
    
    def cache_protocols(self, protocols: list) -> bool:
        """Cache all protocols for fast access."""
        return self.set("protocols:all", protocols, expiry=86400)  # 24 hours
    
    def get_cached_protocols(self) -> Optional[list]:
        """Get cached protocols."""
        return self.get("protocols:all")


# Global cache service instance
cache_service = CacheService()
