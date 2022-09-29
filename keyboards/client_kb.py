from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


show_packages_button = KeyboardButton("Показать пакеты")
info_button = KeyboardButton("Информация")
back_button = KeyboardButton("Назад")
main_kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).row(show_packages_button,
                                                                                info_button, back_button)


def get_choose_pack_kb(n, packages_info):
    kb = InlineKeyboardMarkup(row_width=5)
    for i in range(n):
        # print(packages_info[i])
        kb.insert(InlineKeyboardButton(str(i + 1), callback_data="chose " + str(packages_info[i][0])))
    kb.add(InlineKeyboardButton("Назад", callback_data="back"))
    return kb
