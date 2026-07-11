"""Ponto de entrada do app desktop Xeeta Streamer (spec feature-desktop-app-sync)."""

from __future__ import annotations

import sys

from PyQt6.QtWidgets import QApplication

from .main_window import MainWindow


def main() -> int:
    app = QApplication(sys.argv)
    # Necessario para o app continuar rodando em segundo plano (bandeja do
    # sistema) ao fechar a janela principal — spec app-launcher-volume-mixer.
    # Sem isto, o Qt encerraria o processo ao fechar a ultima janela visivel.
    app.setQuitOnLastWindowClosed(False)

    window = MainWindow()
    window.resize(960, 480)
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
