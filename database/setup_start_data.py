from config.default_groups import groups
from database.models import Group
from database.session import async_session_maker


async def init_start_data():
    async with async_session_maker() as session:
        for q in groups:
            if not await session.get(Group, q["id"]):
                session.add(Group(**q))
        await session.commit()

