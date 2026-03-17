# 🎙️ SPEECHFIX — Speech Intelligence

An AI-powered web service designed for interview practice and communication improvement. It captures spoken audio from the browser, transcribes it locally, and provides deep analysis on both grammar and context. Built with **FastAPI**, this project leverages local **OpenAI Whisper** for highly accurate speech-to-text and **Google Gemini (2.5 Flash)** to generate dynamic scenarios and suggest grammatical corrections.

## 🚀 Features

* **Tailored Practice Sessions:** Select specific interview topics (Behavioral, Technical, Situational, Leadership, etc.) and difficulty levels to guide the AI.
* **Smart Microphone Calibration:** Automatically tests the user's microphone before starting, complete with a live audio waveform, ensuring clear capture.
* **Dynamic Interview Scenarios:** Generates and presents random, scenario-based interview questions and hints to help users practice real-world communication.
* **In-Browser Recording:** Users record their responses directly from the browser using the native Web `MediaRecorder` API.
* **Asynchronous UI:** Powered by **HTMX** for a seamless, single-page-application (SPA) feel without heavy JavaScript frameworks. Includes dynamic DOM swapping and inline loading states.
* **Local, High-Accuracy Transcription:** Uses **OpenAI Whisper** running locally on the server to convert spoken audio into raw text, ensuring privacy and handling heavy accents effortlessly.
* **Intelligent Grammar Analysis:** Integrates the **Google Gemini API** to act as an AI interviewer—analyzing sentence structure, generating a grammar score, pinpointing specific errors, and providing a corrected version.

## 🛠️ Tech Stack

### Frontend (The Client)
* **HTML5 & CSS3** (Custom design tokens and animations)
* **Bootstrap 5 & Bootstrap Icons:** For clean, responsive UI components and iconography.
* **HTMX:** For asynchronous form submissions and dynamic HTML injection.
* **Vanilla JavaScript:** Specifically to handle the browser's Microphone/MediaRecorder API, AudioContext visualizers, and state management.

### Backend (The Server)
* **Python 3.10+**
* **FastAPI:** Core backend framework handling routing and API generation.
* **Uvicorn:** ASGI server.
* **Pydub:** For preprocessing and converting browser `.webm` / `.ogg` audio into standard formats.
* **python-multipart:** For handling `Blob` audio uploads from the frontend via HTMX.
* **FFmpeg:** System dependency required for audio decoding.

### AI & External APIs
* **OpenAI Whisper (`openai-whisper`):** Local Speech-to-Text model.
* **Google Gemini (`google-genai`):** LLM for scenario generation, grammar evaluation, and corrections.

## 🌊 Application Flow (5-Stage Architecture)

1. **Stage 0 - Session Setup:** User selects an interview topic and difficulty level.
2. **Stage 1 - Mic Check:** The system requests microphone access and displays a live audio waveform to verify hardware functionality.
3. **Stage 2 - Question Prompt:** FastAPI requests a custom scenario from Gemini based on the user's setup parameters. The question and a helpful hint are displayed on screen.
4. **Stage 3 - Record:** The user speaks their answer, which is recorded by the browser's `MediaRecorder` API. HTMX asynchronously submits the compiled audio blob to the backend.
5. **Stage 4 - Results:** Audio is transcribed by Whisper. The text is analyzed by Gemini. FastAPI returns an HTML partial containing the transcript, a visual score ring, specific error breakdowns, and a corrected response, which HTMX seamlessly injects into the UI.

## 📂 Project Structure

```text
grammer_check
│
├── speechfix
│   ├── __init__.py
│   ├── main.py                <-- FastAPI application entry point
│   │
│   ├── api
│   │   └── v1
│   │       ├── router.py
│   │       ├── questions.py   <-- Gemini question generation routes
│   │       └── speech.py      <-- Audio upload and Whisper analysis routes
│   │
│   ├── core
│   │   ├── config.py
│   │   └── logging.py
│   │
│   ├── services
│   │   ├── grammar_service.py <-- Gemini analysis logic
│   │   ├── scenario_service.py<-- Interview prompt logic
│   │   └── speech_service.py  <-- Whisper transcription logic
│   │
│   ├── static
│   │   ├── app.js             <-- Frontend state, mic API, and visualizer
│   │   └── style.css          <-- UI styling and animations
│   │
│   └── templates
│       ├── index.html         <-- Main HTMX view
│       └── _result.html       <-- Analysis partial returned by HTMX
│
├── .env                       <-- Environment variables (API Keys)
├── requirements.txt           <-- Python dependencies
└── .gitignore
```