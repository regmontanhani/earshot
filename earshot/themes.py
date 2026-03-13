"""Earshot theme system.

Design system (UI/UX Pro Max principles):
  Style: Apple HIG-inspired minimalism with OLED-optimized dark mode
  Typography: SF Pro system font, scale 11/12/13/15/40px
  Spacing: 4pt grid (8, 12, 16, 20, 24, 32px)
  Corners: 10-12px cards, 22px primary CTA (pill shape)
  Colors: Apple semantic palette - deep blacks, cool grays, system blue accent
  Accessibility: WCAG AA contrast, visible focus states, 44px min touch targets
  Anti-patterns avoided: emoji as icons, gray-on-gray text, harsh shadows
"""

DARK_THEME = """
/* ── Base ── */
QWidget {
    background-color: #0D0D0D;
    color: #F5F5F7;
    font-family: -apple-system, "SF Pro Display", "Helvetica Neue", sans-serif;
    font-size: 13px;
}

QMainWindow {
    background-color: #0D0D0D;
}

/* ── Buttons ── */
QPushButton {
    background-color: #1C1C1E;
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 10px;
    padding: 10px 18px;
    color: #F5F5F7;
    font-weight: 500;
    font-size: 13px;
    min-height: 20px;
}

QPushButton:hover {
    background-color: #2C2C2E;
    border-color: rgba(255, 255, 255, 0.12);
}

QPushButton:pressed {
    background-color: #161618;
}

QPushButton:disabled {
    background-color: #1C1C1E;
    color: #48484A;
    border-color: rgba(255, 255, 255, 0.04);
}

/* Primary CTA - pill shape, 44px+ touch target */
QPushButton#recordBtn {
    background-color: #0A84FF;
    border: none;
    border-radius: 22px;
    color: white;
    font-size: 15px;
    font-weight: 600;
    padding: 14px 32px;
    min-height: 22px;
    letter-spacing: 0.3px;
}

QPushButton#recordBtn:hover {
    background-color: #409CFF;
}

QPushButton#recordBtn:pressed {
    background-color: #0071E3;
}

QPushButton#recordBtn[recording="true"] {
    background-color: #FF453A;
}

QPushButton#recordBtn[recording="true"]:hover {
    background-color: #FF6961;
}

/* Ghost buttons */
QPushButton#secondaryBtn {
    background-color: transparent;
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 8px;
    padding: 8px 14px;
    font-size: 12px;
    color: #98989D;
}

QPushButton#secondaryBtn:hover {
    background-color: rgba(255, 255, 255, 0.06);
    color: #F5F5F7;
    border-color: rgba(255, 255, 255, 0.16);
}

QPushButton#secondaryBtn:disabled {
    color: #3A3A3C;
    border-color: rgba(255, 255, 255, 0.04);
}

/* ── Labels ── */
QLabel {
    color: #F5F5F7;
    background: transparent;
}

QLabel#timerLabel {
    font-size: 40px;
    font-weight: 200;
    color: #F5F5F7;
    letter-spacing: 2px;
}

QLabel#statusLabel {
    font-size: 11px;
    font-weight: 500;
    color: #636366;
    letter-spacing: 0.5px;
}

QLabel#historyLabel {
    font-size: 12px;
    color: #8E8E93;
    font-weight: 500;
}

/* ── Transcript area ── */
QTextEdit {
    background-color: #1C1C1E;
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 12px;
    padding: 12px;
    color: #F5F5F7;
    font-size: 13px;
    selection-background-color: #0A84FF;
    selection-color: white;
}

QTextEdit:focus {
    border-color: rgba(10, 132, 255, 0.5);
}

/* ── Scrollbar - thin & minimal ── */
QScrollBar:vertical {
    background-color: transparent;
    width: 6px;
    margin: 4px 2px;
}

QScrollBar::handle:vertical {
    background-color: rgba(255, 255, 255, 0.15);
    border-radius: 3px;
    min-height: 24px;
}

QScrollBar::handle:vertical:hover {
    background-color: rgba(255, 255, 255, 0.25);
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}

QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
    background: transparent;
}

/* ── Separators ── */
QFrame#separator {
    background-color: rgba(255, 255, 255, 0.06);
    max-height: 1px;
}

/* ── Waveform card ── */
QFrame#waveformFrame {
    background-color: #1C1C1E;
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 12px;
}

/* ── Settings dialog controls ── */
QGroupBox {
    background-color: #1C1C1E;
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 12px;
    padding: 16px;
    padding-top: 28px;
    margin-top: 8px;
    font-weight: 600;
    font-size: 13px;
    color: #F5F5F7;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 4px 12px;
    color: #F5F5F7;
}

QComboBox {
    background-color: #2C2C2E;
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 8px;
    padding: 6px 12px;
    color: #F5F5F7;
    min-height: 28px;
}

QComboBox:hover {
    border-color: rgba(255, 255, 255, 0.16);
}

QComboBox::drop-down {
    border: none;
    width: 24px;
}

QComboBox QAbstractItemView {
    background-color: #2C2C2E;
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 8px;
    color: #F5F5F7;
    selection-background-color: #0A84FF;
    padding: 4px;
}

QLineEdit {
    background-color: #2C2C2E;
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 8px;
    padding: 6px 12px;
    color: #F5F5F7;
    min-height: 28px;
}

QLineEdit:focus {
    border-color: rgba(10, 132, 255, 0.5);
}

QCheckBox {
    color: #F5F5F7;
    spacing: 8px;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border-radius: 4px;
    border: 1px solid rgba(255, 255, 255, 0.16);
    background-color: #2C2C2E;
}

QCheckBox::indicator:checked {
    background-color: #0A84FF;
    border-color: #0A84FF;
}

QSlider::groove:horizontal {
    height: 4px;
    background: #3A3A3C;
    border-radius: 2px;
}

QSlider::handle:horizontal {
    width: 18px;
    height: 18px;
    margin: -7px 0;
    background: #F5F5F7;
    border-radius: 9px;
}

QSlider::sub-page:horizontal {
    background: #0A84FF;
    border-radius: 2px;
}

QDialog {
    background-color: #0D0D0D;
}
"""

