#pragma once
// Configuration du squelette firmware Incognito (24 V, ESP32-S3).
// L'AU physique n'est PAS câblé ici : contact NF + relais de sécurité
// indépendants, réarmement manuel, coupure de la puissance des drivers.

#include <stdint.h>

static const uint8_t PIN_ENABLE_LOGICIEL = 4;   // ne remplace pas l'enable matériel
static const uint8_t PIN_RETOUR_AU       = 5;   // lecture, actif bas = AU ok (boucle fermée)
static const uint8_t PIN_WATCHDOG_MAT    = 6;   // impulsion vers le chien de garde matériel
static const uint8_t PIN_ADC_DRDY        = 7;   // ADS1220 (recommandé) ; HX711 non retenu par défaut

static const float FS_PRESENCE_HZ        = 500.0f;  // ADS1220
static const float F_EXC_MIN_HZ          = 18.0f;   // fc = F_EXC_MIN / 10
static const float SEUIL_PRESENCE_KG     = 15.0f;
static const float SEUIL_ABSENCE_KG      = 10.0f;
static const float TEMPO_LEVEE_S         = 0.25f;
static const float WATCHDOG_CONNEXION_S  = 1.5f;
static const float DUREE_RAMPE_S         = 1.5f;

enum EtatPilotage : uint8_t {
  ETAT_ARRET = 0,
  ETAT_ATTENTE_PRESENCE = 1,
  ETAT_RAMPE = 2,
  ETAT_MARCHE = 3,
  ETAT_DEFAUT = 4,
};
