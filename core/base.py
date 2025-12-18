from __future__ import annotations

import httpx
from typing import Dict, Any


class BaseHttpClient:
    """
    Low-level synchronous HTTP client.

    Responsibilities:
        - configure httpx.Client
        - apply authorization
        - provide unified request() method for high-level client

    High-level functionality (validation, status checks, models)
    is implemented in HttpClient which inherits from this class.
    """

    def __init__(
        self,
        base_url: str,
        timeout: float = 10.0,
        verify: bool = True,
        auth_token: str | None = None,
        default_headers: Dict[str, str] | None = None,
    ):
        self.base_url = base_url.rstrip("/")

        headers = default_headers.copy() if default_headers else {}

        if auth_token:
            headers["Authorization"] = f"Bearer {auth_token}"

        self.client = httpx.Client(
            base_url=self.base_url,
            timeout=timeout,
            verify=verify,
            headers=headers,
        )

    def _request(self, method: str, url: str, **kwargs: Any) -> httpx.Response:
        """
        Raw HTTP request with automatic status check.

        :raises httpx.HTTPStatusError: If response status is 400-599
        """
        response = self.client.request(method, url, **kwargs)
        response.raise_for_status()
        return response

    def close(self) -> None:
        """Close underlying httpx.Client."""
        self.client.close()
