# Rapport — couche 1 Aboutissants et premier module de mouvement

Voir aussi `docs/rapport_vac_u_lock_collecteur_cadres.md`.

Les dépôts `/workspace/equinox`, `/workspace/neogothique` et
`/workspace/incognito` ont été inspectés **sans modification**.

Les trois gammes partagent la même architecture en trois couches, les
unités internes **mm / kg / deg / N / MPa**, la conversion **mm → cm
uniquement** dans le pont Fusion, et l’export de User Parameters avec un
préfixe (`eq_`, `neo_`, `inc_`). Equinox et Néogothique exposent un
objet `Param` + schéma + accès par chemin ; Incognito utilise des
dataclasses figées et le préfixe `inc_`.

---

## 1. Ancrages relevés dans chaque gamme

### Equinox (cotes réelles, sources citées)

Interface la plus complète, et la seule dont on peut déduire une
accroche « œillet + filetage M8 ».

| Grandeur | Valeur | Source |
|---|---|---|
| Filetage des inserts / taraudages (pivots, glissières, ancrages) | **M8** (choix M6 / M8 / M10, à valider) | `equinox/equinox/parametres.py` (`jonctions.filetage_insert`) |
| Longueur d’insert | **20 mm** (dérivé ; 20 mm si densité ≥ 650 kg/m³, 25 mm sinon) | `parametres.py` ; `equinox/equinox/catalogues/attaches.py` (`insert_filete_m8`) |
| CMU catalogue insert M8 | **2500 N** (à confirmer fabricant) | `attaches.py` |
| Fil des œillets / anneaux | **Ø 8 mm**, imposé | `parametres.py` (`inox.diametre_oeillet`) |
| Épaisseur des platines | **2 mm**, imposé | `inox.epaisseur_plaque` |
| Œillets bas sous semelles des pieds arrière | oui, imposé | `ancrage.oeillets_bas` |
| Profondeur de feuillure sous semelle | **10 mm**, à valider | `ancrage.profondeur_encastrement` |
| Saillie de l’œil | **18 mm**, à valider | `ancrage.saillie_oeillet` |
| DI de l’œillet bas | **12 mm** (cote **codée** dans la grammaire, pas un `Param`) | `equinox/equinox/grammaires/ancrages.py` : `r_oeil = fil/2 + 6`, commentaire « oeil di 12 mm mini pour un mousqueton » |
| Visserie de platine d’œillet | 4 vis inox A4 **Ø4** + insert axial M8 | `ancrages.py` |
| CMU catalogue œillet | **2000 N** (à confirmer fabricant) | `attaches.py` (`oeillet_inox_8`) |
| Anneau arrière | oui, à mi-hauteur de traverse (banc / cheval d’arçon), imposé | `ancrage.anneau_arriere`, `position_anneau` |
| DI de l’anneau | **40 mm**, à valider | `ancrage.diametre_interieur_anneau` |
| Fixation de l’anneau | pontet + **tige M8 traversante**, écrou borgne, perçage tube **Ø9**, manchon entretoise **Ø12** soudé | `ancrages.py` |
| CMU catalogue anneau | **2500 N** (à confirmer fabricant) | `attaches.py` (`anneau_inox_8`) |
| Hauteur d’axe de la traverse (donc mi-hauteur ≈ 130 mm, tube 40×40) | **130 mm**, à valider, typologies banc Flore / cheval d’arçon | `traverse.hauteur_axe` |
| Tabouret : 4 anneaux sur ceinture basse | hauteur de ceinture **160 mm**, à valider | `equinox/equinox/grammaires/tabouret.py` |
| Chaise / trône | anneaux poignets en bout d’accoudoirs (**670 mm** au sol), chevilles sur pieds avant, haut de dossier ; œillets bas sous pieds arrière | `grammaires/chaise_trone.py` ; `chaise.hauteur_accoudoirs` |
| Croix de Saint-André | anneaux aux extrémités (poignets, chevilles) et près du nœud ; œillets sous semelles avant | `grammaires/croix_saint_andre.py` (positions géométriques, pas de cote d’anneau supplémentaire) |
| Charge utilisateur | **120 kg**, imposé | `securite.charge_utilisateur` |
| Coef. dynamique | **2,0**, à valider | `securite.coefficient_dynamique` |
| Effort de calcul sur un point de retenue | **F = 2,0 × 0,5 × 120 × 9,81 = 1177 N** | `ancrages.effort_retenue` (hypothèse « un membre qui tire sur un seul point », à valider) |
| CS bois / métal / renversement | 3,0 / 1,8 / 1,5 | `parametres.py` |
| Piton vissé dans le bois de bout | **interdit** comme point de retenue | en-tête de `attaches.py` — aucune cote de piton |

