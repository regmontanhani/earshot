"""Core transcription module using faster-whisper (cross-platform)."""

from __future__ import annotations

import os
import platform
import subprocess
import threading
from pathlib import Path


def _get_device_and_compute() -> tuple[str, str]:
    """Detect best device and compute type for this machine."""
    system = platform.system()
    machine = platform.machine()

    # Apple Silicon
    if system == "Darwin" and machine == "arm64":
        # faster-whisper uses CPU on macOS but is still fast
        return "cpu", "int8"

    # Try CUDA on Windows/Linux
    if system in ("Windows", "Linux"):
        try:
            import torch
            if torch.cuda.is_available():
                return "cuda", "float16"
        except ImportError:
            pass

    # Default to CPU
    return "cpu", "int8"


class Transcriber:
    """Cross-platform Whisper transcription using faster-whisper."""

    MODELS = ["tiny", "base", "small", "medium", "large-v3", "turbo"]

    def __init__(self, model_size: str = "small"):
        """Initialize transcriber with specified model size."""
        if model_size not in self.MODELS:
            raise ValueError(
                f"Unknown model: {model_size}. Choose from: {self.MODELS}"
            )

        self.model_size = model_size
        self._model = None
        self._lock = threading.Lock()

    def _ensure_model(self):
        """Lazy-load the model."""
        if self._model is not None:
            return

        with self._lock:
            if self._model is not None:
                return

            from faster_whisper import WhisperModel

            device, compute_type = _get_device_and_compute()

            try:
                self._model = WhisperModel(
                    self.model_size,
                    device=device,
                    compute_type=compute_type,
                )
            except Exception as e:
                # Fallback to CPU if GPU fails
                if device != "cpu":
                    self._model = WhisperModel(
                        self.model_size,
                        device="cpu",
                        compute_type="int8",
                    )
                else:
                    raise RuntimeError(f"Failed to load Whisper model: {e}") from e

    def transcribe(
        self,
        audio_path: str | Path,
        language: str | None = None,
    ) -> dict:
        """
        Transcribe an audio file.

        Args:
            audio_path: Path to audio file
            language: Optional language code (e.g., 'en', 'es'). Auto-detected if None.

        Returns:
            Dictionary with 'text' and 'segments' keys
        """
        self._ensure_model()

        segments_iter, info = self._model.transcribe(
            str(audio_path),
            language=language,
            beam_size=5,
            vad_filter=True,
        )

        # Collect segments
        segments = []
        all_text = []

        for segment in segments_iter:
            segments.append({
                "start": segment.start,
                "end": segment.end,
                "text": segment.text.strip(),
            })
            all_text.append(segment.text.strip())

        return {
            "text": " ".join(all_text),
            "segments": segments,
            "language": info.language,
        }

    def transcribe_chunks(
        self,
        audio_paths: list[str | Path],
        language: str | None = None,
    ) -> dict:
        """Transcribe multiple audio chunks and merge results."""
        all_text = []
        all_segments = []
        time_offset = 0.0

        for chunk_path in audio_paths:
            result = self.transcribe(chunk_path, language=language)

            all_text.append(result.get("text", ""))

            for segment in result.get("segments", []):
                adjusted_segment = segment.copy()
                adjusted_segment["start"] += time_offset
                adjusted_segment["end"] += time_offset
                all_segments.append(adjusted_segment)

            # Calculate duration of this chunk for offset
            if result.get("segments"):
                last_end = max(seg["end"] for seg in result["segments"])
                time_offset += last_end

        return {
            "text": " ".join(all_text),
            "segments": all_segments,
        }


class OpenAITranscriber:
    """Wrapper for OpenAI Whisper API (for file transcription)."""

    def __init__(self, api_key: str | None = None):
        """Initialize with OpenAI API key."""
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key required. Set OPENAI_API_KEY or pass api_key.")

        try:
            from openai import OpenAI

            self.client = OpenAI(api_key=self.api_key)
        except ImportError as e:
            raise ImportError("openai package required: pip install openai") from e

    def transcribe(
        self,
        audio_path: str | Path,
        language: str | None = None,
    ) -> dict:
        """Transcribe an audio file using OpenAI Whisper API."""
        audio_path = Path(audio_path)

        with open(audio_path, "rb") as f:
            response = self.client.audio.transcriptions.create(
                model="whisper-1",
                file=f,
                language=language,
                response_format="verbose_json",
                timestamp_granularities=["segment"],
            )

        # Convert OpenAI response to our format
        segments = []
        for seg in getattr(response, "segments", []) or []:
            segments.append({
                "start": seg.get("start", 0),
                "end": seg.get("end", 0),
                "text": seg.get("text", ""),
            })

        return {
            "text": response.text,
            "segments": segments,
        }

    def transcribe_chunks(
        self,
        audio_paths: list[str | Path],
        language: str | None = None,
    ) -> dict:
        """Transcribe multiple audio chunks and merge results."""
        all_text = []
        all_segments = []
        time_offset = 0.0

        for chunk_path in audio_paths:
            result = self.transcribe(chunk_path, language=language)
            all_text.append(result.get("text", ""))

            for segment in result.get("segments", []):
                adjusted_segment = segment.copy()
                adjusted_segment["start"] += time_offset
                adjusted_segment["end"] += time_offset
                all_segments.append(adjusted_segment)

            if result.get("segments"):
                last_end = max(seg["end"] for seg in result["segments"])
                time_offset += last_end

        return {
            "text": " ".join(all_text),
            "segments": all_segments,
        }


def get_openai_api_key() -> str | None:
    """Get OpenAI API key from environment, .env file, or config."""
    # Check environment first
    if key := os.environ.get("OPENAI_API_KEY"):
        return key

    # Try loading from .env file
    env_file = Path(__file__).parent.parent / ".env"
    if env_file.exists():
        try:
            for line in env_file.read_text().splitlines():
                line = line.strip()
                if line.startswith("OPENAI_API_KEY="):
                    return line.split("=", 1)[1].strip()
        except Exception:
            pass

    # Check config file
    from earshot.config import load_settings

    settings = load_settings()
    return settings.get("openai_api_key")
