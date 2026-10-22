"""Unit tests for Hacktoberfest sponsor track integrations (Gemma, TabPFN, ElevenLabs)."""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.gemma_service import analyze_with_gemma
from app.tabpfn_analyzer import analyze_bills_with_tabpfn
from app.voice_service import generate_sloth_briefing_text, get_voice_briefing

client = TestClient(app)


def test_gemma_reasoning_pipeline():
    sample_text = """
    BESCOM — Bangalore Electricity Supply Company
    ELECTRICITY CONSUMPTION BILL
    Consumer No: 9182374610
    Bill Date: 2026-10-18
    Due Date: 2026-10-28
    Total Amount Due: ₹1,850.00
    """
    result = analyze_with_gemma(sample_text, "BESCOM_Bill.pdf")
    assert result["category"] == "Bills/Electricity"
    assert result["total_amount"] == 1850.00
    assert result["due_date"] == "2026-10-28"
    assert "model_used" in result


def test_tabpfn_tabular_forecasting():
    insights = analyze_bills_with_tabpfn()
    assert "tabpfn_version" in insights
    assert "TabPFN-3.5" in insights["tabpfn_version"]
    if insights["status"] == "success":
        assert "forecast" in insights
        assert insights["forecast"]["predicted_amount"] > 0


def test_voice_briefing_generation():
    script = generate_sloth_briefing_text()
    assert isinstance(script, str)
    assert len(script) > 20
    assert "Bill Sloth" in script


def test_api_tabpfn_endpoint():
    res = client.get("/api/analytics/tabpfn")
    assert res.status_code == 200
    data = res.json()
    assert "tabpfn_version" in data


def test_api_voice_briefing_endpoint():
    res = client.get("/api/voice/briefing")
    assert res.status_code == 200
    data = res.json()
    assert "script" in data
    assert "provider" in data
