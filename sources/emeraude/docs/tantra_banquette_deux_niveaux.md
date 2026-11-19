# Banquette tantra à deux niveaux (volet 1 — meuble fixe)

**Typologie :** banquette large (1 500 × 1 050 mm) à deux plans : un niveau bas d'assise
(420 mm) et un niveau haut (640 mm) incliné de 12°, reliés par une contremarche à 72°. Le niveau
haut sert d'accoudoir quand on est assis, et d'appui ventral (hanches au bord) quand on est à
genoux sur le niveau bas.

## Grammaire (`tantra_banquette_deux_niveaux.py`)

* Profil fini : avant, niveau bas, contremarche (pente 72°), niveau haut, arrière. Le profil de
  **structure** (coque) supprime le point milieu de la contremarche et recule le point bas
  (db − 240) pour garder un rayon ≥ 150 mm (≈ 169 mm obtenu) ; la mousse forme la marche.
* Flasques en lamellé de hêtre 30 mm ; nombre **recalculé** à partir de la largeur (6 par
  défaut) ; coque 18 mm ; traverses hautes à 2 positions ; 6 ancrages.

## Ergonomie

* niveau bas dans la plage poplitée P5–P95 (355–490) ; profondeur ≥ fesse-poplité P5 ;
* contremarche ≈ hauteur de coude assis (185–295 mm) ; niveau haut ≥ 450 mm de profondeur.

## Compromis

* C'est la pièce la plus chère du volet (≈ 48 h d'ébénisterie, 6 flasques).
* 1 500 mm de long : ce n'est pas un lit ; un grand gabarit allongé en travers dépasse.

<!-- DEBUT GENERE -->

## Résultats calculés (générés par `python -m tantra.rapport`)

| État | Hors-tout l × p × h (mm) | Masse (kg) | Pièces | Ancrages | Conforme |
|---|---|---|---|---|---|
| FIXE | 1500 × 1050 × 641 | 96.6 | 39 | 6 | oui |

### Vérifications — état FIXE

