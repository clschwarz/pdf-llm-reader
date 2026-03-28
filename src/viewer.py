"""PDF-Viewer Widget für DocLens."""

import fitz  # PyMuPDF
from PySide6.QtCore import Qt, Signal, QRectF, QPointF
from PySide6.QtGui import QImage, QPixmap, QPen, QColor, QWheelEvent, QKeyEvent
from PySide6.QtWidgets import (
    QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QGraphicsRectItem,
    QVBoxLayout, QHBoxLayout, QWidget, QLabel, QPushButton, QSpinBox, QMenu,
)


class PDFGraphicsView(QGraphicsView):
    """QGraphicsView mit Zoom via Ctrl+Mausrad und Text-Selektion."""

    zoom_changed = Signal(float)
    text_selected = Signal(str, object)  # (text, fitz.Rect)
    context_menu_requested = Signal(str, object)  # (selected_text, global_pos)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._scene = QGraphicsScene(self)
        self.setScene(self._scene)
        self.setRenderHints(
            self.renderHints()
            | self.renderHints().__class__.Antialiasing
            | self.renderHints().__class__.SmoothPixmapTransform
        )
        self.setDragMode(QGraphicsView.DragMode.NoDrag)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        self._pixmap_item: QGraphicsPixmapItem | None = None
        self._selection_rect: QGraphicsRectItem | None = None
        self._selecting = False
        self._sel_start = QPointF()
        self._sel_end = QPointF()
        self._zoom = 1.0
        self._doc: fitz.Document | None = None
        self._current_page = 0

    def set_document(self, doc: fitz.Document, page: int):
        self._doc = doc
        self._current_page = page

    def display_pixmap(self, pixmap: QPixmap):
        self._scene.clear()
        self._pixmap_item = self._scene.addPixmap(pixmap)
        self._selection_rect = None
        self.setSceneRect(QRectF(pixmap.rect()))

    def wheelEvent(self, event: QWheelEvent):
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            delta = event.angleDelta().y()
            factor = 1.15 if delta > 0 else 1 / 1.15
            self._zoom *= factor
            self._zoom = max(0.25, min(5.0, self._zoom))
            self.setTransform(self.transform().scale(factor, factor) if False else
                              self.transform().__class__())
            self.resetTransform()
            self.scale(self._zoom, self._zoom)
            self.zoom_changed.emit(self._zoom)
            event.accept()
        else:
            super().wheelEvent(event)

    def set_zoom(self, zoom: float):
        self._zoom = max(0.25, min(5.0, zoom))
        self.resetTransform()
        self.scale(self._zoom, self._zoom)
        self.zoom_changed.emit(self._zoom)

    def get_zoom(self) -> float:
        return self._zoom

    # --- Text-Selektion via Maus-Drag ---

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self._pixmap_item:
            self._selecting = True
            self._sel_start = self.mapToScene(event.pos())
            self._sel_end = self._sel_start
            self._clear_selection_rect()
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._selecting:
            self._sel_end = self.mapToScene(event.pos())
            self._draw_selection_rect()
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self._selecting:
            self._selecting = False
            self._sel_end = self.mapToScene(event.pos())

            # Nur auslösen wenn tatsächlich ein Bereich markiert wurde
            rect = self._get_selection_rect()
            if rect.width() > 5 and rect.height() > 5:
                text = self._extract_selected_text(rect)
                if text:
                    self.text_selected.emit(text, rect)
            event.accept()
        else:
            super().mouseReleaseEvent(event)

    def contextMenuEvent(self, event):
        """Rechtsklick-Menü für markierten Text."""
        rect = self._get_selection_rect()
        if rect.width() > 5 and rect.height() > 5:
            text = self._extract_selected_text(rect)
            if text:
                self.context_menu_requested.emit(text, event.globalPos())
                event.accept()
                return
        super().contextMenuEvent(event)

    def _get_selection_rect(self) -> QRectF:
        x1, y1 = self._sel_start.x(), self._sel_start.y()
        x2, y2 = self._sel_end.x(), self._sel_end.y()
        return QRectF(min(x1, x2), min(y1, y2), abs(x2 - x1), abs(y2 - y1))

    def _draw_selection_rect(self):
        self._clear_selection_rect()
        rect = self._get_selection_rect()
        pen = QPen(QColor(137, 180, 250, 200), 1.5)
        brush = QColor(137, 180, 250, 40)
        self._selection_rect = self._scene.addRect(rect, pen, brush)

    def _clear_selection_rect(self):
        if self._selection_rect:
            self._scene.removeItem(self._selection_rect)
            self._selection_rect = None

    def _extract_selected_text(self, scene_rect: QRectF) -> str:
        """Konvertiert Scene-Koordinaten in PDF-Koordinaten und extrahiert Text."""
        if not self._doc or not self._pixmap_item:
            return ""

        pixmap = self._pixmap_item.pixmap()
        if pixmap.isNull():
            return ""

        page = self._doc[self._current_page]
        page_rect = page.rect

        # Skalierungsfaktor: Pixmap → PDF-Koordinaten
        sx = page_rect.width / pixmap.width()
        sy = page_rect.height / pixmap.height()

        pdf_rect = fitz.Rect(
            scene_rect.x() * sx,
            scene_rect.y() * sy,
            (scene_rect.x() + scene_rect.width()) * sx,
            (scene_rect.y() + scene_rect.height()) * sy,
        )

        return page.get_text("text", clip=pdf_rect).strip()


