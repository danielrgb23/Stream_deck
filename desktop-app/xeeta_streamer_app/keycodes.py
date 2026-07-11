"""Tabela de keycodes compativel com a biblioteca Arduino Keyboard.

`USBHIDKeyboard` (arduino-esp32/TinyUSB) e `ESP32-BLE-Keyboard` (NimBLE) usam a
mesma convencao de valores para teclas especiais (0x80+) — a mesma usada pela
biblioteca `Keyboard` oficial do Arduino. Para caracteres imprimiveis comuns
(letras, digitos, pontuacao), o keycode e simplesmente o valor ASCII, que as
duas bibliotecas traduzem internamente para o usage HID correto.

Este arquivo é a fonte da verdade que o app usa para popular o editor de
mapeamento — os valores numéricos aqui DEVEM continuar batendo com o que o
firmware espera em `KeyAction.keycode` (spec profile-core).
"""

from __future__ import annotations

SPECIAL_KEYS: dict[str, int] = {
    "LEFT_CTRL": 0x80,
    "LEFT_SHIFT": 0x81,
    "LEFT_ALT": 0x82,
    "LEFT_GUI": 0x83,
    "RIGHT_CTRL": 0x84,
    "RIGHT_SHIFT": 0x85,
    "RIGHT_ALT": 0x86,
    "RIGHT_GUI": 0x87,
    "UP_ARROW": 0xDA,
    "DOWN_ARROW": 0xD9,
    "LEFT_ARROW": 0xD8,
    "RIGHT_ARROW": 0xD7,
    "BACKSPACE": 0xB2,
    "TAB": 0xB3,
    "RETURN": 0xB0,
    "ENTER": 0xB0,
    "ESC": 0xB1,
    "INSERT": 0xD1,
    "DELETE": 0xD4,
    "PAGE_UP": 0xD3,
    "PAGE_DOWN": 0xD6,
    "HOME": 0xD2,
    "END": 0xD5,
    "CAPS_LOCK": 0xC1,
    "SPACE": ord(" "),
    "F1": 0xC2,
    "F2": 0xC3,
    "F3": 0xC4,
    "F4": 0xC5,
    "F5": 0xC6,
    "F6": 0xC7,
    "F7": 0xC8,
    "F8": 0xC9,
    "F9": 0xCA,
    "F10": 0xCB,
    "F11": 0xCC,
    "F12": 0xCD,
}

# F13-F24 nao sao padrao da biblioteca Arduino Keyboard/BLE Keyboard, mas sao
# muito usadas em atalhos de streaming (OBS etc, ver feature-software-presets)
# justamente por raramente colidirem com atalhos de outros apps. Muitos forks
# de ESP32-BLE-Keyboard/USBHIDKeyboard as expõem a partir de 0xF0; se a
# biblioteca instalada não suportar, o app ainda envia o byte — cabe ao
# firmware/lib decidir o que fazer com um valor não reconhecido.
for _index in range(13, 25):
    SPECIAL_KEYS[f"F{_index}"] = 0xF0 + (_index - 13)


def printable_keycode(char: str) -> int:
    """Keycode de um caractere imprimivel (letra, digito, pontuacao) — ASCII cru."""
    if len(char) != 1:
        raise ValueError("printable_keycode espera um unico caractere")
    return ord(char)


def all_key_names() -> list[str]:
    """Nomes de tecla disponiveis no editor, em ordem de exibicao."""
    printable = [chr(c) for c in range(ord("a"), ord("z") + 1)] + [str(d) for d in range(10)]
    return printable + list(SPECIAL_KEYS.keys())


def keycode_for_name(name: str) -> int:
    if name in SPECIAL_KEYS:
        return SPECIAL_KEYS[name]
    if len(name) == 1:
        return printable_keycode(name)
    raise ValueError(f"Tecla desconhecida: {name!r}")


def name_for_keycode(keycode: int) -> str:
    for name, value in SPECIAL_KEYS.items():
        if value == keycode:
            return name
    if 0x20 <= keycode < 0x7F:
        return chr(keycode)
    return f"0x{keycode:02X}"
