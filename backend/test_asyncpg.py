import asyncio
import asyncpg


async def test():
    try:
        conn = await asyncpg.connect(
            "postgresql://podoskin_user:podoskin_password_123@127.0.0.1:5432/podoskin_db"
        )
        print("Conexion asyncpg OK!")
        await conn.close()
    except Exception as e:
        print(f"Error asyncpg: {type(e).__name__}: {e}")


asyncio.run(test())
