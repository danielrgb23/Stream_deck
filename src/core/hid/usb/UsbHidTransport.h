#pragma once

#include "core/hid/HidTransport.h"

// Transporte HID via USB nativo (TinyUSB / USBHIDKeyboard do arduino-esp32).
// So para chips com USB OTG nativo (ex: ESP32-S3, spec profile-core).
class UsbHidTransport : public HidTransport {
public:
    bool begin() override;
    bool isConnected() override;
    void sendKey(const KeyEvent &event) override;
};
