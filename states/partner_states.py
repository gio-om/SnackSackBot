from aiogram.dispatcher.filters.state import StatesGroup, State


class PFSM(StatesGroup):  # Finite State Machine for partner's dialog
    chose_action = State()


class MAKE_PURCH_FSM(StatesGroup):
    type_code = State()
    approve = State()


class ADD_PACKAGE_FSM(StatesGroup):
    address = State()
    type = State()
    amount = State()
    price = State()
    time = State()
    conformation = State()
