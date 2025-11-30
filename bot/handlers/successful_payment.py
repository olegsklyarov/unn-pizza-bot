import json

from aiogram import Bot, Router
from aiogram.types import Message, SuccessfulPayment

from bot.domain.order_state import OrderState
from bot.domain.storage import Storage

router = Router()


@router.message(lambda message: message.successful_payment is not None)
async def successful_payment_handler(
    message: Message,
    bot: Bot,
    storage: Storage,
) -> None:
    """Обработчик успешного платежа."""
    if not message.from_user or not message.successful_payment:
        return

    telegram_id = message.from_user.id
    successful_payment: SuccessfulPayment = message.successful_payment

    # Parse payload to get order details
    payload = json.loads(successful_payment.invoice_payload)
    pizza_name = payload.get("pizza_name", "Unknown")
    pizza_size = payload.get("pizza_size", "Unknown")
    drink = payload.get("drink", "Unknown")

    # Update user state to ORDER_FINISHED
    await storage.update_user_state(telegram_id, OrderState.ORDER_FINISHED)

    order_confirmation = f"""✅ **Order Confirmed!**
🍕 **Your Order:**
• Pizza: {pizza_name}
• Size: {pizza_size}
• Drink: {drink}

Thank you for your payment! Your pizza will be ready soon.

Send /start to place another order."""

    # Send order confirmation message
    await bot.send_message(
        chat_id=message.chat.id,
        text=order_confirmation,
        parse_mode="Markdown",
    )
