import asyncio

from aiogram import Bot, Router, F
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from bot.domain.fsm import Order
from aiogram.fsm.context import FSMContext

router = Router()


@router.callback_query(
    Order.wait_for_pizza_size,
    F.data.in_(["size_small", "size_medium", "size_large", "size_xl"]),
)
async def pizza_size_handler(
    callback: CallbackQuery,
    bot: Bot,
    state: FSMContext,
) -> None:

    size_mapping = {
        "size_small": "Small (25cm)",
        "size_medium": "Medium (30cm)",
        "size_large": "Large (35cm)",
        "size_xl": "Extra Large (40cm)",
    }

    pizza_size = size_mapping.get(callback.data)

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Coca-Cola", callback_data="drink_coca_cola"),
                InlineKeyboardButton(text="Pepsi", callback_data="drink_pepsi"),
            ],
            [
                InlineKeyboardButton(
                    text="Orange Juice", callback_data="drink_orange_juice"
                ),
                InlineKeyboardButton(
                    text="Apple Juice", callback_data="drink_apple_juice"
                ),
            ],
            [
                InlineKeyboardButton(text="Water", callback_data="drink_water"),
                InlineKeyboardButton(text="Iced Tea", callback_data="drink_iced_tea"),
            ],
            [
                InlineKeyboardButton(text="No drinks", callback_data="drink_none"),
            ],
        ]
    )

    await asyncio.gather(
        bot.answer_callback_query(callback.id),
        state.update_data(pizza_size=pizza_size),
        state.set_state(Order.wait_for_drinks),
        bot.delete_message(
            chat_id=callback.message.chat.id, message_id=callback.message.message_id
        ),
        bot.send_message(
            chat_id=callback.message.chat.id,
            text="Please choose some drinks",
            reply_markup=keyboard,
        ),
    )
