from collections.abc import Generator
from contextlib import contextmanager
from typing import ClassVar

import httpx


class BearerTokenAuth(httpx.Auth):
    """OAuth 2.0 Bearer Token аутентификация для httpx с кешированием токенов.

    Класс реализует аутентификацию OAuth 2.0 с получением токена доступа
    по логину и паролю, автоматическим добавлением Bearer токена в заголовки
    запросов и кешированием токенов для разных пользователей.

    Основные возможности:
        - Автоматическое получение access token при первом запросе
        - Кеширование токенов по хешу пользователя
        - Добавление Bearer токена в заголовки всех запросов
        - Возможность смены пользователя без пересоздания объекта
        - Интеграция с httpx через протокол Auth

    Атрибуты:
        token_url: URL эндпоинта для получения токена
        client_id: Идентификатор клиента для аутентификации
        client_secret: Секрет клиента для аутентификации
        username: Имя пользователя
        password: Пароль пользователя
        scope: Список разрешений (scope) через пробел
        response_type: Тип ответа OAuth
        grant_type: Тип grant OAuth 2.0
        _current_user_key_hash: Хеш-ключ текущего пользователя

    Пример использования:
        >>> auth = BearerTokenAuth(
        ...     token_url="https://api.example.com/token",
        ...     client_id="client_id",
        ...     client_secret="client_secret",
        ...     username="user1",
        ...     password="pass1",
        ...     scope="read write",
        ...     response_type="token",
        ...     grant_type="password"
        ... )
        >>> client = httpx.Client(auth=auth)
    """

    _token_cache: ClassVar[dict[tuple[str, str], str]] = {}

    def __init__(
        self,
        token_url: str,
        client_id: str,
        client_secret: str,
        username: str,
        password: str,
        scope: str,
        response_type: str,
        grant_type: str,
    ) -> None:
        """Инициализирует аутентификацию Bearer Token."""
        self.token_url = token_url
        self.client_id = client_id
        self.client_secret = client_secret
        self.username = username
        self.password = password
        self.scope = scope
        self.response_type = response_type
        self.grant_type = grant_type

        self._admin_user = username, password
        self._current_user_key = self._admin_user

    def _fetch_token(self) -> str:
        """Получает access token с кешированием.

        Returns:
            Access token в виде строки.
        """
        if self._current_user_key in self._token_cache:
            return self._token_cache[self._current_user_key]

        data = {
            "grant_type": self.grant_type,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "username": self.username,
            "password": self.password,
            "scope": self.scope,
            "response_type": self.response_type,
        }

        response = httpx.post(
            self.token_url,
            data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            verify=False,  # noqa: S501
        )
        response.raise_for_status()

        token_data = response.json()
        token: str = token_data["access_token"]

        self._token_cache[self._current_user_key] = token
        return token

    def auth_flow(self, request: httpx.Request) -> Generator[httpx.Request, httpx.Response]:
        """Реализует поток аутентификации httpx.

        Метод вызывается httpx для каждого запроса. Получает токен
        (из кеша или запросом к серверу) и добавляет его в заголовки
        запроса в формате "Bearer {token}".

        Args:
            request: Объект запроса httpx

        Yields:
            Модифицированный объект запроса с заголовком Authorization

        Note:
            Является частью протокола httpx.Auth, вызывается автоматически
            при каждом запросе через клиент httpx.
        """
        token = self._fetch_token()
        request.headers["Authorization"] = f"Bearer {token}"
        yield request

    def _update_user(self, username: str, password: str) -> None:
        """Обновить пользователя."""
        self.username = username
        self.password = password
        self._current_user_key = (self.username, self.password)

    @contextmanager
    def switch_to_user(self, username: str, password: str) -> Generator[None]:
        """Временно переключиться на другого пользователя.

        При выходе из контекстного менеджера переключается на пользователя-администратора.

        Example:
            >>> auth = BearerTokenAuth(...)
            >>> with auth.switch_to_user('user1', 'pass1'):
            ...     client.get("/api")  # Запрос от user1
            >>> # Автоматически вернулся к admin
        """
        self._update_user(username=username, password=password)
        yield
        self._switch_to_admin()

    def _switch_to_admin(self) -> None:
        """Переключиться на пользователя-администратора.

        Администратором считаем пользователя, под которым инициализируется класс.
        """
        self._update_user(*self._admin_user)
