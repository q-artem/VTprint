from aiogram import Router, Bot, F, types
from aiogram.enums import ContentType
import html

from aiogram.fsm.context import FSMContext
from pypdf import PdfReader
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import User
from printer.print_file import print_file
from states.printer_utils import validate_pages_ranges, count_pages, build_file_info_message, convert_file_size, \
    validate_copies_amount, check_access_to_print
from utils.FSM import PrintStates
from utils.FSM_data_classes import PrintData
from utils.callback_factory import ChoicePageRangeCallbackFactory, CancelPrintFileCallbackFactory, \
    CanselEnterPagesRangesCallbackFactory, ConfirmPrintFileCallbackFactory, ChoiceAmountCopiesCallbackFactory, \
    CancelChoiceAmountCopiesCallbackFactory
from utils.files_utils import get_file
from utils.keyboards import get_print_file_menu_keyboard, get_cancel_keyboard, get_confirm_print_file_keyboard

from utils.FSM_utils import set_user_data, get_user_data

router = Router()


@router.message(F.content_type == ContentType.DOCUMENT)
async def handle_document(message: types.Message, bot: Bot, session: AsyncSession, state: FSMContext, _):
    if message.document is None or message.document.file_name is None or message.document.file_size is None:
        await message.answer(_("file_processing_error").format("Error processing file info"))
        return

    if not (message.document.file_name.endswith(".pdf") and message.document.mime_type == "application/pdf"):
        await message.reply(_("file_is_not_pdf"))
        return

    if message.document.file_size > 20 * 1024 * 1024 - 1:
        await message.reply(_("file_is_too_big_max_is_20mb"), link_preview_options=types.LinkPreviewOptions(is_disabled=True))
        return

    file = await get_file(message.document.file_id, message.chat.id, bot)

    try:
        pages_total = len(PdfReader(file).pages)
    except Exception as e:
        await message.reply(_("file_processing_error").format(html.escape(str(e))))
        return

    await set_user_data(state, PrintData(
        chat_id=message.chat.id,
        file_id=message.document.file_id,
        file_name=html.escape(message.document.file_name),
        file_size_converted=await convert_file_size(message.document.file_size),
        pages_total=pages_total,
        pages_to_print=pages_total,  # страниц к печати
    ))

    assert message.from_user is not None
    file_info = await build_file_info_message(_, state, session, message.from_user.id)

    info_message = await message.answer(file_info, reply_markup=get_print_file_menu_keyboard(_))

    async with get_user_data(state, PrintData) as user_data:
        user_data.info_message_id = info_message.message_id

    await state.set_state(PrintStates.setting_parameters)
    print(message.document)


###################### Get pages range ######################


@router.callback_query(PrintStates.setting_parameters, ChoicePageRangeCallbackFactory.filter())
async def handle_choice_page_range(callback: types.CallbackQuery, bot: Bot, session: AsyncSession, state: FSMContext, _):
    async with get_user_data(state, PrintData) as user_data:
        bd_user = await session.get(User, callback.from_user.id)
        await bot.edit_message_text(
            chat_id=user_data.chat_id,
            message_id=user_data.info_message_id,
            text=_("page_range_selecting_available_n_pages").format(user_data.pages_total, bd_user.pages_left if bd_user else 0),
            reply_markup=get_cancel_keyboard(_, CanselEnterPagesRangesCallbackFactory())
        )
    await state.set_state(PrintStates.getting_pages)
    await callback.answer()

@router.message(PrintStates.getting_pages)
async def handle_get_pages(message: types.Message, session: AsyncSession, state: FSMContext, _):
    async with get_user_data(state, PrintData) as user_data:
        if not user_data.pages_total:
            await message.answer(_("file_processing_error").format("File not contains pages"))
            return
        if not await validate_pages_ranges(_, message, user_data.pages_total):
            return
    assert message.text is not None and message.from_user is not None

    pages_amount = await count_pages(message.text)
    db_user = await session.get(User, message.from_user.id)
    pages_left = db_user.pages_left if db_user else 0
    if pages_amount > pages_left:
        await message.answer(_("too_many_pages_you_available_n").format(pages_amount), reply_markup=get_cancel_keyboard(_, CanselEnterPagesRangesCallbackFactory()))
        return

    async with get_user_data(state, PrintData) as user_data:
        user_data.pages_to_print = pages_amount * user_data.copies
        user_data.pages_ranges = message.text

    pref_info = _("pages_ranges_all_pages_from_n_available").format(message.text, user_data.pages_to_print, pages_left)
    info_mess = await build_file_info_message(_, state, session, message.from_user.id, pref_info)
    info_message = await message.answer(info_mess, reply_markup=get_print_file_menu_keyboard(_))
    async with get_user_data(state, PrintData) as user_data:
        user_data.info_message_id = info_message.message_id
    await state.set_state(PrintStates.setting_parameters)


@router.callback_query(PrintStates.getting_pages, CanselEnterPagesRangesCallbackFactory.filter())
async def handle_cancel_get_ranges(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession, _):
    assert callback.message is not None
    await callback.message.answer(_("canceled"))
    info_mess = await build_file_info_message(_, state, session, callback.from_user.id)
    info_message = await callback.message.answer(info_mess, reply_markup=get_print_file_menu_keyboard(_))
    async with get_user_data(state, PrintData) as user_data:
        user_data.info_message_id = info_message.message_id
    await state.set_state(PrintStates.setting_parameters)
    await callback.answer()


######################### Set amount copies ############################

