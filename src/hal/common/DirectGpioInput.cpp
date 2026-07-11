#include "hal/common/DirectGpioInput.h"

#include <Arduino.h>

DirectGpioInput::DirectGpioInput(const uint8_t *pins, uint8_t numPins, uint16_t debounceMs)
    : pins_(pins), numPins_(numPins), debounceMs_(debounceMs) {
    for (uint8_t i = 0; i < MAX_KEYS; i++) {
        lastStableState_[i] = false;
        lastRawState_[i] = false;
        lastChangeMs_[i] = 0;
    }
}

void DirectGpioInput::begin() {
    for (uint8_t i = 0; i < numPins_; i++) {
        pinMode(pins_[i], INPUT_PULLUP);
    }
}

void DirectGpioInput::poll() {
    unsigned long now = millis();

    for (uint8_t i = 0; i < numPins_ && i < MAX_KEYS; i++) {
        bool pressed = digitalRead(pins_[i]) == LOW; // pull-up: LOW = pressionado

        if (pressed != lastRawState_[i]) {
            lastRawState_[i] = pressed;
            lastChangeMs_[i] = now;
        } else if ((now - lastChangeMs_[i]) >= debounceMs_ && pressed != lastStableState_[i]) {
            lastStableState_[i] = pressed;
            queue_.push(InputEvent{i, pressed ? InputEventType::PRESS : InputEventType::RELEASE});
        }
    }
}

bool DirectGpioInput::hasEvent() const {
    return !queue_.isEmpty();
}

InputEvent DirectGpioInput::getEvent() {
    return queue_.pop();
}
