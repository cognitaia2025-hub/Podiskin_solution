import os
import sys
from dotenv import load_dotenv
import psycopg

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

load_dotenv()


def inspect():
    db_url = os.getenv(
        "DATABASE_URL",
        "postgresql://podoskin_user:podoskin_password_123@localhost:5432/podoskin_db",
    )
    print(f"Connecting to: {db_url.split('@')[1]}")  # Print host/db only for security

    try:
        conn = psycopg.connect(db_url)
        cur = conn.cursor()

        cur.execute(
            "SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'usuarios'"
        )
        columns = cur.fetchall()

        print("\n=== COLUMNS IN 'usuarios' ===")
        for col in columns:
            print(f"- {col[0]} ({col[1]})")

        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    inspect()
