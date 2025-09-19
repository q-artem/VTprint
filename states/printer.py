from aiogram import Router, Bot, F, types
from aiogram.enums import ContentType

from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from pypdf import PdfReader
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import User
from states.printer_utils import validate_pages_ranges, count_pages, build_file_info_message, convert_file_size
from utils.FSM import GetPagesState, PrintStates
from utils.FSM_data_classes import PrintData
from utils.callback_factory import ChoicePageRangeCallbackFactory, CancelPrintFileCallbackFactory
from utils.files_utils import get_file
from utils.keyboards import get_print_file_menu_keyboard

from utils.FSM_utils import set_user_data, get_user_data

router = Router()


@router.message(F.content_type == ContentType.DOCUMENT, StateFilter(None))
async def handle_document(message: types.Message, bot: Bot, session: AsyncSession, state: FSMContext, _):
    assert message.document is not None  # на всякий случай

    if not (message.document.file_name.endswith(".pdf") and message.document.mime_type == "application/pdf"):
        await message.reply(_("file_is_not_pdf"))
        return

    if message.document.file_size > 20 * 1024 * 1024 - 1:
        await message.reply(_("file_is_too_big_max_is_20mb"), link_preview_options=types.LinkPreviewOptions(is_disabled=True))
        return

    file = await get_file(message, bot)

    pages_total = len(PdfReader(file).pages)

    await set_user_data(state, PrintData(
        chat_id=message.chat.id,
        file_id=message.document.file_id,
        file_name=message.document.file_name,
        file_size_converted=await convert_file_size(message.document.file_size),
        pages_total=pages_total,
        pages_to_print=pages_total,  # страниц к печати
    ))

    file_info = await build_file_info_message(_, state, session, message.from_user.id)

    info_message = await message.answer(file_info, reply_markup=get_print_file_menu_keyboard(_, pages_total,
                                                                              message.message_id))

    async with get_user_data(state, PrintData) as user_data:
        user_data.info_message_id = info_message.message_id

    # await message.reply(_("file_sent_to_print"))
    await state.set_state(PrintStates.setting_parameters)
    print(message.document)


###################### Get pages range ######################


@router.callback_query(StateFilter(PrintStates.setting_parameters), ChoicePageRangeCallbackFactory.filter())
async def handle_choice_page_range(callback: types.CallbackQuery, bot: Bot, state: FSMContext, _):
    async with get_user_data(state, PrintData) as user_data:
        await bot.edit_message_text(
            chat_id=user_data.chat_id,
            message_id=user_data.info_message_id,
            text=_("page_range_selecting_available_n_pages").format(user_data.pages_total)
        )
    await state.set_state(PrintStates.getting_pages)
    await callback.answer()

@router.message(PrintStates.getting_pages)
async def handle_get_pages(message: types.Message, session: AsyncSession, state: FSMContext, _):
    if not await validate_pages_ranges(message, _):
        return
    pages_amount = await count_pages(message.text)


    await message.answer(_("pages_ranges_all_pages_from_n_available").format(str(message.text), pages_amount, (await session.get(User, message.from_user.id)).pages_left))
    await state.set_state(PrintStates.setting_parameters)

# будет израсходовано 3 ил 5 доступных
############################################################


@router.callback_query(CancelPrintFileCallbackFactory.filter())
async def handle_cancel_print_file(callback: types.CallbackQuery, bot: Bot, state: FSMContext, _):

    if StateFilter(GetPagesState):
        await callback.message.answer(_("print_canceled"))
        await state.clear()
    else:
        await callback.message.answer(_("not_in_print_state"))
    await callback.answer()
