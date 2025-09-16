from aiogram.fsm.state import StatesGroup, State


class GetPagesState(StatesGroup):
    getting_pages = State()

class PrintStates(StatesGroup):
    # waiting_for_file = State()      # Ожидание загрузки файла
    setting_parameters = State()    # Главное меню настройки параметров
    getting_pages = State()         # Ввод диапазона страниц
    setting_copies = State()        # Ввод количества копий
    setting_orientation = State()   # Выбор ориентации (альбом/портрет)
    confirming = State()            # Подтверждение и печать