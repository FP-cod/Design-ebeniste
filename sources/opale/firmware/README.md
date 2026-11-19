# Firmware ESP32 du pouf vibrant Incognito

Squelette C++ (Arduino / PlatformIO, carte ESP32-S3-DevKitC-1).
La logique **testée** est le jumeau Python :

- `incognito.pilotage` — machine d'états ARRET / ATTENTE_PRESENCE / RAMPE / MARCHE / DEFAUT ;
- `incognito.presence` — pont de Wheatstone, filtre, hystérésis, temporisation de levée.

L'API BLE / Wi-Fi, l'appairage sécurisé et le watchdog de connexion
sont spécifiés dans [docs/pilotage_esp32.md](../docs/pilotage_esp32.md).

## Règles de sécurité

- 24 V DC uniquement dans le meuble.
- L'arrêt d'urgence est **physique et indépendant** de l'ESP32 (contact NF,
  relais de sécurité, réarmement manuel, coupure de la puissance des
  trois drivers). Ce firmware ne remplace pas cette chaîne.
- La présence agit aussi sur l'enable **matériel** des drivers (comparateur
  + temporisation, en ET avec le relais). Un chien de garde matériel
  coupe l'enable si le firmware se fige.
- Perte de présence (après 250 ms) et perte de connexion (watchdog 1,5 s)
  mettent les consignes à zéro.

Pas de télécommande ni de pédale : le pilotage passe par BLE ou Wi-Fi
authentifié, plus l'AU câblé.