@router.callback_query(PrintStates.setting_parameters, ChoiceAmountCopiesCallbackFactory.filter())
async def handle_choice_amount_copies(callback: types.CallbackQuery, bot: Bot, session: AsyncSession, state: FSMContext, _):
    async with get_user_data(state, PrintData) as user_data:
        bd_user = await session.get(User, callback.from_user.id)
        await bot.edit_message_text(
            chat_id=user_data.chat_id,
            message_id=user_data.info_message_id,
            text=_("copies_amount_selecting_max_copies").format(user_data.pages_total, bd_user.pages_left if bd_user else 0),
            reply_markup=get_cancel_keyboard(_, CancelChoiceAmountCopiesCallbackFactory())
        )
    await state.set_state(PrintStates.setting_copies)
    await callback.answer()


@router.message(PrintStates.setting_copies)
async def handle_get_amount_copies(message: types.Message, session: AsyncSession, state: FSMContext, _):
    if not await validate_copies_amount(_, message):
        return
    assert message.text is not None  # проверяется в validate_copies_amount
    copies_amount = int(message.text)

    async with get_user_data(state, PrintData) as user_data:
        if not user_data.pages_to_print:
            user_data.pages_to_print = 0
        user_data.pages_to_print = user_data.pages_to_print // user_data.copies * copies_amount
        user_data.copies = copies_amount

    # чтобы copies_amount записался
    assert message.from_user is not None
    db_user = await session.get(User, message.from_user.id)
    pages_left = db_user.pages_left if db_user else 0
    pref_info = _("copies_amount_all_pages_from_n_available").format(copies_amount, user_data.pages_to_print, pages_left)
    info_mess = await build_file_info_message(_, state, session, message.from_user.id, pref_info)
    info_message = await message.answer(info_mess, reply_markup=get_print_file_menu_keyboard(_))

    async with get_user_data(state, PrintData) as user_data:
        user_data.info_message_id = info_message.message_id

    await state.set_state(PrintStates.setting_parameters)


@router.callback_query(PrintStates.setting_copies, CancelChoiceAmountCopiesCallbackFactory.filter())
async def handle_cancel_set_copies(callback: types.CallbackQuery, state: FSMContext,
                                   session: AsyncSession, _):
    assert callback.message is not None
    await callback.message.answer(_("canceled"))
    info_mess = await build_file_info_message(_, state, session, callback.from_user.id)
    info_message = await callback.message.answer(info_mess, reply_markup=get_print_file_menu_keyboard(_))
    async with get_user_data(state, PrintData) as user_data:
        user_data.info_message_id = info_message.message_id
    await state.set_state(PrintStates.setting_parameters)
    await callback.answer()


############################# Print / cancel print file ###############################


@router.callback_query(PrintStates.setting_parameters, ConfirmPrintFileCallbackFactory.filter())
async def handle_confirming_print_file(callback: types.CallbackQuery, bot: Bot, state: FSMContext, _):
    async with get_user_data(state, PrintData) as user_data:
        await bot.edit_message_text(
            chat_id=user_data.chat_id,
            message_id=user_data.info_message_id,
            text=_("confirm_printing_file").format(user_data.file_name),
            reply_markup=get_confirm_print_file_keyboard(_)
        )

    await state.set_state(PrintStates.confirming)
    await callback.answer()


@router.callback_query(PrintStates.confirming, ConfirmPrintFileCallbackFactory.filter())
async def confirming_print_file(callback: types.CallbackQuery, bot: Bot, state: FSMContext, session: AsyncSession, _):
    async with get_user_data(state, PrintData) as user_data:
        if not await check_access_to_print(_, state, session, callback.from_user.id):
            info_mess = await build_file_info_message(_, state, session, callback.from_user.id)
            await bot.edit_message_text(
                chat_id=user_data.chat_id,
                message_id=user_data.info_message_id,
                text=info_mess,
                reply_markup=get_print_file_menu_keyboard(_),
            )
            await state.set_state(PrintStates.setting_parameters)
            await callback.answer()
            return

        is_printed = await print_file(user_data, bot)

        assert callback.message is not None
        if is_printed:
            db_user = await session.get(User, callback.from_user.id)
            assert db_user is not None
            if not user_data.pages_to_print:
                await callback.message.answer(_("file_processing_error").format("Error counting pages to print"))
                return
            db_user.pages_left -= user_data.pages_to_print
            await session.commit()

            await bot.edit_message_text(
                chat_id=user_data.chat_id,
                message_id=user_data.info_message_id,
                text=_("file_sent_to_print").format(db_user.pages_left),
            )
        else:
            await callback.message.answer(_("error_printing_file"))

    await state.clear()
    await callback.answer()


@router.callback_query(PrintStates.confirming, CancelPrintFileCallbackFactory.filter())
async def cancel_confirming_print_file(callback: types.CallbackQuery, bot: Bot, state: FSMContext, session: AsyncSession, _):
    async with get_user_data(state, PrintData) as user_data:
        info_mess = await build_file_info_message(_, state, session, callback.from_user.id)
        await bot.edit_message_text(
            chat_id=user_data.chat_id,
            message_id=user_data.info_message_id,
            text=info_mess,
            reply_markup=get_print_file_menu_keyboard(_)
        )

    await state.set_state(PrintStates.setting_parameters)
    await callback.answer()


@router.callback_query(PrintStates.setting_parameters, CancelPrintFileCallbackFactory.filter())
async def handle_cancel_print_file(callback: types.CallbackQuery, bot: Bot, state: FSMContext, _):
    async with get_user_data(state, PrintData) as user_data:
        await bot.edit_message_text(
            chat_id=user_data.chat_id,
            message_id=user_data.info_message_id,
            text=_("print_canceled"),
        )

    await state.clear()
    await callback.answer()
