# feature-oled-status-display Specification

## Purpose
TBD - created by archiving change 0007-feature-oled-status-display. Update Purpose after archive.
## Requirements
### Requirement: Exibição do perfil ativo na tela OLED
No modelo Streamer, o firmware SHALL exibir o nome do perfil ativo na tela OLED sempre que houver troca
de perfil.

#### Scenario: Trocar perfil via encoder atualiza a tela
- **GIVEN** o device no perfil "OBS"
- **WHEN** o usuário gira o encoder para o próximo perfil ("Premiere")
- **THEN** a tela OLED atualiza para mostrar "Premiere" em menos de 200ms

