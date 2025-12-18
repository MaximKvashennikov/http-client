from __future__ import annotations

import json
import httpx
import allure
from curlify2 import Curlify
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

    @staticmethod
    def _attach_request(method: str, url: str, request_data: Any = None) -> None:
        """Attach request information to Allure report."""

        if request_data is not None:
            allure.attach(
                body=json.dumps(request_data, indent=2, ensure_ascii=False),
                name=f"Request: {method} {url}",
                attachment_type=allure.attachment_type.JSON,
            )

    @staticmethod
    def _attach_curl_command(response: httpx.Response) -> None:
        """Attach cURL command to Allure report."""

        try:
            curl_command = (
                Curlify(response.request).to_curl().replace("-d 'b'''", "-d 'None'")
            )
            allure.attach(
                body=curl_command,
                name="cURL Command",
                attachment_type=allure.attachment_type.TEXT,
            )
        except Exception as e:
            allure.attach(
                body=f"Failed to generate cURL: {str(e)}",
                name="cURL Error",
                attachment_type=allure.attachment_type.TEXT,
            )

    @staticmethod
    def _attach_response(method: str, url: str, response: httpx.Response) -> None:
        """Attach response information to Allure report."""

        response_info = {
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "body": response.json() if response.text else None,
        }

        allure.attach(
            body=json.dumps(response_info, indent=2, ensure_ascii=False),
            name=f"Response: {method} {url}",
            attachment_type=allure.attachment_type.JSON,
        )

        allure.attach(
            body=f"Status: {response.status_code}\n\n{response.text}",
            name=f"Response Raw: {method} {url}",
            attachment_type=allure.attachment_type.TEXT,
        )

    @allure.step("{method} {url}")
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
            json_data = request_model.model_dump(by_alias=True)
            kwargs["json"] = json_data

            # Attach request
            self._attach_request(method, url, request_data=json_data)

        if headers:
            kwargs.setdefault("headers", {}).update(headers)

        response = super().request(method, url, **kwargs)

        # Attach cURL command and response
        self._attach_curl_command(response)
        self._attach_response(method, url, response)

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
            "GET",
            url,
            response_model=response_model,
            expected_status=expected_status,
            headers=headers,
            **kwargs,
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
            "POST",
            url,
            request_model=request_model,
            response_model=response_model,
            expected_status=expected_status,
            headers=headers,
            **kwargs,
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
            "PUT",
            url,
            request_model=request_model,
            response_model=response_model,
            expected_status=expected_status,
            headers=headers,
            **kwargs,
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
            "PATCH",
            url,
            request_model=request_model,
            response_model=response_model,
            expected_status=expected_status,
            headers=headers,
            **kwargs,
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
            "DELETE",
            url,
            response_model=response_model,
            expected_status=expected_status,
            headers=headers,
            **kwargs,
        )
