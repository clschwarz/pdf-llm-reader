"""DocLens — PDF Reader mit KI-Sidebar."""

import sys

from PySide6.QtWidgets import QApplication

from src.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("DocLens")
    app.setOrganizationName("DocLens")
    app.setStyle("Fusion")

    window = MainWindow()
    window.show()

    # PDF als Argument öffnen
    for arg in sys.argv[1:]:
        if arg.lower().endswith(".pdf"):
            window._open_pdf(arg)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
