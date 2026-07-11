"""Persistencia local de perfis do app desktop (spec persistence-schema).

Formato documentado em `docs/desktop-profile-format.md` — este modulo é a
unica fonte da verdade para leitura/escrita desse arquivo; a UI e o cliente
serial nao tocam o arquivo diretamente.
"""

from __future__ import annotations

import json
from pathlib import Path

from . import protocol

DEFAULT_PATH = Path.home() / ".xeeta-streamer" / "profiles.json"


def _key_to_dict(key: protocol.KeyAction) -> dict:
    entry = {"modifiers": key.modifier_names(), "keycode": key.keycode}
    if key.named_action:
        # Presente so quando a tecla veio de uma acao nomeada (spec
        # target-os-shortcuts) — permite re-resolver so essas ao trocar o
        # target_os do perfil, sem tocar em teclas mapeadas manualmente.
        entry["named_action"] = key.named_action
    return entry


def _profile_to_dict(profile_id: int, profile: protocol.Profile) -> dict:
    return {
        "id": profile_id,
        "name": profile.name,
        "target_os": profile.target_os,
        "keys": [_key_to_dict(key) for key in profile.keys],
    }


def _profile_from_dict(data: dict) -> tuple[int, protocol.Profile]:
    keys = [
        protocol.KeyAction.from_modifier_names(
            entry.get("modifiers", []),
            entry.get("keycode", 0),
            named_action=entry.get("named_action"),
        )
        for entry in data.get("keys", [])
    ]
    while len(keys) < protocol.MAX_KEYS_PER_PROFILE:
        keys.append(protocol.KeyAction(protocol.MOD_NONE, 0))

    # Perfis salvos antes desta spec nao tem target_os — default WINDOWS,
    # sem reescrever nada ate o usuario salvar de novo (ver design.md).
    target_os = data.get("target_os", protocol.DEFAULT_TARGET_OS)
    profile = protocol.Profile(name=data.get("name", ""), keys=keys, target_os=target_os)
    return data["id"], profile


class ProfileFile:
    """Um device por arquivo *não* é o modelo — este arquivo cobre todos os
    perfis conhecidos localmente nesta maquina (ver design de persistence-schema:
    fase inicial em JSON, sem banco relacional)."""

    def __init__(self, path: Path | None = None):
        self.path = path or DEFAULT_PATH
        self.schema_version = protocol.PROFILE_SCHEMA_VERSION
        self.profiles: dict[int, protocol.Profile] = {}

    def load(self) -> None:
        if not self.path.exists():
            self.profiles = {}
            return

        data = json.loads(self.path.read_text(encoding="utf-8"))
        self.schema_version = data.get("schema_version", protocol.PROFILE_SCHEMA_VERSION)
        self.profiles = {}
        for entry in data.get("profiles", []):
            profile_id, profile = _profile_from_dict(entry)
            self.profiles[profile_id] = profile

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "schema_version": self.schema_version,
            "profiles": [
                _profile_to_dict(profile_id, profile)
                for profile_id, profile in sorted(self.profiles.items())
            ],
        }
        self.path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    def get(self, profile_id: int) -> protocol.Profile:
        return self.profiles.get(
            profile_id,
            protocol.Profile(name=f"Profile {profile_id}", keys=[protocol.KeyAction(protocol.MOD_NONE, 0)] * protocol.MAX_KEYS_PER_PROFILE),
        )

    def set(self, profile_id: int, profile: protocol.Profile) -> None:
        self.profiles[profile_id] = profile
