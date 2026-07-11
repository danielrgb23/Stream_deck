#pragma once

#include "hal/InputSource.h"
#include "hal/common/InputEventQueue.h"

// Combina varias InputSource concretas (ex: ButtonMatrixInput + EncoderInput
// no Streamer) atras de uma unica InputSource, para que ProfileManager (spec
// profile-core) continue dependendo de uma so interface mesmo quando um
// modelo tem mais de uma fonte fisica de entrada.
template <uint8_t MAX_CHILDREN>
class CompositeInputSource : public InputSource {
public:
    void addSource(InputSource *source) {
        if (count_ < MAX_CHILDREN) {
            children_[count_++] = source;
        }
    }

    void begin() override {
        for (uint8_t i = 0; i < count_; i++) {
            children_[i]->begin();
        }
    }

    void poll() override {
        for (uint8_t i = 0; i < count_; i++) {
            children_[i]->poll();
            while (children_[i]->hasEvent()) {
                queue_.push(children_[i]->getEvent());
            }
        }
    }

    bool hasEvent() const override {
        return !queue_.isEmpty();
    }

    InputEvent getEvent() override {
        return queue_.pop();
    }

private:
    InputSource *children_[MAX_CHILDREN] = {};
    uint8_t count_ = 0;
    InputEventQueue<24> queue_;
};
