"""
Users Module
============
User management endpoints (CRUD for system users).
Separated from auth module for clean architecture.
"""

from .router import router

__all__ = ["router"]
