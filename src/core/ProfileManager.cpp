#include "core/ProfileManager.h"

#include "core/ProfileStore.h"
#include "core/ReservedVolumeCombo.h"

ProfileManager::ProfileManager(InputSource &input, DisplayDriver &display, HidTransport &hid)
    : input_(input), display_(display), hid_(hid) {}

void ProfileManager::begin() {
    ProfileStore::begin();
    input_.begin();
    hid_.begin();
    display_.init();
    display_.showProfile(ProfileStore::getActiveProfile());
}

void ProfileManager::update() {
    input_.poll();
    while (input_.hasEvent()) {
        handleEvent(input_.getEvent());
    }
}

void ProfileManager::handleEvent(const InputEvent &event) {
    switch (event.type) {
        case InputEventType::ROTATE_CW:
            // Sinaliza "subir volume" ao app desktop residente via combo HID
            // reservado (spec app-launcher-volume-mixer) — nao troca mais de
            // perfil (isso agora e o clique do encoder, ver PRESS abaixo).
            hid_.sendKey(KeyEvent{VOLUME_COMBO_MODIFIERS, VOLUME_UP_KEYCODE, true});
            hid_.sendKey(KeyEvent{VOLUME_COMBO_MODIFIERS, VOLUME_UP_KEYCODE, false});
            break;
        case InputEventType::ROTATE_CCW:
            hid_.sendKey(KeyEvent{VOLUME_COMBO_MODIFIERS, VOLUME_DOWN_KEYCODE, true});
            hid_.sendKey(KeyEvent{VOLUME_COMBO_MODIFIERS, VOLUME_DOWN_KEYCODE, false});
            break;
        case InputEventType::PRESS:
            if (event.logicalId == ENCODER_BUTTON_LOGICAL_ID) {
                switchToNextProfile();
            } else {
                resolveKey(event.logicalId, true);
            }
            break;
        case InputEventType::RELEASE:
            if (event.logicalId != ENCODER_BUTTON_LOGICAL_ID) {
                resolveKey(event.logicalId, false);
            }
            break;
    }
}

void ProfileManager::resolveKey(uint8_t logicalId, bool pressed) {
    if (logicalId >= MAX_KEYS_PER_PROFILE) {
        return; // ex: botao do encoder (ENCODER_BUTTON_LOGICAL_ID) — sem acao mapeada nesta fase
    }

    const KeyAction &action = ProfileStore::getActiveProfile().keys[logicalId];
    if (action.keycode == 0) {
        return; // tecla nao mapeada
    }

    hid_.sendKey(KeyEvent{action.modifiers, action.keycode, pressed});
}

void ProfileManager::switchToNextProfile() {
    uint8_t next = (uint8_t)((ProfileStore::getActiveProfileId() + 1) % MAX_PROFILES);
    ProfileStore::setActiveProfile(next);
    display_.showProfile(ProfileStore::getActiveProfile());
}
