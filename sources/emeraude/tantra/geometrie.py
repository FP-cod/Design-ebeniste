# -*- coding: utf-8 -*-
"""Vocabulaire géométrique commun aux grammaires (Python pur).

Convention de repère (identique pour toutes les typologies) :

* x : largeur du meuble (de gauche à droite vu de face), origine au bord gauche ;
* y : profondeur, origine à l'avant, croissant vers l'arrière ;
* z : hauteur, origine au sol.

Chaque pièce est un **polygone plan extrudé selon un axe** :

* ``axe = "x"`` (défaut) : polygone (y, z) extrudé sur ``[x, x + dx]`` —
  flasques, coques, traverses du volet 1 ;
* ``axe = "y"`` : polygone (x, z) extrudé sur ``[y, y + dy]`` — pièces qui
  pivotent autour d'un axe parallèle à y (plateau-cadre du volet 3) ;
* ``axe = "z"`` : polygone (x, y) extrudé sur ``[z, z + dz]``.

Les champs portent les noms ``x``/``dx`` pour l'axe d'extrusion quel qu'il
soit (``debut``/``epaisseur`` en sont des alias). Un prisme est un cas
particulier (rectangle), une flasque cintrée un polygone échantillonné.
Ce choix unique simplifie la génération Fusion (une esquisse sur un plan
parallèle au plan du profil, une extrusion symétrique) et les calculs de
masse et de centre de gravité.
Les états (MEUBLE/CADRE, SALON/RÉVÉLÉ) sont des géométries complètes
recalculées à partir des mêmes paramètres : on relance le script Fusion
après avoir changé le paramètre d'état.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from math import inf

from tantra.courbes import Point2, aire_polygone, centroide_polygone
from tantra.parametres import (
    G,
    NIVEAU_ESSAI_REQUIS,
    NIVEAU_NON_CONFORME,
    ORDRE_NIVEAUX,
)


AXES_EXTRUSION = ("x", "y", "z")


@dataclass(frozen=True)
class Piece:
    """Pièce : polygone plan extrudé selon ``axe`` de ``x`` à ``x + dx`` (mm).

    Pour ``axe="x"`` le profil est en (y, z) ; ``"y"`` : (x, z) ; ``"z"`` : (x, y).
    """

    nom: str
    role: str
    materiau: str
    x: float
    dx: float
    profil: tuple[Point2, ...]
    commentaire: str = ""
    surface_revetement_m2: float = 0.0
    """Surface de revêtement portée par la pièce (mousse habillée), pour le chiffrage."""
    axe: str = "x"

    def __post_init__(self) -> None:
        if self.axe not in AXES_EXTRUSION:
            raise ValueError(f"Pièce {self.nom} : axe d'extrusion inconnu « {self.axe} ».")
        if self.dx <= 0:
            raise ValueError(f"Pièce {self.nom} : dx doit être > 0 (reçu {self.dx}).")
        if len(self.profil) < 3:
            raise ValueError(f"Pièce {self.nom} : profil à au moins 3 sommets requis.")
        if aire_polygone(list(self.profil)) <= 0:
            raise ValueError(f"Pièce {self.nom} : profil d'aire nulle.")

    @property
    def aire_profil_mm2(self) -> float:
        return aire_polygone(list(self.profil))

    @property
    def volume_mm3(self) -> float:
        return self.aire_profil_mm2 * self.dx

    @property
    def volume_m3(self) -> float:
        return self.volume_mm3 * 1e-9

    @property
    def debut(self) -> float:
        return self.x

    @property
    def epaisseur(self) -> float:
        return self.dx

    def vers_3d(self, u: float, v: float, w: float) -> tuple[float, float, float]:
        """Point (u, v) du profil à la cote ``w`` de l'axe d'extrusion → (x, y, z) monde."""
        if self.axe == "x":
            return (w, u, v)
        if self.axe == "y":
            return (u, w, v)
        return (u, v, w)

    def sommets_3d(self, face: str = "debut") -> list[tuple[float, float, float]]:
        """Sommets du profil en coordonnées monde, sur la face ``debut`` ou ``fin``."""
        w = self.x if face == "debut" else self.x + self.dx
        return [self.vers_3d(u, v, w) for u, v in self.profil]

    @property
    def centroide(self) -> tuple[float, float, float]:
        cu, cv = centroide_polygone(list(self.profil))
        return self.vers_3d(cu, cv, self.x + self.dx / 2.0)

    @property
    def aabb(self) -> tuple[float, float, float, float, float, float]:
        """(xmin, xmax, ymin, ymax, zmin, zmax) en coordonnées monde."""
        pts = self.sommets_3d("debut") + self.sommets_3d("fin")
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        zs = [p[2] for p in pts]
        return (min(xs), max(xs), min(ys), max(ys), min(zs), max(zs))


def prisme(nom: str, role: str, materiau: str, x: float, y: float, z: float,
           dx: float, dy: float, dz: float, commentaire: str = "",
           surface_revetement_m2: float = 0.0) -> Piece:
    """Pièce prismatique [x, x+dx] × [y, y+dy] × [z, z+dz] (mm)."""
    if dy <= 0 or dz <= 0:
        raise ValueError(f"Prisme {nom} : dy et dz doivent être > 0.")
    profil = ((y, z), (y + dy, z), (y + dy, z + dz), (y, z + dz))
    return Piece(nom, role, materiau, x, dx, profil, commentaire, surface_revetement_m2)


def piece_profil(nom: str, role: str, materiau: str, x: float, dx: float,
                 profil: list[Point2], commentaire: str = "",
                 surface_revetement_m2: float = 0.0, axe: str = "x") -> Piece:
    """Pièce à profil quelconque extrudée selon ``axe`` sur [x, x + dx]."""
    return Piece(nom, role, materiau, x, dx, tuple(profil), commentaire, surface_revetement_m2, axe)


def prisme_y(nom: str, role: str, materiau: str, x: float, y: float, z: float,
             dx: float, dy: float, dz: float, commentaire: str = "",
             surface_revetement_m2: float = 0.0) -> Piece:
    """Prisme décrit dans le plan (x, z) et extrudé selon y (même boîte que ``prisme``)."""
    if dx <= 0 or dz <= 0:
        raise ValueError(f"Prisme {nom} : dx et dz doivent être > 0.")
    profil = ((x, z), (x + dx, z), (x + dx, z + dz), (x, z + dz))
    return Piece(nom, role, materiau, y, dy, profil, commentaire, surface_revetement_m2, "y")


def boite_contient(ext: tuple, int_: tuple, tol: float = 0.5) -> bool:
    """True si l'AABB ``int_`` est contenue dans l'AABB ``ext`` (tolérance mm)."""
    return (ext[0] - tol <= int_[0] and int_[1] <= ext[1] + tol and ext[2] - tol <= int_[2]
            and int_[3] <= ext[3] + tol and ext[4] - tol <= int_[4] and int_[5] <= ext[5] + tol)


def point_dans_aabb(p: tuple[float, float, float], b: tuple, tol: float = 0.5) -> bool:
    return (b[0] - tol <= p[0] <= b[1] + tol and b[2] - tol <= p[1] <= b[3] + tol
            and b[4] - tol <= p[2] <= b[5] + tol)


def empreinte_au_sol(pieces, tol_z: float = 1.0) -> tuple[float, float, float, float]:
    """Rectangle (xmin, xmax, ymin, ymax) englobant les pièces en contact avec le sol."""
    contacts = [p.aabb for p in pieces if p.aabb[4] <= tol_z]
    if not contacts:
        raise ValueError("Aucune pièce ne touche le sol.")
    return (min(b[0] for b in contacts), max(b[1] for b in contacts),
            min(b[2] for b in contacts), max(b[3] for b in contacts))


@dataclass(frozen=True)
class CasStabilite:
    """Cas de charge pour la stabilité au basculement.

    ``charges_verticales`` : liste de (F_N, x_mm, y_mm), forces descendantes.
    ``force_horizontale`` : (F_N, direction, z_mm) avec direction parmi
    ``"+x"``, ``"-x"``, ``"+y"``, ``"-y"`` (sens de la poussée).
    """

    nom: str
    charges_verticales: tuple[tuple[float, float, float], ...] = ()
    force_horizontale: tuple[float, str, float] | None = None
    coefficient_min: float = 1.5
    commentaire: str = ""


def coefficient_stabilite(cas: CasStabilite, masse_kg: float, cdg: tuple[float, float, float],
                          empreinte: tuple[float, float, float, float]) -> tuple[float, str]:
    """Coefficient au basculement minimal sur les 4 arêtes de l'empreinte.

    Pour chaque arête, moment stabilisant = poids propre × bras + charges
    verticales situées du côté intérieur ; moment renversant = charges
    verticales en porte-à-faux au-delà de l'arête + force horizontale ×
    hauteur (si elle pousse vers cette arête). Retourne (coefficient, arête).
    """
    xmin, xmax, ymin, ymax = empreinte
    aretes = {
        "-x": (lambda x, y: x - xmin), "+x": (lambda x, y: xmax - x),
        "-y": (lambda x, y: y - ymin), "+y": (lambda x, y: ymax - y),
    }
    meilleur = (inf, "")
    poids = masse_kg * G
    for nom, bras in aretes.items():
        stab = poids * bras(cdg[0], cdg[1])
        renv = 0.0
        for f, x, y in cas.charges_verticales:
            b = bras(x, y)
            if b >= 0:
                stab += f * b
            else:
                renv += f * (-b)
        if cas.force_horizontale is not None:
            fh, direction, z = cas.force_horizontale
            if direction == nom:
                renv += fh * z
        if stab <= 0:
            coef = 0.0
        elif renv <= 0:
            coef = inf
        else:
            coef = stab / renv
        if coef < meilleur[0]:
            meilleur = (coef, nom)
    return meilleur


@dataclass(frozen=True)
class Assemblage:
    """Liaison entre deux pièces (ébénisterie ou quincaillerie du catalogue)."""

    nom: str
    fixation: str
    piece_a: str
    piece_b: str
    quantite: int
    commentaire: str = ""

    def __post_init__(self) -> None:
        if self.quantite < 1:
            raise ValueError(f"Assemblage {self.nom} : quantité ≥ 1 requise.")


@dataclass(frozen=True)
class Ancrage:
    """Point d'ancrage pour bracelet ou sangle (insert inox noyé dans un bloc)."""

    nom: str
    position: tuple[float, float, float]
    piece_support: str
    visible: bool
    commentaire: str = ""


