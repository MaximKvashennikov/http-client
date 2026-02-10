import json

import allure
import httpx

from .abstract_hook_handler import AbstractHookHandler


class AllureHandler(AbstractHookHandler):
    """Обработчик для прикрепления запросов и ответов в Allure."""

    def request_hook(self, request: httpx.Request) -> None:
        """Хук для обработки запроса."""
        body = request.content.decode("utf-8")
        try:
            body = json.loads(body)
        except json.JSONDecodeError:
            pass

        request_info = {
            "method": request.method,
            "url": str(request.url),
            "headers": dict(request.headers),
            "params": dict(request.url.params) or None,
            "body": self._truncate_body(body),
        }

        allure.attach(
            body=json.dumps(request_info, indent=2, ensure_ascii=False),
            name=f"Request: {request.method} {request.url.path}",
            attachment_type=allure.attachment_type.JSON,
        )

    def response_hook(self, response: httpx.Response) -> None:
        """Хук для обработки ответа."""
        response.read()

        method = response.request.method
        url = str(response.url)

        try:
            body = response.json()
        except json.JSONDecodeError:
            body = response.text

        response_info = {
            "status_code": response.status_code,
            "elapsed_seconds": response.elapsed.total_seconds(),
            "body": self._truncate_body(body) if body else None,
        }

        allure.attach(
            body=json.dumps(response_info, indent=2, ensure_ascii=False),
            name=f"Response: {method} {url}",
            attachment_type=allure.attachment_type.JSON,
        )
