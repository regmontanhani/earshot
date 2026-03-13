"""Settings dialog for Earshot."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QFileDialog,
    QFormLayout,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QWidget,
)

if TYPE_CHECKING:
    from collections.abc import Callable


class SettingsDialog(QDialog):
    """Settings dialog for Earshot configuration."""

    def __init__(
        self,
        settings: dict,
        on_save: Callable[[dict], None],
        on_theme_change: Callable[[str], None],
        parent: QWidget | None = None,
    ):
        super().__init__(parent)
        self.settings = settings.copy()
        self.on_save = on_save
        self.on_theme_change = on_theme_change

        self._setup_window()
        self._setup_ui()
        self._load_values()

    def _setup_window(self) -> None:
        """Configure dialog properties."""
        self.setWindowTitle("Settings")
        self.setMinimumWidth(420)
        self.setMaximumWidth(500)
        self.setModal(True)

    def _setup_ui(self) -> None:
        """Build the settings UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(24, 24, 24, 24)

        # ── Output ──
        output_group = QGroupBox("Output")
        output_layout = QVBoxLayout(output_group)
        output_layout.setSpacing(12)
        output_layout.setContentsMargins(16, 24, 16, 16)

        # Output directory
        dir_label = QLabel("Save location")
        dir_label.setObjectName("statusLabel")
        output_layout.addWidget(dir_label)

        dir_row = QHBoxLayout()
        dir_row.setSpacing(8)
        self.output_dir_edit = QLineEdit()
        self.output_dir_edit.setReadOnly(True)
        dir_row.addWidget(self.output_dir_edit, 1)

        browse_btn = QPushButton("Browse")
        browse_btn.setObjectName("secondaryBtn")
        browse_btn.setFixedWidth(72)
        browse_btn.clicked.connect(self._browse_output_dir)
        dir_row.addWidget(browse_btn)
        output_layout.addLayout(dir_row)

        # Output formats
        fmt_label = QLabel("Export formats")
        fmt_label.setObjectName("statusLabel")
        output_layout.addWidget(fmt_label)

        formats_row = QHBoxLayout()
        formats_row.setSpacing(16)
        self.format_json = QCheckBox("JSON")
        self.format_txt = QCheckBox("TXT")
        self.format_srt = QCheckBox("SRT")
        formats_row.addWidget(self.format_json)
        formats_row.addWidget(self.format_txt)
        formats_row.addWidget(self.format_srt)
        formats_row.addStretch()
        output_layout.addLayout(formats_row)

        layout.addWidget(output_group)

        # ── Audio & Transcription ──
        trans_group = QGroupBox("Audio & Transcription")
        trans_layout = QVBoxLayout(trans_group)
        trans_layout.setSpacing(12)
        trans_layout.setContentsMargins(16, 24, 16, 16)

        # Audio input device
        device_label = QLabel("Input device")
        device_label.setObjectName("statusLabel")
        trans_layout.addWidget(device_label)

        device_row = QHBoxLayout()
        device_row.setSpacing(8)
        self.audio_device_combo = QComboBox()
        self._populate_audio_devices()
        self.audio_device_combo.setToolTip("Select audio input device for recording")
        device_row.addWidget(self.audio_device_combo, 1)

        refresh_btn = QPushButton("Refresh")
        refresh_btn.setObjectName("secondaryBtn")
        refresh_btn.setFixedWidth(72)
        refresh_btn.clicked.connect(self._refresh_audio_devices)
        device_row.addWidget(refresh_btn)
        trans_layout.addLayout(device_row)

        # Model
        model_label = QLabel("Whisper model")
        model_label.setObjectName("statusLabel")
        trans_layout.addWidget(model_label)

        self.model_combo = QComboBox()
        self.model_combo.addItems(["tiny", "base", "small", "medium", "large-v3", "turbo"])
        self.model_combo.setToolTip(
            "tiny/base: Fast, lower quality\n"
            "small: Good balance (recommended)\n"
            "medium/large-v3: Best quality, slower\n"
            "turbo: Fast + good quality"
        )
        trans_layout.addWidget(self.model_combo)

        local_hint = QLabel("All transcription runs locally on your Mac")
        local_hint.setObjectName("statusLabel")
        trans_layout.addWidget(local_hint)

        layout.addWidget(trans_group)

        # ── Appearance ──
        appearance_group = QGroupBox("Appearance")
        appearance_layout = QVBoxLayout(appearance_group)
        appearance_layout.setSpacing(12)
        appearance_layout.setContentsMargins(16, 24, 16, 16)

        theme_row = QHBoxLayout()
        theme_row.setSpacing(8)
        theme_label = QLabel("Theme")
        theme_label.setFixedWidth(60)
        theme_row.addWidget(theme_label)
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["dark", "light"])
        self.theme_combo.currentTextChanged.connect(self._on_theme_changed)
        theme_row.addWidget(self.theme_combo, 1)
        appearance_layout.addLayout(theme_row)

        opacity_row = QHBoxLayout()
        opacity_row.setSpacing(8)
        opacity_label = QLabel("Opacity")
        opacity_label.setFixedWidth(60)
        opacity_row.addWidget(opacity_label)
        self.opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.opacity_slider.setRange(50, 100)
        self.opacity_slider.valueChanged.connect(self._on_opacity_changed)
        opacity_row.addWidget(self.opacity_slider, 1)
        self.opacity_label = QLabel("100%")
        self.opacity_label.setFixedWidth(36)
        opacity_row.addWidget(self.opacity_label)
        appearance_layout.addLayout(opacity_row)

        self.always_on_top = QCheckBox("Always on top")
        appearance_layout.addWidget(self.always_on_top)

        layout.addWidget(appearance_group)

        # ── API Keys ──
        api_group = QGroupBox("Cloud Transcription (Optional)")
        api_layout = QVBoxLayout(api_group)
        api_layout.setSpacing(12)
        api_layout.setContentsMargins(16, 24, 16, 16)

        api_hint = QLabel("Leave blank to use local faster-whisper (recommended)")
        api_hint.setObjectName("statusLabel")
        api_hint.setWordWrap(True)
        api_layout.addWidget(api_hint)

        api_row = QHBoxLayout()
        api_row.setSpacing(8)
        self.openai_key_edit = QLineEdit()
        self.openai_key_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.openai_key_edit.setPlaceholderText("sk-...")
        api_row.addWidget(self.openai_key_edit, 1)

        self.show_key_btn = QPushButton("Show")
        self.show_key_btn.setObjectName("secondaryBtn")
        self.show_key_btn.setFixedWidth(56)
        self.show_key_btn.setCheckable(True)
        self.show_key_btn.toggled.connect(self._toggle_key_visibility)
        api_row.addWidget(self.show_key_btn)
        api_layout.addLayout(api_row)

        layout.addWidget(api_group)

        # ── Action buttons ──
        layout.addSpacing(4)

        button_row = QHBoxLayout()
        button_row.setSpacing(8)
        button_row.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("secondaryBtn")
        cancel_btn.setFixedWidth(80)
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.clicked.connect(self.reject)
        button_row.addWidget(cancel_btn)

        save_btn = QPushButton("Save")
        save_btn.setObjectName("recordBtn")
        save_btn.setFixedWidth(80)
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        save_btn.clicked.connect(self._save)
        button_row.addWidget(save_btn)

        layout.addLayout(button_row)

    def _load_values(self) -> None:
        """Load current settings into UI."""
        output_dir = self.settings.get("output_dir", "~/Documents/Earshot")
        self.output_dir_edit.setText(str(Path(output_dir).expanduser()))

        formats = self.settings.get("output_formats", ["json", "txt", "srt"])
        self.format_json.setChecked("json" in formats)
        self.format_txt.setChecked("txt" in formats)
        self.format_srt.setChecked("srt" in formats)

        audio_device = self.settings.get("audio_device", "BlackHole 2ch")
        index = self.audio_device_combo.findText(audio_device)
        if index >= 0:
            self.audio_device_combo.setCurrentIndex(index)

        model = self.settings.get("model", "small")
        index = self.model_combo.findText(model)
        if index >= 0:
            self.model_combo.setCurrentIndex(index)

        theme = self.settings.get("theme", "dark")
        index = self.theme_combo.findText(theme)
        if index >= 0:
            self.theme_combo.setCurrentIndex(index)

        opacity = int(self.settings.get("opacity", 0.95) * 100)
        self.opacity_slider.setValue(opacity)
        self.opacity_label.setText(f"{opacity}%")

        self.always_on_top.setChecked(self.settings.get("always_on_top", True))

        api_key = self.settings.get("openai_api_key", "") or ""
        self.openai_key_edit.setText(api_key)

    def _browse_output_dir(self) -> None:
        """Open directory browser."""
        current = self.output_dir_edit.text()
        path = QFileDialog.getExistingDirectory(self, "Select Output Directory", current)
        if path:
            self.output_dir_edit.setText(path)

    def _populate_audio_devices(self) -> None:
        """Populate audio device dropdown."""
        import pyaudio

        self.audio_device_combo.clear()
        pa = pyaudio.PyAudio()

        for i in range(pa.get_device_count()):
            info = pa.get_device_info_by_index(i)
            if info["maxInputChannels"] > 0:
                self.audio_device_combo.addItem(info["name"], i)

        pa.terminate()

    def _refresh_audio_devices(self) -> None:
        """Refresh the audio device list."""
        current = self.audio_device_combo.currentText()
        self._populate_audio_devices()
        index = self.audio_device_combo.findText(current)
        if index >= 0:
            self.audio_device_combo.setCurrentIndex(index)

    def _on_theme_changed(self, theme: str) -> None:
        """Handle theme change - apply immediately."""
        self.on_theme_change(theme)

    def _on_opacity_changed(self, value: int) -> None:
        """Handle opacity slider change."""
        self.opacity_label.setText(f"{value}%")
        if self.parent():
            self.parent().setWindowOpacity(value / 100)

    def _toggle_key_visibility(self, show: bool) -> None:
        """Toggle API key visibility."""
        if show:
            self.openai_key_edit.setEchoMode(QLineEdit.EchoMode.Normal)
            self.show_key_btn.setText("Hide")
        else:
            self.openai_key_edit.setEchoMode(QLineEdit.EchoMode.Password)
            self.show_key_btn.setText("Show")

    def _save(self) -> None:
        """Save settings and close dialog."""
        formats = []
        if self.format_json.isChecked():
            formats.append("json")
        if self.format_txt.isChecked():
            formats.append("txt")
        if self.format_srt.isChecked():
            formats.append("srt")

        self.settings["output_dir"] = self.output_dir_edit.text()
        self.settings["output_formats"] = formats
        self.settings["audio_device"] = self.audio_device_combo.currentText()
        self.settings["model"] = self.model_combo.currentText()
        self.settings["theme"] = self.theme_combo.currentText()
        self.settings["opacity"] = self.opacity_slider.value() / 100
        self.settings["always_on_top"] = self.always_on_top.isChecked()

        api_key = self.openai_key_edit.text().strip()
        if api_key:
            self.settings["openai_api_key"] = api_key
        else:
            self.settings.pop("openai_api_key", None)

        self.on_save(self.settings)

        if hasattr(self.parent(), "_restart_monitoring"):
            self.parent()._restart_monitoring()

        self.accept()
