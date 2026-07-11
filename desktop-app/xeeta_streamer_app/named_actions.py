"""Biblioteca de ações nomeadas multiplataforma (spec target-os-shortcuts).

Cada ação resolve para `(modifiers, keycode)` explicitamente por sistema
operacional — não é uma regra genérica de "trocar CTRL por GUI", porque
nem toda ação segue essa regra (Refazer usa Ctrl+Y no Windows e
Cmd+Shift+Z no Mac, não só o mesmo atalho com o modificador trocado).
Ver a tabela completa em `openspec/changes/feature-target-os-shortcuts/design.md`.
"""

from __future__ import annotations

from . import protocol

# name -> {target_os: (modifier_names, char)}
_ACTIONS: dict[str, dict[str, tuple[list[str], str]]] = {
    "COPY": {
        protocol.TARGET_OS_WINDOWS: (["CTRL"], "c"),
        protocol.TARGET_OS_MAC: (["GUI"], "c"),
    },
    "PASTE": {
        protocol.TARGET_OS_WINDOWS: (["CTRL"], "v"),
        protocol.TARGET_OS_MAC: (["GUI"], "v"),
    },
    "CUT": {
        protocol.TARGET_OS_WINDOWS: (["CTRL"], "x"),
        protocol.TARGET_OS_MAC: (["GUI"], "x"),
    },
    "UNDO": {
        protocol.TARGET_OS_WINDOWS: (["CTRL"], "z"),
        protocol.TARGET_OS_MAC: (["GUI"], "z"),
    },
    "REDO": {
        protocol.TARGET_OS_WINDOWS: (["CTRL"], "y"),
        protocol.TARGET_OS_MAC: (["GUI", "SHIFT"], "z"),
    },
    "SELECT_ALL": {
        protocol.TARGET_OS_WINDOWS: (["CTRL"], "a"),
        protocol.TARGET_OS_MAC: (["GUI"], "a"),
    },
    "SAVE": {
        protocol.TARGET_OS_WINDOWS: (["CTRL"], "s"),
        protocol.TARGET_OS_MAC: (["GUI"], "s"),
    },
    "FIND": {
        protocol.TARGET_OS_WINDOWS: (["CTRL"], "f"),
        protocol.TARGET_OS_MAC: (["GUI"], "f"),
    },
    "CLOSE": {
        protocol.TARGET_OS_WINDOWS: (["CTRL"], "w"),
        protocol.TARGET_OS_MAC: (["GUI"], "w"),
    },
}

DISPLAY_NAMES: dict[str, str] = {
    "COPY": "Copiar",
    "PASTE": "Colar",
    "CUT": "Recortar",
    "UNDO": "Desfazer",
    "REDO": "Refazer",
    "SELECT_ALL": "Selecionar tudo",
    "SAVE": "Salvar",
    "FIND": "Buscar",
    "CLOSE": "Fechar",
}


def action_names() -> list[str]:
    """Nomes de ação disponíveis, na ordem de exibição da tabela acima."""
    return list(_ACTIONS.keys())


def resolve(action_name: str, target_os: str) -> protocol.KeyAction:
    """Resolve uma ação nomeada para a KeyAction do sistema operacional alvo."""
    modifier_names, char = _ACTIONS[action_name][target_os]
    keycode = ord(char)
    return protocol.KeyAction.from_modifier_names(modifier_names, keycode, named_action=action_name)
