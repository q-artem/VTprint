import os

from aiofiles import tempfile
from aiogram import Bot
from aiogram.utils.chat_action import ChatActionSender

local_saved_files = dict()


async def get_file(file_id: str, chat_id: int, bot: Bot):
    if file_id not in local_saved_files:
        async with ChatActionSender.upload_document(chat_id, bot, interval=10):
            async with tempfile.NamedTemporaryFile("wb", delete=False) as file:
                await bot.download(file_id, file.name)
                local_saved_files[file_id] = file.name
    return local_saved_files[file_id]


async def delete_file(file_id: str) -> bool:
    if file_id in local_saved_files:
        os.remove(local_saved_files[file_id])
        del local_saved_files[file_id]
        return True
    return False
