from asyncio import run as asyncio_run
from os import environ

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from src.database import Database
from src.handlers import ReminderMiddleware, router as handlers_router
from src.forms import router as forms_router
from src.logging import Logger
from src.scheduler import Scheduler, send_daily_notification
from src.weather import WeatherAPI


async def main():
    Logger(environ.get('LOGGING_FILE_PATH'))

    bot = Bot(token=environ.get('TELEGRAM_BOT_API_TOKEN'))

    scheduler = Scheduler()
    scheduler.add_morning_task(send_daily_notification, (bot,))
    scheduler.start()

    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(handlers_router)
    dp.include_router(forms_router)

    dp.update.middleware(ReminderMiddleware())

    await Database(environ.get('DATABASE_PATH')).init()

    WeatherAPI(environ.get('OPEN_WAETHER_API_TOKEN'))

    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio_run(main())
