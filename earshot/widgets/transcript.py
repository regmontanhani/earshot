"""Transcript viewer widget."""

from PySide6.QtWidgets import QTextEdit


class TranscriptViewer(QTextEdit):
    """Read-only transcript display with speaker labels."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setPlaceholderText("Transcript will appear here after recording...")
        self.setMinimumHeight(150)

    def set_transcript(self, transcript: dict) -> None:
        """Display a transcript with speaker labels."""
        if not transcript:
            self.clear()
            return

        segments = transcript.get("segments", [])
        if not segments:
            # Just show the plain text
            self.setPlainText(transcript.get("text", ""))
            return

        # Build formatted text with speaker labels
        lines = []
        current_speaker = None

        for seg in segments:
            speaker = seg.get("speaker", "")
            text = seg.get("text", "").strip()

            if not text:
                continue

            if speaker and speaker != current_speaker:
                if lines:
                    lines.append("")  # Blank line between speakers
                lines.append(f"[{speaker}]")
                current_speaker = speaker

            lines.append(text)

        self.setPlainText("\n".join(lines))

    def set_text(self, text: str) -> None:
        """Set plain text content."""
        self.setPlainText(text)
