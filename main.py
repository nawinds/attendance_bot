import logging
import os
import asyncio
import sys
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from aiogram import F

# import datetime

TOKEN = os.getenv("TOKEN")
BOT_ADMIN_ID = int(os.getenv("ADMIN_ID"))
MAIN_GROUP_ID = int(os.getenv("MAIN_GROUP_ID"))
ADMIN_RIGHTS_ONLY = bool(int(os.getenv("ADMIN_RIGHTS_ONLY", 1)))

WEEKDAY_NAMES = ["понедельник", "вторник", "среда", "четверг", "пятница", "суббота"]
POLL_TITLE = "Кто придет на пару Сарычева?"
POLL_OPTIONS = [
    "Буду",
    "Не приду"
]

logging.basicConfig(level=logging.INFO)
dp = Dispatcher()
bot = Bot(TOKEN)

if not os.path.exists("group_chats.txt"):
    open("group_chats.txt", "w")


async def is_admin(message: types.Message) -> bool:
    if type(message) != types.message.Message:
        return False
    if message.chat.type == 'private':
        return int(message.from_user.id) == BOT_ADMIN_ID
    if not ADMIN_RIGHTS_ONLY:
        return True
    admins = [member.user.id for member in await message.bot.get_chat_administrators(
        message.chat.id)]
    return int(message.from_user.id) == BOT_ADMIN_ID or message.from_user.id in admins


async def not_admin(message: types.Message) -> bool:
    return not await is_admin(message)


async def bot_joined(event: types.chat_member_updated.ChatMemberUpdated) -> bool:
    if event.new_chat_member.user.id == bot.id:
        with open("group_chats.txt", encoding="utf-8") as rf:
            group_chats = rf.read().split(",")
            with open("group_chats.txt", "w", encoding="utf-8") as f:
                if event.new_chat_member.status in ("member", "administrator"):
                    f.write(",".join(group_chats + [str(event.chat.id)]))
                    return True
                elif str(event.chat.id) in group_chats:
                    group_chats.remove(str(event.chat.id))
                f.write(",".join(group_chats))
    return False


@dp.my_chat_member(bot_joined)
async def chat_member(event: types.chat_member_updated.ChatMemberUpdated):
    await bot.send_message(event.chat.id, "Всем привет!\n\n"
                                          "Это бот, который отправляет опросы про посещение "
                                          "утром учебного дня. "
                                          "Чтобы узнать подробнее о возможностях бота, "
                                          "отправьте мне команду /help в *личном* сообщении",
                           parse_mode="markdown")


@dp.message(Command("help"), F.chat.func(lambda chat: chat.type == "private"))
@dp.message(Command("start"), F.chat.func(lambda chat: chat.type == "private"))
async def help_command(message: types.Message):
    """
    This handler will be called when user sends `/start` or `/help` command
    """
    await message.answer(f"Здравствуйте!\n\nЭто бот, который утром учебного дня "
                         f"отправляет опросы про посещение на следующий день. Ниже список команд"
                         f"{', доступных админам чатов' if ADMIN_RIGHTS_ONLY else ''}. "
                         f"Эти команды работают только в группах.\n\n"
                         f"/poll – отправить опрос про посещаемость (не по расписанию, вручную)\n"
                         f"/delete – удалить сообщение (например, опрос), отправленное ботом. "
                         f"Эту команду нужно отправлять в ответ на сообщение.\n\n"
                         f"[Исходный код бота здесь]"
                         f"(https://github.com/nawinds/poll_sender_bot)\n\n"
                         f"_Любые вопросы, предложения пишите @nawinds. С удовольствием отвечу!_",
                         parse_mode="markdown", disable_web_page_preview=True)


@dp.message(is_admin, Command("poll"), F.chat.func(lambda chat:
                                                   chat.type in {"group", "supergroup"}))
async def poll(message: types.Message):
    # def format_data(number: int) -> str:
    #     number = str(number)
    #     if len(number) < 2:
    #         number = "0" + number
    #     return number

    # target_day = datetime.datetime.now()
    # if target_day.hour > 15:
    #     target_day = target_day + datetime.timedelta(days=1)
    # weekday = WEEKDAY_NAMES[target_day.weekday()].capitalize()
    # title = f"{weekday}, {format_data(target_day.day)}.{format_data(target_day.month)}"
    title = POLL_TITLE
    poll_message = await message.answer_poll(title, options=POLL_OPTIONS,
                                             is_anonymous=False, allows_multiple_answers=False)
    await message.delete()
    if message.chat.id == MAIN_GROUP_ID:
        with open("last_poll.txt", "w", encoding="utf-8") as wf:
            wf.write(f"{poll_message.chat.id} {poll_message.message_id}")


@dp.message(is_admin, Command("delete"), F.chat.func(lambda chat:
                                                     chat.type in {"group", "supergroup"}))
async def delete(message: types.Message):
    if not message.reply_to_message:
        answer = await message.reply("Отправлять эту команду нужно в ответ на опрос, "
                                     "отправленный этим ботом", disable_notification=True)
        await asyncio.sleep(10)
        await answer.delete()
        await message.delete()
        return
    await message.reply_to_message.delete()
    await message.delete()


@dp.message(not_admin, Command("poll"), F.chat.func(lambda chat:
                                                    chat.type in {"group", "supergroup"}))
@dp.message(not_admin, Command("delete"),
            F.chat.func(lambda chat: chat.type == chat.type in {"group", "supergroup"}))
async def non_admins(message: types.Message):
    answer = await message.reply("Извините, но использовать эту команду могут только админы.\n\n"
                                 "Чтобы узнать подробнее о том, что я умею, отправьте мне команду "
                                 "/help в *личном* сообщении",
                                 disable_notification=True, parse_mode="markdown")
    await asyncio.sleep(10)
    await answer.delete()
    await message.delete()


@dp.message(Command("poll"), F.chat.func(lambda chat: chat.type == "private"))
@dp.message(Command("delete"), F.chat.func(lambda chat: chat.type == "private"))
async def non_groups(message: types.Message):
    await message.reply("Извините, но использовать эту команду можно только в группах.\n\n"
                        "Чтобы узнать подробнее о том, что я умею, отправьте мне команду "
                        "/help в *личном* сообщении", parse_mode="markdown")


@dp.message(Command("help"), F.chat.func(lambda chat: chat.type in {"group", "supergroup"}))
async def non_private(message: types.Message):
    answer = await message.reply("Извините, но использовать эту команду можно только в "
                                 "личном чате, чтобы не засорять группу", parse_mode="markdown")
    await asyncio.sleep(10)
    await answer.delete()
    await message.delete()


# @dp.callback_query(F.data.startswith("list "))
# async def poll_callback(callback_query: types.CallbackQuery):
#     poll_chat, poll_id = map(int, callback_query.data.split()[1].split("_"))
#     poll = await bot.forward_message(callback_query.from_user.id, poll_chat, poll_id)
#     answers = poll.poll.options
#     for option in answers:
#         print(f"{option.text}: {option} votes")
#     await poll.delete()


async def main() -> None:
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
