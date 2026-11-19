# Brief Design Émeraude

Document soumis à Fabien avant toute transmission à l'agent Design Émeraude. Aucun envoi n'a été fait.

Date : 19 novembre 2026 (Europe/Paris).
Sources : `/workspace/tantra` (pile `tan_*` et pile TantraGamme / T1–T4), positionnement validé par Fabien, orientation des meubles camouflables vers Opale.

---

## 1. Contexte et positionnement

Émeraude est la gamme tantra / bien-être de la maison. Elle est **sex-positive**, tournée vers l'accompagnement des postures, le confort et une esthétique sereine. Elle se place en rupture avec les gammes hard / SM (Obsidienne et, le cas échéant, tout vocabulaire de contrainte, d'entrave ou de ferrure apparente).

Intentions à tenir dans le design :

- confort prolongé, postures accompagnées à une ou deux personnes ;
- appuis lombaires et cales (fessière, genoux) intégrés à la forme, non rapportés comme accessoires de contention ;
- courbes douces, matières chaleureuses, lecture « meuble de pièce de vie » plutôt que « meuble de salle de jeux » ;
- pas de vocabulaire de contrainte, pas de ferrures apparentes, pas d'ancrages visuels SM.

Deux piles de travail coexistent aujourd'hui sous `/workspace/tantra`. Elles ne doivent plus être traitées comme une seule « gamme Tantra » indifférenciée.

---

## 2. Périmètre

### Inclus

- Les typologies de confort tantrique, à une ou deux personnes, dont la lecture reste un siège, une chaise longue ou une banquette.
- Les paramètres d'ergonomie déjà documentés (anthropométrie, angles, cales, appuis lombaires, épaisseurs de garnissage), à arbitrer entre les deux piles (voir § 5).
- Le graphe matière chaleureux (bois, cuirs pigmentés, tissus, mousses HR) : les valeurs chiffrées renvoient à la note d'arbitrage matériaux, sans les figer dans ce brief.

### Exclus (orientés vers Opale)

Validé par Fabien : les meubles camouflables sortent d'Émeraude et partent vers Opale.

