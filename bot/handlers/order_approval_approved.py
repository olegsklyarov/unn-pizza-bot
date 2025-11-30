import asyncio
import json
import os

from aiogram import Bot, Router, F
from aiogram.types import CallbackQuery, LabeledPrice
from aiogram.fsm.context import FSMContext

from dotenv import load_dotenv

from bot.domain.fsm import Order

load_dotenv()

router = Router()


@router.callback_query(
    Order.wait_for_order_approve,
    F.data == "order_approve",
)
async def order_approval_approved_handler(
    callback: CallbackQuery,
    bot: Bot,
    state: FSMContext,
) -> None:
    (pizza_name, pizza_size, drink) = await asyncio.gather(
        state.get_value("pizza_name"),
        state.get_value("pizza_size"),
        state.get_value("drink"),
    )

    pizza_prices = {
        "Small (25cm)": 50000,  # 500.00 RUB
        "Medium (30cm)": 65000,  # 650.00 RUB
        "Large (35cm)": 80000,  # 800.00 RUB
        "Extra Large (40cm)": 95000,  # 950.00 RUB
    }
    drink_price = 10000  # 100.00 RUB (if drink is selected and not "No drinks")

    pizza_price = pizza_prices.get(pizza_size)
    prices = [
        LabeledPrice(label=f"Pizza: {pizza_name} ({pizza_size})", amount=pizza_price)
    ]

    if drink and drink != "No drinks":
        prices.append(LabeledPrice(label=f"Drink: {drink}", amount=drink_price))

    order_payload = json.dumps(
        {
            "telegram_id": callback.from_user.id,
            "pizza_name": pizza_name,
            "pizza_size": pizza_size,
            "drink": drink,
        }
    )

    await asyncio.gather(
        bot.answer_callback_query(callback.id),
        bot.delete_message(
            chat_id=callback.message.chat.id, message_id=callback.message.message_id
        ),
        state.set_state(Order.wait_for_payment),
        bot.send_invoice(
            chat_id=callback.message.chat.id,
            title="Pizza Order",
            description=f"Pizza: {pizza_name}, Size: {pizza_size}, Drink: {drink}",
            payload=order_payload,
            provider_token=os.getenv("YOOKASSA_TOKEN"),
            currency="RUB",
            prices=prices,
        ),
    )
