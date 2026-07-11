#include "core/hid/ble/BleHidTransport.h"

#include <BleKeyboard.h>
#include "core/Profile.h"

namespace {
BleKeyboard bleKeyboard("Xeeta Streamer", "Xeeta", 100);
} // namespace

bool BleHidTransport::begin() {
    bleKeyboard.begin();
    return true;
}

bool BleHidTransport::isConnected() {
    return bleKeyboard.isConnected();
}

void BleHidTransport::sendKey(const KeyEvent &event) {
    if (!event.pressed) {
        bleKeyboard.releaseAll();
        return;
    }

    if (event.modifiers & MOD_CTRL) bleKeyboard.press(KEY_LEFT_CTRL);
    if (event.modifiers & MOD_SHIFT) bleKeyboard.press(KEY_LEFT_SHIFT);
    if (event.modifiers & MOD_ALT) bleKeyboard.press(KEY_LEFT_ALT);
    if (event.modifiers & MOD_GUI) bleKeyboard.press(KEY_LEFT_GUI);
    bleKeyboard.press(event.keycode);
}
