# Desserte → cadre à genoux (volet 3 — cadre de contention transformable)

**Principe : le meuble est la structure du cadre.** Aucune pièce n'est ajoutée ni retirée entre
les états (un test le vérifie).

* **MEUBLE** : desserte en chêne de 1 000 × 420 × 750 mm, avec une tablette basse. Le bandeau
  arrière du plateau est en réalité la **barre haute** du cadre. Il est tenonné (enfourchement
  chevillé) sur deux **montants télescopiques** en lamellé de hêtre 70 × 70 qui coulissent dans
  des **fourreaux** de chêne de 110 × 110 (les pieds arrière).
* **CADRE** :
  1. On tire les deux doigts d'indexage et on lève la barre de 400 mm, aidé par des vérins à gaz
     moins forts que le poids : la barre ne monte jamais seule. Les doigts se ré-enclenchent
     seuls, puis on engage les goupilles captives.
  2. On fait basculer la tablette de 180° vers l'avant autour de son axe traversant Ø16. Sa face
     rembourrée passe dessus et devient un **agenouilloir** (dessus à 180 mm), porté à l'avant par
     deux pieds pivotants. Elle est verrouillée par un doigt d'indexage et une goupille.

La personne s'agenouille, buste sur le plateau (pupitre), poignets à la barre (1 150 mm),
chevilles au nez de l'agenouilloir. Elle est **sur** le meuble : les tractions sur les ancrages
sont des efforts internes.

## Mécanismes étudiés

