# -*- coding: utf-8 -*-
"""Couche 2 - Catalogues de la gamme Rangement.

- ``bois`` : essences (reprises a l'identique des autres gammes) et finitions ;
- ``garnissage`` : cuirs et tissus (teintes reprises, ``TEINTES_CUIR``) ;
- ``quincaillerie`` : metaux, finitions metal, visserie, charnieres, verins ;
- ``systemes`` : tiroirs, portes, etageres, crochets, barres, serrures, ports ;
- ``jonctions`` : jonctions d'ebenisterie + fonctions de dimensionnement.

Chaque entree cite sa ``source`` (fichier d'une autre gamme) ou porte la
mention « À VALIDER ».
"""

from . import bois, garnissage, quincaillerie, systemes, jonctions  # noqa: F401

CATEGORIES = {
    "bois": ("bois.essence", bois.ESSENCES),
    "finition_bois": ("bois.finition", bois.FINITIONS_BOIS),
    "cuir": ("cuir.famille", garnissage.GARNISSAGES),
    "metal": ("quincaillerie.metal", quincaillerie.METAUX),
    "finition_metal": ("quincaillerie.finition_metal", quincaillerie.FINITIONS_METAL),
    "systeme": (None, systemes.SYSTEMES),
    "jonction": ("jonctions.type_caisson", jonctions.JONCTIONS),
}


def entree(categorie, cle):
    """Entree ``cle`` du catalogue ``categorie`` (KeyError explicite sinon)."""
    _, cat = CATEGORIES[categorie]
    if cle not in cat:
        raise KeyError("%s inconnu dans le catalogue %s (choix : %s)" % (cle, categorie, sorted(cat)))
    return cat[cle]
