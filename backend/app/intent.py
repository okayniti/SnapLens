"""
SnapLens — Intent Classification Module

Classifies OCR-extracted text into categories using keyword-based rules.

Current approach: Rule-based (keyword matching)
- Fast, offline, no API needed
- Works well for common screenshot patterns

Future upgrade path: Swap to LLM API (Gemini/OpenAI/Groq) for smarter classification.
The function signature stays the same, so main.py won't need any changes.
That's the beauty of modular design.

Categories:
  - task       (assignments, to-dos, deadlines)
  - reminder   (dates, events, appointments)
  - expense    (payments, bills, receipts, UPI transactions)
  - link       (URLs, website references)
  - note       (default — general information)
"""

import re


# ── Keyword Rules ──────────────────────────────────────
# Each category has a set of keywords/patterns that indicate it.
# The classifier checks which category has the most keyword matches.
# This is simple but effective for screenshots with clear text.

CATEGORY_KEYWORDS = {
    "task": [
        "assignment", "submit", "homework", "due", "deadline",
        "complete", "finish", "todo", "to-do", "to do",
        "project", "task", "deliver", "hand in", "turn in",
        "pending", "remaining", "do this", "must do",
    ],
    "reminder": [
        "remind", "remember", "don't forget", "appointment",
        "meeting", "schedule", "calendar", "event", "tomorrow",
        "today", "tonight", "next week", "next month",
        "am", "pm", "o'clock", "sharp", "attend",
    ],
    "expense": [
        "₹", "$", "rs", "rs.", "rupee", "rupees", "dollar",
        "paid", "payment", "upi", "transaction", "receipt",
        "invoice", "bill", "amount", "total", "price",
        "debit", "credit", "bank", "gpay", "paytm", "phonepe",
        "purchase", "order", "shopping", "cost",
    ],
    "link": [
        "http://", "https://", "www.", ".com", ".org", ".in",
        ".io", ".dev", ".net", ".edu", "github", "linkedin",
        "youtube", "instagram", "twitter", "discord", "link",
        "url", "website", "visit", "click here", "open",
    ],
}

# Patterns that help extract key details from text
DATE_PATTERN = re.compile(
    r'\b(\d{1,2}[-/]\d{1,2}[-/]\d{2,4}|\d{1,2}\s+(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\w*\s+\d{2,4}|\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\w*\s+\d{1,2}(?:,?\s+\d{2,4})?)\b',
    re.IGNORECASE
)

MONEY_PATTERN = re.compile(
    r'[₹$]?\s*\d+[,.]?\d*(?:\.\d{1,2})?',
    re.IGNORECASE
)

URL_PATTERN = re.compile(
    r'https?://[^\s]+|www\.[^\s]+',
    re.IGNORECASE
)


def _count_keyword_matches(text_lower: str, keywords: list) -> int:
    """Count how many keywords from the list appear in the text."""
    return sum(1 for keyword in keywords if keyword in text_lower)


def _extract_key_detail(text: str, category: str) -> str | None:
    """
    Extract the most relevant detail based on category.
    - task/reminder → look for dates
    - expense → look for money amounts
    - link → look for URLs
    """
    if category in ("task", "reminder"):
        match = DATE_PATTERN.search(text)
        return match.group(0) if match else None
    elif category == "expense":
        match = MONEY_PATTERN.search(text)
        return match.group(0) if match else None
    elif category == "link":
        match = URL_PATTERN.search(text)
        return match.group(0) if match else None
    return None


def _generate_title(text: str, category: str) -> str:
    """Generate a short title from the first meaningful line of text."""
    # Get first non-empty line
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    if not lines:
        return f"New {category.capitalize()}"

    # Take first line, truncate to ~50 chars
    first_line = lines[0]
    if len(first_line) > 50:
        first_line = first_line[:47] + "..."
    return first_line


def _generate_action(category: str, key_detail: str | None) -> str:
    """Generate a suggested action based on category."""
    actions = {
        "task": "Save as task" + (f" (due: {key_detail})" if key_detail else ""),
        "reminder": "Create reminder" + (f" for {key_detail}" if key_detail else ""),
        "expense": "Log expense" + (f" of {key_detail}" if key_detail else ""),
        "link": "Save link" + (f": {key_detail}" if key_detail else ""),
        "note": "Save as note for reference",
    }
    return actions.get(category, "Save as note")


def classify_intent(text: str) -> dict:
    """
    Classify the intent of extracted screenshot text.

    Args:
        text: The OCR-extracted text from a screenshot

    Returns:
        Dictionary with: category, title, summary, key_detail, suggested_action

    How it works:
    1. Convert text to lowercase for matching
    2. Count keyword matches for each category
    3. The category with the most matches wins
    4. If no strong match, default to "note"
    5. Extract relevant details (dates, amounts, URLs)
    6. Generate a title and suggested action
    """

    # Handle empty or very short text
    if not text or len(text.strip()) < 3:
        return {
            "category": "note",
            "title": "Unreadable Screenshot",
            "summary": "Could not extract meaningful text from this screenshot.",
            "key_detail": None,
            "suggested_action": "Try uploading a clearer screenshot.",
        }

    text_lower = text.lower()

    # Count keyword matches for each category
    scores = {}
    for category, keywords in CATEGORY_KEYWORDS.items():
        scores[category] = _count_keyword_matches(text_lower, keywords)

    # Find the category with the highest score
    # If all scores are 0, default to "note"
    max_score = max(scores.values())
    if max_score == 0:
        category = "note"
    else:
        category = max(scores, key=scores.get)

    # Extract key detail based on category
    key_detail = _extract_key_detail(text, category)

    # Generate title and action
    title = _generate_title(text, category)
    suggested_action = _generate_action(category, key_detail)

    # Build summary from first ~100 chars of text
    clean_text = " ".join(text.split())  # collapse whitespace
    summary = clean_text[:100] + "..." if len(clean_text) > 100 else clean_text

    return {
        "category": category,
        "title": title,
        "summary": summary,
        "key_detail": key_detail,
        "suggested_action": suggested_action,
    }
