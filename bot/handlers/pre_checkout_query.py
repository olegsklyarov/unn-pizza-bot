from aiogram import Bot, Router
from aiogram.types import PreCheckoutQuery

router = Router()


@router.pre_checkout_query()
async def pre_checkout_query_handler(
    pre_checkout_query: PreCheckoutQuery,
    bot: Bot,
) -> None:
    """Обработчик pre-checkout query для подтверждения платежа."""
    # Answer with ok=True to approve the payment
    await bot.answer_pre_checkout_query(
        pre_checkout_query_id=pre_checkout_query.id, ok=True
    )
