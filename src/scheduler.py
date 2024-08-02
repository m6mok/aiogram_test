from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from contextlib import suppress

from src.database import Database
from src.utils import Singleton


DAILY_NOTIFICATION_MESSAGE = 'Не забудьте проверить уведомления!'


class Scheduler(Singleton):
    def __init__(self):
        self.scheduler = AsyncIOScheduler()

    def add_morning_task(self, task, args):
        self.scheduler.add_job(
            task,
            'cron',
            hour=9,
            args=args,
            timezone='Europe/Moscow'
        )

    def start(self):
        self.scheduler.start()


async def send_daily_notification(bot: Bot):
    for user_id in (
        user[0] for user in await Database.obj.get_users()
    ):
        await bot.send_message(user_id, DAILY_NOTIFICATION_MESSAGE)
