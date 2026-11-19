#include "etats.h"

// Jumeau de incognito.pilotage.MachineEtats (même graphe d'états).

static EtatPilotage g_etat = ETAT_ARRET;
static const char *g_defaut = "";
static float g_t_rampe = 0;
static float g_t_watch = 0;
static float g_t_minut = 0;
static float g_minut_cible = 0;
static Commandes g_cible = {};

void machine_init() {
  g_etat = ETAT_ARRET;
  g_defaut = "";
  g_t_rampe = g_t_watch = g_t_minut = 0;
}

EtatPilotage machine_etat() { return g_etat; }

static SortiesPilotage zero() {
  SortiesPilotage s{};
  s.etat = g_etat;
  s.code_defaut = g_defaut;
  return s;
}

static SortiesPilotage rampe(const Commandes &c, float p) {
  if (p < 0) p = 0;
  if (p > 1) p = 1;
  SortiesPilotage s{};
  s.consigne_vibration = (int)(c.intensite_vibration * p + 0.5f);
  s.consigne_piston    = (int)(c.intensite_piston * p + 0.5f);
  s.consigne_rotation  = (int)(c.intensite_rotation * p + 0.5f);
  s.demande_enable_logiciel = true;
  s.etat = g_etat;
  s.code_defaut = "";
  return s;
}

SortiesPilotage machine_etape(float dt_s, const Commandes &cmd, const EntreesSecurite &sec) {
  if (!sec.connexion_ok) g_t_watch += dt_s;
  else g_t_watch = 0;

  const bool perte = g_t_watch >= WATCHDOG_CONNEXION_S;
  const bool defaut = (!sec.au_relais_ok) || sec.defaut_capteur;

  if (defaut && g_etat != ETAT_DEFAUT) {
    g_etat = ETAT_DEFAUT;
    g_defaut = sec.au_relais_ok ? "capteur" : "au_enclenche";
    g_t_rampe = 0;
    return zero();
  }
  if (g_etat == ETAT_DEFAUT) {
    if (cmd.rearmer && sec.au_relais_ok && !sec.defaut_capteur) {
      g_etat = ETAT_ARRET;
      g_defaut = "";
    }
    return zero();
  }
  if (cmd.arreter) {
    g_etat = ETAT_ARRET;
    g_t_rampe = g_t_minut = 0;
    return zero();
  }
  if (g_etat == ETAT_ARRET) {
    if (cmd.demarrer && sec.connexion_ok) {
      g_cible = cmd;
      g_minut_cible = cmd.minuterie_s;
      g_t_minut = 0;
      g_etat = ETAT_ATTENTE_PRESENCE;
    }
    return zero();
  }
  if (perte) {
    g_etat = ETAT_ARRET;
    g_t_rampe = 0;
    return zero();
  }
  if (g_etat == ETAT_ATTENTE_PRESENCE) {
    if (sec.presence) {
      g_etat = ETAT_RAMPE;
      g_t_rampe = 0;
    }
    return zero();
  }
  if (!sec.presence) {
    g_etat = ETAT_ATTENTE_PRESENCE;
    g_t_rampe = 0;
    return zero();
  }
  if (g_minut_cible > 0) {
    g_t_minut += dt_s;
    if (g_t_minut >= g_minut_cible) {
      g_etat = ETAT_ARRET;
      g_t_rampe = g_t_minut = 0;
      return zero();
    }
  }
  if (g_etat == ETAT_RAMPE) {
    g_t_rampe += dt_s;
    if (g_t_rampe >= DUREE_RAMPE_S) {
      g_etat = ETAT_MARCHE;
      return rampe(g_cible, 1.f);
    }
    return rampe(g_cible, g_t_rampe / DUREE_RAMPE_S);
  }
  g_cible = cmd;
  return rampe(cmd, 1.f);
}
