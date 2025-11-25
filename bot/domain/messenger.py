from abc import ABC, abstractmethod


class Messenger(ABC):
    @abstractmethod
    async def send_message(self, chat_id: int, text: str, **kwargs) -> dict: ...

    @abstractmethod
    async def get_updates(self, **kwargs) -> list: ...

    @abstractmethod
    async def answer_callback_query(self, callback_query_id: str, **kwargs) -> dict: ...

    @abstractmethod
    async def delete_message(self, chat_id: int, message_id: int) -> dict: ...

    @abstractmethod
    async def send_invoice(
        self,
        chat_id: int,
        title: str,
        description: str,
        payload: str,
        provider_token: str,
        currency: str,
        prices: list,
        **kwargs,
    ) -> dict: ...

    @abstractmethod
    async def answer_pre_checkout_query(
        self, pre_checkout_query_id: str, ok: bool, **kwargs
    ) -> dict: ...
