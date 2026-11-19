# -*- coding: utf-8 -*-
"""Couche 2 - Catalogues de la gamme Neogothique.

``CATEGORIES`` relie un nom de categorie au dictionnaire du catalogue ;
``SELECTIONS`` relie chaque parametre de selection (chemin) a sa categorie,
ce qui permet a ``neogothique.regles.changer_materiau`` de savoir quelles
regles appliquer.
"""

from .bois import BOIS, FINITIONS_BOIS
from .garnissage import GARNISSAGE
from .ferrures import METAUX, FINITIONS, COMPOSANTS, PIVOTS, TERMINAISONS, HABILLAGES, DECORS_BARRE
from .attaches import ATTACHES, JONCTIONS_ADMISES  # noqa: F401 (reexport)

CATEGORIES = {
    "bois": BOIS,
    "garnissage": GARNISSAGE,
    "metal": METAUX,
    "finition": FINITIONS,
    "pivot": PIVOTS,
    "attache": ATTACHES,
    "terminaison": TERMINAISONS,
    "habillage": HABILLAGES,
    "decor_barre": DECORS_BARRE,
}

#: chemin de parametre de selection -> categorie de catalogue
SELECTIONS = {
    "bois.essence": "bois",
    "garnissage.cuir_manilles": "garnissage",
    "ferrures.metal": "metal",
    "ferrures.finition": "finition",
    "entrave.manilles.pivot_cou": "pivot",
    "entrave.manilles.pivot_poignets": "pivot",
    "jonctions.type_coulisseau_platine": "attache",
    "jonctions.type_fourreau_semelle": "attache",
    "jonctions.type_traverse_semelle": "attache",
    "jonctions.type_joues_fourreau": "attache",
    "ferrures.terminaison_pentures": "terminaison",
    "cremaillere.habillage": "habillage",
    "cremaillere.decor_barre": "decor_barre",
}


def entree(categorie, cle):
    """Renvoie l'entree ``cle`` de la categorie (KeyError explicite sinon)."""
    cat = CATEGORIES[categorie]
    if cle not in cat:
        raise KeyError("Entree %r absente du catalogue %r (choix : %s)" % (cle, categorie, sorted(cat)))
    return cat[cle]
