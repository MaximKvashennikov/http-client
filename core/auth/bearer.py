import httpx
from typing import Optional


class BearerTokenAuth(httpx.Auth):
    """OAuth 2.0 Bearer Token аутентификация для httpx.

    Класс реализует поток аутентификации OAuth 2.0 с получением токена
    по логину/паролю и автоматическим добавлением Bearer токена в заголовки.

    Основные возможности:
        - Автоматическое получение access token при первом запросе
        - Добавление Bearer токена в заголовки всех запросов
        - Поддержка принудительного обновления токена
        - Интеграция с httpx через протокол Auth

    Атрибуты:
        token_url: URL endpoint для получения токена
        client_id: Идентификатор клиента для аутентификации
        client_secret: Секрет клиента для аутентификации
        username: Имя пользователя
        password: Пароль пользователя
        scope: Список scope через пробел
        response_type: Тип ответа OAuth
        grant_type: Тип grant OAuth 2.0
        _token: Текущий access token (кешируется)
    """

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
        self.token_url = token_url
        self.client_id = client_id
        self.client_secret = client_secret
        self.username = username
        self.password = password
        self.scope = scope
        self.response_type = response_type
        self.grant_type = grant_type

        self._token: Optional[str] = None

    def _fetch_token(self) -> str:
        """Fetch access token"""
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
            verify=False,
        )
        response.raise_for_status()

        token_data = response.json()
        return token_data["access_token"]

    def auth_flow(self, request: httpx.Request):
        """Authentication flow that adds Bearer token to request headers."""
        if self._token is None:
            self._token = self._fetch_token()

        request.headers["Authorization"] = f"Bearer {self._token}"
        yield request

    def refresh_token(self) -> str:
        """Force refresh the access token."""
        self._token = self._fetch_token()
        return self._token