Nuance inox : `inox_316` (316L, Re 200 MPa à l’état recuit, catalogue
métaux). Les vis sont désignées « inox A4 ».

### Néogothique (Entrave cou-poignets)

| Grandeur | Valeur | Source |
|---|---|---|
| Anneaux au sol sous les semelles | oui, à valider (recommandé obligatoire pour la stabilité) | `neogothique/neogothique/parametres.py` (`ancrage.anneaux_sol`) ; `docs/points_a_trancher.md` |
| Capacité par point (« cheville + anneau ») | **2000 N** | `ancrage.capacite_point` |
| Géométrie réellement solidifiée | plaque **40 × 40 × 6 mm**, centre à z = 3 mm | `neogothique/neogothique/grammaires/entrave.py` (`plaque_ancrage_sol`) |
| Position (défauts Entrave) | x = ±**315 mm** (`x_pied = L/2 − retrait − cote/2` = 400 − 30 − 55) ; y = ±(Ls/2 − **45**) = ±**235 mm** (Ls = 560 mm) ; 4 points | `entrave.py` |
| Traction de vérif. sur une manille | **500 N**, à valider (× 1,5 dynamique : basculement à vide sans ancrage) | `charges.traction_manille` ; `points_a_trancher.md` |
| Charge verticale de service | **1500 N**, à valider | `charges.verticale_service` |
| Manilles (précédent cuir, pas un tour anatomique) | DI cou **130 mm** (±15 mm au diamètre), DI poignet **75 mm** ; largeurs 60 / 50 mm ; cuir 6,5 mm | `garnissage.*` |
| Rayon mini d’arête au contact peau | **3 mm** | `securite.arrondi_contact_peau` |
| Jeux | coulisseau 1,5 mm ; mortaise 0,2 mm ; axes 0,3 mm | `tolerances.*` |
| Filetage, Ø de fil, DI d’anneau, Ø de cheville | **non cotés** | voir TODO |

Aucune vis apparente (style de gamme). L’Entrave n’exporte pas une
interface M8 d’ancrage au sol.

### Incognito (banquette, premier meuble)

Règle de discrétion : à l’état fermé, **aucune** ferrure, anneau ou cuir
visible.

| Grandeur | Valeur | Source |
|---|---|---|
| Nombre de points (banquette) | **4**, près des coins du panneau d’appui | `incognito/incognito/grammaires/banquette.py` (`nombre_ancrages`) ; `docs/banquette.md` |
| Insert noyé | **Ø 12 mm**, encastrement **80 mm** | `incognito/incognito/parametres.py` (`GeometrieAncre`) ; `catalogues/fixations.py` (`INSERT_ANCRE_NOYE`) |
| Bloc d’ancrage local (défaut, avant recalage) | **54 × 70 × 80 mm**, cache **10 mm**, bord **30 mm** | `GeometrieAncre` |
| Inset sur le panneau | `inset_x = max(distance_au_bord, 40 mm)` ; `inset_y` centré selon largeur d’appui | `banquette.py` |
| Charge de service / CS / rupture visée | **1500 N**, **CS ≥ 3**, **4500 N** | `ParametresCharge` ; `COEFFICIENT_SECURITE_MIN_RECOMMANDE` |
| Filetage de l’insert | **non documenté** | TODO |
| Œillet / anneau apparent, DI, fil | **inexistants** dans les scripts | TODO |
| Panneau d’appui | 28 mm, trop mince pour noyer l’ancre d’où le **bloc local** masqué sous le cuir | `docs/parametres.md`, `regles.recaler_bloc_ancrage` |
| Tourillons du bloc | Ø12, longueur 50 mm, 4 par bloc | `banquette.py` |

L’interface « œillet M8 » Aboutissants **n’est pas déduite**
d’Incognito. Un adaptateur (et seulement à l’état déployé) reste à
spécifier.

