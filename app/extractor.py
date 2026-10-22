"""Intelligent document extraction pipeline for Bill & Document Sloth.
Extracts embedded text from PDFs, classifies document types, extracts structured fields,
computes field-level confidence scores, and suggests clean, standardized filenames.
"""

import os
import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from pypdf import PdfReader


# Known patterns and signatures for classification
CATEGORY_PATTERNS = {
    "Bills/Electricity": [
        r"\belectricity\b", r"\bpower\b", r"\benergy\b", r"\bkwh\b", r"\bmeter reading\b",
        r"\bdiscom\b", r"\bbescom\b", r"\btneb\b", r"\bmahavitaran\b", r"\bconed\b",
        r"\bduke energy\b", r"\bpg&e\b", r"\belectric\b", r"\bconsumer no\b", r"\bkwh used\b"
    ],
    "Bills/Internet": [
        r"\bbroadband\b", r"\bfiber\b", r"\binternet\b", r"\btelecom\b", r"\bcellular\b",
        r"\bairtel\b", r"\bjio\b", r"\bverizon\b", r"\bat&t\b", r"\bcomcast\b", r"\bxfinity\b",
        r"\bspectrum\b", r"\bvodafone\b", r"\bdata plan\b", r"\blandline\b"
    ],
    "Receipts": [
        r"\breceipt\b", r"\bcashier\b", r"\bpos\b", r"\bstore\b", r"\bcoffee\b", r"\bcafe\b",
        r"\btakeout\b", r"\brestaurant\b", r"\bwalmart\b", r"\btarget\b", r"\bstarbucks\b",
        r"\border #\b", r"\bcard ending in\b", r"\btip\b", r"\bitems purchased\b"
    ],
    "Invoices": [
        r"\btax invoice\b", r"\binvoice\b", r"\bbill to\b", r"\bclient\b", r"\bnet 30\b",
        r"\bpayment terms\b", r"\bgstin\b", r"\bvat no\b", r"\bprofessional fees\b",
        r"\bconsulting\b", r"\bpo number\b", r"\bunit price\b"
    ],
    "Insurance": [
        r"\binsurance\b", r"\bpolicy\b", r"\bpremium\b", r"\bsum assured\b", r"\binsured\b",
        r"\bmediclaim\b", r"\bhealth guard\b", r"\bvehicle insurance\b", r"\bpolicyholder\b",
        r"\bcoverage\b", r"\btpa\b", r"\bclaim\b"
    ],
    "Rent & Agreements": [
        r"\blease\b", r"\brent agreement\b", r"\brental\b", r"\blandlord\b", r"\btenant\b",
        r"\bsecurity deposit\b", r"\bpremises\b", r"\bmonthly rent\b", r"\bmaintenance charges\b"
    ],
    "Warranties": [
        r"\bwarranty\b", r"\bguarantee\b", r"\bdevice care\b", r"\bapplecare\b",
        r"\bextended warranty\b", r"\bserial number\b", r"\bvalid until\b", r"\bcoverage period\b",
        r"\blimited warranty\b"
    ],
    "Academic": [
        r"\btranscript\b", r"\bdegree\b", r"\bdiploma\b", r"\buniversity\b", r"\bcollege\b",
        r"\bmarksheet\b", r"\bgpa\b", r"\bsemester\b", r"\bcredits\b", r"\bacademic\b"
    ]
}

DOCUMENT_TYPE_MAP = {
    "Bills/Electricity": "Electricity Bill",
    "Bills/Internet": "Internet Bill",
    "Receipts": "Purchase Receipt",
    "Invoices": "Invoice",
    "Insurance": "Insurance Policy",
    "Rent & Agreements": "Rent Agreement",
    "Warranties": "Warranty Certificate",
    "Academic": "Academic Document",
    "Other": "Document"
}

KNOWN_ISSUERS = [
    "BESCOM", "Tata Power", "Adani Electricity", "Mahavitaran", "PG&E", "Duke Energy", "ConEdison",
    "Airtel", "Reliance Jio", "ACT Fibernet", "Verizon", "AT&T", "Comcast", "Xfinity", "Spectrum",
    "Star Health", "HDFC ERGO", "ICICI Lombard", "LIC", "Geico", "Progressive", "Allstate",
    "Apple", "Samsung", "Dell", "HP", "Lenovo", "Sony", "LG", "Amazon", "Walmart", "Target",
    "Starbucks", "Blue Tokai", "Uber", "Ola", "Zomato", "Swiggy"
]


