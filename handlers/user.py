import html

from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, CommandStart, CommandObject
from aiogram.fsm.context import FSMContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import User, Group, Language
from utils.FSM_data_classes import PrintData
from utils.FSM_utils import get_user_data
from utils.keyboards import get_lang_keyboard, get_admin_panel_keyboard

router = Router()


@router.message(CommandStart(deep_link=True))
@router.message(Command("start"))
async def cmd_start(message: Message, session: AsyncSession, command: CommandObject):
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
        await message.answer(
            "Вы добавлены в группу {}. Вам доступно {} страниц в день / Success. You're in the {} group now. Each day you can print {} pages.".format(
                group.name, group.sheets_per_day, group.name, group.sheets_per_day))
    else:
        db_user.group_id = group.id
        await session.commit()
        await message.answer(
            "Вы перемещены в группу {}. Новые страницы будут зачислены завтра в соответствии с вашей новой группой / You are moved to group {}. You'll get your new group's set of pages tomorrow.".format(
                group.name, group.name))

    await message.answer("Выберите язык / Please select a language", reply_markup=get_lang_keyboard())


@router.message(Command("admin"))
async def admin(message: Message):
    if message.from_user.id in [1722948286]:
        await message.answer("Admin panel", reply_markup=get_admin_panel_keyboard())
    else:
        await message.answer("Ты не админ, бебебе")


@router.message(Command("snd"))
async def send_message(message: Message, command: Command, bot: Bot):
    if message.from_user.id in [1722948286]:
        args = command.args  # type: ignore
        try:
            user_id = args.split()[0]
            mess = " ".join(args.split()[1:])
            await bot.send_message(user_id, mess)
        except Exception as e:
            await bot.send_message(message.from_user.id, html.escape(str(e)))
            return
        await bot.send_message(message.from_user.id, f"Успешно. Отправлено сообщение <code>{mess}</code>")


@router.message(Command("ban"))
async def send_message(message: Message, session: AsyncSession, command: Command, bot: Bot):
    if message.from_user.id in [1722948286]:
        args = command.args  # type: ignore
        try:
            db_user = await session.get(User, args)
            db_user.banned = 1
            await session.commit()
        except Exception as e:
            await bot.send_message(message.from_user.id, html.escape(str(e)))
            return
        await bot.send_message(message.from_user.id, f"Успешно. Забанен <code>{args}</code>")


@router.message(Command("unban"))
async def send_message(message: Message, session: AsyncSession, command: Command, bot: Bot):
    if message.from_user.id in [1722948286]:
        args = command.args  # type: ignore
        try:
            db_user = await session.get(User, args)
            db_user.banned = 0
            await session.commit()
        except Exception as e:
            await bot.send_message(message.from_user.id, html.escape(str(e)))
            return
        await bot.send_message(message.from_user.id, f"Успешно. Разбанен <code>{args}</code>")


@router.message(Command("help"))
async def help_mess(message: Message, bot: Bot, session: AsyncSession, _):
    await send_help_message(session, message.from_user.id, bot, _)


async def send_help_message(session: AsyncSession, user_id: int, bot: Bot, _, lang_code=None):
    db_user = await session.get(User, user_id)
    if lang_code:
        await bot.send_message(user_id, _("help", lang_code).format(db_user.group.name, db_user.group.sheets_per_day))
    else:
        await bot.send_message(user_id, _("help").format(db_user.group.name, db_user.group.sheets_per_day))


@router.message(Command("report"))
async def report(message: Message, command: Command, bot: Bot, state: FSMContext, session: AsyncSession, _):
    args = command.args  # type: ignore
    if not args:
        await message.answer(_("using_report"))
        return
    db_user = await session.get(User, message.from_user.id)
    async with get_user_data(state, PrintData) as user_data:
        report_mess = (f"Репорт от юзера <code>{message.from_user.id}</code>\n"
                       f"Данные: {user_data}\n"
                       f"Состояние: {await state.get_state()}\n"
                       f"Юзер в бд: {html.escape(str(db_user.__dict__))}\n\n"
                       f"Сообщение:\n"
                       f"{args}")
        await bot.send_message(1722948286, report_mess)


@router.callback_query(F.data.startswith("set_lang:"))
async def set_lang(callback: CallbackQuery, bot: Bot, session: AsyncSession, _):
    lang_code = callback.data.split(":")[1]
    user_id = callback.from_user.id

    db_user = await session.get(User, user_id)
    if db_user:
        db_user.language_code = lang_code
        await session.commit()

    await callback.message.answer(
        _("selected_language", lang_code).format((await session.get(Language, lang_code)).name))
    await send_help_message(session, user_id, bot, _, lang_code)
    await callback.message.answer(_("to_start_work_send_pdf", lang_code))
    await callback.answer()
