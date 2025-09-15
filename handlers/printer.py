import html

from aiogram import Router, Bot, F, types
from aiogram.enums import ContentType
import tempfile

from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from pypdf import PdfReader

from main import DEBUG
from asyncio import create_subprocess_exec

from utils.FSM import GetPagesState
from utils.callback_factory import ChoicePageRangeCallbackFactory
from utils.keyboards import get_print_file_menu_keyboard

router = Router()


@router.message(F.content_type == ContentType.DOCUMENT)
async def handle_document(message: types.Message, bot: Bot, _):
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
        if message.document.file_size < 700:
            file_size = str(message.document.file_size) + " B"
        elif message.document.file_size < 700 * 1024:
            file_size = str(round(message.document.file_size / 1024, 2)) + " KB"
        else:
            file_size = str(round(message.document.file_size / 1024 / 1024, 2)) + " MB"
        pages_amount = len(PdfReader(file).pages)



        file_info = _("file_info").format(html.escape(file_name), file_size, pages_amount)
        if wait_message:
            await wait_message.edit_text(file_info, reply_markup=get_print_file_menu_keyboard(_, pages_amount,
                                                                                              message.message_id))
        else:
            await message.answer(file_info, reply_markup=get_print_file_menu_keyboard(_, pages_amount,
                                                                                      message.message_id))

        await message.reply(_("file_info"))
        await message.reply(_("file_sent_to_print"))
        print(message.document)

        if not DEBUG:
            # await bot.download(message.document.file_id, file.name)

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


@router.callback_query(StateFilter(None), ChoicePageRangeCallbackFactory.filter())
async def handle_choice_page_range(callback: types.CallbackQuery, bot: Bot, state: FSMContext, callback_data: ChoicePageRangeCallbackFactory, _):

    await callback.message.answer(_("page_range_selected") + str(callback_data.file_pages_amount))
    await state.set_state(GetPagesState.getting_pages)

@router.message(GetPagesState.getting_pages)
async def handle_get_pages(message: types.Message, bot: Bot, state: FSMContext, _):

    await message.answer(_("pages") + str(message.text))
    await state.clear()