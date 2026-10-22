"""Pydantic schemas and models for Bill & Document Sloth."""
from datetime import date, datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, field_validator
import re


class DocumentReviewRequest(BaseModel):
    """Payload submitted when user reviews or edits extracted fields."""
    category: Optional[str] = "Other"
    document_type: Optional[str] = "Unknown"
    issuer: Optional[str] = None
    total_amount: Optional[float] = None
    currency: Optional[str] = "₹"
    document_date: Optional[str] = None
    due_date: Optional[str] = None
    billing_period: Optional[str] = None
    invoice_number: Optional[str] = None
    payment_status: Optional[str] = "Unpaid"
    suggested_filename: Optional[str] = None

    @field_validator("document_date", "due_date", mode="before")
    @classmethod
    def validate_date(cls, v: Any) -> Optional[str]:
        if not v or v == "null" or v == "":
            return None
        v_str = str(v).strip()
        # Verify valid ISO date format YYYY-MM-DD
        if re.match(r"^\d{4}-\d{2}-\d{2}$", v_str):
            try:
                datetime.strptime(v_str, "%Y-%m-%d")
                return v_str
            except ValueError:
                pass
        return None

    @field_validator("total_amount", mode="before")
    @classmethod
    def validate_amount(cls, v: Any) -> Optional[float]:
        if v is None or v == "" or v == "null":
            return None
        try:
            val = float(str(v).replace(",", "").replace("₹", "").replace("$", "").replace("€", "").strip())
            return round(val, 2) if val >= 0 else None
        except ValueError:
            return None


class DocumentApproveRequest(BaseModel):
    """Payload to approve and organize a document."""
    custom_filename: Optional[str] = None
    target_category: Optional[str] = None


class SearchFilterRequest(BaseModel):
    """Search and filter criteria for documents."""
    query: Optional[str] = None
    category: Optional[str] = None
    status: Optional[str] = None
    min_amount: Optional[float] = None
    max_amount: Optional[float] = None
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    deadlines_only: Optional[bool] = False


class DocumentResponse(BaseModel):
    """Full representation of a document."""
    id: int
    original_filename: str
    stored_filename: str
    suggested_filename: Optional[str]
    file_path: str
    file_size: int
    mime_type: str
    category: str
    document_type: str
    issuer: Optional[str]
    total_amount: Optional[float]
    currency: str
    document_date: Optional[str]
    due_date: Optional[str]
    billing_period: Optional[str]
    invoice_number: Optional[str]
    payment_status: str
    confidence_scores: Dict[str, float]
    extracted_text: Optional[str]
    status: str
    folder_path: Optional[str]
    is_verified: int
    created_at: str
    updated_at: str


class DashboardStats(BaseModel):
    """Summary metrics for the main dashboard."""
    total_documents: int
    needs_review: int
    upcoming_bills: int
    expiring_soon: int
    categories_breakdown: Dict[str, int]
    recent_activity: List[Dict[str, Any]]
    urgent_deadlines: List[Dict[str, Any]]
