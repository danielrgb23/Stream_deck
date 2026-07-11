#pragma once

#include "core/hid/HidTransport.h"

// Transporte HID via BLE (ESP32-BLE-Keyboard / NimBLE). Para chips sem USB
// nativo (ex: ESP32 WROOM-32, spec profile-core).
class BleHidTransport : public HidTransport {
public:
    bool begin() override;
    bool isConnected() override;
    void sendKey(const KeyEvent &event) override;
};
