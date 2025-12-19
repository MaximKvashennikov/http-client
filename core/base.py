from __future__ import annotations

import httpx
from typing import Dict, Any, Optional


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
        verify: bool = False,
        auth: Optional[httpx.Auth] = None,
        default_headers: Dict[str, str] | None = None,
        **client_kwargs: Any,
    ):
        """
        Initialize low-level HTTP client.

        :param base_url: Base URL for all requests (e.g., "https://api.example.com/v1")
        :param timeout: Request timeout in seconds (default: 10.0)
        :param verify: SSL certificate verification (default: True)
        :param auth: Authentication object (BasicAuth, BearerToken, etc.)
        :param default_headers: Default headers for all requests
        :param client_kwargs: Additional parameters passed to httpx.Client().
                             See httpx documentation for all available options:
                             https://www.python-httpx.org/api/#client
        """
        self.base_url = base_url.rstrip("/")

        headers = default_headers.copy() if default_headers else {}

        self.client = httpx.Client(
            base_url=self.base_url,
            timeout=timeout,
            verify=verify,
            auth=auth,
            headers=headers,
            **client_kwargs,
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
