import os
from enum import Enum
from pathlib import Path
from typing import Literal

# from pydantic import field_validator
from pydantic_settings import BaseSettings
from starlette.config import Config

SOURCE_DIR = Path(__file__).parent.parent.parent
LOG_DEFAULT_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
env_path = os.path.join(SOURCE_DIR, ".env.template")
# env_path = os.path.join(SOURCE_DIR, ".env.prod")
config = Config(env_file=env_path)


class LoggingConfig(BaseSettings):
    LOG_DIR: Path | None = None
    LOG_LEVEL: Literal[
        "DEBUG",
        "INFO",
        "WARNING",
        "ERROR",
        "CRITICAL",
        "EXCEPTION",
    ] = "INFO"
    LOG_FORMAT: str = LOG_DEFAULT_FORMAT


class ApiV1Prefix(BaseSettings):
    prefix: str = "/v1"
    user_prefix: str = "/users"
    superuser_prefix: str = "/superuser"
    hotel_prefix: str = "/hotels"
    room_prefix: str = "/rooms"
    room_type_prefix: str = "/room-types"
    booking_prefix: str = "/bookings"
    country_prefix: str = "/countries"
    review_prefix: str = "/reviews"


class ApiPrefix(BaseSettings):
    prefix: str = "/api"
    auth: str = "/auth"


class RunConfig(BaseSettings):
    HOST: str = config("RUN__HOST", default="0.0.0.0")
    PORT: int = config("RUN__PORT", default=8000)


class GunicornConfig(RunConfig):
    WORKERS: int = config("GUNICORN__WORKERS", default=1)
    TIMEOUT: int = config("GUNICORN__TIMEOUT", default=900)


class AppSettings(BaseSettings):
    APP_NAME: str = config("APP_NAME", default="FastAPI app")
    APP_DESCRIPTION: str | None = config("APP_DESCRIPTION", default=None)
    APP_VERSION: str | None = config("APP_VERSION", default=None)
    LICENSE_NAME: str | None = config("LICENSE_NAME", default=None)
    CONTACT_NAME: str | None = config("CONTACT_NAME", default=None)
    CONTACT_EMAIL: str | None = config("CONTACT_EMAIL", default=None)


class EskizSettings(BaseSettings):
    ESKIZ_EMAIL: str = config("ESKIZ_EMAIL")
    ESKIZ_PASSWORD: str = config("ESKIZ_PASSWORD")
    ESKIZ_TEST_PHONE_NUMBER: str = config("ESKIZ_TEST_PHONE_NUMBER")
    ESKIZ_TEMPLATE_TEXT: str = config(
        "ESKIZ_TEMPLATE_TEXT",
        default="Zmenu ilovasiga kirish uchun tasdiqlash kodi: ",
    )
    ESKIZ_FROM: str = "4546"


class PaymeSettings(BaseSettings):
    PAYME_MERCHANT_ID: str = config("PAYME_MERCHANT_ID")
    PAYME_CASSA_ID: str = config("PAYME_CASSA_ID")
    PAYME_SECRET_KEY: str = config("PAYME_SECRET_KEY")
    PAYME_ACCOUNT_FIELD: str = "restaurant_id"
    PAYME_AMOUNT_FIELD: str = "amount"
    PAYME_RETURN_URL: str = "https://zmenu.uz/"
    PAYME_PROD_URL: str = "https://checkout.paycom.uz/"
    PAYME_TEST_URL: str = "https://test.paycom.uz/"
    PAYME_IS_TEST_MODE: bool = True
    PAY_AMOUNT: int = 100000