---

## 2. TODO / cotes manquantes

Aucune de ces valeurs n’a été inventée. Elles valent `None` dans
`common/params_globaux.py` (`statut=todo`).

1. `tolerances.jeu_axe_petit_oeil` — jeu de l’axe de bride dans l’œillet bas DI 12 mm (l’axe lui-même est un paramètre Aboutissants à valider, Ø6 proposé).
2. `ancrages.equinox.diametre_piton` / `filetage_piton` — pas de piton coté ; usage interdit comme retenue.
3. `ancrages.neogothique.filetage` — « cheville + anneau » sans filetage.
4. `ancrages.neogothique.diametre_fil` — plaque 40×40×6 seulement.
5. `ancrages.neogothique.diametre_interieur_anneau` — pas de DI, passage d’axe de bride non garanti.
6. `ancrages.neogothique.diametre_cheville` — mention sans cote.
7. `ancrages.incognito.filetage` — insert Ø12 sans filetage (M8 / M10 / M12 ou axe lisse : inconnu).
8. `ancrages.incognito.diametre_interieur_oeillet` — pas d’œillet apparent.
9. `ancrages.incognito.diametre_fil` — pas d’anneau apparent.
10. `mouvement.moteur_entraxe_fixation` — platine électrique future, moteur non choisi.
11. `mouvement.moteur_couple_nominal` — idem.

Autres points non cotés dans les meubles, traités comme paramètres
Aboutissants **à valider** (pas comme cotes de meuble) : tours
anthropométriques S/M/L/XL (références génériques), sections de sangle
commerciales, course / hauteur de la machine, charge de poussée 400 N,
aluminium 6082-T6 (absent des catalogues de meubles).

---

## 3. Compromis confort / solidité / discrétion

- **Œillet bas Equinox (DI 12, saillie 18, encastré sous semelle)** :
  très discret, mais œil trop petit pour un axe robuste (Ø6 proposé).
  L’**anneau arrière DI 40** à ~130 mm du sol est bien meilleur pour la
  bride, au prix d’une visibilité déjà assumée par la gamme (inox
  discret, pas caché).
- **Piton visse** : tentant et discret, **interdit** par Equinox en bois
  de bout. Ne pas y revenir.
- **Néogothique** : les ferrures apparentes font partie du style ; les
  plaques d’ancrage sont sous les semelles (peu visibles). Mais sans DI
  d’anneau coté, on ne peut pas encore garantir une bride compatible.
  L’Entrave **bascule à vide** sous 500 N × 1,5 : l’ancrage au sol n’est
  pas optionnel.
- **Incognito** : le compromis majeur est déjà écrit dans la gamme : un
  panneau d’appui élégant (28 mm) ne peut pas noyer une ancre 1500 N /
  CS 3 avec 10 mm de cache — d’où des **blocs locaux** plus volumineux,
  masqués sous le cuir. Réduire le cache trahirait l’ancre. Une machine
  rapportée, visible, n’est compatible qu’avec l’état **déployé**, et
  seulement après définition d’un adaptateur sur l’insert Ø12 (filetage
  inconnu). Accrocher quoi que ce soit à l’état fermé enfreint la règle
  de discrétion.
- **Machine** : trous d’excentricité (réglage discret, positif, plus sûr
  qu’un excentrique mal bloqué) contre un réglage continu plus confortable.
  Course longue = disque plus gros, plus visible, efforts de bielle plus
  élevés. Hauteur 700 mm alignée sur un banc, mais le bras de levier
  aggrave le renversement (voir § 4). Châssis au sol + bride locatrice :
  plus stable et plus honnête qu’une machine pendue à un seul œillet,
  moins discret.
- **Confort peau** : rayon mini 3 mm (Entrave), recommandé 5 mm sur les
  pièces longuement appliquées. Manilles Entrave largement dimensionnées
  (DI poignet 75 mm ≈ 236 mm de tour intérieur vs ~170 mm anatomique M)
  : de la place pour le cuir, à ne pas interpréter comme un tour de
  poignet.
- **CS** : Incognito impose un minimum recommandé de 3 sur les ancrages
  de personne ; Equinox n’a que 1,8 sur le métal de structure. Les
  Aboutissants retiennent **CS 3** pour tout point de retenue, et
  rappellent que la **CMU du meuble** (2000–2500 N côté Equinox, 1500 N
  service / 4500 N visés côté Incognito) est en pratique plus limitante
  qu’une vis M8.

