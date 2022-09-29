from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage


TOKEN = '5605681547:AAFUii4kERDSRzBuHLQaa681r3NRqlOXuKg'  # Token of bot
storage = MemoryStorage()

bot = Bot(token=TOKEN)  # Create Bot
dp = Dispatcher(bot, storage=storage)  # Create Dispatcher
