#pragma once

#include "hal/InputEvent.h"

// Fila circular simples de InputEvent. Desacopla a leitura de hardware
// (poll) do consumo (getEvent) nas InputSource concretas que leem hardware
// fisico (ButtonMatrixInput, EncoderInput) — evita duplicar essa logica em
// cada uma.
template <uint8_t CAPACITY>
class InputEventQueue {
public:
    bool push(const InputEvent &event) {
        uint8_t next = (uint8_t)((head_ + 1) % CAPACITY);
        if (next == tail_) {
            return false; // fila cheia — evento descartado
        }
        buffer_[head_] = event;
        head_ = next;
        return true;
    }

    bool isEmpty() const {
        return head_ == tail_;
    }

    InputEvent pop() {
        InputEvent event = buffer_[tail_];
        tail_ = (uint8_t)((tail_ + 1) % CAPACITY);
        return event;
    }

private:
    InputEvent buffer_[CAPACITY];
    uint8_t head_ = 0;
    uint8_t tail_ = 0;
};
