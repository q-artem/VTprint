from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from utils.callback_factory import ChoicePageRangeCallbackFactory, AcceptPrintFileCallbackFactory, \
    CancelPrintFileCallbackFactory


def get_lang_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇷🇺 Русский", callback_data="set_lang:ru")],
        [InlineKeyboardButton(text="🇬🇧 English", callback_data="set_lang:en")]
    ])


def get_admin_panel_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Ссылочки на бота", callback_data="get_referral_links:")],
    ])


def get_print_file_menu_keyboard(_, pages_total, message_with_file_id, pages_ranges: str = ""):
    builder = InlineKeyboardBuilder()
    builder.button(text=_("choice_page_range"),
                   callback_data=ChoicePageRangeCallbackFactory())
    builder.button(text=_("accept_print"),
                   callback_data=AcceptPrintFileCallbackFactory(pages_total=pages_total,
                                                                message_with_file_id=message_with_file_id,
                                                                pages_ranges=pages_ranges))
    builder.button(text=_("cancel_print"), callback_data=CancelPrintFileCallbackFactory())
    builder.adjust(2)
    return builder.as_markup()
