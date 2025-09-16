from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, CommandStart, CommandObject
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import User, Group, Language
from utils.keyboards import get_lang_keyboard, get_admin_panel_keyboard

router = Router()

@router.message(CommandStart(deep_link=True))
@router.message(Command("start"))
async def cmd_start(message: Message, bot: Bot, session: AsyncSession, command: CommandObject):
    # Регистрация пользователя
    user_id = message.from_user.id
    lang_code = message.from_user.language_code[:2]
    # нету аргументов
    if not command.args:
        if await session.get(User, user_id):
            await message.answer("Выберите язык / Please select a language", reply_markup=get_lang_keyboard())
            return
        await message.answer("Нононо мистер фиш, нужна ссылочка")
        return
    # есть аргументы
    try:
        _, user_group, _, password = command.args.split("-")
        group = await session.scalar(select(Group).where(Group.name == user_group))
    except Exception as e:
        await message.answer("Неправильная ссылка / Invalid link")
        print(e)
        return
    # есть аргументы правильного формата
    if not group:
        await message.answer("Неправильная группа / Invalid group")
        return
    if group.password != password:
        await message.answer("Неправильный пароль / Invalid password")
        return
    # тут группа и пароль совпали
    db_user = await session.get(User, user_id)
    if not db_user:  # если нет в бд
        language = await session.get(Language, lang_code)
        if not language:
            language = await session.get(Language, "en")
        db_user = User(user_id=user_id, language_code=language.code, group_id=group.id, pages_left=group.sheets_per_day)
        session.add(db_user)
        await session.commit()
        await message.answer("Вы добавлены в группу {}. Вам доступно {} страниц в день / Success. You're in the {} group now. Each day you can print {} pages.".format(group.name, group.sheets_per_day, group.name, group.sheets_per_day))
    else:
        db_user.group_id = group.id
        await session.commit()
        await message.answer("Вы перемещены в группу {}. Новые страницы будут зачислены завтра в соответствии с вашей новой группой / You are moved to group {}. You'll get your new group's set of pages tomorrow.".format(group.name, group.name))

    await message.answer("Выберите язык / Please select a language", reply_markup=get_lang_keyboard())


@router.message(Command("admin"))
async def admin(message: Message, session: AsyncSession, bot: Bot):
    if message.from_user.id in [1722948286]:
        await message.answer("Admin panel", reply_markup=get_admin_panel_keyboard())
    else:
        await message.answer("Ты не админ, бебебе")


@router.callback_query(F.data.startswith("set_lang:"))
async def set_lang(callback: CallbackQuery, session: AsyncSession, _):
    lang_code = callback.data.split(":")[1]
    user_id = callback.from_user.id

    db_user = await session.get(User, user_id)
    if db_user:
        db_user.language_code = lang_code
        await session.commit()

    await callback.message.answer(_("selected_language", lang_code).format((await session.get(Language, lang_code)).name))
    await callback.message.answer(_("to_start_work_send_pdf"))
    await callback.answer()