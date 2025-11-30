import asyncio

from aiogram import F, Bot, Router
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext

from bot.domain.fsm import Order

router = Router()


@router.callback_query(
    Order.wait_for_order_approve,
    F.data == "order_restart",
)
async def order_approval_restart_handler(
    callback: CallbackQuery,
    bot: Bot,
    state: FSMContext,
) -> None:

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Margherita", callback_data="pizza_margherita"
                ),
                InlineKeyboardButton(text="Pepperoni", callback_data="pizza_pepperoni"),
            ],
            [
                InlineKeyboardButton(
                    text="Quattro Stagioni", callback_data="pizza_quattro_stagioni"
                ),
                InlineKeyboardButton(
                    text="Capricciosa", callback_data="pizza_capricciosa"
                ),
            ],
            [
                InlineKeyboardButton(text="Diavola", callback_data="pizza_diavola"),
                InlineKeyboardButton(
                    text="Prosciutto", callback_data="pizza_prosciutto"
                ),
            ],
        ]
    )

    await asyncio.gather(
        state.set_data({}),
        state.set_state(Order.wait_for_pizza_name),
        bot.answer_callback_query(callback.id),
        bot.delete_message(
            chat_id=callback.message.chat.id, message_id=callback.message.message_id
        ),
        bot.send_message(
            chat_id=callback.message.chat.id,
            text="Please choose pizza type",
            reply_markup=keyboard,
        ),
    )
