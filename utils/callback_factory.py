from typing import Optional
from aiogram.filters.callback_data import CallbackData

class ChoicePageRangeCallbackFactory(CallbackData, prefix="choice_page_range"):
    pass
    # Optional[int] = None

class CancelPrintFileCallbackFactory(CallbackData, prefix="cancel_print_file"):
    pass

class CanselEnterPagesRangesCallbackFactory(CallbackData, prefix="cancel_enter_pages_ranges"):
    pass

class ConfirmPrintFileCallbackFactory(CallbackData, prefix="cancel_print_file"):
    pass