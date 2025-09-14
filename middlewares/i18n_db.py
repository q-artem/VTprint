# middlewares/i18n_db.py

from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from aiogram.utils.i18n import I18nMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select


from database.models import User  # твои модели


class I18nDatabaseMiddleware(I18nMiddleware):
    def __init__(self, session_pool, i18n):
        super().__init__(i18n=i18n)
        self.session_pool = session_pool  # пул сессий SQLAlchemy (асинхронный!)

    async def get_locale(self, event: Message | CallbackQuery, data: Dict[str, Any]) -> str:
        user_id = event.from_user.id

        # Получаем сессию из пула (предполагается, что ты передаешь session в data через другую мидлварь)
        session: AsyncSession = data.get("session")
        if not session:
            return self.i18n.default_locale

        try:
            stmt = select(User.language_code).where(User.user_id == user_id)
            result = await session.execute(stmt)
            language_code = result.scalar_one_or_none()
            if language_code:
                return language_code
        except Exception:
            # Логируй ошибку, если нужно
            pass

        return self.i18n.default_locale

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any],
    ) -> Any:
        # Устанавливаем локаль ДО вызова хендлера
        locale = await self.get_locale(event, data)
        self.i18n.current_locale = locale



        # Передаем locale в data, чтобы можно было использовать в хендлерах
        data["locale"] = locale

        return await handler(event, data)