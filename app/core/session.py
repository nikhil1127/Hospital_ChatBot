"""
Session Management for Hospital Bot
====================================
Manages user conversation state using Redis.
"""

import json
import os
from typing import Optional

# Try to import redis, fallback to memory dict if not available
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    print("Warning: redis not installed. Using in-memory session storage (will be lost on restart).")


class SessionManager:
    """Manages user sessions with Redis (or in-memory fallback)"""

    def __init__(self):
        self.redis_client = None
        self.memory_store = {}  # Fallback storage

        if REDIS_AVAILABLE:
            try:
                redis_host = os.getenv("REDIS_HOST", "localhost")
                redis_port = int(os.getenv("REDIS_PORT", 6379))
                redis_db = int(os.getenv("REDIS_DB", 0))

                self.redis_client = redis.Redis(
                    host=redis_host,
                    port=redis_port,
                    db=redis_db,
                    decode_responses=True,
                    socket_connect_timeout=5
                )
                # Test connection
                self.redis_client.ping()
                print(f"Connected to Redis at {redis_host}:{redis_port}")
            except Exception as e:
                print(f"Redis connection failed: {e}. Using in-memory storage.")
                self.redis_client = None

    def get_session(self, user_id: str) -> dict:
        """Retrieve user session from storage"""
        session_key = f"session:{user_id}"

        if self.redis_client:
            try:
                data = self.redis_client.get(session_key)
                if data:
                    return json.loads(data)
            except Exception as e:
                print(f"Redis get error: {e}")

        # Fallback to memory
        if user_id in self.memory_store:
            return self.memory_store[user_id].copy()

        # Return default session structure
        return {
            "state": "START",
            "context": {},
            "history": []
        }

    def update_session(self, user_id: str, session_data: dict):
        """Update user session with 30-minute TTL"""
        session_key = f"session:{user_id}"

        if self.redis_client:
            try:
                # Store with 30-minute expiry (1800 seconds)
                self.redis_client.setex(
                    session_key,
                    1800,
                    json.dumps(session_data)
                )
                return
            except Exception as e:
                print(f"Redis set error: {e}")

        # Fallback to memory
        self.memory_store[user_id] = session_data.copy()

    def clear_session(self, user_id: str):
        """Clear user session"""
        session_key = f"session:{user_id}"

        if self.redis_client:
            try:
                self.redis_client.delete(session_key)
            except Exception as e:
                print(f"Redis delete error: {e}")

        # Also clear from memory
        if user_id in self.memory_store:
            del self.memory_store[user_id]

    def get_session_ttl(self, user_id: str) -> Optional[int]:
        """Get remaining TTL for session in seconds"""
        session_key = f"session:{user_id}"

        if self.redis_client:
            try:
                ttl = self.redis_client.ttl(session_key)
                return ttl if ttl > 0 else None
            except Exception as e:
                print(f"Redis TTL error: {e}")

        return None


# Global session manager instance
session_manager = SessionManager()
