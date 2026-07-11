# Formato do arquivo local de perfis do app desktop

Definido pela spec `persistence-schema` (0002). O app desktop ainda não existe (feature bloqueada,
ver `feature-desktop-app-sync` 0008) — este documento só fixa o contrato de dados com antecedência,
para que o formato não precise ser inventado no meio da implementação do app.

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
      "keys": [
        { "modifiers": ["CTRL"], "keycode": 60 },
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
- `profiles[].keys` — um item por tecla física (`MAX_KEYS_PER_PROFILE`, hoje 8), na mesma ordem do
  array `keys` do struct `Profile` do firmware:
  - `modifiers` — lista de zero ou mais de `"CTRL"`, `"SHIFT"`, `"ALT"`, `"GUI"` (nomes legíveis no app;
    o firmware usa o bitmask `MOD_CTRL|MOD_SHIFT|MOD_ALT|MOD_GUI` de `src/core/Profile.h`).
  - `keycode` — usage ID de teclado HID; `0` significa tecla não mapeada.

## Sincronização com o device

Este arquivo é a cópia local; a cópia autoritativa em runtime é a cache RAM do firmware (spec
`persistence-schema`). O app grava neste arquivo e envia o mesmo conteúdo ao device via `SET_PROFILE`
(protocolo serial, comando de feature definido em `feature-button-mapping` / `feature-desktop-app-sync`,
não em `serial-protocol` que só fixa o envelope).
