# Rapport — Vac-U-Lock, collecteur d'urine et cadres modulaires

Les dépôts `/workspace/equinox`, `/workspace/neogothique` et
`/workspace/incognito` ont été inspectés **sans modification**.

Ce document complète `docs/rapport_couche1_mouvement.md`. Il couvre les
trois aboutissants ajoutés après la couche 1 et la machine mécanique :
l'interface Vac-U-Lock, le collecteur d'urine, et les cadres de
contention modulaires. Les charges et CMU rappelées ici sont des
**hypothèses de conception**, pas des valeurs certifiées.

Les tests hors Fusion passent : **56 passed**.

---

## 1. Port Vac-U-Lock

### 1.1 Principe

Le port est un **ergot mâle** (plug) destiné à recevoir n'importe quel
accessoire Vac-U-Lock du marché (cavité en base). Il s'ajoute aux
fixations existantes (filetage 1 pouce NPT, points d'ancrage) **sans les
remplacer**. Ce n'est **pas** un équivalent du NPT, ni un raccord de
fluide.

### 1.2 Cotes sourcées (et divergences)

| Grandeur | Valeur retenue | Source | Statut |
|---|---|---|---|
| Longueur du plug | **76,2 mm** (3 in), mode préféré du brevet | US 5,127,396 | à valider, calibrage sur pièce obligatoire |
| Ø tête max | **31,75 mm** (1,25 in) | Brevet, mode préféré ; un détaillant (ABS Holdings) | à valider |
| Ø tête, source alternative | **27,94 mm** (1,1 in) | Boutique officielle Doc Johnson, Double Up Plug 5,3 in × 1,1 in ; circonférence 3,5 in ≈ Ø 1,11 in | conservée, non inventée |
| Ø tige max | **19,05 mm** (0,75 in) | US 5,127,396 | à valider |
| Ø milieu, longueurs de sections, angle de cône, interférence de cavité, épaisseur de collerette | **None** | absents des sources publiques consultées | TODO |
| Profondeur de cavité | 76,2 mm (dérivée de la longueur) | même forme « légèrement plus petite » (brevet, interférence non chiffrée) | dérivé |
| Forme | Révolution tête / milieu / tige, flancs « balle » à deux épaulements paraboliques (non cotés) | Brevet | enveloppe simplifiée, pas une cote de définition |

**Deux variantes, on ne tranche pas** (décision Fabien). `variante_tete`
= `brevet` (31,75 mm, https://vac-u-lock.com/vac-u-lock-patent.html) ou
`boutique` (27,94 mm). Un jeu de cales d'ajustement (0,25 / 0,5 / 1,0 /
2,0 mm, inox 316L ou PP / PE-HD) rattrape le jeu radial typique de
1,905 mm. Les cales n'entrent pas un ergot 31,75 mm dans une cavité
27,94 mm : dans ce cas, choisir la variante boutique. Calibrage sur
pièce réelle toujours recommandé (étoile, cône, Ø milieu restent TODO).

Aucune source publique consultée ne décrit une **cavité étoilée**. Elle
n'a pas été modélisée.

Le profil Fusion est une **enveloppe** (Ø tête, Ø tige, longueur) : le
nez de 4 mm et le maintien du Ø tête jusqu'à mi-longueur sont des
hypothèses d'atelier clairement signalées, pas des cotes du brevet.

### 1.3 Filetage 1 pouce NPT (ASME B1.20.1)

| Grandeur | Valeur |
|---|---|
| Pas | 11,5 TPI (pas 2,209 mm) |
| Ø extérieur | 33,401 mm |
| Cônicité | 1:16 (0,0625) |
| Angle de filet | 60° |
| L1 / L2 / L4 | 10,160 / 17,343 / 25,006 mm |
| E0 / K0 | 30,826 / 29,060 mm |

Présence dans les meubles (grep, **sans modification**) : **Incognito
seulement** (housses / actionneur). Absent d'Equinox et de Néogothique,
et absent des inserts Ø12 Incognito. Ces deux gammes **n'ont pas été
modifiées** pour y ajouter un NPT : l'ajout rétroactif, possible si l'on
veut une compatibilité Sybian partout, reste une **décision à prendre**.
Le NPT peut servir de montage arrière optionnel (`filete_et_npt`) ou de
vidange de cuve ; ce n'est pas un Vac-U-Lock. Le montage arrière par
défaut de l'ergot est désormais le **filetage côté machine** (voir le
catalogue vaculocks.com, défaut M8x1.25).

