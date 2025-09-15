from aiogram.fsm.state import StatesGroup, State


class GetPagesState(StatesGroup):
    getting_pages = State()