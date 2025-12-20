import logging
import sys
from typing import TextIO


class HttpxLoggerConfigurator:
    """
    Configures built-in httpx logger (high-level only).
    """

    def __init__(
        self,
        level: int = logging.DEBUG,
        stream: TextIO | None = sys.stdout
    ) -> None:
        self.level = level
        self.stream = stream

    def configure(self) -> None:
        logger = logging.getLogger("httpx")
        logger.setLevel(self.level)
        logger.propagate = False

        handler = logging.StreamHandler(self.stream)

        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)

        if not logger.handlers:
            logger.addHandler(handler)
