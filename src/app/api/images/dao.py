from app.api.images.models import Image
from app.core.db.dao import BaseDAO


class ImageDAO(BaseDAO):
    model = Image
