from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from bot.domain.storage import Storage


class StorageMiddleware(BaseMiddleware):
    """Middleware для передачи Storage в хэндлеры через event data."""

    def __init__(self, storage: Storage) -> None:
        self._storage = storage

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        data["storage"] = self._storage
        return await handler(event, data)
