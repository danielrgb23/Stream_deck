#include <Arduino.h>
#include "core/DeviceModel.h"
#include "core/ProfileManager.h"
#include "core/SerialProtocol.h"
#include "core/Version.h"
#include "core/hid/ble/BleHidTransport.h"
#include "hal/common/CompositeInputSource.h"
#include "hal/common/DirectGpioInput.h"
#include "hal/common/EncoderInput.h"
#include "hal/essential/NullDisplay.h"

// Desligado por padrao — reative (1) para depurar fiacao nova: loga cada
// InputEvent e um dump periodico do estado cru de cada pino no serial.
#define DEBUG_LOG_INPUT_EVENTS 0

namespace {
// Pinout do protótipo físico validado em bancada (5 botões em pinos diretos,
// sem matriz, + encoder rotativo). OLED ainda não instalado — NullDisplay.
const uint8_t BUTTON_PINS[] = {4, 5, 13, 14, 16};
const uint8_t ENCODER_PIN_CLK = 21;
const uint8_t ENCODER_PIN_DT = 22;
const uint8_t ENCODER_PIN_SW = 25;

DirectGpioInput buttons(BUTTON_PINS, sizeof(BUTTON_PINS));
EncoderInput encoder(ENCODER_PIN_CLK, ENCODER_PIN_DT, ENCODER_PIN_SW);
CompositeInputSource<2> input;
NullDisplay display;
BleHidTransport hid;
ProfileManager profileManager(input, display, hid);

#if DEBUG_LOG_INPUT_EVENTS
const char *eventTypeName(InputEventType type) {
    switch (type) {
        case InputEventType::PRESS: return "PRESS";
        case InputEventType::RELEASE: return "RELEASE";
        case InputEventType::ROTATE_CW: return "ROTATE_CW";
        case InputEventType::ROTATE_CCW: return "ROTATE_CCW";
    }
    return "?";
}
#endif
} // namespace

void setup() {
    SerialProtocol::begin();
    Serial.printf("Xeeta Streamer [%s] fw v%s booting\n", deviceModelName(), firmwareVersionString());

    input.addSource(&buttons);
    input.addSource(&encoder);

    profileManager.begin();
}

void loop() {
    SerialProtocol::poll();

    // Poll+drain unico: cada evento e encaminhado ao ProfileManager a partir
    // da mesma leitura (chamar input.poll() de novo e profileManager.update()
    // depois duplicaria o poll e perderia eventos ja drenados aqui).
    input.poll();
    while (input.hasEvent()) {
        InputEvent event = input.getEvent();
#if DEBUG_LOG_INPUT_EVENTS
        Serial.printf("[input] logicalId=%u type=%s\n", event.logicalId, eventTypeName(event.type));
#endif
        profileManager.handleEvent(event);
    }

#if DEBUG_LOG_INPUT_EVENTS
    static unsigned long lastDump = 0;
    unsigned long now = millis();
    if (now - lastDump >= 500) {
        lastDump = now;
        Serial.printf(
            "[raw] b1(%d)=%d b2(%d)=%d b3(%d)=%d b4(%d)=%d b5(%d)=%d clk(%d)=%d dt(%d)=%d sw(%d)=%d\n",
            BUTTON_PINS[0], digitalRead(BUTTON_PINS[0]),
            BUTTON_PINS[1], digitalRead(BUTTON_PINS[1]),
            BUTTON_PINS[2], digitalRead(BUTTON_PINS[2]),
            BUTTON_PINS[3], digitalRead(BUTTON_PINS[3]),
            BUTTON_PINS[4], digitalRead(BUTTON_PINS[4]),
            ENCODER_PIN_CLK, digitalRead(ENCODER_PIN_CLK),
            ENCODER_PIN_DT, digitalRead(ENCODER_PIN_DT),
            ENCODER_PIN_SW, digitalRead(ENCODER_PIN_SW));
    }
#endif
}
