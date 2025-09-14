# middlewares/i18n_db.py

from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from middlewares.i18n import i18n


from database.models import User  # твои модели


class I18nDatabaseMiddleware(BaseMiddleware):
    async def get_locale(self, event: Message | CallbackQuery, data: Dict[str, Any]) -> str:
        user_id = event.from_user.id

        session: AsyncSession = data.get("session")
        if not session:
            return i18n.default_locale

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
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any],
    ) -> Any:
        locale = await self.get_locale(event, data)

        def _(text: str) -> str:
            return i18n.gettext(text, locale=locale)

        def __(text: str, lasy_locale: str) -> str:
            return i18n.gettext(text, locale=lasy_locale)

        data["locale"] = locale
        data["_"] = _
        data["__"] = __

        return await handler(event, data)
