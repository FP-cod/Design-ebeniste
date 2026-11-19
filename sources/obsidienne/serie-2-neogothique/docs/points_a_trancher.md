# Entrave cou-poignets : points a trancher (v0.2 « raffine »)

Les chiffres viennent de `neogothique/grammaires/entrave.py` (logique pure, 128 tests pytest). **Rien
n'a encore tourne dans Fusion 360** : la construction a ete testee contre un mock de l'API seulement.
Le detail avant -> apres est dans `docs/ajustements_v2.md`, le vocabulaire de style dans `docs/style.md`.

## A. Nouveaux choix esthetiques

| # | Point | Options | Recommandation |
|---|---|---|---|
| A1 | `style.proportions` | `nombre_or` (14,6 / 61,8 / 23,6 %), `harmonique` 1:5:2, `libre` | **nombre_or** : le chapiteau le plus elance, et c'est le mode qui laisse la fenetre de loquet la plus large |
| A2 | `entrave.pied.type_arret` | `droit` (biais 45 deg), `langue_de_boeuf` (cuilleron) | **langue_de_boeuf** a la main si l'ebeniste le maitrise (plus noble) ; sinon `droit` (defaut, faisable en machine) |
| A3 | `entrave.pied.section` | carre 100 (chanfreins arretes), octogonal 120 sur plats | **carre 100 a chanfreins arretes** : plus fin qu'en v0.1 ; l'octogone fait doublon avec le chanfrein et reduit le coulisseau (46 mm a 100, 60 mm a 120) |
| A4 | `style.motif_ajours` | ogive, trilobe, quadrilobe | **ogive equilaterale**, 5 baies : la lecture gothique la plus claire et la plus simple a decouper ; quadrilobe pour la plaque de cremaillere |
| A5 | `entrave.ceinture.active` | ceintures ajourees ou pas | **oui** : c'est elle qui transforme la table en meuble ; +0,7 kg |
| A6 | `ferrures.terminaison_pentures` | fleur de lys, queue d'aronde, trilobe, droite | **fleur de lys** pour la platine (piece d'apparat) ; queue d'aronde si on veut plus sobre / moins cher |
| A7 | `cremaillere.habillage` | capot ajoure (lancette), plaque decoupee (quadrilobes), aucun | **capot ajoure** : cache le mecanisme de calage, garde la lecture du cran par la fenetre |
| A8 | `cremaillere.decor_barre` | lisse, festonnee (barre 30), ajouree (35 x 10) | **lisse** sous capot ; festonnee seulement si `habillage = aucun` |
| A9 | `sellerie.matelassage_platine` | aucun, losange, capitonne | **losange** (47 cellules, pas 50) : capitonne = boutons qui marquent la peau a l'appui |
| A10 | `ferrures.finition` | fer forge cire noir, bruni, laiton vieilli | **fer forge cire noir** pour la structure ; laiton vieilli en accent (tetes de rivets, bague) |
| A11 | Semelles 566 x 140 x 54 (racine 2, phi^2) | garder, ou revenir a 560 x 90 x 60 | **garder** : plus stables et elles portent la plinthe sans debord |
| A12 | Cremaillere dentee visible devant le pied (x 238 a 258) | laisser apparente, ou capot forge | **petit capot forge** en tole 2,5 mm a modeliser en v0.3 (pas encore fait) |

## B. Points mecaniques (mis a jour)

1. **Debattement** : dessus de platine de 300 a 450 mm (interpretation conservee). Recouvrement en haut
   67 mm pour un coulisseau de 61 mm (**1,10 x**, cible 1,5 x, alerte ; hauteur_mini requise 315 mm).
   L'option 325 -> 450 en 6 positions donne 1,92 x. **Recommandation : garder 300 -> 450 avec patins
   anti-jeu en laiton** dans les fourreaux (jeu 1,5 -> 0,3 mm).
2. **Fenetre du loquet etroite** : le loquet doit tomber dans le fut (bague dessous, astragale dessus) :
   z = 172,5 a ≈ 177 mm, retenu 175. Agrandir plinthe/chapiteau (mode libre) ou la course la ferme : la
   grammaire leve une erreur explicite. **Recommandation : accepter** (c'est verifie et teste) ; si besoin
   de souplesse, autoriser le loquet a traverser l'astragale (non fait).
3. **Stabilite** : Ms/Mr = 0,29 en Y et 0,38 en X (masse 43,3 kg, plus legere de 4 kg que la v0.1).
   **Ancrage au sol obligatoire** (313 N par anneau, capacite 2 000 N).
4. **Platine moulee** : flexion 2,2 MPa / 16,6 ; fleche 0,25 / 2,05 mm ; le bec-de-corbin coute 5,3 %
   de module de section. Platine 40 mm possible (3,4 MPa) mais avec un chant inferieur ramene a 25 mm.
   **Recommandation : 50 mm.**
5. **Ferrures affinees** : toutes ont une marge >= 1,5. La plus juste est l'**axe de pivot 18 mm
   (marge 1,59)** ; a 16 mm (v0.1) la marge tomberait a 1,13 (alerte). Chevilles de pied : 4 x 7 mm,
   marge 1,71. Paroi de fourreau 15 mm sur les plats, 17,2 mm dans l'arete chanfreinee (mini 12).
6. **Pivot de cou** : axe vertical a chape (defaut). **Securite** : ouverture rapide sans outil de la
   manille de cou (`securite.ouverture_rapide_cou = True`), cisaille a portee de main.
7. **Fer / laiton** : en laiton les regles regrossissent tout (pene 14, axe 20, barre 30 x 10...).
   **Recommandation : fer forge cire noir, laiton vieilli en accent.**
8. **Noyer** : hypothese D27 (f_m,k = 27 MPa) a confirmer.
9. **Simplifications** : dents et trous de crans du pignon non tailles ; adoucissement 1,5 mm des aretes
   non moulurees non modelise ; piqures et filets de sellerie non modelises (cellules du matelassage
   oui) ; terminaisons forgees a epaisseur constante (pas d'emboutissage ni de nervure).
