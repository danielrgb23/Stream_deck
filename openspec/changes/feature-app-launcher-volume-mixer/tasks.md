# Tasks: feature-app-launcher-volume-mixer

## 1. Firmware — encoder repaginado

- [ ] 1.1 Definir constantes dos 2 combos reservados de volume (subir/descer) em `ProfileManager.cpp`
- [ ] 1.2 `ROTATE_CW`/`ROTATE_CCW` passam a chamar `hid_.sendKey()` com o combo de volume, em vez de
      `switchToNextProfile()`/`switchToPreviousProfile()`
- [ ] 1.3 `PRESS` em `ENCODER_BUTTON_LOGICAL_ID` passa a chamar `switchToNextProfile()`
- [ ] 1.4 Validar compilação dos 3 envs (`pio run`)
- [ ] 1.5 Teste manual em hardware: girar o encoder emite o combo de volume (capturar via app residente
      ou log serial); clicar troca de perfil e atualiza o OLED (Streamer)

## 2. Modelo de dados (app desktop)

- [ ] 2.1 Adicionar campo opcional `app_path` em `KeyAction` (`protocol.py`), análogo a `named_action`
- [ ] 2.2 Adicionar campo opcional `volume_mixer_app` em `Profile` (`protocol.py`)
- [ ] 2.3 Definir a tabela de 8 combos reservados por posição de tecla (`app_launcher.py` novo módulo)
- [ ] 2.4 Atualizar `profile_store.py` (leitura/escrita dos dois campos novos no JSON local)
- [ ] 2.5 Atualizar `docs/desktop-profile-format.md` com os campos novos
- [ ] 2.6 Confirmar que `Profile.to_bytes()`/`from_bytes()` continuam ignorando os dois campos (wire
      format inalterado)

## 3. Enumeração de apps instalados

- [ ] 3.1 `installed_apps.py`: listar atalhos do Menu Iniciar no Windows (nome + caminho do `.lnk`)
- [ ] 3.2 `installed_apps.py`: listar pacotes `.app` em `/Applications` (+ `~/Applications`) no Mac
- [ ] 3.3 Função `open_app(path)` multiplataforma (`os.startfile` no Windows, `open -a`/`subprocess` no
      Mac)

## 4. Editor (UI)

- [ ] 4.1 Painel lateral com a lista de apps instalados (arrastável)
- [ ] 4.2 Suporte a drag-and-drop de um app para um `KeySlotWidget` → grava `app_path` + combo reservado
      daquela posição; UI mostra "Abrir app: <nome>" no lugar dos checkboxes/combo manual
- [ ] 4.3 Área de "app de volume" no editor de perfil, aceitando drag-and-drop → grava
      `volume_mixer_app`
- [ ] 4.4 Indicar visualmente quando rodando no Mac que volume por processo não está disponível
      (fallback sempre master)

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
