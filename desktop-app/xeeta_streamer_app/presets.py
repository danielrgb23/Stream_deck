"""Biblioteca de presets de perfil (spec feature-software-presets).

Um "pacote de perfil" é um JSON com metadados (nome, software-alvo, notas de
uso) e um mapeamento default de teclas — pronto para aplicar a um perfil sem
exigir edição manual tecla por tecla. Os pacotes ficam em `desktop-app/presets/`,
um arquivo por pacote.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from . import protocol

PRESETS_DIR = Path(__file__).resolve().parent.parent / "presets"


@dataclass
class Preset:
    name: str
    target_software: str
    keys: list[protocol.KeyAction]
    notes: str = ""
    source_path: Path | None = field(default=None, repr=False)

    def to_profile(self) -> protocol.Profile:
        return protocol.Profile(name=self.name, keys=list(self.keys))

    @staticmethod
    def from_dict(data: dict, source_path: Path | None = None) -> "Preset":
        keys = [
            protocol.KeyAction.from_modifier_names(entry.get("modifiers", []), entry.get("keycode", 0))
            for entry in data.get("keys", [])
        ]
        while len(keys) < protocol.MAX_KEYS_PER_PROFILE:
            keys.append(protocol.KeyAction(protocol.MOD_NONE, 0))

        return Preset(
            name=data["name"],
            target_software=data.get("target_software", ""),
            keys=keys[: protocol.MAX_KEYS_PER_PROFILE],
            notes=data.get("notes", ""),
            source_path=source_path,
        )


def list_presets(presets_dir: Path | None = None) -> list[Preset]:
    """Carrega todos os pacotes `*.json` do diretório de presets, em ordem alfabética."""
    directory = presets_dir or PRESETS_DIR
    if not directory.exists():
        return []

    presets = []
    for path in sorted(directory.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        presets.append(Preset.from_dict(data, source_path=path))
    return presets
