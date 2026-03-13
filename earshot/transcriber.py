"""Core transcription module using MLX-Whisper and OpenAI."""

import os
from pathlib import Path

import mlx_whisper


class Transcriber:
    """Wrapper for MLX-Whisper transcription (local, for live recording chunks)."""

    # Available models (MLX-optimized)
    MODELS = {
        "tiny": "mlx-community/whisper-tiny-mlx",
        "base": "mlx-community/whisper-base-mlx",
        "small": "mlx-community/whisper-small-mlx",
        "medium": "mlx-community/whisper-medium-mlx",
        "large-v3": "mlx-community/whisper-large-v3-mlx",
    }

    def __init__(self, model_size: str = "large-v3"):
        """Initialize transcriber with specified model size."""
        if model_size not in self.MODELS:
            raise ValueError(f"Unknown model: {model_size}. Choose from: {list(self.MODELS.keys())}")

        self.model_size = model_size
        self.model_path = self.MODELS[model_size]

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
        audio_path = str(audio_path)

        result = mlx_whisper.transcribe(
            audio_path,
            path_or_hf_repo=self.model_path,
            language=language,
            word_timestamps=True,
            verbose=False,
        )

        return result

    def transcribe_chunks(
        self,
        audio_paths: list[str | Path],
        language: str | None = None,
    ) -> dict:
        """
        Transcribe multiple audio chunks and merge results.

        Args:
            audio_paths: List of paths to audio chunks
            language: Optional language code

        Returns:
            Merged dictionary with 'text' and 'segments' keys
        """
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
        """
        Transcribe an audio file using OpenAI Whisper API.

        Args:
            audio_path: Path to audio file
            language: Optional language code

        Returns:
            Dictionary with 'text' and 'segments' keys
        """
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
    from .config import load_settings
    settings = load_settings()
    return settings.get("openai_api_key")
