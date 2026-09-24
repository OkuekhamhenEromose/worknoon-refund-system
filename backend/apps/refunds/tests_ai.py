import pytest

from apps.refunds.services.ai_service import AIResult, AIServiceError


def test_ai_result_accepts_valid_payload():
    result = AIResult.from_dict({
        "classification": "DAMAGED_ITEM",
        "confidence": 0.95,
        "risk_flags": [],
        "reasoning_summary": "The customer reports a damaged item.",
        "customer_response": "We can review your damaged-item refund request.",
    })
    assert result.confidence == 0.95
    assert result.as_dict()["classification"] == "DAMAGED_ITEM"


def test_ai_result_rejects_invalid_confidence():
    with pytest.raises(AIServiceError):
        AIResult.from_dict({
            "classification": "DAMAGED_ITEM",
            "confidence": "high",
            "risk_flags": [],
            "reasoning_summary": "x",
            "customer_response": "y",
        })


def test_ai_result_rejects_unknown_classification():
    with pytest.raises(AIServiceError):
        AIResult.from_dict({
            "classification": "APPROVE_REFUND",
            "confidence": 1,
            "risk_flags": [],
            "reasoning_summary": "x",
            "customer_response": "y",
        })


def test_ai_result_rejects_missing_required_fields():
    with pytest.raises(AIServiceError):
        AIResult.from_dict({
            "classification": "DAMAGED_ITEM",
            "confidence": 0.8,
            "risk_flags": [],
            "reasoning_summary": "Only the response is missing.",
        })


def test_ai_result_rejects_non_string_risk_flag():
    with pytest.raises(AIServiceError):
        AIResult.from_dict({
            "classification": "DAMAGED_ITEM",
            "confidence": 0.8,
            "risk_flags": ["ok", 123],
            "reasoning_summary": "The item appears damaged.",
            "customer_response": "We can review the request.",
        })
