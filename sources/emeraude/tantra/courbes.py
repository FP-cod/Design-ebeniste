# -*- coding: utf-8 -*-
"""Courbes paramétriques des profils de soutien (Python pur).

Les surfaces de soutien du volet 1 sont des **profils latéraux** dans le
plan (y, z) — y vers l'arrière du meuble, z vers le haut — extrudés selon
x (largeur). Un profil est défini par des **points-clés** (position,
hauteur, angle de tangente) reliés par des cubiques d'Hermite : on règle
ainsi directement les grandeurs ergonomiques (hauteur d'un sommet, pente
d'une assise, angle d'un dossier) sans manipuler de pôles de Bézier.

Fonctions fournies : échantillonnage, interpolation z(y), pente, rayon
de courbure minimal (faisabilité du cintrage), décalage normal (couche
de mousse, sous-face de flasque), polygones et centroïdes.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import atan2, cos, degrees, hypot, inf, radians, sin

Point2 = tuple[float, float]


@dataclass(frozen=True)
class PointCle:
    """Point de passage d'un profil : (y, z) en mm, tangente en degrés.

    L'angle est mesuré depuis +y (vers l'arrière), positif vers le haut.
    """

    y: float
    z: float
    angle_deg: float = 0.0
    nom: str = ""


def _hermite(p0: Point2, p1: Point2, t0: Point2, t1: Point2, t: float) -> Point2:
    h00 = 2 * t**3 - 3 * t**2 + 1
    h10 = t**3 - 2 * t**2 + t
    h01 = -2 * t**3 + 3 * t**2
    h11 = t**3 - t**2
    return (
        h00 * p0[0] + h10 * t0[0] + h01 * p1[0] + h11 * t1[0],
        h00 * p0[1] + h10 * t0[1] + h01 * p1[1] + h11 * t1[1],
    )


def profil_hermite(points: tuple[PointCle, ...] | list[PointCle],
                   n_par_segment: int = 24, tension: float = 1.0) -> list[Point2]:
    """Échantillonne une courbe d'Hermite passant par ``points``.

    La norme de chaque tangente vaut ``tension × corde`` du segment, ce
    qui donne une courbe régulière sans boucle pour des points ordonnés.
    """
    if len(points) < 2:
        raise ValueError("Il faut au moins deux points-clés.")
    if n_par_segment < 2:
        raise ValueError("n_par_segment doit être ≥ 2.")
    sortie: list[Point2] = []
    for i in range(len(points) - 1):
        a, b = points[i], points[i + 1]
        corde = hypot(b.y - a.y, b.z - a.z)
        if corde == 0:
            raise ValueError(f"Points-clés confondus ({a.nom or i}, {b.nom or i + 1}).")
        ta = (tension * corde * cos(radians(a.angle_deg)), tension * corde * sin(radians(a.angle_deg)))
        tb = (tension * corde * cos(radians(b.angle_deg)), tension * corde * sin(radians(b.angle_deg)))
        debut = 0 if i == 0 else 1
        for k in range(debut, n_par_segment + 1):
            sortie.append(_hermite((a.y, a.z), (b.y, b.z), ta, tb, k / n_par_segment))
    return sortie


def arc(cy: float, cz: float, rayon: float, a0_deg: float, a1_deg: float, n: int = 16) -> list[Point2]:
    """Arc de cercle échantillonné de ``a0`` à ``a1`` (degrés, sens trigonométrique)."""
    if rayon <= 0 or n < 1:
        raise ValueError("Rayon > 0 et n ≥ 1 requis.")
    return [
        (cy + rayon * cos(radians(a0_deg + (a1_deg - a0_deg) * k / n)),
         cz + rayon * sin(radians(a0_deg + (a1_deg - a0_deg) * k / n)))
        for k in range(n + 1)
    ]


def longueur(points: list[Point2]) -> float:
    """Longueur développée d'une polyligne (mm)."""
    return sum(hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(points, points[1:]))


def est_monotone_y(points: list[Point2]) -> bool:
    return all(b[0] > a[0] for a, b in zip(points, points[1:]))


def z_a(points: list[Point2], y: float) -> float:
    """Hauteur du profil à l'abscisse ``y`` (interpolation linéaire)."""
    if not est_monotone_y(points):
        raise ValueError("z_a exige un profil strictement croissant en y.")
    if y <= points[0][0]:
        return points[0][1]
    if y >= points[-1][0]:
        return points[-1][1]
    for a, b in zip(points, points[1:]):
        if a[0] <= y <= b[0]:
            t = (y - a[0]) / (b[0] - a[0])
            return a[1] + t * (b[1] - a[1])
    raise AssertionError("inaccessible")


def angle_a(points: list[Point2], y: float) -> float:
    """Pente locale (degrés) du profil à l'abscisse ``y``."""
    if not est_monotone_y(points):
        raise ValueError("angle_a exige un profil strictement croissant en y.")
    for a, b in zip(points, points[1:]):
        if a[0] <= y <= b[0]:
            return degrees(atan2(b[1] - a[1], b[0] - a[0]))
    a, b = (points[0], points[1]) if y < points[0][0] else (points[-2], points[-1])
    return degrees(atan2(b[1] - a[1], b[0] - a[0]))


