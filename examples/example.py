"""
Пример использования HttpClient с публичным Petstore API.
"""

from tenacity import retry, stop_after_attempt, wait_fixed
from core import HttpClient
from examples.petstore_models import Pet

# конфигурация retry (опционально)
retry_decorator = retry(stop=stop_after_attempt(3), wait=wait_fixed(1))

# создаём клиент — public petstore swagger (v2)
client = HttpClient(
    base_url="https://petstore.swagger.io/v2",
    auth_token=None,  # у public API токен не нужен
    default_headers={"User-Agent": "qa-http-client/1.0"},
    retry_decorator=retry_decorator
)

pet_req = Pet(
    id=123456789,
    name="test-pet",
    photo_urls=["https://example.com/pet.jpg"],
    status="available"
)

def main():
    # POST /pet -> возвращает объект Pet и статус 200
    created = client.post(
        "/pet",
        request_model=pet_req,
        # response_model=Pet,
        expected_status=200
    )
    print("Created:", created.json())

    # GET /pet/{petId}
    fetched = client.get(
        f"/pet/{pet_req.id}",
        response_model=Pet,
        expected_status=200
    )
    print("Fetched:", fetched)

    resp = client.delete(f"/pet/{pet_req.id}", expected_status=200)
    print("Delete raw response status:", resp.status_code)

    client.close()

def test_httpx():
    main()

if __name__ == "__main__":
    main()
