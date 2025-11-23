import asyncio
import json

from bot.domain.messenger import Messenger
from bot.domain.order_state import OrderState
from bot.domain.storage import Storage
from bot.handlers.handler import Handler, HandlerStatus


class PizzaDrinksHandler(Handler):
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

        if state != OrderState.WAIT_FOR_DRINKS:
            return False

        callback_data = update["callback_query"]["data"]
        return callback_data.startswith("drink_")

    async def handle(
        self,
        update: dict,
        state: OrderState,
        order_json: dict,
        storage: Storage,
        messenger: Messenger,
    ) -> HandlerStatus:
        telegram_id = update["callback_query"]["from"]["id"]
        callback_data = update["callback_query"]["data"]

        # Extract drink name from callback data (remove 'drink_' prefix)
        drink_mapping = {
            "drink_coca_cola": "Coca-Cola",
            "drink_pepsi": "Pepsi",
            "drink_orange_juice": "Orange Juice",
            "drink_apple_juice": "Apple Juice",
            "drink_water": "Water",
            "drink_iced_tea": "Iced Tea",
            "drink_none": "No drinks",
        }
        selected_drink = drink_mapping.get(callback_data)

        order_json["drink"] = selected_drink
        chat_id = update["callback_query"]["message"]["chat"]["id"]
        message_id = update["callback_query"]["message"]["message_id"]
        callback_query_id = update["callback_query"]["id"]

        # Выполнить обновления БД и answer_callback_query параллельно
        await asyncio.gather(
            storage.update_user_order_json(telegram_id, order_json),
            storage.update_user_state(telegram_id, OrderState.WAIT_FOR_ORDER_APPROVE),
            messenger.answer_callback_query(callback_query_id),
        )

        # Create order summary message
        pizza_name = order_json.get("pizza_name", "Unknown")
        pizza_size = order_json.get("pizza_size", "Unknown")
        drink = order_json.get("drink", "Unknown")

        order_summary = f"""🍕 **Your Order Summary:**

**Pizza:** {pizza_name}
**Size:** {pizza_size}
**Drink:** {drink}

Is everything correct?"""

        # Удалить сообщение и отправить новое параллельно
        await asyncio.gather(
            messenger.delete_message(chat_id=chat_id, message_id=message_id),
            messenger.send_message(
                chat_id=chat_id,
                text=order_summary,
                parse_mode="Markdown",
                reply_markup=json.dumps(
                    {
                        "inline_keyboard": [
                            [
                                {"text": "✅ Ok", "callback_data": "order_approve"},
                                {
                                    "text": "🔄 Start again",
                                    "callback_data": "order_restart",
                                },
                            ],
                        ],
                    },
                ),
            ),
        )
        return HandlerStatus.STOP
