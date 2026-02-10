import allure
import httpx
from curlify2 import Curlify

from .abstract_hook_handler import AbstractHookHandler


class CurlHandler(AbstractHookHandler):
    """Обработчик для генерации cURL команд из HTTP запросов."""

    def request_hook(self, request: httpx.Request) -> None:
        """Хук для обработки запроса.

        Генерирует cURL команду из запроса и прикрепляет ее к Allure отчету.

        """
        try:
            curl_command = Curlify(request).to_curl()

            # Заменяем некорректные значения в теле запроса, bug библиотеки
            curl_command = curl_command.replace("-d 'b'''", "-d 'None'")

            allure.attach(
                body=curl_command,
                name=f"cURL Command: {request.method} {request.url.path}",
                attachment_type=allure.attachment_type.TEXT,
            )

        except Exception as e:
            allure.attach(
                body=f"Failed to generate cURL: {e!s}\nRequest: {request.method} {request.url}",
                name="cURL Generation Error",
                attachment_type=allure.attachment_type.TEXT,
            )

    def response_hook(self, response: httpx.Response) -> None:
        """Для cURL команд ответ не требуется, метод оставляем пустым."""
        pass
