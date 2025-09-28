import asyncio
import logging
from asyncio import create_subprocess_exec
from venv import logger

from aiogram.client.default import DefaultBotProperties

from database.setup_start_data import init_start_data
from middlewares.block_nuregistreted import BlockUnregisteredMiddleware
from utils.config_reader import config

from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode

from database.session import init_db, async_session_maker
from middlewares.db import DatabaseSessionMiddleware

from middlewares.i18n_db import I18nDatabaseMiddleware

from aiogram.fsm.storage.redis import RedisStorage
from redis.asyncio import Redis

import states.printer
import handlers.user
import utils.admin_utils
import handlers.unprocessed_updates

DEBUG = True
COMPILE_TRANSLATES_ON_START = True

async def main():
    logging.basicConfig(level=logging.INFO)
    logging.getLogger("pypdf").setLevel(logging.ERROR)  # ТИХОНЕЧКО

    storage = RedisStorage(Redis())

    bot = Bot(token=config.bot_token.get_secret_value(),
              default=DefaultBotProperties(
                  parse_mode=ParseMode.HTML,
              ))

    dp = Dispatcher(storage=storage)


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
    dp.include_router(states.printer.router)
    dp.include_router(handlers.unprocessed_updates.router)

    if DEBUG:  # удаление состояний
        keys = await storage.redis.keys('fsm:*')
        if keys:
            await storage.redis.delete(*keys)


    if COMPILE_TRANSLATES_ON_START:
        process = await create_subprocess_exec("sh", "./3_compile_translates.sh")
        await process.wait()
        logger.info("Translates compiled")
    await init_db()
    await init_start_data()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
