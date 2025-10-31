import json

from bot.domain.messenger import Messenger
from bot.domain.order_state import OrderState
from bot.domain.storage import Storage
from bot.handlers.handler import Handler, HandlerStatus


class SuccessfulPaymentHandler(Handler):
    def can_handle(
        self,
        update: dict,
        state: OrderState,
        order_json: dict,
        storage: Storage,
        messenger: Messenger,
    ) -> bool:
        if "message" not in update:
            return False

        return "successful_payment" in update["message"]

    def handle(
        self,
        update: dict,
        state: OrderState,
        order_json: dict,
        storage: Storage,
        messenger: Messenger,
    ) -> HandlerStatus:
        telegram_id = update["message"]["from"]["id"]
        successful_payment = update["message"]["successful_payment"]

        # Parse payload to get order details
        payload = json.loads(successful_payment["invoice_payload"])
        pizza_name = payload.get("pizza_name", "Unknown")
        pizza_size = payload.get("pizza_size", "Unknown")
        drink = payload.get("drink", "Unknown")

        # Update user state to ORDER_FINISHED
        storage.update_user_state(telegram_id, OrderState.ORDER_FINISHED)

        order_confirmation = f"""✅ **Order Confirmed!**
🍕 **Your Order:**
• Pizza: {pizza_name}
• Size: {pizza_size}
• Drink: {drink}

Thank you for your payment! Your pizza will be ready soon.

Send /start to place another order."""

        # Send order confirmation message
        messenger.send_message(
            chat_id=update["message"]["chat"]["id"],
            text=order_confirmation,
            parse_mode="Markdown",
        )

        return HandlerStatus.STOP
