#include "core/SerialProtocol.h"

#include <Arduino.h>
#include <string.h>
#include "core/ProfileStore.h"
#include "core/Version.h"

namespace SerialProtocol {

namespace {

enum class ParseState {
    WAIT_PROTOCOL_VERSION,
    WAIT_COMMAND_ID,
    WAIT_LENGTH_LOW,
    WAIT_LENGTH_HIGH,
    WAIT_PAYLOAD,
};

ParseState state = ParseState::WAIT_PROTOCOL_VERSION;
SerialPacket incoming;
uint16_t payloadIndex = 0;

void sendPacket(uint8_t commandId, const uint8_t *payload, uint16_t length) {
    uint8_t header[4] = {
        SERIAL_PROTOCOL_VERSION,
        commandId,
        (uint8_t)(length & 0xFF),
        (uint8_t)((length >> 8) & 0xFF),
    };
    Serial.write(header, sizeof(header));
    if (length > 0 && payload != nullptr) {
        Serial.write(payload, length);
    }
}

void handlePing() {
    // Payload "PONG" em ASCII (alem do command_id CMD_PONG) para permitir
    // conferencia visual em um terminal serial cru, sem parser de envelope
    // (task de teste manual da spec serial-protocol).
    const uint8_t body[4] = {'P', 'O', 'N', 'G'};
    sendPacket(CMD_PONG, body, sizeof(body));
}

void handleGetVersion() {
    const uint8_t body[4] = {
        FW_VERSION_MAJOR,
        FW_VERSION_MINOR,
        FW_VERSION_PATCH,
        SERIAL_PROTOCOL_VERSION,
    };
    sendPacket(CMD_VERSION_INFO, body, sizeof(body));
}

void handleGetActiveProfile() {
    uint8_t body[1 + sizeof(Profile::name)];
    body[0] = ProfileStore::getActiveProfileId();
    memcpy(body + 1, ProfileStore::getActiveProfile().name, sizeof(Profile::name));
    sendPacket(CMD_ACTIVE_PROFILE_INFO, body, sizeof(body));
}

void dispatch(const SerialPacket &packet) {
    switch (packet.command_id) {
        case CMD_PING:
            handlePing();
            break;
        case CMD_GET_VERSION:
            handleGetVersion();
            break;
        case CMD_GET_ACTIVE_PROFILE:
            handleGetActiveProfile();
            break;
        default:
            // Comando desconhecido nesta fase (comandos de feature sao
            // adicionados pelas specs correspondentes). Ignorado
            // silenciosamente para nao travar o parser.
            break;
    }
}

void resetParser() {
    state = ParseState::WAIT_PROTOCOL_VERSION;
    payloadIndex = 0;
}

} // namespace

void begin() {
    Serial.begin(SERIAL_BAUD_RATE);
    resetParser();
}

void poll() {
    while (Serial.available() > 0) {
        uint8_t b = (uint8_t)Serial.read();

        switch (state) {
            case ParseState::WAIT_PROTOCOL_VERSION:
                incoming.protocol_version = b;
                state = ParseState::WAIT_COMMAND_ID;
                break;

            case ParseState::WAIT_COMMAND_ID:
                incoming.command_id = b;
                state = ParseState::WAIT_LENGTH_LOW;
                break;

            case ParseState::WAIT_LENGTH_LOW:
                incoming.payload_length = b;
                state = ParseState::WAIT_LENGTH_HIGH;
                break;

            case ParseState::WAIT_LENGTH_HIGH:
                incoming.payload_length |= ((uint16_t)b << 8);
                payloadIndex = 0;
                if (incoming.payload_length == 0) {
                    dispatch(incoming);
                    resetParser();
                } else if (incoming.payload_length > SERIAL_PACKET_MAX_PAYLOAD) {
                    // Pacote maior que o suportado nesta fase: descarta e
                    // reinicia o parser em vez de travar esperando bytes
                    // que talvez nunca completem um payload valido.
                    resetParser();
                } else {
                    state = ParseState::WAIT_PAYLOAD;
                }
                break;

            case ParseState::WAIT_PAYLOAD:
                incoming.payload[payloadIndex++] = b;
                if (payloadIndex >= incoming.payload_length) {
                    dispatch(incoming);
                    resetParser();
                }
                break;
        }
    }
}

} // namespace SerialProtocol
