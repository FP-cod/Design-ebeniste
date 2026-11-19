# Pilotage ESP32 (BLE + Wi-Fi) — pouf vibrant Incognito

Le module ESP32-S3 remplace la télécommande et la pédale. Document
jumeau du firmware (`firmware/`) et de `incognito.pilotage` /
`incognito.presence`. Les modèles sont des **hypothèses de conception**,
pas une certification.

## Architecture de sécurité (deux chaînes)

| Chaîne | Rôle | Indépendante de l'ESP32 ? |
| --- | --- | --- |
| **AU physique** | Contact **NF**, relais de sécurité à contacts guidés, **réarmement manuel**. Coupe le **24 V des drivers** des trois modules (vibration, piston, rotation). | **Oui.** L'ESP32 n'est pas dans la boucle. Il reste alimenté (convertisseur 24→5 V en amont du relais de puissance) pour passer en `DEFAUT`. |
| **Présence** | Cellules Wheatstone + chemin matériel (filtre analogique, comparateur à hystérésis, temporisation 200–300 ms) en **ET** avec les contacts du relais, sur l'**enable matériel** des drivers. | Le chemin enable est matériel. L'ESP32 lit le même signal pour sa machine d'états, mais un plantage logiciel ne doit pas maintenir l'enable. Un **chien de garde matériel** (impulsion périodique) coupe l'enable si le firmware se fige. |

Placement de l'AU : sous le **chant avant droit de la couronne** (lèvre de 18 mm, ≈ x = largeur − 90 mm). Accessible assis (les doigts s'enroulent sous la lèvre, portée ~250 mm depuis l'axe). Discret : invisible sur la façade velours, identifiable au toucher (ISO 13850). Le réarmement du relais, dans le boîtier, **n'autorise** le redémarrage que depuis `ARRET` : il ne relance pas le mouvement.

## Machine d'états

`ARRET` → (commande démarrer + connexion) → `ATTENTE_PRESENCE` → (présence) → `RAMPE` (durée typique 1,5 s) → `MARCHE`.

Coupures :

- perte de présence (après temporisation 250 ms, déjà appliquée par le détecteur) : consignes à zéro, retour `ATTENTE_PRESENCE` ;
- perte de connexion (watchdog **1,5 s** sans BLE / session Wi-Fi) : consignes à zéro, retour `ARRET` ;
- AU, défaut capteur, dérive de zéro : `DEFAUT`, consignes à zéro, **réarmement manuel** (AU relâché + commande réarmer).

Curseurs d'intensité 0–1000 (pourmil) par module (vibration, piston, rotation), profils mémorisés, minuterie de session (0 = aucune).

## Présence (Wheatstone)

Les **FSR sont écartés** : hystérésis, dérive à la chaleur et à l'humidité, pas de diagnostic de pont, caractéristique peu fiable au seuil.

- Quatre cellules 50 kg (pont de Wheatstone) sous la couronne, zone centrale, chacune avec **butée de surcharge** (jeu ~0,4 mm).
- Zone de référence : accéléromètre (ou cellule hors appui), **soustraite** du signal central.
- Passe-bas logiciel Butterworth ordre 2, **fc ≤ f_exc_min / 10** (calcul automatique : 1,80 Hz si f_exc_min = 18 Hz ; atténuation 40 dB à f_exc pour un ordre 2). Sert à la tare, à la dérive et au diagnostic.
- Décision de présence : chemin rapide (moyenne ~50 ms sur le signal soustrait) + hystérésis 15 kg / 10 kg + temporisation de levée **250 ms** (plage 200–300 ms). Justification : deux périodes à 8 Hz, ignore un creux vibratoire ou un rebond, tout en coupant assez tôt après une levée ; l'AU reste la coupure d'urgence.
- Tare automatique selle vide (housse éventuelle sous le seuil).
- Défauts : hors-plage ADC, dérive du zéro > 2,5 kg (humidité / fluage de jauge).

ADC : **ADS1220 recommandé** (≥ 500 SPS, anti-repli maîtrisable). **HX711 80 SPS** : Nyquist 40 Hz, une vibration 8–40 Hz se replie dans la bande utile **sans** filtre anti-repli analogique strict — non retenu par défaut.

Un seul filtre à 1,8 Hz ne peut pas à la fois atténuer 40 dB à 18 Hz et transitoire en 200–300 ms : d'où le double chemin (strict + rapide + soustraction).

## API BLE

Base UUID 128 bits : `8f1e0000-6c6f-4e63-b167-496e636f676e`.

Toutes les caractéristiques ci-dessous exigent un lien **chiffré et authentifié** (bonding). Pas de lecture/écriture en clair.

| UUID | Nom | Propriétés | Format | Rôle |
| --- | --- | --- | --- | --- |
| `…0001` | Service de pilotage Incognito | service primaire | — | — |
| `…0002` | État | lecture, notify | `uint8` (0–4 = ARRET…DEFAUT) | Machine d'états |
| `…0003` | Commande | écriture | `uint8` : 1 démarrer, 2 arrêter, 3 réarmer, 4 tare | — |
| `…0004` | Intensité vibration | lecture, écriture, notify | `uint16` 0–1000, little-endian | Curseur |
| `…0005` | Intensité piston | lecture, écriture, notify | `uint16` 0–1000 | Curseur |
| `…0006` | Intensité rotation | lecture, écriture, notify | `uint16` 0–1000 | Curseur |
| `…0007` | Profil | lecture, écriture | `uint8` index + 3×`uint16` intensités + `uint16` minuterie (s) | Profils |
| `…0008` | Minuterie | lecture, écriture, notify | `uint16` secondes restantes | 0 = inactive |
| `…0009` | Présence | lecture, notify | `int32` poids filtré (g) + `uint8` drapeaux (présent, défaut) | Diagnostic |
| `…000A` | Défaut | lecture, notify | `uint8` code + chaîne UTF-8 courte | — |
| `…000B` | Version | lecture | UTF-8 | Firmware |

CCCD obligatoires sur les notify. MTU négocié ≥ 64 octets.

### Appairage sécurisé

- BLE 4.2+ **LE Secure Connections**, bonding persistant.
- Association par **comparaison numérique** ou **code** ; **Just Works interdit** en production (pas de MITM protection).
- Après bonding, la publicité peut rester visible, mais toute écriture de consigne exige le lien authentifié.
- Un appareil non bondé ne peut pas démarrer les modules.

## Wi-Fi authentifié

- Mode nominal : station WPA2/WPA3 vers un réseau connu, provisionné une fois.
- Si non provisionné : SoftAP **WPA2** (mot de passe unique imprimé dans le dossier de fabrication, pas d'AP ouvert).
- API : session authentifiée (jeton) sur HTTPS ou WebSocket TLS lorsqu'une pile TLS est disponible ; à défaut, uniquement sur le SoftAP WPA2, jamais en clair sur un réseau ouvert.
- La session Wi-Fi, comme le BLE, nourrit le **watchdog de connexion** (1,5 s).

## Boîtier

PETG, IP67 visé (détail : [etancheite_pouf_vibrant.md](etancheite_pouf_vibrant.md)) : évent ePTFE, presse-étoupes, fenêtre d'antenne plastique **non masquée** par le bois métallisé ou une tôle. Coin arrière gauche du caisson, 120 × 80 × 45 mm.
