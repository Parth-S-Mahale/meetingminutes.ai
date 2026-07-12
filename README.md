# Meeting Summarizer AI

Meeting Summarizer AI is an end-to-end application that converts meeting audio into structured meeting minutes using **automatic speech recognition (ASR)** and **LLM-based summarization**. It includes a FastAPI backend and a React frontend.

The system accepts an uploaded meeting recording, transcribes it using **OpenAI Whisper**, and then generates:
- a concise **meeting summary**
- **key decisions**
- **action items** with owner/deadline placeholders

This project was built as a real-world assignment submission and is structured as a production-style backend service using **FastAPI**, **SQLite**, **SQLAlchemy**, and **Transformers-based local AI inference**.


---

## Features

- Upload meeting audio files via API
- Automatic speech-to-text transcription using **Whisper**
- Meeting summarization using **Llama / local Hugging Face LLM**
- Structured output:
  - summary
  - key decisions
  - action items
- SQLite persistence for meeting records
- FastAPI + Swagger docs for easy testing
- Configurable via `.env`
- Local GPU support for NVIDIA CUDA setups

---

## Tech Stack

### Backend
- Python 3.11
- FastAPI
- Uvicorn
- SQLAlchemy
- Pydantic / pydantic-settings

### AI / ML
- PyTorch
- Hugging Face Transformers
- Whisper ASR (`openai/whisper-medium.en`)
- LLM summarizer (`meta-llama/Llama-3.2-3B-Instruct` or configurable alternative)

### Storage / Utilities
- SQLite
- FFmpeg
- python-multipart
- python-dotenv

---

## Problem Statement

Meetings often generate long recordings that are difficult to revisit manually. The goal of this project is to automate the workflow of turning a meeting recording into structured minutes.

Given an uploaded audio file, the system should:
1. transcribe the spoken content,
2. summarize the meeting,
3. extract decisions and action items,
4. persist the result for later access.

---

## Architecture Overview

The project follows a simple backend pipeline:

1. **Client uploads meeting audio**
2. FastAPI receives the file and stores it in the `uploads/` directory
3. The audio is passed to the **Whisper ASR pipeline**
4. Whisper generates a transcript
5. The transcript is passed to the **LLM summarization pipeline**
6. The summarizer returns structured JSON:
   - summary
   - key decisions
   - action items
7. The final result is stored in **SQLite**
8. The API returns the processed meeting response

---

## High-Level Flow

```text
Audio Upload
   ↓
FastAPI Endpoint
   ↓
Save File to uploads/
   ↓
Whisper ASR (Transcription)
   ↓
Transcript
   ↓
LLM Summarization Prompt
   ↓
Structured Meeting Summary JSON
   ↓
Persist to SQLite
   ↓
Return API Response
```

Meeting-Summarizer/
```
│
├── app/
│   ├── api/
│   │   └── meetings.py                # FastAPI routes
│   │
│   ├── prompts/
│   │   └── meeting_summary_prompt.py  # LLM prompt template
│   │
│   ├── schemas/
│   │   └── meeting.py                 # Pydantic request/response schemas
│   │
│   ├── services/
│   │   ├── transcription_service.py   # Whisper transcription pipeline
│   │   └── summarization_service.py   # LLM summarization pipeline
│   │
│   ├── config.py                      # Application settings from .env
│   ├── database.py                    # DB engine + session config
│   ├── models.py                      # SQLAlchemy models
│   └── main.py                        # FastAPI app entry point
│
├── uploads/                           # Uploaded audio files
├── outputs/                           # Optional generated output artifacts
├── meeting_summarizer.db              # SQLite database (local)
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Setup Instructions

### Frontend

The React + Vite client lives in `frontend/` and communicates with the FastAPI API using Axios.

```bash
cd frontend
npm install
npm run dev
```

It opens at `http://localhost:5173` and expects the backend at `http://127.0.0.1:8000/api/v1` by default. Copy `frontend/.env.example` to `frontend/.env` to customize the API URL.

