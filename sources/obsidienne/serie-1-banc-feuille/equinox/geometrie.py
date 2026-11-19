# -*- coding: utf-8 -*-
"""Geometrie pure (sans Fusion) : vecteurs, primitives, courbes Equinox.

Toutes les coordonnees sont en mm, repere du meuble :
X longitudinal (0 = bout arriere du plateau, cote bassin / genoux ;
X croissant vers l'avant, cote epaules / coudes), Y lateral, Z vertical
(0 = sol). Les primitives sont decrites ici puis construites dans Fusion
par ``equinox.fusion_outils`` (conversion en cm) ou tracees par
``equinox.apercu`` (matplotlib).
"""

import math

from .catalogues.bois import BOIS
from .catalogues.metaux import METAUX

#: Masses volumiques des materiaux hors catalogues [kg/m3].
DENSITES_DIVERSES = {
    "mousse_hr": 50.0,
    "contreplaque_bouleau": 680.0,
    "bronze": 8800.0,
    "cuir": 900.0,
}


def densite(materiau):
    """Masse volumique [kg/m3] d'une cle materiau (bois, metal ou divers)."""
    for cat in (BOIS, METAUX):
        if materiau in cat:
            return cat[materiau]["densite"]
    if materiau in DENSITES_DIVERSES:
        return DENSITES_DIVERSES[materiau]
    raise KeyError("Materiau sans densite : %s" % materiau)


# ---------------------------------------------------------------------------
# Vecteurs (tuples de 3 floats)
# ---------------------------------------------------------------------------
def add(a, b):
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def sub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def mul(a, k):
    return (a[0] * k, a[1] * k, a[2] * k)


def dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def norme(a):
    return math.sqrt(dot(a, a))


def unitaire(a):
    n = norme(a)
    return mul(a, 1.0 / n)


def lerp(a, b, t):
    return add(a, mul(sub(b, a), t))


def rotation_y(p, pivot, angle_deg):
    """Rotation de ``p`` autour de l'axe parallele a Y passant par ``pivot``.

    Angle positif : sens trigonometrique vu depuis +Y (X vers -Z), meme
    convention que Matrix3D.setToRotation(angle, (0,1,0), pivot) dans Fusion.
    """
    a = math.radians(angle_deg)
    x, z = p[0] - pivot[0], p[2] - pivot[2]
    return (pivot[0] + x * math.cos(a) + z * math.sin(a), p[1], pivot[2] - x * math.sin(a) + z * math.cos(a))


def longueur_polyligne(points):
    return sum(norme(sub(points[i + 1], points[i])) for i in range(len(points) - 1))


def rayon_trois_points(a, b, c):
    """Rayon du cercle passant par trois points (inf si alignes)."""
    ab, bc, ca = norme(sub(b, a)), norme(sub(c, b)), norme(sub(a, c))
    aire2 = norme(cross(sub(b, a), sub(c, a)))
    if aire2 < 1e-9:
        return float("inf")
    return ab * bc * ca / (2.0 * aire2)


def rayon_courbure_min_polyligne(points):
    return min([rayon_trois_points(points[i - 1], points[i], points[i + 1]) for i in range(1, len(points) - 1)]
               or [float("inf")])


# ---------------------------------------------------------------------------
# Primitives
# ---------------------------------------------------------------------------
class Primitive(object):
    """Base : ``nom``, ``materiau`` (cle catalogue), ``categorie``."""
    categorie = "bois"

    def volume_mm3(self):
        raise NotImplementedError

    def centroide(self):
        raise NotImplementedError

    def masse_kg(self, densite_forcee=None):
        rho = densite_forcee if densite_forcee is not None else densite(self.materiau)
        return self.volume_mm3() * 1e-9 * rho


