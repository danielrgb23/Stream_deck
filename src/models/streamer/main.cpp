#include <Arduino.h>
#include "core/DeviceModel.h"
#include "core/ProfileManager.h"
#include "core/SerialProtocol.h"
#include "core/Version.h"
#include "core/hid/ble/BleHidTransport.h"
#include "hal/common/ButtonMatrixInput.h"
#include "hal/common/CompositeInputSource.h"
#include "hal/common/EncoderInput.h"
#include "hal/streamer/OledStatusDisplay.h"

namespace {
// Pinout placeholder — ajustar quando o layout de PCB do Streamer existir.
const uint8_t ROW_PINS[] = {32, 33};
const uint8_t COL_PINS[] = {25, 26, 27, 14};
const uint8_t ENCODER_PIN_A = 18;
const uint8_t ENCODER_PIN_B = 19;
const uint8_t ENCODER_PIN_BUTTON = 21;

ButtonMatrixInput buttons(ROW_PINS, sizeof(ROW_PINS), COL_PINS, sizeof(COL_PINS));
EncoderInput encoder(ENCODER_PIN_A, ENCODER_PIN_B, ENCODER_PIN_BUTTON);
CompositeInputSource<2> input;
OledStatusDisplay display;
BleHidTransport hid;
ProfileManager profileManager(input, display, hid);
} // namespace

void setup() {
    input.addSource(&buttons);
    input.addSource(&encoder);

    SerialProtocol::begin();
    Serial.printf("Xeeta Streamer [%s] fw v%s booting\n", deviceModelName(), firmwareVersionString());

    profileManager.begin();
}

void loop() {
    SerialProtocol::poll();
    profileManager.update();
}
