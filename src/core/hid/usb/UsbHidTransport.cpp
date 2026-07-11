#include "core/hid/usb/UsbHidTransport.h"

#include <USB.h>
#include <USBHIDKeyboard.h>
#include "core/Profile.h"

namespace {
USBHIDKeyboard keyboard;
bool connected = false;
} // namespace

bool UsbHidTransport::begin() {
    keyboard.begin();
    USB.begin();
    connected = true;
    return true;
}

bool UsbHidTransport::isConnected() {
    return connected;
}

void UsbHidTransport::sendKey(const KeyEvent &event) {
    if (!event.pressed) {
        keyboard.releaseAll();
        return;
    }

    if (event.modifiers & MOD_CTRL) keyboard.press(KEY_LEFT_CTRL);
    if (event.modifiers & MOD_SHIFT) keyboard.press(KEY_LEFT_SHIFT);
    if (event.modifiers & MOD_ALT) keyboard.press(KEY_LEFT_ALT);
    if (event.modifiers & MOD_GUI) keyboard.press(KEY_LEFT_GUI);
    keyboard.press(event.keycode);
}
