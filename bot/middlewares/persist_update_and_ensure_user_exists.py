from typing import Any, Awaitable, Callable

import asyncio

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, User
from aiogram.utils.serialization import deserialize_telegram_object_to_python

from bot.domain.storage import Storage


class PersistUpdateAndEnsureUserExistsMiddleware(BaseMiddleware):

    def __init__(self, storage: Storage) -> None:
        self._storage: Storage = storage

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        payload = deserialize_telegram_object_to_python(event)
        user: User = data["event_from_user"]

        await asyncio.gather(
            self._storage.ensure_user_exists(user.id),
            self._storage.persist_update(payload),
            return_exceptions=True,
        )

        return await handler(event, data)