| Niveau | Code | Détail |
|---|---|---|
| ok | `ergo_niveau_bas_assise` | Niveau bas 420 mm dans la plage poplitée P5–P95 (355–490 mm) : utilisable en assise. |
| ok | `ergo_profondeur_bas` | Profondeur du niveau bas 480 mm ≥ fesse-poplité P5 435 mm. |
| ok | `ergo_hauteur_marche` | Contremarche 220 mm ≈ hauteur coude assis P5–P95 (185–295 mm) : le niveau haut sert d'accoudoir assis, et d'appui ventral (hanches au bord) agenouillé sur le niveau bas. |
| ok | `ergo_profondeur_haut` | Niveau haut 570 mm de profondeur (≥ 450 mm pour y poser le buste ou s'y asseoir). |
| ok (compromis) | `ergo_longueur_allonge` | Longueur 1500 mm : allongé en travers sur le niveau haut, tête et jambes dépassent pour un grand gabarit (choix d'encombrement, pas un lit). |
| ok | `coque_flexion` | Coque 18 mm : 6 flasques nécessaires pour une charge de genou 1650 N (bande 200 mm, CS 3) ; 6 prévues. |
| ok | `coque_cintrage` | Rayon mini de la coque ≈ 169 mm pour un rayon de cintrage mini 150 mm (plis de 1.5 mm). Faisable. |
| ok | `tenons_traverses` | Tenons des traverses (11 × 60 mm) : 165 N par tenon (toute la charge de 2 personne(s) par les traverses, part doublée pour l'excentrement), CS 10.3. |
| ok | `bloc_arrachement` | Arrachement insert : R_k ≈ 11.2 kN, CS 7.4 (visé ≥ 3) — formule EC5 des vis, par analogie. |
| ok | `bloc_paroi` | Parois 17.0 mm de part et d'autre de l'insert : CS cisaillement 5.4 (paroi mini calculée 9.4 mm). |
| ok | `bloc_essence` | Bloc en Chêne massif : un contreplaqué tient mal un insert (cisaillement roulant) — bloc en massif ou lamellé exigé. |
| essai requis | `bloc_essai` | Essai d'arrachement réel de l'insert dans le bloc (série et bois réels). |
| ok | `bloc_ancrage_dimensions` | Bloc d'ancrage recalculé : 50 × 80 × 80 mm, 2 tourillons Ø12, + 30 mm de flasque traversée. |
| ok | `stabilite_agenouille_au_nez` | Stabilité « agenouille_au_nez » : coefficient 9.70 (arête -y, minimum 1.5). Une personne (dynamique) agenouillée sur l'arête avant. |
| ok | `stabilite_assis_retombee` | Stabilité « assis_retombee » : coefficient 5.19 (arête +y, minimum 1.5). Une personne assise sur l'arête arrière du niveau haut. |
| ok | `stabilite_poussee_longitudinale` | Stabilité « poussee_longitudinale » : coefficient 3.62 (arête -x, minimum 1.5). Une personne assise en bout + poussée de 300 N. |
| AVERTISSEMENT (compromis) | `traction_exterieure_ancrage` | Traction extérieure de 1500 N à 493 mm, meuble vide : coefficient 0.91. Les ancrages servent à retenir une personne installée sur le meuble ; ne jamais les relier à un point extérieur ni tirer depuis l'extérieur. |
| essai requis | `essai_statique` | Essai statique de la surface : 3 × charge de service, 10 min, sans rupture ni déformation permanente (type EN 1728 adapté). |
| essai requis | `essai_fatigue` | Essai de fatigue des assemblages (cycles d'assise/rythme) — référence EN 1728 / EN 12520, à adapter à l'usage. |
| essai requis | `essai_ancrages` | Essai de traction de chaque ancrage à 3 × 1500 N, sur prototype. |
| essai requis | `visa_ingenieur` | Modèles simplifiés : visa d'un ingénieur structure avant série. |

Ancrages (FIXE) :

* `ancrage_1g` — (0, 200, 286) mm, dans `banquette_bloc_ancrage_1g` : Insert inox M12 traversant la flasque, anneau rabattable affleurant.
* `ancrage_1d` — (1500, 200, 286) mm, dans `banquette_bloc_ancrage_1d` : Insert inox M12 traversant la flasque, anneau rabattable affleurant.
* `ancrage_2g` — (0, 731, 493) mm, dans `banquette_bloc_ancrage_2g` : Insert inox M12 traversant la flasque, anneau rabattable affleurant.
* `ancrage_2d` — (1500, 731, 493) mm, dans `banquette_bloc_ancrage_2d` : Insert inox M12 traversant la flasque, anneau rabattable affleurant.
* `ancrage_3g` — (0, 930, 460) mm, dans `banquette_bloc_ancrage_3g` : Insert inox M12 traversant la flasque, anneau rabattable affleurant.
* `ancrage_3d` — (1500, 930, 460) mm, dans `banquette_bloc_ancrage_3d` : Insert inox M12 traversant la flasque, anneau rabattable affleurant.

### Chiffrage indicatif (estimation datée de novembre 2026, HT sauf mention)

| Poste | Montant |
|---|---|
| Bois (pertes comprises) | 426 € |
| Mousses | 34 € |
| Revêtements (+25 % de chutes) | 244 € |
| Quincaillerie | 263 € |
| Finition + emballage | 155 € |
| Amortissement moules | 120 € |
| Main-d'œuvre (48.1 h ébénisterie + 4.4 h tapisserie) | 3017 € |
| **Coût de revient** | **4260 € HT** |
| Prix de vente indicatif (× 1,45) | 6180 € HT — **7410 € TTC** (fourchette 5550–9250 €) |
| Prototype unitaire | ≈ 20300 € TTC |

### Paramètres Fusion propres à la typologie

* `tan_banquette2n_profondeur_niveau_bas` = 480 mm — Profondeur utile du niveau bas.
* `tan_banquette2n_pente_contremarche` = 72 deg — Pente de la contremarche arrondie.
* `tan_banquette2n_n_flasques` = 6  — Nombre de flasques (calculé).

<!-- FIN GENERE -->
