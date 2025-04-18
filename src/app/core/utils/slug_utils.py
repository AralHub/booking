from slugify import slugify as slugify_func
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.hotel import Hotel
from app.models.location import City


async def generate_slug_for_hotel(
    session: AsyncSession,
    name: str,
) -> str:
    base_slug = slugify_func(name)

    # Формируем запрос для поиска всех slug, начинающихся с base_slug
    # Используем LIKE с шаблоном base_slug-% или точно совпадающим с base_slug
    query = select(Hotel.slug).where(
        (Hotel.slug == base_slug) | (Hotel.slug.like(f"{base_slug}-%"))
    )

    # Выполняем запрос и получаем все существующие slug
    result = await session.execute(query)
    existing_slugs = result.scalars().all()

    # Если нет совпадений, возвращаем базовый slug
    if not existing_slugs:
        print(f"Уникальный slug создан: {base_slug}")
        return base_slug

    # Находим максимальный числовой суффикс среди существующих slugs
    max_suffix = 0
    for slug in existing_slugs:
        if slug == base_slug:
            max_suffix = max(max_suffix, 1)
        elif slug.startswith(f"{base_slug}-"):
            try:
                suffix = int(slug[len(base_slug) + 1 :])
                max_suffix = max(max_suffix, suffix + 1)
            except ValueError:
                continue

    # Создаем новый slug с суффиксом на единицу больше максимального
    new_slug = f"{base_slug}-{max_suffix}"
    print(f"Создан новый slug с инкрементом: {new_slug}")

    return new_slug


async def generate_slug_for_city(
    session: AsyncSession,
    name: str,
) -> str:
    base_slug = slugify_func(name)

    # Формируем запрос для поиска всех slug, начинающихся с base_slug
    # Используем LIKE с шаблоном base_slug-% или точно совпадающим с base_slug
    query = select(City.slug).where(
        (City.slug == base_slug) | (City.slug.like(f"{base_slug}-%"))
    )

    # Выполняем запрос и получаем все существующие slug
    result = await session.execute(query)
    existing_slugs = result.scalars().all()

    if not existing_slugs:
        print(f"Уникальный slug города создан: {base_slug}")
        return base_slug

    # Находим максимальный числовой суффикс среди существующих slugs
    max_suffix = 0
    for slug in existing_slugs:
        if slug == base_slug:
            max_suffix = max(max_suffix, 1)
        elif slug.startswith(f"{base_slug}-"):
            try:
                suffix = int(slug[len(base_slug) + 1 :])
                max_suffix = max(max_suffix, suffix + 1)
            except ValueError:
                continue

    # Создаем новый slug с суффиксом на единицу больше максимального
    new_slug = f"{base_slug}-{max_suffix}"
    print(f"Создан новый slug города с инкрементом: {new_slug}")

    return new_slug
