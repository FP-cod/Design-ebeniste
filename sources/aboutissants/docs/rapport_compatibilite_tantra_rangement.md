# Rapport — compatibilité Tantra et Rangement

Les dépôts `/workspace/tantra` et `/workspace/rangement` ont été
inspectés **en lecture seule**, sans modification (pas plus qu'Equinox,
Néogothique ou Incognito). Les cotes reprises dans
`common/params_globaux.py` (`ancrages.tantra`, `ancrages.rangement`)
citent le fichier et le nom de variable sources. Toute cote absente
vaut `None`, `statut=todo`, avec justification. Rien n'est inventé.

Ce document complète `docs/rapport_couche1_mouvement.md` et
`docs/rapport_vac_u_lock_collecteur_cadres.md`.

---

## 1. Points d'ancrage relevés

### Tantra — interface commune

Insert d'ancre **M12** inox A4, Ø ext. **16 mm**, encastrement **60 mm**
(`INSERT_ANCRE_M12.cotes_mm`, `tantra/tantra/catalogues/fixations.py`).
Charge de service **1500 N**, CS **3** → rupture visée **4500 N**
(`ParametresCharge`, `tantra/tantra/parametres.py`). Anneau rabattable
affleurant : cuvette **Ø 50 × 12 mm** — **DI et fil non cotés** (TODO).
Cache aimanté **Ø 40 × 10 mm**. Retrait sous surface (volet camouflable)
**10 mm**. Bloc d'ancrage recalé par défaut (chêne, recouvrement 0) :
**50 × 80 × 80 mm**, tourillons Ø12 × 50, distance au bord
`max(25 mm, 2Ø)`.

Aucun **NPT**, aucun **port Vac-U-Lock**, aucun emplacement de
**collecteur** ou de **machine** dans les scripts.

| Typologie | Ancrages (défauts) | Source |
|---|---|---|
| `tantra_chaise_double_courbe` | **4** (2 Y × 2 flasques) ; Y = **760 / 1560 mm** | `positions_ancrages` ; `ancrages_flasques` |
| `tantra_fauteuil_lombaire` | **2** (une paire) | `tantra_fauteuil_lombaire.py` |
| `tantra_banquette_deux_niveaux` | **6** (3 par flasque) | `tantra_banquette_deux_niveaux.py` |
| `tantra_siege_repose_genoux` | **4** (genoux + assise, g/d) | `tantra_siege_repose_genoux.py` |
| `camo_canape` | **6** masqués (1/accoudoir, 2 avant, 2 arrière) ; visibles en RÉVÉLÉ seulement (arrière toujours sous galette) | `CAMO_CANAPE` ; `_salon.py` |
| `camo_fauteuil` | **4** masqués (2 accoudoirs, 2 avant ; pas d'arrière) | `camo_fauteuil.py` (`ancrages_arriere=False`) |
| `cadre_desserte_genoux` | **4** (2 poignets sur barre haute, 2 chevilles dans le nez) ; Z poignets **750 mm** (MEUBLE) / **1150 mm** (CADRE) | `cadre_desserte_genoux.py` ; cotes typologie |
| `cadre_table_inclinee` | **aucun coté** — typologie étudiée, grammaire non livrée | `docs/cadre_table_inclinee.md` |

Les Z calculés par les courbes (ex. chaise ~198 / 621 mm) ne sont pas
des paramètres nommés : on ne les fige pas ici.

Les inserts **M6 / M8** mentionnés dans `TYPOLOGIES.md` et l'ancien
`TantraGamme/lib/catalogues.py` concernent le **garnissage démontable**,
pas la retenue de personne.

Les ancrages Tantra sont dimensionnés pour retenir une personne
**installée sur le meuble** (effort interne). Une traction extérieure
de 1500 N, meuble vide, peut le faire basculer (la grammaire le
signale).

### Rangement — râtelier mural (seule grammaire livrée)

Filetage d'insert **M8**, longueur **20 mm**, CMU catalogue **2500 N**
(reprise Equinox). **Un râtelier n'est pas un point d'ancrage de
personne** (`charges.effort_accidentel` = 300 N, vérifié en alerte
seulement).

Ports Aboutissants **natifs** : `ports.vac_u_lock` et `ports.npt` vrais ;
**2 ports / module**, entraxe **200 mm**, axe à **130 mm** du bas de
panneau (pose typ. **900 mm**), plot **70 × 40 mm**. Système par défaut
`port_vac_u_lock_npt` (ergot à arrière `npt_1_male` — **à trancher** vs
`filete_machine` M8x1.25 × 16). Autres systèmes : `port_vac_u_lock_m8`,
`port_npt_1_femelle`, `port_cache_affleurant` (cache 10 mm). Panneau
dorsal **22 mm**. Crochets : **4 / module**, axe à **400 mm** (tige Ø8,
platine Ø40, saillie 60 mm, insert M8) — supports d'accessoires, pas
des œillets de retenue. Barres : **2 / module**, première à **680 mm**.
Module **600 × 320 mm**.

Typologies `armoire_accessoires`, `coffre`, `support_exposition`,
`armoire_verrouillable` : **pas de grammaire livrée**, aucun port ni
collecteur coté. `pose.capacite_support_mur` = `None` (TODO).

---

## 2. Tableau de compatibilité synthétique

Statuts : **compatible** / **compatible_adaptateur** / **limite** /
**incompatible**. Détail et légende :
`catalogues/compatibilite.py` (`matrice_interfaces_gammes`) et
`cadres/cadre_modulaire.py` (cadres × meubles).

| Interface | Equinox | Néogothique | Incognito (hors pouf) | Tantra | Rangement |
|---|---|---|---|---|---|
| Œillet M8 | compatible | limite | limite | compatible_adaptateur (M12, DI anneau TODO) | **incompatible** (M8 présent, mais pas un ancrage de personne) |
| Port Vac-U-Lock | compatible_adaptateur | compatible_adaptateur | compatible_adaptateur | limite (pas de port natif ; adaptateur M12 possible, décision) | **compatible** (ports natifs ; montage arrière à trancher) |
| Collecteur d'urine | compatible | compatible | limite | limite (sièges livrés, aucun emplacement coté) | **incompatible** (pas d'assise sur le râtelier) |
| NPT 1" | incompatible (absent) | incompatible (absent) | compatible (housses) | **incompatible** (absent ; pas d'ajout rétroactif ici) | **compatible** (douilles femelles natives) |
| Machine mécanique | compatible_adaptateur | compatible_adaptateur | limite | limite (châssis au sol ; liaison M12 sous réserve) | **incompatible** (pas un appui de machine) |
| Cadre au sol | compatible_adaptateur | compatible_adaptateur | limite | compatible_adaptateur (camouflable : RÉVÉLÉ seulement) | limite (cohabitation, pas de liaison aux crochets) |
| Cadre mural | compatible_adaptateur | limite | limite | limite | limite (même mur, support TODO, pas de liaison aux inserts) |
| Poutre suspendue | limite | limite | limite | limite | limite |

