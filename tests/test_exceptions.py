"""Tests for exception classes."""

from brainus_ai.exceptions import (
    APIError,
    AuthenticationError,
    BrainusError,
    QuotaExceededError,
    RateLimitError,
)


class TestBrainusError:
    def test_is_exception(self) -> None:
        assert issubclass(BrainusError, Exception)

    def test_message_attribute(self) -> None:
        e = BrainusError("something broke")
        assert e.message == "something broke"

    def test_str_representation(self) -> None:
        e = BrainusError("something broke")
        assert "something broke" in str(e)


class TestAuthenticationError:
    def test_is_brainus_error(self) -> None:
        assert issubclass(AuthenticationError, BrainusError)

    def test_message(self) -> None:
        e = AuthenticationError("bad key")
        assert e.message == "bad key"


class TestRateLimitError:
    def test_is_brainus_error(self) -> None:
        assert issubclass(RateLimitError, BrainusError)

    def test_retry_after_none_by_default(self) -> None:
        e = RateLimitError()
        assert e.retry_after is None

    def test_retry_after_set(self) -> None:
        e = RateLimitError("limit hit", retry_after=60)
        assert e.retry_after == 60

    def test_default_message(self) -> None:
        e = RateLimitError()
        assert e.message == "Rate limit exceeded"

    def test_custom_message(self) -> None:
        e = RateLimitError("slow down")
        assert e.message == "slow down"


class TestQuotaExceededError:
    def test_is_brainus_error(self) -> None:
        assert issubclass(QuotaExceededError, BrainusError)

    def test_message(self) -> None:
        e = QuotaExceededError("quota gone")
        assert e.message == "quota gone"


class TestAPIError:
    def test_is_brainus_error(self) -> None:
        assert issubclass(APIError, BrainusError)

    def test_status_code_none_by_default(self) -> None:
        e = APIError("error")
        assert e.status_code is None

    def test_status_code_set(self) -> None:
        e = APIError("server error", status_code=500)
        assert e.status_code == 500

    def test_message(self) -> None:
        e = APIError("bad gateway", status_code=502)
        assert e.message == "bad gateway"


class TestInstanceofChecks:
    def test_all_subclass_of_brainus_error(self) -> None:
        for cls in [AuthenticationError, RateLimitError, QuotaExceededError, APIError]:
            assert issubclass(cls, BrainusError)

    def test_all_subclass_of_exception(self) -> None:
        for cls in [BrainusError, AuthenticationError, RateLimitError, QuotaExceededError, APIError]:
            assert issubclass(cls, Exception)

    def test_can_catch_with_base_class(self) -> None:
        try:
            raise AuthenticationError("bad key")
        except BrainusError as e:
            assert e.message == "bad key"
        else:
            assert False, "Should have caught exception"
