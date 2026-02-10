"""
SnapLens — FastAPI Backend Entry Point

This is the main server file. All API routes start here.
Right now it only has a health check endpoint.
We'll add /upload, /analyze, and /items endpoints as we build.
"""

from fastapi import FastAPI

# Create the FastAPI app instance
app = FastAPI(
    title="SnapLens API",
    description="Turn screenshots into actionable tasks, notes, and reminders.",
    version="0.1.0",
)


@app.get("/")
def health_check():
    """
    Health check endpoint.
    Returns a simple JSON to confirm the server is running.
    Every production API has one of these — it's how monitoring tools
    know your service is alive.
    """
    return {"status": "ok", "message": "SnapLens API is running 🧠"}
