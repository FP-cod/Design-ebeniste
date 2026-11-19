# -*- coding: utf-8 -*-
"""Couche 3 - Grammaires par typologie de meuble de rangement.

Chaque module expose :

- ``concevoir(params=None, overrides=None) -> Plan`` : logique pure, testable ;
- ``run(context)`` : point d'entree Fusion (construit le Plan dans le design).

Premiere grammaire livree : ``ratelier_mural`` (demonstration). Les autres
typologies (armoire_accessoires, coffre, support_exposition,
armoire_verrouillable) ont deja leurs parametres et verifications en
couches 1-2 ; leurs grammaires restent a ecrire.
"""

GRAMMAIRES = ("ratelier_mural",)
