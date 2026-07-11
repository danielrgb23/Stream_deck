"""Enumeração de aplicativos instalados (spec app-launcher-volume-mixer).

Windows: atalhos (`.lnk`) do Menu Iniciar. Mac: pacotes `.app` em
`/Applications`. Sem ícone nesta versão (Non-Goal do design.md) — só nome
e caminho, para popular o painel arrastável do editor.
"""

from __future__ import annotations

import os
import platform
import subprocess
from dataclasses import dataclass
from pathlib import Path

_WINDOWS_START_MENU_DIRS = [
    Path(os.environ.get("PROGRAMDATA", "")) / "Microsoft" / "Windows" / "Start Menu" / "Programs",
    Path(os.environ.get("APPDATA", "")) / "Microsoft" / "Windows" / "Start Menu" / "Programs",
]

_MAC_APPLICATION_DIRS = [
    Path("/Applications"),
    Path.home() / "Applications",
]


@dataclass
class InstalledApp:
    name: str
    path: str


def list_installed_apps() -> list[InstalledApp]:
    system = platform.system()
    if system == "Windows":
        return _list_windows_apps()
    if system == "Darwin":
        return _list_mac_apps()
    return []


def _list_windows_apps() -> list[InstalledApp]:
    apps: dict[str, InstalledApp] = {}
    for start_menu_dir in _WINDOWS_START_MENU_DIRS:
        if not start_menu_dir.is_dir():
            continue
        for shortcut in start_menu_dir.rglob("*.lnk"):
            name = shortcut.stem
            apps[name] = InstalledApp(name=name, path=str(shortcut))
    return sorted(apps.values(), key=lambda app: app.name.lower())


def _list_mac_apps() -> list[InstalledApp]:
    apps: dict[str, InstalledApp] = {}
    for applications_dir in _MAC_APPLICATION_DIRS:
        if not applications_dir.is_dir():
            continue
        for bundle in applications_dir.glob("*.app"):
            name = bundle.stem
            apps[name] = InstalledApp(name=name, path=str(bundle))
    return sorted(apps.values(), key=lambda app: app.name.lower())


def open_app(path: str) -> None:
    """Abre o app/atalho vinculado. Multiplataforma: `.lnk` é resolvido pelo
    próprio Windows via `os.startfile`; `.app` é aberto via `open` no Mac."""
    system = platform.system()
    if system == "Windows":
        os.startfile(path)  # type: ignore[attr-defined]
    elif system == "Darwin":
        subprocess.run(["open", path], check=False)
    else:
        subprocess.run(["xdg-open", path], check=False)
