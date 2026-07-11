# Tasks: feature-target-os-shortcuts

## 1. Modelo de dados

- [ ] 1.1 Adicionar campo `target_os` (`WINDOWS` | `MAC`, default `WINDOWS`) por perfil em
      `profile_store.py` (leitura/escrita no JSON local)
- [ ] 1.2 Adicionar campo opcional `named_action` por tecla no JSON local (ausente/`null` = mapeamento
      manual)
- [ ] 1.3 Atualizar `docs/desktop-profile-format.md` com os dois campos novos

## 2. Biblioteca de ações nomeadas

- [ ] 2.1 Criar `desktop-app/xeeta_streamer_app/named_actions.py` com a tabela
      Copiar/Colar/Recortar/Desfazer/Refazer/Selecionar tudo/Salvar/Buscar/Fechar, `(modifiers, keycode)`
      por SO (ver tabela em `design.md`)
- [ ] 2.2 Função `resolve(action_name, target_os) -> KeyAction`

## 3. Editor (UI)

- [ ] 3.1 Adicionar seletor de `target_os` no editor de perfil (`main_window.py`/`editor_widget.py`)
- [ ] 3.2 Adicionar combo de "ação nomeada" em cada `KeySlotWidget`, ao lado dos checkboxes de
      modificador + combo de tecla manual existentes
- [ ] 3.3 Selecionar uma ação nomeada preenche modificadores + tecla e grava `named_action`; editar
      manualmente depois de novo limpa `named_action` (volta a ser mapeamento manual)
- [ ] 3.4 Trocar `target_os` do perfil re-resolve só as teclas com `named_action` preenchido

## 4. Validação

- [ ] 4.1 Teste: perfil Mac com "Copiar" na tecla 2 → `KeyAction` resolvida é `GUI+C`
- [ ] 4.2 Teste: mesmo perfil trocado para Windows → tecla 2 vira `CTRL+C`
- [ ] 4.3 Teste: tecla mapeada manualmente (sem `named_action`) não muda ao trocar `target_os`
- [ ] 4.4 Confirmar que nada disso muda o payload de `SET_PROFILE` nem exige mudança de firmware —
      o device sempre recebe só `modifiers`/`keycode` já resolvidos, como hoje
