"""Integration tests for Bill & Document Sloth API endpoints."""

import os
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import init_db

client = TestClient(app)


def setup_module(module):
    """Ensure database is initialized before running tests."""
    init_db()


def test_get_dashboard():
    response = client.get("/api/dashboard")
    assert response.status_code == 200
    data = response.json()
    assert "total_documents" in data
    assert "needs_review" in data
    assert "upcoming_bills" in data
    assert "urgent_deadlines" in data


def test_generate_demo_documents():
    response = client.post("/api/demo/generate")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert len(data["items"]) >= 5


def test_list_documents():
    response = client.get("/api/documents")
    assert response.status_code == 200
    docs = response.json()
    assert len(docs) > 0


def test_natural_language_search():
    # Search for electricity bills
    response = client.get("/api/documents?query=Show my electricity bills")
    assert response.status_code == 200
    docs = response.json()
    for d in docs:
        assert d["category"] == "Bills/Electricity"


def test_review_and_approve_document():
    # Get first document
    list_res = client.get("/api/documents")
    docs = list_res.json()
    assert len(docs) > 0
    doc_id = docs[0]["id"]

    # Save review correction
    review_res = client.post(
        f"/api/documents/{doc_id}/review",
        json={
            "category": "Bills/Electricity",
            "document_type": "Electricity Bill",
            "issuer": "BESCOM Verified",
            "total_amount": 1850.0,
            "currency": "₹",
            "due_date": "2026-10-28",
            "document_date": "2026-10-18",
            "suggested_filename": "2026-10_Electricity_Bill_BESCOM_Verified.pdf"
        }
    )
    assert review_res.status_code == 200

    # Approve and organize
    approve_res = client.post(
        f"/api/documents/{doc_id}/approve",
        json={
            "custom_filename": "2026-10_Electricity_Bill_BESCOM_Verified.pdf",
            "target_category": "Bills/Electricity"
        }
    )
    assert approve_res.status_code == 200
    details = approve_res.json()["details"]
    assert details["status"] == "organized"
    assert "Bills_Electricity" in details["folder_path"]

    # Test undo organization
    undo_res = client.post(f"/api/documents/{doc_id}/undo")
    assert undo_res.status_code == 200
    undo_data = undo_res.json()
    assert undo_data["restored_status"] == "needs_review"


def test_export_csv():
    response = client.get("/api/documents/export/csv")
    assert response.status_code == 200
    assert "text/csv" in response.headers["content-type"]
    assert "ID,Original Filename,Suggested Filename" in response.text
