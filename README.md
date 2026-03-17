# 🎙️ SpeechFix

An AI-powered web service that captures spoken audio from the browser, transcribes it locally, and provides deep grammatical analysis. Built with **FastAPI**, this project leverages local **OpenAI Whisper** for highly accurate speech-to-text and **Google Gemini (2.5 Flash)** to identify grammatical mistakes, explain errors, and suggest corrected sentences.

## 🚀 Features

* **In-Browser Recording:** Users can record their voice directly from the browser using the native Web `MediaRecorder` API.
* **Asynchronous UI:** Powered by **HTMX** for a seamless, single-page-application (SPA) feel without heavy JavaScript frameworks.
* **Local, High-Accuracy Transcription:** Uses **OpenAI Whisper** running locally on the server to convert spoken audio into raw text, ensuring privacy and handling heavy accents effortlessly.
* **Intelligent Grammar Analysis:** Integrates the **Google Gemini API** to act as an AI grammar teacher—analyzing sentence structure, pinpointing errors, and providing educational feedback.
* **Data Persistence:** Stores transcription sessions and AI feedback in a **MySQL** database using **SQLAlchemy**.

## 🛠️ Tech Stack

### Frontend (The Client)
* **HTML5 & CSS3**
* **Bootstrap 5:** For clean, responsive UI components.
* **HTMX:** For asynchronous form submissions and dynamic DOM swapping.
* **Vanilla JavaScript:** Specifically to handle the browser's Microphone/MediaRecorder API.

### Backend (The Server)
* **Python 3.10+**
* **FastAPI:** Core backend framework.
* **Uvicorn:** ASGI server.
* **Pydub:** For preprocessing and converting browser `.webm` audio into `.wav` formats.
* **python-multipart:** For handling `Blob` audio uploads from the frontend.
* **FFmpeg:** System dependency required for audio decoding.

### AI & External APIs
* **OpenAI Whisper (`openai-whisper`):** Local Speech-to-Text model.
* **Google Gemini (`google-genai`):** LLM for grammar correction and formatting.

### Database & Storage
* **MySQL & SQLAlchemy:** Relational database and ORM.

## 🌊 Application Flow

1. **Initiate:** User clicks "Start Recording" on the frontend.
2. **Capture:** Vanilla JS requests microphone access and records speech.
3. **Compile:** User clicks "Stop Recording"; audio is packaged into a `.webm` `Blob`.
4. **Transmit:** HTMX asynchronously submits the audio to the FastAPI backend.
5. **Receive & Preprocess:** FastAPI accepts the file, and `pydub` standardizes the audio format to `.wav`.
6. **Transcribe:** Audio is passed to the local OpenAI Whisper model, returning raw text.
7. **Analyze:** Text is routed to Google Gemini for grammar evaluation and corrections.
8. **Persist:** Original text, AI corrections, and explanations are saved to MySQL.
9. **Render:** FastAPI returns the feedback as an HTML snippet, which HTMX seamlessly injects into the UI.

## Project Structure

```
grammer_check
│
├── speechfix
│   ├── __init__.py
|   |
│   ├── main.py
|   |
│   ├── api
│   │   └── v1
│   │       ├── router.py
│   │       └── speech_routes.py
│   │
│   ├── core
│   │   ├── config.py
│   │   ├── logging.py
│   │   └── security.py
│   │
│   │
│   ├── models
│   │   ├── database.py
│   │   └── speech_record.py
│   │
│   ├── schemas
│   │   ├── request.py
│   │   └── response.py
│   │
│   ├── services
│   │   ├── analysis_service.py
│   │   ├── grammar_service.py
│   │   └── speech_service.py
│   │
│   ├── static
│   │   ├── app.js
│   │   └── style.css
│   │
│   ├── templates
│   │   └── index.html
│   │
│   ├── utils
│   │   ├── audio_utils.py
│   │   └── text_utils.py
│   │
│   └── workers
│       └── task_queue.py
|
├── docker
├── scripts
├── tests
├── README.md
├── requirements.txt
└── .gitignore

```

## ⚙️ Local Setup & Installation

### 1. System Requirements
* Before installing Python packages, ensure **FFmpeg** is installed on your system:
* **Windows:** Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add it to your system PATH.
* **Mac:** `brew install ffmpeg`
* **Linux:** `sudo apt update && sudo apt install ffmpeg`
