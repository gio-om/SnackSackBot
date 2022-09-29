from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


client_button = KeyboardButton(text="Клиент")
partner_button = KeyboardButton(text="Партнер")
start_kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).row(client_button, partner_button)
