"""OpenAI-kompatibler API-Client mit Streaming für DocLens."""

import json

import httpx
from PySide6.QtCore import QThread, Signal

from src.settings import load_setting


class StreamWorker(QThread):
    """Sendet eine Chat-Anfrage und streamt die Antwort Token für Token."""

    token_received = Signal(str)
    finished_response = Signal()
    error_occurred = Signal(str)

    def __init__(self, messages: list[dict], parent=None):
        super().__init__(parent)
        self.messages = messages
        self._cancelled = False

    def cancel(self):
        self._cancelled = True

    def run(self):
        url = load_setting("api/url")
        key = load_setting("api/key")
        model = load_setting("api/model")
        temperature = load_setting("api/temperature")
        max_tokens = load_setting("api/max_tokens")

        if not url:
            self.error_occurred.emit("Keine API-URL konfiguriert. Bitte unter Einstellungen setzen.")
            return

        endpoint = f"{url.rstrip('/')}/chat/completions"

        headers = {"Content-Type": "application/json"}
        if key:
            headers["Authorization"] = f"Bearer {key}"

        payload = {
            "model": model or "gx10-llm",
            "messages": self.messages,
            "stream": True,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        try:
            with httpx.Client(timeout=120) as client:
                with client.stream("POST", endpoint, json=payload, headers=headers) as response:
                    if response.status_code != 200:
                        body = response.read().decode()
                        self.error_occurred.emit(f"API-Fehler {response.status_code}: {body[:200]}")
                        return

                    for line in response.iter_lines():
                        if self._cancelled:
                            return

                        if not line.startswith("data: "):
                            continue

                        data = line[6:]
                        if data.strip() == "[DONE]":
                            break

                        try:
                            chunk = json.loads(data)
                            delta = chunk["choices"][0].get("delta", {})
                            content = delta.get("content")
                            if content:
                                self.token_received.emit(content)
                        except (json.JSONDecodeError, KeyError, IndexError):
                            continue

        except httpx.ConnectError:
            self.error_occurred.emit(
                f"Verbindung zu {url} fehlgeschlagen.\n"
                "Ist der LLM-Server erreichbar?"
            )
        except httpx.ReadTimeout:
            self.error_occurred.emit("Zeitüberschreitung — der Server antwortet nicht.")
        except Exception as e:
            self.error_occurred.emit(f"Fehler: {e}")
        finally:
            if not self._cancelled:
                self.finished_response.emit()
