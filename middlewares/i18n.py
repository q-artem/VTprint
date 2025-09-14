import os

from aiogram.utils.i18n import I18n

i18n = I18n(path=os.path.join(os.path.dirname(__file__), "../locales"), default_locale="en", domain="vt-print")
