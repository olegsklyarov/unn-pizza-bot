from bot.domain.messenger import Messenger
from bot.domain.order_state import OrderState
from bot.domain.storage import Storage
from bot.handlers.handler import Handler, HandlerStatus


class OrderApprovalApprovedHandler(Handler):
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
        return callback_data == "order_approve"

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

        storage.update_user_state(telegram_id, OrderState.ORDER_FINISHED)

        pizza_name = order_json.get("pizza_name", "Unknown")
        pizza_size = order_json.get("pizza_size", "Unknown")
        drink = order_json.get("drink", "Unknown")

        order_confirmation = f"""✅ **Order Confirmed!**
🍕 **Your Order:**
• Pizza: {pizza_name}
• Size: {pizza_size}
• Drink: {drink}

Thank you for your order! Your pizza will be ready soon.

Send /start to place another order."""

        # Send order confirmation message
        messenger.send_message(
            chat_id=update["callback_query"]["message"]["chat"]["id"],
            text=order_confirmation,
            parse_mode="Markdown",
        )

        return HandlerStatus.STOP
