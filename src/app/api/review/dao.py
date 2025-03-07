from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dao import BaseDAO

from .models import Review, ReviewCategory, ReviewCategoryRating
from .schemas import ReviewCreate


class ReviewDAO(BaseDAO):
    model = Review


class ReviewCategoryDAO(BaseDAO):
    model = ReviewCategory


class ReviewCategoryRatingDAO(BaseDAO):
    model = ReviewCategoryRating
