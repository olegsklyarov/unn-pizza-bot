import json
import logging
import os
import time

import pg8000
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
    def _get_connection(self):
        """Create and return a PostgreSQL connection."""
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

        return pg8000.connect(
            host=host,
            port=int(port),
            user=user,
            password=password,
            database=database,
        )

    def persist_update(self, update: dict) -> None:
        method_name = "persist_update"
        sql_query = "INSERT INTO telegram_events (payload) VALUES (%s)"
        start_time = time.time()

        logger.info(f"[DB] → {method_name} - {sql_query}")

        payload = json.dumps(update, ensure_ascii=False, indent=2)
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        "INSERT INTO telegram_events (payload) VALUES (%s)", (payload,)
                    )
                conn.commit()

            duration_ms = (time.time() - start_time) * 1000
            logger.info(f"[DB] ← {method_name} - {duration_ms:.2f}ms")
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.error(f"[DB] ✗ {method_name} - {duration_ms:.2f}ms - Error: {e}")
            raise

    def update_user_order_json(self, telegram_id: int, order_json: dict) -> None:
        method_name = "update_user_order_json"
        sql_query = "UPDATE users SET order_json = %s WHERE telegram_id = %s"
        start_time = time.time()

        logger.info(f"[DB] → {method_name} - {sql_query}")

        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        "UPDATE users SET order_json = %s WHERE telegram_id = %s",
                        (json.dumps(order_json, ensure_ascii=False, indent=2), telegram_id),
                    )
                conn.commit()

            duration_ms = (time.time() - start_time) * 1000
            logger.info(f"[DB] ← {method_name} - {duration_ms:.2f}ms")
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.error(f"[DB] ✗ {method_name} - {duration_ms:.2f}ms - Error: {e}")
            raise

    def recreate_database(self) -> None:
        method_name = "recreate_database"
        start_time = time.time()

        logger.info(f"[DB] → {method_name} - DROP/CREATE TABLES")

        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    # cursor.execute("DROP TABLE IF EXISTS telegram_events")
                    # cursor.execute("DROP TABLE IF EXISTS users")
                    cursor.execute(
                        """
                        CREATE TABLE IF NOT EXISTS telegram_events
                        (
                            id SERIAL PRIMARY KEY,
                            payload TEXT NOT NULL
                        )
                        """
                    )
                    cursor.execute(
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
                conn.commit()

            duration_ms = (time.time() - start_time) * 1000
            logger.info(f"[DB] ← {method_name} - {duration_ms:.2f}ms")
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.error(f"[DB] ✗ {method_name} - {duration_ms:.2f}ms - Error: {e}")
            raise

    def get_user(self, telegram_id: int) -> dict | None:
        method_name = "get_user"
        sql_query = "SELECT id, telegram_id, created_at, state, order_json FROM users WHERE telegram_id = %s"
        start_time = time.time()

        logger.info(f"[DB] → {method_name} - {sql_query}")

        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        "SELECT id, telegram_id, created_at, state, order_json FROM users WHERE telegram_id = %s",
                        (telegram_id,),
                    )
                    result = cursor.fetchone()
                    if result:
                        user_data = {
                            "id": result[0],
                            "telegram_id": result[1],
                            "created_at": result[2],
                            "state": result[3],
                            "order_json": result[4],
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

    def clear_user_order_json(self, telegram_id: int) -> None:
        method_name = "clear_user_order_json"
        sql_query = "UPDATE users SET state = NULL, order_json = NULL WHERE telegram_id = %s"
        start_time = time.time()

        logger.info(f"[DB] → {method_name} - {sql_query}")

        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        "UPDATE users SET state = NULL, order_json = NULL WHERE telegram_id = %s",
                        (telegram_id,),
                    )
                conn.commit()

            duration_ms = (time.time() - start_time) * 1000
            logger.info(f"[DB] ← {method_name} - {duration_ms:.2f}ms")
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.error(f"[DB] ✗ {method_name} - {duration_ms:.2f}ms - Error: {e}")
            raise

    def update_user_state(self, telegram_id: int, state: OrderState) -> None:
        method_name = "update_user_state"
        sql_query = "UPDATE users SET state = %s WHERE telegram_id = %s"
        start_time = time.time()

        logger.info(f"[DB] → {method_name} - {sql_query}")

        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        "UPDATE users SET state = %s WHERE telegram_id = %s",
                        (state, telegram_id),
                    )
                conn.commit()

            duration_ms = (time.time() - start_time) * 1000
            logger.info(f"[DB] ← {method_name} - {duration_ms:.2f}ms")
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.error(f"[DB] ✗ {method_name} - {duration_ms:.2f}ms - Error: {e}")
            raise

    def ensure_user_exists(self, telegram_id: int) -> None:
        method_name = "ensure_user_exists"
        start_time = time.time()

        logger.info(f"[DB] → {method_name} - SELECT/INSERT users")

        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        "SELECT 1 FROM users WHERE telegram_id = %s",
                        (telegram_id,),
                    )

                    if cursor.fetchone() is None:
                        cursor.execute(
                            "INSERT INTO users (telegram_id) VALUES (%s)",
                            (telegram_id,),
                        )
                conn.commit()

            duration_ms = (time.time() - start_time) * 1000
            logger.info(f"[DB] ← {method_name} - {duration_ms:.2f}ms")
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.error(f"[DB] ✗ {method_name} - {duration_ms:.2f}ms - Error: {e}")
            raise
