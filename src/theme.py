"""Dark/Light Mode Stylesheets für DocLens."""

DARK_THEME = """
QMainWindow, QDialog {
    background-color: #1e1e2e;
    color: #cdd6f4;
}
QTabWidget::pane {
    border: 1px solid #45475a;
    background-color: #1e1e2e;
}
QTabBar::tab {
    background-color: #313244;
    color: #cdd6f4;
    padding: 6px 16px;
    border: 1px solid #45475a;
    border-bottom: none;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
    margin-right: 2px;
}
QTabBar::tab:selected {
    background-color: #1e1e2e;
    border-bottom: 2px solid #89b4fa;
}
QTabBar::tab:hover {
    background-color: #45475a;
}
QToolBar {
    background-color: #181825;
    border-bottom: 1px solid #45475a;
    spacing: 4px;
    padding: 2px;
}
QToolButton {
    background-color: transparent;
    color: #cdd6f4;
    border: 1px solid transparent;
    border-radius: 4px;
    padding: 4px 8px;
    font-size: 13px;
}
QToolButton:hover {
    background-color: #313244;
    border-color: #45475a;
}
QToolButton:pressed {
    background-color: #45475a;
}
QPushButton {
    background-color: #313244;
    color: #cdd6f4;
    border: 1px solid #45475a;
    border-radius: 4px;
    padding: 5px 12px;
    font-size: 13px;
}
QPushButton:hover {
    background-color: #45475a;
}
QPushButton:pressed {
    background-color: #585b70;
}
QPushButton#sendButton {
    background-color: #89b4fa;
    color: #1e1e2e;
    border: none;
    font-weight: bold;
}
QPushButton#sendButton:hover {
    background-color: #74c7ec;
}
QPushButton#templateButton {
    background-color: #313244;
    color: #a6adc8;
    border: 1px solid #45475a;
    padding: 3px 8px;
    font-size: 11px;
}
QPushButton#templateButton:hover {
    background-color: #45475a;
    color: #cdd6f4;
}
QTextEdit, QPlainTextEdit {
    background-color: #181825;
    color: #cdd6f4;
    border: 1px solid #45475a;
    border-radius: 4px;
    padding: 4px;
    font-size: 13px;
}
QLineEdit {
    background-color: #181825;
    color: #cdd6f4;
    border: 1px solid #45475a;
    border-radius: 4px;
    padding: 6px;
    font-size: 13px;
}
QLineEdit:focus, QTextEdit:focus {
    border-color: #89b4fa;
}
QLabel {
    color: #cdd6f4;
}
QLabel#contextLabel {
    color: #a6adc8;
    font-size: 11px;
    padding: 2px 4px;
}
QLabel#statusLabel {
    color: #a6adc8;
    font-size: 12px;
}
QSplitter::handle {
    background-color: #45475a;
    width: 2px;
}
QScrollBar:vertical {
    background-color: #181825;
    width: 10px;
    border: none;
}
QScrollBar::handle:vertical {
    background-color: #45475a;
    border-radius: 5px;
    min-height: 30px;
}
QScrollBar::handle:vertical:hover {
    background-color: #585b70;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
QScrollBar:horizontal {
    background-color: #181825;
    height: 10px;
    border: none;
}
QScrollBar::handle:horizontal {
    background-color: #45475a;
    border-radius: 5px;
    min-width: 30px;
}
QScrollBar::handle:horizontal:hover {
    background-color: #585b70;
}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
}
QMenu {
    background-color: #313244;
    color: #cdd6f4;
    border: 1px solid #45475a;
    padding: 4px;
}
QMenu::item {
    padding: 6px 24px;
    border-radius: 4px;
}
QMenu::item:selected {
    background-color: #45475a;
}
QGraphicsView {
    background-color: #11111b;
    border: none;
}
QSpinBox {
    background-color: #181825;
    color: #cdd6f4;
    border: 1px solid #45475a;
    border-radius: 4px;
    padding: 2px 4px;
}
"""

