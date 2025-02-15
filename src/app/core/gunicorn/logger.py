from logging import Formatter

from core.config import settings
from gunicorn.glogging import Logger


class GunicornLogger(Logger):
    def setup(self, cfg) -> None:
        super().setup(cfg)

        self._set_handler(
            log=self.access_log,
            output=cfg.accesslog,
            fmt=Formatter(fmt=settings.logging_config.LOG_FORMAT),
        )
        self._set_handler(
            log=self.error_log,
            output=cfg.errorlog,
            fmt=Formatter(fmt=settings.logging_config.LOG_FORMAT),
        )
