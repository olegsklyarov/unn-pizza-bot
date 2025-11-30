import json
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, User

from bot.domain.order_state import OrderState
from bot.domain.storage import Storage


class UserStateMiddleware(BaseMiddleware):
    def __init__(self, storage: Storage) -> None:
        self._storage = storage

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        storage = self._storage

        user: User = data["event_from_user"]

        telegram_id: int = user.id
        await storage.ensure_user_exists(telegram_id)
        user = await storage.get_user(telegram_id)

        state_str = user.get("state")
        data["user_state"] = OrderState(state_str) if state_str else None
        order_json_str = user.get("order_json") or "{}"
        data["order_json"] = json.loads(order_json_str)

        return await handler(event, data)
