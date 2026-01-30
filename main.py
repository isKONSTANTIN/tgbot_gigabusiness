import asyncio
import logging
from aiogram import Bot, Dispatcher
from config import TOKEN

from handlers_menu import router_menu
from handlers_survey import router_survey


async def main():
    logging.basicConfig(level=logging.INFO)
    bot = Bot(token=TOKEN)
    dp = Dispatcher()
    dp.include_routers(router_menu, router_survey)
    print("Бот запущен")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Exit")