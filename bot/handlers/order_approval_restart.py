import asyncio

from aiogram import Bot, Router
from aiogram.filters import Text
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from bot.domain.order_state import OrderState
from bot.domain.storage import Storage

router = Router()


@router.callback_query(Text("order_restart"))
async def order_approval_restart_handler(
    callback: CallbackQuery,
    bot: Bot,
    storage: Storage,
    user_state: OrderState | None,
) -> None:
    """Обработчик перезапуска заказа."""
    if not callback.from_user or not callback.message:
        return

    if user_state != OrderState.WAIT_FOR_ORDER_APPROVE:
        return

    telegram_id = callback.from_user.id

    # Выполнить answer_callback_query, delete_message и обновления БД параллельно
    await asyncio.gather(
        callback.answer(),
        bot.delete_message(
            chat_id=callback.message.chat.id, message_id=callback.message.message_id
        ),
        storage.clear_user_order_json(telegram_id),
        storage.update_user_state(telegram_id, OrderState.WAIT_FOR_PIZZA_NAME),
    )

    # Создаем inline клавиатуру для выбора пиццы
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

    # Send pizza selection message with inline keyboard
    await bot.send_message(
        chat_id=callback.message.chat.id,
        text="Please choose pizza type",
        reply_markup=keyboard,
    )