### 1.4 Verrouillage complémentaire et arrachement

Le vide théorique maximal sous la tête, vide parfait, vaut
p_atm × section ≈ **80 N**. L'effort de calcul retenu est
400 N × k_dyn 2 = **800 N** (poussée nominale **validée** à 400 N,
effort de calcul d'ancrage 2400 N avec CS 3). Le vide, même idéal, est très inférieur ; le
frottement cavité/ergot n'est pas chiffré (TODO, notamment avec
lubrifiant ou poudre). Un **verrouillage mécanique complémentaire** est
donc requis pour la machine.

**Défaut : collier de serrage** (désactivable), seul mode compatible avec
des accessoires du marché **non percés**. Il appuie la base de
l'accessoire contre un épaulement (épaisseur 8 mm : hypothèse d'atelier,
`collerette_epaisseur` reste TODO). Goupille transversale et baïonnette
sont des options, avec alerte : elles exigeraient des formes absentes
des godes du commerce.

Cycles de tenue : **aucune donnée fabricant trouvée (TODO)**. Inspection
à prévoir. CMU des vis du collier (M4 × 2, A4-70, un plan, CS 3) : voir
`catalogues.vac_u_lock.rapport_arrachement` — hypothèse, pas une CMU
certifiée.

### 1.5 Matériaux

L'ergot de série est en **inox 316L** (Ra ≤ 0,8 µm, nettoyable, contact
silicone/PVC compatible). Laiton et alu : pièces sèches ou platines,
pas l'ergot. Bois, cuir, sangle : interdits au contact de l'emboîtement.

### 1.6 Intégration

- Module réutilisable `interfaces/port_vac_u_lock.py` (`calculer_port`,
  `adapter_sur_tige`, `adaptateur_ancrage`, `run(context)`).
- **Machine** : port en bout de `tige_sortie`, avec raccord Ø16 mm →
  corps NPT (Ø ext. 33,4 mm). Rien n'est modifié sur le meuble.
- **Variante meuble**, adaptateurs rapportés, cache affleurant à l'état
  fermé (`etat_deploiement = 0`) :
  - Equinox : chape sur l'anneau **DI 40** (préféré à l'œillet bas DI 12).
  - Incognito : douille sur insert **Ø12**, filetage **TODO**, cache de
    recouvrement 10 mm.
  - Néogothique : bride sur plaque **40 × 40 × 6**, filetage et DI
    d'anneau **TODO**.

---

## 2. Collecteur d'urine

### 2.1 Périmètre

Aboutissant de récupération, à l'arrière ou sous le meuble / près d'un
aboutissant **fixe**, sans modifier les meubles.

**Cible :** typologies Equinox, Néogothique et Incognito **hors pouf**,
plus les aboutissants fixes (machine mécanique).

**Le pouf vibrant Incognito n'est pas une cible** (plus de module de
collecte). `pouf` / `pouf_vibrant` lèvent une erreur. Aucune
modification de `/workspace/incognito`.

Solutions couvertes : **entonnoir déployable**, **gouttière sous
siège**, **réservoir amovible**, **raccord de vidange 1 pouce NPT**.
Contact fluide : **inox 316L** ou résine/polymère non poreux (**PP**,
**PE-HD**), joints EPDM / silicone platine / FKM. Cuir et sangle :
habillage **hors zone humide** uniquement (erreur si on les force au
mouillé).

### 2.2 Volume, hygiène, vidange

Volume utile par défaut **500 mL**, coefficient anti-débordement 1,2 →
cuve **600 mL**. Ordre de grandeur sourcé : miction typique 200–300 ou
200–350 mL le jour, 300–400 mL au lever, capacité vésicale souvent
citée 400–600 mL / ≈ 500 mL (UnityPoint Health ; StatPearls NBK562181 ;
Kettering).

Hygiène : non poreux, rincable, rayons intérieurs ≥ **5 mm**, pente ≥
**2 %** (ordre de grandeur EN 12056-2, 1:50), pas de recoin, pièces
démontables, lèvre anti-éclaboussures, couvercle et siphon (garde d'eau
50 mm) pour les odeurs.

Trois modes de vidange, **paramétrables** :

