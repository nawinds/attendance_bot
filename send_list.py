import logging
import os
import datetime
import asyncio
from main import bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from send_poll import START_DATE

LIST_ADMINS = list(map(int, os.getenv("LIST_ADMINS").split(",")))
logging.basicConfig(level=logging.INFO)


def format_data(number: int) -> str:
    number = str(number)
    if len(number) < 2:
        number = "0" + number
    return number


async def send_list():
    with open("last_poll.txt", encoding="utf-8") as f:
        poll_chat, poll_id = map(int, f.read().split())

    for chat in LIST_ADMINS:
        if chat:
            await send_poll(int(chat), poll_chat, poll_id)


async def send_poll(chat_id: int, poll_chat: int, poll_id: int) -> None:
    copied_poll_message = await bot.forward_message(chat_id, poll_chat, poll_id)
    # inline_kb = InlineKeyboardMarkup(
    #     inline_keyboard=[
    #         [InlineKeyboardButton(text="Получить список",
    #                               callback_data=f"list {poll_chat}_{poll_id}")]]
    # )
    #
    # await copied_poll_message.reply("Чтобы получить список отсутствующих, "
    #                                 "нажмите на кнопку ниже:", reply_markup=inline_kb)


async def main():
    if not os.path.exists("last_poll.txt"):
        open("last_poll.txt", "w")

    if datetime.datetime.now().weekday() not in (1, 4):
        exit()

    if datetime.datetime.now() < START_DATE:
        exit()

    await send_list()
    await bot.session.close()


if __name__ == '__main__':
    asyncio.run(main())