def extract_text_from_file(file_path: str) -> str:
    """Extract text content from a file (PDF or text)."""
    if not os.path.exists(file_path):
        return ""
    
    ext = os.path.splitext(file_path)[1].lower()
    extracted_text = ""

    if ext == ".pdf":
        try:
            reader = PdfReader(file_path)
            pages_text = []
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    pages_text.append(text)
            extracted_text = "\n\n".join(pages_text).strip()
        except Exception as e:
            print(f"Error reading PDF {file_path}: {e}")
            extracted_text = ""
    elif ext in [".txt", ".md", ".csv", ".json", ".log"]:
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                extracted_text = f.read().strip()
        except Exception as e:
            print(f"Error reading text file {file_path}: {e}")
            extracted_text = ""

    return extracted_text


def classify_document(text: str, filename: str = "") -> Tuple[str, str, float]:
    """
    Classify document into category and document_type using content and filename.
    Returns (category, document_type, confidence_score).
    """
    combined_content = f"{filename} {text}".lower()
    
    scores: Dict[str, float] = {}
    # Category base weights: Specific utility/device categories should outweigh generic "Invoice"
    category_weights = {
        "Bills/Electricity": 1.5,
        "Bills/Internet": 1.5,
        "Warranties": 1.4,
        "Insurance": 1.4,
        "Rent & Agreements": 1.4,
        "Receipts": 1.2,
        "Academic": 1.2,
        "Invoices": 1.0,
        "Other": 0.5
    }

    for category, patterns in CATEGORY_PATTERNS.items():
        score = 0.0
        weight = category_weights.get(category, 1.0)
        for pattern in patterns:
            matches = len(re.findall(pattern, combined_content, re.IGNORECASE))
            score += (matches * weight)
        scores[category] = score

    # Find the top category
    best_category = "Other"
    max_score = 0.0
    for cat, sc in scores.items():
        if sc > max_score:
            max_score = sc
            best_category = cat

    confidence = min(0.98, max(0.40, 0.50 + (max_score * 0.10))) if max_score > 0 else 0.30
    document_type = DOCUMENT_TYPE_MAP.get(best_category, "Document")

    return best_category, document_type, round(confidence, 2)


