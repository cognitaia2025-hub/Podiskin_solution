#!/usr/bin/env python3
"""
Simulador de Chat Web - Podoskin Solution
==========================================

Simula el flujo completo de un usuario en el chat web:
1. Enviar mensajes sin registro
2. Buscar si existe como paciente
3. Registrarse como nuevo paciente
4. Enviar mensajes con ID de paciente

Uso:
    python scripts/test_web_chat.py
"""

import asyncio
import aiohttp
import json
import uuid
from datetime import datetime
from typing import Optional, Dict, Any
from colorama import init, Fore, Back, Style

# Inicializar colorama para colores en terminal
init(autoreset=True)

# Configuración
BASE_URL = "http://localhost:8000"
SESSION_ID = str(uuid.uuid4())

# Colores
USER_COLOR = Fore.CYAN
BOT_COLOR = Fore.GREEN
INFO_COLOR = Fore.YELLOW
SUCCESS_COLOR = Fore.GREEN + Style.BRIGHT
ERROR_COLOR = Fore.RED + Style.BRIGHT

# Datos de prueba
TEST_PATIENT = {
    "first_name": "Amelia",
    "second_name": "Sofia",
    "first_last_name": "Vargas",
    "second_last_name": "Mendoza",
    "birth_date": "1995-05-04"
}

