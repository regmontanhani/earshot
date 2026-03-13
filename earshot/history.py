"""Session history manager for browsing past transcriptions."""

from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from watchdog.events import FileCreatedEvent, FileSystemEventHandler
from watchdog.observers import Observer


@dataclass
class Session:
    """A recorded transcription session."""

    timestamp: datetime
    base_name: str
    duration: float | None
    preview: str
    files: list[Path]

    @property
    def display_time(self) -> str:
        """Format timestamp for display."""
        return self.timestamp.strftime("%b %d, %I:%M %p")

    @classmethod
    def from_json_file(cls, json_path: Path) -> Session | None:
        """Load session from a JSON transcript file."""
        try:
            with open(json_path) as f:
                data = json.load(f)

            # Parse timestamp from filename: meeting_2026-03-13_15-17-03.json
            base_name = json_path.stem
            timestamp = cls._parse_timestamp(base_name)

            # Extract preview from transcript text
            text = data.get("text", "")
            preview = text[:200] + "..." if len(text) > 200 else text

            # Calculate duration from last segment
            segments = data.get("segments", [])
            duration = segments[-1].get("end", 0) if segments else None

            # Find related files
            files = list(json_path.parent.glob(f"{base_name}.*"))

            return cls(
                timestamp=timestamp,
                base_name=base_name,
                duration=duration,
                preview=preview,
                files=files,
            )
        except Exception:
            return None

    @staticmethod
    def _parse_timestamp(base_name: str) -> datetime:
        """Parse timestamp from base name like 'meeting_2026-03-13_15-17-03'."""
        # Try to extract date/time from the name
        parts = base_name.split("_")
        if len(parts) >= 3:
            try:
                date_str = parts[-2]  # 2026-03-13
                time_str = parts[-1]  # 15-17-03
                dt_str = f"{date_str}_{time_str}"
                return datetime.strptime(dt_str, "%Y-%m-%d_%H-%M-%S")
            except ValueError:
                pass

        # Fall back to file modification time would require Path, use now as fallback
        return datetime.now()


class HistoryManager:
    """Manages session history from the output directory."""

    def __init__(self, output_dir: Path, on_change: Callable[[], None] | None = None):
        self.output_dir = output_dir
        self.on_change = on_change
        self._sessions: list[Session] = []
        self._current_index: int = -1  # -1 means "new session"
        self._observer: Observer | None = None

    @property
    def sessions(self) -> list[Session]:
        """Get all sessions sorted by timestamp (newest first)."""
        return self._sessions

    @property
    def current_session(self) -> Session | None:
        """Get the currently selected session."""
        if 0 <= self._current_index < len(self._sessions):
            return self._sessions[self._current_index]
        return None

    @property
    def current_index(self) -> int:
        """Get current index (-1 for new session)."""
        return self._current_index

    @property
    def total_count(self) -> int:
        """Get total number of sessions."""
        return len(self._sessions)

    @property
    def has_previous(self) -> bool:
        """Check if there's a previous session."""
        return self._current_index < len(self._sessions) - 1

    @property
    def has_next(self) -> bool:
        """Check if there's a next session."""
        return self._current_index > -1

    def scan(self) -> None:
        """Scan output directory for existing sessions."""
        self._sessions = []

        if not self.output_dir.exists():
            return

        # Find all JSON files
        json_files = list(self.output_dir.glob("*.json"))

        for json_path in json_files:
            session = Session.from_json_file(json_path)
            if session:
                self._sessions.append(session)

        # Sort by timestamp, newest first
        self._sessions.sort(key=lambda s: s.timestamp, reverse=True)

    def start_watching(self) -> None:
        """Start watching the output directory for changes."""
        if self._observer:
            return

        self.output_dir.mkdir(parents=True, exist_ok=True)

        handler = _HistoryEventHandler(self)
        self._observer = Observer()
        self._observer.schedule(handler, str(self.output_dir), recursive=False)
        self._observer.start()

    def stop_watching(self) -> None:
        """Stop watching the output directory."""
        if self._observer:
            self._observer.stop()
            self._observer.join()
            self._observer = None

    def go_previous(self) -> Session | None:
        """Navigate to the previous (older) session."""
        if self.has_previous:
            self._current_index += 1
            return self.current_session
        return None

    def go_next(self) -> Session | None:
        """Navigate to the next (newer) session."""
        if self.has_next:
            self._current_index -= 1
            return self.current_session
        return None

    def go_to_new(self) -> None:
        """Navigate to new session mode."""
        self._current_index = -1

    def get_display_label(self) -> str:
        """Get the navigation label text."""
        if self._current_index == -1:
            return "New Session"

        if not self._sessions:
            return "No sessions"

        session = self.current_session
        if session:
            # Show "Mar 13, 3:15 PM (2 of 5)"
            pos = self._current_index + 1
            total = len(self._sessions)
            return f"{session.display_time} ({pos} of {total})"

        return "Unknown session"

    def _on_file_created(self, path: Path) -> None:
        """Handle new file creation."""
        if path.suffix != ".json":
            return

        session = Session.from_json_file(path)
        if session:
            # Insert at correct position to maintain sort order
            self._sessions.insert(0, session)
            self._sessions.sort(key=lambda s: s.timestamp, reverse=True)

            # Adjust current index if we're not at new session
            if self._current_index >= 0:
                self._current_index += 1

            if self.on_change:
                self.on_change()


class _HistoryEventHandler(FileSystemEventHandler):
    """Watchdog event handler for history manager."""

    def __init__(self, manager: HistoryManager):
        self.manager = manager

    def on_created(self, event: FileCreatedEvent) -> None:
        """Handle file creation."""
        if not event.is_directory:
            self.manager._on_file_created(Path(event.src_path))
