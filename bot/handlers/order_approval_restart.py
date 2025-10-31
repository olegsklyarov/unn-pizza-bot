import json

from bot.domain.messenger import Messenger
from bot.domain.order_state import OrderState
from bot.domain.storage import Storage
from bot.handlers.handler import Handler, HandlerStatus


class OrderApprovalRestartHandler(Handler):
    def can_handle(
        self,
        update: dict,
        state: OrderState,
        order_json: dict,
        storage: Storage,
        messenger: Messenger,
    ) -> bool:
        if "callback_query" not in update:
            return False

        if state != OrderState.WAIT_FOR_ORDER_APPROVE:
            return False

        callback_data = update["callback_query"]["data"]
        return callback_data == "order_restart"

    def handle(
        self,
        update: dict,
        state: OrderState,
        order_json: dict,
        storage: Storage,
        messenger: Messenger,
    ) -> HandlerStatus:
        telegram_id = update["callback_query"]["from"]["id"]

        messenger.answer_callback_query(update["callback_query"]["id"])
        messenger.delete_message(
            chat_id=update["callback_query"]["message"]["chat"]["id"],
            message_id=update["callback_query"]["message"]["message_id"],
        )

        storage.clear_user_order_json(telegram_id)

        # Update user state to wait for pizza selection
        storage.update_user_state(telegram_id, OrderState.WAIT_FOR_PIZZA_NAME)

        # Send pizza selection message with inline keyboard
        messenger.send_message(
            chat_id=update["callback_query"]["message"]["chat"]["id"],
            text="Please choose pizza type",
            reply_markup=json.dumps(
                {
                    "inline_keyboard": [
                        [
                            {
                                "text": "Margherita",
                                "callback_data": "pizza_margherita",
                            },
                            {
                                "text": "Pepperoni",
                                "callback_data": "pizza_pepperoni",
                            },
                        ],
                        [
                            {
                                "text": "Quattro Stagioni",
                                "callback_data": "pizza_quattro_stagioni",
                            },
                            {
                                "text": "Capricciosa",
                                "callback_data": "pizza_capricciosa",
                            },
                        ],
                        [
                            {"text": "Diavola", "callback_data": "pizza_diavola"},
                            {
                                "text": "Prosciutto",
                                "callback_data": "pizza_prosciutto",
                            },
                        ],
                    ],
                },
            ),
        )

        return HandlerStatus.STOP
