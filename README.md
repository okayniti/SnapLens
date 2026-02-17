<p align="center">
  <h1 align="center">🧠 SnapLens</h1>
  <p align="center"><strong>Turn forgotten screenshots into actionable tasks, notes, reminders, and structured memory.</strong></p>
  <p align="center">
    <img src="https://img.shields.io/badge/python-3.12-blue?logo=python&logoColor=white" />
    <img src="https://img.shields.io/badge/FastAPI-0.128-009688?logo=fastapi&logoColor=white" />
    <img src="https://img.shields.io/badge/Gemini_Vision-2.0_Flash-4285F4?logo=google&logoColor=white" />
    <img src="https://img.shields.io/badge/Chrome_Extension-Manifest_v3-F7C948?logo=googlechrome&logoColor=white" />
    <img src="https://img.shields.io/badge/status-MVP_Complete-brightgreen" />
  </p>
</p>

---

![SnapLens Demo](https://github.com/user-attachments/assets/7408c4ba-037f-4200-9be6-9f6c39e0e67d)

---

## The Problem

Every day, we screenshot things that matter — an assignment deadline, a UPI payment confirmation, a link someone shared, a meeting reminder, a recipe we want to try later.

Then we never look at them again.

They sit in galleries, buried under memes and random photos. The **intent behind the screenshot is lost** — the task never gets done, the bill is forgotten, the link disappears.

Screenshots are one of the most common digital actions, yet there is **no system that understands why you took one** and helps you act on it.

---

## The Solution

SnapLens treats every screenshot as a **signal of intent**.

Upload a screenshot. SnapLens **sees** it using AI vision, **understands** why you saved it, **classifies** it into a category, and **suggests** what to do next — then stores it as structured, searchable memory.

```
Dead screenshot → Actionable intelligence
```

No manual tagging. No folder organization. Just upload and let the AI handle the rest.

---

## How It Works

```
┌──────────────────────────────────────────────────────────────────────┐
│                         USER JOURNEY                                 │
│                                                                      │
│   📸 Upload Screenshot          🧩 Or capture via Chrome Extension   │
│         │                                │                           │
│         └──────────────┬─────────────────┘                           │
│                        ▼                                             │
│              ┌─────────────────┐                                     │
│              │  FastAPI Backend │                                     │
│              └────────┬────────┘                                     │
│                       ▼                                              │
│              ┌─────────────────┐                                     │
│              │  Gemini Vision   │  ← Reads image directly            │
│              │  AI Analysis     │  ← Classifies intent               │
│              └────────┬────────┘  ← Extracts key details             │
│                       ▼                                              │
│              ┌─────────────────┐                                     │
│              │  Smart Suggestion│  "Save as task (due: March 15)"    │
│              └────────┬────────┘                                     │
│                       ▼                                              │
│              ┌─────────────────┐                                     │
│              │  SQLite Database │  ← Stored as structured memory     │
│              └────────┬────────┘                                     │
│                       ▼                                              │
│              ┌─────────────────┐                                     │
│              │   Dashboard      │  Tasks │ Notes │ Reminders │ $     │
│              └─────────────────┘                                     │
└──────────────────────────────────────────────────────────────────────┘
```

### Step-by-Step User Flow

1. **Upload** — Drag a screenshot into SnapLens (web) or click the Chrome extension on any tab
2. **AI Vision** — Gemini 2.0 Flash reads the image directly — no OCR middleman needed
3. **Classification** — AI categorizes it: `task` · `reminder` · `expense` · `link` · `note`
4. **Key Detail Extraction** — Pulls out dates, amounts, URLs, deadlines automatically
5. **Smart Suggestion** — "Save as task (due: March 15)" or "Log expense of ₹499"
6. **Save** — One click to store as structured memory
7. **Dashboard** — Browse, filter, and manage all saved items by category

---

## Architecture

SnapLens has two components — but they share one brain:

### 1. Web AI Engine (Core Product)
The full experience. Upload screenshots, see AI analysis, manage your dashboard. This is where all data lives.

### 2. Chrome Extension (Input Shortcut)
Captures the current browser tab with one click and sends it to the same backend. Shows a quick suggestion popup. Not a separate app — just a faster way to feed screenshots into the system.

### AI Pipeline

| Stage | What Happens | Technology |
|-------|-------------|------------|
| 📸 **Input** | Screenshot received via web upload or Chrome extension | FastAPI · JavaScript |
| 👁️ **Vision** | Image sent directly to Gemini — reads AND understands in one step | Gemini 2.0 Flash (Vision) |
| 🧠 **Classification** | Categorized as task, reminder, expense, link, or note | Structured prompt engineering |
| 🔑 **Extraction** | Key details pulled out — dates, amounts, URLs, deadlines | LLM structured output |
| 💾 **Storage** | Saved to database with metadata and timestamps | SQLite · Pydantic validation |
| 📋 **Dashboard** | Filterable, categorized view with stats and management | Vanilla HTML/CSS/JS |

### Design Decision: Why Gemini Vision over OCR?

The initial architecture used Tesseract OCR → text → LLM. But OCR **failed on dark UIs, icons, and styled text** — common in real screenshots. Switching to Gemini Vision eliminated the OCR bottleneck entirely. The LLM now *sees* the original image, understanding visual context that text extraction misses.

The old OCR + keyword-matching pipeline is preserved as an automatic fallback — if Gemini is unavailable, the app degrades gracefully instead of breaking.

---

## Tech Stack

| Layer | Technology | Why This Choice |
|-------|-----------|-----------------|
| **Backend** | Python · FastAPI · Uvicorn | Async-ready, auto-generates API docs, type-safe with Pydantic |
| **AI Engine** | Google Gemini 2.0 Flash (Vision) | Multimodal — reads images directly, no OCR step needed |
| **Database** | SQLite | Zero-config for MVP, single-file, easy to upgrade to PostgreSQL |
| **Frontend** | Vanilla HTML · CSS · JavaScript | No framework overhead, fast to iterate, full control |
| **Extension** | Chrome Manifest v3 | Latest Chrome standard, `activeTab` permission (minimal access) |
| **Fallback** | Tesseract OCR + keyword rules | Graceful degradation if Gemini is unavailable |

---

## Features

- 📸 **Screenshot upload** — drag & drop or file picker with type and size validation
- 👁️ **AI vision analysis** — reads images directly, handles dark UIs, icons, and styled text
- 🧠 **Intent classification** — categorizes into task · reminder · expense · link · note
- 🔑 **Key detail extraction** — dates, amounts, URLs pulled automatically
- 💡 **Smart suggestions** — "Save as task (due: March 15)" with contextual actions
- 📋 **Dashboard** — tabbed view with category stats, filtering, and item management
- 🧩 **Chrome Extension** — capture any tab with one click, instant AI analysis
- 🔄 **Graceful fallback** — OCR + rules if Gemini is unavailable, app never breaks
- 🗑️ **Item management** — save, browse, filter, and delete from the dashboard
- 📊 **Category stats** — real-time counts per category on the dashboard

---

## Installation & Local Setup

### Prerequisites

- Python 3.10+ ([download](https://www.python.org/downloads/))
- Git ([download](https://git-scm.com/))
- A free Gemini API key ([get one here](https://aistudio.google.com))

### Setup (Windows / Git Bash)

```bash
# Clone the repository
git clone https://github.com/okayniti/SnapLens.git
cd SnapLens

# Create and activate virtual environment
python -m venv venv
source venv/Scripts/activate    # Windows (Git Bash)
# venv\Scripts\activate         # Windows (CMD)

# Install dependencies
pip install -r backend/requirements.txt

# Set up your API key
echo "GEMINI_API_KEY=your_key_here" > .env
```

### Run

```bash
uvicorn backend.app.main:app --reload
```

### Access

| What | URL |
|------|-----|
| **Web App** | [http://127.0.0.1:8000/app](http://127.0.0.1:8000/app) |
| **Dashboard** | [http://127.0.0.1:8000/app/dashboard.html](http://127.0.0.1:8000/app/dashboard.html) |
| **API Docs** | [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) |

---

## Usage

### Web App
1. Open [http://127.0.0.1:8000/app](http://127.0.0.1:8000/app)
2. Drag & drop a screenshot or click to select one
3. Click **Analyze** — AI reads and classifies the screenshot
4. Review the suggestion → click **Save as Task / Note / Reminder / Expense**
5. Visit the **Dashboard** to browse, filter, and manage saved items

### Chrome Extension
1. Go to `chrome://extensions/` → enable **Developer mode**
2. Click **Load unpacked** → select the `extension/` folder
3. Navigate to any page → click the SnapLens icon in the toolbar
4. Click **Capture Screenshot** → see instant AI analysis
5. Save with one click — it appears on your dashboard

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Health check |
| `POST` | `/upload` | Upload screenshot → AI analysis |
| `POST` | `/items` | Save an analyzed result to database |
| `GET` | `/items` | List saved items (optional `?category=task`) |
| `DELETE` | `/items/{id}` | Remove a saved item |

Full interactive documentation available at `/docs` (auto-generated by FastAPI).

---

## Project Structure

```
SnapLens/
├── backend/
│   ├── app/
│   │   ├── main.py            # FastAPI routes, upload handling, CRUD
│   │   ├── intent.py          # Gemini Vision analysis + fallback engine
│   │   ├── ocr.py             # Tesseract OCR (fallback only)
│   │   ├── database.py        # SQLite connection, schema, queries
│   │   └── models.py          # Pydantic request/response validation
│   ├── uploads/               # Uploaded screenshots (gitignored)
│   └── requirements.txt
├── frontend/
│   ├── index.html             # Upload page with AI analysis UI
│   └── dashboard.html         # Saved items dashboard with tabs
├── extension/
│   ├── manifest.json          # Chrome Manifest v3 config
│   ├── popup.html/css/js      # Extension popup UI + capture logic
│   └── icons/                 # Extension icons
├── .env                       # API key (not committed)
├── .gitignore
└── README.md
```

---

## Future Improvements

| Improvement | Why It Matters |
|-------------|---------------|
| **PostgreSQL migration** | Production-ready persistence, multi-user support |
| **User authentication** | Personal accounts, private data |
| **Full-text search** | Search across all saved items by content |
| **Batch upload** | Analyze multiple screenshots at once |
| **Export to Notion / Google Tasks** | Push saved items to external productivity tools |
| **Mobile PWA** | Upload directly from phone gallery |
| **Webhook integrations** | Auto-create Trello cards, calendar events |

---

## Why This Project Matters

Most AI demos are chatbots or toy classifiers. SnapLens solves a **real behavioral problem** — screenshot hoarding — with a **real AI pipeline**: vision, classification, structured output, and persistent storage.

It demonstrates:
- **AI Engineering** — Prompt design, vision API integration, structured JSON output, graceful degradation
- **System Design** — Modular architecture, dependency-first development, clean separation of concerns
- **Product Thinking** — Real problem → focused MVP → iterate. Not features for features' sake.
- **Full Stack Development** — Python backend, vanilla frontend, Chrome extension, database, API design

---

## Resume-Ready Description

> **SnapLens** — AI-powered screenshot intelligence system that uses Gemini Vision to classify screenshots into actionable categories (tasks, reminders, expenses, notes), extract key details, and store them as structured memory. Built with FastAPI, Gemini 2.0 Flash, SQLite, and a Chrome extension for browser-native capture.

---

## Author

**Niti** — AI/ML student building real-world AI products from scratch.

- GitHub: [@okayniti](https://github.com/okayniti)

---

<p align="center"><sub>Built with focus, shipped with intent.</sub></p>
