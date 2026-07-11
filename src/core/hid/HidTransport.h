#pragma once

#include <stdint.h>

// Seletores de transporte HID, escolhidos via build_flags (-D HID_TRANSPORT=...)
// em platformio.ini — nunca em runtime (spec profile-core: "evita incluir as
// duas libs no mesmo binário sem necessidade"). Nomes prefixados (nao "USB"/
// "BLE" nus) para nao colidir com o objeto global `USB` do arduino-esp32.
#define HID_TRANSPORT_USB 1
#define HID_TRANSPORT_BLE 2

#ifndef HID_TRANSPORT
#error "HID_TRANSPORT nao definido. Compile com um dos envs de platformio.ini."
#endif

// keycode segue a convencao da biblioteca Arduino Keyboard (compativel
// entre USBHIDKeyboard, do arduino-esp32, e ESP32-BLE-Keyboard) — nao e o
// usage ID cru da tabela USB HID.
struct KeyEvent {
    uint8_t modifiers;
    uint8_t keycode;
    bool pressed;
};

// Interface de transporte HID (spec profile-core). ProfileManager e o
// restante do core SHALL NOT importar TinyUSB nem ESP32-BLE-Keyboard
// diretamente — apenas esta interface.
class HidTransport {
public:
    virtual ~HidTransport() = default;

    virtual bool begin() = 0;
    virtual bool isConnected() = 0;
    virtual void sendKey(const KeyEvent &event) = 0;
};
