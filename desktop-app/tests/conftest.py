"""Fixtures compartilhadas dos testes do app desktop.

`QT_QPA_PLATFORM=offscreen` antes de importar PyQt6 permite rodar os testes
de UI sem uma sessão gráfica real (CI, terminal via SSH, etc.) — precisa ser
setado antes do primeiro import de PyQt6, por isso fica no topo daqui.
"""

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PyQt6.QtWidgets import QApplication


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance() or QApplication([])
    yield app
