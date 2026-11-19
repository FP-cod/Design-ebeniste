# -*- coding: utf-8 -*-
"""Couche 3 - Grammaires par typologie de meuble.

Chaque module expose :

- ``concevoir(params=None, **overrides) -> Plan`` : logique pure, testable ;
- ``run(context)`` : point d'entree Fusion (construit le Plan dans le design).

``ancrages`` est un module transversal reutilise par toutes les typologies.
"""

TYPOLOGIES = ("banc_flore", "croix_saint_andre", "tabouret", "chaise_trone")