| Mécanisme | Verdict |
|---|---|
| Pantographe | écarté : trop d'articulations à verrouiller, jeu cumulé, pincements multiples |
| Compas (contrefiches) | retenu pour la table inclinée (fiche), pas ici |
| Charnières à axe traversant | retenu : agenouilloir (Ø16 inox, bagues POM) |
| Montants télescopiques | retenu : barre haute ; recouvrement ≥ 3 × section |
| Pivots à index | retenu : verrou primaire (doigt d'indexage à ressort) |
| Verrou à came | utilisé seulement comme anti-jeu : ce n'est pas un verrou de forme, il ne compte pas dans la double sécurité |

## Verrouillages, pincement, déverrouillage sous charge

* Double sécurité sur chaque liaison qui maintient l'état CADRE :
  * deux verrous de forme ;
  * chacun seul à CS ≥ 3, en comptant la portance du bois (EC5 8.32 × 0,7) ;
  * l'un s'enclenche seul ;
  * les deux sont captifs.
* **Pincement** (EN ISO 13854) :
  * ombre de 30 mm entre la barre et le haut des fourreaux (≥ 25) ;
  * jeux de cisaillement de 6 mm barre/plateau et tablette/pieds (≤ 8).
* **Déverrouillage sous charge** : sous 25 % de la charge, la force de retrait du doigt dépasse
  60 N. Séquence imposée : décharger puis déverrouiller.
* **Effort de manœuvre** : ≤ 150 N.

## Compromis

* **Hauteur de barre / recouvrement** : avec une desserte de 750 mm, un télescope à un étage
  donne au mieux une barre à ~1 150 mm, recouvrement 3 × 70 mm compris. À 1 250 mm la grammaire
  passe en non conforme (test) : il faudrait un télescope à deux étages, plus cher et avec plus
  de jeu.
* **Stabilité à vide** : si quelqu'un tire la barre vers l'avant (300 N) alors que personne n'est
  à genoux, le coefficient vaut 0,48. Un **tirant mural** (≈ 590 N, patte à crochet en tête de
  fourreau) est prévu par défaut ; sans lui, la grammaire refuse.
* Pieds arrière massifs (110 mm) : ils se lisent comme un choix de dessin, mais ils signent le
  meuble.

<!-- DEBUT GENERE -->

## Résultats calculés (générés par `python -m tantra.rapport`)

| État | Hors-tout l × p × h (mm) | Masse (kg) | Pièces | Ancrages | Conforme |
|---|---|---|---|---|---|
| MEUBLE | 1000 × 420 × 750 | 37.8 | 19 | 4 | oui |
| CADRE | 1000 × 680 × 1150 | 37.9 | 19 | 4 | oui |

### Vérifications — état MEUBLE

| Niveau | Code | Détail |
|---|---|---|
| ok | `telescope_recouvrement` | Recouvrement en CADRE 230 mm pour une section de 70 mm (≥ 3 × section = 210). Course 400 mm. Au-delà, prévoir un télescope à deux étages (coût, jeu). |
| ok | `montant_flexion` | Montant 70×70 lamelle_hetre en console de 500 mm, 1500 N horizontal en tête : CS 5.7. |
| ok | `montant_appui_fourreau` | Pression de contact montant/fourreau ≈ 1.6 MPa (couple repris par le recouvrement, bagues POM). |
| ok | `barre_flexion` | Barre 60×70 chêne, portée 890 mm, deux poignets à ±250 mm (2 × 1500 N) : CS vertical 5.3, horizontal 4.6. |
| ok | `insert_barre` | Insert vertical dans la barre : largeur 60 mm (besoin 50) × profondeur 70 mm (besoin 70 = encastrement 60 + recouvrement 10). |
| ok | `insert_nez_tablette` | Insert horizontal dans le nez de tablette : largeur 65 mm (besoin 50) × profondeur 70 mm (besoin 60 = encastrement 60 + recouvrement 0). |
| ok | `enfourchement_barre` | Enfourchement barre/montant (23 × 60 mm) chevillé par 2 tourillons Ø12 traversants, 1500 N : CS 7.2. |
| ok | `telescope_double_securite` | telescope : 2 verrou(s) de forme indépendants (2 exigés). |
| ok | `telescope_verrou_1_seul` | telescope — Doigt d'indexage à ressort Ø16 seul : R_k ≈ 84.4 kN pour 1500 N, CS 56.3 (≥ 3 exigé, verrou seul). |
| ok | `telescope_verrou_2_seul` | telescope — Goupille à bille Ø12 inox sur câble seul : R_k ≈ 95.0 kN pour 1500 N, CS 63.3 (≥ 3 exigé, verrou seul). |
| ok | `telescope_auto_enclenchement` | telescope : au moins un verrou à ressort qui s'enclenche seul en fin de course. |
| ok | `telescope_imperdables` | telescope : verrous captifs (aucune pièce volante). |
| ok | `telescope_verrou_1_bois` | telescope — Doigt d'indexage à ressort Ø16 dans chene (paroi 20 mm) : R ≈ 8.5 kN (min acier / portance bois), CS 5.7. |
| ok | `telescope_verrou_2_bois` | telescope — Goupille à bille Ø12 inox sur câble dans chene (paroi 20 mm) : R ≈ 13.3 kN (min acier / portance bois), CS 8.9. |
| ok | `telescope_deverrouillage_sous_charge` | telescope — Doigt d'indexage à ressort Ø16 : force de retrait ≈ 152 N sous 25 % de la charge de service (375 N, μ = 0.3). Retrait à la main improbable sous charge. |
| ok | `agenouilloir_double_securite` | agenouilloir : 2 verrou(s) de forme indépendants (2 exigés). |
| ok | `agenouilloir_verrou_1_seul` | agenouilloir — Doigt d'indexage à ressort Ø12, bouton à cran de repos seul : R_k ≈ 47.5 kN pour 1500 N, CS 31.7 (≥ 3 exigé, verrou seul). |
| ok | `agenouilloir_verrou_2_seul` | agenouilloir — Goupille à bille Ø10 inox sur câble seul : R_k ≈ 66.0 kN pour 1500 N, CS 44.0 (≥ 3 exigé, verrou seul). |
| ok | `agenouilloir_auto_enclenchement` | agenouilloir : au moins un verrou à ressort qui s'enclenche seul en fin de course. |
| ok | `agenouilloir_imperdables` | agenouilloir : verrous captifs (aucune pièce volante). |
| ok | `agenouilloir_verrou_1_bois` | agenouilloir — Doigt d'indexage à ressort Ø12, bouton à cran de repos dans chene (paroi 22.5 mm) : R ≈ 7.5 kN (min acier / portance bois), CS 5.0. |
| ok | `agenouilloir_verrou_2_bois` | agenouilloir — Goupille à bille Ø10 inox sur câble dans chene (paroi 22.5 mm) : R ≈ 12.8 kN (min acier / portance bois), CS 8.5. |
| ok | `agenouilloir_deverrouillage_sous_charge` | agenouilloir — Doigt d'indexage à ressort Ø12, bouton à cran de repos : force de retrait ≈ 138 N sous 25 % de la charge de service (375 N, μ = 0.3). Retrait à la main improbable sous charge. |
| ok | `axe_tablette` | Axe Ø16 de la tablette dans le pied avant 45 mm : CS 15.3 (portance du bois des joues). |
| ok | `tablette_flexion` | Tablette 25 mm sur 778 mm entre pieds pivotants, 990 N : CS 5.7. |
| ok | `plateau_appui_buste` | Plateau en appui de buste : CS 8.7. |
| ok | `pincement_barre_fourreau_fin_course` | Jeu « barre_fourreau_fin_course » = 30 mm : zone interdite ]8 ; 25[ mm (doigts, EN ISO 13854). Conforme. |
| ok | `pincement_barre_plateau_cisaillement` | Jeu « barre_plateau_cisaillement » = 6 mm : zone interdite ]8 ; 25[ mm (doigts, EN ISO 13854). Conforme. |
| ok | `pincement_tablette_pieds_avant` | Jeu « tablette_pieds_avant » = 6 mm : zone interdite ]8 ; 25[ mm (doigts, EN ISO 13854). Conforme. |
| ok | `descente_amortie` | Descente de la barre freinée par vérins à gaz (pas de chute libre sur les mains). |
| ok | `pas_de_montee_spontanee` | Vérins (2 × 30 N) moins forts que le poids mobile (80 N) : la barre ne monte pas seule au déverrouillage. |
| ok | `effort_levage_barre` | Levage barre + montants (8.2 kg) : 20 N à deux mains, vérins déduits. |
| ok | `effort_bascule_tablette` | Bascule de la tablette (5.3 kg) : ≈ 26 N en début de mouvement. |
| ok | `stabilite_desserte_appui_bord` | Stabilité « desserte_appui_bord » : coefficient ∞ (arête —, minimum 1.5). Appui vertical de 300 N au bord avant du plateau (type EN 12521). |
| ok | `stabilite_desserte_poussee` | Stabilité « desserte_poussee » : coefficient 1.26 (arête -y, minimum 1.2). Idem + 100 N horizontal vers l'avant. |
| essai requis | `essai_statique` | Essai statique de la surface : 3 × charge de service, 10 min, sans rupture ni déformation permanente (type EN 1728 adapté). |
| essai requis | `essai_fatigue` | Essai de fatigue des assemblages (cycles d'assise/rythme) — référence EN 1728 / EN 12520, à adapter à l'usage. |
| essai requis | `essai_ancrages` | Essai de traction de chaque ancrage à 3 × 1500 N, sur prototype. |
| essai requis | `visa_ingenieur` | Modèles simplifiés : visa d'un ingénieur structure avant série. |
| essai requis | `essai_verrous` | Essai de chaque liaison verrouillée : 3 × charge, un verrou retiré, puis 1000 cycles de manœuvre (usure des doigts/bagues). |

Ancrages (MEUBLE) :

* `ancrage_poignet_1` — (250, 360, 750) mm, dans `desserte_barre_haute` : Insert vertical sur le dessus de la barre, cache affleurant en MEUBLE.
* `ancrage_poignet_2` — (750, 360, 750) mm, dans `desserte_barre_haute` : Insert vertical sur le dessus de la barre, cache affleurant en MEUBLE.
* `ancrage_cheville_1` — (350, 305, 148) mm, dans `desserte_nez_tablette` : Insert horizontal dans le nez de la tablette (face cachée en MEUBLE).
* `ancrage_cheville_2` — (650, 305, 148) mm, dans `desserte_nez_tablette` : Insert horizontal dans le nez de la tablette (face cachée en MEUBLE).

### Vérifications — état CADRE

| Niveau | Code | Détail |
|---|---|---|
| ok | `telescope_recouvrement` | Recouvrement en CADRE 230 mm pour une section de 70 mm (≥ 3 × section = 210). Course 400 mm. Au-delà, prévoir un télescope à deux étages (coût, jeu). |
| ok | `montant_flexion` | Montant 70×70 lamelle_hetre en console de 500 mm, 1500 N horizontal en tête : CS 5.7. |
| ok | `montant_appui_fourreau` | Pression de contact montant/fourreau ≈ 1.6 MPa (couple repris par le recouvrement, bagues POM). |
| ok | `barre_flexion` | Barre 60×70 chêne, portée 890 mm, deux poignets à ±250 mm (2 × 1500 N) : CS vertical 5.3, horizontal 4.6. |
| ok | `insert_barre` | Insert vertical dans la barre : largeur 60 mm (besoin 50) × profondeur 70 mm (besoin 70 = encastrement 60 + recouvrement 10). |
| ok | `insert_nez_tablette` | Insert horizontal dans le nez de tablette : largeur 65 mm (besoin 50) × profondeur 70 mm (besoin 60 = encastrement 60 + recouvrement 0). |
| ok | `enfourchement_barre` | Enfourchement barre/montant (23 × 60 mm) chevillé par 2 tourillons Ø12 traversants, 1500 N : CS 7.2. |
| ok | `telescope_double_securite` | telescope : 2 verrou(s) de forme indépendants (2 exigés). |
| ok | `telescope_verrou_1_seul` | telescope — Doigt d'indexage à ressort Ø16 seul : R_k ≈ 84.4 kN pour 1500 N, CS 56.3 (≥ 3 exigé, verrou seul). |
| ok | `telescope_verrou_2_seul` | telescope — Goupille à bille Ø12 inox sur câble seul : R_k ≈ 95.0 kN pour 1500 N, CS 63.3 (≥ 3 exigé, verrou seul). |
| ok | `telescope_auto_enclenchement` | telescope : au moins un verrou à ressort qui s'enclenche seul en fin de course. |
| ok | `telescope_imperdables` | telescope : verrous captifs (aucune pièce volante). |
| ok | `telescope_verrou_1_bois` | telescope — Doigt d'indexage à ressort Ø16 dans chene (paroi 20 mm) : R ≈ 8.5 kN (min acier / portance bois), CS 5.7. |
| ok | `telescope_verrou_2_bois` | telescope — Goupille à bille Ø12 inox sur câble dans chene (paroi 20 mm) : R ≈ 13.3 kN (min acier / portance bois), CS 8.9. |
| ok | `telescope_deverrouillage_sous_charge` | telescope — Doigt d'indexage à ressort Ø16 : force de retrait ≈ 152 N sous 25 % de la charge de service (375 N, μ = 0.3). Retrait à la main improbable sous charge. |
| ok | `agenouilloir_double_securite` | agenouilloir : 2 verrou(s) de forme indépendants (2 exigés). |
| ok | `agenouilloir_verrou_1_seul` | agenouilloir — Doigt d'indexage à ressort Ø12, bouton à cran de repos seul : R_k ≈ 47.5 kN pour 1500 N, CS 31.7 (≥ 3 exigé, verrou seul). |
| ok | `agenouilloir_verrou_2_seul` | agenouilloir — Goupille à bille Ø10 inox sur câble seul : R_k ≈ 66.0 kN pour 1500 N, CS 44.0 (≥ 3 exigé, verrou seul). |
| ok | `agenouilloir_auto_enclenchement` | agenouilloir : au moins un verrou à ressort qui s'enclenche seul en fin de course. |
| ok | `agenouilloir_imperdables` | agenouilloir : verrous captifs (aucune pièce volante). |
| ok | `agenouilloir_verrou_1_bois` | agenouilloir — Doigt d'indexage à ressort Ø12, bouton à cran de repos dans chene (paroi 22.5 mm) : R ≈ 7.5 kN (min acier / portance bois), CS 5.0. |
| ok | `agenouilloir_verrou_2_bois` | agenouilloir — Goupille à bille Ø10 inox sur câble dans chene (paroi 22.5 mm) : R ≈ 12.8 kN (min acier / portance bois), CS 8.5. |
| ok | `agenouilloir_deverrouillage_sous_charge` | agenouilloir — Doigt d'indexage à ressort Ø12, bouton à cran de repos : force de retrait ≈ 138 N sous 25 % de la charge de service (375 N, μ = 0.3). Retrait à la main improbable sous charge. |
| ok | `axe_tablette` | Axe Ø16 de la tablette dans le pied avant 45 mm : CS 15.3 (portance du bois des joues). |
| ok | `tablette_flexion` | Tablette 25 mm sur 778 mm entre pieds pivotants, 990 N : CS 5.7. |
| ok | `plateau_appui_buste` | Plateau en appui de buste : CS 8.7. |
| ok | `pincement_barre_fourreau_fin_course` | Jeu « barre_fourreau_fin_course » = 30 mm : zone interdite ]8 ; 25[ mm (doigts, EN ISO 13854). Conforme. |
| ok | `pincement_barre_plateau_cisaillement` | Jeu « barre_plateau_cisaillement » = 6 mm : zone interdite ]8 ; 25[ mm (doigts, EN ISO 13854). Conforme. |
| ok | `pincement_tablette_pieds_avant` | Jeu « tablette_pieds_avant » = 6 mm : zone interdite ]8 ; 25[ mm (doigts, EN ISO 13854). Conforme. |
| ok | `descente_amortie` | Descente de la barre freinée par vérins à gaz (pas de chute libre sur les mains). |
| ok | `pas_de_montee_spontanee` | Vérins (2 × 30 N) moins forts que le poids mobile (80 N) : la barre ne monte pas seule au déverrouillage. |
| ok | `effort_levage_barre` | Levage barre + montants (8.2 kg) : 20 N à deux mains, vérins déduits. |
| ok | `effort_bascule_tablette` | Bascule de la tablette (5.3 kg) : ≈ 26 N en début de mouvement. |
| ok | `stabilite_agenouille_pousse_avant` | Stabilité « agenouille_pousse_avant » : coefficient 2.26 (arête +y, minimum 1.5). À genoux, buste sur le plateau, poussée de 300 N vers l'arrière en haut de la barre. |
| ok | `stabilite_agenouille_tire_vers_soi` | Stabilité « agenouille_tire_vers_soi » : coefficient 1.67 (arête -y, minimum 1.5). À genoux, traction de 300 N vers l'avant en haut de la barre (partenaire). |
| ok | `stabilite_lateral` | Stabilité « lateral » : coefficient 2.13 (arête -x, minimum 1.2). Poussée latérale 300 N en haut de la barre. |
| ok (compromis) | `stabilite_vide_traction_barre` | Cadre vide, traction de 300 N vers l'avant en haut de la barre : coefficient propre 0.48. Tirant mural requis ≈ 588 N (patte à crochet en tête de fourreau, cheville adaptée au mur) — prévu. |
| essai requis | `essai_statique` | Essai statique de la surface : 3 × charge de service, 10 min, sans rupture ni déformation permanente (type EN 1728 adapté). |
| essai requis | `essai_fatigue` | Essai de fatigue des assemblages (cycles d'assise/rythme) — référence EN 1728 / EN 12520, à adapter à l'usage. |
| essai requis | `essai_ancrages` | Essai de traction de chaque ancrage à 3 × 1500 N, sur prototype. |
| essai requis | `visa_ingenieur` | Modèles simplifiés : visa d'un ingénieur structure avant série. |
| essai requis | `essai_verrous` | Essai de chaque liaison verrouillée : 3 × charge, un verrou retiré, puis 1000 cycles de manœuvre (usure des doigts/bagues). |

Ancrages (CADRE) :

* `ancrage_poignet_1` — (250, 360, 1150) mm, dans `desserte_barre_haute` : Insert vertical sur le dessus de la barre, cache affleurant en MEUBLE.
* `ancrage_poignet_2` — (750, 360, 1150) mm, dans `desserte_barre_haute` : Insert vertical sur le dessus de la barre, cache affleurant en MEUBLE.
* `ancrage_cheville_1` — (350, -260, 148) mm, dans `desserte_nez_tablette` : Insert horizontal dans le nez de la tablette (face cachée en MEUBLE).
* `ancrage_cheville_2` — (650, -260, 148) mm, dans `desserte_nez_tablette` : Insert horizontal dans le nez de la tablette (face cachée en MEUBLE).

### Chiffrage indicatif (estimation datée de novembre 2026, HT sauf mention)

| Poste | Montant |
|---|---|
| Bois (pertes comprises) | 217 € |
| Mousses | 5 € |
| Revêtements (+25 % de chutes) | 41 € |
| Quincaillerie | 435 € |
| Finition + emballage | 89 € |
| Amortissement moules | 0 € |
| Main-d'œuvre (28.5 h ébénisterie + 2.0 h tapisserie) | 1758 € |
| **Coût de revient** | **2550 € HT** |
| Prix de vente indicatif (× 1,45) | 3690 € HT — **4430 € TTC** (fourchette 3300–5550 €) |
| Prototype unitaire | ≈ 9000 € TTC |

### Paramètres Fusion propres à la typologie

* `tan_desserte_etat` = 0  — 0 = MEUBLE, 1 = CADRE.
* `tan_desserte_section_montant` = 70 mm — Section des montants télescopiques.
* `tan_desserte_section_fourreau` = 110 mm — Section des fourreaux (pieds arrière).
* `tan_desserte_jeu_fin_course` = 30 mm — Ombre anti-écrasement barre / fourreaux.

Changer `tan_desserte_etat` puis relancer le script régénère l'autre état.

<!-- FIN GENERE -->
