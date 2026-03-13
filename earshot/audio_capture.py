"""Audio capture module - records system audio from BlackHole."""

import os
import tempfile
import threading
import time
import wave
from collections.abc import Callable
from pathlib import Path

import numpy as np
import pyaudio


class AudioCapture:
    """Records audio from a specified input device (e.g., BlackHole)."""

    SAMPLE_RATE = 16000
    CHANNELS = 1
    CHUNK_SIZE = 1024
    FORMAT = pyaudio.paInt16

    def __init__(
        self,
        device_name: str = "BlackHole 2ch",
        chunk_duration: int = 30,
        silence_timeout: int = 60,
        on_chunk_ready: Callable[[Path], None] | None = None,
        on_silence_timeout: Callable[[], None] | None = None,
        on_audio_level: Callable[[float], None] | None = None,
        save_chunks: bool = True,
    ):
        """
        Initialize audio capture.

        Args:
            device_name: Name of input device to record from
            chunk_duration: Duration of each audio chunk in seconds
            silence_timeout: Seconds of silence before auto-stopping
            on_chunk_ready: Callback when a chunk is ready for processing
            on_silence_timeout: Callback when silence timeout is reached
            on_audio_level: Callback with current audio level (0.0-1.0)
            save_chunks: If False, only monitors audio levels without saving
        """
        self.device_name = device_name
        self.chunk_duration = chunk_duration
        self.silence_timeout = silence_timeout
        self.on_chunk_ready = on_chunk_ready
        self.on_silence_timeout = on_silence_timeout
        self.on_audio_level = on_audio_level
        self.save_chunks = save_chunks

        self.audio = pyaudio.PyAudio()
        self.stream = None
        self.recording = False
        self.thread = None

        self.chunks: list[Path] = []
        self.temp_dir = None

        # Silence detection
        self.silence_threshold = 500  # Amplitude threshold
        self.last_sound_time = 0

        # Current audio level (0.0 to 1.0) for visualization
        self.current_level = 0.0
        self._level_lock = threading.Lock()

    def get_current_level(self) -> float:
        """Get the current audio level (0.0 to 1.0)."""
        with self._level_lock:
            return self.current_level

    def _set_current_level(self, level: float) -> None:
        """Set the current audio level."""
        with self._level_lock:
            self.current_level = min(1.0, max(0.0, level))

    def find_device_index(self) -> int | None:
        """Find the index of the specified audio device."""
        for i in range(self.audio.get_device_count()):
            info = self.audio.get_device_info_by_index(i)
            if self.device_name.lower() in info["name"].lower():
                if info["maxInputChannels"] > 0:
                    return i
        return None

    def list_devices(self) -> list[dict]:
        """List all available input devices."""
        devices = []
        for i in range(self.audio.get_device_count()):
            info = self.audio.get_device_info_by_index(i)
            if info["maxInputChannels"] > 0:
                devices.append(
                    {
                        "index": i,
                        "name": info["name"],
                        "channels": info["maxInputChannels"],
                    }
                )
        return devices

    def start(self) -> bool:
        """
        Start recording audio.

        Returns:
            True if recording started successfully, False otherwise
        """
        if self.recording:
            return False

        device_index = self.find_device_index()
        if device_index is None:
            return False

        if self.save_chunks:
            self.temp_dir = tempfile.mkdtemp(prefix="whisperx_")
        self.chunks = []
        self.recording = True
        self.last_sound_time = time.time()

        self.thread = threading.Thread(target=self._record_loop, args=(device_index,))
        self.thread.daemon = True
        self.thread.start()

        return True

    def stop(self) -> list[Path]:
        """
        Stop recording and return paths to recorded chunks.

        Returns:
            List of paths to recorded audio chunks
        """
        self.recording = False

        if self.thread and self.thread is not threading.current_thread():
            self.thread.join(timeout=2.0)
            self.thread = None

        return self.chunks

    def get_elapsed_time(self) -> float:
        """Get elapsed recording time in seconds."""
        return len(self.chunks) * self.chunk_duration

    def _record_loop(self, device_index: int) -> None:
        """Main recording loop (runs in separate thread)."""
        try:
            self.stream = self.audio.open(
                format=self.FORMAT,
                channels=self.CHANNELS,
                rate=self.SAMPLE_RATE,
                input=True,
                input_device_index=device_index,
                frames_per_buffer=self.CHUNK_SIZE,
            )

            frames = []
            chunk_samples = self.SAMPLE_RATE * self.chunk_duration
            samples_recorded = 0
            chunk_index = 0

            while self.recording:
                try:
                    data = self.stream.read(self.CHUNK_SIZE, exception_on_overflow=False)
                    samples_recorded += self.CHUNK_SIZE

                    # Only store frames if we're saving chunks
                    if self.save_chunks:
                        frames.append(data)

                    # Check for silence and update level
                    audio_data = np.frombuffer(data, dtype=np.int16)
                    amplitude = np.abs(audio_data).mean()

                    # Update current level for visualization (normalize to 0-1)
                    # Max int16 amplitude is ~32768, typical speech is 500-5000
                    normalized_level = min(1.0, amplitude / 5000.0)
                    self._set_current_level(normalized_level)

                    # Call level callback if set
                    if self.on_audio_level:
                        self.on_audio_level(normalized_level)

                    if amplitude > self.silence_threshold:
                        self.last_sound_time = time.time()
                    elif time.time() - self.last_sound_time > self.silence_timeout:
                        if self.on_silence_timeout:
                            self.on_silence_timeout()
                        break

                    # Save chunk when duration reached (only if saving)
                    if self.save_chunks and samples_recorded >= chunk_samples:
                        chunk_path = self._save_chunk(frames, chunk_index)
                        self.chunks.append(chunk_path)

                        if self.on_chunk_ready:
                            self.on_chunk_ready(chunk_path)

                        frames = []
                        samples_recorded = 0
                        chunk_index += 1

                except OSError:
                    continue

            # Save remaining frames (only if saving)
            if self.save_chunks and frames:
                chunk_path = self._save_chunk(frames, chunk_index)
                self.chunks.append(chunk_path)

            self.stream.stop_stream()
            self.stream.close()

        except Exception as e:
            print(f"Recording error: {e}")

        finally:
            self.recording = False

    def _save_chunk(self, frames: list, index: int) -> Path:
        """Save recorded frames to a WAV file."""
        chunk_path = Path(self.temp_dir) / f"chunk_{index:04d}.wav"

        with wave.open(str(chunk_path), "wb") as wf:
            wf.setnchannels(self.CHANNELS)
            wf.setsampwidth(self.audio.get_sample_size(self.FORMAT))
            wf.setframerate(self.SAMPLE_RATE)
            wf.writeframes(b"".join(frames))

        return chunk_path

    def cleanup(self) -> None:
        """Clean up temporary files."""
        if self.temp_dir and os.path.exists(self.temp_dir):
            import shutil

            shutil.rmtree(self.temp_dir, ignore_errors=True)

    def __del__(self):
        """Cleanup on deletion."""
        if hasattr(self, "audio"):
            self.audio.terminate()
