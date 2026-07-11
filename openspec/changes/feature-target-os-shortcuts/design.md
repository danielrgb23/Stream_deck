## Context

Hoje o editor de perfil (`desktop-app/xeeta_streamer_app/editor_widget.py`) só monta uma `KeyAction`
(`modifiers` + `keycode`) a partir de checkboxes de modificador brutos + um combo de tecla
(`keycodes.py`). Não existe noção de "para qual sistema operacional este perfil é". O firmware
(`ProfileManager`/`HidTransport`) já é e continua agnóstico disso — só emite o `modifiers`/`keycode` que
o perfil tem, seja qual for a origem. Toda a mudança desta spec é no app desktop.

## Goals / Non-Goals

**Goals:**
- Permitir marcar um perfil como destinado a Windows ou Mac.
- Oferecer uma lista de ações comuns (Copiar, Colar, etc.) que já resolvem para o modificador certo.
- Preservar mapeamentos manuais existentes ao trocar o SO-alvo de um perfil.

**Non-Goals:**
- Não inclui detecção automática do SO do computador conectado (isso exigiria o firmware/app saberem
  algo sobre o host, que não é informação disponível hoje via HID) — a escolha é manual, por perfil.
- Não cobre atalhos específicos de aplicativo (esses continuam sendo o papel de
  `feature-software-presets`); esta spec é só sobre o conjunto pequeno de ações universais do SO.
- Não muda o protocolo serial nem o schema de perfil do firmware.

## Decisions

### Onde mora o `target_os`
Fica só no JSON local do app (`profile_store.py` / `docs/desktop-profile-format.md`), como um campo novo
por perfil. Alternativa considerada: mandar o `target_os` para o firmware junto do perfil. Rejeitada —
o firmware não precisa saber disso, já recebe o resultado final resolvido; adicionar o campo lá
significaria bump de `schema_version` (spec `persistence-schema`) para algo que só o app usa.

### Tabela de ações nomeadas: por SO, não "swap de modificador" genérico
Cada ação nomeada mapeia explicitamente para `(modifiers, keycode)` por SO, em vez de uma regra genérica
"troca CTRL por GUI". Motivo: a maioria das ações troca só o modificador principal (Copiar = Ctrl+C /
Cmd+C), mas "Refazer" não — Windows usa `Ctrl+Y`, Mac usa `Cmd+Shift+Z`. Uma regra de swap genérica
acertaria a maioria e erraria essa. Tabela por SO evita esse tipo de exceção silenciosa.

| Ação            | Windows           | Mac                  |
|-----------------|-------------------|----------------------|
| Copiar          | Ctrl+C            | Cmd+C                |
| Colar           | Ctrl+V            | Cmd+V                |
| Recortar        | Ctrl+X            | Cmd+X                |
| Desfazer        | Ctrl+Z            | Cmd+Z                |
| Refazer         | Ctrl+Y            | Cmd+Shift+Z          |
| Selecionar tudo | Ctrl+A            | Cmd+A                |
| Salvar          | Ctrl+S            | Cmd+S                |
| Buscar          | Ctrl+F            | Cmd+F                |
| Fechar          | Ctrl+W            | Cmd+W                |

### Rastrear "esta tecla veio de uma ação nomeada" para não sobrescrever edição manual
Cada entrada de tecla no JSON local ganha um campo opcional `named_action` (nome da ação, ex: `"COPY"`,
ou ausente/`null` se foi montada manualmente). Ao trocar `target_os`, o app re-resolve só as teclas com
`named_action` preenchido; teclas sem esse campo (editadas manualmente) ficam como estão. Alternativa
considerada: não rastrear nada e sempre perguntar ao usuário se quer re-resolver tudo — mais simples de
implementar, mas cria risco de sobrescrever silenciosamente uma escolha manual do usuário que por acaso
bate com os mesmos bytes de uma ação nomeada; rastrear explicitamente evita ambiguidade.

### UI: ação nomeada como atalho para preencher os campos manuais, não um modo separado
Selecionar uma ação nomeada no editor preenche os checkboxes de modificador + combo de tecla existentes
(e grava `named_action`); o usuário ainda pode editar manualmente depois — nesse caso `named_action` é
limpo (a tecla volta a ser tratada como manual). Não é um tipo de dado paralelo à `KeyAction` existente,
é só uma forma mais rápida de preenchê-la.

## Risks / Trade-offs

- [Risco] Tabela de ações fixa no código (`named_actions.py`) — adicionar uma ação nova exige editar
  código, não é dado configurável em runtime. → Mitigação: aceitável para o conjunto pequeno e estável
  de ações universais de SO; ações específicas de app continuam vindo de presets (JSON, já
  configurável).
- [Risco] Usuário edita manualmente uma tecla para os *mesmos* bytes que uma ação nomeada já geraria —
  `named_action` é limpo mesmo assim (edição manual sempre limpa o campo, não há tentativa de
  "detectar" que os bytes coincidem). → Aceitável: resultado funcional é idêntico, só perde o
  auto-resolve numa futura troca de SO, que o usuário pode refazer com um clique.

## Migration Plan

Perfis locais já salvos sem `target_os` são tratados como `target_os = WINDOWS` (default) na leitura —
não é uma migração destrutiva, só um valor default para um campo novo. Nenhum dado existente é reescrito
até o usuário salvar o perfil de novo.

## Open Questions

- Vale expor mais ações (ex: Zoom in/out, capturas de tela) nesta mesma spec ou deixar para uma
  biblioteca de presets futura? Mantido como está por ora — o conjunto acima cobre o pedido original
  (Copiar/Colar/etc.); expandir a tabela depois é uma mudança aditiva simples, não exige nova spec.
