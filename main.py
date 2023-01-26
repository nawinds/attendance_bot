import logging
import os
import asyncio
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types.chat import ChatType as ct


API_TOKEN = os.getenv("TOKEN")
BOT_ADMIN_ID = os.getenv("ADMIN_ID")

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


async def is_admin(message: types.Message) -> bool:
    admins = [member.user.id for member in await message.bot.get_chat_administrators(message.chat.id)]
    return message.from_user.id == BOT_ADMIN_ID or message.from_user.id in admins


async def not_admin(message: types.Message) -> bool:
    return not await is_admin(message)


async def bot_joined(event: types.chat_member_updated.ChatMemberUpdated) -> bool:
    return event.new_chat_member.user.id == dp.bot.id and \
           event.new_chat_member.status == "member"


@dp.my_chat_member_handler(bot_joined)
async def chat_member(event: types.chat_member_updated.ChatMemberUpdated):
    await bot.send_message(event.chat.id, "Всем привет!")


@dp.message_handler(commands=['start', 'help'], chat_type=[ct.PRIVATE])
async def help_command(message: types.Message):
    """
    This handler will be called when user sends `/start` or `/help` command
    """
    await message.reply("Hi!\nI'm EchoBot!\nPowered by aiogram.")


@dp.message_handler(is_admin, commands=["poll"],
                    chat_type=[ct.GROUP, ct.SUPERGROUP])
async def poll(message: types.Message):
    options = [
        "Буду в школе",
        "Не приду",
        "Посмотреть результаты"
    ]
    await message.answer_poll("day?", options=options,
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
