# Formato do arquivo local de perfis do app desktop

Definido pela spec `persistence-schema`, usado pelo módulo `desktop-app/xeeta_streamer_app/profile_store.py`
(specs `feature-desktop-app-sync`, `target-os-shortcuts` e `app-launcher-volume-mixer`).

## Localização

```
~/.xeeta-streamer/profiles.json
```

Um arquivo por usuário, cobrindo todos os devices já configurados nessa máquina (fase inicial, sem
banco relacional — ver design de 0002). SQLite fica em aberto como evolução futura.

## Schema

```json
{
  "schema_version": 1,
  "profiles": [
    {
      "id": 0,
      "name": "OBS",
      "target_os": "MAC",
      "volume_mixer_app": "Discord",
      "keys": [
        { "modifiers": ["GUI"], "keycode": 99, "named_action": "COPY" },
        { "modifiers": ["CTRL", "ALT", "SHIFT"], "keycode": 240, "app_path": "/Applications/Spotify.app" },
        { "modifiers": [], "keycode": 0 }
      ]
    }
  ]
}
```

- `schema_version` — espelha o mesmo conceito do `schema_version` do firmware (spec `persistence-schema`);
  permite migração do arquivo local sem invalidar perfis já salvos por usuários.
- `profiles[].id` — índice do perfil no device (`0..MAX_PROFILES-1`, hoje `MAX_PROFILES = 8`,
  ver `src/core/Profile.h`).
- `profiles[].name` — mesmo campo `name` do struct binário `Profile` do firmware (até 15 caracteres +
  terminador nulo — `char name[16]`).
- `profiles[].target_os` — `"WINDOWS"` ou `"MAC"` (spec `target-os-shortcuts`). Ausente em arquivos
  salvos antes dessa spec — nesse caso o app assume `"WINDOWS"` na leitura (`DEFAULT_TARGET_OS`), sem
  reescrever nada até o usuário salvar o perfil de novo. **Só existe neste arquivo local — o firmware
  nunca recebe nem armazena este campo.**
- `profiles[].volume_mixer_app` (opcional, spec `app-launcher-volume-mixer`) — caminho (Windows) ou nome
  de processo (Mac) do app cujo volume o encoder ajusta enquanto este perfil estiver ativo. Ausente =
  volume master do sistema. **Só existe neste arquivo local**; no Mac este campo é sempre ignorado no
  ajuste real (Apple não expõe API pública de volume por processo — ver `volume_control.py`).
- `profiles[].keys` — um item por tecla física (`MAX_KEYS_PER_PROFILE`, hoje 8), na mesma ordem do
  array `keys` do struct `Profile` do firmware:
  - `modifiers` — lista de zero ou mais de `"CTRL"`, `"SHIFT"`, `"ALT"`, `"GUI"` (nomes legíveis no app;
    o firmware usa o bitmask `MOD_CTRL|MOD_SHIFT|MOD_ALT|MOD_GUI` de `src/core/Profile.h`).
  - `keycode` — segue a convenção da biblioteca Arduino Keyboard (ver `keycodes.py`), não o usage ID cru
    da tabela USB HID; `0` significa tecla não mapeada.
  - `named_action` (opcional, spec `target-os-shortcuts`) — nome da ação nomeada que gerou este
    `modifiers`/`keycode` (ex: `"COPY"`, ver `named_actions.py`). Ausente/omitido quando a tecla foi
    mapeada manualmente no editor. Usado só para saber quais teclas re-resolver ao trocar `target_os` —
    **também não vai para o firmware**, é metadado só do app.
  - `app_path` (opcional, spec `app-launcher-volume-mixer`) — caminho do executável que esta tecla abre.
    Quando presente, `modifiers`/`keycode` é sempre o combo reservado daquela posição de tecla
    (`Ctrl+Alt+Shift+F13` a `F20`, ver `app_launcher.py`) — o app residente detecta esse combo via
    atalho global do SO e abre este app. **Também não vai para o firmware** como conceito — o que chega
    via `SET_PROFILE` é só o combo reservado, indistinguível de qualquer outro mapeamento manual.

## Sincronização com o device

Este arquivo é a cópia local; a cópia autoritativa em runtime é a cache RAM do firmware (spec
`persistence-schema`). O app grava neste arquivo e envia o mesmo conteúdo ao device via `SET_PROFILE`
(protocolo serial, comando de feature definido em `feature-button-mapping` / `feature-desktop-app-sync`,
não em `serial-protocol` que só fixa o envelope).
