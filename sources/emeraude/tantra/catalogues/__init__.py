# -*- coding: utf-8 -*-
"""Catalogues de la gamme Tantra (couche 2) : matériaux, fixations, mécanismes, coûts.

Chaque catalogue est un dictionnaire ``identifiant ASCII → dataclass figée``
avec une fonction ``*_par_nom`` qui lève ``KeyError`` en listant le catalogue.
Les règles de recalcul qui exploitent ces catalogues sont dans ``tantra.regles``.
"""

from tantra.catalogues.couts import CATALOGUE_COUTS, masses_volumiques
from tantra.catalogues.fixations import FIXATIONS, fixation_par_nom
from tantra.catalogues.mecanismes import VERROUS, AXES, verrou_par_nom, axe_par_nom
from tantra.catalogues.mousses import MOUSSES, mousse_par_nom

__all__ = [
    "CATALOGUE_COUTS", "masses_volumiques", "FIXATIONS", "fixation_par_nom",
    "VERROUS", "AXES", "verrou_par_nom", "axe_par_nom", "MOUSSES", "mousse_par_nom",
]
