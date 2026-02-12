"""
SnapLens — FastAPI Backend Entry Point

This is the main server file. All API routes start here.
Current endpoints:
  GET  /          → Health check
  POST /upload    → Upload a screenshot for AI analysis
"""

import os
import uuid
import shutil
from datetime import datetime

from fastapi import FastAPI, UploadFile, File, HTTPException

# Import our OCR module (the first piece of the AI pipeline!)
from backend.app.ocr import extract_text

# Create the FastAPI app instance
app = FastAPI(
    title="SnapLens API",
    description="Turn screenshots into actionable tasks, notes, and reminders.",
    version="0.1.0",
)

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
    5. Returns the extracted text (intent classification coming next!)
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
    # This is the first step of our AI pipeline!
    extracted_text = extract_text(file_path)

    # Step 5: Return the upload confirmation + extracted text
    return {
        "status": "success",
        "filename": unique_name,
        "size_mb": round(file_size_mb, 2),
        "extracted_text": extracted_text,
        "message": "Screenshot processed! Text extracted via OCR.",
    }
