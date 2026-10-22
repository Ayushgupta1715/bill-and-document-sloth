"""FastAPI application and REST endpoints for Bill & Document Sloth."""

import os
import shutil
import json
import csv
import io
from datetime import datetime, date
from typing import List, Optional
from fastapi import FastAPI, File, UploadFile, HTTPException, Query, Response
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

from app.database import init_db, get_connection, log_action
from app.models import (
    DocumentReviewRequest, DocumentApproveRequest, DocumentResponse, DashboardStats
)
from app.extractor import analyze_document_pipeline, sanitize_filename
from app.organizer import organize_document, undo_last_action
from app.demo_generator import generate_all_sample_documents
from app.gemma_service import analyze_with_gemma
from app.tabpfn_analyzer import analyze_bills_with_tabpfn
from app.voice_service import get_voice_briefing, synthesize_elevenlabs_audio

# Sentry Agent & Performance Tracing ($100 Sentry Prize Category)
SENTRY_DSN = os.getenv("SENTRY_DSN", "")
try:
    import sentry_sdk
    from sentry_sdk.integrations.fastapi import FastApiIntegration
    if SENTRY_DSN:
        sentry_sdk.init(
            dsn=SENTRY_DSN,
            traces_sample_rate=1.0,
            integrations=[FastApiIntegration()]
        )
except ImportError:
    pass

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOADS_DIR = os.path.join(BASE_DIR, "documents", "uploads")
ORGANIZED_DIR = os.path.join(BASE_DIR, "documents", "organized")
STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")

# Ensure base folders exist
os.makedirs(UPLOADS_DIR, exist_ok=True)
os.makedirs(ORGANIZED_DIR, exist_ok=True)
os.makedirs(STATIC_DIR, exist_ok=True)

# Initialize database
init_db()

