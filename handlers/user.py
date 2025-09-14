from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, CommandStart, CommandObject
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import User, Group, Language
from utils.print_links_to_join import get_links_to_join

router = Router()

# Клавиатура выбора языка
def get_lang_keyboard():
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇷🇺 Русский", callback_data="set_lang:ru")],
        [InlineKeyboardButton(text="🇬🇧 English", callback_data="set_lang:en")]
    ])

@router.message(CommandStart(deep_link=True))
@router.message(Command("start"))
async def cmd_start(message: Message, bot: Bot, session: AsyncSession, command: CommandObject):
    # Регистрация пользователя
    user_id = message.from_user.id
    lang_code = message.from_user.language_code[:2]
    try:
        _, user_group, _, password = command.args.split("-")
        print(command.args.split("-"))
        group = await session.scalar(select(Group).where(Group.name == user_group))
    except Exception as e:
        await message.answer("Неправильная ссылка / Incorrect link")
        print(e)
        return

    if not group:
        await message.answer("Неправильная группа / Incorrect group")
        return
    if group.password != password:
        await message.answer("Неправильный пароль / Incorrect password")
        return
    # тут группа и пароль совпали
    db_user = await session.get(User, user_id)
    if not db_user:  # если нет в бд
        language = await session.get(Language, lang_code)
        if not language:
            language = await session.get(Language, "en")
        db_user = User(user_id=user_id, language_code=language.code, group_id=group.id)
        session.add(db_user)
        await session.commit()
        await message.answer("Вы добавлены в группу {} / You are added to group {}".format(group.name, group.name))
    else:
        db_user.group_id = group.id
        await session.commit()
        await message.answer("Вы перемещены в группу {} / You are moved to group {}".format(group.name, group.name))

    await message.answer("Выберите язык / Please select a language", reply_markup=get_lang_keyboard())


@router.callback_query(F.data.startswith("set_lang:"))
async def set_lang(callback: CallbackQuery, session: AsyncSession, _):
    lang_code = callback.data.split(":")[1]
    user_id = callback.from_user.id

    db_user = await session.get(User, user_id)
    if db_user:
        db_user.language_code = lang_code
        await session.commit()

    await callback.message.answer(_("selected_language", lang_code).format((await session.get(Language, lang_code)).name))
    await callback.answer()