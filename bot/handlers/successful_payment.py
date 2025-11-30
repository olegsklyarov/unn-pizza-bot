import asyncio
import json

from aiogram import Bot, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, SuccessfulPayment

from bot.domain.fsm import Order

router = Router()


@router.message(F.successful_payment)
async def successful_payment_handler(
    message: Message,
    bot: Bot,
    state: FSMContext,
) -> None:
    successful_payment: SuccessfulPayment = message.successful_payment

    payload = json.loads(successful_payment.invoice_payload)
    pizza_name = payload.get("pizza_name")
    pizza_size = payload.get("pizza_size")
    drink = payload.get("drink")

    order_confirmation = f"""✅ **Order Confirmed!**
🍕 **Your Order:**
• Pizza: {pizza_name}
• Size: {pizza_size}
• Drink: {drink}

Thank you for your payment! Your pizza will be ready soon.

Send /start to place another order."""

    await asyncio.gather(
        await state.set_state(Order.order_finished),
        bot.send_message(
            chat_id=message.chat.id,
            text=order_confirmation,
            parse_mode="Markdown",
        ),
        return_exceptions=True,
    )
