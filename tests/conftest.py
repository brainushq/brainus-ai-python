"""Shared fixtures for Brainus AI SDK tests."""

import pytest
from brainus_ai import BrainusAI

VALID_API_KEY = "brainus_test_key_abc123"
BASE_URL = "https://api.brainus.lk"


@pytest.fixture
def api_key() -> str:
    return VALID_API_KEY


@pytest.fixture
def client() -> BrainusAI:
    return BrainusAI(api_key=VALID_API_KEY)


# Reusable mock response payloads
QUERY_RESPONSE = {
    "answer": "Python is a high-level programming language.",
    "citations": [
        {
            "document_id": "doc_001",
            "document_name": "Python Basics.pdf",
            "pages": [1, 2],
            "metadata": {"subject": "ICT", "grade": "12"},
            "chunk_text": "Python is a high-level...",
        }
    ],
    "has_citations": True,
}

USAGE_RESPONSE = {
    "total_requests": 42,
    "total_tokens": 8500,
    "total_cost_usd": 0.034,
    "by_endpoint": {"/api/v1/dev/query": 42},
    "quota_remaining": 958,
    "quota_percentage": 4.2,
    "plan": {
        "name": "Pro",
        "rate_limit_per_minute": 60,
        "rate_limit_per_day": 1000,
        "monthly_quota": 1000,
    },
    "period_start": "2026-03-01",
    "period_end": "2026-03-31",
}

PLANS_RESPONSE = {
    "plans": [
        {
            "id": "plan_free",
            "name": "Free",
            "description": "Free tier",
            "rate_limit_per_minute": 10,
            "rate_limit_per_day": 100,
            "monthly_quota": 100,
            "price_lkr": None,
            "allowed_models": ["brainusai-fast"],
            "features": {},
            "is_active": True,
        },
        {
            "id": "plan_pro",
            "name": "Pro",
            "description": "Pro tier",
            "rate_limit_per_minute": 60,
            "rate_limit_per_day": 1000,
            "monthly_quota": 1000,
            "price_lkr": 2500.0,
            "allowed_models": ["brainusai-fast", "brainusai-thinking"],
            "features": {"priority_support": True},
            "is_active": True,
        },
    ]
}
