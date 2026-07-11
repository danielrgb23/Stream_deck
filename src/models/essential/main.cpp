#include <Arduino.h>
#include "core/DeviceModel.h"
#include "core/ProfileManager.h"
#include "core/SerialProtocol.h"
#include "core/Version.h"
#include "core/hid/ble/BleHidTransport.h"
#include "hal/common/ButtonMatrixInput.h"
#include "hal/essential/NullDisplay.h"

namespace {
// Pinout placeholder — ajustar quando o layout de PCB do Essential existir.
const uint8_t ROW_PINS[] = {32, 33};
const uint8_t COL_PINS[] = {25, 26, 27, 14};

ButtonMatrixInput buttons(ROW_PINS, sizeof(ROW_PINS), COL_PINS, sizeof(COL_PINS));
NullDisplay display;
BleHidTransport hid;
ProfileManager profileManager(buttons, display, hid);
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
