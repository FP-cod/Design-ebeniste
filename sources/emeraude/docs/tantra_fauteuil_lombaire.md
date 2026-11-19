# Fauteuil tantra à soutien lombaire (volet 1 — meuble fixe)

**Typologie :** fauteuil bas et profond, deux places en duo (une personne assise, l'autre à
califourchon) : cale avant relevée, bombé lombaire marqué, dossier incliné. Chêne massif, coque
en contreplaqué cintré, cuir.

## Grammaire (`tantra_fauteuil_lombaire.py`)

* Points clés : nez (0, z_cale − 45, 40°), cale (y 120), ischions, lombaire (200 mm au-dessus de
  l'assise, bombé de 25 mm), sommet du dossier. Pas de point de « pli » : tension 1,1 pour un
  raccord assise/dossier continu.
* **Profil de structure lissé** : la coque suit une ligne plus douce ; la cale et le nez sont
  formés dans la mousse HR55 (sinon le rayon de cintrage serait trop serré).
* Assise 340 mm inclinée de 12°, profondeur 440 mm, angle assise/dossier 108°, dossier 820 mm.
* 3 flasques de chêne 32 mm, coque 21 mm, socle 50 mm en retrait de 20 mm, 2 ancrages.

## Ergonomie

* assise ≤ hauteur poplitée P5 (355) + 20 mm : volontairement basse (posture enveloppée) ;
* profondeur ≤ fesse-poplité P5 + 10 mm ; centre lombaire 150 à 250 mm au-dessus de l'assise ;
* angle 100 à 115° ; dossier ≥ hauteur d'épaule assis P5 − 50 mm ; largeur ≥ hanches P95 + 2 × 100 mm.

## Compromis

* Assise basse : très confortable pour le duo, mais se relever est plus difficile pour un P95.
* Coque épaissie à 21 mm pour rester à 3 flasques (coût) plutôt que 4 flasques en 18 mm.

<!-- DEBUT GENERE -->

## Résultats calculés (générés par `python -m tantra.rapport`)

| État | Hors-tout l × p × h (mm) | Masse (kg) | Pièces | Ancrages | Conforme |
|---|---|---|---|---|---|
| FIXE | 760 × 889 × 820 | 43.8 | 20 | 2 | oui |

### Vérifications — état FIXE

| Niveau | Code | Détail |
|---|---|---|
| ok | `ergo_hauteur_assise` | Assise 340 mm ≤ poplité P5 355 + 20 mm : pieds au sol pour tous ; volontairement bas (genoux au-dessus des hanches pour P95 490 mm, posture enveloppée recherchée). |
| ok | `ergo_profondeur` | Profondeur utile 440 mm ≤ fesse-poplité P5 435 + 10 mm : un petit gabarit atteint le dossier sans compression du creux poplité. |
| ok | `ergo_lombaire` | Centre du bombé lombaire à 200 mm au-dessus de l'assise (plage 150–250 mm). |
| ok | `ergo_angle_dossier` | Angle assise/dossier 108° (100–115° : détente sans perdre le soutien lombaire ; au-delà, le bassin glisse en rétroversion). |
| ok | `ergo_hauteur_dossier` | Dossier 480 mm au-dessus de l'assise ≥ épaules P5 505 − 50 mm : omoplates soutenues ; nuque libre (pas d'appui-tête). |
| ok | `ergo_largeur_duo` | Largeur 760 mm ≥ hanches P95 435 + 2 × 100 mm (genoux de la personne assise à califourchon de part et d'autre). |
| ok | `coque_flexion` | Coque 21 mm : 3 flasques nécessaires pour une charge de genou 1650 N (bande 200 mm, CS 3) ; 3 prévues. |
| ok | `coque_cintrage` | Rayon mini de la coque ≈ 178 mm pour un rayon de cintrage mini 150 mm (plis de 1.5 mm). Faisable. |
| ok | `tenons_traverses` | Tenons des traverses (11 × 60 mm) : 412 N par tenon (toute la charge de 2 personne(s) par les traverses, part doublée pour l'excentrement), CS 4.1. |
| ok | `bloc_arrachement` | Arrachement insert : R_k ≈ 11.2 kN, CS 7.4 (visé ≥ 3) — formule EC5 des vis, par analogie. |
| ok | `bloc_paroi` | Parois 17.0 mm de part et d'autre de l'insert : CS cisaillement 5.4 (paroi mini calculée 9.4 mm). |
| ok | `bloc_essence` | Bloc en Chêne massif : un contreplaqué tient mal un insert (cisaillement roulant) — bloc en massif ou lamellé exigé. |
| essai requis | `bloc_essai` | Essai d'arrachement réel de l'insert dans le bloc (série et bois réels). |
| ok | `bloc_ancrage_dimensions` | Bloc d'ancrage recalculé : 50 × 80 × 80 mm, 2 tourillons Ø12, + 32 mm de flasque traversée. |
| ok | `stabilite_duo_assis_poussee_dossier` | Stabilité « duo_assis_poussee_dossier » : coefficient 4.97 (arête +y, minimum 1.5). Deux personnes assises + poussée de 300 N vers l'arrière en haut du dossier. |
| ok | `stabilite_assis_sur_le_nez` | Stabilité « assis_sur_le_nez » : coefficient ∞ (arête —, minimum 1.5). Une personne (dynamique) assise sur l'extrême avant de la cale. |
| ok | `stabilite_appui_sommet_dossier` | Stabilité « appui_sommet_dossier » : coefficient ∞ (arête —, minimum 1.5). Une personne appuyée sur le haut du dossier (par derrière). |
| ok | `stabilite_assis_bord_lateral` | Stabilité « assis_bord_lateral » : coefficient 1.95 (arête -x, minimum 1.2). Assis au bord + poussée latérale accidentelle. |
| AVERTISSEMENT (compromis) | `traction_exterieure_ancrage` | Traction extérieure de 1500 N à 233 mm, meuble vide : coefficient 0.44. Les ancrages servent à retenir une personne installée sur le meuble ; ne jamais les relier à un point extérieur ni tirer depuis l'extérieur. |
| essai requis | `essai_statique` | Essai statique de la surface : 3 × charge de service, 10 min, sans rupture ni déformation permanente (type EN 1728 adapté). |
| essai requis | `essai_fatigue` | Essai de fatigue des assemblages (cycles d'assise/rythme) — référence EN 1728 / EN 12520, à adapter à l'usage. |
| essai requis | `essai_ancrages` | Essai de traction de chaque ancrage à 3 × 1500 N, sur prototype. |
| essai requis | `visa_ingenieur` | Modèles simplifiés : visa d'un ingénieur structure avant série. |

Ancrages (FIXE) :

* `ancrage_1g` — (0, 160, 233) mm, dans `fauteuil_bloc_ancrage_1g` : Insert inox M12 traversant la flasque, anneau rabattable affleurant.
* `ancrage_1d` — (760, 160, 233) mm, dans `fauteuil_bloc_ancrage_1d` : Insert inox M12 traversant la flasque, anneau rabattable affleurant.

### Chiffrage indicatif (estimation datée de novembre 2026, HT sauf mention)

| Poste | Montant |
|---|---|
| Bois (pertes comprises) | 273 € |
| Mousses | 27 € |
| Revêtements (+25 % de chutes) | 127 € |
| Quincaillerie | 89 € |
| Finition + emballage | 93 € |
| Amortissement moules | 120 € |
| Main-d'œuvre (25.2 h ébénisterie + 3.0 h tapisserie) | 1616 € |
| **Coût de revient** | **2350 € HT** |
| Prix de vente indicatif (× 1,45) | 3400 € HT — **4080 € TTC** (fourchette 3050–5100 €) |
| Prototype unitaire | ≈ 13300 € TTC |

### Paramètres Fusion propres à la typologie

* `tan_lombaire_hauteur_cale` = 45 mm — Saillie de la cale fessière.
* `tan_lombaire_hauteur_lombaire` = 200 mm — Centre du bombé lombaire au-dessus de l'assise.
* `tan_lombaire_saillie_lombaire` = 25 mm — Saillie du bombé lombaire.
* `tan_lombaire_ep_flasque` = 32 mm — Épaisseur des flasques chêne.
* `tan_lombaire_ep_coque` = 21 mm — Épaisseur de la coque cintrée.

<!-- FIN GENERE -->
