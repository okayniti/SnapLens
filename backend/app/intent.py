"""
SnapLens — AI Analysis Module (Gemini Vision)

Analyzes screenshots using Google Gemini's vision capability.

Architecture upgrade (v2 → v3):
  v1: Image → Tesseract OCR → Keyword rules      (noisy, bad on dark UIs)
  v2: Image → Tesseract OCR → Gemini text prompt  (still limited by OCR quality)
  v3: Image → Gemini Vision (sees image directly)  ← current

Why this is better:
  - Gemini SEES the actual screenshot — no OCR middleman
  - Understands visual context (dark mode, icons, layout)
  - Reads text AND understands meaning in one step
  - Dramatically better accuracy on real-world screenshots

Fallback:
  If Gemini fails → OCR + rule-based classification (never breaks)

Categories:
  - task, reminder, expense, link, note
"""

import os
import re
import json
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ── Gemini Setup (new google-genai package) ────────────
try:
    from google import genai
    from google.genai import types
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_AVAILABLE and GEMINI_API_KEY and GEMINI_API_KEY != "your_api_key_here":
    client = genai.Client(api_key=GEMINI_API_KEY)
    USE_LLM = True
else:
    USE_LLM = False


# ── Vision Prompt ──────────────────────────────────────
VISION_PROMPT = """You are SnapLens, an AI that analyzes screenshots.

Look at this screenshot carefully. Your job:
1. READ all meaningful text in the image
2. IGNORE UI noise (nav bars, status bars, icons, buttons, app chrome)
3. IDENTIFY the core content the user wanted to capture
4. CLASSIFY it into one category

Categories (pick exactly one):
- "task" — assignments, to-dos, deadlines, action items
- "reminder" — dates, events, appointments, scheduled things
- "expense" — payments, bills, receipts, transactions, prices
- "link" — URLs, website references, resource links
- "note" — general information, knowledge, anything else

Respond in this EXACT JSON format (no markdown, no backticks, no extra text):
{
  "extracted_text": "The meaningful text you can read from the screenshot (focus on content, skip UI elements)",
  "category": "task|reminder|expense|link|note",
  "title": "Short, clear title (max 50 chars)",
  "summary": "1-2 sentence summary of WHAT MATTERS in this screenshot",
  "key_detail": "Most important specific detail (date, amount, URL) or null",
  "suggested_action": "What the user should do with this (be specific)"
}

Rules:
- extracted_text should contain the ACTUAL CONTENT, not every pixel of text
- Title should be descriptive, not generic
- For expenses: extract exact amounts
- For tasks: extract deadlines
- For links: extract URLs
- If the image has no meaningful text, say so honestly"""


# ── Main Analysis Function ─────────────────────────────
def analyze_screenshot(image_path: str) -> dict:
    """
    Analyze a screenshot using Gemini Vision.

    Args:
        image_path: Path to the screenshot image file

    Returns:
        Dictionary with: extracted_text, category, title, summary,
        key_detail, suggested_action
    """

    if USE_LLM:
        result = _analyze_with_gemini(image_path)
        if result:
            return result

    # Fallback: OCR + rules
    return _analyze_with_fallback(image_path)


# ── Gemini Vision Analysis ─────────────────────────────
def _analyze_with_gemini(image_path: str) -> dict | None:
    """Send image directly to Gemini Vision for analysis."""
    try:
        # Upload the image file to Gemini
        uploaded_file = client.files.upload(file=image_path)

        # Send image + prompt to Gemini
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[uploaded_file, VISION_PROMPT]
        )

        raw = response.text.strip()

        # Clean markdown wrapping if present
        if raw.startswith("```"):
            raw = re.sub(r'^```(?:json)?\s*', '', raw)
            raw = re.sub(r'\s*```$', '', raw)

        result = json.loads(raw)

        # Validate required fields
        required = ["extracted_text", "category", "title", "summary", "suggested_action"]
        if not all(key in result for key in required):
            return None

        # Validate category
        valid_categories = {"task", "reminder", "expense", "link", "note"}
        if result["category"] not in valid_categories:
            result["category"] = "note"

        if "key_detail" not in result:
            result["key_detail"] = None

        return result

    except Exception as e:
        print(f"[SnapLens] Gemini Vision error, falling back: {e}")
        return None


