"""Speaker diarization using local Ollama."""

import json
import subprocess
from typing import Optional


def is_ollama_available() -> bool:
    """Check if Ollama is installed and running."""
    try:
        result = subprocess.run(
            ["ollama", "list"],
            capture_output=True,
            timeout=5,
        )
        return result.returncode == 0
    except (subprocess.SubprocessError, FileNotFoundError):
        return False


def identify_speakers(transcript: dict, model: str = "llama3.2") -> Optional[dict]:
    """
    Use Ollama to identify speakers in a transcript.
    
    Args:
        transcript: Transcript dictionary with 'segments'
        model: Ollama model to use
    
    Returns:
        Dictionary mapping speaker IDs to names, or None if failed
    """
    if not is_ollama_available():
        return None
    
    # Build transcript text for analysis (first 50 segments for context)
    segments = transcript.get("segments", [])[:50]
    transcript_text = "\n".join(
        f"SPEAKER_{i % 3:02d}: {seg.get('text', '').strip()}"
        for i, seg in enumerate(segments)
        if seg.get("text", "").strip()
    )
    
    if not transcript_text:
        return None
    
    prompt = f"""Below is a transcript with speaker labels like SPEAKER_00, SPEAKER_01, etc. Based on the conversation context, names mentioned, and how people refer to each other, identify who each speaker is.

Reply ONLY with a JSON object mapping speaker IDs to names, like:
{{"SPEAKER_00": "John Smith", "SPEAKER_01": "Jane Doe"}}

If you cannot identify a speaker, use a descriptive label like "Host" or "Guest 1".

Transcript:
{transcript_text}"""

    try:
        result = subprocess.run(
            ["ollama", "run", model],
            input=prompt,
            capture_output=True,
            text=True,
            timeout=60,
        )
        
        if result.returncode != 0:
            return None
        
        # Extract JSON from response
        response = result.stdout.strip()
        
        # Find JSON object in response
        start = response.find("{")
        end = response.rfind("}") + 1
        
        if start == -1 or end == 0:
            return None
        
        json_str = response[start:end]
        speaker_map = json.loads(json_str)
        
        return speaker_map
    
    except (subprocess.SubprocessError, json.JSONDecodeError, Exception):
        return None


def apply_speaker_names(transcript: dict, speaker_map: dict) -> dict:
    """
    Apply speaker names to transcript segments.
    
    Args:
        transcript: Transcript dictionary with 'segments'
        speaker_map: Dictionary mapping speaker IDs to names
    
    Returns:
        Updated transcript with speaker names applied
    """
    if not speaker_map:
        return transcript
    
    updated = transcript.copy()
    updated["segments"] = []
    
    for seg in transcript.get("segments", []):
        new_seg = seg.copy()
        old_speaker = seg.get("speaker", "")
        
        if old_speaker in speaker_map:
            new_seg["speaker"] = speaker_map[old_speaker]
        
        # Also update text if it contains speaker labels
        text = new_seg.get("text", "")
        for old, new in speaker_map.items():
            text = text.replace(f"[{old}]", f"[{new}]")
            text = text.replace(old, new)
        new_seg["text"] = text
        
        updated["segments"].append(new_seg)
    
    # Update full text as well
    full_text = updated.get("text", "")
    for old, new in speaker_map.items():
        full_text = full_text.replace(f"[{old}]", f"[{new}]")
        full_text = full_text.replace(old, new)
    updated["text"] = full_text
    
    return updated


def diarize_transcript(transcript: dict, model: str = "llama3.2") -> dict:
    """
    Attempt to identify and apply speaker names to transcript.
    
    Args:
        transcript: Transcript dictionary
        model: Ollama model to use
    
    Returns:
        Transcript with speaker names applied (or original if diarization failed)
    """
    speaker_map = identify_speakers(transcript, model)
    
    if speaker_map:
        return apply_speaker_names(transcript, speaker_map)
    
    return transcript
