from sqlalchemy.sql.expression import select

from database.models import User, Group
from database.session import async_session_maker


async def daily_reset_limits():
    offset = 0
    page_size = 1000
    async with async_session_maker() as session:
        while True:
            result = await session.execute(
                select(User).limit(page_size).offset(offset)
            )
            users = result.scalars().all()
            if not users:
                break

            for user in users:
                user.pages_left = (await session.get(Group, user.group_id)).sheets_per_day

            await session.commit()
            offset += page_size
