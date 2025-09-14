import asyncio
import logging
import tempfile
from asyncio import create_subprocess_exec

from aiogram.client.default import DefaultBotProperties

from utils.config_reader import config

from aiogram import Bot, Dispatcher, F, types
from aiogram.enums import ContentType, ParseMode

from database.session import init_db, async_session_maker
from middlewares.db import DatabaseSessionMiddleware
from middlewares.i18n import i18n

from aiogram.utils.i18n import gettext as _

from middlewares.i18n_db import I18nDatabaseMiddleware

import handlers.files
import handlers.user

DEBUG = True

async def main():
    logging.basicConfig(level=logging.INFO)

    API_TOKEN = config.bot_token.get_secret_value()

    bot = Bot(token=API_TOKEN,
              default=DefaultBotProperties(
                  parse_mode=ParseMode.HTML,
              ))

    dp = Dispatcher()




    # мидлвари
    dp.message.outer_middleware(DatabaseSessionMiddleware(async_session_maker))
    dp.callback_query.outer_middleware(DatabaseSessionMiddleware(async_session_maker))

    dp.message.outer_middleware(I18nDatabaseMiddleware())
    dp.callback_query.outer_middleware(I18nDatabaseMiddleware())


    # роутеры
    dp.include_router(handlers.user.router)
    dp.include_router(handlers.files.router)


    await init_db()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
