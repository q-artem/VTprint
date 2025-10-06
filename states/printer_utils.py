import html

from aiogram import types
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import User
from utils.FSM_data_classes import PrintData
from utils.FSM_utils import get_user_data
from utils.callback_factory import CanselEnterPagesRangesCallbackFactory, \
    CancelChoiceAmountCopiesCallbackFactory
from utils.keyboards import get_cancel_keyboard


async def validate_pages_ranges(_, message: types.Message, pages_total: int) -> bool:
    if len(message.text) > 100:
        await message.answer(_("too_much_length_of_range_of_pages"), reply_markup=get_cancel_keyboard(_, CanselEnterPagesRangesCallbackFactory()))
        return False
    pages = message.text.replace(" ", "").split(",")
    last_number = 0
    if set(message.text) - set("0123456789,- "):
        await message.answer(_("wrong_range_of_pages"), reply_markup=get_cancel_keyboard(_, CanselEnterPagesRangesCallbackFactory()))
        return False
    for q in pages:
        if "-" in q:
            try:
                start, end = map(int, q.split("-"))
                if int(start) >= int(end) or int(start) <= last_number:
                    break
                last_number = int(end)
            except Exception as e:
                break
        else:
            try:
                if int(q) <= last_number:
                    break
                last_number = int(q)
            except Exception as e:
                break
    else:
        if last_number > pages_total:
            await message.answer(_("wrong_range_of_pages"), reply_markup=get_cancel_keyboard(_, CanselEnterPagesRangesCallbackFactory()))
            return False
        return True
    await message.answer(_("wrong_range_of_pages"), reply_markup=get_cancel_keyboard(_, CanselEnterPagesRangesCallbackFactory()))
    return False


async def count_pages(pages_ranges: str) -> int:
    pages = pages_ranges.replace(" ", "").split(",")
    count = 0
    for q in pages:
        if "-" in q:
            start, end = map(int, q.split("-"))
            count += end - start + 1
        else:
            count += 1
    return count


async def build_file_info_message(_, state: FSMContext, session: AsyncSession, user_id: int, prefix: str | None = None) -> str:
    async with get_user_data(state, PrintData) as user_data:
        file_id = user_data.file_id
        file_name = user_data.file_name
        file_size_converted = user_data.file_size_converted
        pages_total = user_data.pages_total

        pages_ranges = user_data.pages_ranges
        copies_amount = user_data.copies
        pages_to_print = user_data.pages_to_print

        pages_available = (await session.get(User, user_id)).pages_left

        _str = ""
        if prefix:
            _str += prefix + "\n\n"

        if file_name:
            _str += _("file_name").format(file_name) + "\n"
        if file_size_converted:
            _str += _("file_size").format(file_size_converted) + "\n"
        if pages_total:
            _str += _("pages_amount").format(str(pages_total)) + "\n"

        _str += "\n"
        if pages_ranges:
            _str += _("pages_ranges").format(pages_ranges) + "\n"
        if copies_amount != 1:
            _str += _("copies_amount").format(copies_amount) + "\n"
        if pages_to_print:
            _str += _("pages_to_print").format(str(pages_to_print)) + "\n"

        _str += "\n"
        if pages_available:
            pages_left = pages_available - pages_to_print
            if pages_left >= 0:
                _str += _("pages_available").format(str(pages_available), str(pages_left)) + "\n"
            else:
                _str += _("you_are_not_enough_pages_set_range_or_try_later").format(str(-pages_left)) + "\n"
        _str += _("sure_to_print_or_change_params")

        return _str


async def convert_file_size(file_size: int) -> str:
    if file_size:
        if file_size < 700:
            file_size = str(file_size) + " B"
        elif file_size < 700 * 1024:
            file_size = str(round(file_size / 1024, 2)) + " KB"
        else:
            file_size = str(round(file_size / 1024 / 1024, 2)) + " MB"
    return file_size

async def validate_copies_amount(_, message: types.Message) -> bool:
    try:
        copies = int(message.text)
    except ValueError as e:
        await message.answer(_("please_enter_int"), reply_markup=get_cancel_keyboard(_, CancelChoiceAmountCopiesCallbackFactory()))
        return False
    if copies < 1 or copies > 100:
        await message.answer(_("int_must_be_between_1_and_100"), reply_markup=get_cancel_keyboard(_, CancelChoiceAmountCopiesCallbackFactory()))
        return False
    return True

async def check_access_to_print(_, state: FSMContext, session: AsyncSession, user_id: int) -> bool:
    pages_left = (await session.get(User, user_id)).pages_left
    async with get_user_data(state, PrintData) as user_data:
        if user_data.pages_to_print > pages_left:
            return False
        return True