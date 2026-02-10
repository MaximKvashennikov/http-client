import json
import logging

import httpx

from .abstract_hook_handler import AbstractHookHandler


class LoggingHandler(AbstractHookHandler):
    """Простой обработчик для логирования HTTP запросов."""

    def __init__(self, logger: logging.Logger | None = None) -> None:
        """Инициализирует обработчик логирования.

        Args:
            logger: Логгер для записи сообщений. Если не передан,
                    используется логгер с именем текущего модуля.
        """
        self.logger = logger or logging.getLogger(__name__)

    def request_hook(self, request: httpx.Request) -> None:
        """Хук для логирования запроса."""
        self.logger.info(f"Запрос: {request.method} {request.url}")
        self.logger.debug(f"Параметры: {dict(request.url.params)}")

    def response_hook(self, response: httpx.Response) -> None:
        """Хук для логирования ответа."""
        response.read()

        try:
            body = response.json()
        except json.JSONDecodeError:
            body = response.text

        response_info = {
            "method": response.request.method,
            "url": response.request.url,
            "status_code": response.status_code,
            "elapsed_seconds": response.elapsed.total_seconds(),
            "body": self._truncate_body(body) if body else None,
        }

        if response.status_code >= httpx.codes.BAD_REQUEST:
            self.logger.warning(f"Ответ: {response.status_code}")
            self.logger.warning(response_info)

        else:
            self.logger.info(f"Ответ: {response.status_code}")
            self.logger.debug(response_info)
