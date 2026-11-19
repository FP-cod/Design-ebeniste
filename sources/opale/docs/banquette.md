# Banquette Incognito — grammaire et compromis

Premier meuble de la gamme : une **banquette de salon classique**
(dossier, assise capitonnée, pieds tournés ou fuseaux, tissu sobre)
qui cache un **banc à fessée**. Rien, à l'état fermé, ne trahit la
fonction.

Grammaire : `incognito/grammaires/banquette.py` (Python pur,
testable hors Fusion). Script de génération :
`scripts_fusion/incognito_banquette.py`.

Les cotes du banc déployé (appui **700 mm** × longueur **1150 mm**)
sont des **hypothèses documentées**. Le squelette Equinox disponible
dans `/workspace/equinox` ne contenait que l'architecture du package,
sans les cotes du banc Feuille / Flore : rien n'a donc été repris.

---

## Mécanisme retenu

L'assise se soulève comme un **coffre** :

- charnières invisibles type Soss (typiquement 3), entièrement
  mortaisées dans le chant arrière du couvercle et le panneau arrière ;
- vérins ou compas de maintien (typiquement 2), entièrement contenus
  dans le caisson à l'état fermé ;
- le banc se déploie depuis l'intérieur du caisson : les joues se
  redressent, une traverse les verrouille, le panneau d'appui se place
  à 700 mm, le cuir devient accessible.

Le panneau arrière est **unique** (paroi de caisson et dossier d'un
seul tenant) pour éviter un raccord faible au niveau de l'assise.

### Alternative écartée : dossier basculant ou coulissant

Un dossier qui bascule ou coulisse pour libérer le banc a été écarté,
parce qu'il est **moins solide** et moins discret :

- le dossier est un cadre relativement léger (panneau mince + montants),
  pas une boîte de torsion comme le caisson ; les efforts de charnière
  s'y appliqueraient avec un bras de levier long, au risque de déverser
  les assemblages dossier / caisson ;
- un coulissement impose un jeu, un rail ou une lumière : indices
  visibles en façade, et section restante du traversin arrière
  affaiblie par le mécanisme ;
- le dossier ouvert ne fournit pas une base large et basse au banc
  déployé, contrairement au caisson qui reste en place.

L'ouverture en coffre conserve la boîte structurelle intacte, appuie
les charnières invisibles dans une section généreuse, et sort le
couvercle du chemin de charge du banc.

---

## Deux états, un seul jeu de paramètres

| État | Valeur `inc_etat_deploiement` | Géométrie |
| --- | ---: | --- |
| `FERMEE` | 0 | Apparence salon |
| `DEPLOYEE` | 1 | Banc sorti, couvercle ouvert (~95°), béquille avant en place |

`calculer(etat, params)` et `calculer_deux_etats(params)` partent des
**mêmes** paramètres de base. Les pièces mobiles (couvercle, banc,
béquille, trappes) changent de position ; le caisson, les pieds et le
dossier restent.

---

## Cotes par défaut (état fermé — salon)

| Grandeur | Défaut | mm |
| --- | ---: | --- |
| Longueur hors-tout | 1300 | |
| Profondeur hors-tout (y compris dossier) | 680 | |
| Hauteur d'assise (dessus de coussin) | 430 | |
| Hauteur de dossier | 880 | |
| Hauteur des pieds | 120 | |
| Épaisseur des parois / dossier / couvercle | 22 | |
| Épaisseur du fond | 18 | |
| Mousse d'assise | 80 | |
| Mousse de dossier | 70 | |

Pile d'assise (dérivée) :

```text
pieds 120 + caisson 206 + couvercle 22 + mousse 80 + tissu 2 = 430 mm
hauteur intérieure du caisson = 206 − 18 = 188 mm
```

---

## Cotes par défaut (état déployé — fonctionnel)

| Grandeur | Défaut | mm | Origine |
| --- | ---: | --- | --- |
| Hauteur d'appui (dessus du cuir) | 700 | | Hypothèse |
| Longueur d'appui | 1150 | | Hypothèse |
| Largeur d'appui | 320 | | Hypothèse |
| Épaisseur du panneau d'appui | 28 | | |
| Mousse du banc + cuir | 30 + 2 | | |
| Épaisseur / largeur des joues | 32 / 280 | | |
| Traverse (anti-déversement du cadre) | 22 × 80 | | |
| Angle d'ouverture du couvercle | 95 | ° | |

