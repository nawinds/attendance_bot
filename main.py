import logging
import os
import asyncio
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types.chat import ChatType as ct


API_TOKEN = os.getenv("TOKEN")
BOT_ADMIN_ID = os.getenv("ADMIN_ID")


async def is_admin(message: types.Message) -> bool:
    admins = [member.user.id for member in await message.bot.get_chat_administrators(message.chat.id)]
    return message.from_user.id == BOT_ADMIN_ID or message.from_user.id in admins


logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start', 'help'], chat_type=[ct.PRIVATE])
async def help_command(message: types.Message):
    """
    This handler will be called when user sends `/start` or `/help` command
    """
    await message.reply("Hi!\nI'm EchoBot!\nPowered by aiogram.")


@dp.message_handler(is_admin, commands=["poll"],
                    chat_type=[ct.GROUP, ct.SUPERGROUP, ct.SUPER_GROUP])
async def poll(message: types.Message):
    options = [
        "Буду в школе",
        "Не приду",
        "Посмотреть результаты"
    ]
    await message.answer_poll("day?", options=options,
                              is_anonymous=False, allows_multiple_answers=False)


@dp.message_handler(is_admin, commands=["delete"],
                    chat_type=[ct.GROUP, ct.SUPERGROUP, ct.SUPER_GROUP])
async def delete(message: types.Message):
    await message.reply_to_message.delete()


@dp.message_handler(lambda message: not is_admin(message), commands=["poll", "delete"],
                    chat_type=[ct.GROUP, ct.SUPERGROUP, ct.SUPER_GROUP])
async def non_admins(message: types.Message):
    answer = await message.reply("Извините, но использовать эту команду могут только админы.\n\n"
                                 "Чтобы узнать подробнее о том, что я умею, отправьте мне команду "
                                 "/help в *личном* сообщении",
                                 disable_notification=True)
    await asyncio.sleep(5)
    await answer.delete()


@dp.message_handler(commands=["poll", "delete"],
                    chat_type=[ct.PRIVATE])
async def non_groups(message: types.Message):
    answer = await message.reply("Извините, но использовать эту команду можно только в группах.\n\n"
                                 "Чтобы узнать подробнее о том, что я умею, отправьте мне команду "
                                 "/help в *личном* сообщении",
                                 disable_notification=True)
    await asyncio.sleep(5)
    await answer.delete()


if __name__ == '__main__':
    executor.start_polling(dp)
