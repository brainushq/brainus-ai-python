"""Tests for Pydantic models."""

import pytest
from pydantic import ValidationError

from brainus_ai.models import Citation, Plan, QueryFilters, QueryRequest, QueryResponse, UsageStats


class TestCitation:
    def test_valid_citation(self) -> None:
        c = Citation(document_id="d1", document_name="Doc.pdf", pages=[1, 2], metadata={"k": "v"})
        assert c.document_id == "d1"
        assert c.pages == [1, 2]

    def test_pages_none_defaults_to_empty_list(self) -> None:
        c = Citation(document_id="d1", document_name="Doc.pdf", pages=None, metadata={})  # type: ignore[arg-type]
        assert c.pages == []

    def test_metadata_none_defaults_to_empty_dict(self) -> None:
        c = Citation(document_id="d1", document_name="Doc.pdf", pages=[], metadata=None)  # type: ignore[arg-type]
        assert c.metadata == {}

    def test_chunk_text_optional(self) -> None:
        c = Citation(document_id="d1", document_name="Doc.pdf")
        assert c.chunk_text is None

    def test_chunk_text_set(self) -> None:
        c = Citation(document_id="d1", document_name="Doc.pdf", chunk_text="some text")
        assert c.chunk_text == "some text"


class TestQueryFilters:
    def test_all_fields_optional(self) -> None:
        f = QueryFilters()
        assert f.subject is None
        assert f.grade is None
        assert f.year is None
        assert f.category is None
        assert f.language is None

    def test_fields_set(self) -> None:
        f = QueryFilters(subject="ICT", grade="12", year="2024", category="Past Paper", language="English")
        assert f.subject == "ICT"
        assert f.grade == "12"
        assert f.year == "2024"
        assert f.category == "Past Paper"
        assert f.language == "English"


class TestQueryRequest:
    def test_valid_request(self) -> None:
        r = QueryRequest(query="What is Python?")
        assert r.query == "What is Python?"

    def test_empty_query_raises(self) -> None:
        with pytest.raises(ValidationError):
            QueryRequest(query="")

    def test_query_over_1000_chars_raises(self) -> None:
        with pytest.raises(ValidationError):
            QueryRequest(query="x" * 1001)

    def test_optional_fields_default_to_none(self) -> None:
        r = QueryRequest(query="test")
        assert r.store_id is None
        assert r.filters is None
        assert r.model is None

    def test_exclude_none_omits_optional_fields(self) -> None:
        r = QueryRequest(query="test")
        dumped = r.model_dump(exclude_none=True)
        assert "store_id" not in dumped
        assert "filters" not in dumped
        assert "model" not in dumped

    def test_filters_serialised_in_dump(self) -> None:
        r = QueryRequest(query="test", filters=QueryFilters(subject="ICT"))
        dumped = r.model_dump(exclude_none=True)
        assert dumped["filters"]["subject"] == "ICT"


class TestQueryResponse:
    def test_valid_response(self) -> None:
        resp = QueryResponse(answer="42", citations=[], has_citations=False)
        assert resp.answer == "42"
        assert resp.has_citations is False

    def test_citations_default_empty(self) -> None:
        resp = QueryResponse(answer="42", has_citations=False)
        assert resp.citations == []


class TestUsageStats:
    def test_by_endpoint_defaults_to_empty_dict(self) -> None:
        stats = UsageStats(total_requests=0)
        assert stats.by_endpoint == {}

    def test_optional_fields_default_to_none(self) -> None:
        stats = UsageStats(total_requests=0)
        assert stats.total_tokens is None
        assert stats.total_cost_usd is None
        assert stats.plan is None


class TestPlan:
    def test_is_active_defaults_to_true(self) -> None:
        p = Plan(id="p1", name="Free", rate_limit_per_minute=10, rate_limit_per_day=100)
        assert p.is_active is True

    def test_allowed_models_defaults_to_empty(self) -> None:
        p = Plan(id="p1", name="Free", rate_limit_per_minute=10, rate_limit_per_day=100)
        assert p.allowed_models == []

    def test_features_defaults_to_empty_dict(self) -> None:
        p = Plan(id="p1", name="Free", rate_limit_per_minute=10, rate_limit_per_day=100)
        assert p.features == {}
