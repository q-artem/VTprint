from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import User  # Импортируй модель User

class BlockUnregisteredMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message | CallbackQuery, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any],
    ) -> Any:
        session: AsyncSession = data.get("session")

        user_id = None
        if isinstance(event, Message):
            user_id = event.from_user.id
            text = event.text or ""
        elif isinstance(event, CallbackQuery):
            user_id = event.from_user.id
            text = event.data
        else:
            return await handler(event, data)  # allow other updates

        db_user = await session.get(User, user_id)

        # забаненые
        if db_user and db_user.banned:
            if isinstance(event, Message):
                await event.answer(
                    "К сожалению, вы были забанены. Наверное было за что / Unfortunately, you are banned.",
                )
            elif isinstance(event, CallbackQuery):
                await event.message.answer(
                    "К сожалению, вы были забанены. Наверное было за что / Unfortunately, you are banned.",
                )
            return None

        # if in group
        if db_user and db_user.group_id is not None:
            return await handler(event, data)

        # if in db and not in group OR not in db
        if (db_user and db_user.group_id is None) or (not db_user):
            # of object is message with start command
            if isinstance(event, Message) and text.startswith("/start"):
                return await handler(event, data)
            else:
                if isinstance(event, Message):
                    await event.answer(
                        "Вы не привязаны к группе. Используйте пригласительную ссылку. / You are not bound to a group. Use an invitation link.",
                    )
                elif isinstance(event, CallbackQuery):
                    await event.message.answer(
                        "Вы не привязаны к группе. Используйте пригласительную ссылку. / You are not bound to a group. Use an invitation link.",
                    )
                return None

        return await handler(event, data)