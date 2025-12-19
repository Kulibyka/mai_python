from aiogram.fsm.state import State, StatesGroup


class AddPlaceStates(StatesGroup):
    name = State()
    category = State()
    address = State()
    description = State()
    price = State()
    confirm = State()


class SearchStates(StatesGroup):
    category = State()
    price = State()
    rating = State()
    query = State()
