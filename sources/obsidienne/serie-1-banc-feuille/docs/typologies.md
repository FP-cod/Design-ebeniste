# Typologies de mobilier de salle de jeux : recherche et fiches grammaire Equinox

Recherche web faite le 18/11/2026. Il n'existe pas de chiffres de vente publics. Le classement
ci-dessous **recoupe** donc les signaux de popularité disponibles : listes « best-sellers » ou
« les plus populaires » des boutiques, ordre des guides « must-have », et fréquence d'apparition
dans les catalogues. C'est un **classement qualitatif**, pas une mesure de marché.

## Sources

| # | Source | Type | Ce qu'elle indique |
|---|---|---|---|
| S1 | [Metalbound – Top 10 Must-Have BDSM Furniture](https://www.metalbound.com/must-have-bdsm-furniture/) | fabricant / guide | ordre : 1 banc de fessée, 2 lit, 3 croix de Saint-André, 4 chaise, 5 portique de suspension, 7 tabouret de queening, 8 table, 9 cheval pliant |
| S2 | [Tabooless – Best sex furniture 2026](https://tabooless.net/toys/best-sex-furniture-sex-swing-and-more/) | guide | « les balançoires et les bancs sont les meubles les plus populaires » ; croix « iconique » |
| S3 | [BDSMWoody – Best Sellers](https://bdsmwoody.com/fr/collections/best-sellers) | boutique bois | best-sellers dominés par les bancs de fessée réglables, puis la croix de Saint-André, les lits et une table-croix |
| S4 | [Jeux particuliers – boutique](https://jeuxparticuliers.fr/boutique/) | artisan FR (Compagnons du Devoir) | « les plus populaires » : croix de Saint-André, cage de soumission, banc des tentations ; aussi banc à fessées, tabouret modulable, oratoire |
| S5 | [Ryco / Dungeon in a Bag – About](https://dungeoninabag.com/pages/about) | fabricant | la croix de Saint-André fait partie de ses meilleures ventes |
| S6 | [Atomique – BDSM Furniture guide](https://www.atomique.club/post/bdsm-furniture) | club / guide | croix « la plus reconnaissable » ; banc ; cheval de fessée « l'un des plus courants » |
| S7 | [Kinkstay – 12 pieces explained](https://kinkstay.com/bdsm-furniture-guide/) | guide | banc/cheval = la première pièce la plus accessible ; chaise, cage, portique, stocks, pilori ; fourchettes de prix |
| S8 | [Steeltoyz – Meubles BDSM](https://www.steeltoyz.fr/bdsm-bondage/meubles-bdsm/) | fabricant inox | « parmi les plus appréciés » : chevalets, bancs de fessée, lits, cadres, croix |
| S9 | [Meuble BDSM – shop](https://meublebdsm.fr/shop) | boutique FR | catalogue très riche en cages, croix, bancs, pilori, barres d'écartement, sling |
| S10 | [Wikipedia – List of BDSM equipment](https://en.wikipedia.org/wiki/List_of_BDSM_equipment) | encyclopédie | inventaire des typologies (A-frame, Berkley horse, stocks, queening stool, rack, wheel…) |
| S11 | [Démasqué Magazine – BDSM & dungeon furniture](https://www.demasquemagazine.com/post/different-types-of-bdsm-furniture) | magazine | cages, stocks et pilori, cheval de Berkley, cheval de fessée, queening, portique |
| S12 | [BDSM Authority – Sex dungeon furniture](https://bdsmauthority.com/blogs/bdsm-equipment/sex-dungeon-furniture) | guide | 6 familles : bancs/chevaux, croix/cadres, cages, slings, trônes/chaises, tables/lits |

## Classement par popularité

| Rang | Typologie | Signaux | Grammaire Equinox |
|---|---|---|---|
| 1 | **Banc de fessée / de contrainte (agenouillé)** | S1 n°1, S2, S3 (la majorité des best-sellers), S4, S6, S7, S8 | `banc_flore.py` (**complet**) |
| 2 | **Croix de Saint-André** | S1 n°3, S3 n°2, S4 n°1, S5, S6, S8, S2 | `croix_saint_andre.py` (squelette fonctionnel) |
| 3 | **Chaise / trône de contrainte** | S1 n°4, S7, S12, Eromale (2 chaises au catalogue) | `chaise_trone.py` (squelette fonctionnel) |
| 4 | Lit / table de contrainte | S1 n°2 et n°8, S3, S8, S12 | fiche ci-dessous |
| 5 | Cheval / chevalet de fessée | S1 n°9, S6, S8 (cité en premier), S11 | fiche (dérivable de `banc_flore` + override `cheval_arcon`) |
| 6 | Portique de suspension / sling | S1 n°5, S2 (« le plus populaire » avec les bancs), S7, S11 | fiche (pas de script : sécurité critique) |
| 7 | **Tabouret (modulable / queening)** | S1 n°7, S4, S10, S11 | `tabouret.py` (squelette fonctionnel) |
| 8 | Cage | S4 (top 3), S9 (le plus de références), S7, S11 | fiche |
| 9 | Pilori / stocks | S7, S9, S11 | fiche |
| 10 | Barre d'écartement / poutre | S4, S9 | fiche (accessoire) |
| 11 | Oratoire / prie-Dieu, cheval de Berkley, roue, A-frame, tour | S4, S10, S11 | fiches courtes |

Scripts écrits pour les 4 premières typologies demandées : banc (complet), croix, chaise/trône, tabouret.
Le lit/table arrive au rang 4, mais on a gardé le tabouret, explicitement demandé. Le lit/table est
le prochain script à écrire.

## Règles communes à toutes les fiches (vocabulaire Equinox)

- Bois : frêne, fuseaux Ø50 au nœud → Ø40 entre nœuds → Ø30 aux extrémités, splay de 7°, courbes de
  rayon ≥ `bois.rayon_courbure_min`, lamellé-collé pour les grandes courbes.
- Garnissage : cuir cognac, 30 mm de mousse HR sur contreplaqué de bouleau de 18 mm, rayons de bord dérivés
  du matériau (règles).
- Métal : inox 316L brossé, plaques de 2 mm, œillets en fil de 8 mm, capuchons laiton Ø40 × 3.
- Jonctions : tenon-mortaise chevillé aux nœuds, tourillons sur les traverses, inserts M8 pour tout le
  démontable et toute la quincaillerie (jamais une vis dans le bois de bout pour une retenue).
- Ancrages : `ancrages.py`, avec les œillets sous les semelles et des anneaux à mi-hauteur des traverses.
  Effort de calcul d'un point de retenue : 2 × 0,5 × 120 kg × g ≈ 1 180 N (à valider). La CMU marquée du
  fabricant doit être supérieure à cet effort.
- Charge : 120 kg × coefficient dynamique 2. Efforts horizontaux : 0,30 (longitudinal) et 0,15 (latéral)
  × poids. Sécurité : renversement 1,5, bois MOR/3, métal Re/1,8.
- Tout le mobilier de contrainte doit pouvoir être libéré vite : mousquetons à ouverture rapide, aucun
  point de retenue au cou, ciseaux de sécurité à portée. Ce sont des exigences de conception reprises
  dans chaque fiche.

---

## 1. Banc « Flore » (banc de fessée / agenouillé), script complet

Voir `equinox/grammaires/banc_flore.py` et `docs/rapport_banc_flore.txt`. Position levrette dans le sens
de la longueur : genoux à l'arrière sur les ellipses des hélices, buste sur le plateau incliné à 2°
(bassin haut), coudes à l'avant sur les branches.

## 2. Croix de Saint-André « Nervure », squelette

- **Esprit** : deux nervures de feuille en lamellé-collé, légèrement cintrées, croisées à mi-bois.
  Croix inclinée de 6° vers l'arrière, jambe de force en branche.
- **Composants** : `branche_1/2` (fuseau extrémité → nœud → extrémité), `jambe_de_force`,
  `semelle_avant`, `semelle_arriere` (tube 40×40 lesté), `plateforme` à lattes, 6 anneaux (poignets,
  chevilles, taille), œillets sous la semelle avant.
- **Paramètres** : `croix.hauteur` 2100, `largeur_haut` 1250, `largeur_bas` 950, `inclinaison` 6°,
  `profondeur_base` 750, `profondeur_plateforme` 550, `section_branches` 60.
- **Attaches** : mi-bois collé + 2 platines inox de 2 mm + 4 inserts M8 au nœud. Jambe démontable
  (M10 + barillet). Anneaux sur pontet et tige M8 traversante.
- **Sécurité / charge** : sans plateforme, la traction de la personne à 1,9 m fait basculer la croix
  (le script demande environ 200 kg de lest). **Avec plateforme**, la personne se tient sur le meuble :
  ses tractions deviennent internes et seule la poussée du partenaire compte, ce qui passe. Branches :
  Ø71 nécessaire au nœud pour 1 180 N au poignet (alerte du script). On peut aussi prendre une section
  ovale de lamellé-collé ou fixer la croix au mur.

## 3. Chaise / trône « Éventail », squelette

- **Esprit** : dossier en éventail de nervures (une centrale et des secondaires) coiffé d'une branche
  haute. Accoudoirs fins en branche, pieds arrière en sabre.
- **Composants** : `assise`, 4 pieds, `nervure_0..n`, `branche_haute`, `accoudoir_G/D`, anneaux aux
  poignets et chevilles, œillets sous les pieds arrière.
- **Paramètres** : `chaise.hauteur_dossier` 1250, `inclinaison_dossier` 12°, `nervures` 5,
  `hauteur_accoudoirs` 670, `recul_pieds_arriere` 220. Assise à 460 mm (override de typologie),
  inclinée de 4°.
- **Sécurité** : le basculement arrière sous un appui au dossier reste en ALERTE (ratio 1,37 pour 1,5
  exigé ; il manque environ 33 kg de lest). Solutions : plus de recul des pieds, un dossier moins
  incliné, ou un ancrage au sol. Les accoudoirs Ø30 sont trop fins au droit des anneaux de poignet : il
  faut Ø40 localement (nœud).

## 4. Lit / table de contrainte « Canopée », fiche

- **Esprit** : plateau garni de 1900 × 800 sur quatre pieds-branches, ceinture périphérique en nervure.
  Option ciel de lit en branches cintrées, sur le principe d'un portique léger.
- **Composants** : plateau (2 ou 3 sections), ceinture, 4 à 6 pieds, rail d'ancrage périphérique (tube
  inox de 12 mm noyé dans le chant, anneaux coulissants), tiroirs sous le plateau.
- **Paramètres** : `hauteur_assise` 650 à 750 (table) ou 450 (lit), longueur 1900 à 2000, largeur
  750 à 1400, nombre de pieds 4 ou 6.
- **Attaches** : ceinture en tenons-mortaises, plateau sur inserts M8, rail fixé par pattes et inserts
  tous les 300 mm.
- **Charge** : 2 × 120 kg × 2 dynamique, longerons à vérifier en flexion (portée 1,9 m : prévoir 6 pieds
  ou une hauteur de longeron ≥ 120).

## 5. Cheval / chevalet de fessée « Arçon », fiche

- **Esprit** : variante courte et haute du banc Flore. Poutre garnie de 700 × 260 à 760 mm, deux paires
  de pieds en A splayées, appuis genoux et coudes en branches latérales.
- **Script** : override `cheval_arcon` déjà prévu dans `parametres.py` (760 / 700 / 260). Il se dérive de
  `banc_flore` en remplaçant les hélices par des branches fixes. Variante pliante sur charnières inox
  avec verrou.
- **Charge** : appui ventral concentré. Vérifier la poutre en flexion avec une charge ponctuelle de
  120 × 2 × 0,6.

## 6. Portique de suspension / sling « Arche », fiche (pas de script automatique)

- **Esprit** : arche en lamellé-collé, deux arcs croisés (dôme) ou un arc plus deux jambes. Anneaux
  inox au sommet.
- **Paramètres** : hauteur libre ≥ 2200, portée, section lamellé ≥ 80 × 120 (à calculer), pieds
  lestés ou ancrés.
- **Sécurité, non négociable** : les charges dynamiques de suspension sont fortes (coefficient ≥ 3).
  Il faut une quincaillerie certifiée avec CMU (manilles, anneaux forgés), une note de calcul faite par un
  ingénieur bois (Eurocode 5), une procédure de descente d'urgence et des pratiquants formés (S7). Pas de
  script généré tant que le calcul n'est pas validé.

## 7. Tabouret « Graine » (modulable / queening), squelette

- **Esprit** : assise feuille de 400 × 380, 4 pieds fuseau splayés, ceinture basse en branches cintrées
  portant 4 anneaux. Option d'échancrure avant pour le queening.
- **Paramètres** : `hauteur_assise` 440 (override), `tabouret.echancrure` (0 = plein),
  `hauteur_ceinture` 160, `retrait_pieds` 50.
- **Sécurité / charge** : stable avec 120 kg assis. La ceinture basse Ø30 est en limite (alerte) sous la
  traction d'un anneau : il faut Ø32 ou des anneaux placés près des nœuds. En queening, prévoir un
  rembourrage plus ferme (densité 60) et une échancrure à rayon ≥ 20.

## 8. Cage « Racines », fiche

- **Esprit** : barreaux en frêne tourné (Ø30 à 35) entre deux cadres en lamellé, comme des racines
  verticales. Le dessus sert de banc garni (combinaison cage et banc, comme chez S4 et S9).
- **Paramètres** : dimensions intérieures (couchée 1200 × 700 × 800, debout 700 × 700 × 1900),
  entraxe des barreaux ≤ 100.
- **Sécurité** : la porte doit s'ouvrir vite de l'extérieur **et** pouvoir être déverrouillée par une
  tierce personne sans outil. Ventilation, arêtes rayonnées, accès rapide à la personne (S7).

## 9. Pilori / stocks « Liane », fiche

- **Esprit** : planche garnie à charnière en deux demi-lunes de frêne, montée sur un mât-branche
  réglable en hauteur (crans inox, même principe que le pivot des hélices).
- **Sécurité** : l'ouverture du cou doit être **largement surdimensionnée** et ne jamais comprimer.
  Ouverture instantanée (goupille à billes), réglage en hauteur pour éviter toute suspension par la
  tête (S7).

## 10. Barre d'écartement / poutre « Tige », fiche

- **Esprit** : tige en frêne Ø40 avec capuchons laiton et anneaux coulissants sur un insert inox, ou
  poutre de sol basse servant de semelle d'ancrage.
- **Script** : très simple, une seule primitive `Fuseau` plus des `ancrages.anneau_traverse`.

## 11. Autres

- **Oratoire / prie-Dieu** (S4) : agenouilloir garni et appui-coudes, petit cousin du banc Flore.
- **Cheval de Berkley** (S11) : cadre incliné à ouvertures, proche de la croix inclinée.
- **Roue, A-frame, tour** (S9, S10) : faible demande, mécanique spécifique (roulements, freins).
