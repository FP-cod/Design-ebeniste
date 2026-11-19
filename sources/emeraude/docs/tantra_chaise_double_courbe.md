# Chaise tantra double courbe (volet 1 — meuble fixe)

**Typologie :** l'archétype de la chaise tantra. Un profil continu en double S : nez,
petite bosse avant (sous les cuisses ou sous le bassin), creux d'assise, grande courbe
lombaire puis dorsale, sommet et retombée en appui-tête. Elle se lit franchement comme un
meuble érotique : ni camouflable, ni modulable. Ligne moderne mais classique : flasques
chantournées en lamellé de hêtre, coque en contreplaqué cintré, cuir cognac, socle en retrait.

## Grammaire (`tantra/grammaires/tantra_chaise_double_courbe.py`)

* **Points clés** `PointCle(y, z, angle)`, de l'avant vers l'arrière : nez (y 0, z 300, 55°),
  petite bosse (300, 470, 0°), creux (760, 330, 0°), flanc (1200, z, 38°), sommet (L − 300, 760, 0°),
  retombée (L, 760 − 110, −38°). Hermite cubique, tension 0,9, 20 points par segment.
* **Ordre imposé** : 0 < bosse < creux < flanc < L − 150 et creux < bosse < sommet (sinon `ValueError`).
* **Structure** : 3 flasques en lamellé de hêtre 30 mm (BauBuche) sur toute la silhouette, coque
  de 18 mm (≥ 12 plis de 1,5 mm), traverses basses et hautes à tenons, socle en retrait de 40 mm,
  tourillons Ø10.
* **Ancrages** : 4 inserts M12 dans des blocs de chêne de 50 × 80 × 80 mm contre les flasques
  extérieures, aux abscisses 760 et 1560 mm ; anneaux rabattables (assumés, visibles).
* **Recalculs** : nombre de flasques (portée admissible de la coque sous une charge de genou de
  1 650 N, CS 3) ; rayon de cintrage mini ≥ 100 × épaisseur de pli ; bloc d'ancrage (arrachement
  EC5, parois de cisaillement) ; stabilité sur 4 cas.

## Ergonomie (P5–P95, Pheasant & Haslegrave, *Bodyspace*, 3ᵉ éd. 2006)

