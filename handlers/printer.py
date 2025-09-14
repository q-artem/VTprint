from aiogram import Router, Bot, F, types
from aiogram.enums import ContentType
import tempfile

from main import DEBUG
from asyncio import create_subprocess_exec

router = Router()


@router.message(F.content_type == ContentType.DOCUMENT)
async def handle_document(message: types.Message, bot: Bot, _):
    assert message.document is not None  # на всякий случайэ

    if not (message.document.file_name.endswith(".pdf") and message.document.mime_type == "application/pdf"):
        await message.reply(_("file_is_not_pdf"))
        return

    with tempfile.NamedTemporaryFile("wb") as file:
        await message.reply(_("file_sent_to_print"))

        if not DEBUG:
            await bot.download(message.document.file_id, file.name)

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