### Appui des joues

Par défaut, les joues **traversent le fond** du caisson par des lumières
obturées, à l'état fermé, par des **trappes affleurantes**, et
prennent appui **au sol**. Chemin de charge direct ; le caisson sert
de cadre anti-déversement.

Alternative (paramètre `appui_joues_au_sol=False`) : les joues
reposent sur le fond du caisson. Plus simple, mais le fond et ses
assemblages doivent tout reprendre — plus exigeant, à réserver à des
charges plus faibles ou à un fond renforcé. Non retenu par défaut.

---

## Béquille avant / appuie-genoux

Une béquille déployable vers l'avant (portée 400 mm, appuie-genoux à
300 mm de haut) est **retenue par défaut**. Elle est entièrement
rangée dans le caisson à l'état fermé.

Elle a deux rôles : confort d'usage (appui des genoux) et
**allongement de l'emprise au sol**, sans lequel une banquette de
salon, même lestée, ne résiste typiquement pas à une traction
horizontale de 1500 N à 700 mm de haut.

Un lest acier d'environ **10 kg**, posé sur le fond, est également
prévu (invisible à l'état fermé). Il aide, mais ne suffit pas à lui
seul.

---

## Pièces (liste de la grammaire)

- 4 pieds tournés / fuseaux (`pied_avg`, `pied_avd`, `pied_arg`, `pied_ard`)
- caisson : parois avant, gauche, droite ; fond ; panneau arrière-dossier unique
- assise-couvercle + coussin / tissu de façade
- coussin de dossier (tissu de façade)
- banc : panneau, coussin cuir, joue gauche, joue droite, traverse
- blocs d'ancrage locaux (un par point, typiquement 4) + inserts noyés
- trappes de fond (état fermé, si appui au sol)
- lest
- béquille : appuie-genoux + deux pieds (si activée)

Assemblages : **tourillons** et **mortaises-tenons** uniquement en
structure bois ; charnières Soss et vérins invisibles à l'état fermé ;
ancres métalliques noyées, cache affleurant. Aucune vis apparente.

---

## Ancrages

Quatre points d'ancrage pour bracelets, intégrés dans la structure
bois du banc, près des coins du panneau d'appui. Inserts métalliques
noyés dans des **blocs locaux recalculés** (`incognito.regles.recaler_bloc_ancrage`)
selon l'essence et la charge, collés et tourillonnés sous le panneau,
masqués par le cuir. À l'état fermé, tout le banc est dans le caisson :
rien n'est visible.

Charge de service par ancre : **1500 N**. Coefficient de sécurité
**≥ 3** recommandé. Charge de rupture visée : **4500 N**.

---

## Compromis discrétion maximale / résistance

1. **Bloc local plutôt que rail épais.** Un panneau d'appui de 28 mm
   est trop mince pour noyer une ancre 1500 N / CS 3 tout en gardant
   10 mm de retrait sous la surface. Un rail assez épais pour tout
   loger (souvent > 50 mm une fois le cache compris) ne rentrerait
   plus, avec les joues couchées, dans les 188 mm intérieurs du
   caisson, ou ferait une assise trop lourde visuellement. Le bloc
   local, masqué sous le cuir, est le bon côté du compromis.
2. **Retrait de discrétion vs paroi de bois.** Réduire le cache
   trahit l'ancre. On n'y touche pas ; on grossit le bloc caché.
3. **Lumières dans le fond.** Meilleur chemin de charge (appui au
   sol), mais les trappes doivent être parfaitement affleurantes.
   Elles ne se voient que si l'on se penche sous le meuble ; un jeu
   trop grand ou un bois qui travaille les rendrait détectables.
   L'alternative « joues sur le fond » est plus discrète sous le
   meuble, moins solide.
4. **Mortaise Soss dans le panneau arrière.** Le panneau doit rester
   assez section après mortaisage. Ne pas y loger d'ancrage en plus.
5. **Stabilité au basculement.** C'est le compromis le plus sévère.
   Une traction horizontale de 1500 N à 700 mm de haut produit un
   moment de 1050 N·m. Sans béquille avant, le modèle simplifié
   donne un coefficient d'environ 0,56 à vide et 1,03 avec un usager
   sur l'appui — **non conforme** (minimum visé 1,5). Avec la
   béquille avant de 400 mm (défaut) : environ 1,02 à vide (toujours
   insuffisant) et 2,08 avec usager (passe le seuil du modèle). Donc :
   - à vide, il ne faut **pas** solliciter les ancrages, même avec
     la béquille ;
   - les efforts d'ancrage et le poids de l'usager ne se compensent
     que partiellement ;
   - ancrer le caisson au sol ou au mur serait plus sûr, au prix de
     l'apparence « meuble simplement posé » ;
   - ces coefficients sont indicatifs (la masse du modèle est une
     enveloppe, avec recouvrements de pièces) et n'exemptent pas
     d'un essai réel.
6. **Profondeur du meuble.** L'allonger (au-delà de 680 mm) aide la
   stabilité et le rangement, au détriment d'une silhouette de
   banquette très classique.

---

## Ce qui exige un essai de charge réel (et un ingénieur)

Les vérifications de la grammaire (`stabilite_*`, `validation_ancrage`,
etc.) sont des **modèles de conception simplifiés**. Elles ignorent le
dynamisme d'un à-coup, le glissement des pieds, la souplesse du cadre,
les défauts du bois, `k_mod` et `γ_M`.

Avant tout usage :

- justificatif par un ingénieur (Eurocode 5 ou équivalent, y compris
  assemblages et dynamique) ;
- **essai de charge réel** sur prototype :
  - appui du banc, charge verticale progressive puis à-coups, au
    moins jusqu'à la charge de rupture visée ;
  - chaque ancrage, traction dans les directions d'usage, idem ;
  - **essai de stabilité** meuble déployé, avec et sans usager,
    y compris effort horizontal sur un ancrage ;
- vérification que, à l'état fermé, aucune ferrure, lumière ou
  différence de son ne trahit le mécanisme (contrôle discret, pas un
  essai de charge).

Le script Fusion et le package Python **ne certifient rien**.

---

## Paramètres Fusion

`vers_parametres_fusion_banquette()` exporte les cotes propres à la
banquette, dont :

- `inc_etat_deploiement` (0 / 1, sans unité) ;
- `inc_banq_longueur`, `inc_banq_profondeur`, `inc_banq_hauteur_assise`,
  `inc_banq_hauteur_appui`, `inc_banq_longueur_appui`, etc. ;
- les cotes dérivées du caisson (`inc_banq_hauteur_interieure`, …).

Le script `scripts_fusion/incognito_banquette.py` crée ces paramètres,
génère un composant par pièce, et se relance après modification de
`inc_etat_deploiement` pour basculer l'état. Un joint pivot est
tenté sur le couvercle (charnière) ; selon les versions de l'API, il
peut falloir le parachever à la main dans Fusion (revolute as-built
sur le chant arrière). Les unités internes de l'API sont des cm ;
la conversion est isolée dans `incognito.fusion_outils.mm_vers_cm`.

---

## Questions ouvertes pour Fabien

- Essence préférée ? (défaut : chêne)
- Charge cible par ancrage ? (défaut : 1500 N, CS 3 → 4500 N visés)
- Revêtement de façade et couleur ? (défaut : velours)
- Cuir du banc : cognac (défaut) ou noir ?
- Longueur / profondeur de la banquette : 1300 × 680 mm conviennent-ils,
  ou un meuble plus généreux (stabilité, confort visuel) est-il souhaité ?
- Appuie-genoux / béquille avant retenu (recommandé pour la stabilité)
  ou écarté au profit d'un autre dispositif (lest beaucoup plus lourd,
  ancrage au sol) ?
- Appui des joues au sol (lumières + trappes, défaut) ou sur le fond
  du caisson ?
- Nombre et position exacte des ancrages : quatre coins du banc
  (poignets / chevilles) suffisent-ils, ou faut-il des points de
  taille / relais sur le caisson intérieur ?
- Faut-il un profil de pied plus précis (modèle de tournage) dès cette
  couche, ou le laisser à l'ébénisterie / CAM ?
