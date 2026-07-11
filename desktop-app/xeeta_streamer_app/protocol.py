"""Envelope do protocolo serial do firmware (spec serial-protocol).

Espelha byte a byte ``src/core/SerialProtocol.h`` — qualquer mudança lá
(novo comando, novo campo) precisa ser refletida aqui. Não reimplementa a
lógica do firmware, só o formato de wire.
"""

from __future__ import annotations

import struct
from dataclasses import dataclass

PROTOCOL_VERSION = 1
BAUD_RATE = 115200

MAX_PROFILES = 8
MAX_KEYS_PER_PROFILE = 8
PROFILE_NAME_LENGTH = 16
PROFILE_SCHEMA_VERSION = 1

# struct Profile (src/core/Profile.h): schema_version(1) + name(16) + keys(8 * 2)
PROFILE_STRUCT_SIZE = 1 + PROFILE_NAME_LENGTH + MAX_KEYS_PER_PROFILE * 2

MOD_NONE = 0x00
MOD_CTRL = 0x01
MOD_SHIFT = 0x02
MOD_ALT = 0x04
MOD_GUI = 0x08

# Sistema operacional alvo de um perfil (spec target-os-shortcuts). Vive só
# no lado do app (JSON local) — nunca é enviado ao firmware, que só recebe
# modifiers/keycode ja resolvidos via Profile.to_bytes().
TARGET_OS_WINDOWS = "WINDOWS"
TARGET_OS_MAC = "MAC"
TARGET_OS_CHOICES = [TARGET_OS_WINDOWS, TARGET_OS_MAC]
DEFAULT_TARGET_OS = TARGET_OS_WINDOWS

# Combos HID reservados (spec app-launcher-volume-mixer) — sinalizam "abrir
# app"/"ajustar volume" ao app residente via atalho global do SO. Precisam
# bater exatamente com o firmware (src/core/ReservedVolumeCombo.h para os de
# volume; os de tecla são só um valor de modifiers/keycode como outro
# qualquer, gravados via SET_PROFILE normalmente).
RESERVED_ACTION_MODIFIERS = MOD_CTRL | MOD_ALT | MOD_SHIFT

# Um combo por posição de tecla física (F13..F20), na mesma ordem de
# MAX_KEYS_PER_PROFILE — ver keycodes.py (F13 = 0xF0, F14 = 0xF1, ...).
RESERVED_KEY_TRIGGER_KEYCODES = [0xF0 + i for i in range(MAX_KEYS_PER_PROFILE)]

# Fixos — emitidos pelo firmware na rotação do encoder, não fazem parte do
# array keys[] de nenhum perfil (ver ReservedVolumeCombo.h).
RESERVED_VOLUME_UP_KEYCODE = 0xF8  # F21
RESERVED_VOLUME_DOWN_KEYCODE = 0xF9  # F22

MODIFIER_NAMES = {
    MOD_CTRL: "CTRL",
    MOD_SHIFT: "SHIFT",
    MOD_ALT: "ALT",
    MOD_GUI: "GUI",
}
NAME_TO_MODIFIER = {name: bit for bit, name in MODIFIER_NAMES.items()}


class CommandId:
    PING = 0x01
    PONG = 0x02
    GET_VERSION = 0x03
    VERSION_INFO = 0x04
    GET_ACTIVE_PROFILE = 0x05
    ACTIVE_PROFILE_INFO = 0x06
    GET_PROFILE = 0x10
    PROFILE_INFO = 0x11
    SET_PROFILE = 0x12
    SET_PROFILE_ACK = 0x13


def encode_packet(command_id: int, payload: bytes = b"") -> bytes:
    header = struct.pack("<BBH", PROTOCOL_VERSION, command_id, len(payload))
    return header + payload


@dataclass
class Packet:
    protocol_version: int
    command_id: int
    payload: bytes


