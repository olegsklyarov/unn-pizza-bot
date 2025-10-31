from abc import ABC, abstractmethod

from bot.domain.order_state import OrderState


class Storage(ABC):
    @abstractmethod
    def ensure_user_exists(self, telegram_id: int) -> None: ...

    @abstractmethod
    def clear_user_order_json(self, telegram_id: int) -> None: ...

    @abstractmethod
    def update_user_state(self, telegram_id: int, state: OrderState) -> None: ...

    @abstractmethod
    def persist_update(self, update: dict) -> None: ...

    @abstractmethod
    def update_user_order_json(self, telegram_id: int, order_json: dict) -> None: ...

    @abstractmethod
    def recreate_database(self) -> None: ...

    @abstractmethod
    def get_user(self, telegram_id: int) -> dict: ...
