import allure
import httpx
import pytest
from tenacity import RetryError, retry, retry_if_result, stop_after_attempt, wait_fixed

from pt_http_client import HttpClient
from pt_http_client.event_hooks.curl_handler import CurlHandler


class TestHttpClient:
    """Тесты для HttpClient."""

    BASE_URL = "https://jsonplaceholder.typicode.com"

    POST_ID_1 = 1
    POST_ID_2 = 2
    POST_ID_99999 = 99999
    POST_ID_999999 = 999999
    LIMIT_5 = 5
    USER_ID_1 = 1
    RETRY_ATTEMPTS = 3
    RETRY_WAIT = 0.1

    def test_with_context_manager(self) -> None:
        """Позитивный: с контекстным менеджером."""
        with HttpClient(base_url=self.BASE_URL) as client:
            response = client.get(f"/posts/{self.POST_ID_1}")
            assert response.status_code == httpx.codes.OK
            data = response.json()
            assert "id" in data
            assert data["id"] == self.POST_ID_1

    def test_without_context_manager(self) -> None:
        """Позитивный: без контекстного менеджера."""
        client = HttpClient(base_url=self.BASE_URL)

        try:
            response = client.get(f"/posts/{self.POST_ID_2}")
            assert response.status_code == httpx.codes.OK
            data = response.json()
            assert data["id"] == self.POST_ID_2
        finally:
            client.close()

    def test_non_200_response(self) -> None:
        """Негативный: код ответа не 200."""
        with HttpClient(base_url=self.BASE_URL) as client:
            response = client.get(f"/posts/{self.POST_ID_99999}")

            assert response.status_code == httpx.codes.NOT_FOUND
            data = response.json()

            assert data == {}

    def test_with_tenacity_retry(self) -> None:
        """Тест с retry тенасити при 404."""

        def is_404_response(value: httpx.Response) -> bool:
            print(value)
            # Используем set вместо tuple
            error_codes = {httpx.codes.NOT_FOUND, httpx.codes.INTERNAL_SERVER_ERROR}
            return value.status_code in error_codes

        retry_decorator = retry(
            stop=stop_after_attempt(self.RETRY_ATTEMPTS),
            wait=wait_fixed(self.RETRY_WAIT),
            retry=retry_if_result(is_404_response),
        )

        with HttpClient(base_url=self.BASE_URL) as client:
            with pytest.raises(RetryError) as exc_info:
                client.get(f"/posts/{self.POST_ID_999999}", retry=retry_decorator)

            assert "RetryError" in str(exc_info.type)

    def test_with_params_and_add_hook(self) -> None:
        """Тест с передачей параметров."""
        with HttpClient(base_url=self.BASE_URL) as client:
            response = client.get("/posts", params={"userId": self.USER_ID_1, "_limit": self.LIMIT_5})
            assert response.status_code == httpx.codes.OK
            data = response.json()
            assert len(data) <= self.LIMIT_5

            client.add_handler(CurlHandler())

            with allure.step("POST с JSON"):
                response = client.post("/posts", json={"title": "Test", "body": "Content", "userId": self.USER_ID_1})
                assert response.status_code == httpx.codes.CREATED