@dataclass(frozen=True)
class Verification:
    """Résultat d'une vérification simplifiée."""

    code: str
    ok: bool
    niveau: str
    message: str
    compromis: bool = False


def masse_et_cdg(pieces: tuple[Piece, ...] | list[Piece],
                 masses_volumiques: dict[str, float]) -> tuple[float, tuple[float, float, float]]:
    """Masse totale (kg) et centre de gravité (mm) d'un ensemble de pièces."""
    m_tot = 0.0
    sx = sy = sz = 0.0
    for p in pieces:
        try:
            rho = masses_volumiques[p.materiau]
        except KeyError as exc:
            raise KeyError(f"Masse volumique inconnue pour le matériau « {p.materiau} » ({p.nom}).") from exc
        m = p.volume_m3 * rho
        cx, cy, cz = p.centroide
        m_tot += m
        sx += m * cx
        sy += m * cy
        sz += m * cz
    if m_tot <= 0:
        return 0.0, (0.0, 0.0, 0.0)
    return m_tot, (sx / m_tot, sy / m_tot, sz / m_tot)


def coefficient_basculement(poids_n: float, bras_poids_mm: float,
                            moment_renversant_nmm: float,
                            moments_stabilisants_nmm: float = 0.0) -> float:
    """Coefficient au basculement = moments stabilisants / moment renversant.

    ``bras_poids_mm`` : distance horizontale entre le centre de gravité et
    l'arête de basculement (positive si le CDG est du côté stable).
    """
    stabilisant = poids_n * bras_poids_mm + moments_stabilisants_nmm
    if moment_renversant_nmm <= 0:
        return inf
    return stabilisant / moment_renversant_nmm


