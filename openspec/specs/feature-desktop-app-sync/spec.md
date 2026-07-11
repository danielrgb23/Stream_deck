# feature-desktop-app-sync Specification

## Purpose
TBD - created by archiving change 0008-feature-desktop-app-sync. Update Purpose after archive.
## Requirements
### Requirement: Detecção automática do device
O app desktop SHALL detectar a presença de um device Xeeta Streamer conectado via USB, usando o comando
`PING` do protocolo serial, sem depender de driver adicional.

#### Scenario: Conectar o device com o app aberto
- **GIVEN** o app desktop aberto e nenhum device conectado
- **WHEN** o usuário conecta o device via USB
- **THEN** o app detecta o device em até 3 segundos e exibe seu nome/modelo

### Requirement: Edição de perfil sincronizada com o device
O app SHALL permitir editar o mapeamento de teclas de um perfil e sincronizar essa alteração com o
device conectado.

#### Scenario: Salvar alteração de perfil
- **GIVEN** o usuário editou o mapeamento da tecla 2 no app
- **WHEN** o usuário clica em "Salvar"
- **THEN** o app envia o perfil atualizado ao device via `SET_PROFILE` e persiste localmente em JSON

