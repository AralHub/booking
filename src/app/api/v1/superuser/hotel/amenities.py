from fastapi import APIRouter, Depends

from app.api.dependencies.amenities import validate_hotel_amenities_category
from app.api.dependencies.user import get_current_superuser
from app.core import SessionDep, TransactionSessionDep
from app.core.i18n.responses import RESPONSE_MESSAGES, DataResponse, ListResponse
from app.dao.hotel import HotelAmenityDAO
from app.dao.hotel.amenities import (
    HotelAmenityCategoryDAO,
)
from app.schemas.hotel.amenities import (
    HotelAmenityCategoryCreate,
    HotelAmenityCategoryCreateInternal,
    HotelAmenityCategoryFilter,
    HotelAmenityCategoryRead,
    HotelAmenityCategoryUpdate,
    HotelAmenityCategoryWithAmenities,
    HotelAmenityCreate,
    HotelAmenityCreateInternal,
    HotelAmenityFilter,
    HotelAmenityRead,
    HotelAmenityUpdate,
)

router = APIRouter(
    tags=["Superuser Hotel Amenities"],
    prefix="/hotel-amenities",
)


@router.get(
    "",
    response_model=ListResponse[HotelAmenityCategoryWithAmenities],
)
async def get_all_hotel_amenities(
    session=SessionDep,
):
    """
    Все удобства отеля разделенные по категориям
    """
    hotel_amenities = await HotelAmenityCategoryDAO.get_all_amenities(
        session=session,
    )
    return ListResponse(
        data=hotel_amenities,
        total=len(hotel_amenities),
    )


@router.post(
    "/categories/{category_id}/amenities",
    response_model=DataResponse[HotelAmenityRead],
)
async def create_hotel_amenity(
    category_id: int,
    hotel_amenity_data: HotelAmenityCreate,
    validate_hotel_amenities_category: HotelAmenityCategoryRead = Depends(
        validate_hotel_amenities_category
    ),
    session=TransactionSessionDep,
):
    """
    Удобства по категории-удобств отеля
    """
    created_amenity = await HotelAmenityDAO.create(
        session=session,
        values=HotelAmenityCreateInternal(
            name=hotel_amenity_data.to_dict_name(),
            hotel_amenity_category_id=category_id,
        ),
    )
    return DataResponse(
        data=created_amenity,
        message=RESPONSE_MESSAGES.get(
            "DATA_CREATED",
            "Hotel amenity created successfully",
        ),
    )


@router.put(
    "/amenities/{amenity_id}",
    dependencies=[Depends(get_current_superuser)],
    response_model=DataResponse[HotelAmenityRead],
)
async def update_hotel_amenity(
    category_id: int,
    amenity_id: int,
    amenity_update_data: HotelAmenityUpdate,
    session=TransactionSessionDep,
):
    """
    Обновить удобство в категории
    """
    updated_amenity = await HotelAmenityDAO.update(
        session=session,
        filters=HotelAmenityFilter(
            id=amenity_id,
            hotel_amenity_category_id=category_id,
        ),
        values=amenity_update_data,
    )
    return DataResponse(
        data=updated_amenity,
        message=RESPONSE_MESSAGES.get(
            "DATA_UPDATED",
            "Hotel amenity updated successfully",
        ),
    )


@router.delete(
    "/amenities/{amenity_id}",
    response_model=DataResponse[dict],
)
async def delete_hotel_amenity(
    amenity_id: int,
    session=TransactionSessionDep,
):
    await HotelAmenityDAO.delete(
        session=session,
        filters=HotelAmenityFilter(
            id=amenity_id,
        ),
    )
    return DataResponse(
        data={"id": amenity_id},
        message=RESPONSE_MESSAGES.get(
            "DATA_DELETED",
            "Hotel amenity deleted successfully",
        ),
    )


@router.post(
    "/categories",
    response_model=DataResponse[HotelAmenityCategoryRead],
)
async def create_hotel_amenities_category(
    hotel_amenity_category_data: HotelAmenityCategoryCreate,
    session=TransactionSessionDep,
):
    """
    Создать категорию удобств отеля
    """
    created_category = await HotelAmenityCategoryDAO.create(
        session=session,
        values=HotelAmenityCategoryCreateInternal(
            name=hotel_amenity_category_data.to_dict_name(),
        ),
    )
    return DataResponse(
        data=created_category,
        message=RESPONSE_MESSAGES.get(
            "DATA_CREATED",
            "Hotel amenities category created successfully",
        ),
    )


@router.put(
    "/categories/{category_id}",
    dependencies=[Depends(get_current_superuser)],
    response_model=DataResponse[HotelAmenityCategoryRead],
)
async def update_hotel_amenities_category(
    category_id: int,
    amenity_update_data: HotelAmenityCategoryUpdate,
    hotel_amenities_category=Depends(validate_hotel_amenities_category),
    session=TransactionSessionDep,
):
    """
    Обновить удобство в категории
    """
    updated_category = await HotelAmenityCategoryDAO.update(
        session=session,
        filters=HotelAmenityCategoryFilter(
            id=category_id,
        ),
        values=amenity_update_data,
    )
    return DataResponse(
        data=updated_category,
        message=RESPONSE_MESSAGES.get(
            "DATA_UPDATED",
            "Hotel amenities category updated successfully",
        ),
    )


@router.delete(
    "/categories/{category_id}",
    response_model=DataResponse[dict],
)
async def delete_hotel_amenities_category(
    category_id: int,
    hotel_amenities_category=Depends(validate_hotel_amenities_category),
    session=TransactionSessionDep,
):
    """
    Удалить категорию удобств отеля
    """

    await HotelAmenityCategoryDAO.delete(
        session=session,
        filters=HotelAmenityCategoryFilter(
            id=hotel_amenities_category.id,
        ),
    )
    return DataResponse(
        data={"id": category_id},
        message=RESPONSE_MESSAGES.get(
            "DATA_DELETED",
            "Hotel amenities category deleted successfully",
        ),
    )
