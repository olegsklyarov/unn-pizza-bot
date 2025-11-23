from bot.domain.messenger import Messenger
from bot.domain.order_state import OrderState
from bot.domain.storage import Storage
from bot.handlers.handler import Handler, HandlerStatus


class PreCheckoutQueryHandler(Handler):
    def can_handle(
        self,
        update: dict,
        state: OrderState,
        order_json: dict,
        storage: Storage,
        messenger: Messenger,
    ) -> bool:
        return "pre_checkout_query" in update

    async def handle(
        self,
        update: dict,
        state: OrderState,
        order_json: dict,
        storage: Storage,
        messenger: Messenger,
    ) -> HandlerStatus:
        pre_checkout_query = update["pre_checkout_query"]
        pre_checkout_query_id = pre_checkout_query["id"]

        # Answer with ok=True to approve the payment
        await messenger.answer_pre_checkout_query(
            pre_checkout_query_id=pre_checkout_query_id, ok=True
        )

        return HandlerStatus.STOP
