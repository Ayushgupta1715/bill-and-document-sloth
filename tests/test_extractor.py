"""Unit tests for Bill & Document Sloth extraction and organization pipelines."""

import os
import pytest
from app.extractor import (
    classify_document,
    extract_issuer,
    extract_amount,
    extract_dates,
    extract_reference_number,
    generate_suggested_filename,
    sanitize_filename
)
from app.models import DocumentReviewRequest


def test_classify_electricity_bill():
    text = """
    Bangalore Electricity Supply Company (BESCOM)
    ELECTRICITY CONSUMPTION BILL
    Consumer No: 9182374610
    Units Consumed: 142 kWh
    Amount Due: ₹1,850.00
    Due Date: 2026-10-28
    """
    category, doc_type, conf = classify_document(text, "bill.pdf")
    assert category == "Bills/Electricity"
    assert doc_type == "Electricity Bill"
    assert conf >= 0.60


def test_classify_internet_invoice():
    text = """
    Airtel Broadband & Telecommunications
    TAX INVOICE — HIGH SPEED FIBER
    Invoice No: INV-2026-AIR-9481
    Due Date: 2026-10-24
    Total Amount: ₹999.00
    """
    category, doc_type, conf = classify_document(text, "invoice.pdf")
    assert category == "Bills/Internet"
    assert doc_type == "Internet Bill"
    assert conf >= 0.60


def test_classify_receipt():
    text = """
    Blue Tokai Coffee Roasters
    RETAIL STORE PURCHASE RECEIPT
    Flat White Coffee ₹220
    Croissant ₹145
    Total Amount: ₹385.00
    """
    category, doc_type, conf = classify_document(text, "receipt.pdf")
    assert category == "Receipts"
    assert doc_type == "Purchase Receipt"


def test_classify_warranty():
    text = """
    AppleCare+ Proof of Coverage
    OFFICIAL WARRANTY CERTIFICATE
    Product: MacBook Pro
    Serial Number: C02G91XPQ6L4
    Valid Until: 2027-11-15
    """
    category, doc_type, conf = classify_document(text, "warranty.pdf")
    assert category == "Warranties"
    assert doc_type == "Warranty Certificate"


def test_extract_amount_and_currency():
    text = "Payment details: Total Amount Due : ₹1,850.00 please pay on time"
    amount, currency, conf = extract_amount(text)
    assert amount == 1850.00
    assert currency == "₹"
    assert conf >= 0.80


def test_extract_dates():
    text = "Bill Date: 2026-10-18 and Due Date: 2026-10-28"
    doc_date, due_date, period, doc_conf, due_conf = extract_dates(text)
    assert doc_date == "2026-10-18"
    assert due_date == "2026-10-28"
    assert doc_conf >= 0.80
    assert due_conf >= 0.80


def test_sanitize_filename():
    unsafe = '2026/10: Electricity * Bill? <Test>.pdf'
    safe = sanitize_filename(unsafe)
    assert '/' not in safe
    assert ':' not in safe
    assert '*' not in safe
    assert '?' not in safe
    assert '<' not in safe
    assert '>' not in safe


def test_suggested_filename_format():
    filename = generate_suggested_filename(
        doc_date="2026-10-18",
        doc_type="Electricity Bill",
        issuer="BESCOM",
        original_filename="IMG_10283.pdf"
    )
    assert filename == "2026-10_Electricity_Bill_BESCOM.pdf"


def test_pydantic_validation():
    # Valid ISO date
    req = DocumentReviewRequest(
        category="Bills/Electricity",
        due_date="2026-10-28",
        total_amount="1850.00"
    )
    assert req.due_date == "2026-10-28"
    assert req.total_amount == 1850.00

    # Malformed date should be rejected (turned to None) rather than corrupting DB
    req_bad = DocumentReviewRequest(
        due_date="invalid-date-string"
    )
    assert req_bad.due_date is None
