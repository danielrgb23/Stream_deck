#include "core/ProfileStore.h"

#include <Preferences.h>
#include <string.h>
#include <stdio.h>

namespace ProfileStore {

namespace {

// Namespace unico do NVS para este firmware (limite do ESP-IDF: 15 chars).
const char *NVS_NAMESPACE = "xeeta_streamer";
const char *KEY_SCHEMA_VERSION = "schema_version";
const char *KEY_ACTIVE_ID = "active_id";

Preferences prefs;
Profile profiles[MAX_PROFILES];
uint8_t activeProfileId = 0;
uint32_t writeCount = 0;

void profileKey(uint8_t id, char *out, size_t outLen) {
    snprintf(out, outLen, "profile_%u", id);
}

Profile defaultProfile(uint8_t id) {
    Profile p;
    p.schema_version = PROFILE_SCHEMA_VERSION;
    snprintf(p.name, sizeof(p.name), "Profile %u", id);
    for (uint8_t i = 0; i < MAX_KEYS_PER_PROFILE; i++) {
        p.keys[i] = {MOD_NONE, 0};
    }
    return p;
}

// Le um unico perfil do NVS para dentro de profiles[id]. Verifica o
// schema_version ANTES de aceitar o resto do blob (spec persistence-schema:
// "firmware verifica a versao antes de desserializar, evitando leitura
// incorreta de campos"). Blob ausente, de tamanho incorreto, ou com
// schema_version desconhecido cai para um perfil default seguro.
void loadProfileFromNvs(uint8_t id) {
    char key[16];
    profileKey(id, key, sizeof(key));

    uint8_t raw[sizeof(Profile)];
    size_t len = prefs.getBytesLength(key);

    if (len == sizeof(Profile)) {
        prefs.getBytes(key, raw, sizeof(raw));
        uint8_t storedVersion = raw[0]; // schema_version e o primeiro campo do struct
        if (storedVersion >= 1 && storedVersion <= PROFILE_SCHEMA_VERSION) {
            memcpy(&profiles[id], raw, sizeof(Profile));
            return;
        }
    }

    profiles[id] = defaultProfile(id);
}

} // namespace

void begin() {
    prefs.begin(NVS_NAMESPACE, false);

    // Provisionamento do namespace na primeira execucao. Nao conta como
    // "escrita de perfil" (nvsWriteCount rastreia apenas saveProfile).
    if (prefs.getUChar(KEY_SCHEMA_VERSION, 0) == 0) {
        prefs.putUChar(KEY_SCHEMA_VERSION, PROFILE_SCHEMA_VERSION);
    }

    activeProfileId = prefs.getUChar(KEY_ACTIVE_ID, 0);
    if (activeProfileId >= MAX_PROFILES) {
        activeProfileId = 0;
    }

    for (uint8_t id = 0; id < MAX_PROFILES; id++) {
        loadProfileFromNvs(id);
    }
}

uint8_t getActiveProfileId() {
    return activeProfileId;
}

const Profile &getProfile(uint8_t id) {
    if (id >= MAX_PROFILES) {
        id = 0;
    }
    return profiles[id];
}

const Profile &getActiveProfile() {
    return profiles[activeProfileId];
}

void setActiveProfile(uint8_t id) {
    if (id < MAX_PROFILES) {
        activeProfileId = id; // RAM apenas — nenhuma escrita no NVS
    }
}

void saveProfile(uint8_t id, const Profile &profile) {
    if (id >= MAX_PROFILES) {
        return;
    }

    profiles[id] = profile;
    profiles[id].schema_version = PROFILE_SCHEMA_VERSION;

    char key[16];
    profileKey(id, key, sizeof(key));
    prefs.putBytes(key, &profiles[id], sizeof(Profile));
    writeCount++;
}

uint32_t nvsWriteCount() {
    return writeCount;
}

} // namespace ProfileStore
