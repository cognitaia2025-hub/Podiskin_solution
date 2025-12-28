"""
Summaries SubAgent Configuration
"""

import os
from dotenv import load_dotenv

load_dotenv()

# LLM Configuration
LLM_MODEL = os.getenv("SUMMARIES_LLM_MODEL", "claude-3-5-haiku-20241022")
LLM_TEMPERATURE = float(os.getenv("SUMMARIES_LLM_TEMPERATURE", "0.5"))
LLM_MAX_TOKENS = int(os.getenv("SUMMARIES_LLM_MAX_TOKENS", "3000"))

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://localhost/podoskin")

# Summary Templates
SUMMARY_TEMPLATES = {
    "consulta_actual": {
        "breve": """
        ## Resumen de Consulta
        
        **Fecha:** {fecha}
        **Paciente:** {paciente}
        **Motivo:** {motivo_consulta}
        
        **Hallazgos:**
        {hallazgos}
        
        **Plan:**
        {plan_tratamiento}
        """,
        
        "detallado": """
        ## RESUMEN DETALLADO DE CONSULTA
        
        **Información General**
        - Fecha: {fecha}
        - Paciente: {paciente}
        - Edad: {edad} años
        - Motivo de Consulta: {motivo_consulta}
        
        **Signos Vitales**
        {signos_vitales}
        
        **Padecimiento Actual**
        {padecimiento_actual}
        
        **Exploración Física**
        {exploracion_fisica}
        
        **Diagnóstico**
        - Presuntivo: {diagnostico_presuntivo}
        - Definitivo: {diagnostico_definitivo}
        
        **Plan de Tratamiento**
        {plan_tratamiento}
        
        **Indicaciones al Paciente**
        {indicaciones_paciente}
        """,
        
        "para_paciente": """
        ## Su Consulta de Hoy
        
        Estimado(a) {paciente},
        
        Fecha: {fecha}
        
        **¿Por qué vino?**
        {motivo_consulta}
        
        **¿Qué encontramos?**
        {diagnostico_simple}
        
        **¿Qué debe hacer?**
        {indicaciones_paciente}
        
        **Próximos pasos:**
        {seguimiento}
        """
    },
    
    "evolucion_tratamiento": {
        "breve": """
        ## Evolución de Tratamiento
        
        **Paciente:** {paciente}
        **Tratamiento:** {tratamiento}
        **Período:** {periodo}
        
        **Evolución:**
        {evolucion}
        
        **Estado Actual:**
        {estado_actual}
        """,
        
        "detallado": """
        ## EVOLUCIÓN DETALLADA DE TRATAMIENTO
        
        **Paciente:** {paciente}
        **Tratamiento:** {tratamiento}
        **Inicio:** {fecha_inicio}
        **Última Revisión:** {fecha_ultima}
        
        **Objetivo del Tratamiento:**
        {objetivo}
        
        **Evolución por Consultas:**
        {evolucion_detallada}
        
        **Mejorías Observadas:**
        {mejorias}
        
        **Complicaciones:**
        {complicaciones}
        
        **Recomendación:**
        {recomendacion}
        """
    },
    
    "historial_completo": {
        "breve": """
        ## Historial Médico
        
        **Paciente:** {paciente}
        **Fecha de Registro:** {fecha_registro}
        **Total de Consultas:** {total_consultas}
        
        **Principales Diagnósticos:**
        {diagnosticos}
        
        **Tratamientos Relevantes:**
        {tratamientos}
        
        **Alergias:**
        {alergias}
        """,
        
        "detallado": """
        ## HISTORIAL MÉDICO COMPLETO
        
        **Datos del Paciente**
        - Nombre: {paciente}
        - Edad: {edad}
        - Fecha de Registro: {fecha_registro}
        - Total de Consultas: {total_consultas}
        
        **Antecedentes Personales**
        {antecedentes}
        
        **Alergias Conocidas**
        {alergias}
        
        **Historial de Consultas**
        {historial_consultas}
        
        **Evolución de Signos Vitales**
        {evolucion_vitales}
        
        **Tratamientos Completados**
        {tratamientos_completados}
        
        **Tratamientos Activos**
        {tratamientos_activos}
        
        **Observaciones Generales**
        {observaciones}
        """
    }
}

# Search Configuration
SEMANTIC_SEARCH_ENABLED = os.getenv("SEMANTIC_SEARCH_ENABLED", "false").lower() == "true"
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
SEARCH_THRESHOLD = float(os.getenv("SEARCH_THRESHOLD", "0.7"))

# Validation
MIN_SUMMARY_LENGTH = int(os.getenv("MIN_SUMMARY_LENGTH", "50"))
MAX_SUMMARY_LENGTH = int(os.getenv("MAX_SUMMARY_LENGTH", "5000"))

# Checkpointer
CHECKPOINTER_TYPE = os.getenv("SUMMARIES_CHECKPOINTER", "memory")

# LangSmith
LANGSMITH_PROJECT = os.getenv("LANGSMITH_PROJECT", "podoskin-summaries")
