#pragma once

#include <stdint.h>
#include "core/Profile.h"

// ProfileStore e a unica peca do firmware que fala com o NVS (Preferences).
// ProfileManager (spec profile-core) so enxerga esta interface — nunca
// chama Preferences diretamente.
//
// Contrato (spec persistence-schema):
// - begin() le todos os perfis e o active_id do NVS UMA vez, no boot.
// - setActiveProfile() troca o indice ativo em RAM e NAO grava no NVS.
// - saveProfile() e a UNICA operacao que grava um perfil no NVS, e so deve
//   ser chamada por uma mudanca explicita de configuracao (ex: comando
//   SET_PROFILE vindo do app desktop), nunca por uma troca de perfil.
namespace ProfileStore {

// Le todos os perfis e o profile ativo do NVS para a cache em RAM.
// Deve ser chamado uma vez, no boot.
void begin();

// Retorna o id (0..MAX_PROFILES-1) do perfil ativo, direto da RAM.
uint8_t getActiveProfileId();

// Retorna referencia somente-leitura ao perfil pelo id, direto da cache RAM.
const Profile &getProfile(uint8_t id);

// Retorna referencia somente-leitura ao perfil ativo, direto da cache RAM.
const Profile &getActiveProfile();

// Troca o perfil ativo. Apenas atualiza o indice em RAM — nenhuma escrita
// no NVS acontece aqui (requisito de persistence-schema).
void setActiveProfile(uint8_t id);

// Grava um perfil no NVS (blob binario) e atualiza a cache RAM correspondente.
// Unico ponto de escrita de perfil no NVS — chamar apenas em resposta a uma
// mudanca explicita de configuracao.
void saveProfile(uint8_t id, const Profile &profile);

// Numero de escritas de perfil feitas no NVS desde o boot. Existe para
// permitir o teste de regressao "trocar perfil N vezes == zero escritas".
uint32_t nvsWriteCount();

} // namespace ProfileStore
