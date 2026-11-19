# -*- coding: utf-8 -*-
"""Catalogue des essences classiques de la gamme Incognito.

La source de vérité des propriétés est le vocabulaire de
``incognito.parametres`` (couche 1). Ce module l'expose sous forme de
catalogue interrogeable, destiné aux règles de recalcul et aux grammaires.
"""

from __future__ import annotations

from incognito.parametres import (
    CHENE,
    ESSENCES_BASE,
    FRENE,
    HETRE,
    MERISIER,
    NOYER,
    Essence,
)

ESSENCES: dict[str, Essence] = dict(ESSENCES_BASE)

# Réexport des constantes pour un import direct depuis le catalogue.
__all__ = [
    "Essence",
    "ESSENCES",
    "CHENE",
    "NOYER",
    "HETRE",
    "FRENE",
    "MERISIER",
    "essence_par_nom",
    "noms_essences",
]


def essence_par_nom(nom: str) -> Essence:
    """Retourne une essence par identifiant ASCII (chene, noyer, hetre, frene, merisier)."""
    try:
        return ESSENCES[nom]
    except KeyError as exc:
        connues = ", ".join(noms_essences())
        raise KeyError(f"Essence inconnue « {nom} ». Catalogue : {connues}.") from exc


def noms_essences() -> tuple[str, ...]:
    return tuple(sorted(ESSENCES))
