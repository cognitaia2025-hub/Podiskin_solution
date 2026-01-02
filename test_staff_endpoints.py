"""
Test Script for Staff Management Endpoints
===========================================
Tests the new user management endpoints in /auth/users

Requirements:
- Backend running on localhost:8000
- Admin user exists and can login
- Database properly initialized

Usage:
    python test_staff_endpoints.py
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def print_section(title):
    """Print a section header."""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def print_result(success, message):
    """Print test result."""
    icon = "✅" if success else "❌"
    print(f"{icon} {message}")

def login_as_admin():
    """Login and get admin token."""
    print_section("1. LOGIN AS ADMIN")
    
    # Try admin user
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={
            "username": "admin",
            "password": "admin123"
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        token = data.get("access_token")
        user = data.get("user")
        print_result(True, f"Logged in as: {user.get('nombre_completo')} ({user.get('rol')})")
        return token
    else:
        print_result(False, f"Login failed: {response.status_code}")
        print(f"Response: {response.text}")
        return None

def test_list_users(token):
    """Test GET /auth/users."""
    print_section("2. LIST ALL USERS")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/auth/users", headers=headers)
    
    if response.status_code == 200:
        users = response.json()
        print_result(True, f"Found {len(users)} users")
        for user in users[:3]:  # Show first 3
            print(f"   - {user['nombre_completo']} ({user['rol']}) - {user['email']}")
        if len(users) > 3:
            print(f"   ... and {len(users) - 3} more")
        return True
    else:
        print_result(False, f"Failed to list users: {response.status_code}")
        print(f"Response: {response.text}")
        return False

def test_create_user(token):
    """Test POST /auth/users."""
    print_section("3. CREATE NEW USER")
    
    headers = {"Authorization": f"Bearer {token}"}
    new_user = {
        "nombre_usuario": "test.user",
        "password": "testpass123",
        "nombre_completo": "Test User",
        "email": "test@podoskin.com",
        "id_rol": 3  # Recepcionista
    }
    
    response = requests.post(
        f"{BASE_URL}/auth/users",
        headers=headers,
        json=new_user
    )
    
    if response.status_code == 201:
        user = response.json()
        print_result(True, f"User created: {user['nombre_completo']} (ID: {user['id']})")
        return user['id']
    elif response.status_code == 400:
        print_result(False, "User already exists (this is okay)")
        # Try to find existing user
        response = requests.get(f"{BASE_URL}/auth/users", headers=headers)
        if response.status_code == 200:
            users = response.json()
            for user in users:
                if user['nombre_usuario'] == 'test.user':
                    print(f"   Found existing user with ID: {user['id']}")
                    return user['id']
        return None
    else:
        print_result(False, f"Failed to create user: {response.status_code}")
        print(f"Response: {response.text}")
        return None

def test_update_user(token, user_id):
    """Test PUT /auth/users/:id."""
    print_section("4. UPDATE USER")
    
    if not user_id:
        print_result(False, "No user ID to update")
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    update_data = {
        "nombre_completo": "Test User Updated",
        "id_rol": 2  # Change to Podologo
    }
    
    response = requests.put(
        f"{BASE_URL}/auth/users/{user_id}",
        headers=headers,
        json=update_data
    )
    
    if response.status_code == 200:
        user = response.json()
        print_result(True, f"User updated: {user['nombre_completo']} - Role: {user['rol']}")
        return True
    else:
        print_result(False, f"Failed to update user: {response.status_code}")
        print(f"Response: {response.text}")
        return False

def test_get_user(token, user_id):
    """Test GET /auth/users/:id."""
    print_section("5. GET USER BY ID")
    
    if not user_id:
        print_result(False, "No user ID to fetch")
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/auth/users/{user_id}", headers=headers)
    
    if response.status_code == 200:
        user = response.json()
        print_result(True, f"User fetched: {user['nombre_completo']}")
        print(f"   Email: {user['email']}")
        print(f"   Role: {user['rol']}")
        print(f"   Active: {user['activo']}")
        return True
    else:
        print_result(False, f"Failed to get user: {response.status_code}")
        print(f"Response: {response.text}")
        return False

def test_delete_user(token, user_id):
    """Test DELETE /auth/users/:id."""
    print_section("6. DELETE (DEACTIVATE) USER")
    
    if not user_id:
        print_result(False, "No user ID to delete")
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.delete(f"{BASE_URL}/auth/users/{user_id}", headers=headers)
    
    if response.status_code == 200:
        result = response.json()
        print_result(True, f"User deactivated: {result.get('message')}")
        return True
    else:
        print_result(False, f"Failed to delete user: {response.status_code}")
        print(f"Response: {response.text}")
        return False

def test_list_roles(token):
    """Test GET /api/roles (needed for staff management)."""
    print_section("7. LIST AVAILABLE ROLES")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/roles", headers=headers)
    
    if response.status_code == 200:
        roles = response.json()
        print_result(True, f"Found {len(roles)} roles")
        for role in roles:
            print(f"   - {role['nombre_rol']} (ID: {role['id']})")
        return True
    else:
        print_result(False, f"Failed to list roles: {response.status_code}")
        print(f"Response: {response.text}")
        return False

def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("  STAFF MANAGEMENT ENDPOINT TESTS")
    print("="*60)
    print("\nMake sure the backend is running on localhost:8000")
    print("and you have an admin user (admin/admin123)\n")
    
    # Step 1: Login
    token = login_as_admin()
    if not token:
        print("\n❌ TESTS FAILED: Could not login as admin")
        print("\nTry creating an admin user first:")
        print("  python backend/create_test_user.py")
        return
    
    # Step 2: List users
    test_list_users(token)
    
    # Step 3: List roles
    test_list_roles(token)
    
    # Step 4: Create user
    user_id = test_create_user(token)
    
    # Step 5: Get user
    test_get_user(token, user_id)
    
    # Step 6: Update user
    test_update_user(token, user_id)
    
    # Step 7: Get updated user
    test_get_user(token, user_id)
    
    # Step 8: Delete user
    test_delete_user(token, user_id)
    
    # Step 9: Verify deletion
    print_section("8. VERIFY USER DEACTIVATED")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/auth/users?activo_only=false", headers=headers)
    if response.status_code == 200:
        users = response.json()
        test_user = next((u for u in users if u['id'] == user_id), None)
        if test_user and not test_user['activo']:
            print_result(True, "User is properly deactivated")
        else:
            print_result(False, "User deactivation not reflected")
    
    print("\n" + "="*60)
    print("  TESTS COMPLETE")
    print("="*60 + "\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
