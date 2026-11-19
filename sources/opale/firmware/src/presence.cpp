#include "incognito_config.h"

// Jumeau simplifié de incognito.presence (tare, soustraction, hystérésis,
// temporisation de levée 250 ms). Le filtre strict (fc = f_exc_min/10)
// et le chemin rapide sont implémentés côté Python ; ici, un 1er ordre
// sur la voie soustraite suffit au squelette.

struct EtatPresenceFw {
  bool present;
  bool defaut;
  float poids_kg;
};

static float g_tare = 0;
static float g_lp = 0;
static float g_sous_seuil_s = 0;
static bool g_present = false;

void presence_tare(float brut_kg) {
  g_tare = brut_kg;
  g_lp = 0;
  g_sous_seuil_s = 0;
  g_present = false;
}

EtatPresenceFw presence_etape(float centrale_kg, float reference_kg, float dt_s) {
  const float soustrait = centrale_kg - reference_kg - g_tare;
  const float fc = F_EXC_MIN_HZ / 10.0f;
  const float tau = 1.0f / (6.2831853f * fc);
  const float a = dt_s / (tau + dt_s);
  g_lp = g_lp + a * (soustrait - g_lp);

  // Chemin rapide ≈ soustrait (la moyenne courte est dans le jumeau Python).
  const float rapide = soustrait;
  if (g_present) {
    if (rapide < SEUIL_ABSENCE_KG) {
      g_sous_seuil_s += dt_s;
      if (g_sous_seuil_s >= TEMPO_LEVEE_S) {
        g_present = false;
        g_sous_seuil_s = 0;
      }
    } else {
      g_sous_seuil_s = 0;
    }
  } else if (rapide >= SEUIL_PRESENCE_KG) {
    g_present = true;
    g_sous_seuil_s = 0;
  }
  EtatPresenceFw e{};
  e.present = g_present;
  e.defaut = (centrale_kg > 80.f) || (centrale_kg < -5.f);
  e.poids_kg = g_lp;
  if (e.defaut) e.present = false;
  return e;
}
