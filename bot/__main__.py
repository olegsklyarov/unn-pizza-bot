import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
import dotenv


dotenv.load_dotenv()


dp = Dispatcher()


@dp.message(F.text)
async def message_text_echo_handler(message: Message) -> None:
    await message.answer(message.text)


async def main() -> None:
    bot = Bot(token=os.getenv("TELEGRAM_TOKEN"))
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
