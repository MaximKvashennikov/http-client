"""
Пример использования HttpClient с публичным Petstore API.
"""

import httpx
from tenacity import retry, stop_after_attempt, wait_fixed
from core import HttpClient
from examples.petstore_models import Pet


class SimpleBearerAuth(httpx.Auth):
    """Simple Bearer token authentication for testing."""

    def __init__(self, token: str):
        self.token = token

    def auth_flow(self, request):
        if self.token:
            request.headers["Authorization"] = f"Bearer {self.token}"
        yield request


def test_petstore():
    retry_decorator = retry(
        stop=stop_after_attempt(3), wait=wait_fixed(2), reraise=True
    )

    client = HttpClient(
        base_url="https://petstore.swagger.io/v2",
        default_headers={"User-Agent": "qa-http-client/1.0"},
    )

    pet_req = Pet(
        id=123456789,
        name="test-pet",
        photo_urls=["https://example.com/pet.jpg"],
        status="available",
    )

    created = client.post(
        "/pet",
        request_model=pet_req,
        # response_model=Pet,
        expected_status=200,
        retry=retry_decorator,
    )
    print("Created:", created.json())

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


def test_bearer_auth_positive():
    print("POSITIVE TEST: Valid Bearer token")

    valid_client = HttpClient(
        base_url="https://httpbin.org",
        auth=SimpleBearerAuth("valid-token-123"),
        timeout=10.0,
    )

    try:
        response = valid_client.get(
            "/bearer",
            expected_status=200,
            headers={"Accept": "application/json"}
        )

        result = response.json()
        print(f"   ✅ Status: {response.status_code}")
        print(f"   ✅ Token: {result['token']}")
        print(f"   ✅ Authenticated: {result['authenticated']}")

        # Assertions
        assert response.status_code == 200
        assert result['token'] == "valid-token-123"
        assert result['authenticated'] is True

    except Exception as e:
        print(f"   ❌ Failed: {e}")
        raise

def test_bearer_auth_negative():
    print("NEGATIVE TEST: Empty Bearer token")

    empty_auth_client = HttpClient(
        base_url="https://httpbin.org",
        auth=SimpleBearerAuth(""),  # Empty token
        timeout=10.0,
    )

    try:
        response = empty_auth_client.get("/bearer",expected_status=401)

        # If we get here with 200, it's unexpected
        result = response.json()
        print(f"   ❌ UNEXPECTED: Got 200 with empty token")
        print(f"      Token: '{result['token']}'")
        print(f"      Authenticated: {result['authenticated']}")

        # This shouldn't happen
        assert False, "Should have gotten 401 for empty token"

    except httpx.HTTPStatusError as e:
        assert e.response.status_code == 401
        print(f"   ✅ Got expected 401 for empty token")

    except Exception as e:
        print(f"   ❌ Failed: {e}")
        raise

    finally:
        empty_auth_client.close()
