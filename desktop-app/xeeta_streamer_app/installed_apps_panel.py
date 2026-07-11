"""Painel arrastável de aplicativos instalados (spec app-launcher-volume-mixer).

Lista os apps de `installed_apps.list_installed_apps()`; arrastar um item
carrega o caminho do app como texto simples no `QMimeData` (`event.mimeData().text()`)
— é isso que os alvos de drop (`KeySlotWidget`, área de "app de volume" do
perfil) esperam. `QListWidget` sozinho não gera MIME `text/plain` ao
arrastar (só o formato interno de item-data), por isso o `startDrag` é
sobrescrito aqui.
"""

from __future__ import annotations

from PyQt6.QtCore import Qt, QMimeData
from PyQt6.QtGui import QDrag
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from . import installed_apps


class _DraggableAppList(QListWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setDragEnabled(True)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setDragDropMode(QAbstractItemView.DragDropMode.DragOnly)

    def startDrag(self, supported_actions) -> None:  # noqa: N802 (nome exigido pelo Qt)
        item = self.currentItem()
        if item is None:
            return

        mime = QMimeData()
        mime.setText(item.data(Qt.ItemDataRole.UserRole))

        drag = QDrag(self)
        drag.setMimeData(mime)
        drag.exec(Qt.DropAction.CopyAction)


class InstalledAppsPanel(QWidget):
    """Lista + botão de atualizar. Arraste um item para uma tecla ou para a
    área de 'app de volume' do perfil."""

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Aplicativos instalados (arraste para uma tecla ou para 'app de volume'):"))

        self._list = _DraggableAppList()
        layout.addWidget(self._list, stretch=1)

        refresh_button = QPushButton("Atualizar lista")
        refresh_button.clicked.connect(self.refresh)
        layout.addWidget(refresh_button)

        self.refresh()

    def refresh(self) -> None:
        self._list.clear()
        for app in installed_apps.list_installed_apps():
            item = QListWidgetItem(app.name)
            item.setData(Qt.ItemDataRole.UserRole, app.path)
            self._list.addItem(item)
