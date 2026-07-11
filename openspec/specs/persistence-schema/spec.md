# persistence-schema Specification

## Purpose
TBD - created by archiving change 0002-persistence-schema. Update Purpose after archive.
## Requirements
### Requirement: Perfil ativo em cache de RAM
O firmware SHALL manter o perfil ativo inteiramente em RAM durante a operação normal, e SHALL NOT
escrever no NVS a cada troca de perfil.

#### Scenario: Trocar de perfil sem desgastar a flash
- **GIVEN** um device ligado com um perfil ativo carregado em RAM
- **WHEN** o usuário troca de perfil via encoder
- **THEN** apenas o índice em RAM é atualizado, sem operação de escrita no NVS

### Requirement: Schema de perfil versionado
Todo perfil persistido SHALL conter um campo `schema_version`, permitindo migração de dados em versões
futuras do firmware sem invalidar perfis já gravados em devices no campo.

#### Scenario: Firmware novo lê perfil de schema antigo
- **GIVEN** um perfil gravado no NVS com `schema_version = 1`
- **WHEN** um firmware que já suporta `schema_version = 2` inicializa
- **THEN** o firmware verifica a versão antes de desserializar, evitando leitura incorreta de campos

