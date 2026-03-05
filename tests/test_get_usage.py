"""Tests for BrainusAI.get_usage()."""

import pytest
from pytest_httpx import HTTPXMock

from brainus_ai import BrainusAI
from brainus_ai.exceptions import APIError, AuthenticationError

from .conftest import BASE_URL, USAGE_RESPONSE, VALID_API_KEY

USAGE_URL = f"{BASE_URL}/api/v1/dev/usage"


@pytest.fixture
def client() -> BrainusAI:
    return BrainusAI(api_key=VALID_API_KEY)


async def test_returns_usage_stats(client: BrainusAI, httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(method="GET", url=USAGE_URL, json=USAGE_RESPONSE)
    stats = await client.get_usage()
    assert stats.total_requests == 42
    assert stats.total_tokens == 8500
    assert stats.total_cost_usd == pytest.approx(0.034)
    assert stats.quota_remaining == 958
    assert stats.quota_percentage == pytest.approx(4.2)
    assert stats.period_start == "2026-03-01"
    assert stats.period_end == "2026-03-31"


async def test_by_endpoint_parsed(client: BrainusAI, httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(method="GET", url=USAGE_URL, json=USAGE_RESPONSE)
    stats = await client.get_usage()
    assert stats.by_endpoint == {"/api/v1/dev/query": 42}


async def test_plan_info_parsed(client: BrainusAI, httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(method="GET", url=USAGE_URL, json=USAGE_RESPONSE)
    stats = await client.get_usage()
    assert stats.plan is not None
    assert stats.plan.name == "Pro"
    assert stats.plan.rate_limit_per_minute == 60
    assert stats.plan.rate_limit_per_day == 1000
    assert stats.plan.monthly_quota == 1000


async def test_optional_fields_absent_default_to_none(client: BrainusAI, httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        method="GET",
        url=USAGE_URL,
        json={"total_requests": 0, "by_endpoint": {}},
    )
    stats = await client.get_usage()
    assert stats.total_tokens is None
    assert stats.total_cost_usd is None
    assert stats.plan is None
    assert stats.quota_remaining is None
    assert stats.period_start is None


async def test_by_endpoint_empty_when_absent(client: BrainusAI, httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        method="GET",
        url=USAGE_URL,
        json={"total_requests": 0, "by_endpoint": {}},
    )
    stats = await client.get_usage()
    assert stats.by_endpoint == {}


async def test_401_raises_authentication_error(client: BrainusAI, httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(method="GET", url=USAGE_URL, status_code=401, json={"detail": "Invalid API key"})
    with pytest.raises(AuthenticationError):
        await client.get_usage()


async def test_500_raises_api_error(client: BrainusAI, httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(method="GET", url=USAGE_URL, status_code=500, json={"detail": "Server error"})
    with pytest.raises(APIError):
        await client.get_usage()


async def test_x_api_key_header_sent(client: BrainusAI, httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(method="GET", url=USAGE_URL, json=USAGE_RESPONSE)
    await client.get_usage()
    assert httpx_mock.get_requests()[0].headers["x-api-key"] == VALID_API_KEY
