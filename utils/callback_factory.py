from typing import Optional
from aiogram.filters.callback_data import CallbackData

class ChoicePageRangeCallbackFactory(CallbackData, prefix="choice_page_range"):
    file_pages_amount: int
    message_with_file_id: int

    # Optional[int] = None

class AcceptPrintFileCallbackFactory(CallbackData, prefix="accept_print_file"):
    file_pages_amount: int
    message_with_file_id: int
    pages_ranges: str
