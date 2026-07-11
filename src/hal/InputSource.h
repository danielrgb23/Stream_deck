#pragma once

#include "hal/InputEvent.h"

// Interface de entrada (spec hal-interfaces). ProfileManager e a emulacao
// HID (spec profile-core) SHALL NOT depender de nenhuma implementacao
// concreta (ButtonMatrixInput, EncoderInput, TouchscreenInput, ...) — apenas
// desta interface.
class InputSource {
public:
    virtual ~InputSource() = default;

    virtual void begin() = 0;

    // Le o hardware e enfileira eventos internamente. Nao bloqueante —
    // chamar a cada iteracao de loop().
    virtual void poll() = 0;

    virtual bool hasEvent() const = 0;

    // Remove e retorna o proximo evento da fila interna. So chamar depois
    // de hasEvent() retornar true.
    virtual InputEvent getEvent() = 0;
};
