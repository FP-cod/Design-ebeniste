# -*- coding: utf-8 -*-
"""Couche 2 - Catalogues de materiaux et systemes d'attache.

Chaque entree est un dictionnaire de proprietes physiques + un champ
``regles`` : liste declarative de regles appliquees par ``equinox.regles``
quand ce materiau devient le materiau actif. Format d'une regle ::

    {"cible": "bois.section_noeud",     # chemin de parametre a recalculer
     "calcul": "section_equivalente",   # nom d'un calcul du moteur
     "args": {...},                     # arguments du calcul (optionnel)
     "raison": "texte lisible"}

Calculs disponibles : voir ``equinox.regles.CALCULS``.
"""

from . import bois, garnissage, metaux, attaches  # noqa: F401

CATEGORIES = {
    "bois": ("bois.essence", bois.BOIS),
    "garnissage": ("garnissage.materiau", garnissage.GARNISSAGES),
    "inox": ("inox.nuance", metaux.METAUX),
    "laiton": ("laiton.nuance", metaux.METAUX),
    "lest": ("traverse.materiau_lest", metaux.METAUX),
}


def entree(categorie, cle):
    """Renvoie l'entree ``cle`` du catalogue ``categorie`` (KeyError sinon)."""
    _, cat = CATEGORIES[categorie]
    if cle not in cat:
        raise KeyError("%s inconnu dans le catalogue %s (choix : %s)" % (cle, categorie, sorted(cat)))
    return cat[cle]
