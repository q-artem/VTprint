from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, TelegramObject
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from middlewares.i18n import i18n

from database.models import User  # твои модели


class I18nDatabaseMiddleware(BaseMiddleware):
    @staticmethod
    async def get_locale(event: Message | CallbackQuery, data: Dict[str, Any]) -> str:
        assert event.from_user is not None
        user_id = event.from_user.id

        _session = data.get("session")
        if not isinstance(_session, AsyncSession):
            return i18n.default_locale
        session: AsyncSession = _session

        try:
            language_code = await session.scalar(select(User.language_code).where(User.user_id == user_id))
            if language_code:
                return language_code
        except Exception as e:
            print("ЗАЛУПА В БД")
            print(e)
            pass

        return i18n.default_locale

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:
        if isinstance(event, (Message, CallbackQuery)):
            locale = await self.get_locale(event, data)

            def _(text: str, curr_locale: str | None = None) -> str:
                if curr_locale:
                    return i18n.gettext(text, locale=curr_locale)
                return i18n.gettext(text, locale=locale)

            data["locale"] = locale
            data["_"] = _

            return await handler(event, data)
        else:
            return await handler(event, data)
