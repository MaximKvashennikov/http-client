"""
Пример использования HttpClient с публичным Petstore API.
"""

import httpx
from tenacity import retry, stop_after_attempt, wait_fixed
from core import HttpClient
from examples.petstore_models import Pet


def test_petstore():
    # конфигурация retry (опционально)
    retry_decorator = retry(
        stop=stop_after_attempt(3), wait=wait_fixed(2), reraise=True
    )

    # создаём клиент — public petstore swagger (v2)
    client = HttpClient(
        base_url="https://petstore.swagger.io/v2",
        default_headers={"User-Agent": "qa-http-client/1.0"},
        auth=httpx.BasicAuth(username="username", password="secret"),
    )

    pet_req = Pet(
        id=123456789,
        name="test-pet",
        photo_urls=["https://example.com/pet.jpg"],
        status="available",
    )

    # POST /pet -> возвращает объект Pet и статус 200
    created = client.post(
        "/pet",
        request_model=pet_req,
        # response_model=Pet,
        expected_status=200,
        retry=retry_decorator,
    )
    print("Created:", created.json())

    # GET /pet/{petId}
    fetched = client.get(f"/pet/{pet_req.id}", response_model=Pet, expected_status=200)
    print("Fetched:", fetched)

    resp = client.delete(f"/pet/{pet_req.id}", expected_status=200)
    print("Delete raw response status:", resp.status_code)

    client.close()


def test_basic_auth():
    # Test with Basic Auth
    client = HttpClient(
        base_url="https://httpbin.org",
        auth=httpx.BasicAuth("user", "pass"),  # правильные креденшелы
    )

    client.get("/basic-auth/user/pass", expected_status=200)
    print("Basic Auth works!")

    # Test with wrong credentials
    client_wrong = HttpClient(
        base_url="https://httpbin.org",
        auth=httpx.BasicAuth("wrong", "wrong"),  # неправильные
    )

    try:
        client_wrong.get("/basic-auth/user/pass")
    except Exception as e:
        print(f"Auth failed as expected: {e}")