app = FastAPI(
    title="Bill & Document Sloth API",
    description="Local-first AI document management and deadline tracker",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/dashboard", response_model=DashboardStats)
def get_dashboard_stats():
    """Retrieve summarized statistics, urgent deadlines, and recent activity."""
    conn = get_connection()
    cursor = conn.cursor()

    # Counts
    cursor.execute("SELECT COUNT(*) FROM documents")
    total_docs = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM documents WHERE status = 'needs_review'")
    needs_review = cursor.fetchone()[0]

    # Upcoming bills (with due_date)
    today_str = datetime.now().strftime("%Y-%m-%d")
    cursor.execute(
        """
        SELECT COUNT(*) FROM documents
        WHERE due_date IS NOT NULL AND due_date != '' AND status != 'rejected'
        """
    )
    upcoming_bills = cursor.fetchone()[0]

    # Expiring documents (warranties / insurance)
    cursor.execute(
        """
        SELECT COUNT(*) FROM documents
        WHERE category IN ('Warranties', 'Insurance') AND due_date IS NOT NULL
        """
    )
    expiring_soon = cursor.fetchone()[0]

    # Category breakdown
    cursor.execute(
        """
        SELECT category, COUNT(*) as count FROM documents
        GROUP BY category
        """
    )
    categories_breakdown = {row["category"]: row["count"] for row in cursor.fetchall()}

    # Urgent deadlines (sorted by due_date ascending)
    cursor.execute(
        """
        SELECT id, original_filename, stored_filename, category, document_type, issuer,
               total_amount, currency, due_date, status, is_verified
        FROM documents
        WHERE due_date IS NOT NULL AND due_date != '' AND status != 'rejected'
        ORDER BY due_date ASC
        LIMIT 10
        """
    )
    urgent_deadlines = []
    for r in cursor.fetchall():
        d = dict(r)
        # Compute urgency label
        due = d["due_date"]
        try:
            days_diff = (datetime.strptime(due, "%Y-%m-%d").date() - datetime.now().date()).days
            if days_diff < 0:
                d["urgency"] = "overdue"
                d["urgency_text"] = f"Overdue by {abs(days_diff)} days"
            elif days_diff == 0:
                d["urgency"] = "today"
                d["urgency_text"] = "Due Today"
            elif days_diff <= 3:
                d["urgency"] = "critical"
                d["urgency_text"] = f"Due in {days_diff} days"
            elif days_diff <= 7:
                d["urgency"] = "soon"
                d["urgency_text"] = f"Due in {days_diff} days"
            else:
                d["urgency"] = "future"
                d["urgency_text"] = f"Due in {days_diff} days"
        except Exception:
            d["urgency"] = "unknown"
            d["urgency_text"] = due
        urgent_deadlines.append(d)

    # Recent activity
    cursor.execute(
        """
        SELECT h.id, h.document_id, h.action_type, h.description, h.timestamp, h.can_undo,
               d.original_filename, d.stored_filename
        FROM actions_history h
        LEFT JOIN documents d ON h.document_id = d.id
        ORDER BY h.id DESC
        LIMIT 8
        """
    )
    recent_activity = [dict(r) for r in cursor.fetchall()]

    conn.close()

    return DashboardStats(
        total_documents=total_docs,
        needs_review=needs_review,
        upcoming_bills=upcoming_bills,
        expiring_soon=expiring_soon,
        categories_breakdown=categories_breakdown,
        recent_activity=recent_activity,
        urgent_deadlines=urgent_deadlines
    )


@app.get("/api/documents")
def list_documents(
    query: Optional[str] = None,
    category: Optional[str] = None,
    status: Optional[str] = None,
    min_amount: Optional[float] = None,
    max_amount: Optional[float] = None,
    deadlines_only: bool = False
):
    """List documents with comprehensive filtering and search capabilities."""
    conn = get_connection()
    cursor = conn.cursor()

    conditions = []
    params = []

    if category and category != "All":
        conditions.append("category = ?")
        params.append(category)

    if status and status != "All":
        conditions.append("status = ?")
        params.append(status)

    if min_amount is not None:
        conditions.append("total_amount >= ?")
        params.append(min_amount)

    if max_amount is not None:
        conditions.append("total_amount <= ?")
        params.append(max_amount)

    if deadlines_only:
        conditions.append("due_date IS NOT NULL AND due_date != ''")

    # Natural language & text search
    if query:
        q = query.strip()
        # Natural language query rules
        if "electricity" in q.lower():
            conditions.append("category = 'Bills/Electricity'")
        elif "internet" in q.lower() or "broadband" in q.lower() or "wifi" in q.lower():
            conditions.append("category = 'Bills/Internet'")
        elif "receipt" in q.lower():
            conditions.append("category = 'Receipts'")
        elif "invoice" in q.lower():
            conditions.append("category = 'Invoices'")
        elif "warranty" in q.lower() or "warranties" in q.lower():
            conditions.append("category = 'Warranties'")
        elif "insurance" in q.lower():
            conditions.append("category = 'Insurance'")
        else:
            conditions.append(
                """
                (original_filename LIKE ? OR suggested_filename LIKE ? OR
                 issuer LIKE ? OR document_type LIKE ? OR extracted_text LIKE ?)
                """
            )
            wildcard = f"%{q}%"
            params.extend([wildcard, wildcard, wildcard, wildcard, wildcard])

    sql = "SELECT * FROM documents"
    if conditions:
        sql += " WHERE " + " AND ".join(conditions)
    sql += " ORDER BY id DESC"

    cursor.execute(sql, params)
    docs = []
    for row in cursor.fetchall():
        d = dict(row)
        d["confidence_scores"] = json.loads(d["confidence_scores"]) if d["confidence_scores"] else {}
        docs.append(d)

    conn.close()
    return docs


@app.get("/api/documents/{doc_id}")
def get_document(doc_id: int):
    """Get single document details."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM documents WHERE id = ?", (doc_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="Document not found")

    d = dict(row)
    d["confidence_scores"] = json.loads(d["confidence_scores"]) if d["confidence_scores"] else {}
    return d


@app.post("/api/upload")
async def upload_documents(files: List[UploadFile] = File(...)):
    """Upload multiple documents, run intelligent extraction, and store results."""
    uploaded_records = []
    conn = get_connection()
    cursor = conn.cursor()

    for file in files:
        if not file.filename:
            continue

        orig_name = file.filename
        safe_name = f"{int(datetime.now().timestamp())}_{sanitize_filename(orig_name)}"
        file_path = os.path.join(UPLOADS_DIR, safe_name)

        # Save to disk
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        # Run extraction pipeline
        analysis = analyze_document_pipeline(file_path, orig_name)

        now = datetime.now().isoformat()
        cursor.execute(
            """
            INSERT INTO documents (
                original_filename, stored_filename, suggested_filename, file_path,
                file_size, mime_type, category, document_type, issuer, total_amount,
                currency, document_date, due_date, billing_period, invoice_number,
                payment_status, confidence_scores, extracted_text, status,
                is_verified, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'needs_review', 0, ?, ?)
            """,
            (
                orig_name,
                safe_name,
                analysis["suggested_filename"],
                file_path,
                analysis["file_size"],
                file.content_type or "application/pdf",
                analysis["category"],
                analysis["document_type"],
                analysis["issuer"],
                analysis["total_amount"],
                analysis["currency"],
                analysis["document_date"],
                analysis["due_date"],
                analysis["billing_period"],
                analysis["invoice_number"],
                "Unpaid",
                json.dumps(analysis["confidence_scores"]),
                analysis["extracted_text"],
                now,
                now
            )
        )
        doc_id = cursor.lastrowid
        conn.commit()

        log_action(
            document_id=doc_id,
            action_type="uploaded",
            description=f"Uploaded and analyzed '{orig_name}' (AI Confidence: {int(analysis['confidence_scores']['overall']*100)}%)",
            new_data={"filename": orig_name, "category": analysis["category"]},
            can_undo=False
        )

        uploaded_records.append({"id": doc_id, "filename": orig_name, "category": analysis["category"]})

    conn.close()
    return {"message": f"Successfully uploaded {len(uploaded_records)} documents", "documents": uploaded_records}


@app.post("/api/documents/{doc_id}/review")
def review_document(doc_id: int, payload: DocumentReviewRequest):
    """Save human-reviewed and verified field corrections."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM documents WHERE id = ?", (doc_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Document not found")

    old_doc = dict(row)
    now = datetime.now().isoformat()

    cursor.execute(
        """
        UPDATE documents
        SET category = ?,
            document_type = ?,
            issuer = ?,
            total_amount = ?,
            currency = ?,
            document_date = ?,
            due_date = ?,
            billing_period = ?,
            invoice_number = ?,
            payment_status = ?,
            suggested_filename = ?,
            is_verified = 1,
            updated_at = ?
        WHERE id = ?
        """,
        (
            payload.category,
            payload.document_type,
            payload.issuer,
            payload.total_amount,
            payload.currency,
            payload.document_date,
            payload.due_date,
            payload.billing_period,
            payload.invoice_number,
            payload.payment_status,
            payload.suggested_filename,
            now,
            doc_id
        )
    )
    conn.commit()
    conn.close()

    log_action(
        document_id=doc_id,
        action_type="edited",
        description=f"Human review and field confirmation saved for document #{doc_id}",
        old_data=old_doc,
        new_data=payload.model_dump(),
        can_undo=True
    )

    return {"message": "Document updated successfully", "id": doc_id}


@app.post("/api/documents/{doc_id}/approve")
def approve_document(doc_id: int, payload: Optional[DocumentApproveRequest] = None):
    """Approve document and organize into structured folder with smart filename."""
    custom_name = payload.custom_filename if payload else None
    target_cat = payload.target_category if payload else None

    try:
        result = organize_document(doc_id, custom_filename=custom_name, target_category=target_cat)
        return {"message": "Document approved and organized successfully", "details": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/documents/{doc_id}/reject")
def reject_document(doc_id: int):
    """Reject or archive document."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE documents SET status = 'rejected', updated_at = ? WHERE id = ?", (datetime.now().isoformat(), doc_id))
    conn.commit()
    conn.close()

    log_action(doc_id, "rejected", f"Document #{doc_id} was rejected", can_undo=True)
    return {"message": "Document marked as rejected"}


@app.post("/api/documents/{doc_id}/undo")
def undo_document_action(doc_id: int):
    """Undo the last reversible action for the document."""
    try:
        result = undo_last_action(doc_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/api/documents/{doc_id}")
def delete_document(doc_id: int):
    """Delete document and remove associated files safely."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT file_path FROM documents WHERE id = ?", (doc_id,))
    row = cursor.fetchone()
    if row and row["file_path"] and os.path.exists(row["file_path"]):
        try:
            os.remove(row["file_path"])
        except Exception:
            pass

    cursor.execute("DELETE FROM documents WHERE id = ?", (doc_id,))
    conn.commit()
    conn.close()
    return {"message": "Document deleted successfully"}


@app.get("/api/documents/{doc_id}/file")
def view_document_file(doc_id: int):
    """Preview document inline in browser."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT file_path, mime_type, original_filename FROM documents WHERE id = ?", (doc_id,))
    row = cursor.fetchone()
    conn.close()

    if not row or not os.path.exists(row["file_path"]):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        row["file_path"],
        media_type=row["mime_type"],
        filename=row["original_filename"],
        content_disposition_type="inline"
    )


@app.post("/api/demo/generate")
def generate_and_import_samples():
    """1-Click Demo: Synthesize realistic sample PDFs and import them."""
    sample_paths = generate_all_sample_documents()
    imported = []
    conn = get_connection()
    cursor = conn.cursor()

    for path in sample_paths:
        orig_name = os.path.basename(path)
        dest_upload = os.path.join(UPLOADS_DIR, orig_name)
        shutil.copy2(path, dest_upload)

        analysis = analyze_document_pipeline(dest_upload, orig_name)
        now = datetime.now().isoformat()

        cursor.execute(
            """
            INSERT INTO documents (
                original_filename, stored_filename, suggested_filename, file_path,
                file_size, mime_type, category, document_type, issuer, total_amount,
                currency, document_date, due_date, billing_period, invoice_number,
                payment_status, confidence_scores, extracted_text, status,
                is_verified, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, 'application/pdf', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'needs_review', 0, ?, ?)
            """,
            (
                orig_name,
                orig_name,
                analysis["suggested_filename"],
                dest_upload,
                analysis["file_size"],
                analysis["category"],
                analysis["document_type"],
                analysis["issuer"],
                analysis["total_amount"],
                analysis["currency"],
                analysis["document_date"],
                analysis["due_date"],
                analysis["billing_period"],
                analysis["invoice_number"],
                "Unpaid",
                json.dumps(analysis["confidence_scores"]),
                analysis["extracted_text"],
                now,
                now
            )
        )
        doc_id = cursor.lastrowid
        conn.commit()

        log_action(
            document_id=doc_id,
            action_type="uploaded",
            description=f"Generated and imported demo document '{orig_name}'",
            new_data={"category": analysis["category"]},
            can_undo=False
        )
        imported.append({"id": doc_id, "name": orig_name})

    conn.close()
    return {"message": f"Generated and loaded {len(imported)} demo documents successfully!", "items": imported}


@app.get("/api/documents/export/csv")
def export_documents_csv():
    """Export document records to CSV format."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM documents ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "ID", "Original Filename", "Suggested Filename", "Category", "Document Type",
        "Issuer", "Total Amount", "Currency", "Document Date", "Due Date",
        "Billing Period", "Invoice Number", "Status", "Is Verified", "Folder Path"
    ])

    for r in rows:
        writer.writerow([
            r["id"], r["original_filename"], r["suggested_filename"], r["category"],
            r["document_type"], r["issuer"], r["total_amount"], r["currency"],
            r["document_date"], r["due_date"], r["billing_period"], r["invoice_number"],
            r["status"], r["is_verified"], r["folder_path"]
        ])

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=sloth_documents_export.csv"}
    )


