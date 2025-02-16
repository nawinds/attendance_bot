import logging
import os
import datetime
import asyncio
from main import POLL_TITLE, POLL_OPTIONS, MAIN_GROUP_ID, bot

START_DATE = datetime.datetime(year=2023, month=2, day=26)
WEEKDAY_NAMES = ["понедельник", "вторник", "среда", "четверг", "пятница", "суббота", "воскресенье"]

logging.basicConfig(level=logging.INFO)


def format_data(number: int) -> str:
    number = str(number)
    if len(number) < 2:
        number = "0" + number
    return number


async def send_poll(chat_id: int, question: str, options: list[str]) -> None:
    poll = await bot.send_poll(chat_id, question, options=options,
                               is_anonymous=False, allows_multiple_answers=False)
    if chat_id == MAIN_GROUP_ID:
        with open("last_poll.txt", "w", encoding="utf-8") as wf:
            wf.write(f"{chat_id} {poll.message_id}")


async def main():
    if not os.path.exists("group_chats.txt"):
        open("group_chats.txt", "w")

    with open("group_chats.txt", encoding="utf-8") as f:
        group_chats = f.read().split(",")

    week = datetime.datetime.now().isocalendar().week
    if week % 2 == 0:
        if datetime.datetime.now().weekday() not in (0, 4):
            exit()
    else:
        if datetime.datetime.now().weekday() not in (2, 4):
            exit()

    if datetime.datetime.now() < START_DATE:
        exit()

    # target_day = datetime.datetime.now()
    # if target_day.hour > 15:
    #    target_day = target_day + datetime.timedelta(days=1)
    # weekday = WEEKDAY_NAMES[target_day.weekday()].capitalize()
    # title = f"{weekday}, {format_data(target_day.day)}.{format_data(target_day.month)}"

    title = POLL_TITLE
    for chat in group_chats:
        if chat:
            await send_poll(int(chat), title, POLL_OPTIONS)

    await bot.session.close()


if __name__ == '__main__':
    asyncio.run(main())