#include "incognito_config.h"

// Spécification API : docs/pilotage_esp32.md
// Appairage BLE : LE Secure Connections + bonding, pas de "Just Works"
// en production. Wi-Fi : WPA2/WPA3 uniquement, API authentifiée.
//
// Les UUIDs et le comportement des caractéristiques sont documentés
// dans docs/pilotage_esp32.md. Ce fichier est un squelette : les
// appels NimBLE / WiFi sont volontairement omis pour rester compilables
// hors SDK, et à brancher sur la carte.

void radio_init() {
  // BLE : publicité après bonding, caractéristiques chiffrées.
  // Wi-Fi : STA provisionnée, sinon SoftAP WPA2 au mot de passe unique,
  // jamais d'AP ouvert.
}

void radio_tick() {
  // Met à jour connexion_ok pour le watchdog de la machine d'états.
}

bool radio_connexion_ok() {
  return false;  // à relier à BLE notify / session Wi-Fi
}
