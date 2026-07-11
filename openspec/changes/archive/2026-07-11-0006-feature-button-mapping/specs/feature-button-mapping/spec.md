# Spec Delta: feature-button-mapping

## ADDED Requirements

### Requirement: Mapeamento de tecla configurável via app
O usuário SHALL poder atribuir uma ação de teclado a cada tecla física através do app desktop, sem
recompilar o firmware.

#### Scenario: Usuário remapeia uma tecla
- **GIVEN** o app desktop conectado a um device via serial
- **WHEN** o usuário atribui a ação "Mute" à tecla física 1 e salva
- **THEN** o firmware persiste esse mapeamento e passa a emitir a ação correspondente ao pressionar a
  tecla 1
