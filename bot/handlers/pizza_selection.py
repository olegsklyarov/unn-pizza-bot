import asyncio

from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from bot.domain.fsm import Order

router = Router()


@router.callback_query(
    Order.wait_for_pizza_name,
    F.data.in_(
        [
            "pizza_margherita",
            "pizza_pepperoni",
            "pizza_quattro_stagioni",
            "pizza_capricciosa",
            "pizza_diavola",
            "pizza_prosciutto",
        ]
    ),
)
async def pizza_selection_handler(
    callback: CallbackQuery,
    bot: Bot,
    state: FSMContext,
) -> None:
    pizza_name = callback.data.replace("pizza_", "").replace("_", " ").title()
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Small (25cm)", callback_data="size_small"),
                InlineKeyboardButton(text="Medium (30cm)", callback_data="size_medium"),
            ],
            [
                InlineKeyboardButton(text="Large (35cm)", callback_data="size_large"),
                InlineKeyboardButton(
                    text="Extra Large (40cm)", callback_data="size_xl"
                ),
            ],
        ]
    )

    await asyncio.gather(
        state.update_data(pizza_name=pizza_name),
        state.set_state(Order.wait_for_pizza_size),
        bot.answer_callback_query(callback.id),
        bot.delete_message(
            chat_id=callback.message.chat.id,
            message_id=callback.message.message_id,
        ),
        bot.send_message(
            chat_id=callback.message.chat.id,
            text="Please select pizza size",
            reply_markup=keyboard,
        ),
    )