# ── Fallback: OCR + Rule-Based ─────────────────────────
def _analyze_with_fallback(image_path: str) -> dict:
    """Fallback using Tesseract OCR + keyword rules."""
    try:
        from backend.app.ocr import extract_text
        text = extract_text(image_path)
    except Exception:
        text = ""

    if not text or len(text.strip()) < 3:
        return {
            "extracted_text": "",
            "category": "note",
            "title": "Unreadable Screenshot",
            "summary": "Could not extract meaningful text from this screenshot.",
            "key_detail": None,
            "suggested_action": "Try uploading a clearer screenshot.",
        }

    # Rule-based classification
    text_lower = text.lower()
    scores = {}
    for category, keywords in CATEGORY_KEYWORDS.items():
        scores[category] = sum(1 for kw in keywords if kw in text_lower)

    max_score = max(scores.values())
    category = max(scores, key=scores.get) if max_score > 0 else "note"

    key_detail = None
    if category in ("task", "reminder"):
        match = DATE_PATTERN.search(text)
        key_detail = match.group(0) if match else None
    elif category == "expense":
        match = MONEY_PATTERN.search(text)
        key_detail = match.group(0) if match else None
    elif category == "link":
        match = URL_PATTERN.search(text)
        key_detail = match.group(0) if match else None

    lines = [line.strip() for line in text.split("\n") if line.strip()]
    title = lines[0][:47] + "..." if lines and len(lines[0]) > 50 else (lines[0] if lines else f"New {category.capitalize()}")

    actions = {
        "task": "Save as task" + (f" (due: {key_detail})" if key_detail else ""),
        "reminder": "Create reminder" + (f" for {key_detail}" if key_detail else ""),
        "expense": "Log expense" + (f" of {key_detail}" if key_detail else ""),
        "link": "Save link" + (f": {key_detail}" if key_detail else ""),
        "note": "Save as note for reference",
    }

    clean_text = " ".join(text.split())
    summary = clean_text[:100] + "..." if len(clean_text) > 100 else clean_text

    return {
        "extracted_text": text,
        "category": category,
        "title": title,
        "summary": summary,
        "key_detail": key_detail,
        "suggested_action": actions.get(category, "Save as note"),
    }


# ── Keyword data for fallback ─────────────────────────
CATEGORY_KEYWORDS = {
    "task": [
        "assignment", "submit", "homework", "due", "deadline",
        "complete", "finish", "todo", "to-do", "to do",
        "project", "task", "deliver", "pending", "must do",
    ],
    "reminder": [
        "remind", "remember", "don't forget", "appointment",
        "meeting", "schedule", "calendar", "event", "tomorrow",
        "today", "tonight", "next week", "attend",
    ],
    "expense": [
        "₹", "$", "rs", "rupee", "dollar", "paid", "payment",
        "upi", "transaction", "receipt", "invoice", "bill",
        "amount", "total", "price", "debit", "credit",
        "gpay", "paytm", "phonepe", "purchase", "cost",
    ],
    "link": [
        "http://", "https://", "www.", ".com", ".org", ".in",
        ".io", ".dev", ".net", "github", "linkedin", "youtube",
        "url", "website", "visit", "click here",
    ],
}

DATE_PATTERN = re.compile(
    r'\b(\d{1,2}[-/]\d{1,2}[-/]\d{2,4}|\d{1,2}\s+(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\w*\s+\d{2,4})\b',
    re.IGNORECASE
)
MONEY_PATTERN = re.compile(r'[₹$]?\s*\d+[,.]?\d*(?:\.\d{1,2})?', re.IGNORECASE)
URL_PATTERN = re.compile(r'https?://[^\s]+|www\.[^\s]+', re.IGNORECASE)
