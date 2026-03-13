"""Main floating window application for Earshot v2."""

from __future__ import annotations

import subprocess
import sys
import threading
from datetime import datetime
from pathlib import Path

from PySide6.QtCore import Qt, QTimer, Signal, Slot
from PySide6.QtGui import QAction, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMenu,
    QPushButton,
    QSystemTrayIcon,
    QVBoxLayout,
    QWidget,
)

from earshot.audio_capture import AudioCapture
from earshot.config import get_output_dir, load_settings, save_settings
from earshot.diarization import diarize_transcript, is_ollama_available
from earshot.history import HistoryManager
from earshot.output_writer import write_all_formats
from earshot.themes import get_theme
from earshot.transcriber import OpenAITranscriber, Transcriber, get_openai_api_key
from earshot.widgets import TranscriptViewer, WaveformWidget
from earshot.widgets.settings import SettingsDialog


class EarshotWindow(QMainWindow):
    """Main floating window for Earshot."""

    # Signals for thread-safe UI updates
    transcription_complete = Signal(dict)
    transcription_failed = Signal(str)
    status_changed = Signal(str)

    def __init__(self):
        super().__init__()
        self.settings = load_settings()
        self._is_recording = False
        self._recording_start: datetime | None = None
        self._audio_capture: AudioCapture | None = None
        self._current_transcript: dict | None = None

        # Initialize history manager
        self._history = HistoryManager(
            get_output_dir(),
            on_change=self._on_history_changed,
        )
        self._history.scan()

        self._setup_window()
        self._setup_ui()
        self._setup_tray()
        self._setup_timer()
        self._setup_shortcuts()
        self._connect_signals()
        self._apply_theme()
        self._update_history_ui()

        # Start watching for new sessions
        self._history.start_watching()

    def _setup_window(self) -> None:
        """Configure window properties."""
        self.setWindowTitle("Earshot")
        self.setMinimumSize(340, 500)
        self.resize(360, 600)

        # Always on top
        if self.settings.get("always_on_top", True):
            self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)

        # Restore geometry if saved
        geometry = self.settings.get("window_geometry")
        if geometry:
            self.restoreGeometry(bytes.fromhex(geometry))

        # Window opacity
        opacity = self.settings.get("opacity", 0.95)
        self.setWindowOpacity(opacity)

    def _setup_ui(self) -> None:
        """Build the UI layout."""
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # Waveform
        self.waveform = WaveformWidget()
        self.waveform.setObjectName("waveformFrame")
        layout.addWidget(self.waveform)

        # Timer
        self.timer_label = QLabel("00:00")
        self.timer_label.setObjectName("timerLabel")
        self.timer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.timer_label)

        # Status
        self.status_label = QLabel("Ready to record")
        self.status_label.setObjectName("statusLabel")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)

        # Record button
        self.record_btn = QPushButton("⏺  Record")
        self.record_btn.setObjectName("recordBtn")
        self.record_btn.clicked.connect(self._toggle_recording)
        layout.addWidget(self.record_btn)

        # Separator
        sep1 = QFrame()
        sep1.setObjectName("separator")
        sep1.setFrameShape(QFrame.Shape.HLine)
        layout.addWidget(sep1)

        # History navigation
        history_row = QHBoxLayout()
        history_row.setSpacing(8)

        self.prev_btn = QPushButton("◀")
        self.prev_btn.setObjectName("secondaryBtn")
        self.prev_btn.setFixedWidth(40)
        self.prev_btn.setEnabled(False)
        self.prev_btn.setToolTip("Previous session")
        self.prev_btn.clicked.connect(self._go_previous)
        history_row.addWidget(self.prev_btn)

        self.history_label = QLabel("New Session")
        self.history_label.setObjectName("historyLabel")
        self.history_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        history_row.addWidget(self.history_label, 1)

        self.next_btn = QPushButton("▶")
        self.next_btn.setObjectName("secondaryBtn")
        self.next_btn.setFixedWidth(40)
        self.next_btn.setEnabled(False)
        self.next_btn.setToolTip("Next session")
        self.next_btn.clicked.connect(self._go_next)
        history_row.addWidget(self.next_btn)

        layout.addLayout(history_row)

        # Transcript viewer
        self.transcript_view = TranscriptViewer()
        layout.addWidget(self.transcript_view, 1)

        # Separator
        sep2 = QFrame()
        sep2.setObjectName("separator")
        sep2.setFrameShape(QFrame.Shape.HLine)
        layout.addWidget(sep2)

        # Action buttons
        action_row = QHBoxLayout()
        action_row.setSpacing(8)

        self.folder_btn = QPushButton("📁 Open Folder")
        self.folder_btn.setObjectName("secondaryBtn")
        self.folder_btn.clicked.connect(self._open_output_folder)
        action_row.addWidget(self.folder_btn)

        action_row.addStretch()

        self.settings_btn = QPushButton("⚙ Settings")
        self.settings_btn.setObjectName("secondaryBtn")
        self.settings_btn.clicked.connect(self._open_settings)
        action_row.addWidget(self.settings_btn)

        layout.addLayout(action_row)

    def _setup_tray(self) -> None:
        """Set up system tray icon."""
        self.tray = QSystemTrayIcon(self)
        # Use a simple icon (we'll improve this later)
        self.tray.setIcon(self.style().standardIcon(self.style().StandardPixmap.SP_MediaVolume))
        self.tray.setToolTip("Earshot")

        # Tray menu
        tray_menu = QMenu()

        show_action = QAction("Show Earshot", self)
        show_action.triggered.connect(self.show)
        tray_menu.addAction(show_action)

        tray_menu.addSeparator()

        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self._quit)
        tray_menu.addAction(quit_action)

        self.tray.setContextMenu(tray_menu)
        self.tray.activated.connect(self._tray_activated)
        self.tray.show()

    def _setup_timer(self) -> None:
        """Set up recording timer."""
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._update_timer)
        self._timer.setInterval(1000)

    def _connect_signals(self) -> None:
        """Connect signals for thread-safe UI updates."""
        self.transcription_complete.connect(self._on_transcription_complete)
        self.transcription_failed.connect(self._on_transcription_failed)
        self.status_changed.connect(self._on_status_changed)

    def _apply_theme(self) -> None:
        """Apply the current theme."""
        theme = self.settings.get("theme", "dark")
        self.setStyleSheet(get_theme(theme))

        # Update waveform color
        if theme == "light":
            self.waveform.set_accent_color("#0066cc")
        else:
            self.waveform.set_accent_color("#4a9eff")

    # Recording controls

    def _toggle_recording(self) -> None:
        """Start or stop recording."""
        if self._is_recording:
            self._stop_recording()
        else:
            self._start_recording()

    def _start_recording(self) -> None:
        """Start audio recording."""
        self._is_recording = True
        self._recording_start = datetime.now()
        self._current_transcript = None

        # Update UI
        self.record_btn.setText("⏹  Stop")
        self.record_btn.setProperty("recording", True)
        self.record_btn.style().unpolish(self.record_btn)
        self.record_btn.style().polish(self.record_btn)
        self.status_label.setText("Recording...")
        self.timer_label.setText("00:00")
        self.transcript_view.clear()

        # Start waveform animation
        self.waveform.set_recording(True)

        # Start audio capture
        self._audio_capture = AudioCapture(
            on_audio_level=self._on_audio_level,
        )
        self._audio_capture.start()

        # Start timer
        self._timer.start()

    def _stop_recording(self) -> None:
        """Stop recording and start transcription."""
        if not self._is_recording:
            return

        self._is_recording = False
        self._timer.stop()

        # Update UI
        self.record_btn.setText("⏺  Record")
        self.record_btn.setProperty("recording", False)
        self.record_btn.style().unpolish(self.record_btn)
        self.record_btn.style().polish(self.record_btn)
        self.status_label.setText("⏳ Transcribing...")
        self.waveform.set_recording(False)

        # Stop audio capture and get chunks
        if self._audio_capture:
            chunks = self._audio_capture.stop()

            # Transcribe in background
            thread = threading.Thread(
                target=self._transcribe_recording,
                args=(chunks,),
                daemon=True,
            )
            thread.start()

    def _transcribe_recording(self, chunks: list[Path]) -> None:
        """Transcribe recorded audio (runs in background thread)."""
        try:
            # Get transcriber
            api_key = get_openai_api_key()
            if api_key:
                transcriber = OpenAITranscriber(api_key)
            else:
                model = self.settings.get("model", "small")
                transcriber = Transcriber(model)

            # Transcribe
            if len(chunks) == 1:
                transcript = transcriber.transcribe(chunks[0])
            else:
                transcript = transcriber.transcribe_chunks(chunks)

            # Diarization
            self.status_changed.emit("🤖 Identifying speakers...")
            if is_ollama_available():
                transcript = diarize_transcript(transcript)

            # Save files
            self.status_changed.emit("💾 Saving...")
            timestamp = self._recording_start.strftime("%Y-%m-%d_%H-%M-%S")
            base_name = f"meeting_{timestamp}"
            output_dir = get_output_dir()

            write_all_formats(
                transcript,
                output_dir,
                base_name,
                formats=self.settings.get("output_formats", ["json", "txt", "srt", "vtt"]),
            )

            # Signal completion
            self.transcription_complete.emit(transcript)

        except Exception as e:
            self.transcription_failed.emit(str(e))

    def _on_audio_level(self, level: float) -> None:
        """Handle audio level updates from capture."""
        # Push to waveform (called from audio thread, but Qt handles this)
        self.waveform.push_level(level)

    @Slot(dict)
    def _on_transcription_complete(self, transcript: dict) -> None:
        """Handle transcription completion."""
        self._current_transcript = transcript
        self.transcript_view.set_transcript(transcript)
        self.status_label.setText("✅ Transcription complete")

    @Slot(str)
    def _on_transcription_failed(self, error: str) -> None:
        """Handle transcription failure."""
        self.status_label.setText(f"❌ Failed: {error[:50]}")

    @Slot(str)
    def _on_status_changed(self, status: str) -> None:
        """Handle status updates from background thread."""
        self.status_label.setText(status)

    def _update_timer(self) -> None:
        """Update the recording timer display."""
        if not self._recording_start:
            return

        elapsed = datetime.now() - self._recording_start
        minutes = int(elapsed.total_seconds() // 60)
        seconds = int(elapsed.total_seconds() % 60)
        self.timer_label.setText(f"{minutes:02d}:{seconds:02d}")

    # Actions

    def _open_output_folder(self) -> None:
        """Open the output folder in Finder."""
        output_dir = get_output_dir()
        output_dir.mkdir(parents=True, exist_ok=True)
        subprocess.run(["open", str(output_dir)])

    def _open_settings(self) -> None:
        """Open settings dialog."""
        dialog = SettingsDialog(
            settings=self.settings,
            on_save=self._on_settings_saved,
            on_theme_change=self._on_theme_preview,
            parent=self,
        )
        dialog.exec()

    def _on_settings_saved(self, new_settings: dict) -> None:
        """Handle settings saved from dialog."""
        self.settings = new_settings
        save_settings(self.settings)
        self._apply_theme()

        # Update always-on-top
        if self.settings.get("always_on_top", True):
            self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
        else:
            self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowStaysOnTopHint)
        self.show()  # Required after changing window flags

    def _on_theme_preview(self, theme: str) -> None:
        """Preview theme change from settings dialog."""
        self.setStyleSheet(get_theme(theme))
        if theme == "light":
            self.waveform.set_accent_color("#0066cc")
        else:
            self.waveform.set_accent_color("#4a9eff")

    def _setup_shortcuts(self) -> None:
        """Set up keyboard shortcuts."""
        # Space to toggle recording
        record_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Space), self)
        record_shortcut.activated.connect(self._toggle_recording)

        # Cmd+, to open settings
        settings_shortcut = QShortcut(QKeySequence("Ctrl+,"), self)
        settings_shortcut.activated.connect(self._open_settings)

        # Cmd+Q to quit
        quit_shortcut = QShortcut(QKeySequence("Ctrl+Q"), self)
        quit_shortcut.activated.connect(self._quit)

        # Left/Right arrows for history navigation
        prev_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Left), self)
        prev_shortcut.activated.connect(self._go_previous)

        next_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Right), self)
        next_shortcut.activated.connect(self._go_next)

    # History navigation

    def _go_previous(self) -> None:
        """Navigate to previous session."""
        if self._is_recording:
            return
        session = self._history.go_previous()
        if session:
            self._load_session(session)
        self._update_history_ui()

    def _go_next(self) -> None:
        """Navigate to next session."""
        if self._is_recording:
            return
        session = self._history.go_next()
        if session:
            self._load_session(session)
        else:
            # Back to "New Session" mode
            self.transcript_view.clear()
            self.status_label.setText("Ready to record")
            self.timer_label.setText("00:00")
        self._update_history_ui()

    def _load_session(self, session) -> None:
        """Load a session into the transcript viewer."""
        # Find the JSON file
        json_files = [f for f in session.files if f.suffix == ".json"]
        if not json_files:
            return

        import json

        with open(json_files[0]) as f:
            transcript = json.load(f)

        self._current_transcript = transcript
        self.transcript_view.set_transcript(transcript)

        # Update UI
        if session.duration:
            minutes = int(session.duration // 60)
            seconds = int(session.duration % 60)
            self.timer_label.setText(f"{minutes:02d}:{seconds:02d}")
        else:
            self.timer_label.setText("--:--")

        self.status_label.setText(session.display_time)

    def _update_history_ui(self) -> None:
        """Update history navigation UI state."""
        self.prev_btn.setEnabled(self._history.has_previous and not self._is_recording)
        self.next_btn.setEnabled(self._history.has_next and not self._is_recording)
        self.history_label.setText(self._history.get_display_label())

    def _on_history_changed(self) -> None:
        """Handle history change from file watcher."""
        # Called from watchdog thread, so use signal
        QTimer.singleShot(0, self._update_history_ui)

    def _tray_activated(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        """Handle tray icon click."""
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            if self.isVisible():
                self.hide()
            else:
                self.show()
                self.raise_()
                self.activateWindow()

    def _quit(self) -> None:
        """Quit the application."""
        # Save window geometry
        self.settings["window_geometry"] = self.saveGeometry().toHex().data().decode()
        save_settings(self.settings)

        # Stop recording if active
        if self._is_recording and self._audio_capture:
            self._audio_capture.stop()

        # Stop history watcher
        self._history.stop_watching()

        QApplication.quit()

    def closeEvent(self, event) -> None:
        """Handle window close - minimize to tray instead."""
        event.ignore()
        self.hide()


def main():
    """Run the Earshot application."""
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)  # Keep running in tray

    window = EarshotWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
