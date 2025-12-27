"""
Mock Data - Datos de Prueba para Modo Demo
==========================================

Datos de prueba en memoria para simular BD sin conexión real.
"""

from datetime import datetime, date, timedelta

# Pacientes de prueba
MOCK_PATIENTS = [
    {
        "id": 1,
        "nombre": "María Fernández",
        "telefono": "686-123-4567",
        "email": "maria.f@email.com",
        "fecha_nacimiento": "1985-03-15",
        "direccion": "Calle Principal 123",
        "notas": "Paciente regular",
        "fecha_registro": "2023-01-10",
    },
    {
        "id": 2,
        "nombre": "Juan Ramírez",
        "telefono": "686-234-5678",
        "email": "juan.r@email.com",
        "fecha_nacimiento": "1978-07-22",
        "direccion": "Av. Reforma 456",
        "notas": "",
        "fecha_registro": "2023-02-15",
    },
    {
        "id": 3,
        "nombre": "Sofía Gómez",
        "telefono": "686-345-6789",
        "email": "sofia.g@email.com",
        "fecha_nacimiento": "1992-11-08",
        "direccion": "Blvd. Juárez 789",
        "notas": "Alérgica a ciertos medicamentos",
        "fecha_registro": "2023-03-20",
    },
    {
        "id": 4,
        "nombre": "Pedro Díaz",
        "telefono": "686-456-7890",
        "email": "pedro.d@email.com",
        "fecha_nacimiento": "1965-05-30",
        "direccion": "Calle Morelos 321",
        "notas": "",
        "fecha_registro": "2023-04-05",
    },
    {
        "id": 5,
        "nombre": "Ana López",
        "telefono": "686-567-8901",
        "email": "ana.l@email.com",
        "fecha_nacimiento": "1988-09-12",
        "direccion": "Av. Hidalgo 654",
        "notas": "Paciente nueva",
        "fecha_registro": "2024-11-01",
    },
]

# Citas de prueba
tomorrow = (date.today() + timedelta(days=1)).isoformat()
today = date.today().isoformat()
yesterday = (date.today() - timedelta(days=1)).isoformat()

MOCK_APPOINTMENTS = [
    # Citas de mañana
    {
        "id": 1,
        "paciente_id": 1,
        "paciente_nombre": "María Fernández",
        "paciente_telefono": "686-123-4567",
        "fecha": tomorrow,
        "hora": "09:00:00",
        "duracion": 45,
        "tratamiento": "Tratamiento de callos",
        "estado": "pendiente",
        "notas": "",
    },
    {
        "id": 2,
        "paciente_id": 2,
        "paciente_nombre": "Juan Ramírez",
        "paciente_telefono": "686-234-5678",
        "fecha": tomorrow,
        "hora": "10:30:00",
        "duracion": 30,
        "tratamiento": "Pedicure",
        "estado": "pendiente",
        "notas": "",
    },
    {
        "id": 3,
        "paciente_id": 3,
        "paciente_nombre": "Sofía Gómez",
        "paciente_telefono": "686-345-6789",
        "fecha": tomorrow,
        "hora": "11:45:00",
        "duracion": 45,
        "tratamiento": "Uñas encarnadas",
        "estado": "pendiente",
        "notas": "",
    },
    # Citas de hoy
    {
        "id": 4,
        "paciente_id": 4,
        "paciente_nombre": "Pedro Díaz",
        "paciente_telefono": "686-456-7890",
        "fecha": today,
        "hora": "14:00:00",
        "duracion": 45,
        "tratamiento": "Onicomicosis",
        "estado": "pendiente",
        "notas": "",
    },
    {
        "id": 5,
        "paciente_id": 5,
        "paciente_nombre": "Ana López",
        "paciente_telefono": "686-567-8901",
        "fecha": today,
        "hora": "15:30:00",
        "duracion": 30,
        "tratamiento": "Tratamiento de verrugas",
        "estado": "pendiente",
        "notas": "",
    },
    # Citas pasadas
    {
        "id": 6,
        "paciente_id": 1,
        "paciente_nombre": "María Fernández",
        "paciente_telefono": "686-123-4567",
        "fecha": yesterday,
        "hora": "10:00:00",
        "duracion": 30,
        "tratamiento": "Pedicure",
        "estado": "completada",
        "notas": "",
    },
]

# Estadísticas mock
MOCK_STATS = {
    "total_patients": len(MOCK_PATIENTS),
    "new_patients_last_month": 1,
    "total_appointments_this_week": 6,
    "completed_appointments": 4,
    "cancelled_appointments": 1,
    "pending_appointments": 5,
}
