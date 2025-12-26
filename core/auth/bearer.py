import httpx
from typing import Optional


class BearerTokenAuth(httpx.Auth):
    def __init__(
        self,
        token_url: str,
        client_id: str,
        client_secret: str,
        scope: str,
        grant_type: str = "client_credentials",
    ) -> None:
        """
        :param token_url: URL of the OAuth 2.0 token endpoint
        :param client_id: Client identifier for authentication
        :param client_secret: Client secret for authentication
        :param scope: Optional space-separated list of scopes
        :param grant_type: OAuth 2.0 grant type (default: "client_credentials")
        """
        self.token_url = token_url
        self.client_id = client_id
        self.client_secret = client_secret
        self.scope = scope
        self.grant_type = grant_type

        self._token: Optional[str] = None

    def _fetch_token(self) -> str:
        """Fetch access token"""
        data = {
            "grant_type": self.grant_type,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "scope": self.scope,
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
