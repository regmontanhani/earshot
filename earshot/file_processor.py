"""File processor module - handles audio/video file input."""

import os
import subprocess
import tempfile
from pathlib import Path

# Supported formats
VIDEO_EXTENSIONS = {".mp4", ".mkv", ".mov", ".avi", ".webm", ".m4v", ".wmv", ".flv"}
AUDIO_EXTENSIONS = {".m4a", ".mp3", ".wav", ".flac", ".ogg", ".aac", ".wma", ".opus"}


def is_video_file(path: Path) -> bool:
    """Check if file is a video format."""
    return path.suffix.lower() in VIDEO_EXTENSIONS


def is_audio_file(path: Path) -> bool:
    """Check if file is an audio format."""
    return path.suffix.lower() in AUDIO_EXTENSIONS


def is_supported_file(path: Path) -> bool:
    """Check if file is a supported audio or video format."""
    return is_video_file(path) or is_audio_file(path)


def get_file_duration(path: Path) -> float | None:
    """Get duration of audio/video file in seconds using ffprobe."""
    try:
        result = subprocess.run(
            [
                "ffprobe",
                "-v",
                "quiet",
                "-show_entries",
                "format=duration",
                "-of",
                "csv=p=0",
                str(path),
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        return float(result.stdout.strip())
    except (subprocess.CalledProcessError, ValueError):
        return None


def extract_audio(video_path: Path, output_path: Path | None = None) -> Path:
    """
    Extract audio from video file.

    Args:
        video_path: Path to video file
        output_path: Optional path for output. If None, creates temp file.

    Returns:
        Path to extracted audio file (WAV format)
    """
    if output_path is None:
        fd, output_path = tempfile.mkstemp(suffix=".wav")
        os.close(fd)
        output_path = Path(output_path)

    subprocess.run(
        [
            "ffmpeg",
            "-i",
            str(video_path),
            "-vn",
            "-acodec",
            "pcm_s16le",
            "-ar",
            "16000",
            "-ac",
            "1",
            str(output_path),
            "-y",
            "-loglevel",
            "error",
        ],
        check=True,
    )

    return output_path


def prepare_audio(input_path: Path) -> tuple[Path, bool]:
    """
    Prepare audio file for transcription.

    For video files, extracts audio to a temp file.
    For audio files, returns the path as-is.

    Args:
        input_path: Path to input file

    Returns:
        Tuple of (audio_path, is_temp) where is_temp indicates if cleanup is needed
    """
    input_path = Path(input_path)

    if not input_path.exists():
        raise FileNotFoundError(f"File not found: {input_path}")

    if is_video_file(input_path):
        audio_path = extract_audio(input_path)
        return audio_path, True
    else:
        return input_path, False


def get_output_base_name(input_path: Path) -> str:
    """Get base name for output files (filename without extension)."""
    return input_path.stem