---

## 4. Points critiques — solidité et sécurité

Hypothèses à citer telles quelles. Ce ne sont **pas** des CMU
fabricant. Essai de charge réel obligatoire avant tout usage.

### 4.1 Charge admissible M8 (traction / cisaillement)

Vis / tige **M8 × 1,25**, section résistante **As = 36,6 mm²**
(ISO 898-1 / ISO 3506). Classe retenue : **A4-70** (Rp0,2 = 450 MPa,
Rm = 700 MPa), cohérente avec la quincaillerie « inox A4 » Equinox.
Ne pas confondre avec la barre/tôle 316L recuite du catalogue Equinox
(Re = 200 MPa), qui n’est pas une vis.

Formules (un plan de cisaillement) :

- traction élastique : `F_t = Rp0,2 × As`
- cisaillement sur filet : `F_c = 0,6 × Rp0,2 × As` (hypothèse courante,
  pas une valeur de norme de levage)
- cisaillement sur fût lisse : `F_c = 0,6 × Rp0,2 × (π d² / 4)`
- charge admissible de calcul : `CMU = F / CS`

| | Élastique | Admissible CS 3 | Admissible CS 1,8 (métal Equinox) |
|---|---:|---:|---:|
| Traction M8 A4-70 | 16 470 N | **5 490 N** | 9 150 N |
| Cisaillement fileté, 1 plan | 9 882 N | **3 294 N** | 5 490 N |
| Cisaillement fût lisse, 1 plan | ≈ 13 572 N | ≈ **4 524 N** | — |
| Axe Ø6 lisse (petit œillet DI 12), cisaillement fût A4-70 | ≈ 7 634 N | ≈ **2 545 N** | — |

**C’est le meuble qui dimensionne l’accroche**, pas la vis M8 :

- œillet Equinox : CMU catalogue **2 000 N** ;
- anneau / insert M8 Equinox : **2 500 N** ;
- point Néogothique : **2 000 N** ;
- ancre Incognito : service **1 500 N**, rupture visée 4 500 N.

Effort de retenue Equinox (personne) : **1 177 N**. Effort de calcul
machine (poussée nominale validée 400 N × k_dyn 2,0) : **800 N**. Les deux
passent sous les CMU catalogue, **à condition** que la bride ne
transforme pas l’effort en un moment que l’insert bois ne peut pas
reprendre, et que la CMU fabricant soit au moins égale au catalogue.

L’axe Ø6 dans l’œillet bas est le maillon faible côté machine (≈ 2 545 N
en CS 3, tout juste au-dessus de la CMU œillet). **Préférer l’anneau
DI 40 + axe Ø10**.

### 4.2 Pincements et coincements

Zones à garder hors d’atteinte, ou à carter :

- disque / maneton / bielle (ciseaux à chaque tour) ;
- entrée du chariot sous les butées et sous le rail ;
- colonne / collier de hauteur (surtout pendant un réglage) ;
- manivelle (rayon 180 mm : zone de heurt).

Un carter partiel du mécanisme bielle-manivelle est recommandé avant
usage. Jeu fonctionnel 0,5 mm (rail métal) : assez pour glisser, pas
assez pour un doigt — le risque est le pincement, pas l’engagement.

### 4.3 Arrêt d’urgence / débrayage

Version mécanique : **goupille de débrayage** sur l’arbre commun, qui
sépare la manivelle (ou le pédalier / treuil) de la transmission. Le
paramètre `mouvement.debrayage` est vrai par défaut ; sa suppression
est une erreur de validation. Prévoir aussi une cisaille / un outil de
libération des attaches de personne à portée de main (même exigence
que l’Entrave pour la manille de cou à ouverture rapide).

La version électrique future devra ajouter un arrêt électrique (coup de
poing, contacteur) **en plus** du débrayage mécanique, pas à sa place.

### 4.4 Butées de fin de course

Le rail réserve 20 mm à chaque bout. Le parcours du chariot, pour toutes
les courses réglables, doit rester **entre** les faces intérieures des
butées : le maneton ne doit jamais être le seul arrêt (risque de mise
en butée sur un point mort, de cisaillement de goupille ou de sortie de
rail). C’est vérifié par le test cinématique hors Fusion.

