# Código Obsoleto - Backend

==========================================

## Archivos Obsoletos Detectados [04/01/26] [17:43]

==========================================

### Archivos de Ejemplo (No usados en producción)

**1. backend/citas/app_example.py**

- Líneas: 1-169
- Razón: Archivo de ejemplo para integración FastAPI standalone
- Recomendación: ELIMINAR (funcionalidad ya integrada en main.py)

**2. backend/citas/demo_validacion.py**

- Líneas: 1-204
- Razón: Script de demostración de validación de conflictos
- Recomendación: MOVER a carpeta /docs o /examples

**3. backend/citas/test_logica.py**

- Líneas: 1-11707
- Razón: Archivo de pruebas de lógica
- Recomendación: MOVER a carpeta /tests

**4. backend/tratamientos/app_example.py**

- Líneas: 1-88
- Razón: Aplicación FastAPI de ejemplo standalone
- Recomendación: ELIMINAR (ya integrado en main.py)

**5. backend/tratamientos/examples.py**

- Líneas: 1-8913
- Razón: Ejemplos de uso del módulo
- Recomendación: MOVER a /docs/examples

**6. backend/tratamientos/test_imc.py**

- Líneas: 1-2354
- Razón: Tests de cálculo de IMC
- Recomendación: MOVER a /tests

**7. backend/agents/state-principal.py**

- Líneas: 1 (archivo vacío)
- Razón: Archivo vacío sin contenido
- Recomendación: ELIMINAR o implementar funcionalidad

### Rutas hardcodeadas obsoletas

**8. backend/citas/app_example.py - Línea 16**

```python
sys.path.insert(0, "/home/runner/work/Podiskin_solution/Podiskin_solution/backend")
```

- Razón: Ruta específica de entorno de desarrollo antiguo
- Impacto: No funciona en otros entornos

**9. backend/citas/demo_validacion.py - Línea 15**

```python
sys.path.insert(0, "/home/runner/work/Podiskin_solution/Podiskin_solution/backend")
```

- Razón: Misma ruta hardcodeada obsoleta

### Resumen para Santiago

Se encontraron varios archivos que ya no se usan en la aplicación principal:

**Archivos de ejemplo y prueba:**
Estos son archivos que se crearon para probar funcionalidades durante el desarrollo, pero ya no son necesarios porque todo está integrado en el sistema principal. Son como "borradores" que se pueden eliminar sin afectar el funcionamiento de tu aplicación.

**Impacto en tu experiencia:**

- NINGUNO: Estos archivos no afectan el funcionamiento actual de la aplicación
- Beneficio de limpiarlos: La carpeta del proyecto será más ordenada y fácil de mantener
- Recomendación: Se pueden eliminar de forma segura o mover a una carpeta de "ejemplos" para referencia futura

---
