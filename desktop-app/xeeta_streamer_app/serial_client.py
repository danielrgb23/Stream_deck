"""Cliente serial do app desktop (spec feature-desktop-app-sync).

Fala o protocolo de `xeeta_streamer_app.protocol` com o firmware via
pyserial. Detecta o device por `PING`/`PONG` (spec serial-protocol),
sem depender de VID/PID de USB.
"""

from __future__ import annotations

import time

import serial
import serial.tools.list_ports

from . import protocol

# Tempo apos abrir a porta para o ESP32 reiniciar (DTR/RTS no open reseta o
# chip) e o firmware terminar o boot antes de responder a comandos.
BOOT_SETTLE_SECONDS = 1.5

DEFAULT_RESPONSE_TIMEOUT = 1.0


class DeviceError(Exception):
    """Erro de comunicacao com o device (timeout, resposta inesperada)."""


class DeviceClient:
    def __init__(self, port: str):
        self.port = port
        self._serial = serial.Serial(port, protocol.BAUD_RATE, timeout=0.1)
        self._parser = protocol.PacketParser()
        time.sleep(BOOT_SETTLE_SECONDS)
        self._serial.reset_input_buffer()

    def close(self) -> None:
        self._serial.close()

    def __enter__(self) -> "DeviceClient":
        return self

    def __exit__(self, *_exc_info) -> None:
        self.close()

    def _send(self, command_id: int, payload: bytes = b"") -> None:
        self._serial.write(protocol.encode_packet(command_id, payload))

    def _read_response(self, expected_command_id: int, timeout: float = DEFAULT_RESPONSE_TIMEOUT) -> protocol.Packet:
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            chunk = self._serial.read(64)
            if not chunk:
                continue
            for packet in self._parser.feed(chunk):
                if packet.command_id == expected_command_id:
                    return packet
        raise DeviceError(f"Sem resposta do device para o comando 0x{expected_command_id:02X}")

    def ping(self, timeout: float = 0.5) -> bool:
        self._send(protocol.CommandId.PING)
        try:
            self._read_response(protocol.CommandId.PONG, timeout=timeout)
            return True
        except DeviceError:
            return False

    def get_version(self) -> tuple[str, int]:
        self._send(protocol.CommandId.GET_VERSION)
        packet = self._read_response(protocol.CommandId.VERSION_INFO)
        major, minor, patch, proto_version = packet.payload[:4]
        return f"{major}.{minor}.{patch}", proto_version

    def get_active_profile(self) -> tuple[int, str]:
        self._send(protocol.CommandId.GET_ACTIVE_PROFILE)
        packet = self._read_response(protocol.CommandId.ACTIVE_PROFILE_INFO)
        profile_id = packet.payload[0]
        name = packet.payload[1:].split(b"\x00", 1)[0].decode("ascii", errors="replace")
        return profile_id, name

    def get_profile(self, profile_id: int) -> protocol.Profile:
        self._send(protocol.CommandId.GET_PROFILE, bytes([profile_id]))
        packet = self._read_response(protocol.CommandId.PROFILE_INFO)
        return protocol.Profile.from_bytes(packet.payload[1:])

    def set_profile(self, profile_id: int, profile: protocol.Profile) -> bool:
        payload = bytes([profile_id]) + profile.to_bytes()
        self._send(protocol.CommandId.SET_PROFILE, payload)
        packet = self._read_response(protocol.CommandId.SET_PROFILE_ACK)
        status = packet.payload[1] if len(packet.payload) > 1 else 1
        return status == 0


def candidate_ports() -> list[str]:
    return [info.device for info in serial.tools.list_ports.comports()]


def find_device(timeout_per_port: float = 1.0) -> str | None:
    """Varre as portas seriais disponiveis e retorna a primeira que responde
    PONG a um PING (spec serial-protocol / feature-desktop-app-sync:
    "detecta o device em até 3 segundos, sem depender de driver adicional").
    """
    for port in candidate_ports():
        try:
            with DeviceClient(port) as client:
                if client.ping(timeout=timeout_per_port):
                    return port
        except (serial.SerialException, OSError):
            continue
    return None
