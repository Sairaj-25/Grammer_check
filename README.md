# 🎙️ 🎙️ InterviewIQ AI — Speech Intelligence for Interview Mastery

An AI-powered web service designed for **interview practice and communication improvement**. It captures spoken audio from the browser, transcribes it locally, and provides deep analysis on both grammar and context. Built with **FastAPI**, this project leverages local **faster-whisper** for highly accurate offline speech-to-text and **Google Gemini (2.5 Flash)** to generate dynamic scenarios and suggest grammatical corrections.

---

## 🚀 Features

- **Tailored Practice Sessions:** Select specific interview topics (Behavioral, Technical, Situational, Leadership, etc.) and difficulty levels to guide the AI.
- **Smart Microphone Calibration:** Automatically tests the user's microphone before starting, complete with a live audio waveform, ensuring clear capture.
- **Dynamic Interview Scenarios:** Generates and presents random, scenario-based interview questions and hints to help users practice real-world communication.
- **In-Browser Recording:** Users record their responses directly from the browser using the native Web `MediaRecorder` API.
- **Asynchronous UI:** Powered by **HTMX** for a seamless, single-page-application (SPA) feel without heavy JavaScript frameworks. Includes dynamic DOM swapping and inline loading states.
- **Local, High-Accuracy Transcription:** Uses **faster-whisper** running entirely on-device to convert spoken audio into raw text, ensuring privacy and handling heavy accents effortlessly.
- **Intelligent Grammar Analysis:** Integrates the **Google Gemini API** to act as an AI interviewer — analyzing sentence structure, generating a grammar score, pinpointing specific errors, and providing a corrected response.

---

## 🛠️ Tech Stack

### Frontend
| Technology | Purpose |
|---|---|
| HTML5 / CSS3 | Custom design tokens and animations |
| Bootstrap 5 + Bootstrap Icons | Responsive UI components and iconography |
| HTMX | Async form submissions and dynamic HTML injection |
| Vanilla JavaScript | Microphone / MediaRecorder API, AudioContext visualizer, state management |

### Backend
| Technology | Purpose |
|---|---|
| Python 3.10+ | Core language |
| FastAPI | Backend framework, routing, API generation |
| Uvicorn | ASGI server |
| Pydub | Preprocessing `.webm` / `.ogg` audio into standard formats |
| python-multipart | Handles audio `Blob` uploads from the frontend |
| FFmpeg | System dependency for audio decoding |
| SQLAlchemy | ORM for session persistence |

### AI & External APIs
| Technology | Purpose |
|---|---|
| `faster-whisper` | Local offline Speech-to-Text model |
| `google-genai` (Gemini 2.5 Flash) | Scenario generation, grammar evaluation, and corrections |

---

## 🌊 Application Flow — 5-Stage Architecture

```
Stage 1 → Stage 2 → Stage 3 → Stage 4 → Stage 5
  Setup     Mic      Question   Record    Results
           Check    Prompt
```

| Stage | Name | Description |
|---|---|---|
| **1** | Session Setup | User selects interview topic and difficulty level |
| **2** | Mic Check | Live audio waveform displayed to verify microphone hardware |
| **3** | Question Prompt | Gemini generates a scenario-based question + hint based on setup |
| **4** | Record | User speaks their answer; audio blob submitted via HTMX |
| **5** | Results | faster-whisper transcribes → Gemini analyzes → score, errors, and corrected response injected into UI |

---

## 📂 Project Structure

```
InterviewIQ/
│
├── speechfix/
│   ├── __init__.py
│   ├── main.py                               # FastAPI application entry point
|   ├── .env                                  # Environment variables (API Keys)
│   │
│   ├── api/
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── router.py                     # All endpoint routers are registered here
│   │       └── endpoints/
│   │                 ├── analysis.py         # Analyses grammar with Gemini, returns the result_partial.html
│   │                 └── questions.py        # Gemini question generation routes
│   │           
│   │
│   ├── models/
│   │   └── faster-whisper-model-small-en-in-0.4/  # Local faster-whisper model (Optional)
│   │
│   ├── services/
│   │   ├── grammar_service.py                # Gemini grammar analysis logic
│   │   ├── generate_question_service.py      # Interview prompt generation logic
│   │   └── audio_transcribe_service.py       # faster-whisper transcription logic
│   │
│   ├── static/
│   │   ├── app.js                            # Frontend state, mic API, and visualizer
│   │   └── style.css                         # UI styling and animations
│   │
│   └── templates/
│       ├── index.html                        # Main HTMX view
│       └── result_partial.html               # Analysis partial returned by HTMX
│
├── requirements.txt                          # Python dependencies
├── README.md                    
└── .gitignore
```

---

## ⚙️ Local Setup & Installation

### 1. System Requirements

Install **FFmpeg** before installing Python packages:

| OS | Command |
|---|---|
| **Windows** | Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to system PATH |
| **macOS** | `brew install ffmpeg` |
| **Linux** | `sudo apt update && sudo apt install ffmpeg` |

### 2. Clone the Repository

```bash
git clone https://github.com/Sairaj-25/Grammer_check.git
cd Grammer_check
```

### 3. Create a Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure Environment Variables

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_google_gemini_api_key_here
```

Get your Gemini API key from [Google AI Studio](https://aistudio.google.com/app/apikey).

### 6. Run the Application

```bash
uvicorn speechfix.main:app --reload
```

The app will be available at **http://127.0.0.1:8000**

---

## 🔌 API Endpoints

### Frontend
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Main application view |


### Question Generation
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/questions/generate` | Generate a scenario-based interview question via Gemini |


### Audio Analysis
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/analyze` | Upload audio blob → transcribe + grammar analysis → returns HTML partial |

---

## 🔑 Environment Variables

| Variable | Required | Description |
|---|---|---|
| `GEMINI_API_KEY` | ✅ Yes | Google Gemini API key for LLM features |

---

## 📦 Key Dependencies

```
fastapi==0.135.1
uvicorn==0.41.0
faster-whisper==1.2.1
google-genai==1.67.0
pydub==0.25.1
SQLAlchemy==2.0.48
Jinja2==3.1.6
python-multipart==0.0.22
python-dotenv==1.2.2
```

> Full list available in [`requirements.txt`](./requirements.txt)

---
