# 🧠 SnapLens

**Turn forgotten screenshots into actionable tasks, notes, reminders, and structured memory.**

> Built with FastAPI + Tesseract OCR + LLM Intent Classification
> <img width="1919" height="1079" alt="image" src="https://github.com/user-attachments/assets/dc553d6c-272b-4dbd-8eb8-d1b35c61d8aa" />



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
