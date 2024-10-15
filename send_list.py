import logging
import os
import datetime
import asyncio
from main import POLL_TITLE, POLL_OPTIONS, bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from send_poll import START_DATE, POLL_OPTIONS

LIST_ADMINS = list(map(int, os.getenv("LIST_ADMINS").split(",")))
logging.basicConfig(level=logging.INFO)


def format_data(number: int) -> str:
    number = str(number)
    if len(number) < 2:
        number = "0" + number
    return number


async def send_list(chat, poll_chat, poll_id):
    pass


async def send_poll(chat_id: int, poll_chat: int, poll_id: int) -> None:
    copied_poll_message = await bot.forward_message(chat_id, poll_chat, poll_id)
    inline_kb = InlineKeyboardMarkup(
        inline_keyboard_barkup=[
            [InlineKeyboardButton(text="Получить список",
                                  callback_data=f"list-{copied_poll_message.message_id}")]]
    )

    await copied_poll_message.reply("Чтобы получить список отсутствующих, "
                                    "нажмите на кнопку ниже:", reply_markup=inline_kb)


if __name__ == '__main__':
    if not os.path.exists("last_poll.txt"):
        open("last_poll.txt", "w")

    with open("last_poll.txt", encoding="utf-8") as f:
        poll_chat, poll_id = map(int, f.read().split())

    if datetime.datetime.now().weekday() in (0, 6):
        exit()

    if datetime.datetime.now() < START_DATE:
        exit()

    title = POLL_TITLE
    loop = asyncio.new_event_loop()
    for chat in LIST_ADMINS:
        if chat:
            loop.run_until_complete(send_list(int(chat), poll_chat, poll_id))
