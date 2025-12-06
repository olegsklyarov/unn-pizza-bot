import asyncio
import os

from aiogram import Bot, Dispatcher
import dotenv


dotenv.load_dotenv()


dp = Dispatcher()


async def main() -> None:
    bot = Bot(token=os.getenv("TELEGRAM_TOKEN"))
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
