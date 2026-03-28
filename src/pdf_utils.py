"""PDF-Textextraktion für DocLens."""

import fitz  # PyMuPDF


def extract_page_text(doc: fitz.Document, page_num: int) -> str:
    """Extrahiert Text einer einzelnen Seite."""
    if 0 <= page_num < len(doc):
        return doc[page_num].get_text("text").strip()
    return ""


def extract_all_text(doc: fitz.Document) -> str:
    """Extrahiert Text aller Seiten."""
    parts = []
    for i in range(len(doc)):
        text = doc[i].get_text("text").strip()
        if text:
            parts.append(f"--- Seite {i + 1} ---\n{text}")
    return "\n\n".join(parts)


def extract_rect_text(doc: fitz.Document, page_num: int, rect: fitz.Rect) -> str:
    """Extrahiert Text innerhalb eines Rechtecks auf einer Seite."""
    if 0 <= page_num < len(doc):
        page = doc[page_num]
        return page.get_text("text", clip=rect).strip()
    return ""


def estimate_tokens(text: str) -> int:
    """Grobe Token-Schätzung (1 Token ~ 4 Zeichen für Deutsch)."""
    return len(text) // 4


def build_system_prompt(context_text: str, context_label: str) -> str:
    """Baut den System-Prompt mit PDF-Kontext."""
    return (
        f"Du bist ein hilfreicher Dokumenten-Analyst. "
        f"Analysiere den folgenden Text ({context_label}) und beantworte Fragen dazu. "
        f"Antworte auf Deutsch.\n\n"
        f"--- Dokumenttext ---\n{context_text}"
    )
