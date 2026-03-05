"""
Brainus AI Python SDK

Official Python client for the Brainus AI API - RAG-powered educational content.
"""

from .client import BrainusAI
from .exceptions import (
    BrainusError,
    AuthenticationError,
    RateLimitError,
    QuotaExceededError,
    APIError,
)
from .models import QueryRequest, QueryResponse, Citation, UsageStats, Plan, QueryFilters, PlanInfo

__version__ = "0.1.7"

__all__ = [
    "BrainusAI",
    "BrainusError",
    "AuthenticationError",
    "RateLimitError",
    "QuotaExceededError",
    "APIError",
    "QueryRequest",
    "QueryResponse",
    "Citation",
    "UsageStats",
    "Plan",
    "QueryFilters",
    "PlanInfo",
]