LIGHT_THEME = """
QMainWindow, QDialog {
    background-color: #eff1f5;
    color: #4c4f69;
}
QTabWidget::pane {
    border: 1px solid #ccd0da;
    background-color: #eff1f5;
}
QTabBar::tab {
    background-color: #e6e9ef;
    color: #4c4f69;
    padding: 6px 16px;
    border: 1px solid #ccd0da;
    border-bottom: none;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
    margin-right: 2px;
}
QTabBar::tab:selected {
    background-color: #eff1f5;
    border-bottom: 2px solid #1e66f5;
}
QTabBar::tab:hover {
    background-color: #ccd0da;
}
QToolBar {
    background-color: #dce0e8;
    border-bottom: 1px solid #ccd0da;
    spacing: 4px;
    padding: 2px;
}
QToolButton {
    background-color: transparent;
    color: #4c4f69;
    border: 1px solid transparent;
    border-radius: 4px;
    padding: 4px 8px;
    font-size: 13px;
}
QToolButton:hover {
    background-color: #ccd0da;
    border-color: #bcc0cc;
}
QToolButton:pressed {
    background-color: #bcc0cc;
}
QPushButton {
    background-color: #e6e9ef;
    color: #4c4f69;
    border: 1px solid #ccd0da;
    border-radius: 4px;
    padding: 5px 12px;
    font-size: 13px;
}
QPushButton:hover {
    background-color: #ccd0da;
}
QPushButton:pressed {
    background-color: #bcc0cc;
}
QPushButton#sendButton {
    background-color: #1e66f5;
    color: #ffffff;
    border: none;
    font-weight: bold;
}
QPushButton#sendButton:hover {
    background-color: #2a6ef6;
}
QPushButton#templateButton {
    background-color: #e6e9ef;
    color: #6c6f85;
    border: 1px solid #ccd0da;
    padding: 3px 8px;
    font-size: 11px;
}
QPushButton#templateButton:hover {
    background-color: #ccd0da;
    color: #4c4f69;
}
QTextEdit, QPlainTextEdit {
    background-color: #ffffff;
    color: #4c4f69;
    border: 1px solid #ccd0da;
    border-radius: 4px;
    padding: 4px;
    font-size: 13px;
}
QLineEdit {
    background-color: #ffffff;
    color: #4c4f69;
    border: 1px solid #ccd0da;
    border-radius: 4px;
    padding: 6px;
    font-size: 13px;
}
QLineEdit:focus, QTextEdit:focus {
    border-color: #1e66f5;
}
QLabel {
    color: #4c4f69;
}
QLabel#contextLabel {
    color: #6c6f85;
    font-size: 11px;
    padding: 2px 4px;
}
QLabel#statusLabel {
    color: #6c6f85;
    font-size: 12px;
}
QSplitter::handle {
    background-color: #ccd0da;
    width: 2px;
}
QScrollBar:vertical {
    background-color: #eff1f5;
    width: 10px;
    border: none;
}
QScrollBar::handle:vertical {
    background-color: #ccd0da;
    border-radius: 5px;
    min-height: 30px;
}
QScrollBar::handle:vertical:hover {
    background-color: #bcc0cc;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
QScrollBar:horizontal {
    background-color: #eff1f5;
    height: 10px;
    border: none;
}
QScrollBar::handle:horizontal {
    background-color: #ccd0da;
    border-radius: 5px;
    min-width: 30px;
}
QScrollBar::handle:horizontal:hover {
    background-color: #bcc0cc;
}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
}
QMenu {
    background-color: #ffffff;
    color: #4c4f69;
    border: 1px solid #ccd0da;
    padding: 4px;
}
QMenu::item {
    padding: 6px 24px;
    border-radius: 4px;
}
QMenu::item:selected {
    background-color: #ccd0da;
}
QGraphicsView {
    background-color: #dce0e8;
    border: none;
}
QSpinBox {
    background-color: #ffffff;
    color: #4c4f69;
    border: 1px solid #ccd0da;
    border-radius: 4px;
    padding: 2px 4px;
}
"""
