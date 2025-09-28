from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from utils.callback_factory import ChoicePageRangeCallbackFactory, \
    CancelPrintFileCallbackFactory, ConfirmPrintFileCallbackFactory, ChoiceAmountCopiesCallbackFactory

from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext



def get_lang_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇷🇺 Русский", callback_data="set_lang:ru")],
        [InlineKeyboardButton(text="🇬🇧 English", callback_data="set_lang:en")]
    ])


def get_admin_panel_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Ссылочки на бота", callback_data="get_referral_links:")],
    ])


def get_print_file_menu_keyboard(_):
    builder = InlineKeyboardBuilder()
    builder.button(text=_("choice_page_range"),
                   callback_data=ChoicePageRangeCallbackFactory())
    builder.button(text=_("choice_copies_amount"),
                   callback_data=ChoiceAmountCopiesCallbackFactory())
    builder.button(text=_("accept_print"),
                   callback_data=ConfirmPrintFileCallbackFactory())
    builder.button(text=_("cancel_print"), callback_data=CancelPrintFileCallbackFactory())
    builder.adjust(1)
    return builder.as_markup()

def get_cancel_keyboard(_, callback_factory: CallbackData):
    builder = InlineKeyboardBuilder()
    builder.button(text=_("cancel"), callback_data=callback_factory)
    return builder.as_markup()

def get_confirm_print_file_keyboard(_):
    builder = InlineKeyboardBuilder()
    builder.button(text=_("confirm_print_file"), callback_data=ConfirmPrintFileCallbackFactory())
    builder.button(text=_("cancel"), callback_data=CancelPrintFileCallbackFactory())
    return builder.as_markup()