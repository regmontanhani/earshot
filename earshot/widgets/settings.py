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
        self.setMinimumWidth(450)
        self.setModal(True)

    def _setup_ui(self) -> None:
        """Build the settings UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(20, 20, 20, 20)

        # Output section
        output_group = QGroupBox("📁 Output")
        output_layout = QFormLayout(output_group)
        output_layout.setSpacing(10)

        # Output directory
        dir_row = QHBoxLayout()
        self.output_dir_edit = QLineEdit()
        self.output_dir_edit.setReadOnly(True)
        dir_row.addWidget(self.output_dir_edit)

        browse_btn = QPushButton("Browse")
        browse_btn.setFixedWidth(80)
        browse_btn.clicked.connect(self._browse_output_dir)
        dir_row.addWidget(browse_btn)

        output_layout.addRow("Directory:", dir_row)

        # Output formats
        formats_row = QHBoxLayout()
        formats_row.setSpacing(12)

        self.format_json = QCheckBox("JSON")
        self.format_txt = QCheckBox("TXT")
        self.format_srt = QCheckBox("SRT")
        self.format_vtt = QCheckBox("VTT")
        self.format_tsv = QCheckBox("TSV")

        formats_row.addWidget(self.format_json)
        formats_row.addWidget(self.format_txt)
        formats_row.addWidget(self.format_srt)
        formats_row.addWidget(self.format_vtt)
        formats_row.addWidget(self.format_tsv)
        formats_row.addStretch()

        output_layout.addRow("Formats:", formats_row)

        layout.addWidget(output_group)

        # Transcription section
        trans_group = QGroupBox("🎤 Transcription")
        trans_layout = QFormLayout(trans_group)
        trans_layout.setSpacing(10)

        self.model_combo = QComboBox()
        self.model_combo.addItems(["tiny", "base", "small", "medium", "large", "turbo"])
        self.model_combo.setToolTip("Whisper model size. Larger = more accurate but slower.")
        trans_layout.addRow("Model:", self.model_combo)

        layout.addWidget(trans_group)

        # Appearance section
        appearance_group = QGroupBox("🎨 Appearance")
        appearance_layout = QFormLayout(appearance_group)
        appearance_layout.setSpacing(10)

        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["dark", "light"])
        self.theme_combo.currentTextChanged.connect(self._on_theme_changed)
        appearance_layout.addRow("Theme:", self.theme_combo)

        # Opacity slider
        opacity_row = QHBoxLayout()
        self.opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.opacity_slider.setRange(50, 100)
        self.opacity_slider.setTickInterval(10)
        self.opacity_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.opacity_slider.valueChanged.connect(self._on_opacity_changed)
        opacity_row.addWidget(self.opacity_slider)

        self.opacity_label = QLabel("100%")
        self.opacity_label.setFixedWidth(40)
        opacity_row.addWidget(self.opacity_label)

        appearance_layout.addRow("Opacity:", opacity_row)

        self.always_on_top = QCheckBox("Always on top")
        appearance_layout.addRow("", self.always_on_top)

        layout.addWidget(appearance_group)

        # API Keys section
        api_group = QGroupBox("🔑 API Keys")
        api_layout = QFormLayout(api_group)
        api_layout.setSpacing(10)

        api_row = QHBoxLayout()
        self.openai_key_edit = QLineEdit()
        self.openai_key_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.openai_key_edit.setPlaceholderText("sk-...")
        api_row.addWidget(self.openai_key_edit)

        self.show_key_btn = QPushButton("Show")
        self.show_key_btn.setFixedWidth(60)
        self.show_key_btn.setCheckable(True)
        self.show_key_btn.toggled.connect(self._toggle_key_visibility)
        api_row.addWidget(self.show_key_btn)

        api_layout.addRow("OpenAI:", api_row)

        hint_label = QLabel("Leave blank to use local MLX-Whisper")
        hint_label.setObjectName("statusLabel")
        api_layout.addRow("", hint_label)

        layout.addWidget(api_group)

        # Separator
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        layout.addWidget(sep)

        # Buttons
        button_row = QHBoxLayout()
        button_row.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("secondaryBtn")
        cancel_btn.clicked.connect(self.reject)
        button_row.addWidget(cancel_btn)

        save_btn = QPushButton("Save")
        save_btn.setObjectName("recordBtn")
        save_btn.clicked.connect(self._save)
        button_row.addWidget(save_btn)

        layout.addLayout(button_row)

    def _load_values(self) -> None:
        """Load current settings into UI."""
        # Output
        output_dir = self.settings.get("output_dir", "~/Documents/Earshot")
        self.output_dir_edit.setText(str(Path(output_dir).expanduser()))

        formats = self.settings.get("output_formats", ["json", "txt", "srt", "vtt"])
        self.format_json.setChecked("json" in formats)
        self.format_txt.setChecked("txt" in formats)
        self.format_srt.setChecked("srt" in formats)
        self.format_vtt.setChecked("vtt" in formats)
        self.format_tsv.setChecked("tsv" in formats)

        # Transcription
        model = self.settings.get("model", "small")
        index = self.model_combo.findText(model)
        if index >= 0:
            self.model_combo.setCurrentIndex(index)

        # Appearance
        theme = self.settings.get("theme", "dark")
        index = self.theme_combo.findText(theme)
        if index >= 0:
            self.theme_combo.setCurrentIndex(index)

        opacity = int(self.settings.get("opacity", 0.95) * 100)
        self.opacity_slider.setValue(opacity)
        self.opacity_label.setText(f"{opacity}%")

        self.always_on_top.setChecked(self.settings.get("always_on_top", True))

        # API Keys
        api_key = self.settings.get("openai_api_key", "") or ""
        self.openai_key_edit.setText(api_key)

    def _browse_output_dir(self) -> None:
        """Open directory browser."""
        current = self.output_dir_edit.text()
        path = QFileDialog.getExistingDirectory(
            self,
            "Select Output Directory",
            current,
        )
        if path:
            self.output_dir_edit.setText(path)

    def _on_theme_changed(self, theme: str) -> None:
        """Handle theme change - apply immediately."""
        self.on_theme_change(theme)

    def _on_opacity_changed(self, value: int) -> None:
        """Handle opacity slider change."""
        self.opacity_label.setText(f"{value}%")

        # Apply immediately to parent window
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
        # Collect values
        formats = []
        if self.format_json.isChecked():
            formats.append("json")
        if self.format_txt.isChecked():
            formats.append("txt")
        if self.format_srt.isChecked():
            formats.append("srt")
        if self.format_vtt.isChecked():
            formats.append("vtt")
        if self.format_tsv.isChecked():
            formats.append("tsv")

        self.settings["output_dir"] = self.output_dir_edit.text()
        self.settings["output_formats"] = formats
        self.settings["model"] = self.model_combo.currentText()
        self.settings["theme"] = self.theme_combo.currentText()
        self.settings["opacity"] = self.opacity_slider.value() / 100
        self.settings["always_on_top"] = self.always_on_top.isChecked()

        # Handle API key
        api_key = self.openai_key_edit.text().strip()
        if api_key:
            self.settings["openai_api_key"] = api_key
        else:
            self.settings.pop("openai_api_key", None)

        self.on_save(self.settings)
        self.accept()
