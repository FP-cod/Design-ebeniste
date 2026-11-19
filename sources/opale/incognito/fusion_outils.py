# -*- coding: utf-8 -*-
"""Outils d'interface avec Fusion 360, sans dépendance à ``adsk``.

L'API Fusion travaille en centimètres. Toutes les grandeurs internes
d'Incognito sont en millimètres. La conversion mm ↔ cm est centralisée
ici, et uniquement ici (même convention que la gamme Equinox).
"""

from __future__ import annotations

from incognito.parametres import (
    ParametresGlobaux,
    TYPOLOGIES,
    vers_parametres_fusion as _vers_parametres_fusion,
)


def mm_vers_cm(longueur_mm: float) -> float:
    """Convertit une longueur de millimètres vers les centimètres internes Fusion."""
    return longueur_mm / 10.0


def cm_vers_mm(longueur_cm: float) -> float:
    """Convertit une longueur des centimètres internes Fusion vers les millimètres."""
    return longueur_cm * 10.0


def vers_parametres_fusion(parametres: ParametresGlobaux | None = None):
    """Raccourci vers ``incognito.parametres.vers_parametres_fusion``."""
    return _vers_parametres_fusion(parametres=parametres, typologies=TYPOLOGIES)
