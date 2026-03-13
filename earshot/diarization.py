"""Speaker diarization using local Ollama."""

from __future__ import annotations

import json
import subprocess
import time


def ensure_ollama_running() -> bool:
    """
    Ensure Ollama is installed and running. Auto-starts if needed.
    
    Returns:
        True if Ollama is available, False if not installed
    """
    # Check if ollama command exists
    try:
        subprocess.run(
            ["which", "ollama"],
            capture_output=True,
            timeout=5,
        )
    except (subprocess.SubprocessError, FileNotFoundError):
        return False

    # Check if already running by trying to list models
    try:
        result = subprocess.run(
            ["ollama", "list"],
            capture_output=True,
            timeout=5,
        )
        if result.returncode == 0:
            return True
    except (subprocess.SubprocessError, FileNotFoundError):
        pass

    # Not running - try to start it
    try:
        # Start ollama serve in background
        subprocess.Popen(
            ["ollama", "serve"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
        
        # Wait for it to be ready (up to 10 seconds)
        for _ in range(20):
            time.sleep(0.5)
            try:
                result = subprocess.run(
                    ["ollama", "list"],
                    capture_output=True,
                    timeout=5,
                )
                if result.returncode == 0:
                    return True
            except Exception:
                pass
        
        return False
    except Exception:
        return False


def is_ollama_available() -> bool:
    """Check if Ollama is installed and running, auto-starting if needed."""
    return ensure_ollama_running()


def ensure_model_available(model: str = "llama3.2") -> bool:
    """
    Ensure the specified Ollama model is downloaded.
    
    Args:
        model: Model name to check/pull
        
    Returns:
        True if model is available, False otherwise
    """
    if not ensure_ollama_running():
        return False
    
    # Check if model exists
    try:
        result = subprocess.run(
            ["ollama", "list"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if model in result.stdout:
            return True
    except Exception:
        pass
    
    # Model not found - try to pull it
    try:
        print(f"📥 Downloading {model} model (first time only)...")
        result = subprocess.run(
            ["ollama", "pull", model],
            capture_output=True,
            text=True,
            timeout=300,  # 5 minute timeout for download
        )
        return result.returncode == 0
    except Exception:
        return False


def identify_speakers(
    transcript: dict, model: str = "llama3.2", verbose: bool = True
) -> list | None:
    """
    Use Ollama to identify speakers and assign them to segments.

    Args:
        transcript: Transcript dictionary with 'segments'
        model: Ollama model to use
        verbose: Print progress messages

    Returns:
        List of speaker names for each segment, or None if failed
    """
    if not ensure_model_available(model):
        if verbose:
            print("⚠️  Ollama not available or model not found, skipping speaker identification")
        return None

    segments = transcript.get("segments", [])
    if not segments:
        if verbose:
            print("⚠️  No segments for speaker identification")
        return None

    # Build numbered transcript for analysis (limit to first 60 segments)
    analysis_segments = segments[:60]
    transcript_text = "\n".join(
        f"[{i}] {seg.get('text', '').strip()}"
        for i, seg in enumerate(analysis_segments)
        if seg.get("text", "").strip()
    )

    if not transcript_text:
        if verbose:
            print("⚠️  No transcript text for speaker identification")
        return None

    prompt = f"""Analyze this transcript and identify who is speaking in each numbered segment.

Look for:
- Names mentioned ("Hi, I'm John", "Thanks Sarah")
- Self-references and introductions
- Context clues about roles (host, guest, interviewer)
- Speaking patterns and topic changes

Reply ONLY with a JSON array where each element is the speaker name for that segment number.
Example: ["Host", "Guest 1", "Host", "Guest 2", "Host"]

Use real names when mentioned, otherwise use descriptive labels like "Host", "Guest 1", "Interviewer", etc.
The array must have exactly {len(analysis_segments)} elements, one for each segment.

Transcript:
{transcript_text}"""

    try:
        if verbose:
            print("🤖 Identifying speakers with Ollama...")

        result = subprocess.run(
            ["ollama", "run", model],
            input=prompt,
            capture_output=True,
            text=True,
            timeout=120,
        )

        if result.returncode != 0:
            if verbose:
                print("⚠️  Ollama returned an error, skipping speaker identification")
            return None

        # Extract JSON from response
        response = result.stdout.strip()

        # Find JSON array in response
        start = response.find("[")
        end = response.rfind("]") + 1

        if start == -1 or end == 0:
            if verbose:
                print("⚠️  Could not parse speaker identification response")
            return None

        json_str = response[start:end]
        speaker_list = json.loads(json_str)

        if not isinstance(speaker_list, list):
            if verbose:
                print("⚠️  Invalid speaker identification response format")
            return None

        if verbose:
            unique_speakers = set(speaker_list)
            print(f"✅ Identified {len(unique_speakers)} speakers")

        return speaker_list

    except subprocess.TimeoutExpired:
        if verbose:
            print("⚠️  Speaker identification timed out")
        return None
    except (subprocess.SubprocessError, json.JSONDecodeError, Exception) as e:
        if verbose:
            print(f"⚠️  Speaker identification failed: {e}")
        return None


def apply_speaker_names(transcript: dict, speaker_list: list) -> dict:
    """
    Apply speaker names to transcript segments.

    Args:
        transcript: Transcript dictionary with 'segments'
        speaker_list: List of speaker names, one per segment

    Returns:
        Updated transcript with speaker names applied
    """
    if not speaker_list:
        return transcript

    segments = transcript.get("segments", [])
    updated = transcript.copy()
    updated["segments"] = []

    for i, seg in enumerate(segments):
        new_seg = seg.copy()

        # Assign speaker from list (use last known if list is shorter)
        if i < len(speaker_list):
            new_seg["speaker"] = speaker_list[i]
        elif speaker_list:
            new_seg["speaker"] = speaker_list[-1]

        updated["segments"].append(new_seg)

    # Rebuild full text with speaker labels
    text_parts = []
    current_speaker = None
    for seg in updated["segments"]:
        speaker = seg.get("speaker", "")
        text = seg.get("text", "").strip()
        if speaker and speaker != current_speaker:
            text_parts.append(f"\n[{speaker}]: {text}")
            current_speaker = speaker
        else:
            text_parts.append(text)

    updated["text"] = " ".join(text_parts).strip()

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
