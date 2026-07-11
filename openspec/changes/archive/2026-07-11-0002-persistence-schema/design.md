# Design: 0002-persistence-schema

## Device (firmware)
- Namespace NVS único: `xeeta_streamer`
- Chaves: `profile_<id>` (blob binário), `active_profile_id` (uint8), `schema_version` (uint8)
- Limite inicial: até 8 perfis por device (evita constante mágica espalhada pelo código — usar
  `MAX_PROFILES` centralizado)
- Serialização: struct binário fixo (não JSON) — parsing JSON custa RAM/CPU desnecessária num MCU

## Cache em RAM
- Perfil ativo vive inteiramente em RAM durante a operação
- NVS só é lido no boot e só é escrito em mudança explícita de configuração vinda do app desktop
- Troca de perfil via encoder/botão = só altera índice em RAM, nunca grava na flash

## App desktop (contrato de dados, implementação é feature futura)
- Fase inicial: arquivo JSON local (`~/.xeeta-streamer/profiles.json`)
- SQLite fica em aberto como evolução futura, não é decisão desta spec
