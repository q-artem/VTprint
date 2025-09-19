from pydantic import BaseModel, Field
from aiogram import types

class PrintData(BaseModel):
    chat_id: int | None = None
    file_id: str | None = None
    file_name: str | None = None
    file_size_converted: str | None = None
    pages_total: int | None = None
    pages_ranges: str = ""
    pages_to_print: int | None = None  # страниц к печати
    copies: int = 1
    info_message_id: int | None = None
