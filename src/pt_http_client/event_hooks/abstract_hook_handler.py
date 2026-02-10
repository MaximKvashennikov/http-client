from abc import ABC, abstractmethod
from typing import Any

import httpx


class AbstractHookHandler(ABC):
    """Абстрактный базовый класс для обработчиков событий httpx.

    Обработчики событий позволяют перехватывать запросы и ответы для
    добавления дополнительной функциональности (логирование, метрики,
    прикрепление данных к отчетам и т.д.).

    Документация httpx: https://www.python-httpx.org/advanced/event-hooks/

    Пример:
        class CustomHandler(AbstractHookHandler):
            @staticmethod
            def request_hook(request: httpx.Request) -> None:
                print(f"Request: {request.method} {request.url}")

            @staticmethod
            def response_hook(response: httpx.Response) -> None:
                print(f"Response: {response.status_code}")
    """

    @abstractmethod
    def request_hook(self, request: httpx.Request) -> None:
        """Обработчик события запроса.

        Вызывается перед отправкой HTTP запроса.

        Args:
            request: Объект запроса httpx.
        """
        pass

    @abstractmethod
    def response_hook(self, response: httpx.Response) -> None:
        """Обработчик события ответа.

        Вызывается после получения HTTP ответа.

        Args:
            response: Объект ответа httpx.
        """
        pass

    @staticmethod
    def _truncate_body(data: Any) -> Any:
        """Обрезает тело запроса/ответа.

        Args:
            data: Данные, которые нужно обрезать. Может быть dict, list или str.

        Returns:
            Оригинальные данные, если они короче максимальной длины,
            или обрезанная версия.
        """
        max_body_length = 40000
        truncate_message = "... [Данные обрезаны]"

        if isinstance(data, (dict, list, str)):
            data_str = str(data)
            if len(data_str) > max_body_length:
                return data_str[:max_body_length] + truncate_message

        return data
