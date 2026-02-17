# 🧠 SnapLens

**Turn screenshots into structured, actionable intelligence — powered by AI vision.**

> Upload a screenshot. SnapLens reads it, understands why you saved it, and suggests what to do next.

![SnapLens Demo](https://github.com/user-attachments/assets/7408c4ba-037f-4200-9be6-9f6c39e0e67d)

---

## The Problem

We take screenshots of assignments, receipts, links, meeting notes — then they sit in our gallery, forgotten. The intent behind the screenshot is lost.

## The Solution

SnapLens is an AI-powered system that:

1. **Sees** the screenshot using Gemini Vision (no OCR middleman)
2. **Understands** intent — is this a task? a payment? a link worth saving?
3. **Suggests** a specific action ("Save as task, due March 15")
4. **Stores** it as structured memory in a searchable dashboard

---

## Architecture

```
┌─────────────────┐     ┌──────────────────────────────┐     ┌─────────────────┐
│  Chrome Extension│     │     FastAPI Backend           │     │    Dashboard     │
│  or Web Upload   │────▶│  Image → Gemini Vision → AI  │────▶│  Tasks / Notes   │
│                  │     │  Analysis → SQLite Save       │     │  Reminders / $   │
└─────────────────┘     └──────────────────────────────┘     └─────────────────┘
```

### AI Pipeline

| Step | What happens | Technology |
|------|-------------|------------|
| 📸 Input | Screenshot uploaded via web or Chrome extension | FastAPI + JavaScript |
| 👁️ Vision | Image sent directly to Gemini — reads AND understands in one step | Gemini 2.0 Flash |
| 🧠 Classification | Categorized as task, reminder, expense, link, or note | Structured prompt engineering |
| 💾 Storage | Saved to SQLite with category, title, summary, key details | SQLite + Pydantic |
| 📋 Dashboard | Filterable view with tabs, stats, and delete | Vanilla HTML/CSS/JS |

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Python 3.12 · FastAPI · Uvicorn |
| **AI Engine** | Google Gemini 2.0 Flash (Vision) |
| **Database** | SQLite (zero-config, file-based) |
| **Frontend** | Vanilla HTML · CSS · JavaScript |
| **Extension** | Chrome Manifest v3 |
| **Fallback** | Tesseract OCR + keyword rules (if Gemini unavailable) |

---

## Features

- 📸 **Screenshot upload** — drag & drop or file picker, with type/size validation
- 👁️ **Gemini Vision analysis** — reads images directly, handles dark UIs, icons, styled text
- 🧠 **Intent classification** — categorizes into task / reminder / expense / link / note
- 💡 **Smart suggestions** — "Save as task (due: March 15)" with extracted key details
- 📋 **Dashboard** — tabbed view with stats, category filtering, and delete
- 🧩 **Chrome Extension** — capture any tab with one click, get instant AI analysis
- 🔄 **Graceful fallback** — if Gemini is down, falls back to OCR + rules

---

## Quick Start

### 1. Clone & Setup

```bash
git clone https://github.com/okayniti/SnapLens.git
cd SnapLens
python -m venv venv
source venv/Scripts/activate   # Windows/Git Bash
pip install -r backend/requirements.txt
```

### 2. Add Your Gemini API Key

Get a free key at [aistudio.google.com](https://aistudio.google.com), then:

```bash
# Create .env in project root
echo "GEMINI_API_KEY=your_key_here" > .env
```

### 3. Run the Server

```bash
uvicorn backend.app.main:app --reload
```

### 4. Open the App

- **Web UI:** [http://127.0.0.1:8000/app](http://127.0.0.1:8000/app)
- **Dashboard:** [http://127.0.0.1:8000/app/dashboard.html](http://127.0.0.1:8000/app/dashboard.html)
- **API Docs:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

### 5. Chrome Extension (optional)

1. Go to `chrome://extensions/`
2. Enable **Developer mode**
3. Click **Load unpacked** → select the `extension/` folder
4. Click the SnapLens icon on any page to capture & analyze

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Health check |
| `POST` | `/upload` | Upload screenshot for AI analysis |
| `POST` | `/items` | Save an analyzed result |
| `GET` | `/items` | List saved items (`?category=task`) |
| `DELETE` | `/items/{id}` | Delete a saved item |

---

## Project Structure

```
SnapLens/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI routes + CRUD endpoints
│   │   ├── intent.py         # Gemini Vision analysis + fallback
│   │   ├── ocr.py            # Tesseract OCR (fallback only)
│   │   ├── database.py       # SQLite connection + schema
│   │   └── models.py         # Pydantic request/response models
│   └── requirements.txt
├── frontend/
│   ├── index.html            # Upload page with video background
│   └── dashboard.html        # Saved items dashboard
├── extension/
│   ├── manifest.json          # Chrome extension config (Manifest v3)
│   ├── popup.html/css/js      # Extension popup UI + logic
│   └── icons/                 # Extension icons
├── .env                       # API key (not committed)
└── .gitignore
```

---

## Design Decisions

| Decision | Why |
|----------|-----|
| **Gemini Vision over Tesseract** | Tesseract fails on dark UIs, icons, styled text. Gemini sees the actual image. |
| **Rule-based fallback** | App works offline/without API key. Never breaks. |
| **SQLite over PostgreSQL** | Zero config for MVP. Easy to upgrade later. |
| **Modular intent.py** | Swapped from keywords → Gemini without touching main.py. Interface stayed the same. |
| **Chrome Extension** | Real workflow shortcut — capture from any tab without leaving the page. |

---

## What I Learned

- **AI Engineering:** Prompt design, vision API integration, structured output parsing
- **System Design:** Modular architecture, dependency-first development, graceful degradation
- **Product Thinking:** Real problem → MVP → iterate. Not features for features' sake.
- **Full Stack:** FastAPI backend, vanilla frontend, Chrome extension, SQLite persistence

---

## License

MIT

---

Built with 🧠 by [okayniti](https://github.com/okayniti)
