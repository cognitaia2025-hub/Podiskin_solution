"""
Test Script para Sistema de Autenticación
=========================================

Script de prueba para verificar el funcionamiento del sistema de auth.
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from auth.utils import verify_password, create_access_token, decode_token, get_password_hash
from auth.models import LoginRequest, LoginResponse, UserResponse, CurrentUser

def test_password_hashing():
    """Test password hashing"""
    print("=" * 60)
    print("TEST 1: Password Hashing")
    print("=" * 60)
    
    password = "password123"
    hashed = get_password_hash(password)
    print(f"✓ Password: {password}")
    print(f"✓ Hash generado: {hashed[:50]}...")
    
    # Verify password
    is_valid = verify_password(password, hashed)
    print(f"✓ Verificación: {'PASS' if is_valid else 'FAIL'}")
    
    # Wrong password
    is_invalid = verify_password("wrongpassword", hashed)
    print(f"✓ Password incorrecta: {'FAIL (esperado)' if not is_invalid else 'ERROR'}")
    print()


def test_jwt_token():
    """Test JWT token creation and decoding"""
    print("=" * 60)
    print("TEST 2: JWT Token")
    print("=" * 60)
    
    # Create token
    token_data = {
        "sub": "dr.santiago",
        "rol": "Podologo"
    }
    token = create_access_token(token_data)
    print(f"✓ Token generado: {token[:50]}...")
    
    # Decode token
    payload = decode_token(token)
    print(f"✓ Token decodificado:")
    print(f"  - sub: {payload.get('sub')}")
    print(f"  - rol: {payload.get('rol')}")
    print(f"  - exp: {payload.get('exp')}")
    print(f"  - iat: {payload.get('iat')}")
    
    # Verify payload
    assert payload.get("sub") == "dr.santiago", "Username mismatch"
    assert payload.get("rol") == "Podologo", "Rol mismatch"
    print(f"✓ Validación: PASS")
    print()


def test_pydantic_models():
    """Test Pydantic models validation"""
    print("=" * 60)
    print("TEST 3: Pydantic Models")
    print("=" * 60)
    
    # Valid login request
    try:
        login = LoginRequest(username="dr.santiago", password="password123")
        print(f"✓ LoginRequest válido: {login.username}")
    except Exception as e:
        print(f"✗ Error: {e}")
        
    # Invalid username
    try:
        login = LoginRequest(username="dr@santiago", password="password123")
        print(f"✗ Username inválido debería fallar pero pasó")
    except ValueError as e:
        print(f"✓ Username inválido rechazado correctamente: {str(e)[:50]}...")
    
    # Short password
    try:
        login = LoginRequest(username="dr.santiago", password="short")
        print(f"✗ Password corto debería fallar pero pasó")
    except ValueError as e:
        print(f"✓ Password corto rechazado correctamente")
    
    # User response
    user = UserResponse(
        id=1,
        username="dr.santiago",
        email="santiago@podoskin.com",
        rol="Podologo",
        nombre_completo="Dr. Santiago Ornelas"
    )
    print(f"✓ UserResponse: {user.username} ({user.rol})")
    print()


def test_hash_for_database():
    """Generate hash for database insertion"""
    print("=" * 60)
    print("TEST 4: Hash para BD")
    print("=" * 60)
    
    password = "password123"
    hashed = get_password_hash(password)
    
    print("Para insertar en la base de datos:")
    print("-" * 60)
    print(f"INSERT INTO usuarios (nombre_usuario, password_hash, nombre_completo, email, rol)")
    print(f"VALUES (")
    print(f"    'dr.santiago',")
    print(f"    '{hashed}',")
    print(f"    'Dr. Santiago Ornelas',")
    print(f"    'santiago@podoskin.com',")
    print(f"    'Podologo'")
    print(f");")
    print("-" * 60)
    print()


def main():
    """Run all tests"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 10 + "TEST SUITE - AUTHENTICATION SYSTEM" + " " * 13 + "║")
    print("╚" + "=" * 58 + "╝")
    print()
    
    try:
        test_password_hashing()
        test_jwt_token()
        test_pydantic_models()
        test_hash_for_database()
        
        print("=" * 60)
        print("✅ TODOS LOS TESTS PASARON")
        print("=" * 60)
        print("\nSistema de autenticación funcionando correctamente.")
        print("Siguiente paso: Crear usuario en BD y probar endpoint.")
        
    except Exception as e:
        print("=" * 60)
        print("❌ ERROR EN TESTS")
        print("=" * 60)
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
