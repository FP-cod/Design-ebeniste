#pragma once
#include "incognito_config.h"

struct Commandes {
  bool demarrer;
  bool arreter;
  bool rearmer;
  int  intensite_vibration;  // 0–1000
  int  intensite_piston;
  int  intensite_rotation;
  float minuterie_s;
};

struct EntreesSecurite {
  bool au_relais_ok;
  bool presence;
  bool defaut_capteur;
  bool connexion_ok;
};

struct SortiesPilotage {
  int  consigne_vibration;
  int  consigne_piston;
  int  consigne_rotation;
  bool demande_enable_logiciel;
  EtatPilotage etat;
  const char *code_defaut;
};

void machine_init();
SortiesPilotage machine_etape(float dt_s, const Commandes &cmd, const EntreesSecurite &sec);
EtatPilotage machine_etat();