| Mode | Rôle | Avantages | Inconvénients |
|---|---|---|---|
| **Réservoir amovible** (défaut recommandé) | Cuve ôtée vers un point d'eau | Pas de raccordement au bâtiment, lavage hors meuble, discret dans le caisson | Volume borné par l'encombrement ; risque d'oubli (d'où le coef 1,2) |
| Gravité vers un point bas | Alternative | Vidange continue, moins de manipulation | Exige une pente et un rejet que le meuble ne fournit pas ; plus de tubulure à rincer |
| Raccord 1 pouce NPT | Option de fond, ou mode dédié | Standard ASME, déjà au catalogue Incognito (housses) ; démontable | Ø généreux pour de l'urine ; absent d'Equinox / Néogothique ; **ce n'est pas un Vac-U-Lock** |

Le Vac-U-Lock **n'est pas retenu** comme raccord de fluide (pas
d'étanchéité liquide sourcée).

Discrétion : rien de visible à l'état fermé (`etat_deploiement = 0`) ;
déploiement par **tiroir** ou **panneau basculant**, dans l'esprit des
trappes affleurantes et du coffre Incognito (ouverture typique ≈ 95°).
Le dossier basculant ou coulissant de cette gamme a été **écarté** : on
ne s'y accroche pas.

### 2.3 Tableau d'arbitrages discrétion / volume utile / facilité de vidange

Une ligne par typologie de meuble (Equinox, Néogothique, Incognito hors
pouf) et pour l'aboutissant fixe (machine mécanique). Les formes et
vidanges indiquées sont des recommandations ; les paramètres restent
libres.

