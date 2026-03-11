"""Output writer module - generates transcript files in multiple formats."""

import json
from pathlib import Path
from typing import Optional


def format_timestamp_srt(seconds: float) -> str:
    """Format seconds as SRT timestamp (HH:MM:SS,mmm)."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:06.3f}".replace(".", ",")


def format_timestamp_vtt(seconds: float) -> str:
    """Format seconds as VTT timestamp (HH:MM:SS.mmm)."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:06.3f}"


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
            
            # Skip empty or zero-duration segments
            if not text or end <= start:
                continue
            
            f.write(f"{index}\n")
            f.write(f"{format_timestamp_srt(start)} --> {format_timestamp_srt(end)}\n")
            f.write(f"{text}\n\n")
            index += 1


def write_vtt(transcript: dict, output_path: Path) -> None:
    """Write transcript as WebVTT subtitles."""
    segments = transcript.get("segments", [])
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("WEBVTT\n\n")
        
        for seg in segments:
            start = seg.get("start", 0)
            end = seg.get("end", 0)
            text = seg.get("text", "").strip()
            
            # Skip empty or zero-duration segments
            if not text or end <= start:
                continue
            
            f.write(f"{format_timestamp_vtt(start)} --> {format_timestamp_vtt(end)}\n")
            f.write(f"{text}\n\n")


def write_tsv(transcript: dict, output_path: Path) -> None:
    """Write transcript as TSV (tab-separated values)."""
    segments = transcript.get("segments", [])
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("start\tend\ttext\n")
        
        for seg in segments:
            start = seg.get("start", 0)
            end = seg.get("end", 0)
            text = seg.get("text", "").strip().replace("\t", " ")
            
            # Skip empty or zero-duration segments
            if not text or end <= start:
                continue
            
            start_ms = int(start * 1000)
            end_ms = int(end * 1000)
            f.write(f"{start_ms}\t{end_ms}\t{text}\n")


def write_all_formats(
    transcript: dict,
    output_dir: Path,
    base_name: str,
    formats: Optional[list[str]] = None,
) -> list[Path]:
    """
    Write transcript in all specified formats.
    
    Args:
        transcript: Transcript dictionary with 'text' and 'segments'
        output_dir: Directory to write files to
        base_name: Base filename (without extension)
        formats: List of formats to write. Defaults to all formats.
    
    Returns:
        List of paths to written files
    """
    if formats is None:
        formats = ["json", "txt", "srt", "vtt", "tsv"]
    
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    writers = {
        "json": write_json,
        "txt": write_txt,
        "srt": write_srt,
        "vtt": write_vtt,
        "tsv": write_tsv,
    }
    
    written_files = []
    
    for fmt in formats:
        if fmt in writers:
            output_path = output_dir / f"{base_name}.{fmt}"
            writers[fmt](transcript, output_path)
            written_files.append(output_path)
    
    return written_files
