from aiogram import types, Dispatcher
from states.client_states import CFSM
from aiogram.dispatcher.filters import Text
from database import db
from keyboards import client_kb, general_kb
from aiogram.dispatcher import FSMContext
from create_bot import bot
import data


async def command_start(message: types.Message):
    print("Client signed in, waiting text")
    await CFSM.show_packages.set()
    await message.answer(data.client_greeting.format(name=message.from_user.first_name),
                         reply_markup=client_kb.main_kb)  # Greeting message


def get_packages_info(packages):
    answer = ""
    cur_num = 1
    for pack in packages:
        # print(pack)
        answer = answer + str(cur_num) + ". Адрес: " + pack[1] + "\nОписание(тип пакета): " + pack[2] + \
                 "\nВремя: " + pack[5] + "\nКоличество: " + str(pack[3]) + "\nЦена за 1 пакет: " + str(pack[4]) \
                 + "\n\n"
        cur_num = cur_num + 1
    return answer


def get_order_info(pack, amount):
    answer = "Адрес: " + pack[1] + "\nОписание(тип пакета): " + pack[2] + \
             "\nВремя: " + pack[5] + "\nКоличество: " + str(amount) + "\nЦена за 1 пакет: " + str(pack[4]) \
             + "\n\n"
    return answer


async def show_packages(message: types.Message):
    packages = db.get_all_packages()
    # print(packages)
    packages_info = get_packages_info(packages)
    await message.answer(packages_info + "Выберите пакет, который хотите забрать",
                         reply_markup=client_kb.get_choose_pack_kb(len(packages), packages))
    await CFSM.choose_package.set()


async def back_command(message: types.Message):
    await message.answer(data.general_greeting, reply_markup=general_kb.start_kb)


async def call_back(callback: types.CallbackQuery):
    await CFSM.show_packages.set()
    await bot.send_message(callback.from_user.id, data.client_greeting.format(name=callback.from_user.first_name),
                           reply_markup=client_kb.main_kb)  # Greeting message


async def call_package(callback: types.CallbackQuery, state: FSMContext):
    await bot.send_message(callback.from_user.id, 'Введите число пакетов, которые хотите забрать')
    async with state.proxy() as data:
        # print(callback.data)
        data['package_id'] = int(callback.data[len('chose'):])
        # print(data['package_id'])
    await CFSM.choose_order_amount.set()


async def choose_order_amount(message: types.Message, state: FSMContext):
    is_correct = True
    for i in message.text:
        if not i.isdigit():
            is_correct = False
            break
    async with state.proxy() as order:
        package_id = order['package_id']
    if is_correct and int(message.text) <= db.get_package_amount(package_id):
        async with state.proxy() as order:
            order['amount'] = int(message.text)
        await message.answer("Отправьте 'Да' для подтверждения")
        await CFSM.approve.set()
    else:
        await message.answer(data.not_a_number)


async def approve_order(message: types.Message, state: FSMContext):
    if message.text == "Да":
        async with state.proxy() as order:
            code = db.create_order_code(order['package_id'], message.from_user.id)
            db.decrease_package(order["package_id"], order["amount"])
            db.add_order(order['package_id'], order["amount"], str(message.from_user.id), int(code))
            await message.answer("Ваш код для получения заказа: " + code)
        await message.answer(data.client_goodbye.format(name=message.from_user.first_name), reply_markup=client_kb.main_kb)
        await notify_package_owner(order["package_id"], order["amount"])
    else:
        await message.answer("Вы можете узнать еще раз о проекте", reply_markup=client_kb.main_kb)
        await CFSM.show_packages.set()


async def notify_package_owner(package_id, amount):
    await bot.send_message(db.get_package_owner_id(package_id), "Вам поступил заказ: "
                           + get_order_info(db.get_package_by_id(package_id), amount))


def register_handlers(dp: Dispatcher):
    dp.register_message_handler(command_start, Text(equals="Клиент"), state="*")
    dp.register_message_handler(show_packages, Text(equals="Показать пакеты"), state=CFSM.show_packages)
    dp.register_message_handler(back_command, Text(equals="Назад"), state="*")
    dp.register_callback_query_handler(call_back, text="back", state="*")
    dp.register_callback_query_handler(call_package, Text(startswith="chose"), state=CFSM.choose_package)
    dp.register_message_handler(choose_order_amount, state=CFSM.choose_order_amount)
    dp.register_message_handler(approve_order, state=CFSM.approve)
