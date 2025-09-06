import asyncio
import logging
import tempfile
from asyncio import create_subprocess_exec

from aiogram import Bot, Dispatcher, F, types
from aiogram.enums import ContentType
from aiogram.filters.command import Command

logging.basicConfig(level=logging.INFO)


API_TOKEN = "8439783657:AAHtTpLuNA6jW2XmDejxHaVcXvIjljIggXs"

bot = Bot(token=API_TOKEN)
dp = Dispatcher()


@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    await message.answer(
        "Привет!\nОтправь мне любой файл, и я сохраню его во временное хранилище."
    )


@dp.message(F.content_type == ContentType.DOCUMENT)
async def handle_document(message: types.Message):
    assert message.document is not None

    with tempfile.NamedTemporaryFile("wb") as file:
        await bot.download(message.document, file.name)

        await message.reply("Файл отправлен на печать")
        process = await create_subprocess_exec(
            "lp",
            "-d",
            "Canon_MF4400_Series",
            file.name,
        )
        await process.wait()


if __name__ == "__main__":
    asyncio.run(dp.start_polling(bot))
