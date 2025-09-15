import html
from venv import logger

from aiogram import Router, Bot, F, types
from aiogram.enums import ContentType
import tempfile

from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from pypdf import PdfReader
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import User
from main import DEBUG
from asyncio import create_subprocess_exec

from utils.FSM import GetPagesState
from utils.callback_factory import ChoicePageRangeCallbackFactory
from utils.keyboards import get_print_file_menu_keyboard

router = Router()


@router.message(F.content_type == ContentType.DOCUMENT)
async def handle_document(message: types.Message, bot: Bot, session: AsyncSession, _):
    assert message.document is not None  # на всякий случайэ

    if not (message.document.file_name.endswith(".pdf") and message.document.mime_type == "application/pdf"):
        await message.reply(_("file_is_not_pdf"))
        return

    if message.document.file_size > 20 * 1024 * 1024 - 1:
        await message.reply(_("file_is_too_big_max_is_20mb"))
        return

    wait_message = None
    if message.document.file_size > 2 * 1024 * 1024:
        wait_message = await message.answer(_("processing_file"))

    with tempfile.NamedTemporaryFile("wb") as file:
        await bot.download(message.document.file_id, file.name)              ##########################

        file_name = file.name
        pages_pdf = len(PdfReader(file).pages)

        file_info = await build_file_info_message(_, file_name, message.document.file_size, pages_pdf, pages_available=(await session.get(User, message.from_user.id)).pages_amount)
        if wait_message:
            await wait_message.edit_text(file_info, reply_markup=get_print_file_menu_keyboard(_, pages_pdf,
                                                                                              message.message_id))
        else:
            await message.answer(file_info, reply_markup=get_print_file_menu_keyboard(_, pages_pdf,
                                                                                      message.message_id))

        await message.reply(_("file_info"))
        await message.reply(_("file_sent_to_print"))
        print(message.document)


@router.callback_query(StateFilter(None), ChoicePageRangeCallbackFactory.filter())
async def handle_choice_page_range(callback: types.CallbackQuery, bot: Bot, state: FSMContext, callback_data: ChoicePageRangeCallbackFactory, _):

    await callback.message.answer(_("page_range_selected") + str(callback_data.file_pages_amount))
    await state.set_state(GetPagesState.getting_pages)

@router.message(GetPagesState.getting_pages)
async def handle_get_pages(message: types.Message, bot: Bot, state: FSMContext, _):

    if not await validate_pages_ranges(message, message.text, _):
        return

    count = await count_pages(message.text)


    await message.answer(_("pages") + str(message.text))
    await state.clear()


async def validate_pages_ranges(message: types.Message, pages_ranges: str, _) -> bool:
    if len(pages_ranges) > 30:
        await message.answer(_("too_much_length_of_range_of_pages"))
        return False
    pages = pages_ranges.split(",")
    last_number = 0
    for q in pages:
        if "-" in q:
            try:
                start, end = map(int, q.split("-"))
                if int(start) >= int(end) or int(start) <= last_number:
                    await message.answer(_("wrong_range_of_pages"))
                    return False
                last_number = int(end)
            except Exception as e:
                await message.answer(_("wrong_range_of_pages"))
                return False
        else:
            try:
                if int(q) <= last_number:
                    await message.answer(_("wrong_range_of_pages"))
                    return False
                last_number = int(q)
            except Exception as e:
                await message.answer(_("wrong_range_of_pages"))
                return False
    return True


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


async def build_file_info_message(_, file_name: str | None = None, file_size: int | None = None,
                                 pages_amount: int | None = None, pages_ranges: str | None = None,
                                 pages_to_print : int | None = None, pages_available: int | None = None) -> str:
    _str = ""
    if file_name:
        _str += _("file_name") + html.escape(file_name) + "\n"
    if file_size:
        if file_size < 700:
            file_size = str(file_size) + " B"
        elif file_size < 700 * 1024:
            file_size = str(round(file_size / 1024, 2)) + " KB"
        else:
            file_size = str(round(file_size / 1024 / 1024, 2)) + " MB"
        _str += _("file_size") + file_size + "\n"
    if pages_amount:
        _str += _("pages_amount") + str(pages_amount) + "\n"

    _str += "\n"
    if pages_ranges:
        _str += _("pages_ranges") + pages_ranges + "\n"
    if pages_to_print:
        _str += _("pages_to_print") + str(pages_to_print) + "\n"

    _str += "\n"
    if pages_available:
        _str += "<b>" + _("pages_available") + str(pages_available) + "</b>" + "\n"
    _str += _("sure_to_print_or_change_params")

    return _str


async def print_file(file_id: str, bot: Bot, pages_numbers: str) -> bool:
    with tempfile.NamedTemporaryFile("wb") as file:
        if not DEBUG:
            try:
                await bot.download(file_id, file.name)

                process = await create_subprocess_exec(
                    "lp",
                    "-n", "1",
                    "-o", "print-quality=5",
                    "-P", '"1,3"',
                    "-d",
                    "Canon_MF4400_Series",
                    "--",
                    file.name,
                )
                await process.wait()
            except Exception as e:
                logger.error(e)
                return False
            return True