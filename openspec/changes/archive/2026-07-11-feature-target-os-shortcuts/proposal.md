# Change: feature-target-os-shortcuts

## Why
O editor de perfil hoje só monta uma tecla a partir de modificadores brutos (`CTRL`/`SHIFT`/`ALT`/`GUI`)
+ uma tecla — o usuário precisa saber que "Cmd" no Mac é o mesmo bit `GUI` que a tecla Windows no PC, e
precisa reconfigurar manualmente cada perfil se usar o mesmo device em mais de um sistema operacional.
Não existe hoje um jeito de dizer "este perfil é para Mac" e ter atalhos comuns (Copiar, Colar, etc.)
resolvidos automaticamente para o modificador certo.

## What Changes
- App desktop: adiciona campo `target_os` por perfil (`WINDOWS` | `MAC`), guardado só no arquivo JSON
  local (spec `persistence-schema` não muda — o firmware continua recebendo somente
  `modificador + keycode` já resolvidos, como hoje).
- App desktop: biblioteca de ações nomeadas comuns e multiplataforma (Copiar, Colar, Recortar, Desfazer,
  Refazer, Selecionar Tudo, Salvar, Buscar, Fechar Janela/Aba) que resolvem para o modificador correto
  conforme o `target_os` do perfil (`CTRL` no Windows, `GUI` no Mac — mesmo bit que já existe em
  `src/core/Profile.h`, só a origem da escolha muda).
- Editor do app: permite escolher o SO-alvo do perfil e escolher uma ação nomeada da lista, em vez de
  montar manualmente modificador + tecla toda vez.
- Nenhuma mudança no firmware nem no protocolo serial — o app resolve a ação nomeada para bytes de
  modificador + keycode antes de enviar via `SET_PROFILE`, exatamente como já faz hoje para mapeamentos
  manuais.

## Capabilities

### New Capabilities
- `target-os-shortcuts`: seleção de sistema operacional alvo por perfil e biblioteca de ações nomeadas
  multiplataforma (Copiar/Colar/Recortar/etc.) resolvidas para o modificador correto conforme o alvo.

### Modified Capabilities
(nenhuma — aditivo; não muda requisitos de `feature-button-mapping` nem `feature-desktop-app-sync`,
só estende o editor que essas specs já definem)

## Impact
- Depende de: `feature-button-mapping` (mapeamento de tecla), `feature-desktop-app-sync` (app/editor)
- Afeta: `desktop-app/xeeta_streamer_app/` (novo módulo de ações nomeadas, campo `target_os` no editor e
  em `profile_store.py`), `docs/desktop-profile-format.md` (novo campo no JSON local)
- Não afeta: firmware (`src/`), protocolo serial (envelope/comandos inalterados — perfil continua
  chegando ao device já resolvido em `modificador + keycode`)
