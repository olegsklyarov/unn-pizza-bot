from abc import ABC, abstractmethod


class Storage(ABC):
    @abstractmethod
    async def ensure_user_exists(self, telegram_id: int) -> None: ...

    @abstractmethod
    async def persist_update(self, update: dict) -> None: ...

    @abstractmethod
    async def recreate_database(self) -> None: ...
