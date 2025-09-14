from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import User, Group, Language

router = Router()

# Клавиатура выбора языка
def get_lang_keyboard():
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇷🇺 Русский", callback_data="set_lang:ru")],
        [InlineKeyboardButton(text="🇬🇧 English", callback_data="set_lang:en")]
    ])

@router.message(Command("start"))
async def cmd_start(message: Message, session: AsyncSession):
    # Регистрация пользователя
    user_id = message.from_user.id
    lang_code = message.from_user.language_code[:2]

    db_user = await session.get(User, user_id)
    if not db_user:
        # Найти или создать группу по умолчанию
        group = await session.get(Group, -100)
        if not group:
            group = Group(name="Default", id=-100, sheets_per_day=5, password="")
            session.add(group)
            await session.commit()

        # Найти язык
        language = await session.get(Language, lang_code)
        if not language:
            language = await session.get(Language, "en")

        db_user = User(user_id=user_id, language_code=language.code, group_id=group.id)
        session.add(db_user)
        await session.commit()

    await message.answer("Выберите язык / Please select a language", reply_markup=get_lang_keyboard())

@router.callback_query(F.data.startswith("set_lang:"))
async def set_lang(callback: CallbackQuery, session: AsyncSession, __):
    lang_code = callback.data.split(":")[1]
    user_id = callback.from_user.id

    db_user = await session.get(User, user_id)
    if db_user:
        db_user.language_code = lang_code
        await session.commit()

    await callback.message.answer(__("selected_language", lang_code).format((await session.get(Language, lang_code)).name))
    await callback.answer()