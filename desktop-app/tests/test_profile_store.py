"""Persistência local de perfis (spec persistence-schema)."""

from pathlib import Path

from xeeta_streamer_app import app_launcher, profile_store, protocol


def test_roundtrip_with_named_action_and_app_launcher_fields(tmp_path: Path):
    keys = [app_launcher.combo_for_key(0)] + [protocol.KeyAction(protocol.MOD_NONE, 0)] * 7
    keys[0].app_path = "/Applications/Spotify.app"
    profile = protocol.Profile(name="Streaming", keys=keys, target_os=protocol.TARGET_OS_MAC, volume_mixer_app="Discord")

    store = profile_store.ProfileFile(tmp_path / "profiles.json")
    store.load()
    store.set(0, profile)
    store.save()

    raw = (tmp_path / "profiles.json").read_text()
    assert '"target_os": "MAC"' in raw
    assert '"volume_mixer_app": "Discord"' in raw
    assert '"app_path": "/Applications/Spotify.app"' in raw

    reloaded = profile_store.ProfileFile(tmp_path / "profiles.json")
    reloaded.load()
    loaded = reloaded.get(0)
    assert loaded.target_os == protocol.TARGET_OS_MAC
    assert loaded.volume_mixer_app == "Discord"
    assert loaded.keys[0].app_path == "/Applications/Spotify.app"
    assert loaded.keys[1].app_path is None


def test_backward_compat_with_profiles_saved_before_later_specs(tmp_path: Path):
    """Perfis salvos antes de target-os-shortcuts/app-launcher-volume-mixer
    nao tem target_os/volume_mixer_app/app_path — devem carregar com defaults,
    sem erro."""
    path = tmp_path / "profiles.json"
    path.write_text(
        '{"schema_version": 1, "profiles": [{"id": 0, "name": "Old", '
        '"keys": [{"modifiers": ["CTRL"], "keycode": 99}]}]}'
    )

    store = profile_store.ProfileFile(path)
    store.load()
    loaded = store.get(0)

    assert loaded.target_os == protocol.DEFAULT_TARGET_OS
    assert loaded.volume_mixer_app is None
    assert loaded.keys[0].app_path is None
    assert loaded.keys[0].named_action is None
