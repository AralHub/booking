__all__ = (
    "main_app",
    "main",
)

from core.config import settings
from core.gunicorn import Application, get_app_options
from main import main_app


def main():
    Application(
        application=main_app,
        options=get_app_options(
            host=settings.gunicorn.HOST,
            port=settings.gunicorn.PORT,
            timeout=settings.gunicorn.TIMEOUT,
            workers=settings.gunicorn.WORKERS,
            log_level=settings.logging_config.LOG_LEVEL,
        ),
    ).run()


if __name__ == "__main__":
    main()
