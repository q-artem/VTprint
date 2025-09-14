
from aiogram import Router, F
from aiogram.enums import ContentType
from aiogram.types import Message
from aiogram import Bot, Dispatcher, F, types
import tempfile

from aiogram_i18n import I18nContext

from main import DEBUG
from asyncio import create_subprocess_exec
from aiogram.utils.i18n import gettext as _


router = Router()


@router.message(F.content_type == ContentType.DOCUMENT)
async def handle_document(message: types.Message, bot: Bot, _):
    assert message.document is not None

    with tempfile.NamedTemporaryFile("wb") as file:
        await message.reply(_("file_sent_to_print"))

        if not DEBUG:
            await bot.download(message.document.file_id, file.name)

            process = await create_subprocess_exec(
                "lp",
                "-d",
                "Canon_MF4400_Series",
                file.name,
            )
            await process.wait()