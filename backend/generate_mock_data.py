"""
Script para generar datos mock - Clínica Podoskin (v3 FINAL)
============================================================

Basado en análisis COMPLETO de estructuras:

USUARIOS: nombre_usuario, password_hash, email, rol, nombre_completo, activo
  - rol: 'Admin', 'Podologo', 'Recepcionista', 'Asistente'

PODOLOGOS: cedula_profesional, nombre_completo, especialidad, telefono, email, activo, id_usuario

PACIENTES (obligatorios): primer_nombre, primer_apellido, sexo, fecha_nacimiento, telefono_principal
  - sexo: 'M', 'F', 'O'

CITAS (obligatorios): id_paciente, id_podologo, fecha_hora_inicio, fecha_hora_fin
  - tipo_cita: 'Consulta', 'Seguimiento', 'Urgencia'
  - estado: 'Pendiente', 'Confirmada', 'Completada', 'Cancelada', 'No_Asistio'
  - ⚠️ NO existe columna motivo_consulta
"""

import pg8000
from datetime import datetime, timedelta, date
from passlib.context import CryptContext
import random

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def get_connection():
    return pg8000.connect(
        host="127.0.0.1",
        port=5432,
        database="podoskin_db",
        user="podoskin_user",
        password="podoskin_password_123",
    )


# ============================================================================
# DATOS MEXICALI / CALEXICO
# ============================================================================

CALLES_MEXICALI = [
    "Av. Reforma",
    "Blvd. Benito Juárez",
    "Calle Pioneros",
    "Av. Madero",
    "Blvd. López Mateos",
    "Av. Obregón",
    "Blvd. Lázaro Cárdenas",
]
CALLES_CALEXICO = ["Main Street", "2nd Street", "Imperial Avenue", "Heffernan Avenue"]
COLONIAS_MEXICALI = ["Centro", "Nueva", "Industrial", "Pueblo Nuevo", "Pro-Hogar"]

NOMBRES_H = [
    "José Luis",
    "Carlos",
    "Miguel",
    "Francisco",
    "Juan",
    "Roberto",
    "Eduardo",
    "Alejandro",
]
NOMBRES_M = [
    "María",
    "Ana",
    "Patricia",
    "Guadalupe",
    "Leticia",
    "Carmen",
    "Adriana",
    "Laura",
]
APELLIDOS = [
    "García",
    "Rodríguez",
    "Martínez",
    "López",
    "González",
    "Hernández",
    "Pérez",
    "Sánchez",
]

# ============================================================================
# GENERADORES
# ============================================================================


def gen_paciente():
    es_mujer = random.random() < 0.5
    nombre = random.choice(NOMBRES_M if es_mujer else NOMBRES_H)
    sexo = "F" if es_mujer else "M"

    # Fecha nacimiento 18-70 años
    hoy = date.today()
    edad = random.randint(18, 70)
    fecha_nac = date(hoy.year - edad, random.randint(1, 12), random.randint(1, 28))

    # Teléfono Mexicali
    telefono = f"686{random.randint(1000000, 9999999)}"

    return {
        "primer_nombre": nombre.split()[0],
        "primer_apellido": random.choice(APELLIDOS),
        "sexo": sexo,
        "fecha_nacimiento": fecha_nac,
        "telefono_principal": telefono,
    }


# ============================================================================
# MAIN
# ============================================================================


