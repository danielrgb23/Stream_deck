"""Ajuste de volume por processo (spec app-launcher-volume-mixer).

Windows: Core Audio via `pycaw` — ajusta a sessão do processo vinculado
(`ISimpleAudioVolume`), com fallback para o volume master
(`IAudioEndpointVolume`) se o processo não estiver rodando ou não houver
app vinculado.

Mac: a Apple não expõe uma API pública equivalente a `ISimpleAudioVolume`
(volume por processo) — Core Audio só cobre master/por dispositivo. Sempre
ajusta o volume master via `osascript` (nativo do macOS, sem dependência
Python extra), documentado como limitação de plataforma (ver design.md).
"""

from __future__ import annotations

import platform
import subprocess

VOLUME_STEP = 0.05  # 5% por detent do encoder


def adjust_volume(app_name: str | None, direction: int) -> None:
    """`direction`: +1 para subir, -1 para descer."""
    system = platform.system()
    if system == "Windows":
        _adjust_windows(app_name, direction)
    elif system == "Darwin":
        _adjust_mac_master(direction)
    # Outros SOs: fora de escopo (Non-Goal do design.md) — no-op.


def _adjust_windows(app_name: str | None, direction: int) -> None:
    try:
        from pycaw.pycaw import AudioUtilities, ISimpleAudioVolume
    except ImportError:
        return  # pycaw nao instalado — nao deveria acontecer no Windows, mas nao crasha

    session_volume = None
    if app_name:
        target = app_name.lower()
        for session in AudioUtilities.GetAllSessions():
            process = session.Process
            if process is not None and target in process.name().lower():
                session_volume = session._ctl.QueryInterface(ISimpleAudioVolume)
                break

    if session_volume is not None:
        current = session_volume.GetMasterVolume()
        new_level = max(0.0, min(1.0, current + direction * VOLUME_STEP))
        session_volume.SetMasterVolume(new_level, None)
        return

    # Sem app vinculado, ou vinculado mas nao rodando -> fallback master.
    _adjust_windows_master(direction)


def _adjust_windows_master(direction: int) -> None:
    from ctypes import POINTER, cast

    from comtypes import CLSCTX_ALL
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))
    current = volume.GetMasterVolumeLevelScalar()
    new_level = max(0.0, min(1.0, current + direction * VOLUME_STEP))
    volume.SetMasterVolumeLevelScalar(new_level, None)


def _adjust_mac_master(direction: int) -> None:
    delta = direction * int(VOLUME_STEP * 100)
    script = f"set volume output volume (output volume of (get volume settings) + ({delta}))"
    subprocess.run(["osascript", "-e", script], check=False)
