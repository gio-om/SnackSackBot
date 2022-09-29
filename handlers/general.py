from aiogram import types, Dispatcher
from database import db
from keyboards import general_kb
import data


async def command_start(message: types.Message):
    await message.answer(data.general_greeting, reply_markup=general_kb.start_kb)
    await db.connect_to_database()


def register_handlers(dp: Dispatcher):
    dp.register_message_handler(command_start, commands=['start', 'help'], state="*")