### 1. Clone the repository
```
git clone <your-repo-url>
cd Meeting-Summarizer
```
### 2. Create virtual environment
```
python -m venv venv
```
- Windows PowerShell
```
.\venv\Scripts\activate
```

- macOS / Linux
```
source venv/bin/activate
```

### 3. Install dependencies
```
pip install -r requirements.txt
```

### 4. Install FFmpeg
FFmpeg is required for loading and decoding audio files before transcription.

#### Windows
Install FFmpeg and make sure it is available in PATH.

#### Example
```bash
winget install Gyan.FFmpeg
```

#### Then verify:
```bash
ffmpeg -version
```

5. Create .env<br>
Create a .env file in the project root using .env.example as reference.

6. Run the app
```bash
uvicorn app.main:app --reload
```
Once running, open:

- Swagger UI: `http://127.0.0.1:8000/docs`
- OpenAPI JSON: `http://127.0.0.1:8000/openapi.json`

## Environment Variables

**Example configuration:**
```env
PROJECT_NAME=Meeting Summarizer AI
API_V1_PREFIX=/api/v1

DATABASE_URL=sqlite:///./meeting_summarizer.db
UPLOAD_DIR=uploads
OUTPUT_DIR=outputs

MAX_UPLOAD_SIZE_MB=100
ALLOWED_AUDIO_EXTENSIONS=[".mp3",".wav",".m4a",".aac",".mp4"]

ASR_MODEL_ID=openai/whisper-medium.en
ASR_DEVICE=cuda
ASR_DTYPE=float16
ASR_CHUNK_LENGTH_S=30

SUMMARIZER_MODEL_ID=meta-llama/Llama-3.2-3B-Instruct
SUMMARIZER_DEVICE_MAP=auto
SUMMARIZER_LOAD_IN_4BIT=False
MAX_NEW_TOKENS=300
TEMPERATURE=0.2
TOP_P=0.9

HF_TOKEN=your_huggingface_token_here
```

## API Endpoints
`POST /api/v1/meetings/upload`

Uploads a meeting audio file, transcribes it, summarizes it, stores the result, and returns the structured meeting output.

#### **Form Data**
- file → audio file (.mp3, .wav, .m4a, .aac, .mp4)
- title → optional meeting title

#### **Example request using Swagger UI**
Open `/docs`, choose the upload endpoint, attach an audio file, and submit.

#### **Output Response**
```json
{
  "id": 1,
  "title": "Sprint Planning Meeting",
  "audio_filename": "sprint_planning.mp3",
  "transcript": "We discussed the sprint backlog, ownership of API tasks, and deadlines for deployment...",
  "summary": "The team reviewed the sprint backlog, assigned API and frontend tasks, and agreed on the deployment timeline for the next release.",
  "key_decisions": [
    "API integration will be completed before frontend testing begins.",
    "The next sprint demo is scheduled for Friday."
  ],
  "action_items": [
    {
      "task": "Implement upload endpoint validation",
      "owner": "Backend Team",
      "deadline": "Friday"
    },
    {
      "task": "Prepare frontend integration test cases",
      "owner": "Frontend Team",
      "deadline": "Next sprint"
    }
  ],
  "created_at": "2026-07-09T18:30:00"
}
```

## Example Workflow

1. Start the FastAPI server
2. Open Swagger UI at `http://127.0.0.1:8000/docs`
3. Upload a meeting recording
4. The system:
   - stores the audio file
   - transcribes it using Whisper
   - generates a structured summary using the summarizer model
   - saves the result in SQLite
5. The API returns the processed meeting object

## Model Notes
### **ASR**

This project uses:
- openai/whisper-medium.en

for English meeting transcription.

### **Summarization**
This project is configured to use:
- `meta-llama/Llama-3.2-3B-Instruct`
for structured meeting summarization.

Since Llama models may be gated on Hugging Face, access to the model and a valid HF token may be required.

If needed, the summarizer model can be swapped to another supported local Hugging Face causal language model through `.env`.
