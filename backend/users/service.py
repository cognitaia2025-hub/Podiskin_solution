"""
Users Service
=============
Business logic for user management operations.
"""

from auth.database import (
    get_all_users,
    get_user_by_id,
    create_user,
    update_user,
    delete_user
)

# Re-export database functions
__all__ = [
    "get_all_users",
    "get_user_by_id",
    "create_user",
    "update_user",
    "delete_user"
]
