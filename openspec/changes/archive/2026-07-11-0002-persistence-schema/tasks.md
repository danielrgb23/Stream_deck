# Tasks: 0002-persistence-schema

- [x] 2.1 Definir namespace e chaves do NVS
- [x] 2.2 Implementar struct binário de perfil com campo `schema_version`
- [x] 2.3 Implementar leitura de perfis no boot
- [x] 2.4 Implementar escrita no NVS apenas via comando explícito (não em troca de perfil)
- [x] 2.5 Implementar cache RAM do perfil ativo
- [x] 2.6 Documentar formato do JSON local do app desktop (mesmo sem app implementado ainda)
- [x] 2.7 Teste: trocar perfil 50x via encoder e confirmar zero escritas no NVS (log/contador) —
      contador (`ProfileStore::nvsWriteCount()`) implementado e procedimento documentado em
      `docs/persistence-manual-test.md`; execução em hardware real não foi possível neste ambiente
      (sem device físico disponível)
