"""Tests for BrainusAI.get_plans()."""

import pytest
from pytest_httpx import HTTPXMock

from brainus_ai import BrainusAI
from brainus_ai.exceptions import APIError, AuthenticationError

from .conftest import BASE_URL, PLANS_RESPONSE, VALID_API_KEY

PLANS_URL = f"{BASE_URL}/api/v1/dev/plans"


@pytest.fixture
def client() -> BrainusAI:
    return BrainusAI(api_key=VALID_API_KEY)


async def test_returns_list_of_plans(client: BrainusAI, httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(method="GET", url=PLANS_URL, json=PLANS_RESPONSE)
    plans = await client.get_plans()
    assert len(plans) == 2


async def test_plan_fields_parsed_correctly(client: BrainusAI, httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(method="GET", url=PLANS_URL, json=PLANS_RESPONSE)
    plans = await client.get_plans()
    free = plans[0]
    assert free.id == "plan_free"
    assert free.name == "Free"
    assert free.description == "Free tier"
    assert free.rate_limit_per_minute == 10
    assert free.rate_limit_per_day == 100
    assert free.monthly_quota == 100
    assert free.price_lkr is None
    assert free.allowed_models == ["brainusai-fast"]
    assert free.is_active is True


async def test_plan_with_price_and_features(client: BrainusAI, httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(method="GET", url=PLANS_URL, json=PLANS_RESPONSE)
    plans = await client.get_plans()
    pro = plans[1]
    assert pro.price_lkr == pytest.approx(2500.0)
    assert "brainusai-thinking" in pro.allowed_models
    assert pro.features == {"priority_support": True}


async def test_empty_plans_list(client: BrainusAI, httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(method="GET", url=PLANS_URL, json={"plans": []})
    plans = await client.get_plans()
    assert plans == []


async def test_optional_description_is_none(client: BrainusAI, httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(
        method="GET",
        url=PLANS_URL,
        json={
            "plans": [
                {
                    "id": "plan_x",
                    "name": "X",
                    "rate_limit_per_minute": 5,
                    "rate_limit_per_day": 50,
                    "allowed_models": [],
                    "features": {},
                    "is_active": True,
                }
            ]
        },
    )
    plans = await client.get_plans()
    assert plans[0].description is None
    assert plans[0].monthly_quota is None
    assert plans[0].price_lkr is None


async def test_401_raises_authentication_error(client: BrainusAI, httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(method="GET", url=PLANS_URL, status_code=401, json={"detail": "Invalid API key"})
    with pytest.raises(AuthenticationError):
        await client.get_plans()


async def test_500_raises_api_error(client: BrainusAI, httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(method="GET", url=PLANS_URL, status_code=500, json={"detail": "Server error"})
    with pytest.raises(APIError):
        await client.get_plans()
