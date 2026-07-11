#include "hal/common/ButtonMatrixInput.h"

#include <Arduino.h>

ButtonMatrixInput::ButtonMatrixInput(const uint8_t *rowPins, uint8_t numRows,
                                      const uint8_t *colPins, uint8_t numCols,
                                      uint16_t debounceMs)
    : rowPins_(rowPins), numRows_(numRows), colPins_(colPins), numCols_(numCols),
      debounceMs_(debounceMs) {
    for (uint8_t i = 0; i < MAX_KEYS; i++) {
        lastStableState_[i] = false;
        lastRawState_[i] = false;
        lastChangeMs_[i] = 0;
    }
}

void ButtonMatrixInput::begin() {
    for (uint8_t r = 0; r < numRows_; r++) {
        pinMode(rowPins_[r], OUTPUT);
        digitalWrite(rowPins_[r], HIGH);
    }
    for (uint8_t c = 0; c < numCols_; c++) {
        pinMode(colPins_[c], INPUT_PULLUP);
    }
}

void ButtonMatrixInput::poll() {
    unsigned long now = millis();

    for (uint8_t r = 0; r < numRows_; r++) {
        digitalWrite(rowPins_[r], LOW);

        for (uint8_t c = 0; c < numCols_; c++) {
            uint8_t logicalId = (uint8_t)(r * numCols_ + c);
            if (logicalId >= MAX_KEYS) {
                continue; // fora da capacidade central (MAX_KEYS_PER_PROFILE)
            }

            bool pressed = digitalRead(colPins_[c]) == LOW; // pull-up: LOW = pressionado

            if (pressed != lastRawState_[logicalId]) {
                lastRawState_[logicalId] = pressed;
                lastChangeMs_[logicalId] = now;
            } else if ((now - lastChangeMs_[logicalId]) >= debounceMs_ &&
                       pressed != lastStableState_[logicalId]) {
                lastStableState_[logicalId] = pressed;
                queue_.push(InputEvent{logicalId, pressed ? InputEventType::PRESS : InputEventType::RELEASE});
            }
        }

        digitalWrite(rowPins_[r], HIGH);
    }
}

bool ButtonMatrixInput::hasEvent() const {
    return !queue_.isEmpty();
}

InputEvent ButtonMatrixInput::getEvent() {
    return queue_.pop();
}
