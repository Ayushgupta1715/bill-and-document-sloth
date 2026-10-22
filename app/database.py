"""Database setup and connection helpers for Bill & Document Sloth."""
import sqlite3
import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "sloth_documents.db")

DEFAULT_CATEGORIES = [
    ("Bills/Electricity", "Zap", "Electricity & Power utility bills", "Bills/Electricity"),
    ("Bills/Internet", "Wifi", "Internet, broadband & phone bills", "Bills/Internet"),
    ("Receipts", "ShoppingBag", "Daily expenses, grocery & store purchase receipts", "Receipts"),
    ("Invoices", "FileText", "Client invoices, consulting & professional bills", "Invoices"),
    ("Insurance", "ShieldCheck", "Health, life, and vehicle insurance policies", "Insurance"),
    ("Rent & Agreements", "Home", "Rental agreements, leases & contracts", "Rent & Agreements"),
    ("Warranties", "Clock", "Product warranties, guarantees & device care", "Warranties"),
    ("Academic", "GraduationCap", "Transcripts, degrees & educational documents", "Academic"),
    ("Other", "Folder", "General & uncategorized documents", "Other"),
]


def get_connection() -> sqlite3.Connection:
    """Return a configured SQLite connection with dict-like row factory."""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    """Initialize database tables and default data."""
    conn = get_connection()
    cursor = conn.cursor()

    # Documents Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            original_filename TEXT NOT NULL,
            stored_filename TEXT NOT NULL,
            suggested_filename TEXT,
            file_path TEXT NOT NULL,
            file_size INTEGER DEFAULT 0,
            mime_type TEXT DEFAULT 'application/pdf',
            category TEXT DEFAULT 'Other',
            document_type TEXT DEFAULT 'Unknown',
            issuer TEXT,
            total_amount REAL,
            currency TEXT DEFAULT '₹',
            document_date TEXT,
            due_date TEXT,
            billing_period TEXT,
            invoice_number TEXT,
            payment_status TEXT DEFAULT 'Unpaid',
            confidence_scores TEXT DEFAULT '{}',
            extracted_text TEXT,
            status TEXT DEFAULT 'needs_review',
            folder_path TEXT,
            is_verified INTEGER DEFAULT 0,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)

    # Actions History Table for audit & safe undo
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS actions_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            document_id INTEGER NOT NULL,
            action_type TEXT NOT NULL,
            description TEXT,
            old_data TEXT,
            new_data TEXT,
            timestamp TEXT NOT NULL,
            can_undo INTEGER DEFAULT 1,
            FOREIGN KEY (document_id) REFERENCES documents(id) ON DELETE CASCADE
        )
    """)

    # Categories Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            icon TEXT DEFAULT 'Folder',
            description TEXT,
            folder_name TEXT NOT NULL
        )
    """)

    # Seed categories if empty
    cursor.execute("SELECT COUNT(*) FROM categories")
    if cursor.fetchone()[0] == 0:
        cursor.executemany(
            "INSERT INTO categories (name, icon, description, folder_name) VALUES (?, ?, ?, ?)",
            DEFAULT_CATEGORIES
        )

    conn.commit()
    conn.close()


def log_action(document_id: int, action_type: str, description: str, old_data: Optional[Dict[str, Any]] = None, new_data: Optional[Dict[str, Any]] = None, can_undo: bool = True) -> int:
    """Log an action in the history table for traceability and undo."""
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    cursor.execute(
        """
        INSERT INTO actions_history (document_id, action_type, description, old_data, new_data, timestamp, can_undo)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            document_id,
            action_type,
            description,
            json.dumps(old_data) if old_data else None,
            json.dumps(new_data) if new_data else None,
            now,
            1 if can_undo else 0
        )
    )
    action_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return action_id
