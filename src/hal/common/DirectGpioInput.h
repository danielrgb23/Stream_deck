#pragma once

#include "core/Profile.h"
#include "hal/InputSource.h"
#include "hal/common/InputEventQueue.h"

// Le N botoes fisicos ligados diretamente cada um ao seu proprio GPIO
// (INPUT_PULLUP, botao liga o pino ao GND quando pressionado) — sem matriz de
// linhas/colunas. Emite eventos PRESS/RELEASE com id logico = indice do pino
// no array passado ao construtor (spec hal-interfaces). Alternativa a
// ButtonMatrixInput para prototipos com poucas teclas onde cada uma tem seu
// proprio pino dedicado.
class DirectGpioInput : public InputSource {
public:
    DirectGpioInput(const uint8_t *pins, uint8_t numPins, uint16_t debounceMs = 20);

    void begin() override;
    void poll() override;
    bool hasEvent() const override;
    InputEvent getEvent() override;

private:
    static const uint8_t MAX_KEYS = MAX_KEYS_PER_PROFILE;

    const uint8_t *pins_;
    uint8_t numPins_;
    uint16_t debounceMs_;

    bool lastStableState_[MAX_KEYS];
    bool lastRawState_[MAX_KEYS];
    unsigned long lastChangeMs_[MAX_KEYS];

    InputEventQueue<16> queue_;
};
