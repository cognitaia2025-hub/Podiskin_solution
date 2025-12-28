"""
Orchestrator Configuration
Configuración del Agente Padre Orquestador
"""

import os
from typing import Dict, List
from dotenv import load_dotenv

load_dotenv()

# LLM Configuration
LLM_MODEL = os.getenv("ORCHESTRATOR_LLM_MODEL", "claude-3-5-haiku-20241022")
LLM_TEMPERATURE = float(os.getenv("ORCHESTRATOR_LLM_TEMPERATURE", "0.3"))
LLM_MAX_TOKENS = int(os.getenv("ORCHESTRATOR_LLM_MAX_TOKENS", "2000"))

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://localhost/podoskin")

# SubAgents Configuration
SUBAGENTS_CONFIG = {
    "summaries": {
        "name": "SubAgente Resúmenes",
        "enabled": True,
        "graph_path": "backend.agents.summaries.graph",
        "timeout_seconds": 30,
        "max_retries": 2
    },
    "analysis": {
        "name": "SubAgente Análisis Clínico",
        "enabled": False,  # Not implemented yet
        "graph_path": "backend.agents.analysis.graph",
        "timeout_seconds": 60,
        "max_retries": 2
    },
    "whatsapp": {
        "name": "SubAgente WhatsApp",
        "enabled": True,
        "graph_path": "backend.agents.sub_agent_whatsApp.graph",
        "timeout_seconds": 20,
        "max_retries": 2
    }
}

# Function Classification
# Simple functions go directly to endpoints
SIMPLE_FUNCTIONS = [
    "update_vital_signs",
    "create_clinical_note",
    "query_patient_data",
    "add_allergy",
    "navigate_to_section",
    "schedule_followup"
]

# Complex functions require SubAgent processing
COMPLEX_FUNCTIONS_MAPPING = {
    "search_patient_history": {
        "subagent": "summaries",  # Uses summaries for semantic search
        "requires_context": True,
        "requires_validation": True
    },
    "generate_summary": {
        "subagent": "summaries",
        "requires_context": True,
        "requires_validation": True
    }
}

# Validation Rules
VALIDATION_RULES = {
    "generate_summary": {
        "min_length": 50,
        "max_length": 5000,
        "required_sections": ["fecha", "paciente"],
        "forbidden_keywords": ["password", "api_key", "token"]
    },
    "search_patient_history": {
        "min_results": 0,
        "max_results": 20,
        "required_fields": ["fecha", "contenido"]
    }
}

# Audit Configuration
AUDIT_ENABLED = os.getenv("AUDIT_ENABLED", "true").lower() == "true"
AUDIT_LOG_TABLE = "orchestrator_audit_logs"

# Checkpointer Configuration
CHECKPOINTER_TYPE = os.getenv("CHECKPOINTER_TYPE", "memory")  # memory, postgres, redis
CHECKPOINTER_URL = os.getenv("CHECKPOINTER_URL", DATABASE_URL)

# Timeouts
DEFAULT_TIMEOUT_SECONDS = int(os.getenv("ORCHESTRATOR_TIMEOUT", "45"))
SUBAGENT_TIMEOUT_SECONDS = int(os.getenv("SUBAGENT_TIMEOUT", "30"))

# Retry Configuration
MAX_RETRIES = int(os.getenv("ORCHESTRATOR_MAX_RETRIES", "2"))
RETRY_DELAY_SECONDS = float(os.getenv("ORCHESTRATOR_RETRY_DELAY", "1.0"))

# LangSmith Configuration (for tracing)
LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")
LANGSMITH_PROJECT = os.getenv("LANGSMITH_PROJECT", "podoskin-orchestrator")
LANGSMITH_ENABLED = os.getenv("LANGSMITH_TRACING", "false").lower() == "true"

if LANGSMITH_ENABLED and LANGSMITH_API_KEY:
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_API_KEY"] = LANGSMITH_API_KEY
    os.environ["LANGCHAIN_PROJECT"] = LANGSMITH_PROJECT
