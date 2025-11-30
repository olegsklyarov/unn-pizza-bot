from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from aiogram.utils.serialization import deserialize_telegram_object_to_python


from bot.domain.storage import Storage


class UpdateDatabaseLoggerMiddleware(BaseMiddleware):
    """Outer Middleware для логирования всех обновлений в БД."""

    def __init__(self, storage: Storage) -> None:
        self._storage = storage

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        payload = deserialize_telegram_object_to_python(event)
        await self._storage.persist_update(payload)

        return await handler(event, data)
