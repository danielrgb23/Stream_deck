"""Worker de comunicacao serial rodando em thread separada.

pyserial e sincrono/bloqueante (inclusive o delay de boot do ESP32 apos abrir
a porta) — rodar isso na thread da UI travaria o PyQt6 a cada operacao.
`MainWindow` conversa com este worker so por sinais/slots.
"""

from __future__ import annotations

from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot

from . import protocol, serial_client


class DeviceWorker(QObject):
    connected = pyqtSignal(str, str, int)  # port, fw_version, protocol_version
    connection_failed = pyqtSignal(str)
    disconnected = pyqtSignal()
    profile_loaded = pyqtSignal(int, object)  # profile_id, protocol.Profile
    profile_saved = pyqtSignal(int, bool)
    active_profile_loaded = pyqtSignal(int, str)
    error = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self._client: serial_client.DeviceClient | None = None

    @pyqtSlot()
    def connect_to_device(self) -> None:
        port = serial_client.find_device()
        if port is None:
            self.connection_failed.emit("Nenhum device encontrado nas portas seriais disponíveis.")
            return

        try:
            self._client = serial_client.DeviceClient(port)
            fw_version, proto_version = self._client.get_version()
        except serial_client.DeviceError as exc:
            self.connection_failed.emit(str(exc))
            return

        self.connected.emit(port, fw_version, proto_version)

    @pyqtSlot()
    def disconnect_from_device(self) -> None:
        if self._client is not None:
            self._client.close()
            self._client = None
        self.disconnected.emit()

    @pyqtSlot()
    def load_active_profile(self) -> None:
        if self._client is None:
            self.error.emit("Não conectado a nenhum device.")
            return
        try:
            profile_id, name = self._client.get_active_profile()
            self.active_profile_loaded.emit(profile_id, name)
        except serial_client.DeviceError as exc:
            self.error.emit(str(exc))

    @pyqtSlot(int)
    def load_profile(self, profile_id: int) -> None:
        if self._client is None:
            self.error.emit("Não conectado a nenhum device.")
            return
        try:
            profile = self._client.get_profile(profile_id)
            self.profile_loaded.emit(profile_id, profile)
        except serial_client.DeviceError as exc:
            self.error.emit(str(exc))

    @pyqtSlot(int, object)
    def save_profile(self, profile_id: int, profile: protocol.Profile) -> None:
        if self._client is None:
            self.error.emit("Não conectado a nenhum device.")
            return
        try:
            ok = self._client.set_profile(profile_id, profile)
            self.profile_saved.emit(profile_id, ok)
        except serial_client.DeviceError as exc:
            self.error.emit(str(exc))
