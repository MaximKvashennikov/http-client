from __future__ import annotations

import httpx
from typing import Any, Callable
from core.event_hooks.abstract_hook_handler import AbstractHookHandler
from core.event_hooks.curl_handler import CurlHandler
from core.event_hooks.allure_handler import AllureHandler
from core.event_hooks.logging_handler import LoggingHandler


class HttpClient:
    """HTTP клиент для выполнения синхронных запросов.

    Класс предоставляет простой интерфейс для работы с HTTP API с поддержкой
    retry логики через декораторы и автоматическим управлением соединением.

    Основные возможности:
        - Автоматическое создание и закрытие соединения
        - Поддержка всех HTTP методов (GET, POST, PUT, PATCH, DELETE)
        - Передача параметров запроса (params, json, headers)
        - Интеграция с retry декораторами (tenacity)
        - Контекстный менеджер для безопасной работы

    Атрибуты:
        base_url: Базовый URL для всех запросов
        timeout: Таймаут запроса по умолчанию в секундах
        verify: Флаг проверки SSL сертификатов
        auth: Объект аутентификации httpx
        default_headers: Заголовки по умолчанию для всех запросов
        client_kwargs: Дополнительные параметры для httpx.Client

    Примеры:
        >>> with HttpClient(base_url="https://api.example.com") as client:
        ...     response = client.get("/users/1")
        ...     print(response.json())
    """

    def __init__(
        self,
        base_url: str,
        timeout: float = 10.0,
        verify: bool = False,
        auth: httpx.Auth | None = None,
        default_headers: dict[str, str] | None = None,
        handlers: list[AbstractHookHandler] | None = None,
        **client_kwargs: Any,
    ) -> None:
        """Инициализирует HTTP клиент.

        Args:
            base_url: Базовый URL для всех запросов
                Пример: "https://api.example.com/v1"
            timeout: Таймаут запроса по умолчанию в секундах
            verify: Флаг проверки SSL сертификатов
            auth: Объект аутентификации httpx (BasicAuth, BearerToken и т.д.)
            default_headers: Заголовки по умолчанию для всех запросов
            handlers: Обработчики запросов/ответов, см. AbstractHookHandler
            **client_kwargs: Дополнительные параметры для httpx.Client
                См. документацию httpx: https://www.python-httpx.org/api/#client

        """

        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.verify = verify
        self.auth = auth
        self.default_headers = default_headers.copy() if default_headers else {}
        self.client_kwargs = client_kwargs
        self._client: httpx.Client | None = None

        self._handlers: list[AbstractHookHandler] = handlers or [
            AllureHandler(),
            CurlHandler(),
            LoggingHandler(),
        ]

    def __enter__(self) -> HttpClient:
        self._setup_client()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()

    def __del__(self):
        self.close()

    def _update_client_hooks(self) -> None:
        """Обновляет event_hooks существующего клиента."""
        if self._client:
            request_hooks = [hook.request_hook for hook in self._handlers]
            response_hooks = [hook.response_hook for hook in self._handlers]

            self._client.event_hooks["request"] = request_hooks
            self._client.event_hooks["response"] = response_hooks

    def add_handler(self, handler: AbstractHookHandler) -> HttpClient:
        """Добавляет обработчик, обновляет хуки клиента"""
        self._handlers.append(handler)

        if self._client:
            self._update_client_hooks()

        return self

    def _setup_client(self) -> httpx.Client:
        """Создает клиент httpx если он еще не создан."""
        if self._client is None:
            self._client = httpx.Client(
                base_url=self.base_url,
                timeout=self.timeout,
                verify=self.verify,
                auth=self.auth,
                headers=self.default_headers,
                **self.client_kwargs,
            )
            self._update_client_hooks()

        return self._client

    def close(self) -> None:
        """Закрытие клиента httpx."""
        if self._client:
            self._client.close()
            self._client = None

    def _send(
        self,
        method: str,
        url: str,
        headers: dict[str, str] | None = None,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
        retry: Callable | None = None,
        **kwargs: Any,
    ) -> httpx.Response:
        """Приватный метод для выполнения HTTP запроса c retry."""

        client = self._setup_client()

        def do_request() -> httpx.Response:
            return client.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                json=json,
                **kwargs,
            )

        return retry(do_request)() if retry else do_request()

    def get(
        self,
        url: str,
        headers: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
        retry: Callable | None = None,
        **kwargs: Any,
    ) -> httpx.Response:
        """Выполнить GET запрос."""
        return self._send(
            method="GET",
            url=url,
            headers=headers,
            params=params,
            json=json,
            retry=retry,
            **kwargs,
        )

    def post(
        self,
        url: str,
        headers: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
        retry: Callable | None = None,
        **kwargs: Any,
    ) -> httpx.Response:
        """Выполнить POST запрос."""
        return self._send(
            method="POST",
            url=url,
            headers=headers,
            params=params,
            json=json,
            retry=retry,
            **kwargs,
        )

    def put(
        self,
        url: str,
        headers: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
        retry: Callable | None = None,
        **kwargs: Any,
    ) -> httpx.Response:
        """Выполнить PUT запрос."""
        return self._send(
            method="PUT",
            url=url,
            headers=headers,
            params=params,
            json=json,
            retry=retry,
            **kwargs,
        )

    def patch(
        self,
        url: str,
        headers: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
        retry: Callable | None = None,
        **kwargs: Any,
    ) -> httpx.Response:
        """Выполнить PATCH запрос."""
        return self._send(
            method="PATCH",
            url=url,
            headers=headers,
            params=params,
            json=json,
            retry=retry,
            **kwargs,
        )

    def delete(
        self,
        url: str,
        headers: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
        retry: Callable | None = None,
        **kwargs: Any,
    ) -> httpx.Response:
        """Выполнить DELETE запрос."""
        return self._send(
            method="DELETE",
            url=url,
            headers=headers,
            params=params,
            json=json,
            retry=retry,
            **kwargs,
        )
