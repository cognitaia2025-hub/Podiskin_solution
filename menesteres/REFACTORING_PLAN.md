# REFACTORING ARCHITECTURE - EXECUTION PLAN

## CRITICAL: PowerShell is not available in this environment

You need to manually create the directory structure first, then I'll provide all the refactored code.

## Step 1: Create Directory Structure

Execute these commands in your terminal (PowerShell or CMD):

```powershell
# Frontend directories
cd C:\Users\Salva\OneDrive\Escritorio\PodoskiSolution

mkdir Frontend\src\pages\admin
mkdir Frontend\src\components\admin

# Backend directory
mkdir backend\users
```

## Step 2: Move and Refactor Files

After creating directories, I'll provide:

### Frontend Refactoring:
1. **StaffTable.tsx** - Extracted table component (~180 lines)
2. **UserFormModal.tsx** - Extracted modal component (~200 lines)
3. **StaffManagement.tsx** - Refactored orchestrator (~150 lines)
4. Move to `pages/admin/StaffManagement.tsx`

### Backend Refactoring:
1. **users/__init__.py** - Module initialization
2. **users/router.py** - User management endpoints
3. **users/service.py** - User business logic
4. Clean `auth/router.py` - Remove user management
5. Update `main.py` - Register new router

## Step 3: Update References

1. Update `App.tsx` import
2. Update `staffService.ts` API endpoints
3. Update test script

---

## EXECUTE THIS FIRST:

Run in terminal:
```cmd
python create_directories.py
```

Then respond "directories created" and I'll provide all the refactored code.

---

## Current Status:
- ❌ Directories not created (PowerShell unavailable)
- ✅ Refactoring plan ready
- ✅ Code ready to generate

**Action Required:** Create directories manually, then I'll continue.
