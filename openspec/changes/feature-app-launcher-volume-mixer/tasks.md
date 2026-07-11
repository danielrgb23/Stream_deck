# Tasks: feature-app-launcher-volume-mixer

## 1. Firmware — encoder repaginado

- [x] 1.1 Definir constantes dos 2 combos reservados de volume (subir/descer) em `ProfileManager.cpp`
      (`src/core/ReservedVolumeCombo.h`)
- [x] 1.2 `ROTATE_CW`/`ROTATE_CCW` passam a chamar `hid_.sendKey()` com o combo de volume, em vez de
      `switchToNextProfile()`/`switchToPreviousProfile()`
- [x] 1.3 `PRESS` em `ENCODER_BUTTON_LOGICAL_ID` passa a chamar `switchToNextProfile()`
      (`ENCODER_BUTTON_LOGICAL_ID` movido para `hal/InputEvent.h` para não acoplar `ProfileManager` à
      implementação concreta `EncoderInput`)
- [x] 1.4 Validar compilação dos 3 envs (`pio run`)
- [x] 1.5 Teste manual em hardware real (ESP32 essential): clicar o encoder avança o perfil
      (`active=1→2→...→7` confirmado via `GET_ACTIVE_PROFILE` com log de debug); girar não altera mais o
      perfil; rotação tenta emitir o combo de volume via BLE HID (erros `notify() rc=-1` esperados —
      sem host BLE pareado nesta sessão de teste, não são falha de lógica)

## 2. Modelo de dados (app desktop)

- [x] 2.1 Adicionar campo opcional `app_path` em `KeyAction` (`protocol.py`), análogo a `named_action`
- [x] 2.2 Adicionar campo opcional `volume_mixer_app` em `Profile` (`protocol.py`)
- [x] 2.3 Definir a tabela de 8 combos reservados por posição de tecla (`app_launcher.py` novo módulo)
- [x] 2.4 Atualizar `profile_store.py` (leitura/escrita dos dois campos novos no JSON local)
- [x] 2.5 Atualizar `docs/desktop-profile-format.md` com os campos novos
- [x] 2.6 Confirmar que `Profile.to_bytes()`/`from_bytes()` continuam ignorando os dois campos (wire
      format inalterado) — coberto por teste automatizado

## 3. Enumeração de apps instalados

- [x] 3.1 `installed_apps.py`: listar atalhos do Menu Iniciar no Windows (nome + caminho do `.lnk`) —
      lógica implementada; não testável neste ambiente (sem Windows disponível)
- [x] 3.2 `installed_apps.py`: listar pacotes `.app` em `/Applications` (+ `~/Applications`) no Mac —
      testado neste Mac real (20 apps encontrados)
- [x] 3.3 Função `open_app(path)` multiplataforma (`os.startfile` no Windows, `open`/`subprocess` no
      Mac) — revisão de código apenas; não executado (evitar abrir um app de verdade durante o teste)

## 4. Editor (UI)

- [x] 4.1 Painel lateral com a lista de apps instalados (arrastável) — `installed_apps_panel.py`,
      integrado em `main_window.py`
- [x] 4.2 Suporte a drag-and-drop de um app para um `KeySlotWidget` → grava `app_path` + combo reservado
      daquela posição; UI mostra "Abrir app: <nome>" no lugar dos checkboxes/combo manual (via
      `QStackedWidget`)
- [x] 4.3 Área de "app de volume" no editor de perfil, aceitando drag-and-drop → grava
      `volume_mixer_app` (`VolumeAppDropArea`, clique direito remove)
- [x] 4.4 Indicar visualmente quando rodando no Mac que volume por processo não está disponível
      (fallback sempre master) — aviso fixo abaixo da área de app de volume quando `platform.system()
      == "Darwin"`

## 5. App residente (bandeja do sistema)

- [ ] 5.1 Ícone de bandeja (`QSystemTrayIcon`) com menu "Abrir"/"Sair"
- [ ] 5.2 Fechar a janela principal esconde em vez de encerrar o processo; só "Sair" encerra de verdade
- [ ] 5.3 Timer periódico (`DeviceWorker`) chamando `GET_ACTIVE_PROFILE` para saber o perfil ativo atual

## 6. Listener de atalho global + dispatch de ação

- [ ] 6.1 Adicionar dependência `pynput` (`requirements.txt`)
- [ ] 6.2 Registrar os 8 combos de tecla + 2 de volume como atalhos globais, numa thread própria
- [ ] 6.3 Handler "abrir app": resolve `app_path` da tecla no perfil ativo conhecido e chama
      `installed_apps.open_app()`
- [ ] 6.4 Handler "ajustar volume": resolve `volume_mixer_app` do perfil ativo conhecido, delega para o
      módulo de volume (task 7)

## 7. Volume por processo

- [ ] 7.1 Adicionar dependência `pycaw` (`requirements.txt`, só relevante no Windows)
- [ ] 7.2 `volume_control.py`: Windows — localizar sessão de áudio do processo vinculado via
      `AudioUtilities.GetAllSessions()`, ajustar via `ISimpleAudioVolume`; sem sessão encontrada → master
- [ ] 7.3 `volume_control.py`: Mac — sempre ajusta volume master (sem tentativa de volume por processo)
- [ ] 7.4 `volume_control.py`: fallback de volume master multiplataforma (o que usar quando não há
      `pycaw`/no Mac)

## 8. Validação

- [ ] 8.1 Teste: arrastar app para tecla → `app_path` + combo reservado corretos gravados no perfil local
- [ ] 8.2 Teste: arrastar app para perfil → `volume_mixer_app` gravado
- [ ] 8.3 Teste: fechar janela principal não derruba a conexão serial nem o listener de atalho global
- [ ] 8.4 Teste (Windows): girar o encoder com app de volume rodando ajusta só aquele processo
- [ ] 8.5 Teste (Windows): girar o encoder com app de volume vinculado mas fechado cai no master
- [ ] 8.6 Teste (Mac): girar o encoder sempre ajusta o master, UI indica a limitação
- [ ] 8.7 Confirmar que perfis salvos antes desta spec (sem `app_path`/`volume_mixer_app`) continuam
      carregando normalmente
