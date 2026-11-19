# -*- coding: utf-8 -*-
"""Outils d'interface avec Fusion 360, sans dépendance à ``adsk``.

L'API Fusion travaille en centimètres ; tout le package est en
millimètres. La conversion mm ↔ cm est centralisée ici, et uniquement
ici (même convention qu'Incognito et Equinox). Les angles sont convertis
en radians ici aussi.
"""

from __future__ import annotations

from math import radians


def mm_vers_cm(longueur_mm: float) -> float:
    """Longueur mm → cm (unité interne de l'API Fusion)."""
    return longueur_mm / 10.0


def cm_vers_mm(longueur_cm: float) -> float:
    """Longueur cm (API Fusion) → mm."""
    return longueur_cm * 10.0


def deg_vers_rad(angle_deg: float) -> float:
    """Angle en degrés → radians (unité des rotations de l'API Fusion)."""
    return radians(angle_deg)


def point_mm_vers_cm(point_mm: tuple[float, float, float]) -> tuple[float, float, float]:
    """Point (x, y, z) mm → cm."""
    return tuple(mm_vers_cm(c) for c in point_mm)  # type: ignore[return-value]
