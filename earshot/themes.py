"""Dark and light theme stylesheets for Earshot."""

DARK_THEME = """
QWidget {
    background-color: #1e1e1e;
    color: #e0e0e0;
    font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
    font-size: 13px;
}

QMainWindow {
    background-color: #1e1e1e;
}

QPushButton {
    background-color: #3a3a3a;
    border: 1px solid #4a4a4a;
    border-radius: 6px;
    padding: 8px 16px;
    color: #e0e0e0;
    font-weight: 500;
}

QPushButton:hover {
    background-color: #4a4a4a;
    border-color: #5a5a5a;
}

QPushButton:pressed {
    background-color: #2a2a2a;
}

QPushButton:disabled {
    background-color: #2a2a2a;
    color: #666666;
    border-color: #3a3a3a;
}

QPushButton#recordBtn {
    background-color: #4a9eff;
    border: none;
    color: white;
    font-size: 14px;
    font-weight: 600;
    padding: 12px 24px;
}

QPushButton#recordBtn:hover {
    background-color: #5aafff;
}

QPushButton#recordBtn:pressed {
    background-color: #3a8eef;
}

QPushButton#recordBtn[recording="true"] {
    background-color: #ff4a4a;
}

QPushButton#recordBtn[recording="true"]:hover {
    background-color: #ff5a5a;
}

QPushButton#secondaryBtn {
    background-color: transparent;
    border: 1px solid #4a4a4a;
    padding: 6px 12px;
}

QPushButton#secondaryBtn:hover {
    background-color: #3a3a3a;
}

QLabel {
    color: #e0e0e0;
}

QLabel#timerLabel {
    font-size: 32px;
    font-weight: 300;
    color: #e0e0e0;
}

QLabel#statusLabel {
    font-size: 12px;
    color: #888888;
}

QLabel#historyLabel {
    font-size: 12px;
    color: #aaaaaa;
}

QTextEdit {
    background-color: #2a2a2a;
    border: 1px solid #3a3a3a;
    border-radius: 6px;
    padding: 8px;
    color: #e0e0e0;
    selection-background-color: #4a9eff;
}

QTextEdit:focus {
    border-color: #4a9eff;
}

QScrollBar:vertical {
    background-color: #2a2a2a;
    width: 8px;
    border-radius: 4px;
}

QScrollBar::handle:vertical {
    background-color: #4a4a4a;
    border-radius: 4px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background-color: #5a5a5a;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}

QFrame#separator {
    background-color: #3a3a3a;
    max-height: 1px;
}

QFrame#waveformFrame {
    background-color: #2a2a2a;
    border: 1px solid #3a3a3a;
    border-radius: 6px;
}
"""

LIGHT_THEME = """
QWidget {
    background-color: #f5f5f5;
    color: #1e1e1e;
    font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
    font-size: 13px;
}

QMainWindow {
    background-color: #f5f5f5;
}

QPushButton {
    background-color: #ffffff;
    border: 1px solid #d0d0d0;
    border-radius: 6px;
    padding: 8px 16px;
    color: #1e1e1e;
    font-weight: 500;
}

QPushButton:hover {
    background-color: #f0f0f0;
    border-color: #c0c0c0;
}

QPushButton:pressed {
    background-color: #e0e0e0;
}

QPushButton:disabled {
    background-color: #f0f0f0;
    color: #999999;
    border-color: #e0e0e0;
}

QPushButton#recordBtn {
    background-color: #0066cc;
    border: none;
    color: white;
    font-size: 14px;
    font-weight: 600;
    padding: 12px 24px;
}

QPushButton#recordBtn:hover {
    background-color: #0077dd;
}

QPushButton#recordBtn:pressed {
    background-color: #0055bb;
}

QPushButton#recordBtn[recording="true"] {
    background-color: #cc0000;
}

QPushButton#recordBtn[recording="true"]:hover {
    background-color: #dd0000;
}

QPushButton#secondaryBtn {
    background-color: transparent;
    border: 1px solid #d0d0d0;
    padding: 6px 12px;
}

QPushButton#secondaryBtn:hover {
    background-color: #f0f0f0;
}

QLabel {
    color: #1e1e1e;
}

QLabel#timerLabel {
    font-size: 32px;
    font-weight: 300;
    color: #1e1e1e;
}

QLabel#statusLabel {
    font-size: 12px;
    color: #666666;
}

QLabel#historyLabel {
    font-size: 12px;
    color: #666666;
}

QTextEdit {
    background-color: #ffffff;
    border: 1px solid #d0d0d0;
    border-radius: 6px;
    padding: 8px;
    color: #1e1e1e;
    selection-background-color: #0066cc;
}

QTextEdit:focus {
    border-color: #0066cc;
}

QScrollBar:vertical {
    background-color: #f0f0f0;
    width: 8px;
    border-radius: 4px;
}

QScrollBar::handle:vertical {
    background-color: #c0c0c0;
    border-radius: 4px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background-color: #a0a0a0;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}

QFrame#separator {
    background-color: #d0d0d0;
    max-height: 1px;
}

QFrame#waveformFrame {
    background-color: #ffffff;
    border: 1px solid #d0d0d0;
    border-radius: 6px;
}
"""


def get_theme(name: str) -> str:
    """Get stylesheet for the specified theme."""
    if name == "light":
        return LIGHT_THEME
    return DARK_THEME
