"""
Service Layer - Módulo de Tratamientos
========================================

Contiene la lógica de negocio y funciones de acceso a datos.
Separado del router para mejor arquitectura y mantenibilidad.
"""

import logging
from typing import List, Optional, Dict, Any, Tuple
from decimal import Decimal

from .database import execute_query, execute_mutation

logger = logging.getLogger(__name__)


# ============================================================================
# CÁLCULO DE IMC
# ============================================================================


def calcular_imc(peso_kg: Decimal, talla_cm: Decimal) -> Decimal:
    """
    Calcula el IMC (Índice de Masa Corporal).
    
    Fórmula: IMC = peso (kg) / (talla (m))²
    
    Args:
        peso_kg: Peso en kilogramos
        talla_cm: Talla en centímetros
        
    Returns:
        IMC calculado, redondeado a 2 decimales
    """
    # Convertir talla a metros
    talla_m = talla_cm / 100
    
    # Calcular IMC: peso / (talla^2)
    imc = peso_kg / (talla_m ** 2)
    
    # Redondear a 2 decimales
    return round(imc, 2)


def clasificar_imc(imc: Decimal) -> str:
    """
    Clasifica el IMC según estándares médicos.
    
    Clasificación:
    - < 18.5: Bajo peso
    - 18.5-24.9: Normal
    - 25-29.9: Sobrepeso
    - >= 30: Obesidad
    
    Args:
        imc: Índice de Masa Corporal
        
    Returns:
        Clasificación del IMC
    """
    if imc < 18.5:
        return "Bajo peso"
    elif imc < 25:
        return "Normal"
    elif imc < 30:
        return "Sobrepeso"
    else:
        return "Obesidad"


# ============================================================================
# TRATAMIENTOS - LÓGICA DE NEGOCIO
# ============================================================================


async def get_tratamientos(activo: Optional[bool] = None) -> List[Dict[str, Any]]:
    """
    Obtiene lista de tratamientos.
    
    Args:
        activo: Filtro por estado activo (None = todos)
        
    Returns:
        Lista de tratamientos
    """
    if activo is not None:
        query = """
            SELECT id, codigo_servicio, nombre_servicio, descripcion,
                   precio_base, duracion_minutos, requiere_consentimiento,
                   activo, fecha_registro
            FROM tratamientos
            WHERE activo = %s
            ORDER BY nombre_servicio
        """
        params = (activo,)
    else:
        query = """
            SELECT id, codigo_servicio, nombre_servicio, descripcion,
                   precio_base, duracion_minutos, requiere_consentimiento,
                   activo, fecha_registro
            FROM tratamientos
            ORDER BY nombre_servicio
        """
        params = ()
    
    tratamientos = await execute_query(query, params)
    return tratamientos or []


async def create_tratamiento(
    codigo_servicio: str,
    nombre_servicio: str,
    descripcion: Optional[str],
    precio_base: Decimal,
    duracion_minutos: int,
    requiere_consentimiento: bool,
    activo: bool
) -> Dict[str, Any]:
    """
    Crea un nuevo tratamiento.
    
    Args:
        codigo_servicio: Código único del servicio
        nombre_servicio: Nombre del tratamiento
        descripcion: Descripción opcional
        precio_base: Precio base del tratamiento
        duracion_minutos: Duración estimada en minutos
        requiere_consentimiento: Si requiere consentimiento informado
        activo: Si está activo
        
    Returns:
        Tratamiento creado
        
    Raises:
        Exception: Si hay error en la creación
    """
    query = """
        INSERT INTO tratamientos (
            codigo_servicio, nombre_servicio, descripcion,
            precio_base, duracion_minutos, requiere_consentimiento, activo
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        RETURNING id, codigo_servicio, nombre_servicio, descripcion,
                  precio_base, duracion_minutos, requiere_consentimiento,
                  activo, fecha_registro
    """
    params = (
        codigo_servicio,
        nombre_servicio,
        descripcion,
        precio_base,
        duracion_minutos,
        requiere_consentimiento,
        activo,
    )
    
    result = await execute_mutation(query, params, returning=True)
    
    if not result:
        raise Exception("Error al crear tratamiento en la base de datos")
    
    return result


async def get_tratamiento(tratamiento_id: int) -> Optional[Dict[str, Any]]:
    """
    Obtiene un tratamiento por ID.
    
    Args:
        tratamiento_id: ID del tratamiento
        
    Returns:
        Tratamiento o None si no existe
    """
    query = """
        SELECT id, codigo_servicio, nombre_servicio, descripcion,
               precio_base, duracion_minutos, requiere_consentimiento,
               activo, fecha_registro
        FROM tratamientos
        WHERE id = %s
    """
    
    return await execute_query(query, (tratamiento_id,), fetch_one=True)


