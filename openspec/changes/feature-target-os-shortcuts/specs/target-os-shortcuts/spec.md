# Spec Delta: target-os-shortcuts

## ADDED Requirements

### Requirement: Seleção de sistema operacional alvo por perfil
O app desktop SHALL permitir definir um `target_os` (`WINDOWS` ou `MAC`) por perfil, persistido apenas
no arquivo JSON local (spec `persistence-schema`) — o firmware não recebe nem armazena esse campo, só o
`modificador + keycode` já resolvido, como já ocorre hoje.

#### Scenario: Definir um perfil como Mac
- **GIVEN** um perfil sendo editado no app desktop
- **WHEN** o usuário seleciona "Mac" como sistema-alvo do perfil
- **THEN** o app salva `target_os = MAC` no arquivo JSON local do perfil

### Requirement: Ações nomeadas multiplataforma resolvidas pelo SO-alvo
O app desktop SHALL oferecer uma biblioteca de ações nomeadas (Copiar, Colar, Recortar, Desfazer,
Refazer, Selecionar Tudo, Salvar, Buscar) que resolvem para o modificador `CTRL` quando o perfil tem
`target_os = WINDOWS` e para o modificador `GUI` quando `target_os = MAC`, antes de montar a `KeyAction`
enviada ao device.

#### Scenario: Atribuir "Copiar" a uma tecla em perfil Mac
- **GIVEN** um perfil com `target_os = MAC`
- **WHEN** o usuário atribui a ação nomeada "Copiar" à tecla física 2
- **THEN** o app resolve a ação para `GUI+C` (equivalente a Cmd+C no Mac) como a `KeyAction` daquela
  tecla, enviada ao device via `SET_PROFILE`

#### Scenario: Mesma ação nomeada em perfil Windows
- **GIVEN** um perfil com `target_os = WINDOWS`
- **WHEN** o usuário atribui a ação nomeada "Copiar" à mesma tecla física
- **THEN** o app resolve a ação para `CTRL+C` (equivalente a Ctrl+C no Windows) como a `KeyAction`
  daquela tecla

### Requirement: Trocar o SO-alvo não sobrescreve mapeamento manual existente
Ao mudar o `target_os` de um perfil já configurado, o app SHALL re-resolver apenas as teclas atribuídas
através de uma ação nomeada — teclas configuradas manualmente com modificador bruto (não via ação
nomeada) SHALL permanecer inalteradas.

#### Scenario: Mudar de Windows para Mac com mapeamento manual existente
- **GIVEN** um perfil `target_os = WINDOWS` com a tecla física 3 mapeada manualmente para `ALT+F4`
  (não através de uma ação nomeada)
- **WHEN** o usuário muda o `target_os` do perfil para `MAC`
- **THEN** a tecla física 3 permanece `ALT+F4`, sem alteração automática
