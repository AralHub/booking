import asyncio

from faker import Faker
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import db_helper
from app.crud.crud_restaurant import crud_restaurant
from app.schemas.restaurant import RestaurantCreateInternal

fake = Faker("ru_RU")


async def create_fake_restaurant(
    session: AsyncSession,
    num_restaurants: int = 1,
):
    """Создает фейковые рестораны в базе данных"""
    for _ in range(num_restaurants):
        restaurant_data = RestaurantCreateInternal(
            name=fake.company(),
            domain=fake.domain_word(),
            description=fake.text(max_nb_chars=200),
            address=fake.address(),
            phone=fake.phone_number(),
            email=fake.email(),
            created_by_user_id=1,  # ID пользователя, который будет владельцем
            is_active=True,
        )

        try:
            await crud_restaurant.create(db=session, object=restaurant_data)
        except Exception as e:
            print(f"Ошибка при создании ресторана: {e}")


async def main():
    async with db_helper.session_factory() as session:
        await create_fake_restaurant(session)


if __name__ == "__main__":
    asyncio.run(main())
