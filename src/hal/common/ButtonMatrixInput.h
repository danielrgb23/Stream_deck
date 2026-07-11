#pragma once

#include "core/Profile.h"
#include "hal/InputSource.h"
#include "hal/common/InputEventQueue.h"

// Le uma matriz de botoes (linhas x colunas) com debounce e emite eventos
// PRESS/RELEASE com id logico = row * numCols + col. Compartilhada por
// Essential e Streamer (spec hal-interfaces) — o pinout de cada modelo e
// passado no construtor, o codigo de scan e identico.
class ButtonMatrixInput : public InputSource {
public:
    ButtonMatrixInput(const uint8_t *rowPins, uint8_t numRows,
                       const uint8_t *colPins, uint8_t numCols,
                       uint16_t debounceMs = 20);

    void begin() override;
    void poll() override;
    bool hasEvent() const override;
    InputEvent getEvent() override;

private:
    static const uint8_t MAX_KEYS = MAX_KEYS_PER_PROFILE;

    const uint8_t *rowPins_;
    uint8_t numRows_;
    const uint8_t *colPins_;
    uint8_t numCols_;
    uint16_t debounceMs_;

    bool lastStableState_[MAX_KEYS];
    bool lastRawState_[MAX_KEYS];
    unsigned long lastChangeMs_[MAX_KEYS];

    InputEventQueue<16> queue_;
};
