"""Ponto de entrada do app desktop Xeeta Streamer (spec feature-desktop-app-sync)."""

from __future__ import annotations

import sys

from PyQt6.QtWidgets import QApplication

from .main_window import MainWindow


def main() -> int:
    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(720, 480)
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