class Fuseau(Primitive):
    """Tronc de cone de ``p0`` (diametre ``d0``) a ``p1`` (diametre ``d1``)."""

    def __init__(self, nom, p0, p1, d0, d1, materiau, categorie="bois"):
        self.nom, self.p0, self.p1, self.d0, self.d1 = nom, tuple(p0), tuple(p1), float(d0), float(d1)
        self.materiau, self.categorie = materiau, categorie

    def longueur(self):
        return norme(sub(self.p1, self.p0))

    def volume_mm3(self):
        r0, r1 = self.d0 / 2.0, self.d1 / 2.0
        return math.pi * self.longueur() / 3.0 * (r0 * r0 + r0 * r1 + r1 * r1)

    def centroide(self):
        r0, r1 = self.d0 / 2.0, self.d1 / 2.0
        t = (r0 * r0 + 2 * r0 * r1 + 3 * r1 * r1) / (4.0 * (r0 * r0 + r0 * r1 + r1 * r1))
        return lerp(self.p0, self.p1, t)

    def diametre_a(self, t):
        return self.d0 + (self.d1 - self.d0) * t


class TubeSpline(Primitive):
    """Section circulaire (pleine ou tube) balayee le long d'une spline 3D."""

    def __init__(self, nom, points, diametre, materiau, paroi=None, ferme=False, categorie="inox"):
        self.nom, self.points, self.diametre = nom, [tuple(p) for p in points], float(diametre)
        self.materiau, self.paroi, self.ferme, self.categorie = materiau, paroi, ferme, categorie

    def longueur(self):
        pts = self.points + ([self.points[0]] if self.ferme else [])
        return longueur_polyligne(pts)

    def aire_section(self):
        r = self.diametre / 2.0
        if self.paroi:
            ri = r - self.paroi
            return math.pi * (r * r - ri * ri)
        return math.pi * r * r

    def volume_mm3(self):
        return self.aire_section() * self.longueur()

    def centroide(self):
        pts = self.points
        poids = [norme(sub(pts[i + 1], pts[i])) for i in range(len(pts) - 1)]
        tot = sum(poids) or 1.0
        c = (0.0, 0.0, 0.0)
        for i, w in enumerate(poids):
            c = add(c, mul(lerp(pts[i], pts[i + 1], 0.5), w / tot))
        return c


class Boite(Primitive):
    """Parallelepipede centre en ``centre``, cotes dx, dy, dz, tourne de
    ``angle_y`` degres autour d'un axe // Y passant par ``pivot`` (defaut :
    le centre)."""

    def __init__(self, nom, centre, dx, dy, dz, materiau, angle_y=0.0, pivot=None, categorie="bois",
                 rayon_bord=0.0):
        self.nom, self.centre, self.dx, self.dy, self.dz = nom, tuple(centre), float(dx), float(dy), float(dz)
        self.materiau, self.angle_y, self.categorie = materiau, float(angle_y), categorie
        self.pivot = tuple(pivot) if pivot else self.centre
        self.rayon_bord = rayon_bord

    def volume_mm3(self):
        return self.dx * self.dy * self.dz

    def centroide(self):
        return rotation_y(self.centre, self.pivot, self.angle_y)

    def sommets(self):
        cx, cy, cz = self.centre
        res = []
        for sx in (-1, 1):
            for sy in (-1, 1):
                for sz in (-1, 1):
                    p = (cx + sx * self.dx / 2, cy + sy * self.dy / 2, cz + sz * self.dz / 2)
                    res.append(rotation_y(p, self.pivot, self.angle_y))
        return res


class PlaqueContour(Primitive):
    """Plaque d'epaisseur ``epaisseur`` dont le contour (points XY) est
    extrude depuis ``z_bas``, puis tournee de ``angle_y`` autour de ``pivot``."""

    def __init__(self, nom, contour, z_bas, epaisseur, materiau, angle_y=0.0, pivot=(0, 0, 0),
                 categorie="garnissage"):
        self.nom, self.contour, self.z_bas, self.epaisseur = nom, [tuple(p[:2]) for p in contour], z_bas, epaisseur
        self.materiau, self.angle_y, self.pivot, self.categorie = materiau, angle_y, tuple(pivot), categorie

    def aire(self):
        pts = self.contour
        s = 0.0
        for i in range(len(pts)):
            x0, y0 = pts[i]
            x1, y1 = pts[(i + 1) % len(pts)]
            s += x0 * y1 - x1 * y0
        return abs(s) / 2.0

    def volume_mm3(self):
        return self.aire() * self.epaisseur

    def centroide(self):
        n = len(self.contour)
        cx = sum(p[0] for p in self.contour) / n
        cy = sum(p[1] for p in self.contour) / n
        return rotation_y((cx, cy, self.z_bas + self.epaisseur / 2.0), self.pivot, self.angle_y)

    def points_3d(self, haut=False):
        z = self.z_bas + (self.epaisseur if haut else 0.0)
        return [rotation_y((x, y, z), self.pivot, self.angle_y) for x, y in self.contour]


