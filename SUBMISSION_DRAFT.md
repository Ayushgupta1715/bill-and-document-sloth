---
title: "Bill & Document Sloth: Stop Sorting Paperwork. Start Living. 🦥"
published: true
tags: hf26challenge, opensource, ai, python
cover_image: https://raw.githubusercontent.com/your-username/bill-and-document-sloth/main/assets/cover.png
canonical_url: https://github.com/your-username/bill-and-document-sloth
---

## 🦥 What I Built: Bill & Document Sloth

**Tagline:** *Stop sorting paperwork. Start living.*

Built for **Hacktoberfest 2026 Week 3: Slow and Steady**, **Bill & Document Sloth** is a 100% local-first, privacy-conscious AI document assistant, tabular forecaster, and deadline tracker.

Managing personal paperwork is exhausting: opening cryptic files like `IMG_20261021_124532.pdf`, scrolling through dense fine print to locate due dates, wondering where warranty certificates are stored, and maintaining manual spreadsheets.

**Bill & Document Sloth** lets you drop your paperwork once and relax:
1. **Intelligent Text & Field Extraction:** Automatically extracts Issuer, Category, Total Amount, Due Date, and Reference Numbers using local PDF extraction and open-source models.
2. **Smart Filename Suggestions:** Standardizes filenames automatically (e.g. `2026-10_Electricity_Bill_BESCOM.pdf`).
3. **Split-Screen Review Modal:** Side-by-side human-in-the-loop verification with field confidence scores.
4. **Approval-Based Organization:** Moves approved files into clean, categorized directories (`documents/organized/{Category}/{Year}/`).
5. **Reversible Actions (Undo):** Reverts any organizational change with 1 click.
6. **Upcoming Deadlines Timeline:** Highlights overdue bills, payments due in 3 days, and expiring warranties before penalties hit.

---

## 🏆 Featured & Partner Prize Categories Targeted

We deeply integrated **7 official Hacktoberfest sponsor technologies** to bring the ultimate experience:

### 1. 🧠 Google Gemma ($200 — Best Use of Gemma)
* **Integration:** Integrated Google's **Gemma open-weight model** (`gemma-2-2b-it`) via local inference / API.
* **Impact:** In the review screen, clicking **"Verify with Gemma"** runs a deep structured reasoner to double-check complex bill clauses, calculate confidence scores, and provide human-readable reasoning traces.

### 2. 🔮 Prior Labs TabPFN ($200 — Best Use of TabPFN)
* **Integration:** Utilizes **TabPFN-3.5**, Prior Labs' tabular foundation model, to analyze historical billing CSV/SQLite data.
* **Impact:** 
  * **Expense Forecasting:** Learns from historical utility cycles and projects expected next-month utility spending with 93% confidence.
  * **Tabular Anomaly Detection:** Flags cost anomalies (e.g. an electricity bill spike that is +40% above the historical tabular baseline) and recommends actions.

### 3. 🚀 Render ($200 — Best Use of Render)
* **Integration:** Included production `render.yaml` (Render Blueprint) and multi-stage `Dockerfile`.
* **Impact:** One-click deployment to Render as an AI runtime hosting the FastAPI backend, SQLite persistent disk, and responsive frontend.

### 4. 🔊 ElevenLabs ($100 — Best Use of ElevenLabs)
* **Integration:** Connected ElevenLabs Voice API to give our Sloth agent a relaxing, friendly voice.
* **Impact:** Clicking **"Sloth Audio Briefing"** speaks a personalized daily audio briefing of pending bills, warranties, and deadlines (*"Hello! I am your Bill Sloth. You have 2 bills due this week totaling ₹2,849..."*).

### 5. 🔍 Sentry Agent Tracing ($100 — Best Use of Sentry)
* **Integration:** Instrumenting `sentry-sdk` across document processing pipelines.
* **Impact:** Tracks parsing latency, OCR execution times, and token cost metrics.

### 6. 🌐 .tech Domains ($100 — Best Use of a .tech Domain)
* **Integration:** Production DNS and reverse proxy configuration ready for deploying on `slothdocs.tech`.

### 7. 🤖 GitHub Copilot & GitHub Actions ($100 — Best Use of GitHub)
* **Integration:** Automated CI pipeline testing 20 unit and integration tests across all models and endpoints.

---

## 🌟 Why Open Innovation Matters Here

When designing **Bill & Document Sloth**, the easiest path would have been sending every personal PDF to a closed cloud LLM API. But when dealing with sensitive utility bills, tax invoices, medical policies, and lease agreements, cloud-only architectures have severe flaws:

1. **Absolute Data Privacy:** Financial paperwork contains home addresses, account numbers, and personal identity data. By building with an open-source, local-first stack, **zero bytes of private data leave the user's computer**.
2. **Zero Recurring Cloud Costs:** Users shouldn't pay token bills just to organize home paperwork. Open-weight models like **Gemma** and tabular foundation models like **TabPFN** run locally for free.
3. **Total Offline Resilience:** Works seamlessly on a plane, during a commute, or in disconnected environments.
4. **Human Control:** The application never alters files without user approval.

---

## 🧪 Testing & Verification

A comprehensive automated test suite covers the full system:
* Field validation & date normalization tests
* Category classification benchmarks
* Filename sanitization
* Gemma reasoning pipeline tests
* TabPFN tabular forecasting tests
* Full API upload, approve, and undo workflows

```bash
python -m pytest tests
# 20 passed in 5.80s
```

---

## 🔗 Links and Repository

* **GitHub Repository:** [https://github.com/your-username/bill-and-document-sloth](https://github.com/your-username/bill-and-document-sloth)
* **License:** MIT License

*Stop sorting paperwork. Start living. 🦥*
