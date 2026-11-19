# -*- coding: utf-8 -*-
"""Gamme Equinox : mobilier d'ebenisterie organique pour salle de jeux dediee.

Architecture en trois couches :

1. ``equinox.parametres`` : vocabulaire partage de la gamme (dimensions, bois,
   garnissage, metaux, traverse/lest, ancrage, securite, jonctions).
2. ``equinox.catalogues`` : materiaux et systemes d'attache, avec regles
   declaratives ; ``equinox.regles`` applique ces regles et liste les
   ajustements geometriques.
3. ``equinox.grammaires`` : un script de grammaire par typologie de meuble.

Unites internes : mm, kg, degres, N, MPa. L'API Fusion travaille en cm :
la conversion est faite exclusivement dans ``equinox.fusion_outils``.
"""

__version__ = "0.1.0"
