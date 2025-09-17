from contextlib import asynccontextmanager
from typing import AsyncGenerator

from aiogram.fsm.context import FSMContext
from pydantic import BaseModel


async def set_user_data(state: FSMContext, model: BaseModel) -> None:
    await state.set_data(
        model.model_dump(
            mode="json",
            exclude_defaults=True,
        )
    )


@asynccontextmanager
async def get_user_data[M: BaseModel](
    state: FSMContext,
    model_type: type[M],
) -> AsyncGenerator[M, None]:
    model = model_type.model_validate(await state.get_data())
    yield model
    await set_user_data(state, model)