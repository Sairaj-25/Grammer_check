"""
Audio transcription service — Faster-Whisper (CPU, int8).

Singleton pattern: the WhisperModel is loaded once and reused.
Audio pipeline: raw bytes → pydub → 16 kHz mono 16-bit WAV → temp file → Whisper.

"""

import io
import logging
import os
import tempfile

from faster_whisper import WhisperModel
from pydub import AudioSegment

from speechfix.core.config import get_settings

logger = logging.getLogger(__name__)

# Singleton model
_model: WhisperModel | None = None


def _get_model() -> WhisperModel:
    """Lazy-load and cache the WhisperModel (loaded once per process)."""
    global _model
    if _model is None:
        settings = get_settings()
        logger.info(
            "Loading WhisperModel: size=%s device=%s compute=%s",
            settings.WHISPER_MODEL_SIZE,
            settings.WHISPER_DEVICE,
            settings.WHISPER_COMPUTE_TYPE,
        )
        _model = WhisperModel(
            settings.WHISPER_MODEL_SIZE,
            device=settings.WHISPER_DEVICE,
            compute_type=settings.WHISPER_COMPUTE_TYPE,
        )
        logger.info("WhisperModel loaded ✓")
    return _model


# Public function (called via run_in_executor)
def transcribe_audio_whisper(audio_bytes: bytes) -> str:
    """
    Converts raw audio bytes to 16 kHz mono WAV and transcribes
    using Faster-Whisper. Returns the transcript string, or an
    error string prefixed with 'Transcription Failed:' on failure.
    """
    tmp_path: str | None = None
    try:
        # 1. Decode audio (webm / ogg / mp4 / wav — whatever the browser sent)
        audio = AudioSegment.from_file(io.BytesIO(audio_bytes))

        # 2. Normalise: Whisper requires 16 kHz, mono, 16-bit PCM
        audio = audio.set_frame_rate(16000).set_channels(1).set_sample_width(2)

        # 3. Write to a temp WAV file on disk.
        #    faster-whisper.transcribe() requires a path or numpy array — NOT BytesIO.
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            audio.export(tmp.name, format="wav")
            tmp_path = tmp.name

        # 4. Transcribe
        model = _get_model()
        segments, info = model.transcribe(tmp_path, beam_size=5)
        transcript = " ".join(seg.text for seg in segments).strip()

        logger.info(
            "Transcribed %.1f s of audio → %d chars",
            info.duration,
            len(transcript),
        )
        return transcript or "No speech detected."

    except Exception as exc:
        logger.error("Whisper transcription error: %s", exc, exc_info=True)
        return f"Transcription Failed: {exc}"

    finally:
        # Always remove the temp file, even on error
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)
