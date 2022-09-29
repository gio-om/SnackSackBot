from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


add_package_button = KeyboardButton("Создать пакет")
make_purchase_button = KeyboardButton("Провести покупку")
back_button = KeyboardButton("Назад")
greeting_kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).row(add_package_button,
                                                                                    make_purchase_button,
                                                                                    back_button)

yes_button = KeyboardButton("Да")
no_button = KeyboardButton("Нет")
conformation_kb = ReplyKeyboardMarkup(resize_keyboard=True).row(yes_button, no_button)
