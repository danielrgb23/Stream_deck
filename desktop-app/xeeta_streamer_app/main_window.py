"""Janela principal do app desktop (specs feature-desktop-app-sync, app-launcher-volume-mixer).

Painel de conexão + seletor de perfil + editor de mapeamento + importação de
preset (spec feature-software-presets). Toda I/O serial roda em
`DeviceWorker`, numa thread separada — este módulo só reage a sinais.

Fica residente na bandeja do sistema (spec app-launcher-volume-mixer):
fechar a janela principal só esconde, não encerra o processo nem derruba a
conexão com o device — só "Sair" no menu da bandeja encerra de verdade.
"""

from __future__ import annotations

from PyQt6.QtCore import QThread, QTimer, Qt, pyqtSignal
from PyQt6.QtGui import QColor, QIcon, QPainter, QPixmap
from PyQt6.QtWidgets import (
    QApplication,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMenu,
    QPushButton,
    QSystemTrayIcon,
    QVBoxLayout,
    QWidget,
)

from . import presets, profile_store, protocol
from .device_worker import DeviceWorker
from .editor_widget import ProfileEditorWidget
from .installed_apps_panel import InstalledAppsPanel

# Intervalo de polling do perfil ativo (GET_ACTIVE_PROFILE, comando já
# existente — spec profile-core) enquanto conectado. Não há canal de eventos
# em tempo real do firmware (decisão registrada em design.md de
# app-launcher-volume-mixer), então isto é como o app sabe qual
# app_path/volume_mixer_app vale agora.
_ACTIVE_PROFILE_POLL_INTERVAL_MS = 1000


def _build_tray_icon() -> QIcon:
    """Ícone simples gerado em runtime — sem depender de um arquivo de
    asset externo no repositório."""
    pixmap = QPixmap(32, 32)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setBrush(QColor("#4a7dff"))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawEllipse(2, 2, 28, 28)
    painter.end()
    return QIcon(pixmap)