class PacketParser:
    """Remonta pacotes a partir de bytes recebidos, um byte por vez.

    Espelha o parser não bloqueante de ``SerialProtocol.cpp`` do firmware,
    mas do lado do host onde ler byte a byte de uma porta serial é comum.
    """

    _WAIT_VERSION, _WAIT_COMMAND, _WAIT_LEN_LOW, _WAIT_LEN_HIGH, _WAIT_PAYLOAD = range(5)

    def __init__(self) -> None:
        self._reset()

    def _reset(self) -> None:
        self._state = self._WAIT_VERSION
        self._protocol_version = 0
        self._command_id = 0
        self._payload_length = 0
        self._payload = bytearray()

    def feed(self, data: bytes) -> list[Packet]:
        packets: list[Packet] = []
        for byte in data:
            packet = self._feed_byte(byte)
            if packet is not None:
                packets.append(packet)
        return packets

    def _feed_byte(self, byte: int) -> Packet | None:
        if self._state == self._WAIT_VERSION:
            self._protocol_version = byte
            self._state = self._WAIT_COMMAND
        elif self._state == self._WAIT_COMMAND:
            self._command_id = byte
            self._state = self._WAIT_LEN_LOW
        elif self._state == self._WAIT_LEN_LOW:
            self._payload_length = byte
            self._state = self._WAIT_LEN_HIGH
        elif self._state == self._WAIT_LEN_HIGH:
            self._payload_length |= byte << 8
            self._payload = bytearray()
            if self._payload_length == 0:
                return self._complete()
            self._state = self._WAIT_PAYLOAD
        elif self._state == self._WAIT_PAYLOAD:
            self._payload.append(byte)
            if len(self._payload) >= self._payload_length:
                return self._complete()
        return None

    def _complete(self) -> Packet:
        packet = Packet(self._protocol_version, self._command_id, bytes(self._payload))
        self._reset()
        return packet


@dataclass
class KeyAction:
    modifiers: int
    keycode: int
    # Nome da acao nomeada (ver named_actions.py) que gerou este
    # modifiers/keycode, ou None se foi montado manualmente no editor.
    # Metadado local apenas — Profile.to_bytes() nao serializa este campo,
    # o firmware nunca recebe/conhece isto (spec target-os-shortcuts).
    named_action: str | None = None
    # Caminho do executavel vinculado (spec app-launcher-volume-mixer).
    # Quando presente, modifiers/keycode SHALL ser o combo reservado da
    # posicao de tecla correspondente (ver app_launcher.py) — o app residente
    # detecta esse combo via atalho global e abre este app. Metadado local
    # apenas, igual named_action.
    app_path: str | None = None

    def modifier_names(self) -> list[str]:
        return [name for bit, name in MODIFIER_NAMES.items() if self.modifiers & bit]

    @staticmethod
    def from_modifier_names(names: list[str], keycode: int, named_action: str | None = None) -> "KeyAction":
        modifiers = 0
        for name in names:
            modifiers |= NAME_TO_MODIFIER[name]
        return KeyAction(modifiers=modifiers, keycode=keycode, named_action=named_action)


@dataclass
class Profile:
    name: str
    keys: list[KeyAction]
    schema_version: int = PROFILE_SCHEMA_VERSION
    # Sistema operacional alvo (spec target-os-shortcuts). Metadado local
    # apenas — Profile.to_bytes() nao serializa este campo.
    target_os: str = DEFAULT_TARGET_OS
    # Caminho (Windows) ou nome de processo (Mac) do app cujo volume o
    # encoder ajusta enquanto este perfil estiver ativo (spec
    # app-launcher-volume-mixer). None = volume master do sistema. Metadado
    # local apenas — Profile.to_bytes() nao serializa este campo; no Mac,
    # este campo e sempre ignorado no ajuste real (ver volume_control.py).
    volume_mixer_app: str | None = None

    def to_bytes(self) -> bytes:
        name_bytes = self.name.encode("ascii", errors="replace")[: PROFILE_NAME_LENGTH - 1]
        name_field = name_bytes + b"\x00" * (PROFILE_NAME_LENGTH - len(name_bytes))

        keys = list(self.keys[:MAX_KEYS_PER_PROFILE])
        while len(keys) < MAX_KEYS_PER_PROFILE:
            keys.append(KeyAction(MOD_NONE, 0))

        body = bytes([self.schema_version]) + name_field
        for key in keys:
            body += bytes([key.modifiers, key.keycode])
        return body

    @staticmethod
    def from_bytes(data: bytes) -> "Profile":
        if len(data) != PROFILE_STRUCT_SIZE:
            raise ValueError(f"Profile esperado com {PROFILE_STRUCT_SIZE} bytes, recebido {len(data)}")

        schema_version = data[0]
        name = data[1:1 + PROFILE_NAME_LENGTH].split(b"\x00", 1)[0].decode("ascii", errors="replace")
        keys = []
        offset = 1 + PROFILE_NAME_LENGTH
        for i in range(MAX_KEYS_PER_PROFILE):
            modifiers, keycode = data[offset + i * 2], data[offset + i * 2 + 1]
            keys.append(KeyAction(modifiers, keycode))
        return Profile(name=name, keys=keys, schema_version=schema_version)
