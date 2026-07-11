#include <Arduino.h>
#include "core/DeviceModel.h"
#include "core/ProfileManager.h"
#include "core/SerialProtocol.h"
#include "core/Version.h"
#include "core/hid/usb/UsbHidTransport.h"
#include "hal/creator_pro/TftTouchDisplay.h"
#include "hal/creator_pro/TouchscreenInput.h"

namespace {
TouchscreenInput touchscreen;
TftTouchDisplay display;
UsbHidTransport hid;
ProfileManager profileManager(touchscreen, display, hid);
} // namespace

void setup() {
    SerialProtocol::begin();
    Serial.printf("Xeeta Streamer [%s] fw v%s booting\n", deviceModelName(), firmwareVersionString());

    profileManager.begin();
}

void loop() {
    SerialProtocol::poll();
    profileManager.update();
}
