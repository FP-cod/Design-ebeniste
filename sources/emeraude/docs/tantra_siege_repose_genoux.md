# Siège à assise inclinée et repose-genoux (volet 1 — meuble fixe)

**Typologie :** variante élargie de l'assis-genoux (assise inclinée vers l'avant de 22°, tibias
en appui sur des coussins). La posture ouvre l'angle tronc-cuisse (~115–120°), met le bassin en
antéversion et laisse le dos libre : on s'y tient chevauché face à un partenaire, ou on y reçoit
quelqu'un sur les genoux. Principe d'après A. C. Mandal, « The seated man (Homo sedens) »,
*Applied Ergonomics* 12(1), 1981.

## Grammaire (`tantra_siege_repose_genoux.py`)

* Deux cadres latéraux en frêne : **patin traîneau lamellé-cintré** (lames de 4 mm, rayon ≥ 40 ×
  lame), montant d'assise, montant de genoux, écharpe de triangulation ; 4 traverses à tenons.
* Assise de 380 mm à 560 mm de haut ; genoux à 320 mm, pente 30° ; 470 mm entre les centres.
* **Patin de 1 060 mm** : le talon dépasse de ~150 mm derrière l'assise. Avec le patin de 900 mm
  d'origine, la grammaire trouvait un coefficient de 0,69 au basculement arrière (personne au bord
  arrière + poussée de 300 N à hauteur d'épaules). Corrigé, et couvert par un test.
* 4 ancrages dans les montants.

## Compromis

* **Réglage unique** : un seul jeu de cotes ne couvre pas confortablement P5 et P95 (~120 mm
  d'écart de cuisse). Il faut deux tailles ou une version sur mesure (avertissement émis par la
  grammaire).
* Pièce la plus légère (≈ 15 kg) et la moins chère, mais la stabilité arrière dépend du patin
  (encombrement en profondeur ≈ 1 080 mm).

<!-- DEBUT GENERE -->

## Résultats calculés (générés par `python -m tantra.rapport`)

| État | Hors-tout l × p × h (mm) | Masse (kg) | Pièces | Ancrages | Conforme |
|---|---|---|---|---|---|
| FIXE | 620 × 1082 × 629 | 15.2 | 21 | 4 | oui |

### Vérifications — état FIXE

