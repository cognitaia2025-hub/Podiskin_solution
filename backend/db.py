import databases
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://podoskin_user:podoskin_password_123@localhost:5432/podoskin_db")

database = databases.Database(DATABASE_URL)
