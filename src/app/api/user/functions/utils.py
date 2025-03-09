import uuid
from datetime import UTC, datetime, timedelta
from pathlib import Path

import bcrypt
import jwt

from app.core.config import settings

# from app.core.utils.eskiz_client import code_generator
from app.core.exceptions.http_exceptions import (
    TooManyRequestsException,
)
from app.core.utils import redis_sms, task_queue


def encode_jwt(
    payload: dict,
    private_key: Path = settings.crypt.PRIVATE_KEY.read_text(),
    algorithm: str = settings.crypt.ALGORITHM,
    expire_minutes: int = settings.crypt.ACCESS_TOKEN_EXPIRE_MINUTES,
    expire_timedelta: timedelta | None = None,
) -> str:
    to_encode = payload.copy()
    now = datetime.now(UTC)
    if expire_timedelta:
        expire = now + expire_timedelta
    else:
        expire = now + timedelta(minutes=expire_minutes)

    to_encode.update(
        exp=expire,
        iat=now,
        jti=str(uuid.uuid4()),
    )
    encoded = jwt.encode(to_encode, private_key, algorithm=algorithm)
    return encoded


def decode_jwt(
    token: str | bytes,
    public_key: Path = settings.crypt.PUBLIC_KEY.read_text(),
    algorithm: str = settings.crypt.ALGORITHM,
) -> dict:
    decoded = jwt.decode(
        token,
        public_key,
        algorithms=algorithm,
    )
    return decoded


def hash_password(
    password: str,
) -> bytes:
    salt = bcrypt.gensalt()
    pwd_bytes: bytes = password.encode()
    return bcrypt.hashpw(pwd_bytes, salt)


async def verify_password(
    password: str,
    hashed_password: str | bytes,
) -> bool:
    pwd_bytes: bytes = password.encode()
    if isinstance(hashed_password, str):
        hashed_password = hashed_password.encode()

    return bcrypt.checkpw(
        password=pwd_bytes,
        hashed_password=hashed_password,
    )


async def send_verification_sms(phone_number: str) -> tuple[bool, str]:
    code = "12345"
    # code = await code_generator()
    success, message = await redis_sms.save_sms_code(
        phone=phone_number,
        code=code,
    )
    if not success:
        raise TooManyRequestsException(message)
    message = f"{settings.eskiz.ESKIZ_TEMPLATE_TEXT} {code}"
    # await task_queue.pool.enqueue_job(
    #     "send_sms_task",
    #     message=message,
    #     phone_number=user_phone_number.phone_number,
    # )
    await task_queue.pool.enqueue_job(
        "send_sms_code",
        message=message,
        phone_number=phone_number,
    )
    return True, "SMS sent successfully"
