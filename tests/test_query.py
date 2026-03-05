"""Tests for BrainusAI.query()."""

import json

import pytest
from pytest_httpx import HTTPXMock

from brainus_ai import BrainusAI
from brainus_ai.exceptions import APIError, AuthenticationError, QuotaExceededError, RateLimitError
from brainus_ai.models import QueryFilters

from .conftest import BASE_URL, QUERY_RESPONSE, VALID_API_KEY

QUERY_URL = f"{BASE_URL}/api/v1/dev/query"


@pytest.fixture
def client() -> BrainusAI:
    return BrainusAI(api_key=VALID_API_KEY)


# ---------------------------------------------------------------------------
# Happy path
# ---------------------------------------------------------------------------


async def test_query_returns_answer(client: BrainusAI, httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(method="POST", url=QUERY_URL, json=QUERY_RESPONSE)
    resp = await client.query("What is Python?")
    assert resp.answer == "Python is a high-level programming language."


async def test_query_returns_citations(client: BrainusAI, httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(method="POST", url=QUERY_URL, json=QUERY_RESPONSE)
    resp = await client.query("What is Python?")
    assert resp.has_citations is True
    assert len(resp.citations) == 1
    c = resp.citations[0]
    assert c.document_id == "doc_001"
    assert c.document_name == "Python Basics.pdf"
    assert c.pages == [1, 2]
    assert c.chunk_text == "Python is a high-level..."
    assert c.metadata == {"subject": "ICT", "grade": "12"}


async def test_query_empty_citations(client: BrainusAI, httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        method="POST",
        url=QUERY_URL,
        json={"answer": "No results.", "citations": [], "has_citations": False},
    )
    resp = await client.query("Obscure topic")
    assert resp.has_citations is False
    assert resp.citations == []


# ---------------------------------------------------------------------------
# Request body construction
# ---------------------------------------------------------------------------


async def test_query_text_in_body(client: BrainusAI, httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(method="POST", url=QUERY_URL, json=QUERY_RESPONSE)
    await client.query("What is Python?")
    body = json.loads(httpx_mock.get_requests()[0].content)
    assert body["query"] == "What is Python?"


async def test_store_id_included_when_provided(client: BrainusAI, httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(method="POST", url=QUERY_URL, json=QUERY_RESPONSE)
    await client.query("test", store_id="store_abc")
    body = json.loads(httpx_mock.get_requests()[0].content)
    assert body["store_id"] == "store_abc"


async def test_store_id_omitted_when_not_provided(client: BrainusAI, httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(method="POST", url=QUERY_URL, json=QUERY_RESPONSE)
    await client.query("test")
    body = json.loads(httpx_mock.get_requests()[0].content)
    assert "store_id" not in body


async def test_model_included_when_provided(client: BrainusAI, httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(method="POST", url=QUERY_URL, json=QUERY_RESPONSE)
    await client.query("test", model="brainusai-thinking")
    body = json.loads(httpx_mock.get_requests()[0].content)
    assert body["model"] == "brainusai-thinking"


async def test_model_omitted_when_not_provided(client: BrainusAI, httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(method="POST", url=QUERY_URL, json=QUERY_RESPONSE)
    await client.query("test")
    body = json.loads(httpx_mock.get_requests()[0].content)
    assert "model" not in body


async def test_filters_as_queryfilters_object(client: BrainusAI, httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(method="POST", url=QUERY_URL, json=QUERY_RESPONSE)
    await client.query("test", filters=QueryFilters(subject="ICT", grade="12"))
    body = json.loads(httpx_mock.get_requests()[0].content)
    assert body["filters"]["subject"] == "ICT"
    assert body["filters"]["grade"] == "12"


async def test_filters_as_plain_dict(client: BrainusAI, httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(method="POST", url=QUERY_URL, json=QUERY_RESPONSE)
    await client.query("test", filters={"subject": "Science", "year": "2024"})
    body = json.loads(httpx_mock.get_requests()[0].content)
    assert body["filters"]["subject"] == "Science"
    assert body["filters"]["year"] == "2024"


async def test_filters_omitted_when_not_provided(client: BrainusAI, httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(method="POST", url=QUERY_URL, json=QUERY_RESPONSE)
    await client.query("test")
    body = json.loads(httpx_mock.get_requests()[0].content)
    assert "filters" not in body


async def test_x_api_key_header_sent(client: BrainusAI, httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(method="POST", url=QUERY_URL, json=QUERY_RESPONSE)
    await client.query("test")
    assert httpx_mock.get_requests()[0].headers["x-api-key"] == VALID_API_KEY


# ---------------------------------------------------------------------------
# Error handling
# ---------------------------------------------------------------------------


async def test_401_raises_authentication_error(client: BrainusAI, httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(method="POST", url=QUERY_URL, status_code=401, json={"detail": "Invalid API key"})
    with pytest.raises(AuthenticationError):
        await client.query("test")


async def test_429_raises_rate_limit_error(client: BrainusAI, httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(method="POST", url=QUERY_URL, status_code=429, json={"detail": "Rate limit exceeded"})
    with pytest.raises(RateLimitError):
        await client.query("test")


async def test_429_retry_after_header_is_parsed(client: BrainusAI, httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        method="POST",
        url=QUERY_URL,
        status_code=429,
        headers={"Retry-After": "30"},
        json={"detail": "Rate limit exceeded"},
    )
    with pytest.raises(RateLimitError) as exc_info:
        await client.query("test")
    assert exc_info.value.retry_after == 30


async def test_429_without_retry_after_header(client: BrainusAI, httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(method="POST", url=QUERY_URL, status_code=429, json={"detail": "Rate limit exceeded"})
    with pytest.raises(RateLimitError) as exc_info:
        await client.query("test")
    assert exc_info.value.retry_after is None


async def test_403_with_quota_raises_quota_exceeded(client: BrainusAI, httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(method="POST", url=QUERY_URL, status_code=403, json={"detail": "Monthly quota exceeded"})
    with pytest.raises(QuotaExceededError):
        await client.query("test")


async def test_403_without_quota_raises_api_error(client: BrainusAI, httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(method="POST", url=QUERY_URL, status_code=403, json={"detail": "Forbidden"})
    with pytest.raises(APIError) as exc_info:
        await client.query("test")
    assert exc_info.value.status_code == 403


async def test_400_missing_store_id_message(client: BrainusAI, httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        method="POST",
        url=QUERY_URL,
        status_code=400,
        json={"detail": "No store_id provided and no default store configured"},
    )
    with pytest.raises(APIError) as exc_info:
        await client.query("test")
    assert exc_info.value.status_code == 400
    assert "store_id" in exc_info.value.message


async def test_400_other_error(client: BrainusAI, httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(method="POST", url=QUERY_URL, status_code=400, json={"detail": "Bad request"})
    with pytest.raises(APIError) as exc_info:
        await client.query("test")
    assert exc_info.value.status_code == 400


async def test_500_raises_api_error(client: BrainusAI, httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(method="POST", url=QUERY_URL, status_code=500, json={"detail": "Internal server error"})
    with pytest.raises(APIError) as exc_info:
        await client.query("test")
    assert exc_info.value.status_code == 500
