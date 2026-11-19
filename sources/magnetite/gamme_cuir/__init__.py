# -*- coding: utf-8 -*-
"""GammeCuir - accessoires en cuir (menottes, bracelets, colliers, sangles, impact, harnais).

Architecture en trois couches (comme Equinox) :

1. ``parametres`` : parametres globaux documentes (JSON + chargeur avec validation) ;
2. ``catalogues`` : cuirs / teintes (mappes sur les meubles Equinox, Neogothique,
   Incognito ; Tantra a confirmer), finitions, fils, quincaillerie, fermetures,
   jonctions ; ``regles`` : compatibilite et securite ;
3. ``grammaires`` : une grammaire par typologie (premiere : ``menottes``).

Destine exclusivement a des adultes consentants. Aucun accessoire n'est concu
pour la suspension.
"""

__version__ = "0.1.0"
