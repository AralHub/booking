
from fastapi import APIRouter

# from app.models.chessboard import

router = APIRouter()


# @router.get("/room-types/{room_type_id}/availability")
# async def get_room_availability(
#     room_type_id: int,
#     start_date: date,
#     end_date: date,
#     session=SessionDep,
# ):
#     result = await session.execute(
#         select(RoomAvailability)
#         .where(
#             RoomAvailability.room_type_variant_id == room_type_id,
#             RoomAvailability.check_date >= start_date,
#             RoomAvailability.check_date <= end_date,
#         )
#         .order_by(RoomAvailability.check_date)
#     )
#     availabilities = result.scalars().all()
#     return availabilities


# @router.put("/room-types/{room_type_id}/availability/{check_date}")
# async def update_room_availability(
#     room_type_id: int,
#     check_date: date,
#     availability_data: dict,
#     session=SessionDep,
# ):
#     pass
