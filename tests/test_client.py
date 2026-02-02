import allure
import pytest
from tenacity import retry, stop_after_attempt, wait_fixed, RetryError
from core.client import HttpClient
from core.event_hooks.curl_handler import CurlHandler


class TestHttpClient:
    BASE_URL = "https://jsonplaceholder.typicode.com"

    def test_with_context_manager(self):
        """Позитивный: с контекстным менеджером."""
        with HttpClient(base_url=self.BASE_URL) as client:
            response = client.get("/posts/1")
            assert response.status_code == 200
            data = response.json()
            assert "id" in data
            assert data["id"] == 1

    def test_without_context_manager(self):
        """Позитивный: без контекстного менеджера."""
        client = HttpClient(base_url=self.BASE_URL)

        try:
            response = client.get("/posts/2")
            assert response.status_code == 200
            data = response.json()
            assert data["id"] == 2
        finally:
            client.close()

    def test_non_200_response(self):
        """Негативный: код ответа не 200."""
        with HttpClient(base_url=self.BASE_URL) as client:
            response = client.get("/posts/99999")
            # jsonplaceholder возвращает пустой объект для несуществующих постов
            assert response.status_code == 404
            data = response.json()
            # Но данные будут пустыми
            assert data == {}

    def test_with_tenacity_retry(self):
        """Тест с retry тенасити при 404."""
        from tenacity import retry_if_result

        def is_404_response(value):
            print(value)
            return value.status_code in (404, 500)

        # Создаем retry декоратор, который ретраит при 404
        retry_decorator = retry(
            stop=stop_after_attempt(3),
            wait=wait_fixed(0.1),
            retry=retry_if_result(is_404_response),
        )

        with HttpClient(base_url=self.BASE_URL) as client:
            # Делаем запрос с retry - он будет ретраить 3 раза при 404
            with pytest.raises(RetryError) as exc_info:
                client.get("/posts/999999", retry=retry_decorator)

            # Можно проверить что исключение действительно RetryError
            assert "RetryError" in str(exc_info.type)

    def test_with_params_and_add_hook(self):
        """Тест с передачей параметров."""
        with HttpClient(base_url=self.BASE_URL) as client:
            # Простой GET с параметрами
            response = client.get("/posts", params={"userId": 1, "_limit": 5})
            assert response.status_code == 200
            data = response.json()
            assert len(data) <= 5  # Проверяем лимит

            # Добавим хук
            client.add_handler(CurlHandler())

            # POST с JSON
            with allure.step("POST с JSON"):
                response = client.post(
                    "/posts", json={"title": "Test", "body": "Content", "userId": 1}
                )
                assert response.status_code == 201
