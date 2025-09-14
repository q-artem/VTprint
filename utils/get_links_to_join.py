from aiogram import Bot

from config.default_groups import groups


async def get_links_to_join(bot: Bot) -> str:
    _str = ""
    for q in groups:
        _str += f"{q['name']} {q["sheets_per_day"]} s/d: https://t.me/{(await bot.get_me()).username}?start=group-{q['name']}-pass-{q['password']}\n"
    return _str
