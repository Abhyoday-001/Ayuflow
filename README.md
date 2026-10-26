# AyuFlow — AI-Assisted Clinical Intake & Hospital Workflow Platform

[![React](https://img.shields.io/badge/Frontend-React%20%7C%20TypeScript%20%7C%20Vite-61DAFB?logo=react&logoColor=black)](https://react.dev/)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL%20%2B%20pgvector-336791?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Tailwind CSS](https://img.shields.io/badge/Styling-Tailwind%20CSS-06B6D4?logo=tailwindcss&logoColor=white)](https://tailwindcss.com/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

---

## 📖 Definition & Overview

**AyuFlow** is an intelligent clinical intake, documentation, and workflow orchestration platform engineered specifically for modern healthcare facilities and government **AYUSH / Allopathic** hospitals. 

In high-volume Outpatient Departments (OPD), healthcare staff and physicians face severe administrative burdens, lengthy manual queue times, and linguistic barriers. AyuFlow transforms this intake experience through a **voice-first, multilingual clinical intake interface** that accurately translates and structures raw patient symptoms into codified clinical facts, assigns digital OPD queue tokens, and segregates care streams between **Ayurvedic medicine** and **Conventional Allopathy** with strict clinical data boundaries.

---

## 🌟 Key Capabilities

### 1. Multimodal & Voice-First Intake
- **Per-Question Voice Input:** Every clinical inquiry features independent, isolated audio capture (`[🎤 Answer by voice]`) and audio guidance (`[🔊 Read aloud]`).
- **Separated TTS and ASR:** Speech synthesis and speech recognition run in strictly isolated pipelines—preventing microphone feedback loops or autonomous trigger states.
- **Patient Confirmation Stage:** Recorded speech is transcribed and presented for patient validation (*"You said: ... [Confirm] [Edit] [Retry]"*) before entering clinical state.
- **Deterministic Field Mapping:** Transcribed responses are deterministically mapped to predefined clinical scales (e.g., Severity, Blood Group, Dosha metrics) without hallucinated defaults.

### 2. Dual-Stream Segregation (AYUSH & Allopathy)
- **Care Stream Routing:** Patients dynamically select their care stream (Allopathy vs. Ayurveda) after common triage.
- **Ayurvedic Clinical Profiling:** Comprehensive Ashtavidha & Dashavidha Pariksha assessments (Nadi, Mutra, Mala, Jihva, Shabda, Sparsha, Druk, Akruti) and Prakriti analysis.
- **Allopathic Clinical Profiling:** SOCRATES pain analysis and systemic reviews with discrete zero-leakage patient filters on doctor dashboards.

### 3. AI Clinical Fact Extraction & Safety by Design
- **Human-in-the-Loop Review:** AI models (Gemini / Ollama) extract structured symptoms, medical history, and timeline facts with source provenance and confidence scores.
- **Strict Clinical Guardrails:** AyuFlow strictly forbids automated autonomous diagnosis or prescription creation. All extractions are presented as editable drafts for doctor verification.
- **Conflict Detection:** Identifies contraindications and cross-system drug interactions (e.g., blood thinners combined with specific herbal formulations).

### 4. Full Multilingual Architecture
- **Complete End-to-End Localization:** Dynamic translation across English, Hindi, Marathi, Malayalam, and regional Indian languages using unified i18n registries.
- **Zero Hardcoded Language Leaks:** All system buttons, audio prompts, error dialogues, and confirmation cards follow the patient's selected dialect.

### 5. Document OCR & ABDM/FHIR Interoperability
- **Prescription & Lab OCR:** Uploaded prescriptions and lab records are parsed using PaddleOCR into structured JSON records.
- **FHIR R4 & ABDM Ready:** Export patient encounters directly into standard FHIR R4 clinical documents compatible with the Ayushman Bharat Digital Mission (ABDM).

---

## 🏗️ Architecture & Technology Stack

```
                                  ┌───────────────────────────────┐
                                  │      AyuFlow Client (Web)     │
                                  │   React 18 + Vite + Tailwind  │
                                  └───────────────┬───────────────┘
                                                  │ REST / Audio
                                                  ▼
                                  ┌───────────────────────────────┐
                                  │       FastAPI Gateway         │
                                  │   Authentication & Routing    │
                                  └───────┬───────────────┬───────┘
                                          │               │
                 ┌────────────────────────┴────┐     ┌────┴────────────────────────┐
                 ▼                             ▼     ▼                             ▼
       ┌───────────────────┐       ┌─────────────────────┐       ┌─────────────────────┐
       │   AI Engine       │       │    Speech & Audio   │       │   Data & Storage    │
       │  Gemini / Ollama  │       │  ASR: Conformer/VAD │       │ PostgreSQL+pgvector │
       │  Extraction & RAG │       │  TTS: MMS Multi-Lang│       │ Google Cloud Storage│
       └───────────────────┘       └─────────────────────┘       └─────────────────────┘
```

| Layer | Technologies |
| :--- | :--- |
| **Frontend** | React 18, TypeScript, Vite, Tailwind CSS, Lucide Icons, `react-i18next` |
| **Backend API** | Python 3.10+, FastAPI, Pydantic v2, Uvicorn, Alembic |
| **Database** | PostgreSQL 16 with `pgvector` extension, SQLAlchemy Async Engine |
| **ASR (Speech-to-Text)** | IndicConformer (Primary), Faster-Whisper (Fallback), Silero VAD |
| **TTS (Text-to-Speech)** | Meta MMS (Massively Multilingual Speech), Web Speech API |
| **OCR & Vision** | PaddleOCR, TrOCR |
| **Storage & Cloud** | Google Cloud Storage (GCS) / Local Object Storage |

---

## 🚀 Getting Started

### Prerequisites
- **Node.js:** v18.0.0 or higher
- **npm:** v9.0.0 or higher
- **Python:** v3.10+ (uv recommended)
- **Docker & Docker Compose:** Required for PostgreSQL + pgvector database

---

### Step 1: Clone the Repository
```bash
git clone https://github.com/Abhyoday-001/Ayuflow.git
cd Ayuflow
```

---

### Step 2: Database Setup (Docker)
Start the PostgreSQL container equipped with `pgvector`:
```bash
docker compose up -d postgres
```

---

### Step 3: Backend Setup
1. Navigate to the backend directory and configure the environment:
   ```bash
   cd backend
   cp .env.example .env
   ```
2. Create a virtual environment and install dependencies:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
3. Run database migrations:
   ```bash
   alembic upgrade head
   ```
4. Start the FastAPI server:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```
   API interactive documentation will be available at [http://localhost:8000/docs](http://localhost:8000/docs).

---

### Step 4: Frontend Setup
1. From the project root, install Node dependencies:
   ```bash
   npm install
   ```
2. Start the Vite development server:
   ```bash
   npm run dev
   ```
3. Open [http://localhost:5173](http://localhost:5173) in your browser.

---

## 📂 Repository Structure

```
.
├── backend/                  # FastAPI Application
│   ├── alembic/              # Database schema migrations
│   ├── app/
│   │   ├── api/routes/       # Endpoints (auth, intake, encounters, asr, tts)
│   │   ├── core/             # Configuration & language registries
│   │   ├── db/               # SQLAlchemy models & session factory
│   │   ├── schemas/          # Pydantic schemas
│   │   └── services/         # Extraction, ASR, TTS, OCR, and FHIR export
│   └── requirements.txt      # Python dependencies
├── docker/                   # Database initialization scripts
├── docker-compose.yml        # Docker service definitions
├── public/                   # Static assets & brand emblems
├── src/                      # React Frontend Source
│   ├── assets/               # Medical graphics & logos
│   ├── components/           # Reusable UI components & Voice handlers
│   ├── context/              # AppContext & global state providers
│   ├── data/                 # Clinical mock records & fixtures
│   ├── pages/                # Patient, Doctor, Worker, and Admin views
│   ├── types/                # TypeScript interfaces & domain types
│   └── utils/                # Translations, stream classification, helpers
├── package.json              # Frontend npm dependencies & build scripts
└── vite.config.ts            # Vite configuration
```

---

## 🔒 Clinical Safety & AI Governance

AyuFlow is architected around foundational clinical ethics:
1. **Advisory Only:** AyuFlow generates clinical drafts; it does not replace medical judgment.
2. **Transparent Audit Logging:** Every AI-assisted extraction logs its prompt version, confidence rating, and the exact textual source from which it was inferred.
3. **Doctor Verification:** No encounter is finalized until a verified medical officer conducts an evaluation and signs off on the record.

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
