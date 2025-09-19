import html

from aiogram import types
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import User
from utils.FSM_data_classes import PrintData
from utils.FSM_utils import get_user_data


async def validate_pages_ranges(message: types.Message, _) -> bool:
    if len(message.text) > 100:
        await message.answer(_("too_much_length_of_range_of_pages"))
        return False
    pages = message.text.split(",")
    last_number = 0
    if set(message.text) - set("0123456789,-"):
        await message.answer(_("wrong_range_of_pages"))
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
        return True
    await message.answer(_("wrong_range_of_pages"))
    return False


async def count_pages(pages_ranges: str) -> int:
    pages = pages_ranges.split(",")
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
        pages_to_print = user_data.pages_to_print

        pages_available = (await session.get(User, user_id)).pages_left

        _str = ""
        if prefix:
            _str += prefix + "\n\n"

        if file_name:
            _str += _("file_name").format(html.escape(file_name)) + "\n"
        if file_size_converted:
            _str += _("file_size").format(file_size_converted) + "\n"
        if pages_total:
            _str += _("pages_amount").format(str(pages_total)) + "\n"

        _str += "\n"
        if pages_ranges:
            print(pages_ranges)
            _str += _("pages_ranges").format(pages_ranges) + "\n"
        if pages_to_print:
            _str += _("pages_to_print").format(str(pages_to_print)) + "\n"

        _str += "\n"
        if pages_available:
            _str += "<b>" + _("pages_available").format(str(pages_available), str(pages_available - pages_to_print)) + "</b>" + "\n"
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
