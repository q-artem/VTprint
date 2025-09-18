from asyncio import create_subprocess_exec
from venv import logger

from aiogram import types, Bot

from main import DEBUG
from utils.files_utils import get_file, delete_file


async def print_file(message: types.Message, bot: Bot, pages_numbers: str | None = None) -> bool:
    file = await get_file(message, bot)
    if not DEBUG:
        try:
            await bot.download(message.document.file_id, file.name)

            process = await create_subprocess_exec(
                "lp",
                "-n", "1",
                "-o", "print-quality=5",
                f"-P {pages_numbers}" if pages_numbers else "",
                "-d",
                "Canon_MF4400_Series",
                "--",
                file.name,
            )
            await process.wait()
            await delete_file(message)
        except Exception as e:
            logger.error(e)
            return False
        return True
    return True
