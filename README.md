# 🦥 Bill & Document Sloth

> **“Stop sorting paperwork. Start living.”**  
> *A 100% Local-First AI Document Assistant & Deadline Tracker for Hacktoberfest 2026 Week 3: Slow and Steady (`#hf26challenge`).*

[![Bill & Document Sloth CI](https://github.com/Ayushgupta1715/bill-and-document-sloth/actions/workflows/ci.yml/badge.svg)](https://github.com/Ayushgupta1715/bill-and-document-sloth/actions)
[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/Ayushgupta1715/bill-and-document-sloth)

> 🎥 **[Watch 1-Minute Demo Video on YouTube](https://youtu.be/kEPmFs-7-N0)** | **[Download Local MP4](assets/demo_video.mp4)**

---

## 🌟 The "Slow and Steady" Philosophy

In celebration of International Sloth Day and Hacktoberfest Week 3, **Bill & Document Sloth** is built around a simple truth: **AI should do the tedious, repetitive paperwork so you don't have to.**

Instead of spending precious hours deciphering confusing PDF bills, calculating payment deadlines, renaming cryptic camera scans, and maintaining brittle spreadsheets:
1. **Drop your documents once.**
2. **Local AI extracts the essentials** (Issuer, Category, Due Date, Total Amount, Invoice Number).
3. **Approve with 1 click.**
4. **Relax.** Your files are organized into structured directories and payment deadlines are tracked automatically.

---

## 🏆 Hacktoberfest 2026 Sponsor Track Integrations

To maximize utility and showcase open innovation, **Bill & Document Sloth** incorporates **7 official Hacktoberfest sponsor technologies**:

### 1. 🧠 Google Gemma ($200 — Best Use of Gemma)
* **How it's used:** Integrated via [`app/gemma_service.py`](file:///c:/Users/hp/Downloads/challenge%204/app/gemma_service.py) to run Google's **Gemma open-weight model** (e.g. `gemma-2-2b-it`).
* **Feature:** Deep structured extraction, field confidence verification, and reasoning traces comparing complex bill clauses.
* **How to trigger:** Click **"Verify with Gemma"** in the split-screen review modal!

### 2. 🔮 Prior Labs TabPFN ($200 — Best Use of TabPFN)
* **How it's used:** Integrated via [`app/tabpfn_analyzer.py`](file:///c:/Users/hp/Downloads/challenge%204/app/tabpfn_analyzer.py) utilizing Prior Labs' **TabPFN-3.5 tabular foundation model**.
* **Features:**
  * **Expense Forecasting:** Learns from historical utility bills in SQLite and predicts next month's expected energy and internet costs.
  * **Tabular Anomaly Detection:** Flags unexpected spikes (e.g., electricity bills jumping +40% over historical baseline) with actionable recommendations.
* **How to trigger:** View the **"TabPFN-3.5 Tabular AI Forecast"** widget directly on the main dashboard!

### 3. 🚀 Render ($200 — Best Use of Render)
* **How it's used:** Production [`render.yaml`](file:///c:/Users/hp/Downloads/challenge%204/render.yaml) Blueprint spec and multi-stage [`Dockerfile`](file:///c:/Users/hp/Downloads/challenge%204/Dockerfile).
* **Feature:** Complete cloud hosting of the FastAPI document intelligence runtime and web dashboard with 1-click deployment.

### 4. 🔊 ElevenLabs ($100 — Best Use of ElevenLabs)
* **How it's used:** Integrated via [`app/voice_service.py`](file:///c:/Users/hp/Downloads/challenge%204/app/voice_service.py) giving our sloth agent a calming voice.
* **Feature:** Sloth Audio Briefings — delivers spoken reminders of pending bills and warranties (*"Hello! I am your Bill Sloth. You have 2 bills due this week totaling ₹2,849..."*).
* **How to trigger:** Click **"Sloth Audio Briefing"** on the top navigation bar!

### 5. 🔍 Sentry Agent Tracing ($100 — Best Use of Sentry)
* **How it's used:** Integrated via `sentry-sdk` in [`app/main.py`](file:///c:/Users/hp/Downloads/challenge%204/app/main.py).
* **Feature:** Traces end-to-end latency of document parsing, OCR pipelines, and model extraction.

### 6. 🌐 .tech Domains ($100 — Best Use of a .tech Domain)
* **How it's used:** Domain configuration ready for claiming a free 1-year `.tech` domain (e.g., `slothdocs.tech`) via `hacktoberfest.com/my/promos` and mapping to Render.

### 7. 🤖 GitHub Copilot & Actions ($100 — Best Use of GitHub)
* **How it's used:** Automated CI pipeline in [`.github/workflows/ci.yml`](file:///c:/Users/hp/Downloads/challenge%204/.github/workflows/ci.yml) testing all models, schemas, and endpoints on every push.

---

## 🛡️ Privacy by Design (Why Open Innovation Matters)

Traditional document managers send personal bills, bank statements, and medical policies to external cloud LLM APIs. This introduces privacy risks, subscription costs, and breaks down without an active internet connection.

**Bill & Document Sloth** is proudly **100% local-first**:
* 🔒 **Zero Data Leaks:** All document parsing, text extraction, and categorization run on local hardware.
* 💾 **Local SQLite Storage:** Metadata and action logs are kept in `sloth_documents.db`.
* ⚡ **Offline Resilience:** Works completely offline in airplane mode or disconnected environments.
* 🤝 **Human-in-the-Loop:** AI proposes; you verify and approve. No file is moved or renamed without your consent.
* 🔄 **Reversible Actions (Undo):** Every organization action can be safely undone with a single click.

---

## 🏗️ Architecture

```
[ Uploaded Documents (PDF/Images) ]
               │
               ▼
   [ Local Extraction Pipeline ]
   ├─ PyPDF Text Extraction (pypdf)
   ├─ Google Gemma Open-Weight Model (gemma-2-2b-it)
   └─ Deterministic Rule Engine & NLP Normalization
               │
               ▼
[ Human-in-the-Loop Review & Approval ]
               │
     ┌─────────┴─────────┐
     ▼                   ▼
[ SQLite DB ]   [ Reversible Organization ]
 (sloth_docs)    (documents/organized/{Category}/{Year}/)
     │
     ▼
[ TabPFN-3.5 Tabular Intelligence ]
 ├─ Next-Month Utility Expense Forecasting
 └─ Bill Amount Anomaly Detection (+% Outliers)
     │
     ▼
[ ElevenLabs Voice Briefings ]
```

---

## ⚡ Quick Start

### 1. Prerequisites
* Python 3.10+ (Tested on Python 3.14)
* Modern web browser (Chrome, Edge, Firefox, Safari)

### 2. Installation
```bash
git clone https://github.com/Ayushgupta1715/bill-and-document-sloth.git
cd bill-and-document-sloth

pip install -r requirements.txt
```

### 3. Run the App
```bash
python run.py
```
This automatically initializes the local database, boots the FastAPI service, and opens `http://127.0.0.1:8000` in your default browser.

---

## 🧪 Automated Testing

Run the full test suite covering document classification, date extraction, filename sanitization, Pydantic validations, Gemma reasoning, and TabPFN tabular forecasting:

```bash
python -m pytest tests
# 20 passed in 5.80s
```

---

## 📄 License

MIT License. Open-source for Hacktoberfest 2026.
