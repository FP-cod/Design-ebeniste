# -*- coding: utf-8 -*-
"""Gamme Neogothique : mobilier d'ebenisterie massive, medievale et brutale.

Contraste assume avec la gamme Equinox (organique, aerienne) : essences
sombres (chene massif, noyer), cuir noir, ferrures apparentes en fer forge
mat ou laiton mat, sections carrees ou octogonales, angles francs, zero
courbe organique, jonctions d'ebenisterie (tenons-mortaises, tourillons,
chevilles, clefs), zero vis apparente.

Architecture en trois couches (meme decoupage qu'Equinox) :

1. ``neogothique.parametres`` : vocabulaire de la gamme (dimensions, bois,
   cuir, ferrures, cremailleres, jonctions, tolerances, charges).
2. ``neogothique.catalogues`` : materiaux et systemes d'attache avec champ
   ``regles`` declaratif ; ``neogothique.regles`` applique ces regles et
   liste les ajustements geometriques avec une explication lisible.
3. ``neogothique.grammaires`` : un script de grammaire par typologie
   (premier meuble : ``entrave`` - Entrave cou-poignets).

Unites internes : mm, kg, degres, N, MPa. L'API Fusion travaille en cm :
la conversion est faite exclusivement dans ``neogothique.fusion_outils``.
"""

__version__ = "0.1.0"
