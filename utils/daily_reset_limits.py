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
                db_group = await session.get(Group, user.group_id)
                user.pages_left = db_group.sheets_per_day if db_group else 0

            await session.commit()
            offset += page_size