class MainWindow(QMainWindow):
    request_connect = pyqtSignal()
    request_load_profile = pyqtSignal(int)
    request_save_profile = pyqtSignal(int, object)
    request_active_profile = pyqtSignal()

    def __init__(self, local_store: profile_store.ProfileFile | None = None):
        super().__init__()
        self.setWindowTitle("Xeeta Streamer")

        self._local_store = local_store or profile_store.ProfileFile()
        self._local_store.load()
        self._current_profile_id = 0
        self._connected = False
        # Perfil ativo conhecido no device, atualizado por polling periódico
        # (ver _active_profile_timer abaixo) — é o que o listener de atalho
        # global (spec app-launcher-volume-mixer) usa para saber qual
        # app_path/volume_mixer_app vale agora.
        self.known_active_profile_id = 0

        self._worker_thread = QThread(self)
        self._worker = DeviceWorker()
        self._worker.moveToThread(self._worker_thread)
        self._worker_thread.start()

        self.request_connect.connect(self._worker.connect_to_device)
        self.request_load_profile.connect(self._worker.load_profile)
        self.request_save_profile.connect(self._worker.save_profile)
        self.request_active_profile.connect(self._worker.load_active_profile)
        self._worker.connected.connect(self._on_connected)
        self._worker.connection_failed.connect(self._on_connection_failed)
        self._worker.profile_loaded.connect(self._on_profile_loaded)
        self._worker.profile_saved.connect(self._on_profile_saved)
        self._worker.active_profile_loaded.connect(self._on_active_profile_loaded)
        self._worker.error.connect(self._on_error)

        self._active_profile_timer = QTimer(self)
        self._active_profile_timer.setInterval(_ACTIVE_PROFILE_POLL_INTERVAL_MS)
        self._active_profile_timer.timeout.connect(self.request_active_profile.emit)

        self._build_ui()
        self._build_tray_icon()
        self._editor.set_profile(self._local_store.get(self._current_profile_id))

    def _build_ui(self) -> None:
        central = QWidget()
        layout = QVBoxLayout(central)

        top_row = QHBoxLayout()
        self._status_label = QLabel("Desconectado")
        top_row.addWidget(self._status_label, stretch=1)
        self._connect_button = QPushButton("Conectar")
        self._connect_button.clicked.connect(self._handle_connect_clicked)
        top_row.addWidget(self._connect_button)
        layout.addLayout(top_row)

        profile_row = QHBoxLayout()
        profile_row.addWidget(QLabel("Perfil:"))
        self._profile_combo = QComboBox()
        self._profile_combo.addItems([str(i) for i in range(protocol.MAX_PROFILES)])
        self._profile_combo.currentIndexChanged.connect(self._handle_profile_changed)
        profile_row.addWidget(self._profile_combo)

        self._load_button = QPushButton("Carregar do device")
        self._load_button.clicked.connect(self._handle_load_clicked)
        profile_row.addWidget(self._load_button)

        self._preset_combo = QComboBox()
        self._preset_combo.addItem("Importar preset...")
        self._presets = presets.list_presets()
        for preset in self._presets:
            self._preset_combo.addItem(f"{preset.name} ({preset.target_software})")
        self._preset_combo.currentIndexChanged.connect(self._handle_preset_selected)
        profile_row.addWidget(self._preset_combo)

        layout.addLayout(profile_row)

        editor_row = QHBoxLayout()
        self._editor = ProfileEditorWidget()
        editor_row.addWidget(self._editor, stretch=3)
        self._apps_panel = InstalledAppsPanel()
        editor_row.addWidget(self._apps_panel, stretch=1)
        layout.addLayout(editor_row)

        save_row = QHBoxLayout()
        self._save_button = QPushButton("Salvar (device + local)")
        self._save_button.clicked.connect(self._handle_save_clicked)
        save_row.addWidget(self._save_button)
        layout.addLayout(save_row)

        self.setCentralWidget(central)

    def _build_tray_icon(self) -> None:
        self._tray_icon = QSystemTrayIcon(_build_tray_icon(), self)
        self._tray_icon.setToolTip("Xeeta Streamer")

        menu = QMenu()
        open_action = menu.addAction("Abrir")
        open_action.triggered.connect(self._show_from_tray)
        menu.addSeparator()
        quit_action = menu.addAction("Sair")
        quit_action.triggered.connect(self._quit_application)
        self._tray_icon.setContextMenu(menu)

        self._tray_icon.activated.connect(self._handle_tray_activated)
        self._tray_icon.show()

    def _handle_tray_activated(self, reason) -> None:
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self._show_from_tray()

    def _show_from_tray(self) -> None:
        self.show()
        self.raise_()
        self.activateWindow()

    def _quit_application(self) -> None:
        self._active_profile_timer.stop()
        self._worker_thread.quit()
        self._worker_thread.wait()
        self._tray_icon.hide()
        QApplication.instance().quit()

    def closeEvent(self, event) -> None:  # noqa: N802 (nome exigido pelo Qt)
        # Fechar a janela (botão de fechar/Cmd+W) esconde em vez de encerrar
        # o processo — o app continua residente na bandeja, mantendo a
        # conexão com o device (spec app-launcher-volume-mixer). Só "Sair"
        # no menu da bandeja encerra de verdade (_quit_application).
        event.ignore()
        self.hide()

    def _handle_connect_clicked(self) -> None:
        self._status_label.setText("Conectando...")
        self._connect_button.setEnabled(False)
        self.request_connect.emit()

    def _on_connected(self, port: str, fw_version: str, proto_version: int) -> None:
        self._connected = True
        self._connect_button.setEnabled(True)
        self._connect_button.setText("Reconectar")
        self._status_label.setText(f"Conectado em {port} (fw v{fw_version}, protocolo v{proto_version})")
        self._active_profile_timer.start()

    def _on_connection_failed(self, message: str) -> None:
        self._connected = False
        self._connect_button.setEnabled(True)
        self._status_label.setText(f"Falha ao conectar: {message}")
        self._active_profile_timer.stop()

    def _on_active_profile_loaded(self, profile_id: int, _name: str) -> None:
        self.known_active_profile_id = profile_id

    def _handle_profile_changed(self, index: int) -> None:
        self._current_profile_id = index
        self._editor.set_profile(self._local_store.get(index))

    def _handle_load_clicked(self) -> None:
        if not self._connected:
            self._status_label.setText("Conecte a um device antes de carregar.")
            return
        self.request_load_profile.emit(self._current_profile_id)

    def _on_profile_loaded(self, profile_id: int, profile: protocol.Profile) -> None:
        self._local_store.set(profile_id, profile)
        self._local_store.save()
        if profile_id == self._current_profile_id:
            self._editor.set_profile(profile)
        self._status_label.setText(f"Perfil {profile_id} carregado do device.")

    def _handle_save_clicked(self) -> None:
        profile = self._editor.get_profile()
        self._local_store.set(self._current_profile_id, profile)
        self._local_store.save()

        if not self._connected:
            self._status_label.setText("Salvo localmente (sem device conectado).")
            return
        self.request_save_profile.emit(self._current_profile_id, profile)

    def _on_profile_saved(self, profile_id: int, ok: bool) -> None:
        if ok:
            self._status_label.setText(f"Perfil {profile_id} salvo no device e localmente.")
        else:
            self._status_label.setText(f"Falha ao salvar perfil {profile_id} no device (salvo só localmente).")

    def _on_error(self, message: str) -> None:
        self._status_label.setText(f"Erro: {message}")

    def _handle_preset_selected(self, index: int) -> None:
        if index == 0:
            return
        preset = self._presets[index - 1]
        self._editor.set_profile(preset.to_profile())
        self._preset_combo.setCurrentIndex(0)
