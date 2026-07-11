# serial-protocol Specification

## Purpose
TBD - created by archiving change 0003-serial-protocol. Update Purpose after archive.
## Requirements
### Requirement: Protocolo serial versionado
O firmware SHALL implementar um protocolo de comunicação serial cujo primeiro campo de todo pacote seja
a versão do protocolo, permitindo evolução futura sem quebrar dispositivos já em campo.

#### Scenario: Identificar versão do firmware e protocolo
- **GIVEN** um device conectado via USB em 115200 baud
- **WHEN** o comando `GET_VERSION` é enviado
- **THEN** o device responde com a versão semântica do firmware e a versão do protocolo serial

### Requirement: Detecção de presença do device
O firmware SHALL responder a um comando `PING` com `PONG`, permitindo que o app desktop detecte a
presença do device sem depender de identificação por USB VID/PID.

#### Scenario: App desktop detecta o device
- **GIVEN** o device conectado a uma porta serial
- **WHEN** o app envia `PING`
- **THEN** o device responde `PONG` dentro de um timeout aceitável (ex: 200ms)