| Niveau | Code | Détail |
|---|---|---|
| ok | `ergo_longueur_cuisse` | Distance assise → genoux 528 mm dans [fesse-poplité P5 435 ; fesse-genou P95 645] mm : tibias en appui juste sous la rotule. |
| ok | `ergo_angle_cuisse` | Cuisses inclinées de 27° sous l'horizontale (20–35° : angle tronc-cuisse ≈ 110–125°, bassin en antéversion ; Mandal 1981). |
| ok | `ergo_inclinaison_assise` | Assise inclinée de 22° vers l'avant (12–30°). |
| ok | `ergo_tibias` | Repose-genoux à 320 mm ≤ hauteur genou P5 455 − 60 : les pointes de pied touchent le sol derrière le coussin pour tous les gabarits. |
| AVERTISSEMENT (compromis) | `ergo_reglage_unique` | Un seul jeu de cotes ne couvre pas confortablement P5 et P95 sur cette typologie (écart de cuisse ~120 mm) : prévoir deux tailles ou un coussin de genoux déplaçable (rail à index, ±60 mm). |
| ok | `ergo_largeur` | Largeur 620 mm ≥ hanches P95 + 2 × 80 mm. |
| ok (compromis) | `montant_loge_insert` | Montants de 50 mm (selon x) ≥ bloc d'ancrage requis 50 mm : l'insert est noyé directement dans le montant de frêne, sans bloc rapporté. Compromis : montants plus massifs qu'un siège ordinaire (35–40 mm). |
| ok | `bloc_arrachement` | Arrachement insert : R_k ≈ 11.2 kN, CS 7.4 (visé ≥ 3) — formule EC5 des vis, par analogie. |
| ok | `bloc_paroi` | Parois 17.0 mm de part et d'autre de l'insert : CS cisaillement 5.4 (paroi mini calculée 9.4 mm). |
| ok | `bloc_essence` | Bloc en Chêne massif : un contreplaqué tient mal un insert (cisaillement roulant) — bloc en massif ou lamellé exigé. |
| essai requis | `bloc_essai` | Essai d'arrachement réel de l'insert dans le bloc (série et bois réels). |
| ok | `patin_cintrage` | Rayon mini du patin ≈ 283 mm ≥ 160 mm (lamellé-cintré, lames de 4 mm, règle R ≥ 40 × épaisseur de lame pour le frêne). |
| ok | `assise_flexion` | Panneau d'assise 18 mm sur 520 mm de portée, 3300 N répartis : CS 3.3 (sans compter les deux traverses intermédiaires). |
| ok | `tenons_montants` | Tenons des montants d'assise (17 × 60 mm) : 825 N chacun, CS 3.2. |
| ok | `stabilite_penche_avant` | Stabilité « penche_avant » : coefficient 4.78 (arête -y, minimum 1.5). Assis, penché en avant, + poussée de 300 N vers l'avant à hauteur d'assise. |
| ok | `stabilite_bascule_arriere` | Stabilité « bascule_arriere » : coefficient 1.80 (arête +y, minimum 1.5). Assis au bord arrière, poussée de 300 N vers l'arrière à hauteur d'épaules. |
| ok | `stabilite_chevauchement_lateral` | Stabilité « chevauchement_lateral » : coefficient 2.82 (arête -x, minimum 1.2). Deux personnes (l'une sur l'autre), balancement latéral 300 N à hauteur de buste. |
| AVERTISSEMENT (compromis) | `traction_exterieure_ancrage` | Traction extérieure de 1500 N à 280 mm, meuble vide : coefficient 0.11. Les ancrages servent à retenir une personne installée sur le meuble ; ne jamais les relier à un point extérieur ni tirer depuis l'extérieur. |
| essai requis | `essai_statique` | Essai statique de la surface : 3 × charge de service, 10 min, sans rupture ni déformation permanente (type EN 1728 adapté). |
| essai requis | `essai_fatigue` | Essai de fatigue des assemblages (cycles d'assise/rythme) — référence EN 1728 / EN 12520, à adapter à l'usage. |
| essai requis | `essai_ancrages` | Essai de traction de chaque ancrage à 3 × 1500 N, sur prototype. |
| essai requis | `visa_ingenieur` | Modèles simplifiés : visa d'un ingénieur structure avant série. |

Ancrages (FIXE) :

* `ancrage_genoux_g` — (0, 195, 134) mm, dans `montant_genoux_g` : Chevilles (insert M12 + anneau rabattable).
* `ancrage_assise_g` — (0, 710, 280) mm, dans `montant_assise_g` : Poignets / taille.
* `ancrage_genoux_d` — (620, 195, 134) mm, dans `montant_genoux_d` : Chevilles (insert M12 + anneau rabattable).
* `ancrage_assise_d` — (620, 710, 280) mm, dans `montant_assise_d` : Poignets / taille.

### Chiffrage indicatif (estimation datée de novembre 2026, HT sauf mention)

| Poste | Montant |
|---|---|
| Bois (pertes comprises) | 76 € |
| Mousses | 10 € |
| Revêtements (+25 % de chutes) | 66 € |
| Quincaillerie | 173 € |
| Finition + emballage | 62 € |
| Amortissement moules | 0 € |
| Main-d'œuvre (23.1 h ébénisterie + 2.3 h tapisserie) | 1456 € |
| **Coût de revient** | **1840 € HT** |
| Prix de vente indicatif (× 1,45) | 2670 € HT — **3200 € TTC** (fourchette 2400–4000 €) |
| Prototype unitaire | ≈ 7000 € TTC |

### Paramètres Fusion propres à la typologie

* `tan_siege_profondeur_assise` = 380 mm — Profondeur du coussin d'assise.
* `tan_siege_inclinaison_genoux` = 30 deg — Pente des coussins de genoux.
* `tan_siege_longueur_patin` = 1060 mm — Longueur des patins traîneau.
* `tan_siege_ep_cadre` = 50 mm — Épaisseur des cadres latéraux (frêne).

<!-- FIN GENERE -->
