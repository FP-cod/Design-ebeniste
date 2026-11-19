# Canapé deux places à ancrages escamotés (volet 2 — camouflable)

**Principe :** à l'état **SALON**, un canapé classique (dossier droit, accoudoirs pleins,
galettes, pieds fuseaux, velours déperlant). Aucun élément visible : ni anneau, ni vis, ni cuir
technique. À l'état **RÉVÉLÉ**, un geste par fonction :

1. **Manchettes d'accoudoir** : on soulève le dessus de l'accoudoir par l'arrière ; il pivote sur
   des charnières invisibles Soss à l'avant (ouverture 105°) et découvre un insert M12 vertical
   dans la traverse haute de l'accoudoir.
2. **Bavette** : le panneau tapissé qui habille la ceinture avant bascule vers l'avant sur son
   chant bas et découvre deux inserts horizontaux dans la traverse avant (chêne 70 mm).
3. **Galettes** : on les soulève ; deux inserts verticaux dans la traverse arrière sont fermés par
   des caches aimantés tapissés.

Les anneaux à épaulement se vissent seulement à l'usage et se rangent hors du meuble.
Différence avec la banquette Incognito : aucun coffre ni vérin ; seules des pièces tapissées
pivotent.

## Grammaire (`tantra/grammaires/camo_canape.py` + `_salon.py`)

* Une seule fonction `construire_salon` produit les deux états à partir des mêmes paramètres.
* `verifier_discretion` : en SALON, chaque ancrage doit être couvert par sa pièce (manchette
  au-dessus, bavette devant, galette au-dessus), sinon non conforme. En RÉVÉLÉ, les ancrages
  d'accoudoir et avant doivent être accessibles.
* `verifs_communes` contrôle :
  * que la pièce loge l'insert sans bloc rapporté (largeur ≥ 2 parois + Ø, profondeur ≥ 60 mm + recouvrement) ;
  * la flexion des traverses avant et d'accoudoir sous 1 500 N par ancrage, CS ≥ 3, et les tenons ;
  * l'épaisseur pour charnières Soss, l'effort d'ouverture et le pincement (jeu de charnière 3 mm) ;
  * la fermeture sans ressort et le revêtement.

## Compromis

* **Discrétion / tenue** : la traverse avant passe de 50 à 70 mm pour loger l'insert (60 mm
  d'encastrement). La grammaire refuse 50 mm, et un test le vérifie.
* **Effort extérieur** : comme tout meuble posé, le canapé basculerait sous une traction
  extérieure de 1 500 N ; les ancrages servent à retenir une personne **assise ou allongée
  dessus**.
* **Prix** : ≈ 8,3 k€ TTC en pièce artisanale, au-dessus du segment vide 1–3 k€ (voir étude de marché).

<!-- DEBUT GENERE -->

## Résultats calculés (générés par `python -m tantra.rapport`)

| État | Hors-tout l × p × h (mm) | Masse (kg) | Pièces | Ancrages | Conforme |
|---|---|---|---|---|---|
| SALON | 1754 × 902 × 860 | 103.6 | 34 | 6 | oui |
| REVELE | 1754 × 1137 × 1288 | 103.6 | 34 | 6 | oui |

### Vérifications — état SALON