LIGHT_THEME = """
/* ── Base ── */
QWidget {
    background-color: #FFFFFF;
    color: #1D1D1F;
    font-family: -apple-system, "SF Pro Display", "Helvetica Neue", sans-serif;
    font-size: 13px;
}

QMainWindow {
    background-color: #FFFFFF;
}

/* ── Buttons ── */
QPushButton {
    background-color: #F5F5F7;
    border: 1px solid rgba(0, 0, 0, 0.06);
    border-radius: 10px;
    padding: 10px 18px;
    color: #1D1D1F;
    font-weight: 500;
    font-size: 13px;
    min-height: 20px;
}

QPushButton:hover {
    background-color: #E8E8ED;
    border-color: rgba(0, 0, 0, 0.1);
}

QPushButton:pressed {
    background-color: #D1D1D6;
}

QPushButton:disabled {
    background-color: #F5F5F7;
    color: #AEAEB2;
    border-color: rgba(0, 0, 0, 0.04);
}

/* Primary CTA */
QPushButton#recordBtn {
    background-color: #007AFF;
    border: none;
    border-radius: 22px;
    color: white;
    font-size: 15px;
    font-weight: 600;
    padding: 14px 32px;
    min-height: 22px;
    letter-spacing: 0.3px;
}

QPushButton#recordBtn:hover {
    background-color: #0071E3;
}

QPushButton#recordBtn:pressed {
    background-color: #0064D2;
}

QPushButton#recordBtn[recording="true"] {
    background-color: #FF3B30;
}

QPushButton#recordBtn[recording="true"]:hover {
    background-color: #FF453A;
}

/* Ghost buttons */
QPushButton#secondaryBtn {
    background-color: transparent;
    border: 1px solid rgba(0, 0, 0, 0.08);
    border-radius: 8px;
    padding: 8px 14px;
    font-size: 12px;
    color: #86868B;
}

QPushButton#secondaryBtn:hover {
    background-color: rgba(0, 0, 0, 0.03);
    color: #1D1D1F;
    border-color: rgba(0, 0, 0, 0.12);
}

QPushButton#secondaryBtn:disabled {
    color: #C7C7CC;
    border-color: rgba(0, 0, 0, 0.04);
}

/* ── Labels ── */
QLabel {
    color: #1D1D1F;
    background: transparent;
}

QLabel#timerLabel {
    font-size: 40px;
    font-weight: 200;
    color: #1D1D1F;
    letter-spacing: 2px;
}

QLabel#statusLabel {
    font-size: 11px;
    font-weight: 500;
    color: #86868B;
    letter-spacing: 0.5px;
}

QLabel#historyLabel {
    font-size: 12px;
    color: #86868B;
    font-weight: 500;
}

/* ── Transcript area ── */
QTextEdit {
    background-color: #F5F5F7;
    border: 1px solid rgba(0, 0, 0, 0.06);
    border-radius: 12px;
    padding: 12px;
    color: #1D1D1F;
    font-size: 13px;
    selection-background-color: #007AFF;
    selection-color: white;
}

QTextEdit:focus {
    border-color: rgba(0, 122, 255, 0.4);
}

/* ── Scrollbar ── */
QScrollBar:vertical {
    background-color: transparent;
    width: 6px;
    margin: 4px 2px;
}

QScrollBar::handle:vertical {
    background-color: rgba(0, 0, 0, 0.12);
    border-radius: 3px;
    min-height: 24px;
}

QScrollBar::handle:vertical:hover {
    background-color: rgba(0, 0, 0, 0.2);
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}

QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
    background: transparent;
}

/* ── Separators ── */
QFrame#separator {
    background-color: rgba(0, 0, 0, 0.06);
    max-height: 1px;
}

/* ── Waveform card ── */
QFrame#waveformFrame {
    background-color: #F5F5F7;
    border: 1px solid rgba(0, 0, 0, 0.06);
    border-radius: 12px;
}

/* ── Settings dialog controls ── */
QGroupBox {
    background-color: #F5F5F7;
    border: 1px solid rgba(0, 0, 0, 0.06);
    border-radius: 12px;
    padding: 16px;
    padding-top: 28px;
    margin-top: 8px;
    font-weight: 600;
    font-size: 13px;
    color: #1D1D1F;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 4px 12px;
    color: #1D1D1F;
}

QComboBox {
    background-color: #FFFFFF;
    border: 1px solid rgba(0, 0, 0, 0.08);
    border-radius: 8px;
    padding: 6px 12px;
    color: #1D1D1F;
    min-height: 28px;
}

QComboBox:hover {
    border-color: rgba(0, 0, 0, 0.16);
}

QComboBox::drop-down {
    border: none;
    width: 24px;
}

QComboBox QAbstractItemView {
    background-color: #FFFFFF;
    border: 1px solid rgba(0, 0, 0, 0.08);
    border-radius: 8px;
    color: #1D1D1F;
    selection-background-color: #007AFF;
    selection-color: white;
    padding: 4px;
}

QLineEdit {
    background-color: #FFFFFF;
    border: 1px solid rgba(0, 0, 0, 0.08);
    border-radius: 8px;
    padding: 6px 12px;
    color: #1D1D1F;
    min-height: 28px;
}

QLineEdit:focus {
    border-color: rgba(0, 122, 255, 0.4);
}

QCheckBox {
    color: #1D1D1F;
    spacing: 8px;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border-radius: 4px;
    border: 1px solid rgba(0, 0, 0, 0.16);
    background-color: #FFFFFF;
}

QCheckBox::indicator:checked {
    background-color: #007AFF;
    border-color: #007AFF;
}

QSlider::groove:horizontal {
    height: 4px;
    background: #D1D1D6;
    border-radius: 2px;
}

QSlider::handle:horizontal {
    width: 18px;
    height: 18px;
    margin: -7px 0;
    background: #FFFFFF;
    border: 1px solid rgba(0, 0, 0, 0.12);
    border-radius: 9px;
}

QSlider::sub-page:horizontal {
    background: #007AFF;
    border-radius: 2px;
}

QDialog {
    background-color: #FFFFFF;
}
"""


def get_theme(name: str) -> str:
    """Get stylesheet for the specified theme."""
    if name == "light":
        return LIGHT_THEME
    return DARK_THEME
