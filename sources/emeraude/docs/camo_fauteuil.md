# Fauteuil bergère à repose-genoux escamotable (volet 2 — camouflable)

**Principe :** à l'état **SALON**, une bergère classique. À l'état **RÉVÉLÉ** :

* la **façade d'assise** (bavette) pivote de 90° vers l'avant sur son chant bas ; sa face
  intérieure, rembourrée (HR55, 50 mm) et gainée de cuir lavable, devient un **repose-genoux** à
  215 mm du sol ;
* les **béquilles** (2, ou 3 si le calcul l'exige) se déplient sous le nez du repose-genoux.
  Elles touchent le sol et élargissent l'empreinte vers l'avant ;
* les **manchettes** découvrent deux inserts (poignets) ; la bavette ouverte découvre deux
  inserts dans la traverse avant (chevilles/genoux).

Position type : à genoux sur le repose-genoux, buste sur l'assise.

## Grammaire (`camo_fauteuil.py`)

* Même socle `_salon.py` que le canapé : 1 galette, pas d'ancrage arrière, traverses 50 × 140 mm.
* `nombre_bequilles` réutilise la règle des supports de coque : flexion du contreplaqué de 25 mm
  sous 60 % du poids dynamique.
* Contrôles propres : flexion du repose-genoux, pincement au repliage des béquilles (30 mm),
  stabilité « à genoux » (béquilles au sol).

## Compromis

* Le repose-genoux est porté par les béquilles ; les charnières ne font que guider. L'essai doit
  le confirmer, et la grammaire émet un avertissement.
* Les béquilles repliées occupent une partie de l'épaisseur de mousse de la bavette.

<!-- DEBUT GENERE -->

## Résultats calculés (générés par `python -m tantra.rapport`)

| État | Hors-tout l × p × h (mm) | Masse (kg) | Pièces | Ancrages | Conforme |
|---|---|---|---|---|---|
| SALON | 784 × 822 × 900 | 55.0 | 36 | 4 | oui |
| REVELE | 784 × 1041 × 1250 | 55.2 | 36 | 4 | oui |

### Vérifications — état SALON

| Niveau | Code | Détail |
|---|---|---|
| ok | `discretion_ancrage_accoudoir_g` | ancrage_accoudoir_g masqué par « fauteuil_manchette_g » à l'état SALON. |
| ok | `discretion_ancrage_accoudoir_d` | ancrage_accoudoir_d masqué par « fauteuil_manchette_d » à l'état SALON. |
| ok | `discretion_ancrage_avant_1` | ancrage_avant_1 masqué par « fauteuil_bavette » à l'état SALON. |
| ok | `discretion_ancrage_avant_2` | ancrage_avant_2 masqué par « fauteuil_bavette » à l'état SALON. |
| ok | `insert_traverse_accoudoir` | Insert vertical dans la traverse d'accoudoir : largeur 60 mm (besoin 50) × profondeur 70 mm (besoin 60 = encastrement 60 + recouvrement 0). Recouvrement assuré par la manchette (pas de bois au-dessus). |
| ok | `insert_traverse_avant` | Insert horizontal dans la traverse avant : largeur 140 mm (besoin 50) × profondeur 70 mm (besoin 60 = encastrement 60 + recouvrement 0). Recouvrement assuré par la bavette. |
| ok | `traverse_avant_flexion` | Traverse avant 70×140 mm, portée 520 mm, deux ancrages tirés ensemble (2 × 1500 N, équivalent centré 0,75) : CS 15.6. |
| ok | `traverse_accoudoir_flexion` | Traverse d'accoudoir 60×70 mm, portée 580 mm, 1500 N vertical au milieu : CS 9.0. |
| ok | `tenons_traverse_accoudoir` | Tenons de la traverse d'accoudoir (20 × 55 mm), 750 N chacun : CS 3.9. |
| ok | `tenons_traverse_avant` | Tenons de la traverse avant (23 × 110 mm), 1500 N chacun (cas défavorable : un seul ancrage près d'un tenon) : CS 4.6. |
| ok | `charnieres_manchette` | Âme de manchette 22 mm (Soss n°208 : ≥ 22 mm). |
| ok | `effort_manchette` | Ouverture d'une manchette (1.4 kg) : ≈ 7 N à la main, loqueteaux compris. |
| ok | `pincement_manchette_charniere` | Jeu « manchette_charniere » = 3 mm : zone interdite ]8 ; 25[ mm (doigts, EN ISO 13854). Conforme. |
| ok | `fermeture_amortie` | Manchettes et bavette : fermeture sur butées caoutchouc + aimants, pas de ressort de rappel (aucune fermeture spontanée sur les doigts). |
| ok | `revetement_salon` | Revêtement « velours_deperlant » : aspect salon et lavable/déperlant. |
| ok | `repose_genoux_flexion` | Repose-genoux contreplaqué 25 mm, 2 béquilles (portée 480 mm), 60 % du poids dynamique (990 N) : CS 4.9. |
| ok | `charnieres_bavette_effort` | Bavette-genoux : l'effort vertical passe par les béquilles et le chant bas en appui sur la traverse ; les charnières Soss ne guident que la rotation (à confirmer à l'essai). |
| ok | `pincement_bequille_repliage` | Jeu « bequille_repliage » = 30 mm : zone interdite ]8 ; 25[ mm (doigts, EN ISO 13854). Conforme. |
| ok | `stabilite_assis_pousse_dossier` | Stabilité « assis_pousse_dossier » : coefficient 2.65 (arête +y, minimum 1.5). Personne assise, poussée de 300 N en haut du dossier. |
| ok | `stabilite_assis_sur_accoudoir` | Stabilité « assis_sur_accoudoir » : coefficient ∞ (arête —, minimum 1.2). Assis brusquement sur l'accoudoir. |
| AVERTISSEMENT (compromis) | `traction_exterieure_ancrage` | Traction extérieure de 1500 N à 583 mm, meuble vide : coefficient 0.25. Les ancrages servent à retenir une personne installée sur le meuble ; ne jamais les relier à un point extérieur ni tirer depuis l'extérieur. |
| essai requis | `essai_statique` | Essai statique de la surface : 3 × charge de service, 10 min, sans rupture ni déformation permanente (type EN 1728 adapté). |
| essai requis | `essai_fatigue` | Essai de fatigue des assemblages (cycles d'assise/rythme) — référence EN 1728 / EN 12520, à adapter à l'usage. |
| essai requis | `essai_ancrages` | Essai de traction de chaque ancrage à 3 × 1500 N, sur prototype. |
| essai requis | `visa_ingenieur` | Modèles simplifiés : visa d'un ingénieur structure avant série. |

Ancrages (SALON) :

* `ancrage_accoudoir_g` — (65, 410, 593) mm, dans `fauteuil_traverse_acc_g` : Insert vertical dans la traverse haute d'accoudoir.
* `ancrage_accoudoir_d` — (715, 410, 593) mm, dans `fauteuil_traverse_acc_d` : Insert vertical dans la traverse haute d'accoudoir.
* `ancrage_avant_1` — (260, 80, 220) mm, dans `fauteuil_traverse_avant` : Insert horizontal (axe y) dans la traverse avant.
* `ancrage_avant_2` — (520, 80, 220) mm, dans `fauteuil_traverse_avant` : Insert horizontal (axe y) dans la traverse avant.

### Vérifications — état REVELE

| Niveau | Code | Détail |
|---|---|---|
| ok | `acces_ancrage_accoudoir_g` | ancrage_accoudoir_g accessible à l'état RÉVÉLÉ. |
| ok | `acces_ancrage_accoudoir_d` | ancrage_accoudoir_d accessible à l'état RÉVÉLÉ. |
| ok | `acces_ancrage_avant_1` | ancrage_avant_1 accessible à l'état RÉVÉLÉ. |
| ok | `acces_ancrage_avant_2` | ancrage_avant_2 accessible à l'état RÉVÉLÉ. |
| ok | `insert_traverse_accoudoir` | Insert vertical dans la traverse d'accoudoir : largeur 60 mm (besoin 50) × profondeur 70 mm (besoin 60 = encastrement 60 + recouvrement 0). Recouvrement assuré par la manchette (pas de bois au-dessus). |
| ok | `insert_traverse_avant` | Insert horizontal dans la traverse avant : largeur 140 mm (besoin 50) × profondeur 70 mm (besoin 60 = encastrement 60 + recouvrement 0). Recouvrement assuré par la bavette. |
| ok | `traverse_avant_flexion` | Traverse avant 70×140 mm, portée 520 mm, deux ancrages tirés ensemble (2 × 1500 N, équivalent centré 0,75) : CS 15.6. |
| ok | `traverse_accoudoir_flexion` | Traverse d'accoudoir 60×70 mm, portée 580 mm, 1500 N vertical au milieu : CS 9.0. |
| ok | `tenons_traverse_accoudoir` | Tenons de la traverse d'accoudoir (20 × 55 mm), 750 N chacun : CS 3.9. |
| ok | `tenons_traverse_avant` | Tenons de la traverse avant (23 × 110 mm), 1500 N chacun (cas défavorable : un seul ancrage près d'un tenon) : CS 4.6. |
| ok | `charnieres_manchette` | Âme de manchette 22 mm (Soss n°208 : ≥ 22 mm). |
| ok | `effort_manchette` | Ouverture d'une manchette (1.4 kg) : ≈ 7 N à la main, loqueteaux compris. |
| ok | `pincement_manchette_charniere` | Jeu « manchette_charniere » = 3 mm : zone interdite ]8 ; 25[ mm (doigts, EN ISO 13854). Conforme. |
| ok | `fermeture_amortie` | Manchettes et bavette : fermeture sur butées caoutchouc + aimants, pas de ressort de rappel (aucune fermeture spontanée sur les doigts). |
| ok | `revetement_salon` | Revêtement « velours_deperlant » : aspect salon et lavable/déperlant. |
| ok | `repose_genoux_flexion` | Repose-genoux contreplaqué 25 mm, 2 béquilles (portée 480 mm), 60 % du poids dynamique (990 N) : CS 4.9. |
| ok | `charnieres_bavette_effort` | Bavette-genoux : l'effort vertical passe par les béquilles et le chant bas en appui sur la traverse ; les charnières Soss ne guident que la rotation (à confirmer à l'essai). |
| ok | `pincement_bequille_repliage` | Jeu « bequille_repliage » = 30 mm : zone interdite ]8 ; 25[ mm (doigts, EN ISO 13854). Conforme. |
| ok | `stabilite_assis_pousse_dossier` | Stabilité « assis_pousse_dossier » : coefficient 2.71 (arête +y, minimum 1.5). Personne assise, poussée de 300 N en haut du dossier. |
| ok | `stabilite_assis_sur_accoudoir` | Stabilité « assis_sur_accoudoir » : coefficient ∞ (arête —, minimum 1.2). Assis brusquement sur l'accoudoir. |
| ok | `stabilite_a_genoux` | Stabilité « a_genoux » : coefficient 2.88 (arête -y, minimum 1.5). À genoux sur le repose-genoux, buste sur l'assise, poussée vers l'avant. |
| AVERTISSEMENT (compromis) | `traction_exterieure_ancrage` | Traction extérieure de 1500 N à 583 mm, meuble vide : coefficient 0.25. Les ancrages servent à retenir une personne installée sur le meuble ; ne jamais les relier à un point extérieur ni tirer depuis l'extérieur. |
| essai requis | `essai_statique` | Essai statique de la surface : 3 × charge de service, 10 min, sans rupture ni déformation permanente (type EN 1728 adapté). |
| essai requis | `essai_fatigue` | Essai de fatigue des assemblages (cycles d'assise/rythme) — référence EN 1728 / EN 12520, à adapter à l'usage. |
| essai requis | `essai_ancrages` | Essai de traction de chaque ancrage à 3 × 1500 N, sur prototype. |
| essai requis | `visa_ingenieur` | Modèles simplifiés : visa d'un ingénieur structure avant série. |

Ancrages (REVELE) :

* `ancrage_accoudoir_g` — (65, 410, 593) mm, dans `fauteuil_traverse_acc_g` : Insert vertical dans la traverse haute d'accoudoir.
* `ancrage_accoudoir_d` — (715, 410, 593) mm, dans `fauteuil_traverse_acc_d` : Insert vertical dans la traverse haute d'accoudoir.
* `ancrage_avant_1` — (260, 80, 220) mm, dans `fauteuil_traverse_avant` : Insert horizontal (axe y) dans la traverse avant.
* `ancrage_avant_2` — (520, 80, 220) mm, dans `fauteuil_traverse_avant` : Insert horizontal (axe y) dans la traverse avant.

### Chiffrage indicatif (estimation datée de novembre 2026, HT sauf mention)

| Poste | Montant |
|---|---|
| Bois (pertes comprises) | 366 € |
| Mousses | 41 € |
| Revêtements (+25 % de chutes) | 290 € |
| Quincaillerie | 373 € |
| Finition + emballage | 103 € |
| Amortissement moules | 0 € |
| Main-d'œuvre (36.8 h ébénisterie + 8.1 h tapisserie) | 2556 € |
| **Coût de revient** | **3730 € HT** |
| Prix de vente indicatif (× 1,45) | 5410 € HT — **6490 € TTC** (fourchette 4850–8100 €) |
| Prototype unitaire | ≈ 13150 € TTC |

### Paramètres Fusion propres à la typologie

* `tan_bergere_etat` = 0  — 0 = SALON, 1 = RÉVÉLÉ.
* `tan_bergere_mousse_bavette` = 50 mm — Rembourrage du repose-genoux.
* `tan_bergere_largeur_accoudoir` = 130 mm — Largeur d'un accoudoir.

Changer `tan_bergere_etat` puis relancer le script régénère l'autre état.

<!-- FIN GENERE -->
