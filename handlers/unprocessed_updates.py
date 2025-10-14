from aiogram import Router
from aiogram import types

router = Router()

@router.message()
async def other_mess(message: types.Message, _):
    await message.answer(_("to_start_work_send_pdf"))

@router.callback_query()
async def other_callback(callback: types.CallbackQuery, _):
    if callback.message is None:
        await callback.answer(_("error_try_again"))
        return
    await callback.message.answer(_("you_are_not_in_print_state"))
    await callback.message.answer(_("to_start_work_send_pdf"))
    await callback.answer()
