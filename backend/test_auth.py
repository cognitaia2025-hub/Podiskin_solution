"""
Test de Autenticación - Podoskin Solution
==========================================

Script de prueba para verificar el sistema de autenticación.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from auth import (
    verify_password,
    get_password_hash,
    create_access_token,
    decode_access_token,
    verify_token,
)


def test_password_hashing():
    """Test de hashing de contraseñas."""
    print("\n🧪 Test 1: Password Hashing")
    print("-" * 50)
    
    password = "password123"
    
    # Generar hash
    hashed = get_password_hash(password)
    print(f"✅ Password hash generado: {hashed[:50]}...")
    
    # Verificar contraseña correcta
    is_valid = verify_password(password, hashed)
    assert is_valid, "La verificación de contraseña correcta falló"
    print("✅ Verificación de contraseña correcta: OK")
    
    # Verificar contraseña incorrecta
    is_invalid = verify_password("wrong_password", hashed)
    assert not is_invalid, "La verificación de contraseña incorrecta falló"
    print("✅ Verificación de contraseña incorrecta: OK")
    
    print("✅ Test de password hashing: PASSED")


def test_jwt_token_creation():
    """Test de creación de JWT tokens."""
    print("\n🧪 Test 2: JWT Token Creation")
    print("-" * 50)
    
    token_data = {
        "sub": "dr.santiago",
        "rol": "Podologo"
    }
    
    # Crear token
    token = create_access_token(token_data)
    print(f"✅ Token JWT creado: {token[:50]}...")
    
    # Decodificar token
    payload = decode_access_token(token)
    assert payload is not None, "No se pudo decodificar el token"
    print(f"✅ Token decodificado exitosamente")
    
    # Verificar contenido
    assert payload["sub"] == "dr.santiago", "Username incorrecto en token"
    assert payload["rol"] == "Podologo", "Rol incorrecto en token"
    assert "exp" in payload, "Token sin expiración"
    assert "iat" in payload, "Token sin timestamp de emisión"
    print(f"✅ Payload del token:")
    print(f"   - Username: {payload['sub']}")
    print(f"   - Rol: {payload['rol']}")
    print(f"   - Expira en: {payload['exp']}")
    print(f"   - Emitido en: {payload['iat']}")
    
    print("✅ Test de JWT token creation: PASSED")


def test_jwt_token_verification():
    """Test de verificación de JWT tokens."""
    print("\n🧪 Test 3: JWT Token Verification")
    print("-" * 50)
    
    # Crear token válido
    token_data = {
        "sub": "dr.santiago",
        "rol": "Podologo"
    }
    token = create_access_token(token_data)
    
    # Verificar token válido
    is_valid, payload = verify_token(token)
    assert is_valid, "Token válido marcado como inválido"
    assert payload is not None, "Payload es None para token válido"
    print("✅ Verificación de token válido: OK")
    
    # Verificar token inválido
    invalid_token = "invalid.token.here"
    is_invalid, payload_invalid = verify_token(invalid_token)
    assert not is_invalid, "Token inválido marcado como válido"
    assert payload_invalid is None, "Payload no es None para token inválido"
    print("✅ Verificación de token inválido: OK")
    
    print("✅ Test de JWT token verification: PASSED")


def test_models_validation():
    """Test de validación de modelos Pydantic."""
    print("\n🧪 Test 4: Pydantic Models Validation")
    print("-" * 50)
    
    from auth.models import LoginRequest, UserResponse, LoginResponse
    
    # Test LoginRequest válido
    try:
        login_req = LoginRequest(
            username="dr.santiago",
            password="password123"
        )
        print("✅ LoginRequest válido: OK")
    except Exception as e:
        print(f"❌ Error en LoginRequest válido: {e}")
        raise
    
    # Test LoginRequest con username inválido
    try:
        invalid_login = LoginRequest(
            username="dr.santiago@invalid",  # @ no permitido
            password="password123"
        )
        print("❌ LoginRequest inválido no fue rechazado")
        assert False, "Validación de username falló"
    except Exception:
        print("✅ LoginRequest con username inválido rechazado: OK")
    
    # Test UserResponse
    try:
        user_resp = UserResponse(
            id=1,
            username="dr.santiago",
            email="santiago@podoskin.com",
            rol="Podologo",
            nombre_completo="Dr. Santiago Ornelas"
        )
        print("✅ UserResponse válido: OK")
    except Exception as e:
        print(f"❌ Error en UserResponse: {e}")
        raise
    
    # Test LoginResponse
    try:
        login_resp = LoginResponse(
            access_token="fake.token.here",
            token_type="bearer",
            expires_in=3600,
            user=user_resp
        )
        print("✅ LoginResponse válido: OK")
    except Exception as e:
        print(f"❌ Error en LoginResponse: {e}")
        raise
    
    print("✅ Test de Pydantic models validation: PASSED")


def run_all_tests():
    """Ejecuta todos los tests."""
    print("\n" + "="*50)
    print("🧪 TESTS DE AUTENTICACIÓN - PODOSKIN SOLUTION")
    print("="*50)
    
    try:
        test_password_hashing()
        test_jwt_token_creation()
        test_jwt_token_verification()
        test_models_validation()
        
        print("\n" + "="*50)
        print("✅ TODOS LOS TESTS PASARON EXITOSAMENTE")
        print("="*50)
        print("\n✨ El sistema de autenticación está funcionando correctamente")
        return 0
        
    except Exception as e:
        print("\n" + "="*50)
        print("❌ TESTS FALLARON")
        print("="*50)
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
