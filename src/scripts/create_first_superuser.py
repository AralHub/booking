import asyncio
import logging
from datetime import UTC, datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    MetaData,
    String,
    Table,
    insert,
    select,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import db_helper
from app.core.config import settings
from app.core.utils.auth_utils import hash_password
from app.models.user import User

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def create_first_user(session: AsyncSession) -> None:
    try:
        name = settings.first_user.ADMIN_NAME
        phone_number = settings.first_user.ADMIN_PHONE_NUMBER
        username = settings.first_user.ADMIN_USERNAME
        hashed_password = hash_password(settings.first_user.ADMIN_PASSWORD).decode(
            "utf-8"
        )

        query = select(User).filter_by(phone_number=phone_number)
        result = await session.execute(query)
        user = result.scalar_one_or_none()

        if user is None:
            metadata = MetaData()
            user_table = Table(
                "users",
                metadata,
                Column(
                    "id", Integer, primary_key=True, autoincrement=True, nullable=False
                ),
                Column("name", String(30), nullable=False),
                Column(
                    "phone_number", String(15), nullable=False, unique=True, index=True
                ),
                Column("hashed_password", String, nullable=False),
                Column(
                    "is_fully_registered",
                    Boolean,
                    default=False,
                    server_default="false",
                ),
                Column("is_verified", Boolean, default=False, server_default="false"),
                Column("is_active", Boolean, default=False, server_default="false"),
                Column(
                    "created_at",
                    DateTime(timezone=True),
                    default=lambda: datetime.now(UTC),
                    nullable=False,
                ),
                Column("updated_at", DateTime),
                Column("is_superuser", Boolean, default=False, server_default="false"),
                Column("tier_id", Integer, ForeignKey("tiers.id"), index=True),
            )

            data = {
                "name": name,
                "phone_number": phone_number,
                "hashed_password": hashed_password,
                "is_superuser": True,
                "is_fully_registered": True,
                "is_active": True,
                "is_verified": True,
            }

            stmt = insert(user_table).values(data)
            async with db_helper.engine.connect() as conn:
                await conn.execute(stmt)
                await conn.commit()

            logger.info(f"Admin user {username} created successfully.")

        else:
            logger.info(f"Admin user {username} already exists.")

    except Exception as e:
        logger.error(f"Error creating admin user: {e}")


async def main():
    async with db_helper.session_factory() as session:
        await create_first_user(session)


if __name__ == "__main__":
    asyncio.run(main())
