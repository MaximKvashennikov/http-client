from __future__ import annotations

import httpx
from typing import Callable, Dict, Any


class BaseHttpClient:
    """
    Low-level synchronous HTTP client.

    Responsibilities:
        - configure httpx.Client
        - apply authorization
        - apply retry decorator (if provided)
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
            retry_decorator: Callable | None = None,
    ):
        self.base_url = base_url.rstrip("/")
        self.retry_decorator = retry_decorator

        headers = default_headers.copy() if default_headers else {}

        if auth_token:
            headers["Authorization"] = f"Bearer {auth_token}"

        self.client = httpx.Client(
            base_url=self.base_url,
            timeout=timeout,
            verify=verify,
            headers=headers,
        )

    def request(self, method: str, url: str, **kwargs: Any) -> httpx.Response:
        """
        Execute a raw HTTP request with optional retry support.
        """

        def do():
            return self.client.request(method, url, **kwargs)

        if self.retry_decorator:
            return self.retry_decorator(do)()

        return do()

    def close(self) -> None:
        """Close underlying httpx.Client."""
        self.client.close()
