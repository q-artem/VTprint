from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from utils.callback_factory import ChoicePageRangeCallbackFactory


def get_lang_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇷🇺 Русский", callback_data="set_lang:ru")],
        [InlineKeyboardButton(text="🇬🇧 English", callback_data="set_lang:en")]
    ])


def get_admin_panel_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Ссылочки на бота", callback_data="get_referral_links:")],
    ])


def get_print_file_menu_keyboard(_, file_pages_amount, message_with_file_id):
    builder = InlineKeyboardBuilder()
    builder.button(text=_("choice_page_range"), callback_data=ChoicePageRangeCallbackFactory(file_pages_amount=file_pages_amount, message_with_file_id=message_with_file_id))
    builder.adjust(2)
    return builder.as_markup()
