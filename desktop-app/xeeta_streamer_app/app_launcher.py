"""Ação "abrir app" por tecla física (spec app-launcher-volume-mixer).

Cada posição de tecla física tem um combo HID reservado e fixo
(`Ctrl+Alt+Shift+F13` a `F20`) — quando o usuário arrasta um app para uma
tecla, o editor grava esse combo como `modifiers`/`keycode` da tecla (como
qualquer outro mapeamento) e o caminho do app em `app_path`. O firmware não
sabe nem precisa saber que aquele combo específico significa "abrir app" —
ele só emite o que o perfil manda, como sempre fez.

O app residente detecta o combo via atalho global do SO e usa
`logical_id_for_combo()` para descobrir qual tecla (logo, qual `app_path` do
perfil ativo) disparou, sem precisar reimplementar a lógica de resolução de
tecla do firmware.
"""

from __future__ import annotations

from . import protocol


def combo_for_key(logical_id: int) -> protocol.KeyAction:
    """Combo reservado da posição de tecla `logical_id` (0..MAX_KEYS_PER_PROFILE-1)."""
    if not (0 <= logical_id < protocol.MAX_KEYS_PER_PROFILE):
        raise ValueError(f"logical_id fora da faixa: {logical_id}")
    keycode = protocol.RESERVED_KEY_TRIGGER_KEYCODES[logical_id]
    return protocol.KeyAction(modifiers=protocol.RESERVED_ACTION_MODIFIERS, keycode=keycode)


def logical_id_for_combo(modifiers: int, keycode: int) -> int | None:
    """Posição de tecla correspondente a um combo detectado pelo listener global,
    ou None se o combo não é nenhum dos reservados para abrir app."""
    if modifiers != protocol.RESERVED_ACTION_MODIFIERS:
        return None
    try:
        return protocol.RESERVED_KEY_TRIGGER_KEYCODES.index(keycode)
    except ValueError:
        return None


def is_volume_up_combo(modifiers: int, keycode: int) -> bool:
    return modifiers == protocol.RESERVED_ACTION_MODIFIERS and keycode == protocol.RESERVED_VOLUME_UP_KEYCODE


def is_volume_down_combo(modifiers: int, keycode: int) -> bool:
    return modifiers == protocol.RESERVED_ACTION_MODIFIERS and keycode == protocol.RESERVED_VOLUME_DOWN_KEYCODE
