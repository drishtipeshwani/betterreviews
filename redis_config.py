import redis
import os

class RedisConfig:
    """Centralized Redis configuration and client management"""
    
    def __init__(self):
        self.host = os.getenv('REDIS_HOST', 'localhost')
        self.port = int(os.getenv('REDIS_PORT', 6379))
        self.db = int(os.getenv('REDIS_DB', 0))
        self.decode_responses = True
        self._client = None
        self._redis_url = f"redis://{self.host}:{self.port}"
        self._index = None
        self._index_schema = None

    @property
    def client(self):
        """Get Redis client instance (singleton pattern)"""
        if self._client is None:
            self._client = redis.Redis(
                host=self.host,
                port=self.port,
                db=self.db,
                decode_responses=self.decode_responses
            )
        return self._client
    
    @property
    def redis_url(self):
        """Get Redis URL for RedisVL"""
        return self._redis_url
    
    def test_connection(self):
        """Test Redis connection"""
        try:
            self.client.ping()
            return True, "Redis connection successful"
        except Exception as e:
            return False, f"Redis connection failed: {str(e)}"
    
    def close_connection(self):
        """Close Redis connection"""
        if self._client:
            self._client.close()
            self._client = None
            self._index = None
            
    def get_search_index(self, index_name):
        """Get the search index from Redis (cached)"""
        try:
            if self._index is None:
                self._index = self.client.ft(index_name)
            print(f"Search index '{index_name}' fetched successfully: {self._index}")
            return self._index
        except Exception as e:
            return f"Error fetching search index: {str(e)}"

    def get_index_info(self, index_name):
        """Get index information from Redis (cached)"""
        try:
            if self._index_schema is None:
                # Fetch schema from Redis and cache it
                self._index_schema = self.client.ft(index_name).info()
            print(f"Index schema for '{index_name}': {self._index_schema}")
            return self._index_schema
        except Exception as e:
            return f"Index not found: {str(e)}"
    
    def index_exists(self, index_name):
        """Check if index exists in Redis"""
        try:
            self.client.ft(index_name).info()
            return True
        except:
            return False
    
    def clear_schema_cache(self):
        """Clear cached schema (call this if index is recreated)"""
        self._index_schema = None

# Global Redis instance
redis_config = RedisConfig()

# Convenience functions
def get_redis_client():
    """Get the shared Redis client instance"""
    return redis_config.client

def get_redis_url():
    """Get the Redis URL for RedisVL"""
    return redis_config.redis_url

def index_exists():
    """Check if the review index exists"""
    return redis_config.index_exists(INDEX_NAME)

def get_search_index():
    """Get the search index from Redis"""
    return redis_config.get_search_index(INDEX_NAME)

def get_cached_index_info():
    """Get the cached index schema"""
    return redis_config.get_index_info(INDEX_NAME)

# Index name constant
INDEX_NAME = "review_idx"
