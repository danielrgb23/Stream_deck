#pragma once

#include "core/Profile.h"

// Combo HID reservado emitido na rotacao do encoder, para sinalizar "subir"/
// "descer volume" ao app desktop residente via atalho global do SO — nao e
// um atalho "de verdade", e so um canal de sinalizacao reaproveitando o
// HidTransport ja existente (spec app-launcher-volume-mixer). Nao faz parte
// do array keys[] do perfil: rotacao do encoder nunca foi uma "tecla logica"
// configuravel por posicao, e continua nao sendo.
//
// Ctrl+Alt+Shift + seta pra cima/baixo — faixa incomum de colidir com
// atalhos de outros programas, e nao usa F21/F22 porque a lib de atalho
// global do app desktop (pynput) so suporta F1-F20. keycode segue a
// convencao Arduino Keyboard (ver desktop-app/xeeta_streamer_app/keycodes.py),
// nao usage ID cru de HID.
#define VOLUME_COMBO_MODIFIERS (MOD_CTRL | MOD_ALT | MOD_SHIFT)
#define VOLUME_UP_KEYCODE 0xDA   // seta para cima
#define VOLUME_DOWN_KEYCODE 0xD9 // seta para baixo
