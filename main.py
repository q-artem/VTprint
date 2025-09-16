import asyncio
import logging
import tempfile
from asyncio import create_subprocess_exec

from aiogram.client.default import DefaultBotProperties

from database.setup_start_data import init_start_data
from middlewares.block_nuregistreted import BlockUnregisteredMiddleware
from utils.config_reader import config

from aiogram import Bot, Dispatcher, F, types
from aiogram.enums import ContentType, ParseMode

from database.session import init_db, async_session_maker
from middlewares.db import DatabaseSessionMiddleware
from middlewares.i18n import i18n

from aiogram.utils.i18n import gettext as _

from middlewares.i18n_db import I18nDatabaseMiddleware

import handlers.printer
import handlers.user
import utils.admin_utils
import handlers.unprocessed_updates

DEBUG = True

async def main():
    logging.basicConfig(level=logging.INFO)
    logging.getLogger("pypdf").setLevel(logging.ERROR)  # ТИХОНЕЧКО

    API_TOKEN = config.bot_token.get_secret_value()

    bot = Bot(token=API_TOKEN,
              default=DefaultBotProperties(
                  parse_mode=ParseMode.HTML,
              ))

    dp = Dispatcher()


    # мидлвари
    dp.message.outer_middleware(DatabaseSessionMiddleware(async_session_maker))
    dp.callback_query.outer_middleware(DatabaseSessionMiddleware(async_session_maker))

    dp.message.outer_middleware(BlockUnregisteredMiddleware())
    dp.callback_query.outer_middleware(BlockUnregisteredMiddleware())

    dp.message.outer_middleware(I18nDatabaseMiddleware())
    dp.callback_query.outer_middleware(I18nDatabaseMiddleware())


    # роутеры
    dp.include_router(utils.admin_utils.router)
    dp.include_router(handlers.user.router)
    dp.include_router(handlers.printer.router)
    dp.include_router(handlers.unprocessed_updates.router)


    await init_db()
    await init_start_data()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
