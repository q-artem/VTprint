from typing import Optional
from aiogram.filters.callback_data import CallbackData

class ChoicePageRangeCallbackFactory(CallbackData, prefix="choice_page_range"):
    pass
    # Optional[int] = None

class CancelPrintFileCallbackFactory(CallbackData, prefix="cancel_print_file"):
    pass

class CanselEnterPagesRangesCallbackFactory(CallbackData, prefix="cancel_enter_pages_ranges"):
    pass

class ConfirmPrintFileCallbackFactory(CallbackData, prefix="confirm_print_file"):
    pass

class ChoiceAmountCopiesCallbackFactory(CallbackData, prefix="choice_amount_copies"):
    pass

class CancelChoiceAmountCopiesCallbackFactory(CallbackData, prefix="cancel_choice_amount_copies"):
    pass