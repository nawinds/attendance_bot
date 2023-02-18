import logging
import os
from aiogram import Bot, Dispatcher
import datetime
import asyncio


API_TOKEN = os.getenv("TOKEN")

START_DATE = datetime.datetime(year=2022, month=2, day=26)
WEEKDAY_NAMES = ["понедельник", "вторник", "среда", "четверг", "пятница", "суббота", "воскресенье"]
OPTIONS = [
    "Буду в школе",
    "Не приду",
    "Посмотреть результаты"
]

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

if not os.path.exists("group_chats.txt"):
    open("group_chats.txt", "w")

with open("group_chats.txt", encoding="utf-8") as f:
    group_chats = f.read().split(",")

if datetime.datetime.now().weekday() == 5:
    exit()

if datetime.datetime.now() < START_DATE:
    exit()


def format_data(number: int) -> str:
    number = str(number)
    if len(number) < 2:
        number = "0" + number
    return number


async def send_poll(chat_id: int, question: str, options: list[str]) -> None:
    await bot.send_poll(chat_id, question, options=options,
                        is_anonymous=False, allows_multiple_answers=False)


target_day = datetime.datetime.now()
if target_day.hour > 15:
    target_day = target_day + datetime.timedelta(days=1)
weekday = WEEKDAY_NAMES[target_day.weekday()].capitalize()
title = f"{weekday}, {format_data(target_day.day)}.{format_data(target_day.month)}"
loop = asyncio.new_event_loop()
for chat in group_chats:
    if chat:
        loop.run_until_complete(send_poll(int(chat), title, OPTIONS))
