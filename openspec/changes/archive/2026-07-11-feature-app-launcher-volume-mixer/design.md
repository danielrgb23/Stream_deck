## Context

Hoje toda ação de tecla vira um `KeyAction` (`modifiers` + `keycode`) que o firmware emite via
`HidTransport` (teclado USB ou BLE). O app desktop só existe enquanto a janela está aberta; ao fechar,
a conexão serial cai. O encoder rotaciona → troca de perfil (no firmware, `ProfileManager`); o clique do
encoder não tem ação (`ProfileManager::resolveKey` ignora ids fora de `0..MAX_KEYS_PER_PROFILE-1`).

Esta spec precisa de duas capacidades que o device sozinho não tem: abrir um programa e ler/setar volume
de um processo especifico — nenhuma das duas é algo que se faz com uma tecla de teclado. As decisões
abaixo foram tomadas em conversa direta com o usuário (ver seção final "Decisões confirmadas com o
usuário").

## Goals / Non-Goals

**Goals:**
- Tecla física → abrir um app instalado (por perfil).
- Encoder rotativo → subir/descer volume do app vinculado ao perfil ativo (ou master, sem vínculo).
- Encoder clique → trocar de perfil.
- App desktop funcionando em segundo plano (bandeja do sistema), sem depender da janela principal
  aberta.
- Zero mudança no envelope do protocolo serial ou no schema binário de `Profile`.

**Non-Goals:**
- Não inclui um mixer de volume completo (sliders para todos os apps rodando) — só o vínculo simples
  "este perfil controla o volume deste app".
- Não inclui ícones dos apps instalados nesta primeira versão (só nome + caminho executável) — fica
  como possível melhoria futura, não bloqueia a feature.
- Não tenta resolver volume por app no Mac via nenhum workaround (ex: instalar um driver de áudio
  virtual de terceiros) — isso é uma feature bem maior e separada, fora de escopo aqui.

## Decisions

### Mecanismo de disparo: combo HID reservado + hotkey global no app (não novo canal serial)
Ver "Decisões confirmadas com o usuário" — resumo: o device sinaliza "abrir app na tecla N" ou "subir/
descer volume" emitindo um combo de teclado raro e fixo via `HidTransport`, exatamente como qualquer
outra tecla hoje. O app desktop residente registra esses combos como atalhos globais do SO (lib
`pynput`) e, ao detectar um, resolve localmente o que fazer (abrir tal app, ajustar volume de tal
processo) consultando o perfil ativo conhecido localmente.

Alternativa considerada e rejeitada: estender o protocolo serial para o firmware empurrar eventos de
tecla em tempo real. Rejeitada por exigir manter a porta serial sempre aberta em background (conflita
com abrir o editor de configuração ao mesmo tempo, já que a maioria dos SOs só permite um processo por
vez segurando a porta) e por mudar `SerialProtocol.cpp`/`ProfileManager.cpp` do firmware sem necessidade
— o mecanismo de combo reservado resolve o problema reaproveitando 100% da infraestrutura de
`HidTransport` já implementada.

### Tabela de combos reservados
Faixa `Ctrl+Alt+Shift+F13` até `F24` (12 combos disponíveis, modificadores + tecla praticamente nunca
usados por nenhum outro programa):

| Combo                        | Significado                                  |
|-------------------------------|-----------------------------------------------|
| `Ctrl+Alt+Shift+F13`          | Ação "abrir app" da tecla física 1            |
| `Ctrl+Alt+Shift+F14`          | Ação "abrir app" da tecla física 2            |
| ...                           | (uma por tecla física, até `MAX_KEYS_PER_PROFILE`) |
| `Ctrl+Alt+Shift+F20`          | Ação "abrir app" da tecla física 8            |
| `Ctrl+Alt+Shift+F21`          | Volume: subir (encoder rotação horária)       |
| `Ctrl+Alt+Shift+F22`          | Volume: descer (encoder rotação anti-horária) |

Os 8 primeiros combos (por tecla) são valores possíveis de `KeyAction.modifiers`/`keycode` gravados no
perfil via `SET_PROFILE`, exatamente como qualquer outro mapeamento manual — o firmware não sabe nem
precisa saber que aquele combo específico "significa abrir app", ele só emite o que o perfil manda,
como sempre fez. Os 2 combos de volume são constantes fixas no firmware (`ProfileManager.cpp`), emitidas
diretamente na rotação do encoder — não fazem parte do array `keys[]` do perfil, porque rotação nunca
foi (e continua não sendo) uma "tecla lógica" configurável por posição.

### Encoder: rotação = volume, clique = troca de perfil
Troca de comportamento em `ProfileManager::handleEvent` (`src/core/ProfileManager.cpp`):
- `ROTATE_CW` → `hid_.sendKey(VOLUME_UP_COMBO)` (em vez de `switchToNextProfile()`)
- `ROTATE_CCW` → `hid_.sendKey(VOLUME_DOWN_COMBO)` (em vez de `switchToPreviousProfile()`)
- `PRESS` com `logicalId == ENCODER_BUTTON_LOGICAL_ID` → `switchToNextProfile()` (a lógica que já existe,
  só muda de gatilho — clique sempre avança para o próximo perfil, sem direção "anterior" via clique;
  se precisar de "anterior" no futuro, dá pra usar clique-longo, mas isso fica para uma iteração futura)
- `RELEASE` do botão do encoder continua sem ação, como hoje

O restante do `ProfileManager` (resolução de `KeyAction` para teclas físicas normais, troca de display)
não muda.

### Modelo de dados: dois campos novos, só no lado do app
- Por **tecla** (dentro de `KeyAction`, análogo a `named_action` de `target-os-shortcuts`): campo opcional
  `app_path` (caminho do executável). Quando presente, o editor mostra a tecla como "abrir app: <nome>"
  em vez dos checkboxes de modificador, e o `modifiers`/`keycode` gravado é o combo reservado daquela
  posição de tecla (tabela acima) — resolvido automaticamente pelo editor, o usuário nunca escolhe esse
  combo manualmente.
- Por **perfil**: campo opcional `volume_mixer_app` (caminho ou nome de processo do app cujo volume o
  encoder controla enquanto esse perfil estiver ativo). Ausente/`null` = volume master.

Ambos os campos são metadado só do JSON local (`profile_store.py`) — nunca vão para o firmware.
`Profile.to_bytes()`/`from_bytes()` não mudam.

### App residente: bandeja do sistema + polling do perfil ativo
`QSystemTrayIcon` (PyQt6) com menu "Abrir", "Sair". Fechar a janela principal (`X`) esconde em vez de
encerrar o processo; só "Sair" no menu da bandeja encerra de verdade. O `DeviceWorker` (já existe,
roda numa `QThread` separada) ganha um timer periódico (ex: a cada 1s) chamando `GET_ACTIVE_PROFILE`
(comando já existente, spec `profile-core`) para saber qual perfil está ativo — é assim que o app sabe
qual `volume_mixer_app`/quais `app_path` valem no momento, sem precisar de nenhum comando novo no
protocolo serial. O listener de atalho global (`pynput`) roda em sua própria thread, disparando os
handlers de "abrir app"/"ajustar volume" quando detecta um dos combos reservados.

### Volume por processo: pycaw no Windows, master no Mac
Windows: `pycaw.pycaw.AudioUtilities.GetAllSessions()`, localizar a sessão cujo processo bate com
`volume_mixer_app`, ajustar via `ISimpleAudioVolume.SetMasterVolume()` em passos (ex: ±5% por detent do
encoder). Sem sessão encontrada (app não está rodando) → cai no volume master do sistema.

Mac: **não existe** API pública da Apple equivalente a `ISimpleAudioVolume` — Core Audio só expõe
volume master/por dispositivo, não por processo. Confirmado com o usuário: no Mac o ajuste sempre atua
no volume master, independente de `volume_mixer_app` estar preenchido ou não. Documentar isso
claramente na UI (ex: campo desabilitado ou aviso quando o app roda no Mac).

### Enumeração de apps instalados
Windows: listar atalhos (`.lnk`) em `%ProgramData%\Microsoft\Windows\Start Menu\Programs` e
`%AppData%\Microsoft\Windows\Start Menu\Programs` (nome do atalho = nome exibido; abrir via
`os.startfile()` resolve o `.lnk` sozinho, sem precisar de lib extra para ler o destino real).
Mac: listar pacotes `.app` em `/Applications` (e `~/Applications` se existir).
Sem ícone nesta versão (Non-Goal) — só nome + caminho, numa lista arrastável no editor.

## Risks / Trade-offs

- [Risco] Combo reservado colidir com um atalho já usado por outro programa do usuário (ex: alguém já
  usa `Ctrl+Alt+Shift+F16` pra outra coisa). → Mitigação: faixa escolhida é extremamente incomum;
  aceitável para v1. Se colidir, o usuário percebe rápido (a ação não dispara ou dispara a coisa
  errada) e pode reportar — não há como eliminar 100% o risco de colisão com atalho de terceiros sem
  inventar um canal fora do teclado (rejeitado acima).
- [Risco] `pynput` exige permissão de Acessibilidade no Mac para monitorar teclado globalmente (como
  Alfred/BetterTouchTool). → Mitigação: documentar isso no README do app desktop; sem essa permissão,
  as ações de app-launcher/volume simplesmente não disparam (atalhos normais continuam funcionando
  normalmente, já que esses não dependem do listener global).
- [Risco] Perfil sem app vinculado ao volume, mas usuário gira o encoder — comportamento deve ser volume
  master, não erro/travamento. → Mitigação: fallback explícito no handler, coberto nos cenários da spec.
- [Risco] Polling de `GET_ACTIVE_PROFILE` a cada 1s consome ciclos de CPU/bateria do host enquanto o
  device está conectado. → Aceitável para v1 (intervalo de 1s é barato); pode virar configurável depois
  se necessário.

## Migration Plan

Perfis locais já salvos sem `app_path`/`volume_mixer_app` continuam válidos — ambos os campos são
opcionais, ausência = comportamento de hoje (tecla mapeada normalmente / volume sempre master). Nenhuma
migração destrutiva.

## Decisões confirmadas com o usuário

- Mecanismo de disparo: combo HID reservado + hotkey global no app residente (não um novo canal serial
  em tempo real) — ver seção "Mecanismo de disparo" acima.
- Volume por processo: implementado de verdade no Windows (pycaw); no Mac cai sempre no volume master,
  documentado como limitação de plataforma (Apple não expõe API pública equivalente).
- Papéis do encoder trocados: rotação agora é volume, clique agora é troca de perfil (antes era o
  contrário — rotação trocava perfil, clique não fazia nada).

## Open Questions

- Vale um clique-longo do encoder para "perfil anterior" (hoje só avança)? Deixado de fora desta
  primeira versão — adicionar depois é aditivo, não exige mudança nesta spec.
