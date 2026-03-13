"""Widgets package for Earshot UI components."""

from earshot.widgets.settings import SettingsDialog
from earshot.widgets.transcript import TranscriptViewer
from earshot.widgets.waveform import WaveformWidget

__all__ = ["WaveformWidget", "TranscriptViewer", "SettingsDialog"]
