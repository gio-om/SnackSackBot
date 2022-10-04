from aiogram import types, Dispatcher
from states.partner_states import MAKE_PURCH_FSM, ADD_PACKAGE_FSM, PFSM
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
from keyboards import partner_kb, general_kb
from create_bot import bot
from database import db
import data


def get_package_info(code):
    order = db.get_order_by_code(code)
    order_info = "Тип пакета: " + order[3] + "\nКод: " + str(order[9]) + "\nКоличество: " + str(order[4]) +\
                 "\nЦена (общая): " + str(order[5] * order[4])
    return order_info


async def command_start(message: types.Message):  # Start partner dialog
    partner_username = message.from_user.username
    if partner_username in db.get_all_partners():  # Check if partner
        print("Partner signed in, waiting text")
        await message.answer(data.partner_greeting, reply_markup=partner_kb.greeting_kb)  # Greeting message
        rules_file = open("rules.txt", "rb")  # File to send
        await bot.send_document(message.from_user.id, document=rules_file)  # Send rules file
        await PFSM.chose_action.set()
    else:
        await message.answer("Вы не зарегистрированный партнер, напишите @gioom1 для регистрации")
        await message.answer(data.general_greeting, reply_markup=general_kb.start_kb)


async def make_purchase_command(message: types.Message):
    await message.answer('Введите код ⬇')
    await MAKE_PURCH_FSM.type_code.set()


async def type_code(message: types.Message, state: FSMContext):
    async with state.proxy() as order:
        order['code'] = int(message.text)
    await message.answer("Выдайте и проведите оплату пакета: " + get_package_info(int(message.text)))  # code
    await message.answer("Если покупатель оплатил заказ, то введите 'Да', иначе 'Нет'")
    await MAKE_PURCH_FSM.approve.set()


async def approve_order(message: types.Message, state: FSMContext):
    async with state.proxy() as order:
        db.complete_order(order['code'])
    await message.answer("Заказ закрыт!", reply_markup=partner_kb.greeting_kb)
    await state.reset_state()


async def cancel_order(message: types.Message, state: FSMContext):
    async with state.proxy() as order:
        db.cancel_order(order['code'])
    await message.answer("Заказ отменен", reply_markup=partner_kb.greeting_kb)
    await state.reset_state()


async def add_package(message: types.Message):
    await message.answer('Введите адресс магазина')
    await ADD_PACKAGE_FSM.address.set()
    # print("add_package")


async def back_command(message: types.Message):
    await message.answer(data.general_greeting, reply_markup=general_kb.start_kb)


async def choose_address(message: types.Message, state: FSMContext):
    async with state.proxy() as data:  # Write address
        data['address'] = message.text

    await message.answer('Введите тип пакета')
    await ADD_PACKAGE_FSM.type.set()


async def choose_type(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['type'] = message.text

    await message.answer('Введите количество пакетов')
    await ADD_PACKAGE_FSM.amount.set()


async def choose_amount(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['amount'] = int(message.text)

    await message.answer('Введите цену за пакет')
    await ADD_PACKAGE_FSM.price.set()


async def choose_price(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['price'] = int(message.text)

    await message.answer('Введите время, до которого можно забрать пакет в формате ГГГГ-ММ-ДД ЧЧ:ММ')
    await ADD_PACKAGE_FSM.time.set()


async def choose_time(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['time'] = message.text
        data['telegram_id'] = message.from_user.id
        await message.answer('Адрес: {address}\nТип пакета: {type}\nКоличество: {amount}\nЦена: {price}\nВремя: {time}'.
                            format(address=data['address'],
                            type=data['type'],
                            amount=data['amount'],
                            price=data['price'],
                            time=data['time']))

    await message.answer('Добавить этот пакет? (Да/Нет)', reply_markup=partner_kb.conformation_kb)
    await ADD_PACKAGE_FSM.conformation.set()


async def confirm_package_command(message: types.Message, state: FSMContext):
    await db.add_package(state)
    await message.answer('Пакет добавлен в БД. Вы можете добавить еще один пакет, либо провести покупку.',
                         reply_markup=partner_kb.greeting_kb)
    await state.reset_state()
    await PFSM.chose_action.set()


async def decline_package_command(message: types.Message, state: FSMContext):
    await state.reset_state()
    await message.answer(data.partner_greeting, reply_markup=partner_kb.greeting_kb)
    await PFSM.chose_action.set()


def register_handlers(dp: Dispatcher):
    dp.register_message_handler(command_start, Text(equals="Партнер"), state="*")
    dp.register_message_handler(back_command, Text(equals="Назад"), state=PFSM.chose_action)
    dp.register_message_handler(make_purchase_command, Text(equals="Провести покупку"), state=PFSM.chose_action)
    dp.register_message_handler(add_package, Text(equals="Создать пакет"), state=PFSM.chose_action)

    # Handlers to add a package
    dp.register_message_handler(choose_address, state=ADD_PACKAGE_FSM.address)
    dp.register_message_handler(choose_type, state=ADD_PACKAGE_FSM.type)
    dp.register_message_handler(choose_amount, state=ADD_PACKAGE_FSM.amount)
    dp.register_message_handler(choose_price, state=ADD_PACKAGE_FSM.price)
    dp.register_message_handler(choose_time, state=ADD_PACKAGE_FSM.time)
    dp.register_message_handler(confirm_package_command, Text(equals="Да", ignore_case=True),
                                state=ADD_PACKAGE_FSM.conformation)
    dp.register_message_handler(decline_package_command, Text(equals="Нет", ignore_case=True),
                                state=ADD_PACKAGE_FSM.conformation)

    # Handlers to make purchase
    dp.register_message_handler(type_code, state=MAKE_PURCH_FSM.type_code)
    dp.register_message_handler(approve_order, Text(equals="Да", ignore_case=True), state=MAKE_PURCH_FSM.approve)
    dp.register_message_handler(cancel_order, Text(equals="Нет", ignore_case=True), state=MAKE_PURCH_FSM.approve)
