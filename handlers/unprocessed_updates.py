from aiogram import Router
from aiogram.types import Message

router = Router()

@router.message()
async def other_mess(message: Message, _):
    await message.answer(_("to_start_work_send_pdf"))