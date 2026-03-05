"""Tests for async context manager and close()."""

from unittest.mock import AsyncMock, patch

import pytest
from pytest_httpx import HTTPXMock

from brainus_ai import BrainusAI

from .conftest import BASE_URL, QUERY_RESPONSE, VALID_API_KEY

QUERY_URL = f"{BASE_URL}/api/v1/dev/query"


async def test_context_manager_returns_client() -> None:
    async with BrainusAI(api_key=VALID_API_KEY) as client:
        assert isinstance(client, BrainusAI)


async def test_context_manager_closes_on_exit(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(method="GET", url=f"{BASE_URL}/api/v1/dev/usage", json={"total_requests": 0, "by_endpoint": {}})
    async with BrainusAI(api_key=VALID_API_KEY) as client:
        await client.get_usage()
    # After exiting, the underlying httpx client should be closed.
    assert client._client.is_closed


async def test_close_marks_client_as_closed() -> None:
    client = BrainusAI(api_key=VALID_API_KEY)
    assert not client._client.is_closed
    await client.close()
    assert client._client.is_closed


async def test_requests_work_inside_context_manager(httpx_mock: HTTPXMock) -> None:
    httpx_mock.add_response(method="POST", url=QUERY_URL, json=QUERY_RESPONSE)
    async with BrainusAI(api_key=VALID_API_KEY) as client:
        resp = await client.query("test")
    assert resp.answer == "Python is a high-level programming language."
