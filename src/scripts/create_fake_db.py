import asyncio

from faker import Faker
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import db_helper

fake = Faker("ru_RU")


async def create_fake_db(
    session: AsyncSession,
):
    pass


async def main():
    async with db_helper.session_factory() as session:
        await create_fake_db(session)


if __name__ == "__main__":
    asyncio.run(main())
