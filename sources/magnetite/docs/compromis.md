# Compromis : confort / solidite / finition / cout

Redige a la main ; les valeurs citees sont les defauts de `parametres_gamme_cuir.defauts.json`. Les couts sont
des categories relatives (aucun prix). Les charges de quincaillerie sont des **estimations non sourcees** : un
choix ne devient « solide » qu'avec la charge de rupture marquee du fournisseur retenu.

Notation : ++ tres favorable, + favorable, 0 neutre, - defavorable, -- tres defavorable.

## 1. Epaisseur du cuir exterieur (classes 2-2,5 / 3-3,5 / 4-5 mm)

| Classe | Confort | Solidite | Finition | Cout | Commentaire |
|---|---|---|---|---|---|
| fine 2-2,5 | ++ souple d'emblee | - (bande 50 mm au trou : ~1,8-2,3 kN a 20 MPa, sous les 3 kN requis) | + tranche fine | ++ | bracelets de jeu leger, doublures, passants |
| **moyenne 3-3,5 (defaut 3,5)** | + se cintre sur un poignet S (rayon/epaisseur ~6,8) | + 3,2 kN au trou (tout juste au-dessus de 3 kN) | ++ tranche lissable, trous qui tiennent | + | meilleur equilibre pour menottes de contention |
| forte 4-5 | - raide, rodage long ; alerte `cintrage` sur petites tailles | ++ | + aspect « harnais » massif | - | sangles de contention, harnais ; a eviter sur poignet S |

Calcul : resistance = (largeur - trou) x epaisseur x 20 MPa (ordre de grandeur repris de Neogothique),
comparee a 500 N x 1,5 x 4 = 3 000 N (traction, coefficient dynamique et coefficient cuir Neogothique).

## 2. Rembourrage (0 / feutre / latex 4 mm / neoprene) et nombre de couches

| Choix | Confort | Solidite | Finition | Cout |
|---|---|---|---|---|
| 1 couche, sans doublure | -- (tranche et chair contre la peau) | + | - | ++ |
| 2 couches (exterieur + doublure agneau) | + | + (la doublure ne porte pas) | ++ | + |
| **3 couches, latex 4 mm (defaut)** | ++ repartit la pression, absorbe les a-coups | 0 (le rembourrage ne porte rien ; interrompu sous rivets et trous) | + bombe, couture plus delicate | - (temps + matiere) ; latex = allergene a signaler |
| 3 couches, feutre laine | + ferme, se forme au membre | 0 | + traditionnel | - |

Effet geometrique : chaque mm d'epaisseur ajoute ~3,1 mm (pi x e) a la longueur developpee. Le rembourrage
ajoute aussi de l'empilement aux rivets (choix de tige automatique dans les regles).

## 3. Couture sellier vs rivets

| Jonction | Confort | Solidite | Finition | Cout |
|---|---|---|---|---|
| Couture sellier seule | ++ aucun metal cote peau | + indecousable, mais limitee par le pont de cuir | ++ | -- (main d'oeuvre : ~231 points, ~3 m de fil par menotte) |
| Rivets seuls | - tete cote peau (double calotte lisse obligatoire) | - en cisaillement : 2 rivets ~1,4 kN *estime* < 3 kN | 0 | ++ |
| **Rivets + couture (defaut patte d'anneau)** | + | ++ redondance (essai de traction a faire) | ++ | - |
| Rivets (defaut rabat de boucle) | 0 (sous le rabat, hors zone de contact) | + effort repris par la boucle | + | ++ demontable pour changer la boucle |

## 4. Inox vs laiton

| Metal | Confort | Solidite | Finition / assortiment | Cout |
|---|---|---|---|---|
| Inox 316L brosse | ++ contact peau OK, se desinfecte | ++ (anneaux soudes) | accord **noir**, bleu nuit ; ancrages Equinox inox A4 | + |
| Inox 316L PVD noir | ++ | ++ (revetement rayable) | accord **Entrave** fer forge noir | - |
| **Laiton massif CW510L (defaut)** | + sans plomb (option contact Equinox) | - anneaux moules non soudes (~2,5 kN *estime*) | accord **cognac / tan / havane** | - |
| Laiton patine | - eviter le contact prolonge (Neogothique) | - | accord brun fonce / Entrave laiton | - |
| Acier nickele | -- allergie nickel, rouille | 0 | - | ++ (entree de gamme uniquement) |

Point dur : l'assortiment cognac + laiton et la solidite tirent en sens oppose. Options : anneau D laiton
massif certifie (charge fournisseur >= 3 kN), ou anneau inox PVD or (non catalogue), ou anneau inox brosse
assume en contraste.

## 5. Boucle a ardillon vs cadenas (et mousqueton, scratch)

| Fermeture | Confort | Solidite (contention) | Securite | Cout |
|---|---|---|---|---|
| **Boucle a ardillon (defaut)** | + reglable au trou (15 mm) | ++ | ++ s'ouvre en secondes sans outil | 0 |
| Boucle verrouillable + cadenas | + | ++ | - ouverture lente : deverrouillage rapide aval **obligatoire** (ECHEC sinon), cle + double a portee | - |
| Mousqueton entre deux anneaux | 0 pas de reglage | + | ++ | 0 |
| Scratch | + | -- s'ouvre sous traction | ECHEC en `contention`, ALERTE en `jeu_leger` | ++ |

## 6. Largeur de bande (poignet 50 / cheville 60 mm)

Plus large = pression mieux repartie et section resistante plus forte, mais moins de mobilite du poignet et
boucle plus grosse/couteuse. En dessous de 40 mm, alerte en usage `contention`.
