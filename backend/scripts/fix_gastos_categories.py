import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()


def fix_categories():
    try:
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST", "127.0.0.1"),
            port=int(os.getenv("DB_PORT", "5432")),
            database=os.getenv("DB_NAME", "podoskin_db"),
            user=os.getenv("DB_USER", "podoskin_user"),
            password=os.getenv("DB_PASSWORD", "podoskin_password_123"),
        )
        cur = conn.cursor()

        print("Eliminando constraint de categorías en tabla gastos...")

        # Intentar obtener el nombre del constraint
        cur.execute(
            """
            SELECT conname
            FROM pg_constraint
            WHERE conrelid = 'gastos'::regclass
            AND contype = 'c'
            AND pg_get_constraintdef(oid) LIKE '%categoria%';
        """
        )

        constraints = cur.fetchall()

        if not constraints:
            print("No se encontró constraint de categoría. Tal vez ya fue eliminado.")
        else:
            for constraint in constraints:
                constraint_name = constraint[0]
                print(f"Eliminando constraint: {constraint_name}")
                cur.execute(f"ALTER TABLE gastos DROP CONSTRAINT {constraint_name};")

        conn.commit()
        print(
            "Constraint eliminado exitosamente. Ahora se aceptan todas las categorias."
        )

    except Exception as e:
        print(f"Error: {e}")
    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    fix_categories()
