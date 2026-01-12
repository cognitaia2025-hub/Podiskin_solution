#!/bin/bash
# Script para ejecutar pruebas del Web Chat
# Inicia el backend si no está corriendo y luego ejecuta los tests

set -e

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${YELLOW}║   PRUEBAS INTEGRACIÓN WEB CHAT - PODOSKIN SOLUTION            ║${NC}"
echo -e "${YELLOW}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Verificar si el backend está corriendo
echo -e "${YELLOW}🔍 Verificando backend...${NC}"
if curl -s http://localhost:8000/api/chatbot/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Backend ya está corriendo${NC}"
    BACKEND_RUNNING=true
else
    echo -e "${YELLOW}⚠️  Backend no está corriendo${NC}"
    echo -e "${YELLOW}📝 Para que las pruebas funcionen, el backend debe estar corriendo${NC}"
    echo ""
    echo -e "${YELLOW}Opciones:${NC}"
    echo "  1. Iniciar backend manualmente:"
    echo "     cd /workspaces/Podiskin_solution/backend"
    echo "     python main.py"
    echo ""
    echo "  2. Ejecutar pruebas cuando el backend esté listo"
    echo ""
    echo -e "${RED}❌ Abortando pruebas${NC}"
    exit 1
fi

echo ""

# Verificar que las tablas existan
echo -e "${YELLOW}🔍 Verificando base de datos...${NC}"
if ! psql -U postgres -d podoskin_db -c "SELECT 1 FROM pacientes LIMIT 1;" > /dev/null 2>&1; then
    echo -e "${RED}❌ Error: Tabla 'pacientes' no existe o no es accesible${NC}"
    echo -e "${YELLOW}💡 Aplicar migración:${NC}"
    echo "   psql -U postgres -d podoskin_db -f data/migrations/20_web_chat_integration.sql"
    exit 1
fi

# Verificar columna patient_id
if ! psql -U postgres -d podoskin_db -c "SELECT patient_id FROM pacientes LIMIT 1;" > /dev/null 2>&1; then
    echo -e "${RED}❌ Error: Columna 'patient_id' no existe en tabla pacientes${NC}"
    echo -e "${YELLOW}💡 Aplicar migración:${NC}"
    echo "   psql -U postgres -d podoskin_db -f data/migrations/20_web_chat_integration.sql"
    exit 1
fi

echo -e "${GREEN}✅ Base de datos configurada correctamente${NC}"
echo ""

# Ejecutar pruebas
echo -e "${YELLOW}🚀 Ejecutando simulador de chat web...${NC}"
echo ""

python scripts/test_web_chat_simple.py

EXIT_CODE=$?

echo ""
if [ $EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✅ Pruebas completadas exitosamente${NC}"
else
    echo -e "${RED}❌ Pruebas fallaron con código: $EXIT_CODE${NC}"
fi

exit $EXIT_CODE
