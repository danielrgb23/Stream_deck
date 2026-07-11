#include "hal/common/EncoderInput.h"

#include <Arduino.h>

EncoderInput::EncoderInput(uint8_t pinA, uint8_t pinB, uint8_t pinButton)
    : pinA_(pinA), pinB_(pinB), pinButton_(pinButton) {}

void EncoderInput::begin() {
    pinMode(pinA_, INPUT_PULLUP);
    pinMode(pinB_, INPUT_PULLUP);
    pinMode(pinButton_, INPUT_PULLUP);
    lastEncoded_ = (uint8_t)((digitalRead(pinA_) << 1) | digitalRead(pinB_));
    lastButtonState_ = digitalRead(pinButton_) == LOW;
}

void EncoderInput::poll() {
    // Tabela classica de transicao de quadratura: indice = (estado anterior
    // de 2 bits << 2) | estado atual de 2 bits.
    static const int8_t TRANSITION[16] = {
        0, -1, 1, 0,
        1, 0, 0, -1,
        -1, 0, 0, 1,
        0, 1, -1, 0,
    };

    uint8_t encoded = (uint8_t)((digitalRead(pinA_) << 1) | digitalRead(pinB_));
    uint8_t sum = (uint8_t)((lastEncoded_ << 2) | encoded);
    int8_t direction = TRANSITION[sum & 0x0F];

    if (direction > 0) {
        // logicalId ignorado para eventos de rotacao — ProfileManager troca
        // de perfil (proximo/anterior), nao resolve uma tecla especifica.
        queue_.push(InputEvent{0, InputEventType::ROTATE_CW});
    } else if (direction < 0) {
        queue_.push(InputEvent{0, InputEventType::ROTATE_CCW});
    }
    lastEncoded_ = encoded;

    bool buttonPressed = digitalRead(pinButton_) == LOW; // pull-up: LOW = pressionado
    if (buttonPressed != lastButtonState_) {
        lastButtonState_ = buttonPressed;
        queue_.push(InputEvent{ENCODER_BUTTON_LOGICAL_ID,
                                buttonPressed ? InputEventType::PRESS : InputEventType::RELEASE});
    }
}

bool EncoderInput::hasEvent() const {
    return !queue_.isEmpty();
}

InputEvent EncoderInput::getEvent() {
    return queue_.pop();
}
