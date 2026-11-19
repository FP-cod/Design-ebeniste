#include "etats.h"

// Point d'entrée Arduino. L'AU câblé coupe la puissance des drivers
// sans passer par cette boucle. L'ESP32 reste alimenté pour signaler
// DEFAUT. Un chien de garde matériel reçoit une impulsion périodique
// sur PIN_WATCHDOG_MAT ; s'il s'arrête, l'enable matériel tombe.

void presence_tare(float);
struct EtatPresenceFw { bool present; bool defaut; float poids_kg; };
EtatPresenceFw presence_etape(float, float, float);
void radio_init();
void radio_tick();
bool radio_connexion_ok();

void setup() {
  machine_init();
  radio_init();
  presence_tare(0.f);
}

void loop() {
  const float dt = 0.002f;  // 500 Hz, calé sur l'ADS1220
  radio_tick();
  // Lectures ADC (centrale, référence) : à brancher sur l'ADS1220.
  const EtatPresenceFw pres = presence_etape(0.f, 0.f, dt);
  EntreesSecurite sec{};
  sec.au_relais_ok = true;   // lire PIN_RETOUR_AU
  sec.presence = pres.present;
  sec.defaut_capteur = pres.defaut;
  sec.connexion_ok = radio_connexion_ok();
  Commandes cmd{};  // rempli par BLE / Wi-Fi
  machine_etape(dt, cmd, sec);
}
