# Style Neogothique « raffine » (v0.2) : vocabulaire et parametres

Le style reste medieval / neogothique : angles francs, sections carrees ou
octogonales, ferrures apparentes, assemblages chevilles, aucune vis visible.
L'elegance vient de la **finition** : proportions reglees, moulures sur les
chants, ferronnerie plus fine et forgee, sellerie de maroquinier. La regle
« zero courbe organique » de la v0.1 devient : **pas de courbes organiques type
Equinox (splines, galbes libres), mais des moulures et chanfreins travailles sur
les chants**. Toute la geometrie est faite de droites et d'arcs de cercle
(quarts de cercle des moulures, arcs brises des ogives, lobes), donc usinable a
la toupie / fraise de forme et dessinable exactement dans Fusion.

## 1. Proportions (`style.proportions`)

| Mode | Plinthe / fut / chapiteau (H = hauteur visible du pied) | Remarque |
|---|---|---|
| `nombre_or` (defaut) | H/phi^4, H/phi, H/phi^3 (14,6 % / 61,8 % / 23,6 %) | 1/phi + 1/phi^3 + 1/phi^4 = 1 exactement |
| `harmonique` | 1 : 5 : 2 (12,5 % / 62,5 % / 25 %) | plinthe/chapiteau = octave, chapiteau/fut = dixieme majeure |
| `libre` | `style.part_plinthe`, `style.part_chapiteau` | parts <= 0,7 au total (validation) |

Les autres rapports de la gamme : platine 800 x 400 (2:1, octave) ;
semelle 140 x 54 (largeur / phi^2) et 566 de long (400 x racine(2), trace
*ad quadratum*) ; ceinture 80 mm (≈ 50 x phi) ; chant inferieur de platine
31 mm (50 / phi) ; ogives equilaterales (`style.ratio_rayon_ogive` = 1).

**Contrainte mecanique** : le loquet doit tomber dans le fut, entre la bague et
l'astragale. La fenetre est etroite (≈ 172 a 177 mm) : un chapiteau ou une
plinthe plus hauts (mode libre, rapport 1:4:2...) la ferment, la grammaire leve
alors une `ErreurGeometrie` explicite.

## 2. Pied-colonne (`entrave.pied.*`)

De bas en haut : **plinthe** (abaque inferieur, debord `debord_base` par face,
conge `rayon_conge_plinthe` vers le fut) ; **bague forgee** au pied du fut
(`fourreau.frette_hauteur`) ; **fut** au fruit leger (`fuselage` par face, ≈ 1,5
deg) dont les aretes portent un **chanfrein arrete** (`chanfrein_arrete`,
s'arretant a `longueur_arret` des extremites par un arret `droit` a 45 deg ou en
`langue_de_boeuf`) ; **astragale** (boudin `rayon_astragale`) ; **chapiteau** :
cavet `rayon_cavet` sous un abaque (tailloir) occupant `part_abaque` du
chapiteau. `cote` est la cote du **fut** en bas ; plinthe et abaque font
`cote + 2 x debord_base` (124 mm). La paroi du fourreau est controlee sur les
plats (`fourreau.paroi`) et dans l'arete chanfreinee (`paroi_diagonale_min`).
En octogonal, les pans coupes remplacent le chanfrein arrete.

## 3. Chants moulures (`*.chant_*`)

Types disponibles (`profils.TYPES_CHANT`) : `droit`, `chanfrein`, `conge`
(quart-de-rond creux vers l'exterieur, doux au toucher), `quart_de_rond`
(convexe), `cavet` (creux), `bec_de_corbin` (tore + gorge + listel). Defauts :
platine dessus `conge` 4 mm, dessous `bec_de_corbin` 31 x 14 mm (allege
visuellement les 50 mm de noyer, -5,3 % de module de section seulement, flexion
recalculee) ; semelle `quart_de_rond` 8 mm, bouts en cavet (`garde_cavet`) ;
ceinture chanfrein bas 4 mm. Les aretes non moulurees gardent un adoucissement
`bois.chanfrein_aretes` de 1,5 mm (non modelise).

## 4. Ceintures ajourees (`entrave.ceinture.*`)

Bandeaux avant et arriere sous la platine (mobiles avec elle), en retrait de
`retrait` sous le bord, ajoures de `nombre_arcades` baies au motif
`style.motif_ajours` : `ogive` (arc brise, rayon `ratio_rayon_ogive` x baie),
`trilobe`, `quadrilobe`. Largeur de baie = `ratio_largeur` x entraxe ; bois
plein `marge` dessus et dessous ; les montants doivent garder au moins
`style.montant_mini` (verification `montants_ceinture`). Les ceintures
s'arretent avant les chapiteaux.

## 5. Ferronnerie (`ferrures.*`, `entrave.pentures.*`, `cremaillere.*`)

- Fer plat 28 x 4 (au lieu de 40 x 5) : non porteur, decor + anti-fente ;
  terminaisons forgees `ferrures.terminaison_pentures` : `fleur_de_lys`,
  `queue_d_aronde`, `trilobe`, `droite` (catalogue `TERMINAISONS`, qui impose
  une longueur de branche mini).
- Rivets **goutte de suif** : tige `rivet_diametre`, calotte
  `tete_rivet_diametre` x `tete_rivet_hauteur` (tete >= 1,5 x tige).
- Pieces porteuses affinees mais justifiees : chaque verification de ferrure
  affinee doit garder une marge >= `charges.marge_mini_ferrures` (1,5), sinon
  alerte (synthese `marges_ferrures`). Axe de pivot porte a 18 mm pour cela.
- Barre de calage 24 x 8 ; `cremaillere.decor_barre` (`lisse`, `festonnee`,
  `ajouree`) avec regle de **section nette mini** (le decor elargit la barre
  automatiquement) ; `cremaillere.habillage` : `capot_ajoure` (tole
  `capot_epaisseur` en U, lancettes), `plaque_decoupee` (quadrilobes), `aucun`.
- Finitions : « fer forge cire noir », « bruni », « laiton vieilli ».

## 6. Sellerie (`sellerie.*`, `garnissage.*`)

Cuir par defaut `cuir_sellier_fin_noir` (veau tannage vegetal, ame
synthetique, doublure) ; point sellier double main au pas de 3,2 mm (8
points/pouce), fil de lin cire 0,55 mm, filet d'embellissement a 3 mm du bord,
tranches teintees et lustrees, rembourrage fin 3 mm. Coussin d'appui avant
(`coussin_avant`, 15 mm) matelasse `losange` (pas 50) ou `capitonne` (boutons
recouverts de 12 mm aux noeuds) ou `aucun`. Le catalogue garnissage porte les
regles sellerie de chaque cuir (ex. harnais : pas 4 mm, pas de rembourrage ;
PU : piqure machine).
