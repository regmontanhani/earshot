"""Waveform visualization widget."""

import math

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor, QLinearGradient, QPainter, QPainterPath
from PySide6.QtWidgets import QWidget


class WaveformWidget(QWidget):
    """Real-time audio level visualization with smooth rounded bars."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(80)
        self.setMaximumHeight(100)

        self._levels: list[float] = [0.0] * 40
        self._is_recording = False
        self._accent_color = QColor("#0A84FF")
        self._glow_color = QColor("#0A84FF")
        self._glow_color.setAlpha(40)

        # Smoother animation at 30 FPS
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._decay_levels)
        self._timer.setInterval(33)

    def set_accent_color(self, color: str) -> None:
        """Set the waveform accent color."""
        self._accent_color = QColor(color)
        self._glow_color = QColor(color)
        self._glow_color.setAlpha(40)
        self.update()

    def set_recording(self, recording: bool) -> None:
        """Start or stop the waveform animation."""
        self._is_recording = recording
        if recording:
            self._timer.start()
        else:
            self._timer.stop()
            self._levels = [0.0] * len(self._levels)
            self.update()

    def push_level(self, level: float) -> None:
        """Add a new audio level sample (0.0 to 1.0)."""
        self._levels = self._levels[1:] + [min(1.0, max(0.0, level))]
        self.update()

    def _decay_levels(self) -> None:
        """Smooth exponential decay."""
        self._levels = [max(0.0, lvl * 0.92) for lvl in self._levels]
        self.update()

    def paintEvent(self, event) -> None:
        """Draw smooth rounded waveform bars with gradient."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = self.width()
        h = self.height()
        bar_count = len(self._levels)
        gap = 3
        bar_w = max(3, (w - (bar_count - 1) * gap) // bar_count)

        total_w = bar_count * bar_w + (bar_count - 1) * gap
        start_x = (w - total_w) // 2

        for i, level in enumerate(self._levels):
            x = start_x + i * (bar_w + gap)

            # Minimum bar height for idle state
            bar_h = max(4, int(level * (h - 16)))
            y = (h - bar_h) // 2

            # Gradient from accent to lighter shade
            grad = QLinearGradient(x, y, x, y + bar_h)
            color = QColor(self._accent_color)

            if level < 0.05:
                color.setAlpha(50)
                grad.setColorAt(0, color)
                grad.setColorAt(1, color)
            elif level < 0.2:
                color.setAlpha(120)
                lighter = QColor(color)
                lighter.setAlpha(80)
                grad.setColorAt(0, color)
                grad.setColorAt(1, lighter)
            else:
                grad.setColorAt(0, color)
                lighter = QColor(color.lighter(130))
                lighter.setAlpha(200)
                grad.setColorAt(1, lighter)

            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(grad)

            radius = min(bar_w / 2, 3)
            painter.drawRoundedRect(x, y, bar_w, bar_h, radius, radius)

        painter.end()
