import asyncio
import os

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv

from bot.domain.storage import Storage
from bot.handlers import get_handlers
from bot.infrastructure.storage_postgres import StoragePostgres
from bot.middlewares.persist_update_and_ensure_user_exists import PersistUpdateAndEnsureUserExistsMiddleware

load_dotenv()


async def main() -> None:
    storage: Storage = StoragePostgres()

    async with Bot(token=os.getenv("TELEGRAM_TOKEN")) as bot:
        dp = Dispatcher(storage=MemoryStorage())
        dp.update.outer_middleware(PersistUpdateAndEnsureUserExistsMiddleware(storage))
        dp.include_routers(*get_handlers())

        try:
            await dp.start_polling(bot)
        except KeyboardInterrupt:
            print("\nBye!")
        finally:
            if hasattr(storage, "close"):
                await storage.close()


if __name__ == "__main__":
    asyncio.run(main())
