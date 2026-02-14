# 🧠 SnapLens

**Turn forgotten screenshots into actionable tasks, notes, reminders, and structured memory.**

> Built with FastAPI + Tesseract OCR + LLM Intent Classification
> <img width="1919" height="874" alt="image" src="https://github.com/user-attachments/assets/d373b01e-78e7-4d68-bab4-266bdd857ac1" />


## Status: 🚧 In Development (Phase 1 Complete)

---

## What is SnapLens?

People take screenshots of assignments, payments, notes, and links — but they get buried and forgotten. SnapLens uses AI to:

1. **Read** screenshot text (OCR)
2. **Understand** why you saved it (LLM intent detection)
3. **Suggest** a meaningful action
4. **Store** it as structured memory (task / note / reminder / expense / link)

## Current Features

- ✅ FastAPI backend with health check
- ✅ Screenshot upload endpoint with validation (file type + size limit)
- 🔜 OCR text extraction
- 🔜 AI intent classification
- 🔜 Dashboard UI

## Tech Stack

- **Backend:** Python + FastAPI
- **OCR:** Tesseract
- **LLM:** Gemini / OpenAI API
- **Database:** SQLite (MVP)
- **Frontend:** HTML + JS + Tailwind CSS
- **Extension:** Chrome Manifest v3
