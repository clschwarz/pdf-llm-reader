"""Hauptfenster für DocLens."""

import os

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (
    QMainWindow, QTabWidget, QSplitter, QWidget, QFileDialog,
    QToolBar, QLabel, QMenu, QMessageBox,
)

from src.viewer import PDFViewer
from src.chat import ChatSidebar
from src.settings import SettingsDialog, load_setting, save_setting
from src.theme import DARK_THEME, LIGHT_THEME


CONTEXT_ACTIONS = [
    ("Erkläre das", "Erkläre den folgenden Text verständlich und ausführlich."),
    ("Zusammenfassen", "Fasse den folgenden Text kurz und prägnant zusammen."),
    ("Übersetzen → EN", "Übersetze den folgenden Text ins Englische."),
    ("Vereinfachen", "Erkläre den folgenden Text in einfacher Sprache."),
    ("Fachbegriffe", "Liste alle Fachbegriffe im folgenden Text auf und erkläre sie kurz."),
]


class DocumentTab(QWidget):
    """Ein Tab mit PDF-Viewer und Chat-Sidebar."""

    def __init__(self, parent=None):
        super().__init__(parent)
        layout_outer = QSplitter(Qt.Orientation.Horizontal, self)

        self.viewer = PDFViewer()
        self.chat = ChatSidebar()

        layout_outer.addWidget(self.viewer)
        layout_outer.addWidget(self.chat)
        layout_outer.setSizes([600, 350])

        # Verbindungen
        self.viewer.page_changed.connect(self.chat.set_page)
        self.viewer.text_selected.connect(self.chat.set_selected_text)
        self.viewer.context_menu_requested.connect(self._show_context_menu)

        from PySide6.QtWidgets import QHBoxLayout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(layout_outer)

    def _show_context_menu(self, text: str, global_pos):
        menu = QMenu(self)
        for label, prompt in CONTEXT_ACTIONS:
            action = menu.addAction(label)
            action.triggered.connect(
                lambda checked, p=prompt, t=text: self.chat.send_with_prompt(p, t)
            )
        menu.exec(global_pos)

    def open_file(self, path: str) -> bool:
        if self.viewer.open_document(path):
            self.chat.set_document(self.viewer.get_document(), 0)
            return True
        return False


