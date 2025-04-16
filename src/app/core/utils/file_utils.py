import os
import shutil
from io import BytesIO

import aiofiles
from fastapi import HTTPException, UploadFile, status
from PIL import Image

from app.core.exceptions.http_exceptions import BadRequestException

from ..config import settings


async def validate_and_save_file(
    file: UploadFile,
    filename: str,
    target_format: str = "webp",
    allowed_formats: list[str] = None,
    folder: str = None,
) -> str:
    """
    Validates image format and saves file in one operation.

    Args:
        file: UploadFile to process
        filename: Name for the saved file (without extension)
        target_format: Format to convert the image to (default: webp)
        allowed_formats: List of allowed formats (default: ["JPEG", "JPG", "PNG"])

    Returns:
        str: Path to the saved file
    """
    if allowed_formats is None:
        allowed_formats = ["JPEG", "JPG", "PNG"]

    try:
        # Read file contents once
        contents = await file.read()

        # Validate image and format
        img = Image.open(BytesIO(contents))
        # if img.format not in allowed_formats:
        #     raise HTTPException(
        #         status_code=status.HTTP_400_BAD_REQUEST,
        #         detail=f"File must be one of: {', '.join(allowed_formats)}",
        #     )

        # Prepare directory path
        directory = settings.upload_path
        if folder:
            directory = os.path.join(directory, folder)
        # Ensure upload directory exists
        os.makedirs(directory, exist_ok=True)
        # Prepare full path
        full_path = os.path.join(
            directory,
            f"{filename}.{target_format}",
        )

        # Save optimized image
        async with aiofiles.open(full_path, "wb") as afile:
            # Convert to target format
            output = BytesIO()
            img.save(output, format=target_format, optimize=True)
            await afile.write(output.getvalue())

        return full_path

    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise BadRequestException(
            f"Error processing image: {str(e)}",
        )


# Специализированные функции для разных случаев
async def save_photo(
    file: UploadFile,
    filename: str,
    folder: str = None,
) -> str:
    """Saves general photo, accepting JPEG, JPG, or PNG"""
    return await validate_and_save_file(
        file=file,
        filename=filename,
        allowed_formats=["JPEG", "JPG", "PNG"],
        folder=folder,
    )


async def save_png(
    file: UploadFile,
    filename: str,
    folder: str = None,
) -> str:
    """Saves PNG only images"""
    return await validate_and_save_file(
        file=file,
        filename=filename,
        allowed_formats=["PNG"],
        folder=folder,
    )


async def delete_hotel_folder(
    hotel_id: int,
    hotel_domain: str,
) -> None:
    """
    Deletes hotel's media folder with all contents

    Args:
        hotel_id: ID of the hotel
    """
    folder_path = os.path.join(
        settings.upload_path,
        f"hotel_{hotel_id}",
    )
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)


async def delete_photo(
    photo_path: str,
) -> None:
    if os.path.exists(photo_path):
        os.remove(photo_path)
