"""Settings-Dialog und Persistenz für DocLens."""

from PySide6.QtCore import QSettings
from PySide6.QtWidgets import (
    QDialog, QDialogButtonBox, QFormLayout, QLabel, QLineEdit, QSpinBox,
    QDoubleSpinBox, QVBoxLayout, QGroupBox,
)

DEFAULTS = {
    "api/url": "",
    "api/key": "",
    "api/model": "gx10-llm",
    "api/temperature": 0.7,
    "api/max_tokens": 4096,
    "app/theme": "dark",
}


def get_settings() -> QSettings:
    return QSettings("DocLens", "DocLens")


def load_setting(key: str):
    s = get_settings()
    val = s.value(key)
    if val is None:
        return DEFAULTS.get(key)
    default = DEFAULTS.get(key)
    if isinstance(default, float):
        return float(val)
    if isinstance(default, int):
        return int(val)
    return val


def save_setting(key: str, value):
    s = get_settings()
    s.setValue(key, value)


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Einstellungen")
        self.setMinimumWidth(450)

        layout = QVBoxLayout(self)

        # API-Gruppe
        api_group = QGroupBox("LLM-Verbindung")
        api_layout = QFormLayout()

        self.url_edit = QLineEdit(str(load_setting("api/url")))
        self.url_edit.setPlaceholderText("http://192.168.50.10:8000/v1")
        api_layout.addRow("API-URL:", self.url_edit)

        self.key_edit = QLineEdit(str(load_setting("api/key")))
        self.key_edit.setPlaceholderText("sk-... (leer wenn nicht nötig)")
        self.key_edit.setEchoMode(QLineEdit.EchoMode.Password)
        api_layout.addRow("API-Key:", self.key_edit)

        self.model_edit = QLineEdit(str(load_setting("api/model")))
        self.model_edit.setPlaceholderText("gx10-llm")
        api_layout.addRow("Modell:", self.model_edit)

        self.temp_spin = QDoubleSpinBox()
        self.temp_spin.setRange(0.0, 2.0)
        self.temp_spin.setSingleStep(0.1)
        self.temp_spin.setDecimals(1)
        self.temp_spin.setValue(float(load_setting("api/temperature")))
        api_layout.addRow("Temperature:", self.temp_spin)

        self.max_tokens_spin = QSpinBox()
        self.max_tokens_spin.setRange(256, 131072)
        self.max_tokens_spin.setSingleStep(256)
        self.max_tokens_spin.setValue(int(load_setting("api/max_tokens")))
        api_layout.addRow("Max Tokens:", self.max_tokens_spin)

        api_group.setLayout(api_layout)
        layout.addWidget(api_group)

        # Hinweis
        hint = QLabel(
            "Kompatibel mit: vLLM, Ollama, OpenAI, LM Studio\n"
            "Die API-URL muss auf /v1 enden (z.B. http://host:8000/v1)"
        )
        hint.setObjectName("contextLabel")
        hint.setWordWrap(True)
        layout.addWidget(hint)

        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._save_and_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _save_and_accept(self):
        save_setting("api/url", self.url_edit.text().strip())
        save_setting("api/key", self.key_edit.text().strip())
        save_setting("api/model", self.model_edit.text().strip())
        save_setting("api/temperature", self.temp_spin.value())
        save_setting("api/max_tokens", self.max_tokens_spin.value())
        self.accept()
