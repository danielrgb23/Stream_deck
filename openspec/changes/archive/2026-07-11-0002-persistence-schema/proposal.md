# Change: 0002-persistence-schema

## Why
Antes de qualquer feature gravar dados, precisamos decidir onde e como perfis são armazenados, para não
reescrever o formato depois que já existirem devices com dados gravados no campo.

## What Changes
- Define uso do NVS (Non-Volatile Storage) do ESP32 como armazenamento de perfil.
- Define schema de perfil versionado (`schema_version`).
- Define estratégia de cache RAM para proteger a flash de desgaste por escrita.
- Define formato de arquivo local do app desktop (JSON) enquanto não há necessidade de banco relacional.

## Impact
- Affected specs: `persistence-schema` (nova)
- Depende de: `build-scaffolding` (0001)
- Bloqueia: `profile-core` (0005) e todas as features que leem/gravam perfil
