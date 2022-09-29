from aiogram.dispatcher.filters.state import StatesGroup, State


class CFSM(StatesGroup):  # Finite State Machine for client's dialog
    show_packages = State()
    choose_package = State()
    choose_order_amount = State()
    approve = State()
