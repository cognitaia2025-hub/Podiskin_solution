# Script de Instalación del Backend - Podoskin Solution
# ======================================================
# Este script configura el entorno virtual con todas las dependencias

Write-Host "🚀 Instalando Backend de Podoskin Solution..." -ForegroundColor Cyan
Write-Host ""

# 1. Verificar Python
Write-Host "1️⃣ Verificando Python..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Python no encontrado. Por favor instala Python 3.11+" -ForegroundColor Red
    exit 1
}
Write-Host "✅ $pythonVersion" -ForegroundColor Green
Write-Host ""

# 2. Crear entorno virtual
Write-Host "2️⃣ Creando entorno virtual..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Write-Host "⚠️ El entorno virtual ya existe. ¿Deseas recrearlo? (S/N)" -ForegroundColor Yellow
    $response = Read-Host
    if ($response -eq "S" -or $response -eq "s") {
        Remove-Item -Recurse -Force venv
        python -m venv venv
        Write-Host "✅ Entorno virtual recreado" -ForegroundColor Green
    } else {
        Write-Host "⏭️ Usando entorno virtual existente" -ForegroundColor Cyan
    }
} else {
    python -m venv venv
    Write-Host "✅ Entorno virtual creado" -ForegroundColor Green
}
Write-Host ""

# 3. Activar entorno virtual
Write-Host "3️⃣ Activando entorno virtual..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️ Error de permisos. Ejecutando:" -ForegroundColor Yellow
    Write-Host "Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser" -ForegroundColor Cyan
    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
    & .\venv\Scripts\Activate.ps1
}
Write-Host "✅ Entorno virtual activado" -ForegroundColor Green
Write-Host ""

# 4. Actualizar pip
Write-Host "4️⃣ Actualizando pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip --quiet
Write-Host "✅ pip actualizado" -ForegroundColor Green
Write-Host ""

# 5. Instalar PyTorch CPU
Write-Host "5️⃣ Instalando PyTorch (CPU version)..." -ForegroundColor Yellow
pip install torch==2.5.0 --index-url https://download.pytorch.org/whl/cpu --quiet
Write-Host "✅ PyTorch instalado" -ForegroundColor Green
Write-Host ""

# 6. Instalar dependencias principales
Write-Host "6️⃣ Instalando dependencias principales..." -ForegroundColor Yellow
Write-Host "   (Esto puede tomar varios minutos...)" -ForegroundColor Gray
pip install -r requirements.txt --quiet
Write-Host "✅ Dependencias instaladas" -ForegroundColor Green
Write-Host ""

# 7. Descargar modelo de embeddings
Write-Host "7️⃣ Descargando modelo de embeddings (all-MiniLM-L6-v2)..." -ForegroundColor Yellow
Write-Host "   (Primera vez: ~90MB, puede tardar...)" -ForegroundColor Gray
python -c "from sentence_transformers import SentenceTransformer; print('Descargando...'); SentenceTransformer('all-MiniLM-L6-v2'); print('✅ Modelo descargado')"
Write-Host ""

# 8. Crear archivo .env si no existe
Write-Host "8️⃣ Configurando archivo .env..." -ForegroundColor Yellow
if (!(Test-Path ".env")) {
    @"
# Database
DATABASE_URL=postgresql://postgres:podoskin2024@localhost:5432/podoskin_db

# Anthropic API
ANTHROPIC_API_KEY=sk-ant-your-api-key-here

# LLM Configuration
LLM_MODEL=claude-3-haiku-20240307
LLM_TEMPERATURE=0.7

# Embeddings
EMBEDDING_MODEL=all-MiniLM-L6-v2
EMBEDDING_DIMENSION=384

# RAG
RAG_K=5
RAG_SCORE_THRESHOLD=0.5

# Logging
LOG_LEVEL=INFO

# Server
HOST=0.0.0.0
PORT=8000
"@ | Out-File -FilePath .env -Encoding utf8
    Write-Host "✅ Archivo .env creado" -ForegroundColor Green
    Write-Host "⚠️ IMPORTANTE: Edita .env y agrega tu ANTHROPIC_API_KEY" -ForegroundColor Yellow
} else {
    Write-Host "⏭️ Archivo .env ya existe" -ForegroundColor Cyan
}
Write-Host ""

# 9. Crear .gitignore si no existe
Write-Host "9️⃣ Configurando .gitignore..." -ForegroundColor Yellow
if (!(Test-Path ".gitignore")) {
    @"
# Python
venv/
__pycache__/
*.py[cod]
*`$py.class
*.so
.Python
*.egg-info/
dist/
build/

# Environment
.env
.env.local

# IDE
.vscode/
.idea/
*.swp
*.swo

# Logs
*.log
logs/

# Jupyter
.ipynb_checkpoints/

# Models cache
.cache/
models/

# OS
.DS_Store
Thumbs.db
"@ | Out-File -FilePath .gitignore -Encoding utf8
    Write-Host "✅ .gitignore creado" -ForegroundColor Green
} else {
    Write-Host "⏭️ .gitignore ya existe" -ForegroundColor Cyan
}
Write-Host ""

# 10. Verificar instalación
Write-Host "🔍 Verificando instalación..." -ForegroundColor Yellow
Write-Host ""

$verification = python -c @"
try:
    import langchain
    import langgraph
    import asyncpg
    import sentence_transformers
    import torch
    print('✅ LangChain:', langchain.__version__)
    print('✅ LangGraph:', langgraph.__version__)
    print('✅ AsyncPG:', asyncpg.__version__)
    print('✅ Sentence Transformers:', sentence_transformers.__version__)
    print('✅ PyTorch:', torch.__version__)
    print('')
    print('🎉 ¡Todo instalado correctamente!')
except Exception as e:
    print('❌ Error:', str(e))
    exit(1)
"@

if ($LASTEXITCODE -eq 0) {
    Write-Host $verification -ForegroundColor Green
} else {
    Write-Host "❌ Error en la verificación" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host "✅ INSTALACIÓN COMPLETADA" -ForegroundColor Green
Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host ""
Write-Host "📝 Próximos pasos:" -ForegroundColor Yellow
Write-Host "1. Edita .env y agrega tu ANTHROPIC_API_KEY" -ForegroundColor White
Write-Host "2. Asegúrate de que Docker con PostgreSQL esté corriendo:" -ForegroundColor White
Write-Host "   docker-compose up -d" -ForegroundColor Cyan
Write-Host "3. Prueba el sub-agente:" -ForegroundColor White
Write-Host "   python agents/sub_agent_whatsApp/example_usage.py" -ForegroundColor Cyan
Write-Host ""
Write-Host "Para activar el entorno virtual en el futuro:" -ForegroundColor Yellow
Write-Host ".\venv\Scripts\Activate.ps1" -ForegroundColor Cyan
Write-Host ""
