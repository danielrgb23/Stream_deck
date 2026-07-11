"""Listener de atalho global para as ações de app-launcher/volume-mixer
(spec app-launcher-volume-mixer).

Registra os 10 combos reservados (8 de tecla + 2 de volume, ver
`app_launcher.py`/`protocol.py`) como atalhos globais do sistema operacional
via `pynput` — não fala com a porta serial, só reage a teclas que o PRÓPRIO
device já emitiu como HID normal. Roda numa thread própria (gerenciada pelo
`pynput`), por isso os callbacks devem ser rápidos e não tocar em widgets Qt
diretamente.
"""

from __future__ import annotations

from typing import Callable

from pynput import keyboard

from . import protocol

_MODIFIER_PREFIX = "<ctrl>+<alt>+<shift>+"


def _hotkey_string(function_key_number: int) -> str:
    return f"{_MODIFIER_PREFIX}<f{function_key_number}>"


class HotkeyListener:
    def __init__(
        self,
        on_key_trigger: Callable[[int], None],
        on_volume_up: Callable[[], None],
        on_volume_down: Callable[[], None],
    ):
        """`on_key_trigger(logical_id)` é chamado quando o combo reservado da
        tecla `logical_id` (0..MAX_KEYS_PER_PROFILE-1) é detectado;
        `on_volume_up`/`on_volume_down` para os combos fixos de volume."""
        self._on_key_trigger = on_key_trigger
        self._on_volume_up = on_volume_up
        self._on_volume_down = on_volume_down
        self._hotkeys: keyboard.GlobalHotKeys | None = None

    def start(self) -> None:
        mapping: dict[str, Callable[[], None]] = {}

        for logical_id in range(protocol.MAX_KEYS_PER_PROFILE):
            function_key_number = 13 + logical_id  # F13..F20, ver RESERVED_KEY_TRIGGER_KEYCODES
            mapping[_hotkey_string(function_key_number)] = self._make_key_handler(logical_id)

        # Setas em vez de F21/F22: pynput (Key enum) só suporta F1-F20.
        mapping[f"{_MODIFIER_PREFIX}<up>"] = self._on_volume_up  # RESERVED_VOLUME_UP_KEYCODE
        mapping[f"{_MODIFIER_PREFIX}<down>"] = self._on_volume_down  # RESERVED_VOLUME_DOWN_KEYCODE

        self._hotkeys = keyboard.GlobalHotKeys(mapping)
        self._hotkeys.start()

    def stop(self) -> None:
        if self._hotkeys is not None:
            self._hotkeys.stop()
            self._hotkeys = None

    def _make_key_handler(self, logical_id: int) -> Callable[[], None]:
        def handler() -> None:
            self._on_key_trigger(logical_id)

        return handler
