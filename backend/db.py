import databases
import os
import asyncpg
from dotenv import load_dotenv

# Cargar entorno
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    # Construir como fallback si no existe DATABASE_URL
    DB_USER = os.getenv("DB_USER", "podoskin_user")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "podoskin_password_123")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME", "podoskin_db")
    DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

database = databases.Database(DATABASE_URL)

async def get_db_connection_citas():
    """Retorna una conexión asíncrona usando asyncpg."""
    # Usar los componentes individuales o parsear la URL
    return await asyncpg.connect(DATABASE_URL)