def extremum_local(points: list[Point2], y_min: float, y_max: float, maximum: bool = True) -> Point2:
    """Point le plus haut (ou le plus bas) du profil entre ``y_min`` et ``y_max``."""
    candidats = [p for p in points if y_min <= p[0] <= y_max]
    if not candidats:
        raise ValueError("Aucun point du profil dans l'intervalle demandé.")
    return max(candidats, key=lambda p: p[1]) if maximum else min(candidats, key=lambda p: p[1])


def rayon_cercle_3_points(a: Point2, b: Point2, c: Point2) -> float:
    """Rayon du cercle circonscrit (inf si points alignés)."""
    ab = hypot(b[0] - a[0], b[1] - a[1])
    bc = hypot(c[0] - b[0], c[1] - b[1])
    ca = hypot(a[0] - c[0], a[1] - c[1])
    aire2 = abs((b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0]))
    if aire2 < 1e-9:
        return inf
    return ab * bc * ca / (2.0 * aire2)


def rayon_courbure_min(points: list[Point2], pas: int = 2) -> float:
    """Rayon de courbure minimal (mm) estimé par cercles à 3 points espacés de ``pas``."""
    r = inf
    for i in range(pas, len(points) - pas):
        r = min(r, rayon_cercle_3_points(points[i - pas], points[i], points[i + pas]))
    return r


def _normale_gauche(a: Point2, b: Point2) -> Point2:
    dy, dz = b[0] - a[0], b[1] - a[1]
    n = hypot(dy, dz)
    if n == 0:
        return (0.0, 1.0)
    return (-dz / n, dy / n)


def decaler(points: list[Point2], distance: float) -> list[Point2]:
    """Décale la polyligne selon sa normale gauche (vers le haut si y croît).

    ``distance`` > 0 : vers le haut (couche de mousse) ; < 0 : vers le bas
    (sous-face d'une flasque d'épaisseur constante). Normales moyennées aux
    sommets ; suffisant pour des courbes régulières de rayon ≫ |distance|.
    """
    if len(points) < 2:
        raise ValueError("Il faut au moins deux points.")
    sortie: list[Point2] = []
    for i, p in enumerate(points):
        if i == 0:
            n = _normale_gauche(points[0], points[1])
        elif i == len(points) - 1:
            n = _normale_gauche(points[-2], points[-1])
        else:
            n1 = _normale_gauche(points[i - 1], p)
            n2 = _normale_gauche(p, points[i + 1])
            nx, nz = n1[0] + n2[0], n1[1] + n2[1]
            norme = hypot(nx, nz) or 1.0
            n = (nx / norme, nz / norme)
        sortie.append((p[0] + distance * n[0], p[1] + distance * n[1]))
    return sortie


def polygone_entre(haut: list[Point2], bas: list[Point2]) -> list[Point2]:
    """Polygone fermé : ``haut`` dans l'ordre, puis ``bas`` en sens inverse."""
    return list(haut) + list(reversed(bas))


def aire_polygone(points: list[Point2]) -> float:
    """Aire (mm², valeur absolue) par la formule du lacet."""
    s = 0.0
    for (y0, z0), (y1, z1) in zip(points, points[1:] + points[:1]):
        s += y0 * z1 - y1 * z0
    return abs(s) / 2.0


def centroide_polygone(points: list[Point2]) -> Point2:
    """Centroïde (y, z) d'un polygone simple."""
    a = 0.0
    cy = cz = 0.0
    for (y0, z0), (y1, z1) in zip(points, points[1:] + points[:1]):
        f = y0 * z1 - y1 * z0
        a += f
        cy += (y0 + y1) * f
        cz += (z0 + z1) * f
    if abs(a) < 1e-12:
        ys = [p[0] for p in points]
        zs = [p[1] for p in points]
        return (sum(ys) / len(ys), sum(zs) / len(zs))
    a *= 0.5
    return (cy / (6.0 * a), cz / (6.0 * a))


def rectangle(y: float, z: float, dy: float, dz: float) -> list[Point2]:
    """Rectangle [y, y+dy] × [z, z+dz] (sens trigonométrique)."""
    if dy <= 0 or dz <= 0:
        raise ValueError("Rectangle de dimensions nulles ou négatives.")
    return [(y, z), (y + dy, z), (y + dy, z + dz), (y, z + dz)]


def tourner(points: list[Point2], angle_deg: float, pivot: Point2) -> list[Point2]:
    """Rotation plane des points autour de ``pivot`` (sens trigonométrique y→z)."""
    a = radians(angle_deg)
    ca, sa = cos(a), sin(a)
    py, pz = pivot
    return [(py + (y - py) * ca - (z - pz) * sa, pz + (y - py) * sa + (z - pz) * ca) for y, z in points]
