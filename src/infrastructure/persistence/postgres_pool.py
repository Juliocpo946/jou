import psycopg
from psycopg import AsyncConnection
from psycopg_pool import AsyncConnectionPool
from config.settings import settings
import logging

logger = logging.getLogger(__name__)

class PostgresPool:
    _pool: AsyncConnectionPool = None

    @classmethod
    async def initialize(cls) -> None:
        if cls._pool is not None:
            return
        
        try:
            cls._pool = AsyncConnectionPool(
                settings.DATABASE_URL,
                min_size=5,
                max_size=settings.DATABASE_POOL_SIZE,
                max_idle=30,
                max_lifetime=3600,
                timeout=settings.DATABASE_POOL_TIMEOUT,
                connect_kwargs={
                    "connect_timeout": 10,
                }
            )
            await cls._pool.open()
            logger.info("Pool PostgreSQL inicializado correctamente")
        except Exception as e:
            logger.error(f"Error inicializando pool PostgreSQL: {str(e)}")
            raise

    @classmethod
    async def close(cls) -> None:
        if cls._pool is not None:
            await cls._pool.close()
            cls._pool = None
            logger.info("Pool PostgreSQL cerrado")

    @classmethod
    async def get_connection(cls) -> AsyncConnection:
        if cls._pool is None:
            raise RuntimeError("Pool no inicializado. Llamar a initialize() primero")
        return await cls._pool.getconn()

    @classmethod
    async def execute(cls, query: str, params: tuple = None):
        async with await cls.get_connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(query, params or ())
                return await cur.fetchall()

    @classmethod
    async def execute_one(cls, query: str, params: tuple = None):
        async with await cls.get_connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(query, params or ())
                return await cur.fetchone()

    @classmethod
    async def execute_update(cls, query: str, params: tuple = None) -> int:
        async with await cls.get_connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(query, params or ())
                await conn.commit()
                return cur.rowcount

    @classmethod
    async def execute_insert(cls, query: str, params: tuple = None) -> str:
        async with await cls.get_connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(query, params or ())
                await conn.commit()
                result = await cur.fetchone()
                return result[0] if result else None

    @classmethod
    async def batch_execute_update(cls, query: str, params_list: list) -> int:
        async with await cls.get_connection() as conn:
            async with conn.cursor() as cur:
                total_rows = 0
                for params in params_list:
                    await cur.execute(query, params)
                    total_rows += cur.rowcount
                await conn.commit()
                return total_rows