* creux ≥ longueur fesse-poplité P5 (435 mm) ; petite bosse 100 à 200 mm au-dessus du creux ;
* pente lombaire 25 à 55° ; longueur développée creux → extrémité ≥ hauteur assis P95 (965 mm) ;
* largeur ≥ hanches assis P95 (435 mm) + 2 × 50 mm (au-delà de 650 mm, les petits gabarits ont du
  mal à poser les genoux de part et d'autre).

## Compromis

* **Confort / tenue des ancrages** : les blocs sont contre les flasques extérieures, là où la
  structure est la plus raide ; ils restent visibles (assumé dans ce volet).
* **Coût / rayon** : un rayon plus serré (courbe plus « sculpturale ») impose des plis plus fins
  ou un moule plus cher ; la grammaire refuse un rayon inférieur à 150 mm.
* **Largeur** : 600 mm, c'est un compromis entre enveloppement et appui des genoux.

<!-- DEBUT GENERE -->

## Résultats calculés (générés par `python -m tantra.rapport`)

| État | Hors-tout l × p × h (mm) | Masse (kg) | Pièces | Ancrages | Conforme |
|---|---|---|---|---|---|
| FIXE | 600 × 1850 × 760 | 74.7 | 22 | 4 | oui |

### Vérifications — état FIXE

| Niveau | Code | Détail |
|---|---|---|
| ok | `ergo_longueur_creux` | Creux d'assise 803 mm (petite bosse → +150 mm de grande courbe) ≥ fesse-poplité P5 435 mm : assise possible dans le creux, cuisses sur la petite bosse. |
| ok | `ergo_elevation_bassin` | Petite bosse 140 mm au-dessus du creux (plage de conception 100–200 mm : en dessous l'effet de bascule du bassin est faible, au-delà l'assise dans le creux comprime l'arrière des cuisses). |
| ok | `ergo_pente_lombaire` | Pente de la grande courbe à 200 mm au-dessus du creux : 38° (plage 25–55° : assez redressée pour soutenir le dos assis, assez couchée pour s'y allonger). |
| ok | `ergo_longueur_dos` | Longueur développée creux → extrémité 1239 mm ≥ hauteur assis P95 965 mm (tronc et tête soutenus allongé). |
| ok | `ergo_largeur` | Largeur 600 mm ≥ hanches assis P95 435 + 2 × 50 = 535 mm. Au-delà de ~650 mm, l'appui des genoux de part et d'autre devient difficile pour les petits gabarits (compromis enveloppement / stabilité). |
| ok | `coque_flexion` | Coque 18 mm : 3 flasques nécessaires pour une charge de genou 1650 N (bande 200 mm, CS 3) ; 3 prévues. |
| ok | `coque_cintrage` | Rayon mini de la coque ≈ 152 mm pour un rayon de cintrage mini 150 mm (plis de 1.5 mm). Faisable. |
| ok | `tenons_traverses` | Tenons des traverses (11 × 60 mm) : 412 N par tenon (toute la charge de 2 personne(s) par les traverses, part doublée pour l'excentrement), CS 4.1. |
| ok | `bloc_arrachement` | Arrachement insert : R_k ≈ 11.2 kN, CS 7.4 (visé ≥ 3) — formule EC5 des vis, par analogie. |
| ok | `bloc_paroi` | Parois 17.0 mm de part et d'autre de l'insert : CS cisaillement 5.4 (paroi mini calculée 9.4 mm). |
| ok | `bloc_essence` | Bloc en Chêne massif : un contreplaqué tient mal un insert (cisaillement roulant) — bloc en massif ou lamellé exigé. |
| essai requis | `bloc_essai` | Essai d'arrachement réel de l'insert dans le bloc (série et bois réels). |
| ok | `bloc_ancrage_dimensions` | Bloc d'ancrage recalculé : 50 × 80 × 80 mm, 2 tourillons Ø12, + 30 mm de flasque traversée. |
| ok | `stabilite_assis_sur_le_nez` | Stabilité « assis_sur_le_nez » : coefficient 5.60 (arête -y, minimum 1.5). Une personne (charge dynamique) assise sur l'extrême avant. |
| ok | `stabilite_appui_sur_la_retombee` | Stabilité « appui_sur_la_retombee » : coefficient 5.64 (arête +y, minimum 1.5). Une personne appuyée sur l'extrémité de l'appui-tête. |
| ok | `stabilite_assis_bord_lateral` | Stabilité « assis_bord_lateral » : coefficient 2.15 (arête -x, minimum 1.2). Une personne assise au bord du creux + poussée latérale accidentelle. |
| ok | `stabilite_vide_poussee_sommet` | Stabilité « vide_poussee_sommet » : coefficient 1.67 (arête -x, minimum 1.2). Meuble vide, poussée latérale de 150 N au sommet. |
| AVERTISSEMENT (compromis) | `traction_exterieure_ancrage` | Traction extérieure de 1500 N à 621 mm, meuble vide : coefficient 0.20. Les ancrages servent à retenir une personne installée sur le meuble ; ne jamais les relier à un point extérieur ni tirer depuis l'extérieur. |
| essai requis | `essai_statique` | Essai statique de la surface : 3 × charge de service, 10 min, sans rupture ni déformation permanente (type EN 1728 adapté). |
| essai requis | `essai_fatigue` | Essai de fatigue des assemblages (cycles d'assise/rythme) — référence EN 1728 / EN 12520, à adapter à l'usage. |
| essai requis | `essai_ancrages` | Essai de traction de chaque ancrage à 3 × 1500 N, sur prototype. |
| essai requis | `visa_ingenieur` | Modèles simplifiés : visa d'un ingénieur structure avant série. |

Ancrages (FIXE) :

* `ancrage_1g` — (0, 760, 198) mm, dans `chaise_bloc_ancrage_1g` : Insert inox M12 traversant la flasque, anneau rabattable affleurant.
* `ancrage_1d` — (600, 760, 198) mm, dans `chaise_bloc_ancrage_1d` : Insert inox M12 traversant la flasque, anneau rabattable affleurant.
* `ancrage_2g` — (0, 1560, 621) mm, dans `chaise_bloc_ancrage_2g` : Insert inox M12 traversant la flasque, anneau rabattable affleurant.
* `ancrage_2d` — (600, 1560, 621) mm, dans `chaise_bloc_ancrage_2d` : Insert inox M12 traversant la flasque, anneau rabattable affleurant.

### Chiffrage indicatif (estimation datée de novembre 2026, HT sauf mention)

| Poste | Montant |
|---|---|
| Bois (pertes comprises) | 315 € |
| Mousses | 35 € |
| Revêtements (+25 % de chutes) | 207 € |
| Quincaillerie | 176 € |
| Finition + emballage | 129 € |
| Amortissement moules | 120 € |
| Main-d'œuvre (28.4 h ébénisterie + 3.9 h tapisserie) | 1851 € |
| **Coût de revient** | **2830 € HT** |
| Prix de vente indicatif (× 1,45) | 4110 € HT — **4930 € TTC** (fourchette 3700–6150 €) |
| Prototype unitaire | ≈ 14750 € TTC |

### Paramètres Fusion propres à la typologie

* `tan_chaise_position_petite_bosse` = 300 mm — Abscisse du sommet de la cale fessière.
* `tan_chaise_position_creux` = 760 mm — Abscisse du point bas.
* `tan_chaise_position_flanc` = 1200 mm — Abscisse de l'inflexion de la grande courbe.
* `tan_chaise_angle_flanc` = 38 deg — Pente au point d'inflexion.
* `tan_chaise_ep_flasque` = 30 mm — Épaisseur des flasques (lamellé-collé).
* `tan_chaise_ep_coque` = 18 mm — Épaisseur de la coque cintrée.
* `tan_chaise_n_flasques` = 3  — Nombre de flasques. Sans unité.

<!-- FIN GENERE -->
