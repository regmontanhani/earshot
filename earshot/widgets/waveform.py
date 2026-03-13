"""Waveform visualization widget."""

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import QWidget


class WaveformWidget(QWidget):
    """Real-time audio level visualization."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(60)
        self.setMaximumHeight(80)

        # Audio level history (for smooth visualization)
        self._levels: list[float] = [0.0] * 50
        self._is_recording = False
        self._accent_color = QColor("#4a9eff")

        # Animation timer
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._decay_levels)
        self._timer.setInterval(50)  # 20 FPS

    def set_accent_color(self, color: str) -> None:
        """Set the waveform accent color."""
        self._accent_color = QColor(color)
        self.update()

    def set_recording(self, recording: bool) -> None:
        """Start or stop the waveform animation."""
        self._is_recording = recording
        if recording:
            self._timer.start()
        else:
            self._timer.stop()
            # Fade out
            self._levels = [0.0] * len(self._levels)
            self.update()

    def push_level(self, level: float) -> None:
        """Add a new audio level sample (0.0 to 1.0)."""
        # Shift levels left and add new one
        self._levels = self._levels[1:] + [min(1.0, max(0.0, level))]
        self.update()

    def _decay_levels(self) -> None:
        """Gradually decay levels when no new data."""
        self._levels = [max(0.0, lvl * 0.95) for lvl in self._levels]
        self.update()

    def paintEvent(self, event) -> None:
        """Draw the waveform bars."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        width = self.width()
        height = self.height()
        bar_count = len(self._levels)
        bar_width = max(2, (width - (bar_count - 1) * 2) // bar_count)
        gap = 2

        # Center the bars
        total_width = bar_count * bar_width + (bar_count - 1) * gap
        start_x = (width - total_width) // 2

        # Draw each bar
        for i, level in enumerate(self._levels):
            x = start_x + i * (bar_width + gap)

            # Bar height based on level (minimum 4px)
            bar_height = max(4, int(level * (height - 8)))

            # Center vertically
            y = (height - bar_height) // 2

            # Color with alpha based on level
            color = QColor(self._accent_color)
            if level < 0.1:
                color.setAlpha(80)
            elif level < 0.3:
                color.setAlpha(150)
            else:
                color.setAlpha(255)

            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(color)
            painter.drawRoundedRect(x, y, bar_width, bar_height, 2, 2)

        painter.end()
