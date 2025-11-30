from aiogram import Router

from bot.handlers import (
    message_start,
    pizza_selection,
    pizza_size,
    pizza_drinks,
    # order_approval_approved,
    order_approval_restart,
    # pre_checkout_query,
    # successful_payment,
)


def get_handlers() -> list[Router]:
    """Возвращает список роутеров для регистрации в dispatcher."""
    return [
        message_start.router,
        pizza_selection.router,
        pizza_size.router,
        pizza_drinks.router,
        # order_approval_approved.router,
        order_approval_restart.router,
        # pre_checkout_query.router,
        # successful_payment.router,
    ]
