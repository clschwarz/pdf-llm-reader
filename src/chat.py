"""Chat-Sidebar Widget für DocLens."""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLineEdit, QPushButton,
    QLabel, QFileDialog, QScrollArea, QFrame,
)

from src.api_client import StreamWorker
from src.pdf_utils import (
    extract_page_text, extract_all_text, estimate_tokens, build_system_prompt,
)


PROMPT_TEMPLATES = [
    ("Zusammenfassen", "Fasse den folgenden Text kurz und prägnant zusammen."),
    ("Übersetzen → EN", "Übersetze den folgenden Text ins Englische."),
    ("Vereinfachen", "Erkläre den folgenden Text in einfacher Sprache, verständlich für Laien."),
    ("Fachbegriffe", "Liste alle Fachbegriffe im folgenden Text auf und erkläre sie kurz."),
]


class ChatSidebar(QWidget):
    """Chat-Sidebar mit Prompt-Templates und Streaming."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._worker: StreamWorker | None = None
        self._messages: list[dict] = []
        self._current_response = ""
        self._doc = None
        self._current_page = 0
        self._selected_text = ""
        self._context_mode = "page"  # "page", "selection", "full"

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        # Header
        header = QLabel("  Chat")
        header.setStyleSheet("font-weight: bold; font-size: 14px; padding: 6px;")
        layout.addWidget(header)

        # Kontext-Anzeige
        self._context_label = QLabel("Kein PDF geladen")
        self._context_label.setObjectName("contextLabel")
        self._context_label.setWordWrap(True)
        layout.addWidget(self._context_label)

        # Kontext-Buttons
        ctx_bar = QWidget()
        ctx_layout = QHBoxLayout(ctx_bar)
        ctx_layout.setContentsMargins(4, 0, 4, 0)
        ctx_layout.setSpacing(4)

        self._ctx_page_btn = QPushButton("Seite")
        self._ctx_page_btn.setObjectName("templateButton")
        self._ctx_page_btn.setCheckable(True)
        self._ctx_page_btn.setChecked(True)
        self._ctx_page_btn.clicked.connect(lambda: self._set_context_mode("page"))
        ctx_layout.addWidget(self._ctx_page_btn)

        self._ctx_full_btn = QPushButton("Ganzes PDF")
        self._ctx_full_btn.setObjectName("templateButton")
        self._ctx_full_btn.setCheckable(True)
        self._ctx_full_btn.clicked.connect(lambda: self._set_context_mode("full"))
        ctx_layout.addWidget(self._ctx_full_btn)

        self._ctx_sel_btn = QPushButton("Markierung")
        self._ctx_sel_btn.setObjectName("templateButton")
        self._ctx_sel_btn.setCheckable(True)
        self._ctx_sel_btn.setEnabled(False)
        self._ctx_sel_btn.clicked.connect(lambda: self._set_context_mode("selection"))
        ctx_layout.addWidget(self._ctx_sel_btn)

        ctx_layout.addStretch()
        layout.addWidget(ctx_bar)

        # Prompt-Template-Buttons
        tmpl_bar = QWidget()
        tmpl_layout = QHBoxLayout(tmpl_bar)
        tmpl_layout.setContentsMargins(4, 0, 4, 0)
        tmpl_layout.setSpacing(4)

        for label, prompt in PROMPT_TEMPLATES:
            btn = QPushButton(label)
            btn.setObjectName("templateButton")
            btn.clicked.connect(lambda checked, p=prompt: self._send_template(p))
            tmpl_layout.addWidget(btn)

        tmpl_layout.addStretch()
        layout.addWidget(tmpl_bar)

        # Chat-Verlauf
        self._chat_display = QTextEdit()
        self._chat_display.setReadOnly(True)
        self._chat_display.setPlaceholderText(
            "Öffne ein PDF und stelle Fragen zum Inhalt..."
        )
        layout.addWidget(self._chat_display, 1)

        # Eingabezeile
        input_bar = QWidget()
        input_layout = QHBoxLayout(input_bar)
        input_layout.setContentsMargins(4, 4, 4, 4)
        input_layout.setSpacing(4)

        self._input = QLineEdit()
        self._input.setPlaceholderText("Frage zum Dokument stellen...")
        self._input.returnPressed.connect(self._send_message)
        input_layout.addWidget(self._input, 1)

        self._send_btn = QPushButton("Senden")
        self._send_btn.setObjectName("sendButton")
        self._send_btn.clicked.connect(self._send_message)
        input_layout.addWidget(self._send_btn)

        layout.addWidget(input_bar)

        # Export-Button
        export_bar = QWidget()
        export_layout = QHBoxLayout(export_bar)
        export_layout.setContentsMargins(4, 0, 4, 4)

        self._export_btn = QPushButton("Chat exportieren")
        self._export_btn.setObjectName("templateButton")
        self._export_btn.clicked.connect(self._export_chat)
        export_layout.addWidget(self._export_btn)

        self._clear_btn = QPushButton("Chat leeren")
        self._clear_btn.setObjectName("templateButton")
        self._clear_btn.clicked.connect(self._clear_chat)
        export_layout.addWidget(self._clear_btn)

        export_layout.addStretch()
        layout.addWidget(export_bar)

    def set_document(self, doc, page: int = 0):
        self._doc = doc
        self._current_page = page
        self._update_context_label()

    def set_page(self, page: int):
        self._current_page = page
        self._update_context_label()

    def set_selected_text(self, text: str):
        self._selected_text = text
        self._ctx_sel_btn.setEnabled(bool(text))
        if text:
            self._set_context_mode("selection")
            self._update_context_label()

    def send_with_prompt(self, prompt: str, text: str):
        """Sendet einen Prompt mit vorgegebenem Text (z.B. vom Kontextmenü)."""
        self._selected_text = text
        self._set_context_mode("selection")
        self._send_template(prompt)

    def _set_context_mode(self, mode: str):
        self._context_mode = mode
        self._ctx_page_btn.setChecked(mode == "page")
        self._ctx_full_btn.setChecked(mode == "full")
        self._ctx_sel_btn.setChecked(mode == "selection")
        self._update_context_label()

    def _update_context_label(self):
        if not self._doc:
            self._context_label.setText("Kein PDF geladen")
            return

        if self._context_mode == "selection" and self._selected_text:
            preview = self._selected_text[:80].replace("\n", " ")
            self._context_label.setText(f'Kontext: Markierung — "{preview}..."')
        elif self._context_mode == "full":
            tokens = estimate_tokens(extract_all_text(self._doc))
            self._context_label.setText(f"Kontext: Ganzes PDF ({len(self._doc)} Seiten, ~{tokens:,} Tokens)")
        else:
            self._context_label.setText(f"Kontext: Seite {self._current_page + 1}")

    def _get_context_text(self) -> tuple[str, str]:
        """Gibt (context_text, context_label) zurück."""
        if not self._doc:
            return "", "kein Dokument"

        if self._context_mode == "selection" and self._selected_text:
            return self._selected_text, "Markierter Text"
        elif self._context_mode == "full":
            return extract_all_text(self._doc), f"Ganzes PDF, {len(self._doc)} Seiten"
        else:
            text = extract_page_text(self._doc, self._current_page)
            return text, f"Seite {self._current_page + 1}"

    def _send_message(self):
        text = self._input.text().strip()
        if not text:
            return
        self._input.clear()
        self._do_send(text)

    def _send_template(self, prompt: str):
        self._do_send(prompt)

    def _do_send(self, user_text: str):
        if self._worker and self._worker.isRunning():
            return

        context_text, context_label = self._get_context_text()

        if not context_text:
            self._append_system("Kein Text im aktuellen Kontext verfügbar.")
            return

        # Nachricht anzeigen
        self._append_user(user_text)

        # API-Nachrichten aufbauen
        system_msg = {"role": "system", "content": build_system_prompt(context_text, context_label)}
        user_msg = {"role": "user", "content": user_text}

        # Bisherigen Verlauf mitsenden (letzte 10 Nachrichten)
        api_messages = [system_msg] + self._messages[-10:] + [user_msg]

        self._messages.append(user_msg)
        self._current_response = ""
        self._set_input_enabled(False)

        self._worker = StreamWorker(api_messages)
        self._worker.token_received.connect(self._on_token)
        self._worker.finished_response.connect(self._on_finished)
        self._worker.error_occurred.connect(self._on_error)
        self._worker.start()

    def _on_token(self, token: str):
        self._current_response += token
        self._update_assistant_message()

    def _on_finished(self):
        if self._current_response:
            self._messages.append({"role": "assistant", "content": self._current_response})
        self._set_input_enabled(True)
        self._input.setFocus()

    def _on_error(self, error: str):
        self._append_system(f"Fehler: {error}")
        self._set_input_enabled(True)
        self._input.setFocus()

    def _set_input_enabled(self, enabled: bool):
        self._input.setEnabled(enabled)
        self._send_btn.setEnabled(enabled)
        self._send_btn.setText("Senden" if enabled else "...")

    def _append_user(self, text: str):
        self._chat_display.append(
            f'<div style="margin: 8px 0;">'
            f'<b style="color: #89b4fa;">Du:</b><br>'
            f'{_escape_html(text)}</div>'
        )

    def _append_system(self, text: str):
        self._chat_display.append(
            f'<div style="margin: 8px 0; color: #f38ba8;">'
            f'{_escape_html(text)}</div>'
        )

    def _update_assistant_message(self):
        """Aktualisiert die letzte Assistant-Nachricht (Streaming)."""
        cursor = self._chat_display.textCursor()
        html = self._chat_display.toHtml()

        # Marker für streaming-Nachricht
        marker = "<!-- STREAMING -->"
        formatted = _escape_html(self._current_response).replace("\n", "<br>")
        block = (
            f'<div style="margin: 8px 0;">{marker}'
            f'<b style="color: #a6e3a1;">DocLens:</b><br>'
            f'{formatted}</div>'
        )

        if marker in html:
            # Ersetze bestehenden Block
            start = html.index(marker)
            # Finde das umschließende <div>
            div_start = html.rfind("<div", 0, start)
            div_end = html.index("</div>", start) + len("</div>")
            html = html[:div_start] + block + html[div_end:]
            self._chat_display.setHtml(html)
        else:
            self._chat_display.append(block)

        # Zum Ende scrollen
        scrollbar = self._chat_display.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def _clear_chat(self):
        self._chat_display.clear()
        self._messages.clear()
        self._current_response = ""

    def _export_chat(self):
        if not self._messages:
            return

        path, _ = QFileDialog.getSaveFileName(
            self, "Chat exportieren", "chat_export.md", "Markdown (*.md)"
        )
        if not path:
            return

        lines = ["# DocLens Chat-Export\n"]
        for msg in self._messages:
            role = "Du" if msg["role"] == "user" else "DocLens"
            lines.append(f"## {role}\n\n{msg['content']}\n")

        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))


def _escape_html(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )
