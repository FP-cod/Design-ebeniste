# -*- coding: utf-8 -*-
"""Gamme Rangement : meubles de rangement et rateliers pour salle de jeux dediee.

Armoires a accessoires, rateliers muraux (menottes, sangles, instruments
d'impact), coffres, supports d'exposition, armoires verrouillables.

Architecture en trois couches, identique a Equinox / Neogothique / Incognito /
Aboutissants :

1. ``rangement.parametres`` : vocabulaire partage de la gamme (modules,
   panneaux, bois, cuir, quincaillerie, charges, discretion, ports, jonctions,
   systemes). Chaque valeur reprise d'une autre gamme cite son fichier source ;
   toute valeur proposee sans source est au statut ``a_valider``.
2. ``rangement.catalogues`` : materiaux (bois, cuir/garnissage, quincaillerie),
   systemes (tiroirs, portes, etageres, crochets, barres, serrures, ports) et
   jonctions d'ebenisterie avec leurs regles de dimensionnement ;
   ``rangement.regles`` verifie la coherence (charges, porte-a-faux, NPT...).
3. ``rangement.grammaires`` : une grammaire par typologie (premiere livree :
   ``ratelier_mural``).

Unites internes : mm, kg, degres, N, MPa. L'API Fusion travaille en cm : la
conversion est faite exclusivement dans ``rangement.fusion_outils``.
"""

__version__ = "0.1.0"
