import asyncio

from aiogram import Bot, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from bot.domain.fsm import Order

router = Router()


@router.message(Command("start"))
async def message_start(
    message: Message,
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
        state.clear(),
        bot.send_message(
            chat_id=message.chat.id,
            text="🍕 Welcome to Pizza shop!",
            reply_markup=None,
        ),
    )

    await asyncio.gather(
        state.set_state(Order.wait_for_pizza_name),
        bot.send_message(
            chat_id=message.chat.id,
            text="Please choose pizza type",
            reply_markup=keyboard,
        ),
    )
