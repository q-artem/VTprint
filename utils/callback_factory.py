from typing import Optional
from aiogram.filters.callback_data import CallbackData

class ChoicePageRangeCallbackFactory(CallbackData, prefix="choice_page_range"):
    pass
    # Optional[int] = None

class AcceptPrintFileCallbackFactory(CallbackData, prefix="accept_print_file"):
    message_with_file_id: int
    pages_ranges: str

class CancelPrintFileCallbackFactory(CallbackData, prefix="cancel_print_file"):
    pass