@dataclass(frozen=True)
class GeometrieMeuble:
    """Résultat d'une grammaire pour un état donné."""

    typologie: str
    etat: str
    pieces: tuple[Piece, ...]
    assemblages: tuple[Assemblage, ...]
    ancrages: tuple[Ancrage, ...]
    verifications: tuple[Verification, ...]
    derivees: dict = field(default_factory=dict)
    quincaillerie: tuple[tuple[str, int], ...] = ()
    """Liste (identifiant catalogue, quantité) hors assemblages, pour le chiffrage."""

    def piece(self, nom: str) -> Piece:
        for p in self.pieces:
            if p.nom == nom:
                return p
        raise KeyError(f"Pièce inconnue « {nom} » ({self.typologie}).")

    def pieces_role(self, role: str) -> tuple[Piece, ...]:
        return tuple(p for p in self.pieces if p.role == role)

    def verification(self, code: str) -> Verification:
        for v in self.verifications:
            if v.code == code:
                return v
        raise KeyError(f"Vérification inconnue « {code} » ({self.typologie}).")

    @property
    def conforme(self) -> bool:
        return all(v.niveau != NIVEAU_NON_CONFORME for v in self.verifications)

    @property
    def compromis(self) -> tuple[Verification, ...]:
        return tuple(v for v in self.verifications if v.compromis)

    @property
    def essais_requis(self) -> tuple[Verification, ...]:
        return tuple(v for v in self.verifications if v.niveau == NIVEAU_ESSAI_REQUIS)

    def plus_grave(self) -> str:
        return max((v.niveau for v in self.verifications), key=ORDRE_NIVEAUX.index, default="ok")

    @property
    def encombrement(self) -> tuple[float, float, float, float, float, float]:
        bs = [p.aabb for p in self.pieces]
        return (min(b[0] for b in bs), max(b[1] for b in bs), min(b[2] for b in bs),
                max(b[3] for b in bs), min(b[4] for b in bs), max(b[5] for b in bs))

    @property
    def dimensions_hors_tout(self) -> tuple[float, float, float]:
        e = self.encombrement
        return (e[1] - e[0], e[3] - e[2], e[5] - e[4])


def poids_n(masse_kg: float) -> float:
    return masse_kg * G
