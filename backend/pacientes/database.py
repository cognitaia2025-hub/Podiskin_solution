"""
Database connection utilities for the pacientes module.
"""

import os
from typing import Optional
import asyncpg
from contextlib import asynccontextmanager


class DatabaseConnection:
    """Database connection manager for async operations."""
    
    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None
    
    async def connect(self):
        """Create database connection pool."""
        if self.pool is None:
            self.pool = await asyncpg.create_pool(
                host=os.getenv("DB_HOST", "127.0.0.1"),
                port=int(os.getenv("DB_PORT", "5432")),
                user=os.getenv("DB_USER", "podoskin_user"),
                password=os.getenv("DB_PASSWORD", "podoskin_password_123"),
                database=os.getenv("DB_NAME", "podoskin_db"),
                min_size=2,
                max_size=10,
            )
    
    async def disconnect(self):
        """Close database connection pool."""
        if self.pool:
            await self.pool.close()
            self.pool = None
    
    @asynccontextmanager
    async def get_connection(self):
        """Get a database connection from the pool."""
        if self.pool is None:
            await self.connect()
        
        async with self.pool.acquire() as connection:
            yield connection


# Global database connection instance
db = DatabaseConnection()


async def get_db_connection():
    """Dependency to get database connection."""
    async with db.get_connection() as conn:
        yield conn