def main():
    conn = get_connection()
    cur = conn.cursor()

    print("🚀 Generando datos mock (v3 FINAL)...")
    print("=" * 50)

    # === 1. ACTUALIZAR SANTIAGO ===
    print("\n[1/5] Actualizando Santiago...")
    cur.execute(
        "UPDATE usuarios SET nombre_completo='Santiago De Jesús Orneles Reynoso', rol='Admin' WHERE nombre_usuario='dr.santiago'"
    )
    cur.execute(
        "UPDATE podologos SET nombre_completo='Santiago De Jesús Orneles Reynoso' WHERE id=4"
    )
    print("   ✅ Santiago = Admin + Podólogo")

    # === 2. CREAR IVETTE ===
    print("\n[2/5] Creando Ivette...")
    pw_hash = pwd_context.hash("password123")

    cur.execute("SELECT id FROM usuarios WHERE nombre_usuario='ivette.martinez'")
    row = cur.fetchone()
    if row:
        ivette_uid = row[0]
        cur.execute(
            "UPDATE usuarios SET nombre_completo='Ivette Martínez García', rol='Recepcionista' WHERE id=%s",
            (ivette_uid,),
        )
    else:
        cur.execute(
            """
            INSERT INTO usuarios (nombre_usuario, password_hash, email, id_rol, nombre_completo, activo)
            VALUES ('ivette.martinez', %s, 'ivette@podoskin.com', (SELECT id FROM roles WHERE nombre_rol='Recepcionista'), 'Ivette Martínez García', true)
            RETURNING id
        """,
            (pw_hash,),
        )
        ivette_uid = cur.fetchone()[0]

    cur.execute("SELECT id FROM podologos WHERE cedula_profesional='POD-002-IMG'")
    row = cur.fetchone()
    if row:
        ivette_pid = row[0]
    else:
        cur.execute(
            """
            INSERT INTO podologos (cedula_profesional, nombre_completo, especialidad, telefono, email, activo, id_usuario)
            VALUES ('POD-002-IMG', 'Ivette Martínez García', 'Podología General', '6861234568', 'ivette@podoskin.com', true, %s)
            RETURNING id
        """,
            (ivette_uid,),
        )
        ivette_pid = cur.fetchone()[0]
    print(f"   ✅ Ivette creada (Podóloga ID: {ivette_pid})")

    # === 3. GENERAR PACIENTES ===
    print("\n[3/5] Generando 18 pacientes...")
    pac_ids = []
    for _ in range(18):
        p = gen_paciente()
        cur.execute(
            """
            INSERT INTO pacientes (primer_nombre, primer_apellido, sexo, fecha_nacimiento, telefono_principal)
            VALUES (%s, %s, %s, %s, %s) RETURNING id
        """,
            (
                p["primer_nombre"],
                p["primer_apellido"],
                p["sexo"],
                p["fecha_nacimiento"],
                p["telefono_principal"],
            ),
        )
        pac_ids.append(cur.fetchone()[0])
    print(f"   ✅ {len(pac_ids)} pacientes creados")

    # === 4. CITAS PASADAS ===
    print("\n[4/5] Generando citas pasadas...")
    citas_past = 0
    for dias in range(30, 0, -2):
        fecha = datetime.now() - timedelta(days=dias)
        if fecha.weekday() >= 5:
            continue

        # Santiago (ID=1)
        for h in [9, 10, 11, 14, 15, 16]:
            if random.random() < 0.5:
                dt = fecha.replace(hour=h, minute=0, second=0, microsecond=0)
                estado = "Completada" if random.random() < 0.85 else "No_Asistio"
                cur.execute(
                    """
                    INSERT INTO citas (id_paciente, id_podologo, fecha_hora_inicio, fecha_hora_fin, tipo_cita, estado, es_primera_vez)
                    VALUES (%s, 4, %s, %s, %s, %s, %s)
                """,
                    (
                        random.choice(pac_ids),
                        dt,
                        dt + timedelta(minutes=30),
                        "Consulta",
                        estado,
                        random.random() < 0.3,
                    ),
                )
                citas_past += 1

        # Ivette (PARALELAS)
        for h in [9, 10, 14, 15]:
            if random.random() < 0.4:
                dt = fecha.replace(hour=h, minute=0, second=0, microsecond=0)
                cur.execute(
                    """
                    INSERT INTO citas (id_paciente, id_podologo, fecha_hora_inicio, fecha_hora_fin, tipo_cita, estado, es_primera_vez)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                    (
                        random.choice(pac_ids),
                        ivette_pid,
                        dt,
                        dt + timedelta(minutes=30),
                        "Consulta",
                        "Completada",
                        False,
                    ),
                )
                citas_past += 1
    print(f"   ✅ {citas_past} citas pasadas")

    # === 5. CITAS FUTURAS ===
    print("\n[5/5] Generando citas futuras...")
    citas_fut = 0
    for dias in range(1, 15):
        fecha = datetime.now() + timedelta(days=dias)
        if fecha.weekday() >= 5:
            continue

        # Santiago
        for h in [9, 10, 11, 12, 14, 15, 16, 17]:
            if random.random() < 0.35:
                dt = fecha.replace(hour=h, minute=0, second=0, microsecond=0)
                estado = random.choice(["Confirmada", "Confirmada", "Pendiente"])
                cur.execute(
                    """
                    INSERT INTO citas (id_paciente, id_podologo, fecha_hora_inicio, fecha_hora_fin, tipo_cita, estado, es_primera_vez)
                    VALUES (%s, 4, %s, %s, %s, %s, %s)
                """,
                    (
                        random.choice(pac_ids),
                        dt,
                        dt + timedelta(minutes=30),
                        random.choice(["Consulta", "Seguimiento"]),
                        estado,
                        False,
                    ),
                )
                citas_fut += 1

        # Ivette (PARALELAS - misma hora)
        for h in [9, 10, 11, 14, 15, 16]:
            if random.random() < 0.3:
                dt = fecha.replace(hour=h, minute=0, second=0, microsecond=0)
                cur.execute(
                    """
                    INSERT INTO citas (id_paciente, id_podologo, fecha_hora_inicio, fecha_hora_fin, tipo_cita, estado, es_primera_vez)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                    (
                        random.choice(pac_ids),
                        ivette_pid,
                        dt,
                        dt + timedelta(minutes=30),
                        "Consulta",
                        "Confirmada",
                        False,
                    ),
                )
                citas_fut += 1
    print(f"   ✅ {citas_fut} citas futuras")

    # === COMMIT ===
    conn.commit()
    conn.close()

    print("\n" + "=" * 50)
    print("🎉 ¡COMPLETADO!")
    print(f"   👤 Santiago (Admin) + Ivette (Recepcionista)")
    print(f"   👥 {len(pac_ids)} pacientes")
    print(f"   📅 {citas_past} citas pasadas + {citas_fut} citas futuras")
    print("=" * 50)


if __name__ == "__main__":
    main()
