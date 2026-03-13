"""Output writer module - generates transcript files in multiple formats."""

import json
from pathlib import Path


def format_timestamp_srt(seconds: float) -> str:
    """Format seconds as SRT timestamp (HH:MM:SS,mmm)."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:06.3f}".replace(".", ",")


def write_json(transcript: dict, output_path: Path) -> None:
    """Write transcript as JSON."""
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(transcript, f, indent=2, ensure_ascii=False)


def write_txt(transcript: dict, output_path: Path) -> None:
    """Write transcript as plain text."""
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(transcript.get("text", ""))


def write_srt(transcript: dict, output_path: Path) -> None:
    """Write transcript as SRT subtitles."""
    segments = transcript.get("segments", [])

    with open(output_path, "w", encoding="utf-8") as f:
        index = 1
        for seg in segments:
            start = seg.get("start", 0)
            end = seg.get("end", 0)
            text = seg.get("text", "").strip()
            speaker = seg.get("speaker", "")

            if not text or end <= start:
                continue

            if speaker:
                text = f"[{speaker}]: {text}"

            f.write(f"{index}\n")
            f.write(f"{format_timestamp_srt(start)} --> {format_timestamp_srt(end)}\n")
            f.write(f"{text}\n\n")
            index += 1


def write_all_formats(
    transcript: dict,
    output_dir: Path,
    base_name: str,
    formats: list[str] | None = None,
) -> list[Path]:
    """Write transcript in all specified formats.

    Args:
        transcript: Transcript dictionary with 'text' and 'segments'
        output_dir: Directory to write files to
        base_name: Base filename (without extension)
        formats: List of formats to write. Defaults to json, txt, srt.

    Returns:
        List of paths to written files
    """
    if formats is None:
        formats = ["json", "txt", "srt"]

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    writers = {
        "json": write_json,
        "txt": write_txt,
        "srt": write_srt,
    }

    written_files = []

    for fmt in formats:
        if fmt in writers:
            output_path = output_dir / f"{base_name}.{fmt}"
            writers[fmt](transcript, output_path)
            written_files.append(output_path)

    return written_files