| Niveau | Code | Détail |
|---|---|---|
| ok | `discretion_ancrage_accoudoir_g` | ancrage_accoudoir_g masqué par « canape_manchette_g » à l'état SALON. |
| ok | `discretion_ancrage_accoudoir_d` | ancrage_accoudoir_d masqué par « canape_manchette_d » à l'état SALON. |
| ok | `discretion_ancrage_avant_1` | ancrage_avant_1 masqué par « canape_bavette » à l'état SALON. |
| ok | `discretion_ancrage_avant_2` | ancrage_avant_2 masqué par « canape_bavette » à l'état SALON. |
| ok | `discretion_ancrage_arriere_1` | ancrage_arriere_1 masqué par « canape_galette_1 » à l'état SALON. |
| ok | `discretion_ancrage_arriere_2` | ancrage_arriere_2 masqué par « canape_galette_2 » à l'état SALON. |
| ok | `insert_traverse_accoudoir` | Insert vertical dans la traverse d'accoudoir : largeur 60 mm (besoin 50) × profondeur 70 mm (besoin 60 = encastrement 60 + recouvrement 0). Recouvrement assuré par la manchette (pas de bois au-dessus). |
| ok | `insert_traverse_avant` | Insert horizontal dans la traverse avant : largeur 160 mm (besoin 50) × profondeur 70 mm (besoin 60 = encastrement 60 + recouvrement 0). Recouvrement assuré par la bavette. |
| ok | `insert_traverse_arriere` | Insert vertical dans la traverse arrière : largeur 50 mm (besoin 50) × profondeur 160 mm (besoin 70 = encastrement 60 + recouvrement 10), cache aimanté affleurant. |
| ok | `traverse_avant_flexion` | Traverse avant 70×160 mm, portée 1410 mm, deux ancrages tirés ensemble (2 × 1500 N, équivalent centré 0,75) : CS 6.6. |
| ok | `traverse_accoudoir_flexion` | Traverse d'accoudoir 60×70 mm, portée 640 mm, 1500 N vertical au milieu : CS 8.2. |
| ok | `tenons_traverse_accoudoir` | Tenons de la traverse d'accoudoir (20 × 55 mm), 750 N chacun : CS 3.9. |
| ok | `tenons_traverse_avant` | Tenons de la traverse avant (23 × 130 mm), 1500 N chacun (cas défavorable : un seul ancrage près d'un tenon) : CS 5.4. |
| ok | `charnieres_manchette` | Âme de manchette 22 mm (Soss n°208 : ≥ 22 mm). |
| ok | `effort_manchette` | Ouverture d'une manchette (2.0 kg) : ≈ 10 N à la main, loqueteaux compris. |
| ok | `pincement_manchette_charniere` | Jeu « manchette_charniere » = 3 mm : zone interdite ]8 ; 25[ mm (doigts, EN ISO 13854). Conforme. |
| ok | `fermeture_amortie` | Manchettes et bavette : fermeture sur butées caoutchouc + aimants, pas de ressort de rappel (aucune fermeture spontanée sur les doigts). |
| ok | `revetement_salon` | Revêtement « velours_deperlant » : aspect salon et lavable/déperlant. |
| ok | `stabilite_deux_assis_pousse_dossier` | Stabilité « deux_assis_pousse_dossier » : coefficient 6.18 (arête +y, minimum 1.5). Deux personnes assises, poussée de 300 N vers l'arrière en haut du dossier. |
| ok | `stabilite_assis_sur_accoudoir` | Stabilité « assis_sur_accoudoir » : coefficient ∞ (arête —, minimum 1.2). Une personne assise brusquement sur l'accoudoir gauche (porte-à-faux latéral). |
| ok | `stabilite_bord_avant` | Stabilité « bord_avant » : coefficient 3.45 (arête -y, minimum 1.5). Personne sur le bord avant (état RÉVÉLÉ, ancrages avant), poussée vers l'avant. |
| AVERTISSEMENT (compromis) | `traction_exterieure_ancrage` | Traction extérieure de 1500 N à 563 mm, meuble vide : coefficient 0.54. Les ancrages servent à retenir une personne installée sur le meuble ; ne jamais les relier à un point extérieur ni tirer depuis l'extérieur. |
| essai requis | `essai_statique` | Essai statique de la surface : 3 × charge de service, 10 min, sans rupture ni déformation permanente (type EN 1728 adapté). |
| essai requis | `essai_fatigue` | Essai de fatigue des assemblages (cycles d'assise/rythme) — référence EN 1728 / EN 12520, à adapter à l'usage. |
| essai requis | `essai_ancrages` | Essai de traction de chaque ancrage à 3 × 1500 N, sur prototype. |
| essai requis | `visa_ingenieur` | Modèles simplifiés : visa d'un ingénieur structure avant série. |

Ancrages (SALON) :

* `ancrage_accoudoir_g` — (85, 440, 573) mm, dans `canape_traverse_acc_g` : Insert vertical dans la traverse haute d'accoudoir.
* `ancrage_accoudoir_d` — (1665, 440, 573) mm, dans `canape_traverse_acc_d` : Insert vertical dans la traverse haute d'accoudoir.
* `ancrage_avant_1` — (522, 30, 220) mm, dans `canape_traverse_avant` : Insert horizontal (axe y) dans la traverse avant.
* `ancrage_avant_2` — (1228, 30, 220) mm, dans `canape_traverse_avant` : Insert horizontal (axe y) dans la traverse avant.
* `ancrage_arriere_1` — (522, 675, 300) mm, dans `canape_traverse_arriere` : Insert vertical sous galette, cache aimanté tapissé (accès : soulever la galette).
* `ancrage_arriere_2` — (1228, 675, 300) mm, dans `canape_traverse_arriere` : Insert vertical sous galette, cache aimanté tapissé (accès : soulever la galette).

### Vérifications — état REVELE

| Niveau | Code | Détail |
|---|---|---|
| ok | `acces_ancrage_accoudoir_g` | ancrage_accoudoir_g accessible à l'état RÉVÉLÉ. |
| ok | `acces_ancrage_accoudoir_d` | ancrage_accoudoir_d accessible à l'état RÉVÉLÉ. |
| ok | `acces_ancrage_avant_1` | ancrage_avant_1 accessible à l'état RÉVÉLÉ. |
| ok | `acces_ancrage_avant_2` | ancrage_avant_2 accessible à l'état RÉVÉLÉ. |
| ok | `insert_traverse_accoudoir` | Insert vertical dans la traverse d'accoudoir : largeur 60 mm (besoin 50) × profondeur 70 mm (besoin 60 = encastrement 60 + recouvrement 0). Recouvrement assuré par la manchette (pas de bois au-dessus). |
| ok | `insert_traverse_avant` | Insert horizontal dans la traverse avant : largeur 160 mm (besoin 50) × profondeur 70 mm (besoin 60 = encastrement 60 + recouvrement 0). Recouvrement assuré par la bavette. |
| ok | `insert_traverse_arriere` | Insert vertical dans la traverse arrière : largeur 50 mm (besoin 50) × profondeur 160 mm (besoin 70 = encastrement 60 + recouvrement 10), cache aimanté affleurant. |
| ok | `traverse_avant_flexion` | Traverse avant 70×160 mm, portée 1410 mm, deux ancrages tirés ensemble (2 × 1500 N, équivalent centré 0,75) : CS 6.6. |
| ok | `traverse_accoudoir_flexion` | Traverse d'accoudoir 60×70 mm, portée 640 mm, 1500 N vertical au milieu : CS 8.2. |
| ok | `tenons_traverse_accoudoir` | Tenons de la traverse d'accoudoir (20 × 55 mm), 750 N chacun : CS 3.9. |
| ok | `tenons_traverse_avant` | Tenons de la traverse avant (23 × 130 mm), 1500 N chacun (cas défavorable : un seul ancrage près d'un tenon) : CS 5.4. |
| ok | `charnieres_manchette` | Âme de manchette 22 mm (Soss n°208 : ≥ 22 mm). |
| ok | `effort_manchette` | Ouverture d'une manchette (2.0 kg) : ≈ 10 N à la main, loqueteaux compris. |
| ok | `pincement_manchette_charniere` | Jeu « manchette_charniere » = 3 mm : zone interdite ]8 ; 25[ mm (doigts, EN ISO 13854). Conforme. |
| ok | `fermeture_amortie` | Manchettes et bavette : fermeture sur butées caoutchouc + aimants, pas de ressort de rappel (aucune fermeture spontanée sur les doigts). |
| ok | `revetement_salon` | Revêtement « velours_deperlant » : aspect salon et lavable/déperlant. |
| ok | `stabilite_deux_assis_pousse_dossier` | Stabilité « deux_assis_pousse_dossier » : coefficient 6.27 (arête +y, minimum 1.5). Deux personnes assises, poussée de 300 N vers l'arrière en haut du dossier. |
| ok | `stabilite_assis_sur_accoudoir` | Stabilité « assis_sur_accoudoir » : coefficient ∞ (arête —, minimum 1.2). Une personne assise brusquement sur l'accoudoir gauche (porte-à-faux latéral). |
| ok | `stabilite_bord_avant` | Stabilité « bord_avant » : coefficient 3.30 (arête -y, minimum 1.5). Personne sur le bord avant (état RÉVÉLÉ, ancrages avant), poussée vers l'avant. |
| AVERTISSEMENT (compromis) | `traction_exterieure_ancrage` | Traction extérieure de 1500 N à 563 mm, meuble vide : coefficient 0.54. Les ancrages servent à retenir une personne installée sur le meuble ; ne jamais les relier à un point extérieur ni tirer depuis l'extérieur. |
| essai requis | `essai_statique` | Essai statique de la surface : 3 × charge de service, 10 min, sans rupture ni déformation permanente (type EN 1728 adapté). |
| essai requis | `essai_fatigue` | Essai de fatigue des assemblages (cycles d'assise/rythme) — référence EN 1728 / EN 12520, à adapter à l'usage. |
| essai requis | `essai_ancrages` | Essai de traction de chaque ancrage à 3 × 1500 N, sur prototype. |
| essai requis | `visa_ingenieur` | Modèles simplifiés : visa d'un ingénieur structure avant série. |

Ancrages (REVELE) :

* `ancrage_accoudoir_g` — (85, 440, 573) mm, dans `canape_traverse_acc_g` : Insert vertical dans la traverse haute d'accoudoir.
* `ancrage_accoudoir_d` — (1665, 440, 573) mm, dans `canape_traverse_acc_d` : Insert vertical dans la traverse haute d'accoudoir.
* `ancrage_avant_1` — (522, 30, 220) mm, dans `canape_traverse_avant` : Insert horizontal (axe y) dans la traverse avant.
* `ancrage_avant_2` — (1228, 30, 220) mm, dans `canape_traverse_avant` : Insert horizontal (axe y) dans la traverse avant.
* `ancrage_arriere_1` — (522, 675, 300) mm, dans `canape_traverse_arriere` : Insert vertical sous galette, cache aimanté tapissé (accès : soulever la galette).
* `ancrage_arriere_2` — (1228, 675, 300) mm, dans `canape_traverse_arriere` : Insert vertical sous galette, cache aimanté tapissé (accès : soulever la galette).

### Chiffrage indicatif (estimation datée de novembre 2026, HT sauf mention)

| Poste | Montant |
|---|---|
| Bois (pertes comprises) | 678 € |
| Mousses | 99 € |
| Revêtements (+25 % de chutes) | 530 € |
| Quincaillerie | 427 € |
| Finition + emballage | 152 € |
| Amortissement moules | 0 € |
| Main-d'œuvre (36.9 h ébénisterie + 13.9 h tapisserie) | 2862 € |
| **Coût de revient** | **4750 € HT** |
| Prix de vente indicatif (× 1,45) | 6890 € HT — **8260 € TTC** (fourchette 6200–10350 €) |
| Prototype unitaire | ≈ 15750 € TTC |

### Paramètres Fusion propres à la typologie

* `tan_canape_etat` = 0  — 0 = SALON, 1 = RÉVÉLÉ.
* `tan_canape_largeur_accoudoir` = 170 mm — Largeur d'un accoudoir.
* `tan_canape_angle_manchette` = 105 deg — Ouverture des manchettes à l'état RÉVÉLÉ.

Changer `tan_canape_etat` puis relancer le script régénère l'autre état.

<!-- FIN GENERE -->
