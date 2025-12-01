from __future__ import annotations
import httpx
from typing import Any
from pydantic import ValidationError
from .exceptions import UnexpectedStatusError
from .base import BaseHttpClient
from .types import ReqModel, RespModel


class HttpClient(BaseHttpClient):
    """
    High-level synchronous HTTP client.

    Adds:
        - optional request_model serialization (Pydantic v2)
        - optional response_model validation
        - expected status code verification
        - convenience HTTP methods (get, post, put, patch, delete)
    """

    def send(
        self,
        method: str,
        url: str,
        request_model: ReqModel | None = None,
        response_model: type[RespModel] | None = None,
        expected_status: int | None = None,
        headers: dict[str, str] | None = None,
        **kwargs: Any,
    ) -> RespModel | httpx.Response:
        """
        Unified high-level request handler.
        """

        if request_model is not None:
            if "json" in kwargs:
                raise ValueError("Pass either request_model or json, not both.")
            kwargs["json"] = request_model.model_dump(by_alias=True)

        if headers:
            kwargs.setdefault("headers", {}).update(headers)

        response = super().request(method, url, **kwargs)

        # status check
        if expected_status is not None and response.status_code != expected_status:
            raise UnexpectedStatusError(
                f"Expected {expected_status}, got {response.status_code}. "
                f"Response: {response.text}"
            )

        # no response model → return raw response
        if not response_model:
            return response

        # validate response
        try:
            return response_model.model_validate(response.json())
        except (ValueError, ValidationError) as e:
            raise ValidationError(
                f"Failed to validate response as {response_model.__name__}: {e}"
            ) from e

    def get(
        self,
        url: str,
        response_model: type[RespModel] | None = None,
        expected_status: int | None = None,
        headers: dict[str, str] | None = None,
        **kwargs: Any,
    ):
        return self.send(
            "GET", url,
            response_model=response_model,
            expected_status=expected_status,
            headers=headers,
            **kwargs
        )

    def post(
        self,
        url: str,
        request_model: ReqModel | None = None,
        response_model: type[RespModel] | None = None,
        expected_status: int | None = None,
        headers: dict[str, str] | None = None,
        **kwargs: Any,
    ):
        return self.send(
            "POST", url,
            request_model=request_model,
            response_model=response_model,
            expected_status=expected_status,
            headers=headers,
            **kwargs
        )

    def put(
        self,
        url: str,
        request_model: ReqModel | None = None,
        response_model: type[RespModel] | None = None,
        expected_status: int | None = None,
        headers: dict[str, str] | None = None,
        **kwargs: Any,
    ):
        return self.send(
            "PUT", url,
            request_model=request_model,
            response_model=response_model,
            expected_status=expected_status,
            headers=headers,
            **kwargs
        )

    def patch(
        self,
        url: str,
        request_model: ReqModel | None = None,
        response_model: type[RespModel] | None = None,
        expected_status: int | None = None,
        headers: dict[str, str] | None = None,
        **kwargs: Any,
    ):
        return self.send(
            "PATCH", url,
            request_model=request_model,
            response_model=response_model,
            expected_status=expected_status,
            headers=headers,
            **kwargs
        )

    def delete(
        self,
        url: str,
        response_model: type[RespModel] | None = None,
        expected_status: int | None = None,
        headers: dict[str, str] | None = None,
        **kwargs: Any,
    ):
        return self.send(
            "DELETE", url,
            response_model=response_model,
            expected_status=expected_status,
            headers=headers,
            **kwargs
        )
