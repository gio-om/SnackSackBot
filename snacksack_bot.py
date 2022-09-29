from aiogram.utils import executor
from create_bot import dp
from handlers import client, partner, general


async def on_startup(_):
    print("Bot is online")


async def on_shutdown(_):
    print("Bot is offline")

general.register_handlers(dp)
partner.register_handlers(dp)
client.register_handlers(dp)

executor.start_polling(dp, skip_updates=True, on_startup=on_startup, on_shutdown=on_shutdown)  # Start pooling
