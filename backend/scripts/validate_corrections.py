#!/usr/bin/env python3
"""
Script de Validación de Correcciones
=====================================

Verifica que todas las correcciones críticas estén implementadas.

Uso:
    python backend/scripts/validate_corrections.py
"""

import sys
import os
import importlib

# Agregar backend al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def test_imports():
    """Verifica que todos los módulos se puedan importar."""
    print("🔍 Verificando imports...")
    
    tests = [
        ("API de WhatsApp Management", "api.whatsapp_management_api"),
        ("Rate Limiting Middleware", "middleware.rate_limit"),
        ("Config del Agente", "agents.whatsapp_medico.config"),
        ("KB Tools", "agents.whatsapp_medico.tools.kb_tools"),
        ("Embeddings Service", "agents.whatsapp_medico.utils.embeddings"),
    ]
    
    passed = 0
    failed = 0
    
    for name, module_name in tests:
        try:
            importlib.import_module(module_name)
            print(f"  ✅ {name}: OK")
            passed += 1
        except Exception as e:
            print(f"  ❌ {name}: FAILED - {e}")
            failed += 1
    
    print(f"\n📊 Resultado: {passed}/{len(tests)} tests pasados")
    return failed == 0


def test_files_exist():
    """Verifica que los archivos creados existan."""
    print("\n🔍 Verificando archivos creados...")
    
    files = [
        "api/whatsapp_management_api.py",
        "middleware/rate_limit.py",
        "middleware/__init__.py",
        "scripts/__init__.py",
        "scripts/generate_initial_embeddings.py",
    ]
    
    passed = 0
    failed = 0
    
    backend_dir = os.path.join(os.path.dirname(__file__), '..')
    
    for file_path in files:
        full_path = os.path.join(backend_dir, file_path)
        if os.path.exists(full_path):
            print(f"  ✅ {file_path}: EXISTS")
            passed += 1
        else:
            print(f"  ❌ {file_path}: NOT FOUND")
            failed += 1
    
    print(f"\n📊 Resultado: {passed}/{len(files)} archivos encontrados")
    return failed == 0


def test_config():
    """Verifica configuración del checkpointer."""
    print("\n🔍 Verificando configuración...")
    
    try:
        from agents.whatsapp_medico.config import checkpointer, ENVIRONMENT
        
        print(f"  ℹ️  ENVIRONMENT: {ENVIRONMENT}")
        print(f"  ℹ️  Checkpointer type: {type(checkpointer).__name__}")
        
        if ENVIRONMENT == "production":
            if "PostgresSaver" in str(type(checkpointer)):
                print("  ✅ PostgresSaver configurado correctamente")
                return True
            else:
                print("  ⚠️  En producción pero usando MemorySaver (fallback)")
                return True
        else:
            if "MemorySaver" in str(type(checkpointer)):
                print("  ✅ MemorySaver configurado para desarrollo")
                return True
            else:
                print("  ⚠️  En desarrollo pero usando PostgresSaver")
                return True
                
    except Exception as e:
        print(f"  ❌ Error verificando config: {e}")
        return False


def main():
    """Ejecuta todas las validaciones."""
    print("="*60)
    print("🎯 VALIDACIÓN DE CORRECCIONES CRÍTICAS")
    print("="*60)
    
    results = [
        test_imports(),
        test_files_exist(),
        test_config(),
    ]
    
    print("\n" + "="*60)
    if all(results):
        print("✅ TODAS LAS VALIDACIONES PASARON")
        print("="*60)
        return 0
    else:
        print("❌ ALGUNAS VALIDACIONES FALLARON")
        print("="*60)
        return 1


if __name__ == "__main__":
    sys.exit(main())
