"""
SnapLens — FastAPI Backend Entry Point

This is the main server file. All API routes start here.
Current endpoints:
  GET  /              → Health check
  POST /upload        → Upload a screenshot for AI analysis
  POST /items         → Save an analyzed result as a categorized item
  GET  /items         → List saved items (optional ?category= filter)
  DELETE /items/{id}  → Delete a saved item
"""

import os
import uuid
import shutil
from datetime import datetime

from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from typing import Optional

# Import our AI pipeline modules
from backend.app.ocr import extract_text
from backend.app.intent import classify_intent
from backend.app.database import init_db, get_connection
from backend.app.models import ItemCreate, ItemResponse

# Create the FastAPI app instance
app = FastAPI(
    title="SnapLens API",
    description="Turn screenshots into actionable tasks, notes, and reminders.",
    version="0.1.0",
)

# ── CORS Middleware ─────────────────────────────────────
# Allows the frontend (running on a different port or file://) to call our API.
# Without this, browsers block cross-origin requests for security.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to your domain
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Initialize Database on Startup ──────────────────────
# This runs once when the server starts.
# Creates the items table if it doesn't exist yet.
init_db()

# ── Serve Frontend Files ────────────────────────────────
# Mount the frontend folder so FastAPI serves HTML/CSS/JS directly
# IMPORTANT: This must be the LAST mount — it catches all paths under /app
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "frontend")
app.mount("/app", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")

# ── Config ──────────────────────────────────────────────
# Directory where uploaded screenshots will be saved
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Only allow image file types (security best practice)
ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".bmp"}
# Max file size: 10 MB (prevent abuse)
MAX_FILE_SIZE_MB = 10


# ── Helper Functions ────────────────────────────────────
def validate_file_extension(filename: str) -> str:
    """
    Check if the uploaded file has an allowed image extension.
    Returns the extension if valid, raises HTTPException if not.

    Why this matters:
    - Prevents users from uploading .exe, .py, or other dangerous files
    - This is a basic but essential security check in any file upload system
    """
    ext = os.path.splitext(filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type '{ext}' not allowed. Use: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    return ext


def generate_unique_filename(extension: str) -> str:
    """
    Generate a unique filename using UUID + timestamp.

    Why not use the original filename?
    - Two users could upload 'screenshot.png' → file overwrite!
    - Original filenames can contain special characters or path traversal attacks
    - UUID guarantees uniqueness without a database lookup
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = uuid.uuid4().hex[:8]
    return f"{timestamp}_{unique_id}{extension}"


# ── Endpoints ───────────────────────────────────────────
@app.get("/")
def health_check():
    """
    Health check endpoint.
    Returns a simple JSON to confirm the server is running.
    """
    return {"status": "ok", "message": "SnapLens API is running 🧠"}


@app.post("/upload")
async def upload_screenshot(file: UploadFile = File(...)):
    """
    Upload a screenshot image for AI analysis.

    What this endpoint does:
    1. Validates the file is an allowed image type
    2. Checks the file size is within limits
    3. Saves it with a unique filename to /uploads
    4. Runs OCR to extract text from the image
    5. Runs LLM intent classification on extracted text
    6. Returns the full AI analysis
    """

    # Step 1: Validate file extension
    extension = validate_file_extension(file.filename)

    # Step 2: Read file content and check size
    contents = await file.read()
    file_size_mb = len(contents) / (1024 * 1024)

    if file_size_mb > MAX_FILE_SIZE_MB:
        raise HTTPException(
            status_code=400,
            detail=f"File too large ({file_size_mb:.1f} MB). Max allowed: {MAX_FILE_SIZE_MB} MB."
        )

    # Step 3: Save with unique filename
    unique_name = generate_unique_filename(extension)
    file_path = os.path.join(UPLOAD_DIR, unique_name)

    with open(file_path, "wb") as f:
        f.write(contents)

    # Step 4: Run OCR to extract text from the screenshot
    extracted_text = extract_text(file_path)

    # Step 5: Run LLM intent classification on the extracted text
    # This is the AI brain — it understands WHY the screenshot was saved
    intent_result = classify_intent(extracted_text)

    # Step 6: Return the full AI analysis
    # The complete pipeline: Image → OCR → Intent → Response
    return {
        "status": "success",
        "filename": unique_name,
        "size_mb": round(file_size_mb, 2),
        "extracted_text": extracted_text,
        "intent": intent_result,
        "message": "Screenshot analyzed successfully!",
    }


# ── Items CRUD Endpoints ────────────────────────────────
# These let the frontend save, list, and delete categorized items.
# The flow: User uploads screenshot → AI analyzes → User clicks "Save as task"
# → Frontend calls POST /items with the analysis result.

@app.post("/items", status_code=201)
def save_item(item: ItemCreate):
    """
    Save an analyzed screenshot result as a categorized item.

    The frontend sends this after the user clicks "Save as task/note/etc."
    It stores the AI analysis in the database for the dashboard to display.
    """
    conn = get_connection()
    cursor = conn.execute(
        """
        INSERT INTO items (category, title, summary, key_detail, extracted_text, suggested_action)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (item.category, item.title, item.summary, item.key_detail,
         item.extracted_text, item.suggested_action)
    )
    conn.commit()
    item_id = cursor.lastrowid

    # Fetch the saved item to return it with id and created_at
    row = conn.execute("SELECT * FROM items WHERE id = ?", (item_id,)).fetchone()
    conn.close()

    return dict(row)


@app.get("/items")
def list_items(category: Optional[str] = Query(None, description="Filter by category: task, note, reminder, expense, link")):
    """
    List all saved items, optionally filtered by category.

    Examples:
      GET /items           → all items
      GET /items?category=task  → only tasks

    Returns items sorted by newest first (most recently saved on top).
    """
    conn = get_connection()

    if category:
        rows = conn.execute(
            "SELECT * FROM items WHERE category = ? ORDER BY created_at DESC",
            (category,)
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM items ORDER BY created_at DESC"
        ).fetchall()

    conn.close()
    return [{"id": row["id"], "category": row["category"], "title": row["title"],
             "summary": row["summary"], "key_detail": row["key_detail"],
             "extracted_text": row["extracted_text"],
             "suggested_action": row["suggested_action"],
             "created_at": row["created_at"]} for row in rows]


@app.delete("/items/{item_id}")
def delete_item(item_id: int):
    """
    Delete a saved item by its ID.

    Used when the user removes an item from the dashboard.
    Returns 404 if the item doesn't exist.
    """
    conn = get_connection()

    # Check if item exists first
    row = conn.execute("SELECT id FROM items WHERE id = ?", (item_id,)).fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail=f"Item with id {item_id} not found.")

    conn.execute("DELETE FROM items WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()

    return {"status": "deleted", "id": item_id}

