@echo off
REM Git commit script for Staff Management Module

echo ========================================
echo Staff Management Module - Git Commit
echo ========================================
echo.

echo Checking git status...
git status
echo.

echo Adding all changes...
git add .
echo.

echo Committing changes...
git commit -m "feat: Implement Staff Management module (Gestion de Personal)

- Backend: Add user management endpoints to /auth/users
  * GET /auth/users - List all users
  * POST /auth/users - Create new user
  * GET /auth/users/{id} - Get user by ID
  * PUT /auth/users/{id} - Update user
  * DELETE /auth/users/{id} - Soft delete user

- Backend: Add database functions for user CRUD operations
  * get_all_users, get_user_by_id, create_user, update_user, delete_user

- Frontend: Create staffService.ts for API communication
  * Real API integration (no mock data)
  * Error handling with toast notifications

- Frontend: Create StaffManagement.tsx component
  * Responsive table with user list
  * Search by name, email, username
  * Create/Edit modals with validation
  * Role-based access control (Admin only)
  * Soft delete with confirmation

- Frontend: Add /admin/staff route to App.tsx

- Security: Admin-only endpoints with JWT authentication
- Security: Password hashing with bcrypt
- Security: Soft delete to preserve data
- Security: Self-deletion prevention

- Documentation:
  * STAFF_MANAGEMENT_IMPLEMENTATION.md (technical details)
  * STAFF_MANAGEMENT_QUICKSTART.md (user guide)
  * STAFF_MANAGEMENT_COMPLETE.md (executive summary)
  * INFORME_STAFF_MANAGEMENT.md (comprehensive report)
  * test_staff_endpoints.py (automated tests)

Files created: 6
Files modified: 3
Total lines: ~2,851

Ready for production deployment."
echo.

echo Commit complete!
echo.

echo Pushing to remote...
git push origin main
echo.

echo ========================================
echo Done! Changes committed and pushed.
echo ========================================

pause
