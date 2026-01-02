#!/usr/bin/env python3
"""
Architecture Refactoring Script
================================
Automates the refactoring of Staff Management module for clean architecture.

WARNING: This script makes significant changes. Commit your work first!
"""

import os
import shutil
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent

def create_directories():
    """Create necessary directory structure."""
    print("\n📁 Creating directory structure...")
    
    dirs = [
        BASE_DIR / "Frontend" / "src" / "pages" / "admin",
        BASE_DIR / "Frontend" / "src" / "components" / "admin",
        BASE_DIR / "backend" / "users"
    ]
    
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)
        print(f"   ✓ {d.relative_to(BASE_DIR)}")

def move_frontend_files():
    """Move and organize frontend files."""
    print("\n📦 Refactoring frontend files...")
    
    # Copy component files
    files_to_copy = [
        ("StaffTable.tsx.new", "Frontend/src/components/admin/StaffTable.tsx"),
        ("UserFormModal.tsx.new", "Frontend/src/components/admin/UserFormModal.tsx"),
        ("StaffManagement.tsx.new", "Frontend/src/pages/admin/StaffManagement.tsx"),
    ]
    
    for src, dest in files_to_copy:
        src_path = BASE_DIR / src
        dest_path = BASE_DIR / dest
        
        if src_path.exists():
            shutil.copy2(src_path, dest_path)
            print(f"   ✓ Copied {src} → {dest}")
        else:
            print(f"   ✗ Missing: {src}")
    
    # Delete old file
    old_file = BASE_DIR / "Frontend" / "src" / "pages" / "StaffManagement.tsx"
    if old_file.exists():
        old_file.unlink()
        print(f"   ✓ Deleted old StaffManagement.tsx")

def move_backend_files():
    """Move and organize backend files."""
    print("\n📦 Creating backend users module...")
    
    files_to_copy = [
        ("users__init__.py.new", "backend/users/__init__.py"),
        ("users_service.py.new", "backend/users/service.py"),
        ("users_router.py.new", "backend/users/router.py"),
    ]
    
    for src, dest in files_to_copy:
        src_path = BASE_DIR / src
        dest_path = BASE_DIR / dest
        
        if src_path.exists():
            shutil.copy2(src_path, dest_path)
            print(f"   ✓ Copied {src} → {dest}")
        else:
            print(f"   ✗ Missing: {src}")

def update_app_tsx():
    """Update import in App.tsx."""
    print("\n✏️  Updating App.tsx...")
    
    app_file = BASE_DIR / "Frontend" / "src" / "App.tsx"
    
    if not app_file.exists():
        print("   ✗ App.tsx not found")
        return
    
    content = app_file.read_text(encoding='utf-8')
    
    # Update import
    old_import = "import StaffManagement from './pages/StaffManagement';"
    new_import = "import StaffManagement from './pages/admin/StaffManagement';"
    
    if old_import in content:
        content = content.replace(old_import, new_import)
        app_file.write_text(content, encoding='utf-8')
        print("   ✓ Updated StaffManagement import")
    else:
        print("   ⚠️  Import already updated or not found")

def update_staff_service():
    """Update API endpoints in staffService.ts."""
    print("\n✏️  Updating staffService.ts...")
    
    service_file = BASE_DIR / "Frontend" / "src" / "services" / "staffService.ts"
    
    if not service_file.exists():
        print("   ✗ staffService.ts not found")
        return
    
    content = service_file.read_text(encoding='utf-8')
    
    # Replace all /auth/users with /api/users
    old_prefix = "'/auth/users"
    new_prefix = "'/api/users"
    
    count = content.count(old_prefix)
    if count > 0:
        content = content.replace(old_prefix, new_prefix)
        service_file.write_text(content, encoding='utf-8')
        print(f"   ✓ Updated {count} API endpoints")
    else:
        print("   ⚠️  Endpoints already updated")

def update_test_script():
    """Update test script with new endpoints."""
    print("\n✏️  Updating test_staff_endpoints.py...")
    
    test_file = BASE_DIR / "test_staff_endpoints.py"
    
    if not test_file.exists():
        print("   ✗ test_staff_endpoints.py not found")
        return
    
    content = test_file.read_text(encoding='utf-8')
    
    # Replace endpoints
    content = content.replace('"/auth/users"', '"/api/users"')
    content = content.replace("'/auth/users'", "'/api/users'")
    content = content.replace('/auth/users/', '/api/users/')
    
    test_file.write_text(content, encoding='utf-8')
    print("   ✓ Updated test endpoints")

def show_manual_steps():
    """Show remaining manual steps."""
    print("\n" + "="*60)
    print("⚠️  MANUAL STEPS REQUIRED")
    print("="*60)
    print()
    print("1. Edit backend/auth/router.py:")
    print("   - Remove lines 348-548 (User Management section)")
    print("   - Keep only auth endpoints (login, logout, me)")
    print()
    print("2. Edit backend/main.py:")
    print("   - Add: from users import router as users_router")
    print("   - Add: app.include_router(users_router, prefix='/api')")
    print()
    print("3. Restart both servers:")
    print("   - Backend: cd backend && python main.py")
    print("   - Frontend: cd Frontend && npm run dev")
    print()
    print("4. Test the refactored module:")
    print("   - Navigate to /admin/staff")
    print("   - Run: python test_staff_endpoints.py")
    print()
    print("="*60)

def cleanup_temp_files():
    """Clean up temporary .new files."""
    print("\n🧹 Cleaning up temporary files...")
    
    temp_files = [
        "StaffTable.tsx.new",
        "UserFormModal.tsx.new",
        "StaffManagement.tsx.new",
        "users__init__.py.new",
        "users_service.py.new",
        "users_router.py.new"
    ]
    
    for f in temp_files:
        file_path = BASE_DIR / f
        if file_path.exists():
            file_path.unlink()
            print(f"   ✓ Deleted {f}")

def main():
    """Main execution."""
    print("="*60)
    print("  ARCHITECTURE REFACTORING")
    print("  Staff Management Module")
    print("="*60)
    
    print("\nThis script will:")
    print("  1. Create directory structure")
    print("  2. Move frontend files to proper locations")
    print("  3. Create backend users module")
    print("  4. Update imports and API endpoints")
    print()
    
    response = input("Continue? (y/n): ")
    if response.lower() != 'y':
        print("\nAborted.")
        return
    
    try:
        create_directories()
        move_frontend_files()
        move_backend_files()
        update_app_tsx()
        update_staff_service()
        update_test_script()
        cleanup_temp_files()
        
        print("\n" + "="*60)
        print("✅ AUTOMATED REFACTORING COMPLETE")
        print("="*60)
        
        show_manual_steps()
        
    except Exception as e:
        print(f"\n❌ Error during refactoring: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