# -------------------------------------------------------------
# SPONSOR TRACK INTEGRATIONS (Hacktoberfest Week 3 Prizes)
# -------------------------------------------------------------

@app.post("/api/ai/gemma/extract/{doc_id}")
def extract_document_with_gemma(doc_id: int):
    """
    Best Use of Gemma ($200 Prize Category):
    Re-analyzes document using Google's Gemma open-weight model
    for deep structured field reasoning and verification.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM documents WHERE id = ?", (doc_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="Document not found")

    doc = dict(row)
    text = doc.get("extracted_text") or doc.get("original_filename")
    gemma_result = analyze_with_gemma(text, doc.get("original_filename"))

    log_action(
        document_id=doc_id,
        action_type="gemma_reasoning",
        description=f"Analyzed with Gemma Open-Weight Model ({gemma_result.get('model_used')})",
        new_data=gemma_result,
        can_undo=False
    )

    return gemma_result


@app.get("/api/analytics/tabpfn")
def get_tabpfn_tabular_insights():
    """
    Best Use of TabPFN ($200 Prize Category - Prior Labs):
    Applies Prior Labs' TabPFN-3.5 tabular foundation model on historical bill records
    to forecast upcoming utility bills and detect tabular cost anomalies.
    """
    return analyze_bills_with_tabpfn()


@app.get("/api/voice/briefing")
def get_sloth_voice_briefing():
    """
    Best Use of ElevenLabs ($100 Prize Category):
    Generates a voice briefing of pending bills and deadlines.
    """
    return get_voice_briefing()


@app.get("/api/voice/stream")
def stream_elevenlabs_voice():
    """Stream synthesized ElevenLabs voice audio for sloth narration."""
    briefing = get_voice_briefing()
    audio_bytes = synthesize_elevenlabs_audio(briefing["script"])
    if not audio_bytes:
        raise HTTPException(status_code=400, detail="ElevenLabs API key not configured or synthesis failed.")
    return Response(content=audio_bytes, media_type="audio/mpeg")


# Serve static web frontend
app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")
