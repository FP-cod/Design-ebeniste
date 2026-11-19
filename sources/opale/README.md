# Incognito

Gamme de mobilier de salon d'apparence classique, dont la fonction
(points d'ancrage, mécanismes) est entièrement cachée dans la
structure et se déploie par un geste discret.

Destiné exclusivement à des adultes consentants. Les modèles de
charge et de section fournis ici sont des hypothèses de conception :
ils ne remplacent ni le calcul d'un ingénieur, ni un essai de charge
réel.

Architecture en trois couches, identique à Equinox / Néogothique :

1. `incognito.parametres` — vocabulaire partagé (dimensions, essences,
   revêtements, discrétion, charges).
2. `incognito.catalogues` et `incognito.regles` — matériaux, fixations,
   règles de recalcul.
3. `incognito.grammaires` — un script de grammaire par typologie.
   Typologies livrées : la **banquette** et le **pouf vibrant**
   (`grammaires/banquette.py`, `grammaires/pouf_vibrant.py`).

Unités internes : mm, kg, degrés, N, MPa. L'API Fusion travaille en
cm : la conversion est faite exclusivement dans
`incognito.fusion_outils`.

## Installation et tests

```bash
# depuis /workspace/incognito, avec le .venv du workspace
/workspace/.venv/bin/pytest
```

## Documentation

- [docs/parametres.md](docs/parametres.md) — couche 1, tableaux des paramètres, compromis.
- [docs/banquette.md](docs/banquette.md) — grammaire de la banquette, mécanisme, stabilité, questions ouvertes.
- [docs/pouf_vibrant.md](docs/pouf_vibrant.md) — pouf vibrant (deux gammes, trois modules, filetage, impression 3D, IP67).
- [docs/pilotage_esp32.md](docs/pilotage_esp32.md) — ESP32 BLE/Wi-Fi, machine d'états, AU câblé, présence Wheatstone, API.
- [docs/etancheite_pouf_vibrant.md](docs/etancheite_pouf_vibrant.md) — dossier d'étanchéité IP67 (boîtier, joints, essais).
- `firmware/` — squelette C++ Arduino/PlatformIO (jumeau testé en Python).

## Scripts Fusion 360

- `scripts_fusion/incognito_parametres_fusion.py` — crée ou met à jour les paramètres utilisateur.
- `scripts_fusion/incognito_banquette.py` — génère les corps ; `inc_etat_deploiement` vaut 0 (fermé) ou 1 (déployé).
- `scripts_fusion/incognito_pouf_vibrant.py` — pouf vibrant ; `inc_sybian_gamme` 0/1, `inc_pouf_etat` 0/1, export STL (moule, panneaux acoustiques, boîtier).
