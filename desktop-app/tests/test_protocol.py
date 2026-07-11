"""Envelope serial + struct Profile (spec serial-protocol, persistence-schema)."""

from xeeta_streamer_app import protocol


def test_encode_packet_matches_firmware_envelope():
    packet = protocol.encode_packet(protocol.CommandId.PING)
    assert packet == bytes([protocol.PROTOCOL_VERSION, protocol.CommandId.PING, 0, 0])


def test_packet_parser_roundtrip():
    parser = protocol.PacketParser()
    data = protocol.encode_packet(protocol.CommandId.PONG, b"PONG")
    packets = parser.feed(data)
    assert len(packets) == 1
    assert packets[0].command_id == protocol.CommandId.PONG
    assert packets[0].payload == b"PONG"


def test_profile_to_bytes_from_bytes_roundtrip():
    keys = [protocol.KeyAction(protocol.MOD_CTRL | protocol.MOD_SHIFT, ord("a"))] + [
        protocol.KeyAction(protocol.MOD_NONE, 0)
    ] * (protocol.MAX_KEYS_PER_PROFILE - 1)
    profile = protocol.Profile(name="OBS", keys=keys)

    raw = profile.to_bytes()
    assert len(raw) == protocol.PROFILE_STRUCT_SIZE

    restored = protocol.Profile.from_bytes(raw)
    assert restored.name == "OBS"
    assert restored.keys[0].modifiers == (protocol.MOD_CTRL | protocol.MOD_SHIFT)
    assert restored.keys[0].keycode == ord("a")
    assert restored.keys[0].modifier_names() == ["CTRL", "SHIFT"]


def test_profile_wire_format_ignores_local_only_fields():
    """target_os (target-os-shortcuts), named_action e app_path
    (app-launcher-volume-mixer) sao metadado local — o firmware nunca os
    recebe, entao to_bytes()/from_bytes() nao devem serializa-los."""
    keys = [
        protocol.KeyAction(protocol.MOD_GUI, ord("c"), named_action="COPY", app_path="/Applications/Spotify.app")
    ] + [protocol.KeyAction(protocol.MOD_NONE, 0)] * (protocol.MAX_KEYS_PER_PROFILE - 1)
    profile = protocol.Profile(name="Test", keys=keys, target_os=protocol.TARGET_OS_MAC, volume_mixer_app="Discord")

    restored = protocol.Profile.from_bytes(profile.to_bytes())

    assert restored.target_os == protocol.DEFAULT_TARGET_OS  # nao veio do wire, e o default
    assert restored.volume_mixer_app is None
    assert restored.keys[0].named_action is None
    assert restored.keys[0].app_path is None
    # mas o modifiers/keycode em si (o que realmente vai pro firmware) e preservado
    assert restored.keys[0].modifiers == protocol.MOD_GUI
    assert restored.keys[0].keycode == ord("c")
