"""Core transcription module using MLX-Whisper."""

import os
from pathlib import Path
from typing import Optional
import mlx_whisper


class Transcriber:
    """Wrapper for MLX-Whisper transcription."""
    
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
        language: Optional[str] = None,
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
        language: Optional[str] = None,
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
