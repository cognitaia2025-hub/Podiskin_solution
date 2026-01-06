# Scripts Backend - Organización

Esta carpeta contiene scripts utilitarios organizados por categoría.

## 📁 Estructura

```
scripts/
├── setup/          Scripts de configuración inicial
├── utils/          Utilidades y herramientas de mantenimiento
├── simulators/     Simuladores para testing y demos
└── examples/       Ejemplos de uso del sistema
```

## 📂 Categorías

### 🔧 setup/
Scripts para configurar el sistema desde cero:
- Configuración inicial de la base de datos
- Creación de usuarios administrativos
- Generación de datos de prueba

**Cuándo usar:** Primera vez que configuras el proyecto o después de resetear la BD.

### 🛠️ utils/
Herramientas de mantenimiento y utilidades:
- Scripts de inspección de base de datos
- Creación de usuarios de prueba
- Limpieza de datos para producción

**Cuándo usar:** Tareas de mantenimiento o debugging.

### 🎭 simulators/
Simuladores interactivos para testing:
- Simuladores de chat (WhatsApp, Operaciones)
- Demos sin conexión a BD
- Herramientas de prueba interactiva

**Cuándo usar:** Testing de agentes y flujos conversacionales.

### 📚 examples/
Ejemplos de código y uso del sistema:
- Ejemplos de integración
- Patrones de uso de la API
- Documentación en código

**Cuándo usar:** Aprender cómo usar componentes del sistema.

---

## 📝 Notas

- Los **tests unitarios** van en la carpeta `tests/` (fuera de scripts/)
- Scripts obsoletos o de un solo uso deben eliminarse
- Mantener documentación actualizada en cada script
