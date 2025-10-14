from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, LinkPreviewOptions

from utils.get_links_to_join import get_links_to_join

router = Router()


@router.callback_query(F.data.startswith("get_referral_links:"))
async def get_referral_links(callback: CallbackQuery, bot: Bot):
    assert callback.message is not None
    await callback.message.answer(await get_links_to_join(bot),
                                  link_preview_options=LinkPreviewOptions(is_disabled=True))
    await callback.answer()