class CryptSettings(BaseSettings):
    PRIVATE_KEY: Path = SOURCE_DIR / "certs" / "jwt-private.pem"
    PUBLIC_KEY: Path = SOURCE_DIR / "certs" / "jwt-public.pem"
    ALGORITHM: str = config("ALGORITHM", default="RS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = config("ACCESS_TOKEN_EXPIRE_MINUTES", default=15)
    REFRESH_TOKEN_EXPIRE_DAYS: int = config("REFRESH_TOKEN_EXPIRE_DAYS", default=30)
    TOKEN_TYPE_FIELD: str = config("TOKEN_TYPE_FIELD", default="type")
    ACCESS_TOKEN_TYPE: str = config("ACCESS_TOKEN_TYPE", default="access")
    REFRESH_TOKEN_TYPE: str = config("REFRESH_TOKEN_TYPE", default="refresh")
    REFRESH_TOKEN_HTTPONLY: bool = config("REFRESH_TOKEN_HTTPONLY", default=True)
    REFRESH_TOKEN_COOKIE_SECURE: bool = config(
        "REFRESH_TOKEN_COOKIE_SECURE", default=True
    )
    REFRESH_TOKEN_COOKIE_SAMESITE: str = config(
        "REFRESH_TOKEN_COOKIE_SAMESITE", default="Lax"
    )


class DatabaseSettings(BaseSettings):
    ECHO: bool = config("DB__ECHO", default=False)
    ECHO_POOL: bool = False
    POOL_SIZE: int = 50
    MAX_OVERFLOW: int = 10
    naming_convention: dict[str, str] = {
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_N_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }
    CREATE_TABLES_ON_START: bool = config("DB__CREATE_TABLES_ON_START", default=True)
    DROP_TABLES_ON_START: bool = config("DB__DROP_TABLES_ON_START", default=False)


class PostgresSettings(DatabaseSettings):
    POSTGRES_USER: str = config("POSTGRES_USER", default="postgres")
    POSTGRES_PASSWORD: str = config("POSTGRES_PASSWORD", default="postgres")
    POSTGRES_SERVER: str = config("POSTGRES_SERVER", default="localhost")
    POSTGRES_PORT: int = config("POSTGRES_PORT", default=5432)
    POSTGRES_DB: str = config("POSTGRES_DB", default="postgres")
    POSTGRES_SYNC_PREFIX: str = config("POSTGRES_SYNC_PREFIX", default="postgresql://")
    POSTGRES_ASYNC_PREFIX: str = config(
        "POSTGRES_ASYNC_PREFIX", default="postgresql+asyncpg://"
    )

    @property
    def POSTGRES_URI(self) -> str:
        if not self.POSTGRES_SERVER:
            raise ValueError("POSTGRES_SERVER must be set to a valid host.")
        return (
            f"{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@"
            f"{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/"
            f"{self.POSTGRES_DB}"
        )

    @property
    def POSTGRES_SYNC_URL(self) -> str:
        return f"{self.POSTGRES_SYNC_PREFIX}{self.POSTGRES_URI}"

    @property
    def POSTGRES_ASYNC_URL(self) -> str:
        return f"{self.POSTGRES_ASYNC_PREFIX}{self.POSTGRES_URI}"


class RedisClientSettings(BaseSettings):
    REDIS_HOST: str = config("REDIS_CLIENT_HOST", default="localhost")
    REDIS_PORT: int = config("REDIS_CLIENT_PORT", default=6379)

    @property
    def REDIS_URL(self) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}"


class ClientSideCacheSettings(BaseSettings):
    CLIENT_CACHE_MAX_AGE: int = config("CLIENT_CACHE_MAX_AGE", default=60)


class DefaultRateLimitSettings(BaseSettings):
    DEFAULT_LIMIT: int = config("DEFAULT_RATE_LIMIT_LIMIT", default=1)
    DEFAULT_PERIOD: int = config("DEFAULT_RATE_LIMIT_PERIOD", default=60)


class FirstUserSettings(BaseSettings):
    ADMIN_NAME: str = config("ADMIN_NAME", default="admin")
    ADMIN_PHONE_NUMBER: str = config("ADMIN_PHONE_NUMBER", default="79999999999")
    ADMIN_EMAIL: str = config("ADMIN_EMAIL", default="admin@admin.com")
    ADMIN_USERNAME: str = config("ADMIN_USERNAME", default="admin")
    ADMIN_PASSWORD: str = config("ADMIN_PASSWORD", default="!Ch4ng3Th1sP4ssW0rd!")


class TestSettings(BaseSettings):
    pass


class EnvironmentOption(str, Enum):
    LOCAL = "local"
    STAGING = "staging"
    PRODUCTION = "production"


class EnvironmentSettings(BaseSettings):
    # ENVIRONMENT: EnvironmentOption = config(
    #     "ENVIRONMENT",
    #     default=EnvironmentOption.LOCAL.value,
    # )
    # ENVIRONMENT: str = config("ENVIRONMENT", default=EnvironmentOption.LOCAL.value)
    ENVIRONMENT: str = config.get("ENVIRONMENT", default=EnvironmentOption.LOCAL.value)


class Settings:
    run: RunConfig = RunConfig()
    gunicorn: GunicornConfig = GunicornConfig()
    logging_config: LoggingConfig = LoggingConfig()
    api: ApiPrefix = ApiPrefix()
    api_v1: ApiV1Prefix = ApiV1Prefix()
    app_settings: AppSettings = AppSettings()
    db: DatabaseSettings = DatabaseSettings()
    postgres: PostgresSettings = PostgresSettings()
    eskiz: EskizSettings = EskizSettings()
    payme: PaymeSettings = PaymeSettings()
    crypt: CryptSettings = CryptSettings()
    first_user: FirstUserSettings = FirstUserSettings()
    test: TestSettings = TestSettings()
    redis_client: RedisClientSettings = RedisClientSettings()
    rate_limit: DefaultRateLimitSettings = DefaultRateLimitSettings()
    client_side_cache: ClientSideCacheSettings = ClientSideCacheSettings()
    environment: EnvironmentSettings = EnvironmentSettings()
    upload_path: str = config("UPLOAD_PATH", default="uploads")


settings = Settings()

print(f"Prefix being used: '{settings.api_v1.prefix}'")
print(f"ENVIRONMENT: '{settings.environment.ENVIRONMENT}'")
print(f"ENVIRONMENT_OPTION: '{EnvironmentOption.LOCAL.value}'")
print(f"REDIS_URL: '{settings.redis_client.REDIS_URL}'")