| Élément dans `/workspace/tantra` | Nature réelle | Destinataire |
|---|---|---|
| `camo_canape` | Typologie de grammaire (`tantra/tantra/parametres.py`, volet `camouflable`) : canapé deux places à ancrages escamotés | Opale |
| `camo_fauteuil` | Typologie de grammaire, même fichier : fauteuil bergère à repose-genoux escamotable | Opale |
| `docs/fiches_camouflables.md` | Fiches documentaires (table basse, banc d'entrée, tête de lit, etc.), pas une typologie de script | Opale, comme corpus documentaire |
| `docs/marche_camouflable.md` | Étude de marché (Liberator, Sportsheets, Tantra Chair, etc.), pas une typologie de meuble | Opale, comme corpus documentaire |

Également hors périmètre Émeraude, sauf arbitrage contraire de Fabien :

- les typologies du volet `cadre` de la pile `tan_*` : `cadre_desserte_genoux` (desserte → cadre à genoux) et `cadre_table_inclinee` (table basse → cadre incliné). Ce sont des meubles transformables dont l'état « cadre » appartient au vocabulaire de contrainte ; leur état « meuble de salon » relève d'Opale plus que d'Émeraude ;
- tout ancrage apparent, ferrure, menotte, port ou point de contention.

---

## 3. Typologies — recommandation de pile

### Les deux piles

**Pile T1–T4 / `TG_*`** (`/workspace/tantra/TantraGamme`, `/workspace/tantra/TYPOLOGIES.md`, `/workspace/tantra/README.md`)

- Quatre typologies proposées en passe 1, sans scripts de grammaire (couche 3 « à venir ») : T1 « La Vague » (chaise longue en S), T2 « Le Lotus » (fauteuil bas à cale et boudin lombaire), T3 « L'Autel » (banquette à dosseret et appui lombaire), T4 « Le Diptyque » (fauteuil à double plan).
- Charge de conception : 2 personnes × 120 kg × coefficient dynamique 2,0 = 4 708,8 N, arrondi 4 709 N dans `TYPOLOGIES.md` (`ChargesConception.charge_verticale_N` dans `tantra/TantraGamme/lib/params_globaux.py`).
- Ergonomie et catalogues déjà structurés (`PARAMS`, `Ergonomie`, mousses, revêtements, `kmod` / `γM`).

**Pile `tan_*` (8 typologies)** (`/workspace/tantra/tantra/parametres.py`, catalogues et grammaires associés)

- Volet tantra (à examiner pour Émeraude) : `tantra_chaise_double_courbe`, `tantra_fauteuil_lombaire`, `tantra_banquette_deux_niveaux`, `tantra_siege_repose_genoux`.
- Volets hors périmètre : `camo_canape`, `camo_fauteuil` ; `cadre_desserte_genoux`, `cadre_table_inclinee`.
- Charges par défaut : poids personne 1 100 N (≈ 112 kg), facteur dynamique 1,5, ancrage de service 1 500 N, coefficient de sécurité 3 (`ParametresCharge` dans `tantra/tantra/parametres.py`). Une charge duo se calcule `nombre_personnes × 1100 × 1,5` : pour deux personnes, 3 300 N, clairement en dessous des 4 709 N de l'autre pile.

### Recommandation (à valider par Fabien)

Conserver comme **référence de positionnement, de charge et de nommage** la pile T1–T4 / `TG_*` (4 709 N, typologies de confort, vocabulaire serein).

Ne pas retenir le modèle 1 100 / 1 500 N de la pile `tan_*` comme charge de conception Émeraude : il est calé sur une personne à 112 kg et un facteur 1,5, plus un ancrage de 1 500 N hérité d'un usage qui n'est plus dans le périmètre.

Réutiliser néanmoins les **quatre typologies du volet tantra** de la pile `tan_*` comme base descriptive déjà chiffrée (cotes et plages dans `parametres.py`), en les rapprochant et, le cas échéant, en les renommant vers T1–T4. Les scripts de couche 3 de TantraGamme n'existent pas encore ; ignorer ce capital de cotes serait une perte. Les deux jeux de cotes ne sont pas identiques : l'agent Design devra les superposer et proposer une cote unique par typologie, sans moyenne primitive.

### Correspondances proposées (à confirmer)

| Proposition Émeraude | T1–T4 (`TYPOLOGIES.md`) | Pile `tan_*` (`parametres.py`) | Commentaire |
|---|---|---|---|
| Chaise longue en S (signature) | T1 La Vague — emprise 1 880 × 640, creux 380, bosse 560, sommet 780 | `tantra_chaise_double_courbe` — longueur 1 850 (plage 1 650–2 000 ; le fichier cite 1 880 mm comme repère « Tantra Chair US »), largeur 600, bosse 470, creux 330, dorsale 760 | Même archétype. Écarts de profil à arbitrer (creux 330 vs 380, bosse 470 vs 560). Nom commercial à choisir (La Vague / autre), identifiant technique à unifier. |
| Fauteuil bas à cale et lombaires | T2 Le Lotus — 780 × 860 × 800, assise avant 280, largeur utile 700, cale +90 à 15–18°, boudin Ø 150 à 200 mm, angle intérieur ≈ 105° | `tantra_fauteuil_lombaire` — largeur 760, hauteur d'assise 340 (plage 300–420), profondeur 440, inclinaison 12°, angle dossier 108°, hauteur dossier 820 | Même usage (duo face à face, cale et lombaire). Hauteur d'assise et profondeur utile divergent (280 / 620 vs 340 / 440) : point de validation prioritaire. |
| Banquette d'appui | T3 L'Autel — banquette hauteur de lit, dosseret bas incliné, boudin lombaire, plateau ≈ 460 | Pas d'équivalent univoque dans `tan_*` | À conserver comme typologie Émeraude si l'on suit T1–T4. À décrire à partir de `TYPOLOGIES.md`, puis à figer. |
| Double plan | T4 Le Diptyque — plans 380 / 680, emprise 1 100 × 720 × 680 | `tantra_banquette_deux_niveaux` — longueur 1 500, profondeur 1 050, niveaux 420 et 640, inclinaison 12° | Parenté fonctionnelle (deux hauteurs d'appui) mais géométries différentes. Trancher si l'on fusionne, si l'on garde les deux, ou si la banquette à deux niveaux reste une typologie distincte. |
| Siège à repose-genoux | Absent de T1–T4 | `tantra_siege_repose_genoux` — assise 560 inclinée 22°, repose-genoux 320, entraxe 470, largeur 620 | Cohérent avec le positionnement confort (bassin ouvert, dos libre), sans vocabulaire de contrainte. Recommandation : **le garder** comme typologie Émeraude, avec un nom serein à choisir. |

`TYPOLOGIES.md` recommandait déjà, en passe 1, de partir sur T2 + T3, et T1 comme pièce signature si le budget de gabarits est accepté. Cette hiérarchie reste un bon ordre de travail, en y ajoutant le siège à repose-genoux si Fabien le confirme, et en tranchant le sort de T4 / banquette à deux niveaux.

---

## 4. Intentions esthétiques

- Ligne calme, volumes tendus, courbes continues plutôt que profils anguleux ou « médiévaux ».
- Bois apparent en teinte chaleureuse ; le choix d'essence (chêne, frêne, noyer, éventuellement lamellé ou contreplaqué cintré pour les coques) est renvoyé à la note matériaux. Pas de fumage noir ni de ferrure forgée.
- Garnissage généreux, toucher confortable, revêtement nettoyable adapté aux huiles de massage : la pile TG recommande déjà un cuir pleine fleur pigmenté plutôt qu'une aniline (`tantra/TantraGamme/lib/params_globaux.py`, commentaire de `cuir_pigmente` / `cuir_aniline`). À confirmer, sans figer l'épaisseur ici.
- Aucun élément de quincaillerie qui se lise comme une attache. Les assemblages bois (tenons, tourillons) peuvent rester visibles s'ils se lisent comme de l'ébénisterie, pas comme de la ferronnerie de contrainte.
- Le meuble doit pouvoir vivre dans une chambre ou un salon sans masquer une seconde fonction SM.

---

## 5. Ergonomie et usage

Paramètres déjà présents dans les fichiers — à citer tels quels, puis à arbitrer. Aucune valeur nouvelle n'est inventée ici.

### Anthropométrie

Pile `tan_*`, `ANTHROPOMETRIE_DEFAUT` et `SOURCE_ANTHROPOMETRIE` dans `tantra/tantra/parametres.py` : source nommée, Pheasant S. & Haslegrave C. M., *Bodyspace*, 3e éd., CRC Press, 2006 (adultes britanniques 19–65 ans), avec renvoi à un contrôle croisé DINED (TU Delft).

| Mesure (mm) | P5 | P50 | P95 |
|---|---|---|---|
| Stature | 1505 | 1675 | 1855 |
| Hauteur poplitée | 355 | 420 | 490 |
| Longueur fesse–poplité | 435 | 488 | 550 |
| Largeur hanches assis | 310 | 368 | 435 |
| Appui lombaire au-dessus de l'assise | 150 | — | 250 |

Pile TG, `Anthropometrie` dans `tantra/TantraGamme/lib/params_globaux.py` : le fichier invoque des « tables ergonomiques type NF EN ISO 7250 / données françaises adultes ». L'ISO 7250 est un protocole de mesure, pas un tableau de données : les chiffres ci-dessous sont donc **à recouper / à sourcer** avant d'être figés.

| Mesure (mm) | P5 | P95 |
|---|---|---|
| Stature | 1530 | 1880 |
| Hauteur poplitée | 380 | 490 |
| Profondeur d'assise (fesse–poplité) | 440 | 530 |
| Largeur hanches assis | — | 430 |
| Centre lombaire au-dessus de l'assise | 170 | 250 |
| Largeur épaules P95 | — | 500 |

Les deux piles ne s'accordent pas sur la stature ni sur la poplitée P5 (355 vs 380) ni sur la profondeur d'assise P5 (435 vs 440, et 530 vs 550 au P95). C'est un point de validation, pas un détail.

### Angles, cales, garnissage (pile TG — `Ergonomie` dans `params_globaux.py`)

- Angle assise / dossier : 100 à 125°.
- Inclinaison d'assise max : 15°.
- Rayon mini d'arête : 6 mm.
- Épaisseur de garnissage : assise 80 mm, dossier 50 mm.
- Boudin lombaire : Ø 160 mm.
- Cale fessière : hauteur 90 mm, pente 18°.
- Largeur d'assise duo : 700 mm.

Dans `TYPOLOGIES.md`, T2 porte une hauteur d'assise avant de 280 mm, une cale de 90 mm, un boudin Ø 150 centré à 200 mm au-dessus de la cale, un dossier à 15° de la verticale. Ces cotes de typologie et les bornes globales `Ergonomie` devront être rendues cohérentes.

### Pile `tan_*` — cotes déjà dans les typologies (`parametres.py`) et épaisseurs par défaut

- Fauteuil : assise 340 mm, profondeur 440 mm (le commentaire du fichier la borne par le fesse–poplité P5), inclinaison 12°, angle dossier 108°.
- Chaise en S : creux 330, bosse 470, dorsale 760, longueur 1850.
- Siège repose-genoux : assise 560 mm à 22°, repose-genoux 320 mm.
- Épaisseurs de mousse par défaut : assise 60 mm, dossier 40 mm (`PARAMETRES_DEFAUT`) — différentes des 80 / 50 mm de la pile TG.

### Usage à couvrir (sans les transformer en brief SM)

Postures accompagnées, assises face à face, semi-allongées, appuis ventraux ou dorsaux sur un second niveau, bassin ouvert sur un siège à repose-genoux. Le design doit dire clairement pour qui et dans quelle plage de tailles chaque typologie reste confortable (P5–P95, une ou deux personnes), et où le compromis cesse de l'être.

---

## 6. Matériaux

Les essences, cuirs, textiles, mousses, charges et coefficients ne se tranchent pas dans ce brief. Ils sont portés par la note d'arbitrage « Note d'arbitrage — matériaux et paramètres globaux » et par le découpage proposé sous `catalogues/materiaux/` (branche locale non publiée `proposition/catalogue-materiaux`).

Pour le Design Émeraude, retenir seulement les principes suivants, déjà documentés dans les fichiers de la pile TG ou de `tan_*` :

- préférer un cuir pigmenté à une aniline en assise (commentaire TG sur le risque de taches, huiles et fluides) ;
- mousses HR fermes sur les assises et cales (HR45 / HR55 selon les fichiers), éventuellement une visco en surcouche, que `tan_*` déconseille déjà là où l'on bouge ;
- ne pas importer le langage matière d'Obsidienne S2 (chêne fumé, ferrures, cuir sellier épais de manille).

Les valeurs chiffrées (épaisseurs de cuir 1,3 vs 1,8 mm, portances de mousse divergentes, kmod, charges) restent à l'arbitrage matières.

---

## 7. Livrables attendus de l'agent Design Émeraude

1. Une intention de gamme écrite (une page) : positionnement, ton, ce qu'Émeraude n'est pas.
2. Le parti typologique : liste retenue, noms commerciaux et identifiants techniques, mapping explicite vers T1–T4 et vers les `tantra_*` conservés, typologies écartées.
3. Pour chaque typologie retenue : dessin d'intention (cotes principales, profil, positions d'usage, plage P5–P95), avec justification des cotes par fichier source quand elles en viennent, et mention « à sourcer » ou « à valider » sinon.
4. Une proposition d'arbitrage là où T1–T4 et `tan_*` divergent (en particulier T1 / chaise en S, T2 / fauteuil, T4 / banquette à deux niveaux, et le siège à repose-genoux).
5. Intention matière et finition (qualitative), sans refermer les valeurs renvoyées à la note matériaux.
6. Points ouverts et ce qui doit être validé par Fabien avant passage au Script.

Hors livrables : scripts Fusion, catalogues chiffrés, création d'agents, et tout travail sur les typologies camouflables ou « cadre ».

---

## 8. Critères de validation avant transmission au Script

- Le positionnement sex-positif / bien-être est lisible sur chaque typologie ; aucune pièce retenue ne dépend d'un état « cadre », d'un ancrage apparent ou d'un camouflage SM.
- Les typologies camouflables et le corpus `fiches_camouflables` / `marche_camouflable` sont bien sortis du périmètre.
- Une seule pile de charge est retenue pour Émeraude, et elle est écrite (hypothèse, unités, nombre de personnes, coefficient dynamique).
- Une seule base anthropométrique est retenue, avec sa source ; les divergences P5/P95 ont été tranchées ou explicitement laissées en « à valider ».
- Chaque typologie a un identifiant unique, un nom d'usage, un jeu de cotes cohérent (plus de doublon T2 / `tantra_fauteuil_lombaire` aux chiffres différents).
- Les demandes au Script sont formulées en paramètres et en grammaire, sans valeur en dur non référencée.
- Les questions matières encore ouvertes sont renvoyées à la note d'arbitrage, pas tranchées par défaut par le Design.

---

## 9. Questions ouvertes

1. Confirmer la recommandation de pile : référence T1–T4 / 4 709 N, réemploi des cotes `tan_*` du volet tantra, abandon du modèle 1 100 / 1 500 N pour Émeraude.
2. Noms commerciaux et identifiants (La Vague, Le Lotus, L'Autel, Le Diptyque, siège à repose-genoux) : les garder, les franciser autrement, ou s'aligner sur les identifiants `tantra_*`.
3. Fusion ou coexistence de T4 et de `tantra_banquette_deux_niveaux`.
4. Conservation du siège à repose-genoux dans Émeraude.
5. Ordre de production : confirmer ou amender la recommandation de passe 1 (T2 + T3 d'abord, T1 en pièce signature).
6. Base anthropométrique : Pheasant & Haslegrave 2006 (sourcée dans `tan_*`) versus chiffres TG présentés comme « ISO 7250 / données françaises » (à recouper).
7. Hauteurs d'assise du fauteuil (280 mm T2 vs 340 mm `tan_*`) et profondeurs utiles (620 vs 440 mm) : compromis P5/P95 à trancher.
8. Épaisseurs de garnissage 80/50 mm (TG) vs 60/40 mm (`tan_*`) : après ou avec la note matériaux.
9. Sort exact des typologies `cadre_*` (recommandation : Opale, pas Émeraude).

---

## 10. Recommandation de pile (synthèse)

Adopter la pile T1–T4 / `TG_*` comme référence de positionnement et de charge (2 × 120 kg × 2,0 = 4 709 N), parce qu'elle décrit un usage duo confortable, sans ancrage, aligné sur le brief sex-positif.

Conserver les quatre typologies du volet tantra de la pile `tan_*` uniquement comme matériau de cotes à rapprocher (et à renommer) vers ces références, en excluant camouflage et cadres.

Ne pas faire de la pile `tan_*` à 1 100 / 1 500 N la base de calcul d'Émeraude.
