#pragma once

#include <stdint.h>

// Limite de perfis por device. Centralizado aqui para nao espalhar a
// constante mágica pelo código (spec persistence-schema).
#define MAX_PROFILES 8

// Numero de teclas fisicas mapeaveis por perfil. Valor inicial generico;
// specs de feature (feature-button-mapping) podem ajustar por modelo.
#define MAX_KEYS_PER_PROFILE 8

// Versao atual do schema de perfil. Incrementar sempre que o layout binario
// de Profile mudar de forma incompativel; ProfileStore usa este valor para
// decidir se um blob lido do NVS pode ser desserializado com seguranca.
#define PROFILE_SCHEMA_VERSION 1

// Bitmask de modificadores de teclado.
#define MOD_NONE  0x00
#define MOD_CTRL  0x01
#define MOD_SHIFT 0x02
#define MOD_ALT   0x04
#define MOD_GUI   0x08

// Uma unica acao de teclado: modificadores + keycode HID. keycode == 0
// significa "tecla nao mapeada".
struct KeyAction {
    uint8_t modifiers;
    uint8_t keycode;
};

// Perfil persistido. Layout binario fixo (sem JSON no firmware) para nao
// gastar RAM/CPU do MCU com parsing — ver design da spec persistence-schema.
//
// schema_version SHALL ser o primeiro campo: permite ao firmware decidir se
// pode desserializar o restante do blob antes de ler qualquer outro campo.
struct Profile {
    uint8_t schema_version;
    char name[16];
    KeyAction keys[MAX_KEYS_PER_PROFILE];
};
