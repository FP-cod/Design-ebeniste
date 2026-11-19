# -*- coding: utf-8 -*-
"""Catalogue des revêtements discrets de la gamme Incognito.

Tissus de façade (velours, lin, laine bouclée, tissu chiné) et cuirs
cognac / noir réservés à l'intérieur caché (banc déployé). Un cuir de
façade existe en dérogation documentée, non retenu par défaut
(règle « zéro cuir visible »).
"""

from __future__ import annotations

from incognito.parametres import (
    CUIR_COGNAC,
    CUIR_NOIR,
    CUIR_SOBRE_FACADE,
    LAINE_BOUCLEE,
    LIN,
    REVETEMENTS_BASE,
    TISSU_CHINE,
    VELOURS,
    Revetement,
)

REVETEMENTS: dict[str, Revetement] = dict(REVETEMENTS_BASE)

__all__ = [
    "Revetement",
    "REVETEMENTS",
    "VELOURS",
    "LIN",
    "LAINE_BOUCLEE",
    "TISSU_CHINE",
    "CUIR_COGNAC",
    "CUIR_NOIR",
    "CUIR_SOBRE_FACADE",
    "revetement_par_nom",
    "revetements_exterieurs_conformes",
    "revetements_interieurs",
]


def revetement_par_nom(nom: str) -> Revetement:
    """Retourne un revêtement par identifiant ASCII."""
    try:
        return REVETEMENTS[nom]
    except KeyError as exc:
        connues = ", ".join(sorted(REVETEMENTS))
        raise KeyError(f"Revêtement inconnu « {nom} ». Catalogue : {connues}.") from exc


def revetements_exterieurs_conformes() -> tuple[Revetement, ...]:
    """Tissus de façade conformes à la règle « zéro cuir visible »."""
    return tuple(
        r for r in REVETEMENTS.values()
        if r.usage == "exterieur_visible" and r.conforme_discretions_defaut()
    )


def revetements_interieurs() -> tuple[Revetement, ...]:
    """Cuirs (et éventuellement autres) destinés à l'intérieur caché."""
    return tuple(r for r in REVETEMENTS.values() if r.usage == "interieur_cache")
