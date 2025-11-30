import asyncio

from aiogram import Bot, Router, F
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from bot.domain.fsm import Order
from aiogram.fsm.context import FSMContext

router = Router()


@router.callback_query(
    Order.wait_for_drinks,
    F.data.in_(
        [
            "drink_coca_cola",
            "drink_pepsi",
            "drink_orange_juice",
            "drink_apple_juice",
            "drink_water",
            "drink_iced_tea",
            "drink_none",
        ]
    ),
)
async def pizza_drinks_handler(
    callback: CallbackQuery,
    bot: Bot,
    state: FSMContext,
) -> None:
    drink_mapping = {
        "drink_coca_cola": "Coca-Cola",
        "drink_pepsi": "Pepsi",
        "drink_orange_juice": "Orange Juice",
        "drink_apple_juice": "Apple Juice",
        "drink_water": "Water",
        "drink_iced_tea": "Iced Tea",
        "drink_none": "No drinks",
    }
    selected_drink = drink_mapping.get(callback.data)

    (pizza_name, pizza_size) = await asyncio.gather(
        state.get_value("pizza_name"),
        state.get_value("pizza_size"),
    )

    order_summary = f"""🍕 **Your Order Summary:**

**Pizza:** {pizza_name}
**Size:** {pizza_size}
**Drink:** {selected_drink}

Is everything correct?"""

    # Создаем inline клавиатуру для подтверждения заказа
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Ok", callback_data="order_approve"),
                InlineKeyboardButton(
                    text="🔄 Start again", callback_data="order_restart"
                ),
            ],
        ]
    )

    await asyncio.gather(
        state.update_data(drink=selected_drink),
        state.set_state(Order.wait_for_order_approve),
        bot.answer_callback_query(callback.id),
        bot.delete_message(
            chat_id=callback.message.chat.id, message_id=callback.message.message_id
        ),
        bot.send_message(
            chat_id=callback.message.chat.id,
            text=order_summary,
            parse_mode="Markdown",
            reply_markup=keyboard,
        ),
    )
