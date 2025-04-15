from sqlalchemy.ext.asyncio import AsyncSession
from app.dao import BaseDAO
from app.dao.hotel import HotelDAO
from app.models.favorites import UserFavorite
from app.schemas.favorites import UserFavoriteFilter
from app.schemas.hotel import HotelFilter


class UserFavoriteDAO(BaseDAO):
    model = UserFavorite

    @classmethod
    async def get_user_favorites(
        cls,
        session: AsyncSession,
        user_id: int,
    ):
        favorite_hotels = await cls.get_all(
            session=session,
            filters=UserFavoriteFilter(
                user_id=user_id,
            ),
        )
        favorites = []
        for favorite_hotel in favorite_hotels:
            hotel = await HotelDAO.get_full_hotel_by_id(
                session=session,
                hotel_id=favorite_hotel.hotel_id,
            )
            favorites.append(hotel)
        return favorites
