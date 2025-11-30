import asyncio
import json
import os

from aiogram import Bot, Router
from aiogram.filters import Text
from aiogram.types import CallbackQuery, LabeledPrice
from dotenv import load_dotenv

from bot.domain.order_state import OrderState
from bot.domain.storage import Storage

load_dotenv()

router = Router()


@router.callback_query(Text("order_approve"))
async def order_approval_approved_handler(
    callback: CallbackQuery,
    bot: Bot,
    storage: Storage,
    user_state: OrderState | None,
    order_json: dict,
) -> None:
    """Обработчик подтверждения заказа."""
    if not callback.from_user or not callback.message:
        return

    if user_state != OrderState.WAIT_FOR_ORDER_APPROVE:
        return

    telegram_id = callback.from_user.id

    # Выполнить answer_callback_query, delete_message и update_user_state параллельно
    await asyncio.gather(
        callback.answer(),
        bot.delete_message(
            chat_id=callback.message.chat.id, message_id=callback.message.message_id
        ),
        storage.update_user_state(telegram_id, OrderState.WAIT_FOR_PAYMENT),
    )

    pizza_name = order_json.get("pizza_name", "Unknown")
    pizza_size = order_json.get("pizza_size", "Unknown")
    drink = order_json.get("drink", "Unknown")

    # Calculate prices (in kopecks for RUB)
    # Base prices - these can be customized
    pizza_prices = {
        "Small (25cm)": 50000,  # 500.00 RUB
        "Medium (30cm)": 65000,  # 650.00 RUB
        "Large (35cm)": 80000,  # 800.00 RUB
        "Extra Large (40cm)": 95000,  # 950.00 RUB
    }
    drink_price = 10000  # 100.00 RUB (if drink is selected and not "No drinks")

    pizza_price = pizza_prices.get(pizza_size, 50000)
    prices = [
        LabeledPrice(label=f"Pizza: {pizza_name} ({pizza_size})", amount=pizza_price)
    ]

    if drink and drink != "No drinks":
        prices.append(LabeledPrice(label=f"Drink: {drink}", amount=drink_price))

    # Create order payload
    order_payload = json.dumps(
        {
            "telegram_id": telegram_id,
            "pizza_name": pizza_name,
            "pizza_size": pizza_size,
            "drink": drink,
        }
    )

    # Send invoice
    await bot.send_invoice(
        chat_id=callback.message.chat.id,
        title="Pizza Order",
        description=f"Pizza: {pizza_name}, Size: {pizza_size}, Drink: {drink}",
        payload=order_payload,
        provider_token=os.getenv("YOOKASSA_TOKEN"),
        currency="RUB",
        prices=prices,
    )