class Disque(Primitive):
    """Cylindre d'axe Z : ``centre`` = centre de la face basse."""

    def __init__(self, nom, centre, diametre, epaisseur, materiau, categorie="laiton"):
        self.nom, self.centre, self.diametre, self.epaisseur = nom, tuple(centre), float(diametre), float(epaisseur)
        self.materiau, self.categorie = materiau, categorie

    def volume_mm3(self):
        return math.pi * (self.diametre / 2.0) ** 2 * self.epaisseur

    def centroide(self):
        return add(self.centre, (0.0, 0.0, self.epaisseur / 2.0))


class TubeCarre(Primitive):
    """Tube carre ``cote`` x ``cote`` paroi ``paroi`` de p0 a p1 (axe quelconque)."""

    def __init__(self, nom, p0, p1, cote, paroi, materiau, categorie="inox"):
        self.nom, self.p0, self.p1, self.cote, self.paroi = nom, tuple(p0), tuple(p1), float(cote), float(paroi)
        self.materiau, self.categorie = materiau, categorie

    def longueur(self):
        return norme(sub(self.p1, self.p0))

    def volume_mm3(self):
        ci = self.cote - 2 * self.paroi
        return (self.cote ** 2 - ci ** 2) * self.longueur()

    def centroide(self):
        return lerp(self.p0, self.p1, 0.5)


# ---------------------------------------------------------------------------
# Composants, jonctions, plan
# ---------------------------------------------------------------------------
class Composant(object):
    """Composant Fusion : un nom et une liste de primitives."""

    def __init__(self, nom, primitives, role=""):
        self.nom, self.primitives, self.role = nom, list(primitives), role

    def masse_kg(self, densites=None):
        densites = densites or {}
        return sum(p.masse_kg(densites.get(p.materiau)) for p in self.primitives)


class Jonction(object):
    """Jonction nommee et calculee (tourillons, tenon-mortaise, taraudage...)."""

    def __init__(self, nom, type_, position, pieces, details):
        self.nom, self.type, self.position, self.pieces, self.details = nom, type_, tuple(position), pieces, details

    def __repr__(self):
        return "Jonction(%s, %s)" % (self.nom, self.type)


class Verification(object):
    """Resultat de verification : niveau 'ok' | 'alerte' | 'echec'."""

    def __init__(self, nom, niveau, valeur, limite, unite, detail):
        self.nom, self.niveau, self.valeur, self.limite, self.unite, self.detail = nom, niveau, valeur, limite, unite, detail

    def __repr__(self):
        return "[%s] %s : %s" % (self.niveau.upper(), self.nom, self.detail)

    __str__ = __repr__


class Plan(object):
    """Resultat d'une grammaire : tout ce qu'il faut pour construire et verifier."""

    def __init__(self, nom, params):
        self.nom, self.params = nom, params
        self.composants, self.jonctions, self.verifications = [], [], []
        self.ajustements, self.notes, self.charges = [], [], []
        self.points_appui = []    # (x, y) des contacts au sol
        self.repere = {}          # points nommes utiles (pivots, centres...)

    def ajouter(self, composant):
        self.composants.append(composant)
        return composant

    def composant(self, nom):
        for c in self.composants:
            if c.nom == nom:
                return c
        raise KeyError(nom)

    def densites(self):
        return {"mousse_hr": self.params.get("garnissage.densite_mousse")}

    def masse_structure(self):
        d = self.densites()
        return sum(c.masse_kg(d) for c in self.composants)

    def cg_structure(self):
        d = self.densites()
        m_tot, acc = 0.0, (0.0, 0.0, 0.0)
        for c in self.composants:
            for p in c.primitives:
                m = p.masse_kg(d.get(p.materiau))
                acc = add(acc, mul(p.centroide(), m))
                m_tot += m
        return mul(acc, 1.0 / m_tot), m_tot

    def echecs(self):
        return [v for v in self.verifications if v.niveau == "echec"]

    def alertes(self):
        return [v for v in self.verifications if v.niveau == "alerte"]


