"""
SnapLens — Pydantic Models

Defines request/response schemas for the API.

Why Pydantic?
- Automatic validation: if someone sends bad data, FastAPI returns a clear error
- Auto-generated API docs: FastAPI reads these models to build /docs page
- Type safety: catches bugs before they reach the database

These models act as a "contract" between frontend and backend.
The frontend knows exactly what shape of data to send and expect.
"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ItemCreate(BaseModel):
    """
    Schema for saving a new item.

    The frontend sends this after the user clicks "Save as task/note/etc."
    All fields come from the AI analysis result — the frontend just forwards them.
    """
    category: str          # task, note, reminder, expense, link
    title: str             # short title from the screenshot
    summary: Optional[str] = None
    key_detail: Optional[str] = None
    extracted_text: Optional[str] = None
    suggested_action: Optional[str] = None


class ItemResponse(BaseModel):
    """
    Schema for returning a saved item.

    Includes the database-generated id and created_at timestamp.
    This is what the dashboard receives when it fetches saved items.
    """
    id: int
    category: str
    title: str
    summary: Optional[str] = None
    key_detail: Optional[str] = None
    extracted_text: Optional[str] = None
    suggested_action: Optional[str] = None
    created_at: str        # ISO timestamp string
