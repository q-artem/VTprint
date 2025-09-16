import os

from aiofiles import tempfile
from aiogram import types, Bot
from aiogram.utils.chat_action import ChatActionSender

local_saved_files = dict()


async def get_file(message: types.Message, bot: Bot):
    if message.document.file_id not in local_saved_files:
        async with ChatActionSender.upload_document(message.chat.id, bot, interval=10):
            async with tempfile.NamedTemporaryFile("wb", delete=False) as file:
                await bot.download(message.document.file_id, file.name)
                local_saved_files[message.document.file_id] = file.name
    return local_saved_files[message.document.file_id]


async def delete_file(message: types.Message) -> bool:
    if message.document.file_id in local_saved_files:
        os.remove(local_saved_files[message.document.file_id])
        del local_saved_files[message.document.file_id]
        return True
    return False
