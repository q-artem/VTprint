from asyncio import create_subprocess_exec
from venv import logger

from aiogram import types, Bot

from config.defines import DEBUG
from utils.FSM_data_classes import PrintData
from utils.files_utils import get_file, delete_file


async def print_file(user_data: PrintData, bot: Bot) -> bool:
    file = await get_file(user_data.file_id, user_data.chat_id, bot)
    if not DEBUG:
        try:
            process = await create_subprocess_exec(
                "lp",
                "-n", "1",
                "-o", "print-quality=5",
                f"-P {user_data.pages_ranges}" if user_data.pages_ranges else "",
                f"-n {user_data.copies}",
                "-d",
                "Canon_MF4400_Series",
                "--",
                file,         ##############################
            )
            await process.wait()
            await delete_file(user_data.file_id)
        except Exception as e:
            logger.error(e)
            return False
        return True
    return True
