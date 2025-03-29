import pytest
from unittest.mock import patch, MagicMock
import json

from app.services.cache import get_cache, set_cache, delete_cache, clear_cache_pattern

@patch('app.services.cache.redis_client')
def test_get_cache_hit(mock_redis):
    """Test successfully getting data from cache"""
    # Mock the Redis client to return a cached value
    mock_redis.get.return_value = json.dumps({"test": "data"})
    
    # Call get_cache
    result = get_cache("test_key")
    
    # Check the result
    assert result == {"test": "data"}
    mock_redis.get.assert_called_once_with("test_key")

@patch('app.services.cache.redis_client')
def test_get_cache_miss(mock_redis):
    """Test cache miss returning None"""
    # Mock the Redis client to return None (cache miss)
    mock_redis.get.return_value = None
    
    # Call get_cache
    result = get_cache("test_key")
    
    # Check the result
    assert result is None
    mock_redis.get.assert_called_once_with("test_key")

@patch('app.services.cache.redis_client')
def test_set_cache(mock_redis):
    """Test setting a value in cache"""
    # Call set_cache
    set_cache("test_key", {"test": "data"}, 60)
    
    # Check that Redis client was called correctly
    mock_redis.setex.assert_called_once_with("test_key", 60, json.dumps({"test": "data"}))

@patch('app.services.cache.redis_client')
def test_delete_cache(mock_redis):
    """Test deleting a value from cache"""
    # Call delete_cache
    delete_cache("test_key")
    
    # Check that Redis client was called correctly
    mock_redis.delete.assert_called_once_with("test_key")

@patch('app.services.cache.redis_client')
def test_clear_cache_pattern(mock_redis):
    """Test clearing cache keys matching a pattern"""
    # Mock the Redis client to return some keys
    mock_redis.scan_iter.return_value = ["test_pattern_1", "test_pattern_2"]
    
    # Call clear_cache_pattern
    clear_cache_pattern("test_pattern")
    
    # Check that Redis client was called correctly
    mock_redis.scan_iter.assert_called_once_with("test_pattern*")
    assert mock_redis.delete.call_count == 2 