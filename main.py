import logging
import os
import asyncio
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types.chat import ChatType as ct
import datetime

API_TOKEN = os.getenv("TOKEN")
BOT_ADMIN_ID = os.getenv("ADMIN_ID")

WEEKDAY_NAMES = ["понедельник", "вторник", "среда", "четверг", "пятница", "суббота"]

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

if not os.path.exists("group_chats.txt"):
    open("group_chats.txt", "w")


async def is_admin(message: types.Message) -> bool:
    admins = [member.user.id for member in await message.bot.get_chat_administrators(message.chat.id)]
    return message.from_user.id == BOT_ADMIN_ID or message.from_user.id in admins


async def not_admin(message: types.Message) -> bool:
    return not await is_admin(message)


async def bot_joined(event: types.chat_member_updated.ChatMemberUpdated) -> bool:
    if event.new_chat_member.user.id == dp.bot.id:
        with open("group_chats.txt", encoding="utf-8") as rf:
            group_chats = rf.read().split(",")
        with open("group_chats.txt", "w", encoding="utf-8") as f:
            if event.new_chat_member.status == "member":
                f.write(",".join(group_chats + [str(event.chat.id)]))
                return True
            elif event.chat.id in group_chats:
                group_chats.remove(event.chat.id)
                f.write(",".join(group_chats))
    return False


@dp.my_chat_member_handler(bot_joined)
async def chat_member(event: types.chat_member_updated.ChatMemberUpdated):
    await bot.send_message(event.chat.id, "Всем привет!\n\n"
                                          "Это бот, который отправляет опросы про посещение "
                                          "каждый вечер накануне учебного дня. "
                                          "Чтобы узнать подробнее о возможностях бота, "
                                          "отправьте мне команду /help в *личном* сообщении",
                           parse_mode="markdown")


@dp.message_handler(commands=['start', 'help'], chat_type=[ct.PRIVATE])
async def help_command(message: types.Message):
    """
    This handler will be called when user sends `/start` or `/help` command
    """
    await message.answer("Здравствуйте!\n\nЭто бот, который каждый вечер накануне учебного дня "
                         "отправляет опросы про посещение школы. Ниже список команд, "
                         "доступных админам чатов. Эти команды работают только в группах.\n\n"
                         "/poll – отправить опрос про посещаемость (не по расписанию, вручную)\n"
                         "/delete – удалить сообщение (например, опрос), отправленное ботом. "
                         "Эту команду нужно отправлять в ответ на сообщение.\n\n"
                         "[Исходный код бота здесь](https://github.com/nawinds/poll_sender_bot)\n\n"
                         "_Любые вопросы, предложения пишите на me@nawinds.top. С удовольствием отвечу!_",
                         parse_mode="markdown", disable_web_page_preview=True)


@dp.message_handler(is_admin, commands=["poll"],
                    chat_type=[ct.GROUP, ct.SUPERGROUP])
async def poll(message: types.Message):
    options = [
        "Буду в школе",
        "Не приду",
        "Посмотреть результаты"
    ]

    def format_data(number: int) -> str:
        number = str(number)
        if len(number) < 2:
            number = "0" + number
        return number

    target_day = datetime.datetime.now()
    if target_day.hour > 15:
        target_day = target_day + datetime.timedelta(days=1)
    weekday = WEEKDAY_NAMES[target_day.weekday()].capitalize()
    title = f"{weekday}, {format_data(target_day.day)}.{format_data(target_day.month)}"
    await message.answer_poll(title, options=options,
                              is_anonymous=False, allows_multiple_answers=False)


@dp.message_handler(is_admin, commands=["delete"],
                    chat_type=[ct.GROUP, ct.SUPERGROUP])
async def delete(message: types.Message):
    if not message.reply_to_message:
        answer = await message.reply("Отправлять эту команду нужно в ответ на опрос, "
                                     "отправленный этим ботом", disable_notification=True)
        await asyncio.sleep(10)
        await answer.delete()
        return
    await message.reply_to_message.delete()


@dp.message_handler(not_admin, commands=["poll", "delete"],
                    chat_type=[ct.GROUP, ct.SUPERGROUP])
async def non_admins(message: types.Message):
    answer = await message.reply("Извините, но использовать эту команду могут только админы.\n\n"
                                 "Чтобы узнать подробнее о том, что я умею, отправьте мне команду "
                                 "/help в *личном* сообщении",
                                 disable_notification=True, parse_mode="markdown")
    await asyncio.sleep(10)
    await answer.delete()


@dp.message_handler(commands=["poll", "delete"],
                    chat_type=[ct.PRIVATE])
async def non_groups(message: types.Message):
    await message.reply("Извините, но использовать эту команду можно только в группах.\n\n"
                        "Чтобы узнать подробнее о том, что я умею, отправьте мне команду "
                        "/help в *личном* сообщении", parse_mode="markdown")


if __name__ == '__main__':
    executor.start_polling(dp)
