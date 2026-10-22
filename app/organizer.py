"""File organization, safe folder management, and reversible undo actions for Bill & Document Sloth."""

import os
import shutil
import sqlite3
import json
from datetime import datetime
from typing import Any, Dict, Optional, Tuple
from app.database import get_connection, log_action
from app.extractor import sanitize_filename

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ORGANIZED_DIR = os.path.join(BASE_DIR, "documents", "organized")
UPLOADS_DIR = os.path.join(BASE_DIR, "documents", "uploads")


def get_unique_filepath(target_dir: str, filename: str) -> str:
    """Return a non-colliding filepath in target_dir."""
    base_name, ext = os.path.splitext(filename)
    counter = 1
    dest = os.path.join(target_dir, filename)
    while os.path.exists(dest):
        dest = os.path.join(target_dir, f"{base_name}_{counter}{ext}")
        counter += 1
    return dest


def organize_document(document_id: int, custom_filename: Optional[str] = None, target_category: Optional[str] = None) -> Dict[str, Any]:
    """
    Approve and organize document into structured folder hierarchy:
    documents/organized/{Category}/{Year}/filename.ext
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM documents WHERE id = ?", (document_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        raise ValueError(f"Document {document_id} not found")

    doc = dict(row)
    old_data = {
        "status": doc["status"],
        "folder_path": doc["folder_path"],
        "file_path": doc["file_path"],
        "stored_filename": doc["stored_filename"],
        "category": doc["category"],
        "is_verified": doc["is_verified"]
    }

    category = target_category or doc["category"] or "Other"
    filename_to_use = custom_filename or doc["suggested_filename"] or doc["stored_filename"]
    filename_to_use = sanitize_filename(filename_to_use)

    # Determine Year subfolder from document_date or current year
    year = "General"
    if doc.get("document_date") and len(doc["document_date"]) >= 4:
        year = doc["document_date"][:4]
    else:
        year = datetime.now().strftime("%Y")

    # Target folder: documents/organized/{Category}/{Year}
    category_folder = category.replace("/", "_")
    target_dir = os.path.join(ORGANIZED_DIR, category_folder, year)
    os.makedirs(target_dir, exist_ok=True)

    dest_filepath = get_unique_filepath(target_dir, filename_to_use)
    final_filename = os.path.basename(dest_filepath)

    # Copy/move file from current path to organized path
    source_path = doc["file_path"]
    if os.path.exists(source_path):
        shutil.copy2(source_path, dest_filepath)
    else:
        # If source file was somehow missing in stored path, check uploads
        fallback_upload = os.path.join(UPLOADS_DIR, doc["stored_filename"])
        if os.path.exists(fallback_upload):
            shutil.copy2(fallback_upload, dest_filepath)
        else:
            raise FileNotFoundError(f"Source file not found at {source_path}")

    # Relative folder path for display
    rel_folder = os.path.relpath(target_dir, BASE_DIR)

    # Update database
    now = datetime.now().isoformat()
    cursor.execute(
        """
        UPDATE documents
        SET status = 'organized',
            category = ?,
            folder_path = ?,
            file_path = ?,
            stored_filename = ?,
            is_verified = 1,
            updated_at = ?
        WHERE id = ?
        """,
        (category, rel_folder, dest_filepath, final_filename, now, document_id)
    )

    new_data = {
        "status": "organized",
        "folder_path": rel_folder,
        "file_path": dest_filepath,
        "stored_filename": final_filename,
        "category": category,
        "is_verified": 1
    }

    conn.commit()
    conn.close()

    log_action(
        document_id=document_id,
        action_type="organized",
        description=f"Organized into '{rel_folder}' as '{final_filename}'",
        old_data=old_data,
        new_data=new_data,
        can_undo=True
    )

    return {
        "id": document_id,
        "status": "organized",
        "folder_path": rel_folder,
        "filename": final_filename,
        "file_path": dest_filepath
    }


def undo_last_action(document_id: int) -> Dict[str, Any]:
    """
    Undo the most recent reversible action for a document.
    Restores the previous file state, folder path, and metadata.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT * FROM actions_history
        WHERE document_id = ? AND can_undo = 1
        ORDER BY id DESC LIMIT 1
        """,
        (document_id,)
    )
    action_row = cursor.fetchone()
    if not action_row:
        conn.close()
        raise ValueError(f"No reversible actions found for document {document_id}")

    action = dict(action_row)
    old_data = json.loads(action["old_data"]) if action.get("old_data") else None

    if not old_data:
        conn.close()
        raise ValueError("Cannot undo: missing historical snapshot")

    # If action was 'organized', remove the newly created file in organized folder
    if action["action_type"] == "organized" and action.get("new_data"):
        new_data = json.loads(action["new_data"])
        created_file = new_data.get("file_path")
        if created_file and os.path.exists(created_file):
            try:
                os.remove(created_file)
            except Exception as e:
                print(f"Warning: could not delete organized file during undo: {e}")

    # Restore previous document state
    now = datetime.now().isoformat()
    cursor.execute(
        """
        UPDATE documents
        SET status = ?,
            category = ?,
            folder_path = ?,
            file_path = ?,
            stored_filename = ?,
            is_verified = ?,
            updated_at = ?
        WHERE id = ?
        """,
        (
            old_data.get("status", "needs_review"),
            old_data.get("category", "Other"),
            old_data.get("folder_path"),
            old_data.get("file_path"),
            old_data.get("stored_filename"),
            old_data.get("is_verified", 0),
            now,
            document_id
        )
    )

    # Mark action as undone
    cursor.execute("UPDATE actions_history SET can_undo = 0 WHERE id = ?", (action["id"],))

    conn.commit()
    conn.close()

    log_action(
        document_id=document_id,
        action_type="undone",
        description=f"Undid action: {action.get('description', '')}",
        can_undo=False
    )

    return {
        "id": document_id,
        "message": "Action successfully undone",
        "restored_status": old_data.get("status", "needs_review")
    }
