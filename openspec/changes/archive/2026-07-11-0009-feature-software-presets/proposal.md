# Change: 0009-feature-software-presets (BLOQUEADA por 0006, 0008)

## Why
Diferencial comercial discutido nas conversas anteriores: vender perfis pré-configurados (OBS, Premiere,
DaVinci, Home Office, Home Assistant) como pacotes prontos, poupando o tempo de configuração do cliente.

## What Changes
- Define formato de "pacote de perfil" (JSON com metadados: nome, software-alvo, mapeamento default).
- App desktop permite importar um pacote pronto e aplicá-lo a um perfil vazio.
- Biblioteca inicial de pacotes: OBS, Premiere/DaVinci, Home Office (Zoom/Teams/Slack), Home Assistant.

## Impact
- Depende de: 0006 (feature-button-mapping), 0008 (feature-desktop-app-sync)
- É a feature mais próxima do que vira valor comercial direto (mencionado como upsell na conversa sobre
  precificação)