# ---------------------------------------------------------------------------
# Courbes Equinox
# ---------------------------------------------------------------------------
def helice_elliptique(centre_depart, centre_arrivee, rayon_depart, a_fin, b_fin, nombre_tours,
                      angle_depart_deg=0.0, n_points=97, fraction_plate=0.5,
                      exposant_rayon=0.6, exposant_centre=1.4, sens=1):
    """Trajectoire de l'helice Equinox (vrille de vigne).

    La spire s'enroule autour d'un axe vertical qui glisse de
    ``centre_depart`` (axe du pied, hauteur du pivot) a ``centre_arrivee``
    (centre de l'ellipse d'appui genou). Le rayon croit de ``rayon_depart``
    (collier autour du pied) jusqu'a l'ellipse finale (demi-axes ``a_fin``
    selon X, ``b_fin`` selon Y). La montee en Z est terminee a
    ``1 - fraction_plate / nombre_tours`` : la derniere demi-spire est
    horizontale et forme le cadre de l'appui genou.

    Le rayon croit plus vite (``exposant_rayon`` < 1) que l'axe ne se deplace
    (``exposant_centre`` > 1) : le pied reste a l'interieur des spires (pas
    d'interference). ``sens`` = +1 / -1 : sens d'enroulement (miroir G/D).

    :returns: liste de points (mm), du pivot vers l'appui genou.
    """
    pts = []
    t_montee = max(1e-6, 1.0 - fraction_plate / float(nombre_tours))
    for i in range(n_points):
        t = i / float(n_points - 1)
        theta = math.radians(angle_depart_deg) + sens * 2 * math.pi * nombre_tours * t
        sr = t ** exposant_rayon
        s = t ** exposant_centre
        a = rayon_depart + (a_fin - rayon_depart) * sr
        b = rayon_depart + (b_fin - rayon_depart) * sr
        u = min(1.0, t / t_montee)
        u = u * u * (3 - 2 * u)  # lissage
        cx = centre_depart[0] + (centre_arrivee[0] - centre_depart[0]) * s
        cy = centre_depart[1] + (centre_arrivee[1] - centre_depart[1]) * s
        cz = centre_depart[2] + (centre_arrivee[2] - centre_depart[2]) * u
        pts.append((cx + a * math.cos(theta), cy + b * math.sin(theta), cz))
    return pts


def contour_superellipse(longueur, largeur, exposant=4.0, n=64, x0=0.0, y0=0.0):
    """Contour 'feuille' arrondi : |2x/L-1|^n + |2y/W|^n = 1 (points XY)."""
    pts = []
    for i in range(n):
        t = 2 * math.pi * i / n
        c, s = math.cos(t), math.sin(t)
        x = (longueur / 2.0) * math.copysign(abs(c) ** (2.0 / exposant), c)
        y = (largeur / 2.0) * math.copysign(abs(s) ** (2.0 / exposant), s)
        pts.append((x0 + longueur / 2.0 + x, y0 + y))
    return pts


def branche(p0, p1, fleche, direction_fleche, n=5):
    """Points d'une branche cintree (arc de cercle approche) de p0 a p1,
    avec une fleche ``fleche`` [mm] dans ``direction_fleche``."""
    d = unitaire(direction_fleche)
    pts = []
    for i in range(n):
        t = i / float(n - 1)
        pts.append(add(lerp(p0, p1, t), mul(d, 4 * fleche * t * (1 - t))))
    return pts


def fuseaux_le_long(nom, points, d0, d1, materiau):
    """Decoupe une polyligne en fuseaux successifs a diametre decroissant."""
    l_tot = longueur_polyligne(points)
    res, acc = [], 0.0
    for i in range(len(points) - 1):
        l = norme(sub(points[i + 1], points[i]))
        da = d0 + (d1 - d0) * acc / l_tot
        db = d0 + (d1 - d0) * (acc + l) / l_tot
        res.append(Fuseau("%s_%d" % (nom, i + 1), points[i], points[i + 1], da, db, materiau))
        acc += l
    return res


def distance_point_segment(p, a, b):
    ab = sub(b, a)
    t = max(0.0, min(1.0, dot(sub(p, a), ab) / dot(ab, ab)))
    return norme(sub(p, lerp(a, b, t))), t