| Gamme | Typologie | Forme conseillée | Vidange conseillée | Déploiement | Discrétion | Volume utile | Facilité de vidange | Arbitrage |
|---|---|---|---|---|---|---|---|---|
| equinox | banc_flore | gouttiere_sous_siege (alternative : entonnoir déployable à l'arrière) | reservoir_amovible (NPT en option de fond ; gravité si rejet prévu) | tiroir arrière / sous le banc | Bonne : le caisson disparaît sous le banc ; rien de visible fermé. L'anneau de traverse (DI 40, z typ. 130 mm) et les œillets de semelle restent libres. | Aisé : 500 mL (cuve 600 mL) tiennent sous un banc d'appui typique 700 mm sans forcer le voile. | Bonne avec réservoir amovible emporté vers un point d'eau. Gravité plus simple en usage mais exige un rejet que le meuble ne fournit pas. | Le volume n'est pas le facteur limitant. On privilégie une gouttière sous siège (meilleure capture sur un banc allongé) malgré un rinçage un peu plus long qu'un entonnoir, et une cuve amovible pour ne pas dépendre du bâtiment. La gravité se justifie seulement si un rejet est prévu à l'installation. |
| equinox | tabouret | entonnoir déployable (gouttière longue peu adaptée à l'emprise courte) | reservoir_amovible | tiroir compact ou panneau basculant sous l'assise | Moyenne à bonne : meuble petit ; un tiroir trop profond se voit. Le voile doit rester affleurant et court. | Juste : 500 mL restent possibles (cuve ~125×85×70 mm) mais l'emprise sous l'assise n'est pas cotée (TODO). Ne pas monter le volume par défaut. | Correcte : cuve amovible courte, à vider souvent si l'usage enchaîne les mictions. NPT peu naturel sur un tabouret mobile. | La discrétion et l'encombrement limitent plus que le volume utile. On sacrifie la gouttière (trop longue) et on garde 500 mL, tiroir court, réservoir amovible. Gravité déconseillée (tabouret déplaçable, pas de rejet lié). |
| equinox | chaise_trone | gouttiere_sous_siege ou entonnoir arrière | reservoir_amovible (NPT optionnel en fond) | tiroir sous l'assise | Bonne : le dessous de chaise masque le caisson ; voile affleurant à l'état fermé. | Aisé à moyen : 500 mL tiennent sous une assise typ. 460 mm, sous réserve du volume réel sous l'assise (non coté, TODO). | Bonne avec cuve amovible. Gravité possible si la chaise est un meuble fixe près d'un rejet. | Plus de place qu'un tabouret, moins qu'un banc. On reste sur 500 mL et le réservoir amovible ; la gouttière sous siège améliore la capture sans nuire à la discrétion si le tiroir est sous l'assise. |
| equinox | croix_saint_andre | entonnoir déployable (pas de gouttière sous siège : pas d'assise) | reservoir_amovible (gravité intéressante si la croix est scellée au sol) | panneau basculant de socle / tiroir bas affleurant | Plus faible : meuble ouvert, pas de caisson d'assise. Le collecteur doit tenir dans un socle bas, rien de visible une fois le panneau refermé. | Aisé au sol (500 mL n'imposent pas un socle haut) — ne pas agrandir le socle pour « gagner » du volume, au détriment de la discrétion. | Bonne si cuve amovible dans le socle. Gravité pertinente sur une croix fixe ; raccord NPT en sortie de socle possible. | Ici la discrétion commande : entonnoir escamotable, socle bas, volume utile standard sans surdimensionner. La facilité de vidange peut aller vers la gravité seulement si le point bas existe déjà (fixation au sol). |
| equinox | cheval_arcon *(grammaire non livrée)* | gouttiere_sous_siege (plateau) ou entonnoir arrière — à confirmer | reservoir_amovible | tiroir sous le plateau / à l'arrière | Potentiellement bonne (meuble bas et long) une fois la grammaire livrée. | Aisé en principe (assise typ. 760 mm, plateau 700×260 mm dans les overrides Equinox) : 500 mL ne posent pas de problème d'encombrement attendu. | Bonne, même logique que le banc Flore. | Typologie listée mais grammaire non livrée : on reprend l'arbitrage du banc (gouttière + cuve amovible) sans inventer d'ancrages au-delà de la famille déjà relevée (anneau de traverse, œillets). Implantation fine en TODO. |
| neogothique | entrave | entonnoir déployable (gouttière courte si le corps est allongé sur le cadre) | reservoir_amovible (gravité ou NPT pertinents : meuble déjà ancré au sol) | tiroir ou panneau basculant dans un caisson bas *entre* les plaques, sans les recouvrir | Moyenne : l'Entrave n'a pas la règle d'invisibilité d'Incognito, mais le caisson peut rester dans le rectangle des plaques (x=±315, y=±235 mm typ. Entrave défaut) et sous le cadre. | Aisé : l'emprise interne (~570×410 mm hors plaques et jeu) accueille largement 500 / 600 mL. | Très bonne : cuve amovible par défaut ; gravité et raccord 1" NPT deviennent intéressants parce que les plaques au sol fixent déjà le meuble (le NPT sort du caisson, pas du meuble). | Le volume n'est pas limitant. On reste à 500 mL. On choisit le réservoir amovible par défaut (lavage hors meuble) tout en prévoyant un fond NPT optionnel, cohérent avec une installation fixe. Ne pas recouvrir les plaques 40×40×6 (filetage / DI TODO). |
| incognito | banquette | gouttiere_sous_siege déployable *ou* entonnoir, hors du volume du banc interne | reservoir_amovible (pas de NPT traversant le meuble ; option de fond de cuve seulement) | tiroir ou panneau basculant / trappe affleurante (comme les trappes de plancher et le coffre ≈ 95° ; pas le dossier basculant, écarté) | Excellente : règle de gamme, rien de visible fermé. Le voile reprend l'épaisseur de recouvrement (10 mm). | Serré en hauteur : pieds typologie 120 mm, assise 430 mm (incognito/parametres.py). Une cuve 500 mL (~70 mm hors tout) tient entre les pieds si l'entonnoir ou la gouttière se déploient *hors* de cette hauteur (tiroir qui sort). Ne pas viser plus de 500 mL par défaut. | Bonne si la cuve sort avec le tiroir (vidange et lavage hors du salon). Gravité et NPT de bâtiment malvenus dans un meuble de salon discret ; le 1" NPT du catalogue housses/actionneur n'est pas un passage à ouvrir dans la banquette. | La hauteur des pieds et le banc déployable dans le coffre limitent le volume et l'emplacement : 500 mL, cuve plate amovible, déploiement hors du coffre d'assise (arrière / trappe de plancher) pour ne pas collisionner le banc ni les 4 inserts Ø12. La discrétion prime ; on ne grossit pas la cuve. |
| incognito | canape *(grammaire non livrée)* | gouttiere_sous_siege (longueur 2/3 places) ou entonnoir | reservoir_amovible | tiroir sous l'assise / dans le caisson, rien de visible fermé | Excellente (règle de gamme). Largeur typ. 1700 / 2200 mm (parametres.py) : le voile se fond dans le caisson. | Aisé en plan (meuble long) ; hauteur d'assise typ. 430 mm, hauteur de pieds non isolée dans la typologie (TODO). 500 mL sans difficulté attendue. | Bonne, cuve amovible. Même réserve que la banquette vis-à-vis d'un NPT de bâtiment. | Grammaire non livrée, ancrages propres non relevés (TODO). Arbitrage provisoire : même logique que la banquette, avec plus de place en longueur donc gouttière sous siège possible. Ne pas inventer d'inserts. |
| incognito | fauteuil *(grammaire non livrée)* | entonnoir déployable (emprise d'une place, gouttière longue peu utile) | reservoir_amovible | tiroir ou panneau basculant sous l'assise | Excellente (règle de gamme), sous réserve d'un tiroir court (largeur typ. 820 mm). | Moyen : une place seulement ; 500 mL restent le bon ordre de grandeur, sans le monter. | Bonne, cuve amovible courte. | Grammaire non livrée (TODO ancrages). Même discrétion qu'une banquette, emprise plus proche du tabouret : entonnoir plutôt que longue gouttière, cuve amovible 500 mL. |
| incognito | table_basse *(grammaire non livrée)* | entonnoir déployable depuis le plateau ou le tiroir (pas une gouttière « sous siège ») | reservoir_amovible (NPT de service possible dans le caisson, sans traverser un meuble d'ancrage non coté) | tiroir ou plateau basculant — déjà prévu par la typologie pour masquer un mécanisme | Excellente : c'est précisément le rôle du tiroir / plateau basculant décrit dans parametres.py. | Aisé : plateau typ. 1200×700×hauteur 420 mm ; 500 mL tiennent largement. | Très bonne : la cuve sort avec le tiroir ; point de vidange discret dans un salon. | Typologie de salon sans grammaire livrée (ancrages TODO). Usage plutôt comme point de collecte / de service discret que comme siège. On garde entonnoir déployable + cuve amovible, en s'appuyant sur le tiroir déjà prévu par la typologie, sans inventer de cotes d'ancrage. |
| incognito | banc_entree *(grammaire non livrée)* | gouttiere_sous_siege ou entonnoir (éventuellement coffre déjà prévu par la typologie) | reservoir_amovible | tiroir ou panneau de coffre / basculant | Excellente si le coffre / le voile reste affleurant (règle de gamme). | Aisé en longueur (typ. 1200×400, assise 430 mm) pour 500 mL ; profondeur 400 mm à caler (grammaire non livrée). | Bonne, cuve amovible. | Proche d'un petit banc Equinox, avec la discrétion Incognito. Grammaire non livrée, ancrages TODO. Recommandation provisoire : gouttière ou entonnoir + cuve amovible 500 mL, sans dossier basculant. |
| incognito | bibliotheque *(grammaire non livrée)* | pas de gouttière sous siège (pas d'assise) ; éventuellement entonnoir de service depuis la plinthe | reservoir_amovible dans la plinthe, ou raccord_npt de service | panneau basculant / plinthe affleurante | Excellente (montants et plinthe masquent déjà des ancrages selon la typologie), à condition qu'aucune ferrure ne dépasse. | Aisé dans une plinthe de profondeur typ. 350 mm ; 500 mL ne posent pas de problème d'encombrement. | Bonne : cuve dans la plinthe, ou NPT de service si l'installation est fixe. Peu d'usage « miction directe ». | Peu adaptée comme collecteur sous un siège. On la retient comme typologie de meuble Incognito hors pouf, plutôt comme point de service / de vidange discret. Grammaire et ancrages de montant non livrés (TODO). |
| aboutissants | sex_machine_mecanique | entonnoir déployable aligné sous l'axe de la tige (gouttière courte possible) | reservoir_amovible (NPT en fond de cuve optionnel ; ne pas détourner le raccord NPT / l'ergot Vac-U-Lock de la tige) | tiroir ou panneau basculant dans un caisson bas indépendant, sous ou derrière la zone de course | Moyenne : la machine est déjà un module visible, plus « technique » qu'un meuble Incognito. Le collecteur ne doit rien ajouter à l'état fermé (socle / tiroir affleurant sous le châssis). | Aisé : caisson au sol, 500 mL sans hausser le châssis. Ne pas fixer la cuve pleine sur le châssis (stabilité au renversement déjà juste sous 800 N à 700 mm). | Bonne avec cuve amovible indépendante. Gravité possible vers un point bas de pièce. Le 1" NPT arrière du port Vac-U-Lock n'est pas une vidange d'urine. | Aboutissant fixe, pas un meuble. On sépare nettement les interfaces : ergot Vac-U-Lock + NPT de la tige d'un côté, collecteur au sol de l'autre. Discrétion = caisson bas autonome, sans surcharger la bride d'œillet. Volume 500 mL par défaut, vidange amovible. |

### 2.4 Implantation par rapport aux ancrages déjà relevés

Aucune cote de meuble n'est inventée. Les typologies sans grammaire
livrée (cheval d'arçon Equinox ; canapé, fauteuil, table basse, banc
d'entrée, bibliothèque Incognito) figurent au tableau avec TODO
d'implantation fine. Les cotes typologiques citée (assise, pieds,
plateau) viennent des `parametres.py` des meubles, pas d'une invention
Aboutissants.

---

## 3. Cadres de contention modulaires

L'aboutissant **devient la structure** : montants et poutres, avec des
ports standard Vac-U-Lock et 1 pouce NPT répartis sur des **plots
rapportés** (on ne perce pas la fibre tendue à Ø 33 mm), plus des
anneaux / points M8 pour les accessoires à venir.

### 3.1 Typologies

| Typologie | Description | Dépendance au bâtiment | Discrétion | Solidité « autonome » |
|---|---|---|---|---|
| **cadre_sol** (défaut) | Portique autoportant (montants, traverses, longrines basses) | Non (hors plancher) | La plus faible (volume visible) | La plus haute |
| **cadre_mural** | Deux montants + traverses contre le mur | **Oui — capacité du support mural = TODO** | Meilleure (applique au mur) | Gouvernée par le mur, aujourd'hui inconnue |
| **poutre_suspendue** | Poutre entre suspentes, vers le plafond / les solives | **Oui — capacité, entraxe et section des solives = TODO** | La plus haute (une membrure) | La plus critique : pas d'installation sans relevé |

Les paramètres d'encombrement (largeur 1200 mm, profondeur 800 mm,
hauteur 2000 mm, longueur de poutre 1800 mm, sections 80 × 80 mm) sont
des **paramètres d'aboutissant à valider**, pas des cotes de meuble. Si
le support de bâtiment est inconnu, la valeur reste `None` + TODO :
rien n'est inventé (pas de CMU de cheville, pas de 63 × 175 de solive).

### 3.2 Jonctions

| Type | Démontable | Discrétion | Modularité | Repère |
|---|---|---|---|---|
| Tenon-mortaise collé | non | haute | faible | Règle Equinox : tenon = section/3, mortaise = 0,8 × section ; capacité catalogue 3000 N (hypothèse) |
| Queue d'aronde | non (coulissante : variante) | haute | faible | Pente 1:6 feuillu, hypothèse d'atelier ; **aucune CMU** dans les catalogues meubles (TODO essai) |
| **Tenon à clé** (défaut) | oui | moyenne (clé / bout de tenon) | moyenne | Tusk tenon Néogothique, compromis retenu |
| Raccord métallique (platine / barillet M8) | oui | faible sauf encastré | haute | Barillet catalogue Equinox 4000 N, insert M8 2500 N — le plus faible gouverne si on mixe |

Solidité / modularité / discrétion : plus la jonction est démontable et
reconfigurable, plus elle tend à devenir visible ou à s'appuyer sur une
vis dont la CMU (et celle de l'insert) peut être inférieure à celle d'un
nœud massif collé. Le tenon à clé est le compromis par défaut.

### 3.3 Charges chiffrées (hypothèses)

Utilisateur **120 kg**, g = 9,81 m/s², k_dyn = **2**, coefficient de
sécurité ancrage / bois = **3**, métal 1,8, renversement 1,5. Poussée
machine **400 N nominale validée** (800 N dynamique, CS 3 → 2400 N).

| Effort | Formule | Valeur |
|---|---|---|
| Poids | m × g | **1177 N** |
| Retenue (formule Equinox déjà au vocabulaire) | k_dyn × 0,5 × m × g | **1177 N** |
| Suspension pessimiste (poids entier, poutre) | k_dyn × m × g | **2354 N** |
| Poussée dynamique machine | 400 × k_dyn | **800 N** |
| Les mêmes, avec CS 3 (effort de calcul d'ancrage) | × 3 | **3532 / 7063 / 2400 N** |

La contrainte admissible bois du catalogue (14 MPa frêne / chêne, 12 MPa
noyer) est déjà une **contrainte admissible d'hypothèse**, distincte du
CS d'ancrage : on ne les multiplie pas l'un par l'autre sans le dire.
Vérification de flexion en travée simple, charge au milieu : M = F L / 4,
W = b h² / 6, σ = M / W. Avec la section 80 × 80 par défaut, σ ≈ 8,3 MPa
sous F_ret à 1200 mm, et ≈ 12,4 MPa sous F_susp à 1800 mm — encore sous
14 MPa, mais **juste** pour la poutre suspendue (augmenter h si la
portée ou la charge croît).

Pour une poutre suspendue à 2 suspentes, descente de charge (équipartition
hypothèse) ≈ **1177 N** par suspente en service dynamique, **3532 N**
avec CS 3 — à comparer à une capacité de solive **aujourd'hui inconnue**.
Pas d'installation murale ou suspendue sans relevé du support.

### 3.4 Matrices de compatibilité

### Cadres × aboutissants

| Typologie | sex_machine_mecanique | port_vac_u_lock | collecteur_urine | sangles | colliers | manilles | anneaux |
|---|---|---|---|---|---|---|---|
| cadre_mural | **limite** — Possible si un anneau mural est à la bonne hauteur, mais la machine développe 800 N de poussée dynamique et un moment que le mur doit reprendre (capacité murale TODO). Sans relevé du support, ne pas compter sur cette typologie pour la machine. | **compatible** — Ports natifs sur traverse haute et montants, cache affleurant — bien adapté au mur. | **limite** — Entonnoir déployable en pied de cadre, cuve dans un tiroir bas. Pas de gouttière sous siège (pas d'assise). Dépend d'un dégagement au sol contre le mur. Compatible en principe, moins naturel que le cadre au sol. | **a_venir** — Ancrages muraux du cadre (à venir), sous réserve du support de bâtiment. | **a_venir** — Idem. | **a_venir** — Idem ; la descente de charge va au mur (TODO). | **compatible_adaptateur** — Anneaux portés par le cadre. Liaison éventuelle à un ancrage de meuble existant par adaptateur, sans modifier le meuble. Le mur reste le maillon TODO. |
| cadre_sol | **compatible** — La machine se bride sur un anneau / œillet M8 porté par le cadre (même logique qu'Equinox) ou sur un montant, sans modifier un meuble. Le châssis repose au sol dans l'emprise du cadre : meilleur cas pour la stabilité déjà juste de la machine (800 N à 700 mm). Prévoir un point d'accroche à hauteur réglable. | **compatible** — Ports natifs sur traverses et montants (plots rapportés + ergot, verrouillage collier, arrière 1 pouce NPT, cache à l'état fermé). | **compatible** — Caisson au sol sous / à l'arrière du portique, entonnoir ou gouttière, cuve amovible 500 mL, éventuellement NPT de fond. Rien de visible si tiroir / panneau bas dans une longrine. Ne pas utiliser l'ergot Vac-U-Lock comme raccord de fluide. | **a_venir** — Points d'accroche / anneaux sur montants et traverses (grammaire sangles à venir). | **a_venir** — Idem, hauteur typique cou / poignets à caler sur la hauteur du cadre (2000 mm défaut). | **a_venir** — Manilles sur anneaux ou inserts M8 du cadre ; CMU à caler (hyp. CS 3). | **compatible** — Anneaux DI 40 / fil Ø8 (famille Equinox, CMU catalogue 2500 N) ou œillets CMU 2000 N peuvent être portés par le cadre lui-même, sans percer un meuble. |
| poutre_suspendue | **incompatible** — La machine a besoin d'un appui au sol (stabilité au renversement déjà juste, Ms/Mr faible sous 800 N à 700 mm). La suspendre à une poutre aggraverait le moment et ferait porter F_poussée + poids sur des solives non relevées. Machine au sol indépendante seulement, pas accrochée à la poutre. | **compatible** — Ports sous / sur la face de la poutre (plots). Le cache fermé préserve une certaine discrétion. La charge d'un accessoire s'ajoute à F_susp — rester dans les efforts déclarés, support TODO. | **incompatible** — Pas de structure au sol : le collecteur ne peut pas être « dans » la poutre. Un caisson indépendant au sol reste possible, mais ce n'est plus un aboutissant de la poutre (le traiter à part, comme un collecteur de typologie aboutissants). | **a_venir** — Sangles / suspentes depuis la poutre ; effort renvoyé aux solives (TODO). | **a_venir** — Idem, hauteur sous poutre à caler (hauteur sous plafond non cotée). | **a_venir** — Manille sur anneau de poutre ; descente de charge vers le plafond TODO. | **compatible** — Anneaux sous la poutre (famille Equinox). Capacité limitée par le *support de solive* (TODO), pas seulement par la CMU d'anneau 2500 N. |

### Cadres × ancrages de meubles

| Typologie | Equinox | Néogothique | Incognito (hors pouf) |
|---|---|---|---|
| cadre_mural | **compatible_adaptateur** — Peut cohabiter avec une typologie murale (croix de Saint-André) en s'appuyant sur des anneaux d'extrémité *sans les modifier*, ou rester un cadre indépendant fixé au mur (support mural TODO, distinct des ancrages Equinox). | **limite** — L'Entrave est déjà un meuble au sol à plaques. Un cadre mural est un second dispositif ; pas de cote d'accroche murale dans la grammaire Entrave. Pas de percage du meuble. | **limite** — Un cadre mural apparent casse la discrétion Incognito (canapé, banquette, bibliothèque…). Une bibliothèque pourrait *masquer* un cadre (plinthe / montants) : typologie salon sans grammaire livrée, ancrages TODO. Ne pas modifier /workspace/incognito, ne pas cibler le pouf. |
| cadre_sol | **compatible_adaptateur** — Le cadre est autonome. Option : le relier sans perçage à un anneau DI 40 ou un œillet de semelle (DI 12, saillie 18 mm) par une chape, pour l'immobiliser au sol. M8 côté accessoire. Les CMU catalogue (œillet 2000 N, anneau 2500 N) peuvent gouverner si on s'y ancre. | **compatible_adaptateur** — Bride sur plaques 40×40×6 (x=±315, y typ. ±235 mm Entrave défaut, capacité 2000 N) sans percage. Filetage et DI d'anneau des plaques : TODO. Le cadre peut aussi rester indépendant dans le rectangle des plaques. | **limite** — Un portique au sol contredit la règle « rien de visible à l'état fermé ». On ne l'installe pas dans le même salon qu'une banquette Incognito si la discrétion de gamme doit tenir, sauf démontage complet. Adaptateur sur insert Ø12 (filetage TODO) possible en théorie, sans modifier le meuble, mais la présence du cadre reste visible. Pouf vibrant : hors sujet collecte ; on ne le cible pas, on ne le modifie pas. |
| poutre_suspendue | **limite** — Pas d'ancrage plafond dans Equinox (œillets au sol, anneau de traverse). La poutre est un aboutissant de bâtiment, pas un accessoire du meuble. Cohabitation possible sans liaison. | **limite** — Pas d'ancrage plafond relevé. Même logique : pas de liaison inventée vers les plaques au sol. | **limite** — Une poutre apparente sous plafond heurte la discrétion de salon, sauf si elle se fait oublier en solive habillée (hors scripts actuels). Support de plafond TODO. Pas de modification des meubles, pouf non ciblé. |

### 3.5 Lecture des compromis

- **Cadre au sol** : seul à offrir, sans le bâtiment, un accueil
  naturel de la machine, du collecteur et des ports. On paie en
  discrétion (volume visible), ce qui le rend **limite** dans un salon
  Incognito.
- **Cadre mural** : meilleur plat, ports bien placés, mais toute charge
  (800 N de poussée, retenue 1177 N, calcul CS3 bien au-delà) passe par
  un mur non relevé.
- **Poutre suspendue** : la plus discrète, incompatible avec la machine
  (stabilité au sol déjà juste) et avec un collecteur « dans » la
  poutre ; les solives manquent au dossier.

Les meubles existants ne sont jamais percés : au mieux un **adaptateur**
(chape d'anneau Equinox, bride de plaque Néogothique, douille Ø12
Incognito, filetages TODO). Le pouf vibrant reste hors cible collecte et
n'est pas modifié.

---

## 4. Fichiers créés ou mis à jour

Couche 1 : `common/params_globaux.py` (paramètres Vac-U-Lock, NPT,
collecteur, cadre — chacun documenté : valeur, unité, plage,
justification, source ; TODO explicites).

Couche 2 : `catalogues/materiaux.py` (polymères PP/PE-HD, joints, tenue
urée / ammoniac / désinfectants), `catalogues/vac_u_lock.py`,
`catalogues/jonctions_cadre.py`.

Couche 3 :

- `interfaces/port_vac_u_lock.py`
- `mouvement/sex_machine_mecanique.py` (port en bout de tige)
- `hygiene/collecteur_urine.py`
- `cadres/cadre_modulaire.py`

Tests hors Fusion (aucun `import adsk` au niveau module) :
`tests/test_port_vac_u_lock.py`, `tests/test_collecteur_urine.py`,
`tests/test_cadre_modulaire.py`, plus les tests déjà présents. Exécution :

```bash
cd /workspace/aboutissants && /workspace/.venv/bin/python -m pytest
```

Résultat : **56 passed**.
