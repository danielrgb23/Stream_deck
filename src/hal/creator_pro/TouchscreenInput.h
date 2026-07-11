#pragma once

#include "hal/InputSource.h"

// Stub do Creator Pro (spec hal-interfaces): apenas compila, sem leitura
// real de toque. Implementacao completa e trabalho futuro fora do escopo
// da fundacao — esta classe existe para que os 3 envs linkem uma
// InputSource concreta desde ja.
class TouchscreenInput : public InputSource {
public:
    void begin() override {}
    void poll() override {}
    bool hasEvent() const override { return false; }
    InputEvent getEvent() override { return InputEvent{0, InputEventType::PRESS}; }
};
