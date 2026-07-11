# Change: 0001-build-scaffolding

## Why
Sem uma estrutura de projeto e convenção de build definida, cada modelo (Essential/Streamer/Creator Pro)
tende a virar um projeto separado ao invés de um único core com variantes. Esta é a primeira spec porque
todas as outras (persistência, protocolo, HAL, core) precisam de um lugar e uma convenção para existir.

## What Changes
- Cria projeto PlatformIO com um `env` por modelo.
- Define a flag `DEVICE_MODEL` (`ESSENTIAL` | `STREAMER` | `CREATOR_PRO`).
- Define convenção de versionamento semântico do firmware (`MAJOR.MINOR.PATCH`).
- Define estrutura de pastas do repositório (core/, hal/, models/, lib/).

## Impact
- Affected specs: `build-scaffolding` (nova)
- Nenhum código de feature ainda. Bloqueia todas as demais specs de fundação.
