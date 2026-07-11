# Spec Delta: hal-interfaces

## ADDED Requirements

### Requirement: Abstração de hardware de entrada e saída
O firmware SHALL expor uma interface `InputSource` e uma interface `DisplayDriver` das quais toda lógica
de perfil/HID depende, sem referenciar diretamente nenhum componente de hardware concreto.

#### Scenario: Trocar modelo sem alterar o core
- **GIVEN** o firmware compilado para o modelo Streamer
- **WHEN** o firmware é recompilado com `DEVICE_MODEL=CREATOR_PRO`
- **THEN** o código de `ProfileManager` e HID (spec `profile-core`) permanece inalterado; apenas as
  implementações concretas de `InputSource`/`DisplayDriver` mudam
