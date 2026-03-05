"""Tests for BrainusAI client initialization."""

import pytest
from brainus_ai import BrainusAI
from brainus_ai.exceptions import AuthenticationError


class TestClientInit:
    def test_valid_key_accepted(self):
        client = BrainusAI(api_key="brainus_abc123")
        assert client.api_key == "brainus_abc123"

    def test_empty_key_raises(self):
        with pytest.raises(AuthenticationError):
            BrainusAI(api_key="")

    def test_wrong_prefix_sk_live_raises(self):
        with pytest.raises(AuthenticationError):
            BrainusAI(api_key="sk_live_abc123")

    def test_wrong_prefix_bare_string_raises(self):
        with pytest.raises(AuthenticationError):
            BrainusAI(api_key="my_secret_key")

    def test_wrong_prefix_openai_style_raises(self):
        with pytest.raises(AuthenticationError):
            BrainusAI(api_key="sk-proj-abc123")

    def test_default_base_url(self):
        client = BrainusAI(api_key="brainus_abc123")
        assert client.base_url == "https://api.brainus.lk"

    def test_trailing_slash_stripped_from_base_url(self):
        client = BrainusAI(api_key="brainus_abc123", base_url="https://api.brainus.lk/")
        assert client.base_url == "https://api.brainus.lk"

    def test_custom_base_url(self):
        client = BrainusAI(api_key="brainus_abc123", base_url="http://localhost:8000")
        assert client.base_url == "http://localhost:8000"

    def test_default_timeout(self):
        client = BrainusAI(api_key="brainus_abc123")
        assert client.timeout == 30.0

    def test_custom_timeout(self):
        client = BrainusAI(api_key="brainus_abc123", timeout=60.0)
        assert client.timeout == 60.0

    def test_default_max_retries(self):
        client = BrainusAI(api_key="brainus_abc123")
        assert client.max_retries == 3

    def test_custom_max_retries(self):
        client = BrainusAI(api_key="brainus_abc123", max_retries=5)
        assert client.max_retries == 5