async def update_tratamiento(
    tratamiento_id: int,
    updates: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    """
    Actualiza un tratamiento existente.
    
    Args:
        tratamiento_id: ID del tratamiento
        updates: Diccionario con campos a actualizar
        
    Returns:
        Tratamiento actualizado o None si no existe
        
    Raises:
        ValueError: Si no hay campos para actualizar
    """
    # Verificar que el tratamiento existe
    existing = await execute_query(
        "SELECT id FROM tratamientos WHERE id = %s",
        (tratamiento_id,),
        fetch_one=True
    )
    
    if not existing:
        return None
    
    # Construir query dinámicamente solo con campos proporcionados
    update_fields = []
    params = []
    
    if "codigo_servicio" in updates and updates["codigo_servicio"] is not None:
        update_fields.append("codigo_servicio = %s")
        params.append(updates["codigo_servicio"])
    
    if "nombre_servicio" in updates and updates["nombre_servicio"] is not None:
        update_fields.append("nombre_servicio = %s")
        params.append(updates["nombre_servicio"])
    
    if "descripcion" in updates and updates["descripcion"] is not None:
        update_fields.append("descripcion = %s")
        params.append(updates["descripcion"])
    
    if "precio_base" in updates and updates["precio_base"] is not None:
        update_fields.append("precio_base = %s")
        params.append(updates["precio_base"])
    
    if "duracion_minutos" in updates and updates["duracion_minutos"] is not None:
        update_fields.append("duracion_minutos = %s")
        params.append(updates["duracion_minutos"])
    
    if "requiere_consentimiento" in updates and updates["requiere_consentimiento"] is not None:
        update_fields.append("requiere_consentimiento = %s")
        params.append(updates["requiere_consentimiento"])
    
    if "activo" in updates and updates["activo"] is not None:
        update_fields.append("activo = %s")
        params.append(updates["activo"])
    
    if not update_fields:
        raise ValueError("No se proporcionaron campos para actualizar")
    
    params.append(tratamiento_id)
    
    query = f"""
        UPDATE tratamientos
        SET {', '.join(update_fields)}
        WHERE id = %s
        RETURNING id, codigo_servicio, nombre_servicio, descripcion,
                  precio_base, duracion_minutos, requiere_consentimiento,
                  activo, fecha_registro
    """
    
    result = await execute_mutation(query, tuple(params), returning=True)
    
    if not result:
        raise Exception("Error al actualizar tratamiento en la base de datos")
    
    return result


async def delete_tratamiento(tratamiento_id: int) -> bool:
    """
    Desactiva un tratamiento (soft delete).
    
    Args:
        tratamiento_id: ID del tratamiento
        
    Returns:
        True si se eliminó, False si no existe
    """
    # Verificar que el tratamiento existe
    existing = await execute_query(
        "SELECT id FROM tratamientos WHERE id = %s",
        (tratamiento_id,),
        fetch_one=True
    )
    
    if not existing:
        return False
    
    # Soft delete: marcar como inactivo
    query = "UPDATE tratamientos SET activo = false WHERE id = %s"
    await execute_mutation(query, (tratamiento_id,), returning=False)
    
    return True


# ============================================================================
# SIGNOS VITALES
# ============================================================================


async def create_signos_vitales(
    cita_id: int,
    peso_kg: Optional[Decimal],
    talla_cm: Optional[Decimal],
    imc: Optional[Decimal],
    presion_sistolica: Optional[int],
    presion_diastolica: Optional[int],
    frecuencia_cardiaca: Optional[int],
    frecuencia_respiratoria: Optional[int],
    temperatura_celsius: Optional[Decimal],
    saturacion_oxigeno: Optional[int],
    glucosa_capilar: Optional[int]
) -> Dict[str, Any]:
    """
    Crea signos vitales para una cita.
    
    Args:
        cita_id: ID de la cita
        peso_kg: Peso en kilogramos
        talla_cm: Talla en centímetros
        imc: IMC calculado
        presion_sistolica: Presión arterial sistólica
        presion_diastolica: Presión arterial diastólica
        frecuencia_cardiaca: Frecuencia cardíaca
        frecuencia_respiratoria: Frecuencia respiratoria
        temperatura_celsius: Temperatura en Celsius
        saturacion_oxigeno: Saturación de oxígeno
        glucosa_capilar: Glucosa capilar
        
    Returns:
        Signos vitales creados
        
    Raises:
        Exception: Si la cita no existe o hay error en la creación
    """
    # Verificar que la cita existe
    cita = await execute_query(
        "SELECT id FROM citas WHERE id = %s",
        (cita_id,),
        fetch_one=True
    )
    
    if not cita:
        raise ValueError(f"Cita no encontrada: {cita_id}")
    
    # Insertar signos vitales
    query = """
        INSERT INTO signos_vitales (
            id_cita, peso_kg, talla_cm, imc,
            ta_sistolica, ta_diastolica,
            frecuencia_cardiaca, frecuencia_respiratoria,
            temperatura_c, saturacion_o2, glucosa_capilar,
            fecha_registro
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
        RETURNING id, id_cita, peso_kg, talla_cm, imc,
                  ta_sistolica, ta_diastolica,
                  frecuencia_cardiaca, frecuencia_respiratoria,
                  temperatura_c, saturacion_o2, glucosa_capilar,
                  fecha_registro
    """
    
    params = (
        cita_id,
        peso_kg,
        talla_cm,
        imc,
        presion_sistolica,
        presion_diastolica,
        frecuencia_cardiaca,
        frecuencia_respiratoria,
        temperatura_celsius,
        saturacion_oxigeno,
        glucosa_capilar,
    )
    
    result = await execute_mutation(query, params, returning=True)
    
    if not result:
        raise Exception("Error al crear signos vitales en la base de datos")
    
    return result


# ============================================================================
# DIAGNÓSTICOS
# ============================================================================


async def get_cita_con_podologo(cita_id: int) -> Optional[Dict[str, Any]]:
    """
    Obtiene información de una cita incluyendo datos del podólogo.
    
    Args:
        cita_id: ID de la cita
        
    Returns:
        Información de la cita y podólogo o None si no existe
    """
    query = """
        SELECT c.id, c.id_podologo, u.username as podologo_nombre
        FROM citas c
        JOIN podologos p ON c.id_podologo = p.id
        JOIN usuarios u ON p.id_usuario = u.id
        WHERE c.id = %s
    """
    
    return await execute_query(query, (cita_id,), fetch_one=True)


async def get_cie10_descripcion(codigo_cie10: str) -> Optional[str]:
    """
    Obtiene la descripción de un código CIE-10.
    
    Args:
        codigo_cie10: Código CIE-10
        
    Returns:
        Descripción del código o None si no existe
    """
    cie10 = await execute_query(
        "SELECT descripcion FROM catalogo_cie10 WHERE codigo = %s AND activo = true",
        (codigo_cie10,),
        fetch_one=True
    )
    
    return cie10["descripcion"] if cie10 else None


async def create_diagnostico(
    cita_id: int,
    tipo: str,
    descripcion: str,
    codigo_cie10: Optional[str],
    id_podologo: int
) -> Dict[str, Any]:
    """
    Crea un diagnóstico para una cita.
    
    Args:
        cita_id: ID de la cita
        tipo: Tipo de diagnóstico (Presuntivo/Definitivo)
        descripcion: Descripción del diagnóstico
        codigo_cie10: Código CIE-10 opcional
        id_podologo: ID del podólogo
        
    Returns:
        Diagnóstico creado
        
    Raises:
        Exception: Si hay error en la creación
    """
    query = """
        INSERT INTO nota_clinica (
            id_cita, 
            motivo_consulta, 
            diagnostico_presuntivo,
            diagnostico_definitivo,
            codigo_cie10_presuntivo_manual,
            codigo_cie10_definitivo_manual,
            elaborado_por
        )
        VALUES (%s, %s, 
                CASE WHEN %s = 'Presuntivo' THEN %s ELSE NULL END,
                CASE WHEN %s = 'Definitivo' THEN %s ELSE NULL END,
                CASE WHEN %s = 'Presuntivo' THEN %s ELSE NULL END,
                CASE WHEN %s = 'Definitivo' THEN %s ELSE NULL END,
                %s
        )
        ON CONFLICT (id_cita) DO UPDATE SET
            diagnostico_presuntivo = CASE WHEN %s = 'Presuntivo' THEN %s ELSE nota_clinica.diagnostico_presuntivo END,
            diagnostico_definitivo = CASE WHEN %s = 'Definitivo' THEN %s ELSE nota_clinica.diagnostico_definitivo END,
            codigo_cie10_presuntivo_manual = CASE WHEN %s = 'Presuntivo' THEN %s ELSE nota_clinica.codigo_cie10_presuntivo_manual END,
            codigo_cie10_definitivo_manual = CASE WHEN %s = 'Definitivo' THEN %s ELSE nota_clinica.codigo_cie10_definitivo_manual END
        RETURNING id, id_cita, fecha_elaboracion
    """
    
    params = (
        cita_id,
        descripcion,  # motivo_consulta
        tipo,
        descripcion,
        tipo,
        descripcion,
        tipo,
        codigo_cie10,
        tipo,
        codigo_cie10,
        id_podologo,
        # Para el UPDATE
        tipo,
        descripcion,
        tipo,
        descripcion,
        tipo,
        codigo_cie10,
        tipo,
        codigo_cie10,
    )
    
    result = await execute_mutation(query, params, returning=True)
    
    if not result:
        raise Exception("Error al crear diagnóstico en la base de datos")
    
    return result


# ============================================================================
# CATÁLOGO CIE-10
# ============================================================================


async def search_cie10(search: str, limit: int = 50) -> List[Dict[str, Any]]:
    """
    Busca códigos CIE-10 por código, descripción o categoría.
    
    Args:
        search: Término de búsqueda
        limit: Número máximo de resultados
        
    Returns:
        Lista de códigos CIE-10 coincidentes
    """
    query = """
        SELECT id, codigo, descripcion, categoria, subcategoria
        FROM catalogo_cie10
        WHERE activo = true
          AND (
              codigo ILIKE %s
              OR descripcion ILIKE %s
              OR categoria ILIKE %s
          )
        ORDER BY codigo
        LIMIT %s
    """
    
    search_pattern = f"%{search}%"
    params = (search_pattern, search_pattern, search_pattern, limit)
    
    resultados = await execute_query(query, params)
    return resultados or []
