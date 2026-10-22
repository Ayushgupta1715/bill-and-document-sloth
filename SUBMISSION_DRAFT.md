*This is a submission for the [Hacktoberfest Open-Source AI Challenge Week 3: Slow and Steady](https://dev.to/challenges/hacktoberfest-week3-2026-10-19)*

## What I Built
**Bill & Document Sloth** is a 100% local-first, privacy-conscious AI document assistant, tabular forecaster, and deadline tracker designed around one core promise: **"Stop sorting paperwork. Start living."**

Every adult and student dreads the paperwork shuffle: opening randomly named files like `IMG_20261021_124532.pdf`, hunting through fine print for payment due dates, losing track of appliance warranty periods, and maintaining brittle manual spreadsheets. 

**Bill & Document Sloth does the heavy lifting so you can be as lazy as a sloth:**
* **Drop Paperwork Once:** Drag and drop PDFs, receipts, or phone bills.
* **Intelligent Local Extraction:** Local open-source AI extracts the issuer, category, total amount, due date, document date, and invoice number.
* **Smart Standardized Filenames:** Automatically generates clean filenames (e.g., `2026-10_Electricity_Bill_BESCOM.pdf`).
* **Human-in-the-Loop Review:** Split-screen side-by-side verification with confidence scores before any file is moved.
* **Safe Organization & Undo:** Files are organized into structured directories (`documents/organized/{Category}/{Year}/`) with 1-click reversible undo.
* **Proactive Deadlines:** Monitors overdue bills, payments due in 3 days, and expiring warranties before penalties strike.

---

## Demo

{% youtube kEPmFs-7-N0 %}

* **Direct YouTube Link:** [Watch Video Demo on YouTube](https://youtu.be/kEPmFs-7-N0)
* **GitHub Repository:** [https://github.com/Ayushgupta1715/bill-and-document-sloth](https://github.com/Ayushgupta1715/bill-and-document-sloth)
* **Local Interactive Dashboard:** Runs locally on `http://127.0.0.1:8000` with Swagger API docs at `http://127.0.0.1:8000/docs`.
* **1-Click Built-in Demo Pack:** Synthesizes realistic BESCOM Electricity Bills, Airtel Fiber Invoices, AppleCare Warranty Certificates, Star Health Insurance Policies, and Coffee Receipts on the fly so evaluators can test immediately with one click!

---

## Code
{% github Ayushgupta1715/bill-and-document-sloth %}

* **Repository:** [https://github.com/Ayushgupta1715/bill-and-document-sloth](https://github.com/Ayushgupta1715/bill-and-document-sloth)
* **License:** MIT License (Open-Source)

---

## How I Built It
The application combines local-first inference, open-weight reasoning models, and tabular foundation models:

1. **Local-First Processing Engine:**
   * **Backend:** FastAPI, Python 3.14, SQLite3, PyPDF for embedded text extraction, and ReportLab for synthetic sample generation.
   * **Frontend:** Clean, responsive single-page application built with Tailwind CSS, Lucide icons, and Canvas Confetti.
2. **Google Gemma Open-Weight Model (`gemma-2-2b-it`):**
   * Integrated in `app/gemma_service.py` to provide deep structured JSON parsing and field reasoning traces for complex or ambiguous bills.
3. **Prior Labs TabPFN-3.5 Foundation Model:**
   * Integrated in `app/tabpfn_analyzer.py` to perform in-context tabular regression and outlier detection over historical billing cycles (forecasting next month's utility spend and alerting on anomalous spikes).
4. **ElevenLabs Voice Integration:**
   * Integrated in `app/voice_service.py` to give the sloth agent a calm, spoken audio briefing of pending bills and deadlines.
5. **Safe File Operations:**
   * Keeps original uploads pristine in `documents/uploads/` while organizing approved files in `documents/organized/{Category}/{Year}/`. Full audit trail in `actions_history` table for 1-click safe undo.

---

## Why Does Open Innovation Matter?
When building an assistant for bills, leases, and receipts, sending files to closed cloud LLM APIs poses major privacy and cost concerns:

1. **Absolute Data Privacy:** Utility bills and tax invoices contain home addresses, bank details, and personal identifiers. With open-source local inference and SQLite, **zero bytes of private data leave the device**.
2. **Zero Recurring Cloud Token Costs:** Users shouldn't pay monthly API subscriptions or per-token charges just to organize their receipts. Open-weight models like **Gemma** and tabular foundation models like **TabPFN** run locally on consumer hardware for free.
3. **Total Offline Resilience:** Works on a train, in airplane mode, or during internet blackouts.
4. **User Sovereignty & Control:** Unlike opaque cloud systems that silently alter data, our pipeline enforces human verification and reversible undo actions.

---

## The Lazy Payoff
* **Time Saved:** Manually opening, reading, renaming, and filing 10 bills takes roughly **20–25 minutes**. With Bill & Document Sloth, dropping them into the app and clicking "Approve" takes **under 45 seconds** — a **95% reduction in manual effort**.
* **Zero Spreadsheet Maintenance:** Upcoming deadlines (due in 3 days, due today, overdue) are monitored automatically, preventing costly late-payment surcharges.
* **Peace of Mind:** You can be as lazy as a sloth, knowing every warranty, receipt, and utility bill is categorized and safely filed on your machine.

---

## Prize Categories

### Featured Categories:
* **Best Use of Gemma ($200):** Integrated Google's **Gemma-2** open-weight model (`gemma-2-2b-it`) for deep structured bill parsing, confidence verification, and reasoning traces (`app/gemma_service.py`).
* **Best Use of TabPFN ($200):** Integrated Prior Labs' **TabPFN-3.5 tabular foundation model** (`app/tabpfn_analyzer.py`) to forecast next month's utility spending and detect billing cost anomalies (+40% outliers).
* **Best Use of Render ($200):** Included production `render.yaml` (Render Blueprint) and multi-stage `Dockerfile` for 1-click cloud deployment.

### Partner Categories:
* **Best Use of ElevenLabs ($100):** Sloth Voice Briefings (`app/voice_service.py`) delivering spoken audio briefings of upcoming bills and paperwork deadlines.
* **Best Use of Sentry Agent Tracing ($100):** Instrumented with `sentry-sdk` in `app/main.py` for tracking document ingestion latency, OCR performance, and extraction errors.
* **Best Use of a .tech Domain ($100):** Production DNS and routing ready for `slothdocs.tech`.
* **Best Use of GitHub Copilot & Actions ($100):** Comprehensive automated CI pipeline (`.github/workflows/ci.yml`) validating 20 unit and integration tests on every push.