class WebChatSimulator:
    def __init__(self, base_url: str, session_id: str):
        self.base_url = base_url
        self.session_id = session_id
        self.patient_id: Optional[str] = None
        self.patient_info: Optional[Dict[str, Any]] = None
        
    def print_separator(self, char="=", length=70):
        """Imprime un separador visual"""
        print(char * length)
    
    def print_header(self, text: str):
        """Imprime un encabezado destacado"""
        self.print_separator()
        print(f"{INFO_COLOR}{text}")
        self.print_separator()
    
    def print_user_message(self, message: str):
        """Imprime mensaje del usuario"""
        print(f"\n{USER_COLOR}👤 Usuario: {message}")
    
    def print_bot_message(self, message: str):
        """Imprime mensaje del bot"""
        print(f"{BOT_COLOR}🤖 Maya: {message}\n")
    
    def print_info(self, message: str):
        """Imprime información del sistema"""
        print(f"{INFO_COLOR}ℹ️  {message}")
    
    def print_success(self, message: str):
        """Imprime mensaje de éxito"""
        print(f"{SUCCESS_COLOR}✅ {message}")
    
    def print_error(self, message: str):
        """Imprime mensaje de error"""
        print(f"{ERROR_COLOR}❌ {message}")
    
    async def health_check(self) -> bool:
        """Verifica que el backend esté funcionando"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/api/chatbot/health") as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        self.print_success(f"Backend conectado: {data.get('message')}")
                        self.print_info(f"Agente: {data.get('agent')}")
                        self.print_info(f"Canal: {data.get('channel')}")
                        return True
                    else:
                        self.print_error(f"Backend respondió con código: {resp.status}")
                        return False
        except Exception as e:
            self.print_error(f"No se pudo conectar al backend: {e}")
            return False
    
    async def send_message(self, message: str, include_patient_info: bool = False) -> Dict[str, Any]:
        """Envía un mensaje al chatbot"""
        payload = {
            "message": message,
            "session_id": self.session_id,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "user_context": {
                "page": "/",
                "previous_messages": 0,
                "user_agent": "WebChatSimulator/1.0"
            }
        }
        
        if include_patient_info and self.patient_info:
            payload["patient_info"] = self.patient_info
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/chatbot/message",
                    json=payload,
                    headers={"Content-Type": "application/json"}
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return data
                    else:
                        text = await resp.text()
                        self.print_error(f"Error en mensaje: {resp.status} - {text}")
                        return {"error": True, "status": resp.status}
        except Exception as e:
            self.print_error(f"Excepción al enviar mensaje: {e}")
            return {"error": True, "message": str(e)}
    
    async def lookup_patient(self, first_name: str, first_last_name: str, birth_date: str) -> Dict[str, Any]:
        """Busca un paciente existente"""
        payload = {
            "first_name": first_name,
            "first_last_name": first_last_name,
            "birth_date": birth_date
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/patient/lookup",
                    json=payload,
                    headers={"Content-Type": "application/json"}
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return data
                    else:
                        text = await resp.text()
                        self.print_error(f"Error en búsqueda: {resp.status} - {text}")
                        return {"error": True, "status": resp.status}
        except Exception as e:
            self.print_error(f"Excepción al buscar paciente: {e}")
            return {"error": True, "message": str(e)}
    
    async def register_patient(self, patient_data: Dict[str, str]) -> Dict[str, Any]:
        """Registra un nuevo paciente"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/patient/register",
                    json=patient_data,
                    headers={"Content-Type": "application/json"}
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return data
                    else:
                        text = await resp.text()
                        self.print_error(f"Error en registro: {resp.status} - {text}")
                        return {"error": True, "status": resp.status}
        except Exception as e:
            self.print_error(f"Excepción al registrar paciente: {e}")
            return {"error": True, "message": str(e)}
    
    async def simulate_conversation(self):
        """Simula una conversación completa"""
        
        self.print_header("🚀 SIMULADOR DE CHAT WEB - PODOSKIN SOLUTION")
        print(f"{INFO_COLOR}Session ID: {self.session_id}\n")
        
        # 1. Health Check
        self.print_header("1️⃣  VERIFICANDO BACKEND")
        if not await self.health_check():
            self.print_error("Backend no disponible. Asegúrate de que esté corriendo en http://localhost:8000")
            return
        
        await asyncio.sleep(1)
        
        # 2. Primer mensaje sin registro
        self.print_header("2️⃣  CONVERSACIÓN SIN REGISTRO")
        messages = [
            "Hola, ¿cuáles son sus horarios de atención?",
            "¿Qué servicios ofrecen?",
            "¿Cuánto cuesta una consulta?"
        ]
        
        for msg in messages:
            self.print_user_message(msg)
            response = await self.send_message(msg)
            
            if response.get("error"):
                continue
            
            self.print_bot_message(response.get("response", "Sin respuesta"))
            
            if response.get("suggestions"):
                self.print_info(f"Sugerencias: {', '.join(response.get('suggestions', []))}")
            
            await asyncio.sleep(1.5)
        
        # 3. Buscar si el paciente existe
        self.print_header("3️⃣  BÚSQUEDA DE PACIENTE")
        self.print_info(f"Buscando: {TEST_PATIENT['first_name']} {TEST_PATIENT['first_last_name']}")
        self.print_info(f"Fecha de nacimiento: {TEST_PATIENT['birth_date']}")
        
        lookup_result = await self.lookup_patient(
            TEST_PATIENT['first_name'],
            TEST_PATIENT['first_last_name'],
            TEST_PATIENT['birth_date']
        )
        
        if lookup_result.get("error"):
            self.print_error("Error al buscar paciente")
            return
        
        print(f"\n{INFO_COLOR}📄 Respuesta del servidor:")
        print(json.dumps(lookup_result, indent=2, ensure_ascii=False))
        
        await asyncio.sleep(1)
        
        # 4. Registrar si no existe
        if not lookup_result.get("found"):
            self.print_header("4️⃣  REGISTRO DE NUEVO PACIENTE")
            self.print_info("Paciente no encontrado. Procediendo con el registro...")
            
            register_result = await self.register_patient(TEST_PATIENT)
            
            if register_result.get("error"):
                self.print_error("Error al registrar paciente")
                return
            
            print(f"\n{SUCCESS_COLOR}🎉 PACIENTE REGISTRADO EXITOSAMENTE")
            print(f"{INFO_COLOR}📄 Respuesta del servidor:")
            print(json.dumps(register_result, indent=2, ensure_ascii=False))
            
            if register_result.get("success"):
                self.patient_id = register_result.get("patient_id")
                self.print_success(f"\n🆔 ID COMPLETO GENERADO: {self.patient_id}")
                
                # Verificar formato del ID
                parts = self.patient_id.split("-")
                if len(parts) == 4:
                    self.print_info(f"   Últimas 2 letras apellido: {parts[0]}")
                    self.print_info(f"   Últimas 2 letras nombre: {parts[1]}")
                    self.print_info(f"   Fecha nacimiento (MMDD): {parts[2]}")
                    self.print_info(f"   Contador: {parts[3]}")
        else:
            self.print_header("4️⃣  PACIENTE YA EXISTE")
            self.patient_id = lookup_result.get("patient_id")
            self.print_success(f"Paciente encontrado con ID: {self.patient_id}")
        
        # Actualizar patient_info
        self.patient_info = {
            "patient_id": self.patient_id,
            "first_name": TEST_PATIENT['first_name'],
            "first_last_name": TEST_PATIENT['first_last_name'],
            "is_registered": True
        }
        
        await asyncio.sleep(2)
        
        # 5. Mensajes con patient_id
        self.print_header("5️⃣  CONVERSACIÓN CON PACIENTE REGISTRADO")
        registered_messages = [
            "Quiero agendar una cita",
            "¿Cuál es su dirección?",
            "Gracias por la información"
        ]
        
        for msg in registered_messages:
            self.print_user_message(msg)
            self.print_info(f"(Enviando con patient_id: {self.patient_id})")
            
            response = await self.send_message(msg, include_patient_info=True)
            
            if response.get("error"):
                continue
            
            self.print_bot_message(response.get("response", "Sin respuesta"))
            
            await asyncio.sleep(1.5)
        
        # 6. Resumen final
        self.print_header("6️⃣  RESUMEN DE LA SESIÓN")
        self.print_success(f"Session ID: {self.session_id}")
        self.print_success(f"Patient ID: {self.patient_id}")
        self.print_success(f"Paciente: {TEST_PATIENT['first_name']} {TEST_PATIENT['first_last_name']}")
        self.print_success(f"Fecha de nacimiento: {TEST_PATIENT['birth_date']}")
        self.print_separator()
        
        # Verificar conversación en la base de datos
        self.print_info("\n💡 Para ver la conversación en la BD, ejecuta:")
        print(f"""
{Fore.CYAN}psql -U postgres -d podoskin_db -c "
    SELECT * FROM web_chat_sessions WHERE session_id = '{self.session_id}';
"

psql -U postgres -d podoskin_db -c "
    SELECT * FROM web_chat_messages 
    WHERE session_id = '{self.session_id}' 
    ORDER BY timestamp;
"
{Style.RESET_ALL}""")

async def main():
    """Función principal"""
    simulator = WebChatSimulator(BASE_URL, SESSION_ID)
    
    try:
        await simulator.simulate_conversation()
    except KeyboardInterrupt:
        print(f"\n\n{ERROR_COLOR}❌ Simulación interrumpida por el usuario")
    except Exception as e:
        print(f"\n\n{ERROR_COLOR}❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print(f"""
{Fore.YELLOW}╔════════════════════════════════════════════════════════════════╗
║   SIMULADOR DE CHAT WEB - PODOSKIN SOLUTION                  ║
║   Prueba de integración Web Chat + Agente Maya               ║
╚════════════════════════════════════════════════════════════════╝{Style.RESET_ALL}
    """)
    
    asyncio.run(main())