### 4.5 Arêtes

Rayon mini 3 mm au contact peau (Entrave), 5 mm recommandé sur la tige
de sortie, la poignée et toute pièce longuement appliquée. Chanfreiner
systématiquement les débouchés de trous et les chapes.

### 4.6 Stabilité

Un châssis léger (hypothèse 15 kg + lest 8 kg, empattement 450 mm) **ne
tient pas seul** une poussée de 800 N à 700 mm de haut : Ms/Mr ≈ 0,09
pour une cible 1,5. Ce n’est pas un oubli de lest : il faudrait plusieurs
centaines de kilos. Conséquences non négociables :

- la machine ne doit **pas** être utilisée en appui libre ;
- la bride sur un ancrage de meuble (ou un ancrage au sol dédié) reprend
  le couple, les pieds du châssis formant l’autre point de la paire de
  forces ;
- le meuble lui-même doit être stable ou ancré (l’Entrave et la
  banquette Incognito le rappellent déjà : traction horizontale à vide =
  basculement) ;
- un essai de basculement réel, bride serrée **et** bride desserrée, est
  obligatoire.

### 4.7 Nettoyage / hygiène des pièces en contact

- Tige de sortie, poignée, éventuellement chape : **inox 316L**
  (recommandé Equinox pour désinfectants chlorés et fluides corporels).
  Éviter l’inox 304 avec un javellisant.
- Poignée : laiton **sans plomb** (CW510L) ou inox ; le CW614N du
  catalogue Equinox contient du plomb, déconseillé au contact prolongé.
- Aluminium 6082 : anodiser ; isolation vis-à-vis de l’inox (corrosion
  galvanique). Pièces de contact : préférer l’inox, plus faciles à
  laver et non poreuses.
- Bois : pas de bois brut en zone de fluides. Si un élément d’ébénisterie
  apparaît, finition fermée, ou pièce démontable.
- Conception : tige et poignée **démontables** sans outillage spécial,
  pas de poches fermées, pas de filetage exposé côté contact.

### 4.8 Usage

Adultes consentants uniquement. Les attaches de personne doivent pouvoir
être ouvertes rapidement, indépendamment de la machine. La charge de
poussée nominale est **validée à 400 N** (800 N dynamique, CS 3 → 2400 N) :
ce n’est pas un appui de tout le poids du corps.

---

## 5. Fichiers créés

| Chemin | Rôle |
|---|---|
| `/workspace/aboutissants/README.md` | Architecture 3 couches, conventions |
| `/workspace/aboutissants/pytest.ini` | Tests |
| `/workspace/aboutissants/docs/rapport_couche1_mouvement.md` | Le présent rapport |
| `/workspace/aboutissants/common/params_globaux.py` | Couche 1, 149 paramètres documentés |
| `/workspace/aboutissants/common/fusion_utils.py` | mm↔cm, User Parameters `abo_*` |
| `/workspace/aboutissants/catalogues/materiaux.py` | Inox, laiton, alu, bois |
| `/workspace/aboutissants/catalogues/visserie.py` | M8, hypothèses de charge |
| `/workspace/aboutissants/mouvement/sex_machine_mecanique.py` | Grammaire + `run(context)` |
| `/workspace/aboutissants/tests/test_params_globaux.py` | Cohérence des paramètres |
| `/workspace/aboutissants/tests/test_sex_machine_mecanique.py` | Cinématique hors Fusion |

Aucun fichier n’a été modifié dans `equinox/`, `neogothique/` ni
`incognito/`.

---

## 6. Résultat des tests

Exécutés le 18 novembre 2026 (Europe/Paris), hors Fusion, sans `adsk` :

```
/workspace/.venv/bin/python -m pytest /workspace/aboutissants/tests
# 31 passed
```

Couverture utile : plages, tolérances > 0, CS ≥ 1 (alerte si CS ancrage
< 3), tours S < M < L < XL, fidélité des cotes Equinox / Néogothique /
Incognito, présence des TODO, `course = 2e` (exacte aux points 0 et π,
numérique sur un tour), chariot dans les butées tous les 15°, charges
M8, absence d’`import adsk` au chargement des modules.