Les meubles ne sont jamais percés. Tantra / Rangement n'ont pas été
modifiés.

---

## 3. TODO et décisions à soumettre

Cotes `None` / `todo` ajoutées :

1. `ancrages.tantra.diametre_interieur_anneau` — cuvette Ø50 cotée, pas le DI.
2. `ancrages.tantra.diametre_fil` — fil d'anneau non documenté.
3. `ancrages.tantra.emplacement_collecteur` / `emplacement_machine`.
4. `ancrages.tantra.cadre_table_inclinee_nombre` — grammaire non livrée.
5. `ancrages.rangement.capacite_support_mur` — déjà TODO dans Rangement.
6. `ancrages.rangement.emplacement_collecteur` / `emplacement_machine`.
7. `ancrages.rangement.diametre_interieur_anneau` / `diametre_fil` — pas d'anneau de retenue.

Décisions (liste complète : `catalogues.compatibilite.decisions_a_trancher`) :

- **Tantra** : DI / fil de l'anneau ; adaptateur M12↔M8 ou brides M12 ;
  ports / NPT natifs rétroactifs ou seulement des adaptateurs ; cotes
  d'implantation collecteur / machine ; suite de la table inclinée ;
  confirmer la discipline SALON / RÉVÉLÉ pour les aboutissants visibles.
- **Rangement** : montage arrière `npt_1_male` vs `filete_machine` M8
  (déjà signalé dans Rangement) ; confirmer l'interdiction d'ancrer une
  personne ou une machine sur crochets / barres / inserts ; ports ou
  collecteur dans les caissons encore non grammatisés ; relevé du
  support mural.

---

## 4. Fichiers Aboutissants créés ou mis à jour

- `common/params_globaux.py` — `ancrages.tantra`, `ancrages.rangement`,
  `npt_1.present_tantra` / `present_rangement`, `GAMMES_ANCRAGES`.
- `catalogues/compatibilite.py` — matrices interfaces × gammes.
- `cadres/cadre_modulaire.py` — cadres × Tantra / Rangement.
- `hygiene/collecteur_urine.py` — typologies, implantations, arbitrages.
- `interfaces/port_vac_u_lock.py` — `adaptateur_ancrage` Tantra / Rangement.
- `tests/test_compatibilite_tantra_rangement.py` et tests existants étendus.
- `README.md` et le présent rapport.

Aucun fichier n'a été modifié dans `tantra/`, `rangement/`, `equinox/`,
`neogothique/` ni `incognito/`.

---

## 5. Tests

Exécutés le 18 novembre 2026 (Europe/Paris), hors Fusion, sans `adsk` :

```
cd /workspace/aboutissants && /workspace/.venv/bin/python -m pytest
```

Résultat : **69 passed**.