class MainWindow(QMainWindow):
    """DocLens Hauptfenster."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("DocLens — PDF Reader mit KI")
        self.setMinimumSize(1000, 700)

        # Tab-Widget
        self._tabs = QTabWidget()
        self._tabs.setTabsClosable(True)
        self._tabs.tabCloseRequested.connect(self._close_tab)
        self._tabs.setDocumentMode(True)
        self.setCentralWidget(self._tabs)

        # Toolbar
        self._create_toolbar()

        # Menübar
        self._create_menubar()

        # Theme laden
        self._apply_theme()

        # Leerer Start-Tab
        self._add_empty_tab()

    def _create_toolbar(self):
        toolbar = QToolBar("Werkzeuge")
        toolbar.setMovable(False)
        toolbar.setIconSize(toolbar.iconSize())
        self.addToolBar(toolbar)

        # PDF öffnen
        open_action = QAction("PDF öffnen", self)
        open_action.setShortcut(QKeySequence("Ctrl+O"))
        open_action.triggered.connect(self._open_file)
        toolbar.addAction(open_action)

        toolbar.addSeparator()

        # Neuer Tab
        new_tab_action = QAction("+ Tab", self)
        new_tab_action.setShortcut(QKeySequence("Ctrl+T"))
        new_tab_action.triggered.connect(self._add_empty_tab)
        toolbar.addAction(new_tab_action)

        toolbar.addSeparator()

        # Theme Toggle
        self._theme_action = QAction("Helles Design", self)
        self._theme_action.triggered.connect(self._toggle_theme)
        toolbar.addAction(self._theme_action)

        # Spacer
        spacer = QWidget()
        spacer.setFixedWidth(20)
        toolbar.addWidget(spacer)

        # Einstellungen
        settings_action = QAction("Einstellungen", self)
        settings_action.setShortcut(QKeySequence("Ctrl+,"))
        settings_action.triggered.connect(self._open_settings)
        toolbar.addAction(settings_action)

    def _create_menubar(self):
        menubar = self.menuBar()

        # Datei
        file_menu = menubar.addMenu("Datei")
        file_menu.addAction("PDF öffnen", self._open_file, QKeySequence("Ctrl+O"))
        file_menu.addAction("Neuer Tab", self._add_empty_tab, QKeySequence("Ctrl+T"))
        file_menu.addAction("Tab schließen", self._close_current_tab, QKeySequence("Ctrl+W"))
        file_menu.addSeparator()
        file_menu.addAction("Beenden", self.close, QKeySequence("Ctrl+Q"))

        # Ansicht
        view_menu = menubar.addMenu("Ansicht")
        view_menu.addAction("Vergrößern", self._zoom_in, QKeySequence("Ctrl++"))
        view_menu.addAction("Verkleinern", self._zoom_out, QKeySequence("Ctrl+-"))
        view_menu.addSeparator()
        view_menu.addAction("Design umschalten", self._toggle_theme)

        # Einstellungen
        menubar.addAction("Einstellungen", self._open_settings)

    def _add_empty_tab(self):
        tab = DocumentTab()
        idx = self._tabs.addTab(tab, "Neues Dokument")
        self._tabs.setCurrentIndex(idx)
        return tab

    def _open_file(self):
        paths, _ = QFileDialog.getOpenFileNames(
            self, "PDF öffnen", "", "PDF-Dateien (*.pdf)"
        )
        for path in paths:
            self._open_pdf(path)

    def _open_pdf(self, path: str):
        # Aktuellen Tab nutzen wenn er leer ist
        current_tab = self._tabs.currentWidget()
        if isinstance(current_tab, DocumentTab) and current_tab.viewer.get_document() is None:
            tab = current_tab
        else:
            tab = self._add_empty_tab()

        if tab.open_file(path):
            name = os.path.basename(path)
            idx = self._tabs.indexOf(tab)
            self._tabs.setTabText(idx, name)
            self._tabs.setTabToolTip(idx, path)
        else:
            QMessageBox.warning(self, "Fehler", f"PDF konnte nicht geöffnet werden:\n{path}")

    def _close_tab(self, index: int):
        if self._tabs.count() > 1:
            self._tabs.removeTab(index)
        else:
            # Letzten Tab nicht schließen, sondern leeren
            tab = self._tabs.widget(0)
            if isinstance(tab, DocumentTab):
                self._tabs.removeTab(0)
                self._add_empty_tab()

    def _close_current_tab(self):
        self._close_tab(self._tabs.currentIndex())

    def _zoom_in(self):
        tab = self._tabs.currentWidget()
        if isinstance(tab, DocumentTab):
            tab.viewer.zoom_in()

    def _zoom_out(self):
        tab = self._tabs.currentWidget()
        if isinstance(tab, DocumentTab):
            tab.viewer.zoom_out()

    def _toggle_theme(self):
        current = load_setting("app/theme")
        new_theme = "light" if current == "dark" else "dark"
        save_setting("app/theme", new_theme)
        self._apply_theme()

    def _apply_theme(self):
        theme = load_setting("app/theme")
        if theme == "light":
            self.setStyleSheet(LIGHT_THEME)
            self._theme_action.setText("Dunkles Design")
        else:
            self.setStyleSheet(DARK_THEME)
            self._theme_action.setText("Helles Design")

    def _open_settings(self):
        dlg = SettingsDialog(self)
        dlg.exec()

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                if url.toLocalFile().lower().endswith(".pdf"):
                    event.acceptProposedAction()
                    return

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            if path.lower().endswith(".pdf"):
                self._open_pdf(path)