class PDFViewer(QWidget):
    """Kompletter PDF-Viewer mit Navigation und Zoom."""

    page_changed = Signal(int)
    text_selected = Signal(str)
    context_menu_requested = Signal(str, object)  # (text, global_pos)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._doc: fitz.Document | None = None
        self._current_page = 0
        self._dpi = 150

        # Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Graphics View
        self._view = PDFGraphicsView()
        self._view.text_selected.connect(self._on_text_selected)
        self._view.context_menu_requested.connect(self.context_menu_requested)
        self._view.zoom_changed.connect(self._on_zoom_changed)
        layout.addWidget(self._view, 1)

        # Navigation Bar
        nav_bar = QWidget()
        nav_layout = QHBoxLayout(nav_bar)
        nav_layout.setContentsMargins(8, 4, 8, 4)

        self._prev_btn = QPushButton("◀")
        self._prev_btn.setFixedWidth(32)
        self._prev_btn.clicked.connect(self.prev_page)
        nav_layout.addWidget(self._prev_btn)

        self._page_spin = QSpinBox()
        self._page_spin.setMinimum(1)
        self._page_spin.setFixedWidth(60)
        self._page_spin.valueChanged.connect(self._on_page_spin_changed)
        nav_layout.addWidget(self._page_spin)

        self._page_label = QLabel("/ 0")
        self._page_label.setObjectName("statusLabel")
        nav_layout.addWidget(self._page_label)

        self._next_btn = QPushButton("▶")
        self._next_btn.setFixedWidth(32)
        self._next_btn.clicked.connect(self.next_page)
        nav_layout.addWidget(self._next_btn)

        nav_layout.addStretch()

        self._zoom_out_btn = QPushButton("−")
        self._zoom_out_btn.setFixedWidth(32)
        self._zoom_out_btn.clicked.connect(self.zoom_out)
        nav_layout.addWidget(self._zoom_out_btn)

        self._zoom_label = QLabel("100%")
        self._zoom_label.setObjectName("statusLabel")
        self._zoom_label.setFixedWidth(48)
        self._zoom_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        nav_layout.addWidget(self._zoom_label)

        self._zoom_in_btn = QPushButton("+")
        self._zoom_in_btn.setFixedWidth(32)
        self._zoom_in_btn.clicked.connect(self.zoom_in)
        nav_layout.addWidget(self._zoom_in_btn)

        layout.addWidget(nav_bar)
        self._update_nav_state()

    def open_document(self, path: str) -> bool:
        """Öffnet ein PDF-Dokument. Gibt True bei Erfolg zurück."""
        try:
            self._doc = fitz.open(path)
            self._current_page = 0
            self._page_spin.setMaximum(len(self._doc))
            self._page_label.setText(f"/ {len(self._doc)}")
            self._render_page()
            self._update_nav_state()
            return True
        except Exception:
            self._doc = None
            return False

    def get_document(self) -> fitz.Document | None:
        return self._doc

    def get_current_page(self) -> int:
        return self._current_page

    def get_page_count(self) -> int:
        return len(self._doc) if self._doc else 0

    def _render_page(self):
        if not self._doc:
            return
        page = self._doc[self._current_page]
        mat = fitz.Matrix(self._dpi / 72, self._dpi / 72)
        pix = page.get_pixmap(matrix=mat)

        img = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(img)
        self._view.display_pixmap(pixmap)
        self._view.set_document(self._doc, self._current_page)

        self._page_spin.blockSignals(True)
        self._page_spin.setValue(self._current_page + 1)
        self._page_spin.blockSignals(False)
        self.page_changed.emit(self._current_page)

    def _update_nav_state(self):
        has_doc = self._doc is not None
        page_count = len(self._doc) if has_doc else 0
        self._prev_btn.setEnabled(has_doc and self._current_page > 0)
        self._next_btn.setEnabled(has_doc and self._current_page < page_count - 1)
        self._page_spin.setEnabled(has_doc)
        self._zoom_in_btn.setEnabled(has_doc)
        self._zoom_out_btn.setEnabled(has_doc)

    def prev_page(self):
        if self._doc and self._current_page > 0:
            self._current_page -= 1
            self._render_page()
            self._update_nav_state()

    def next_page(self):
        if self._doc and self._current_page < len(self._doc) - 1:
            self._current_page += 1
            self._render_page()
            self._update_nav_state()

    def _on_page_spin_changed(self, value: int):
        if self._doc and 1 <= value <= len(self._doc):
            self._current_page = value - 1
            self._render_page()
            self._update_nav_state()

    def zoom_in(self):
        self._view.set_zoom(self._view.get_zoom() * 1.2)

    def zoom_out(self):
        self._view.set_zoom(self._view.get_zoom() / 1.2)

    def _on_zoom_changed(self, zoom: float):
        self._zoom_label.setText(f"{int(zoom * 100)}%")

    def _on_text_selected(self, text: str, rect):
        self.text_selected.emit(text)