def extract_issuer(text: str, filename: str = "") -> Tuple[Optional[str], float]:
    """Extract issuer/provider name from text or known entities."""
    combined = f"{filename}\n{text}"
    
    # Check known issuers first
    for known in KNOWN_ISSUERS:
        if re.search(rf"\b{re.escape(known)}\b", combined, re.IGNORECASE):
            return known, 0.95

    # Check common provider prefix patterns
    patterns = [
        r"(?:Provider|Billed By|Issuer|Company|Merchant|From|Issued By):\s*([A-Za-z0-9 &.,'-]{3,40})",
        r"(?:Welcome to|Thank you for choosing)\s+([A-Za-z0-9 &.,'-]{3,30})"
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            issuer = match.group(1).strip()
            # Basic sanity check
            if len(issuer) >= 3 and not issuer.lower().startswith("date"):
                return issuer, 0.85

    # Fallback to inspecting first 3 non-empty lines of text
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    if lines:
        for candidate in lines[:3]:
            if 3 <= len(candidate) <= 35 and not any(kw in candidate.lower() for kw in ["invoice", "bill", "tax", "date", "receipt", "page", "statement"]):
                return candidate, 0.65

    return None, 0.20


def extract_amount(text: str) -> Tuple[Optional[float], str, float]:
    """
    Extract total amount and currency from text.
    Returns (amount, currency, confidence).
    """
    # Detect currency
    currency = "₹"
    if "$" in text or "USD" in text:
        currency = "$"
    elif "€" in text or "EUR" in text:
        currency = "€"
    elif "£" in text or "GBP" in text:
        currency = "£"
    elif "₹" in text or "INR" in text or "Rs" in text or "Rs." in text:
        currency = "₹"

    # Targeted patterns for total amount
    patterns = [
        r"(?:Total Amount|Amount Due|Total Payable|Grand Total|Net Payable|Total Charges|Total|Balance Due|Amount)\s*[:=\-]?\s*(?:₹|Rs\.?|INR|\$|€|£)?\s*([\d,]+(?:\.\d{1,2})?)",
        r"(?:₹|Rs\.?|INR|\$|€|£)\s*([\d,]+(?:\.\d{1,2})?)\s*(?:due|total|payable)",
    ]

    candidates: List[Tuple[float, float]] = []

    for idx, pattern in enumerate(patterns):
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            raw_val = match.group(1).replace(",", "").strip()
            try:
                val = float(raw_val)
                # Ignore zero, trivial amounts, or giant arbitrary year numbers
                if 1.0 <= val < 100000000 and val != 2024 and val != 2025 and val != 2026:
                    conf = 0.92 if idx == 0 else 0.75
                    candidates.append((val, conf))
            except ValueError:
                continue

    if candidates:
        # Sort by confidence, then pick candidate
        best_val, best_conf = candidates[0]
        return best_val, currency, best_conf

    return None, currency, 0.20


def parse_date_string(date_str: str) -> Optional[str]:
    """Parse various date string formats and convert to ISO YYYY-MM-DD."""
    date_str = date_str.strip()
    formats = [
        "%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%m/%d/%Y",
        "%d %B %Y", "%d %b %Y", "%B %d, %Y", "%b %d, %Y",
        "%Y/%m/%d", "%d.%m.%Y", "%B %d %Y", "%b %d %Y"
    ]
    for fmt in formats:
        try:
            parsed = datetime.strptime(date_str, fmt)
            # Sanity range: between 2000 and 2040
            if 2000 <= parsed.year <= 2040:
                return parsed.strftime("%Y-%m-%d")
        except ValueError:
            continue
    return None


def extract_dates(text: str) -> Tuple[Optional[str], Optional[str], Optional[str], float, float]:
    """
    Extract document date, due/expiry date, and billing period from text.
    Returns (document_date, due_date, billing_period, doc_date_conf, due_date_conf).
    """
    DATE_TOKEN = r"(\d{4}[-/.]\d{1,2}[-/.]\d{1,2}|\d{1,2}[-/.]\d{1,2}[-/.]\d{2,4}|[A-Za-z]{3,9}\s+\d{1,2},?\s+\d{4}|\d{1,2}\s+[A-Za-z]{3,9}\s+\d{4})"

    # Patterns for Due Date or Expiry Date
    due_patterns = [
        rf"(?:Due Date|Payment Due Date|Pay By|Payment Due|Valid Until|Expiry Date|Renewal Date|Expires On|Expires)\s*[:=\-]?\s*{DATE_TOKEN}",
        rf"(?:Due on|Valid thru)\s*[:=\-]?\s*{DATE_TOKEN}"
    ]

    due_date = None
    due_conf = 0.20
    for pattern in due_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            raw_candidate = match.group(1).strip()
            parsed = parse_date_string(raw_candidate)
            if parsed:
                due_date = parsed
                due_conf = 0.90
                break

    # Patterns for Document Date / Bill Date / Invoice Date
    doc_patterns = [
        rf"(?:Invoice Date|Bill Date|Document Date|Date of Issue|Dated|Order Date|Purchase Date)\s*[:=\-]?\s*{DATE_TOKEN}",
        rf"(?<!Due\s)(?<!Expiry\s)\bDate\s*[:=\-]\s*{DATE_TOKEN}"
    ]

    doc_date = None
    doc_conf = 0.20
    for pattern in doc_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            raw_candidate = match.group(1).strip()
            parsed = parse_date_string(raw_candidate)
            if parsed and parsed != due_date:
                doc_date = parsed
                doc_conf = 0.88
                break

    # If document date is still missing, search for any general date
    if not doc_date:
        generic_date_pattern = r"\b(\d{4}[-/.]\d{1,2}[-/.]\d{1,2}|\d{1,2}[-/.]\d{1,2}[-/.]\d{2,4})\b"
        matches = re.findall(generic_date_pattern, text)
        for m in matches:
            parsed = parse_date_string(m)
            if parsed and parsed != due_date:
                doc_date = parsed
                doc_conf = 0.60
                break
                break

    # Billing Period pattern (e.g. October 2026, or 01 Oct 2026 - 31 Oct 2026)
    period_pattern = r"(?:Billing Period|Bill Period|Period|Cycle)\s*[:=\-]?\s*([A-Za-z0-9,./ -]{6,35})"
    billing_period = None
    period_match = re.search(period_pattern, text, re.IGNORECASE)
    if period_match:
        billing_period = period_match.group(1).strip().rstrip(".,")

    return doc_date, due_date, billing_period, doc_conf, due_conf


def extract_reference_number(text: str) -> Optional[str]:
    """Extract invoice number, bill number, or reference number."""
    patterns = [
        r"(?:Invoice No|Invoice Number|Bill No|Bill Number|Policy No|Policy Number|Account No|Order ID|Order No|Receipt No|Reference No)\s*[:=\-]?\s*([A-Za-z0-9\-_/#]{4,30})",
        r"(?:Invoice|Bill|Policy|Order)#\s*([A-Za-z0-9\-_/#]{4,30})"
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            ref = match.group(1).strip()
            if len(ref) >= 3 and not any(kw in ref.lower() for kw in ["date", "due", "total"]):
                return ref
    return None


def sanitize_filename(name: str) -> str:
    """Remove illegal characters from proposed filename."""
    # Replace illegal filename characters with underscore
    sanitized = re.sub(r'[\\/*?:"<>|]', '_', name)
    sanitized = re.sub(r'\s+', '_', sanitized)
    sanitized = re.sub(r'_+', '_', sanitized)
    return sanitized.strip('_')


def generate_suggested_filename(
    doc_date: Optional[str],
    doc_type: str,
    issuer: Optional[str],
    original_filename: str
) -> str:
    """
    Generate clean, standardized filename following PRD FR-04:
    Example: 2026-10_Electricity_Bill_ExampleProvider.pdf
    """
    ext = os.path.splitext(original_filename)[1] or ".pdf"
    
    # Extract Year-Month
    date_prefix = ""
    if doc_date and len(doc_date) >= 7:
        date_prefix = doc_date[:7]
    else:
        date_prefix = datetime.now().strftime("%Y-%m")

    # Document type label
    clean_type = sanitize_filename(doc_type.replace(" ", "_"))

    # Issuer label
    clean_issuer = sanitize_filename((issuer or "Document").replace(" ", "_"))

    suggested = f"{date_prefix}_{clean_type}_{clean_issuer}{ext}"
    return suggested


def analyze_document_pipeline(file_path: str, original_filename: str) -> Dict[str, Any]:
    """
    Full document intelligence pipeline.
    Extracts text, classifies, parses fields, computes confidence scores,
    and returns a clean structured dictionary.
    """
    text = extract_text_from_file(file_path)
    file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0

    category, doc_type, cat_conf = classify_document(text, original_filename)
    issuer, issuer_conf = extract_issuer(text, original_filename)
    amount, currency, amount_conf = extract_amount(text)
    doc_date, due_date, billing_period, doc_date_conf, due_date_conf = extract_dates(text)
    ref_num = extract_reference_number(text)

    suggested_filename = generate_suggested_filename(doc_date, doc_type, issuer, original_filename)

    confidence_scores = {
        "category": cat_conf,
        "document_type": cat_conf,
        "issuer": issuer_conf,
        "total_amount": amount_conf,
        "document_date": doc_date_conf,
        "due_date": due_date_conf,
        "overall": round((cat_conf + issuer_conf + amount_conf + doc_date_conf + due_date_conf) / 5.0, 2)
    }

    return {
        "category": category,
        "document_type": doc_type,
        "issuer": issuer,
        "total_amount": amount,
        "currency": currency,
        "document_date": doc_date,
        "due_date": due_date,
        "billing_period": billing_period,
        "invoice_number": ref_num,
        "suggested_filename": suggested_filename,
        "confidence_scores": confidence_scores,
        "extracted_text": text[:3000] if text else "",  # store preview text
        "file_size": file_size
    }
