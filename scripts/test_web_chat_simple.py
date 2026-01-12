#!/usr/bin/env python3
"""
Simulador Simple de Chat Web - Podoskin Solution
=================================================

Versión simple con requests (síncrono) para pruebas rápidas.

Uso:
    python scripts/test_web_chat_simple.py
"""

import requests
import json
import uuid
from datetime import datetime
from time import sleep

# Configuración
BASE_URL = "http://localhost:8000"
SESSION_ID = str(uuid.uuid4())

# Datos de prueba
TEST_PATIENT = {
    "first_name": "Amelia",
    "second_name": "Sofia",
    "first_last_name": "Vargas",
    "second_last_name": "Mendoza",
    "birth_date": "1995-05-04"
}

def print_separator(char="=", length=70):
    print(char * length)

def print_header(text):
    print_separator()
    print(f">>> {text}")
    print_separator()

def health_check():
    """Verifica que el backend esté funcionando"""
    print_header("1. VERIFICANDO BACKEND")
    try:
        response = requests.get(f"{BASE_URL}/api/chatbot/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Backend conectado: {data.get('message')}")
            print(f"   Agente: {data.get('agent')}")
            print(f"   Canal: {data.get('channel')}")
            return True
        else:
            print(f"❌ Backend respondió con código: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ No se pudo conectar al backend: {e}")
        print(f"   Asegúrate de que el servidor esté corriendo en {BASE_URL}")
        return False

def send_message(message, patient_info=None):
    """Envía un mensaje al chatbot"""
    payload = {
        "message": message,
        "session_id": SESSION_ID,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "user_context": {
            "page": "/",
            "previous_messages": 0,
            "user_agent": "WebChatSimulator/1.0"
        }
    }
    
    if patient_info:
        payload["patient_info"] = patient_info
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/chatbot/message",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Error en mensaje: {response.status_code}")
            print(f"   Respuesta: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Excepción al enviar mensaje: {e}")
        return None

def lookup_patient(first_name, first_last_name, birth_date):
    """Busca un paciente existente"""
    payload = {
        "first_name": first_name,
        "first_last_name": first_last_name,
        "birth_date": birth_date
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/patient/lookup",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Error en búsqueda: {response.status_code}")
            print(f"   Respuesta: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Excepción al buscar paciente: {e}")
        return None

def register_patient(patient_data):
    """Registra un nuevo paciente"""
    try:
        response = requests.post(
            f"{BASE_URL}/api/patient/register",
            json=patient_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Error en registro: {response.status_code}")
            print(f"   Respuesta: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Excepción al registrar paciente: {e}")
        return None

def main():
    print("""
╔════════════════════════════════════════════════════════════════╗
║   SIMULADOR SIMPLE DE CHAT WEB - PODOSKIN SOLUTION            ║
║   Prueba de integración Web Chat + Agente Maya                ║
╚════════════════════════════════════════════════════════════════╝
    """)
    
    print(f"Session ID: {SESSION_ID}\n")
    
    # 1. Health Check
    if not health_check():
        return
    
    sleep(1)
    
    # 2. Mensajes sin registro
    print_header("2. CONVERSACIÓN SIN REGISTRO")
    messages = [
        "Hola, ¿cuáles son sus horarios de atención?",
        "¿Qué servicios ofrecen?"
    ]
    
    for msg in messages:
        print(f"\n👤 Usuario: {msg}")
        response = send_message(msg)
        
        if response:
            print(f"🤖 Maya: {response.get('response', 'Sin respuesta')[:200]}...")
            if response.get('suggestions'):
                print(f"   💡 Sugerencias: {', '.join(response.get('suggestions', []))}")
        
        sleep(1)
    
    # 3. Buscar paciente
    print_header("3. BÚSQUEDA DE PACIENTE")
    print(f"Buscando: {TEST_PATIENT['first_name']} {TEST_PATIENT['first_last_name']}")
    print(f"Fecha de nacimiento: {TEST_PATIENT['birth_date']}")
    
    lookup_result = lookup_patient(
        TEST_PATIENT['first_name'],
        TEST_PATIENT['first_last_name'],
        TEST_PATIENT['birth_date']
    )
    
    if lookup_result:
        print("\n📄 Resultado de búsqueda:")
        print(json.dumps(lookup_result, indent=2, ensure_ascii=False))
    else:
        print("❌ Error al buscar paciente")
        return
    
    sleep(1)
    
    # 4. Registrar si no existe
    patient_id = None
    
    if not lookup_result.get("found"):
        print_header("4. REGISTRO DE NUEVO PACIENTE")
        print("Paciente no encontrado. Procediendo con el registro...")
        
        register_result = register_patient(TEST_PATIENT)
        
        if register_result:
            print("\n🎉 PACIENTE REGISTRADO EXITOSAMENTE")
            print("📄 Respuesta del servidor:")
            print(json.dumps(register_result, indent=2, ensure_ascii=False))
            
            if register_result.get("success"):
                patient_id = register_result.get("patient_id")
                print(f"\n✅ 🆔 ID COMPLETO GENERADO: {patient_id}")
                
                # Verificar formato del ID
                parts = patient_id.split("-")
                if len(parts) == 4:
                    print(f"   📌 Últimas 2 letras apellido: {parts[0]}")
                    print(f"   📌 Últimas 2 letras nombre: {parts[1]}")
                    print(f"   📌 Fecha nacimiento (MMDD): {parts[2]}")
                    print(f"   📌 Contador: {parts[3]}")
                    print(f"\n   ✅ FORMATO CORRECTO: [AP]-[NO]-[MMDD]-[####]")
        else:
            print("❌ Error al registrar paciente")
            return
    else:
        print_header("4. PACIENTE YA EXISTE")
        patient_id = lookup_result.get("patient_id")
        print(f"✅ Paciente encontrado con ID: {patient_id}")
    
    sleep(2)
    
    # 5. Mensajes con patient_id
    print_header("5. CONVERSACIÓN CON PACIENTE REGISTRADO")
    patient_info = {
        "patient_id": patient_id,
        "first_name": TEST_PATIENT['first_name'],
        "first_last_name": TEST_PATIENT['first_last_name'],
        "is_registered": True
    }
    
    registered_messages = [
        "Quiero agendar una cita"
    ]
    
    for msg in registered_messages:
        print(f"\n👤 Usuario: {msg}")
        print(f"   (Enviando con patient_id: {patient_id})")
        
        response = send_message(msg, patient_info)
        
        if response:
            print(f"🤖 Maya: {response.get('response', 'Sin respuesta')[:200]}...")
        
        sleep(1)
    
    # 6. Resumen final
    print_header("6. RESUMEN DE LA SESIÓN")
    print(f"✅ Session ID: {SESSION_ID}")
    print(f"✅ Patient ID: {patient_id}")
    print(f"✅ Paciente: {TEST_PATIENT['first_name']} {TEST_PATIENT['first_last_name']}")
    print(f"✅ Fecha de nacimiento: {TEST_PATIENT['birth_date']}")
    print_separator()
    
    print("\n💡 Para ver la conversación en la BD, ejecuta:")
    print(f"""
psql -U postgres -d podoskin_db -c "
    SELECT * FROM web_chat_sessions WHERE session_id = '{SESSION_ID}';
"

psql -U postgres -d podoskin_db -c "
    SELECT message_type, content, timestamp 
    FROM web_chat_messages 
    WHERE session_id = '{SESSION_ID}' 
    ORDER BY timestamp;
"
    """)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Simulación interrumpida por el usuario")
    except Exception as e:
        print(f"\n\n❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()
