import json
import logging
import os
import time

import asyncpg
from dotenv import load_dotenv

from bot.domain.order_state import OrderState
from bot.domain.storage import Storage

load_dotenv()

# Настройка логирования для БД запросов
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s.%(msecs)03d] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


class StoragePostgres(Storage):
    def __init__(self) -> None:
        self._pool: asyncpg.Pool | None = None

    async def _get_pool(self) -> asyncpg.Pool:
        """Создать и вернуть connection pool для PostgreSQL."""
        if self._pool is None:
            host = os.getenv("POSTGRES_HOST")
            port = os.getenv("POSTGRES_PORT")
            user = os.getenv("POSTGRES_USER")
            password = os.getenv("POSTGRES_PASSWORD")
            database = os.getenv("POSTGRES_DATABASE")

            if host is None:
                raise ValueError("POSTGRES_HOST environment variable is not set")
            if port is None:
                raise ValueError("POSTGRES_PORT environment variable is not set")
            if user is None:
                raise ValueError("POSTGRES_USER environment variable is not set")
            if password is None:
                raise ValueError("POSTGRES_PASSWORD environment variable is not set")
            if database is None:
                raise ValueError("POSTGRES_DATABASE environment variable is not set")

            self._pool = await asyncpg.create_pool(
                host=host,
                port=int(port),
                user=user,
                password=password,
                database=database,
            )
        return self._pool

    async def close(self) -> None:
        """Закрыть connection pool."""
        if self._pool:
            await self._pool.close()
            self._pool = None

    async def persist_update(self, update: dict) -> None:
        method_name = "persist_update"
        sql_query = "INSERT INTO telegram_events (payload) VALUES ($1)"
        start_time = time.time()

        logger.info(f"[DB] → {method_name} - {sql_query}")

        payload = json.dumps(update, ensure_ascii=False, indent=2)
        try:
            pool = await self._get_pool()
            async with pool.acquire() as conn:
                await conn.execute(
                    "INSERT INTO telegram_events (payload) VALUES ($1)", payload
                )

            duration_ms = (time.time() - start_time) * 1000
            logger.info(f"[DB] ← {method_name} - {duration_ms:.2f}ms")
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.error(f"[DB] ✗ {method_name} - {duration_ms:.2f}ms - Error: {e}")
            raise

    async def update_user_order_json(self, telegram_id: int, order_json: dict) -> None:
        method_name = "update_user_order_json"
        sql_query = "UPDATE users SET order_json = $1 WHERE telegram_id = $2"
        start_time = time.time()

        logger.info(f"[DB] → {method_name} - {sql_query}")

        try:
            pool = await self._get_pool()
            async with pool.acquire() as conn:
                await conn.execute(
                    "UPDATE users SET order_json = $1 WHERE telegram_id = $2",
                    json.dumps(order_json, ensure_ascii=False, indent=2),
                    telegram_id,
                )

            duration_ms = (time.time() - start_time) * 1000
            logger.info(f"[DB] ← {method_name} - {duration_ms:.2f}ms")
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.error(f"[DB] ✗ {method_name} - {duration_ms:.2f}ms - Error: {e}")
            raise

    async def recreate_database(self) -> None:
        method_name = "recreate_database"
        start_time = time.time()

        logger.info(f"[DB] → {method_name} - DROP/CREATE TABLES")

        try:
            pool = await self._get_pool()
            async with pool.acquire() as conn:
                await conn.execute("DROP TABLE IF EXISTS telegram_events")
                await conn.execute("DROP TABLE IF EXISTS users")
                await conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS telegram_events
                    (
                        id SERIAL PRIMARY KEY,
                        payload TEXT NOT NULL
                    )
                    """
                )
                await conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS users
                    (
                        id SERIAL PRIMARY KEY,
                        telegram_id BIGINT NOT NULL UNIQUE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        state TEXT DEFAULT NULL,
                        order_json TEXT DEFAULT NULL
                    )
                    """
                )

            duration_ms = (time.time() - start_time) * 1000
            logger.info(f"[DB] ← {method_name} - {duration_ms:.2f}ms")
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.error(f"[DB] ✗ {method_name} - {duration_ms:.2f}ms - Error: {e}")
            raise

    async def get_user(self, telegram_id: int) -> dict | None:
        method_name = "get_user"
        sql_query = "SELECT id, telegram_id, created_at, state, order_json FROM users WHERE telegram_id = $1"
        start_time = time.time()

        logger.info(f"[DB] → {method_name} - {sql_query}")

        try:
            pool = await self._get_pool()
            async with pool.acquire() as conn:
                result = await conn.fetchrow(
                    "SELECT id, telegram_id, created_at, state, order_json FROM users WHERE telegram_id = $1",
                    telegram_id,
                )
                if result:
                    user_data = {
                        "id": result["id"],
                        "telegram_id": result["telegram_id"],
                        "created_at": result["created_at"],
                        "state": result["state"],
                        "order_json": result["order_json"],
                    }
                    duration_ms = (time.time() - start_time) * 1000
                    logger.info(f"[DB] ← {method_name} - {duration_ms:.2f}ms")
                    return user_data
                duration_ms = (time.time() - start_time) * 1000
                logger.info(f"[DB] ← {method_name} - {duration_ms:.2f}ms (no result)")
                return None
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.error(f"[DB] ✗ {method_name} - {duration_ms:.2f}ms - Error: {e}")
            raise

    async def clear_user_order_json(self, telegram_id: int) -> None:
        method_name = "clear_user_order_json"
        sql_query = (
            "UPDATE users SET state = NULL, order_json = NULL WHERE telegram_id = $1"
        )
        start_time = time.time()

        logger.info(f"[DB] → {method_name} - {sql_query}")

        try:
            pool = await self._get_pool()
            async with pool.acquire() as conn:
                await conn.execute(
                    "UPDATE users SET state = NULL, order_json = NULL WHERE telegram_id = $1",
                    telegram_id,
                )

            duration_ms = (time.time() - start_time) * 1000
            logger.info(f"[DB] ← {method_name} - {duration_ms:.2f}ms")
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.error(f"[DB] ✗ {method_name} - {duration_ms:.2f}ms - Error: {e}")
            raise

    async def update_user_state(self, telegram_id: int, state: OrderState) -> None:
        method_name = "update_user_state"
        sql_query = "UPDATE users SET state = $1 WHERE telegram_id = $2"
        start_time = time.time()

        logger.info(f"[DB] → {method_name} - {sql_query}")

        try:
            pool = await self._get_pool()
            async with pool.acquire() as conn:
                await conn.execute(
                    "UPDATE users SET state = $1 WHERE telegram_id = $2",
                    state,
                    telegram_id,
                )

            duration_ms = (time.time() - start_time) * 1000
            logger.info(f"[DB] ← {method_name} - {duration_ms:.2f}ms")
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.error(f"[DB] ✗ {method_name} - {duration_ms:.2f}ms - Error: {e}")
            raise

    async def ensure_user_exists(self, telegram_id: int) -> None:
        method_name = "ensure_user_exists"
        start_time = time.time()

        logger.info(f"[DB] → {method_name} - SELECT/INSERT users")

        try:
            pool = await self._get_pool()
            async with pool.acquire() as conn:
                result = await conn.fetchrow(
                    "SELECT 1 FROM users WHERE telegram_id = $1",
                    telegram_id,
                )

                if result is None:
                    await conn.execute(
                        "INSERT INTO users (telegram_id) VALUES ($1)",
                        telegram_id,
                    )

            duration_ms = (time.time() - start_time) * 1000
            logger.info(f"[DB] ← {method_name} - {duration_ms:.2f}ms")
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.error(f"[DB] ✗ {method_name} - {duration_ms:.2f}ms - Error: {e}")
            raise
