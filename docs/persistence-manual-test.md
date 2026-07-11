# Teste manual: zero escritas no NVS ao trocar de perfil (spec persistence-schema, task 2.7)

`ProfileStore::nvsWriteCount()` (`src/core/ProfileStore.h`) conta apenas chamadas a `saveProfile()` —
a única função que grava no NVS. `setActiveProfile()` (troca de perfil) nunca a chama.

Não há hardware físico disponível neste ambiente para rodar o teste fim-a-fim; o procedimento com um
device real é:

1. Adicionar temporariamente, no `loop()` do modelo em teste (`src/models/<modelo>/main.cpp`), um log
   a cada troca de perfil:
   ```cpp
   Serial.printf("active=%u writes=%u\n", ProfileStore::getActiveProfileId(), ProfileStore::nvsWriteCount());
   ```
2. Flashar o device e trocar de perfil 50x via encoder (Streamer) ou pelo mecanismo de troca do
   Essential.
3. Confirmar no monitor serial que `writes` permanece `0` durante toda a sequência — só deve subir se
   `saveProfile()` for chamado explicitamente (comando de configuração vindo do app desktop, fora do
   escopo desta spec de fundação).
4. Remover o log de depuração antes de mergear (não faz parte do contrato de produto).
