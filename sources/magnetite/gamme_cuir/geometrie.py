# -*- coding: utf-8 -*-
"""Geometrie pure (sans Fusion) : contours plans, primitives et plan de construction.

Tout est en mm, dans le plan XY (le cuir est modelise A PLAT : patron de
coupe), epaisseurs selon +Z. ``fusion_outils`` traduit ces primitives en
esquisses / extrusions Fusion (et convertit en cm).

Contour = liste de segments :

- ``("ligne", (x1, y1), (x2, y2))``
- ``("arc", (xc, yc), rayon, angle_debut_deg, angle_fin_deg)`` parcouru dans
  le sens trigonometrique de debut a fin (fin > debut) ;
- ``("cercle", (xc, yc), rayon)`` (contour ferme a lui seul).
"""

import math


# ---------------------------------------------------------------------------
# Contours
# ---------------------------------------------------------------------------
def rect_arrondi(xmin, xmax, ymin, ymax, r_gauche, r_droite=None):
    """Rectangle a coins arrondis : rayon r_gauche aux deux coins x=xmin, r_droite a x=xmax.

    Un rayon egal a la demi-hauteur donne un bout demi-rond (pas de segment
    vertical de longueur nulle).
    """
    r_droite = r_gauche if r_droite is None else r_droite
    h = ymax - ymin
    if xmax <= xmin or h <= 0:
        raise ValueError("rectangle degenere")
    for r in (r_gauche, r_droite):
        if r < 0 or r > h / 2.0 + 1e-9:
            raise ValueError("rayon %g hors [0, %g]" % (r, h / 2.0))
    if r_gauche + r_droite > xmax - xmin + 1e-9:
        raise ValueError("rayons trop grands pour la longueur")
    rg, rd = r_gauche, r_droite
    seg = []
    # bas, de gauche a droite
    if xmax - rd > xmin + rg + 1e-9:
        seg.append(("ligne", (xmin + rg, ymin), (xmax - rd, ymin)))
    if rd > 0:
        seg.append(("arc", (xmax - rd, ymin + rd), rd, -90.0, 0.0))
    if (ymax - rd) - (ymin + rd) > 1e-9:
        seg.append(("ligne", (xmax, ymin + rd), (xmax, ymax - rd)))
    if rd > 0:
        seg.append(("arc", (xmax - rd, ymax - rd), rd, 0.0, 90.0))
    if xmax - rd > xmin + rg + 1e-9:
        seg.append(("ligne", (xmax - rd, ymax), (xmin + rg, ymax)))
    if rg > 0:
        seg.append(("arc", (xmin + rg, ymax - rg), rg, 90.0, 180.0))
    if (ymax - rg) - (ymin + rg) > 1e-9:
        seg.append(("ligne", (xmin, ymax - rg), (xmin, ymin + rg)))
    if rg > 0:
        seg.append(("arc", (xmin + rg, ymin + rg), rg, 180.0, 270.0))
    return seg


def contour_bande(x0, x1, largeur, rayon_g, rayon_d=None, y_centre=0.0):
    """Bande de cuir le long de X, centree sur y_centre, extremites arrondies."""
    return rect_arrondi(x0, x1, y_centre - largeur / 2.0, y_centre + largeur / 2.0, rayon_g, rayon_d)


def cercle(centre, diametre):
    return [("cercle", tuple(centre), diametre / 2.0)]


def contour_d(x_barre, passage, fil):
    """Anneau D a plat : barre droite centree en x_barre (selon Y), arrondi vers +X.

    Renvoie (contour_exterieur, contour_interieur). passage = largeur interieure.
    """
    ri = passage / 2.0
    ro = ri + fil
    xc = x_barre + fil / 2.0          # bord interieur de la barre = centre des arcs
    xe = x_barre - fil / 2.0          # bord exterieur de la barre
    ext = [("ligne", (xe, -ro), (xe, ro)), ("ligne", (xe, ro), (xc, ro)),
           ("arc", (xc, 0.0), ro, -90.0, 90.0), ("ligne", (xc, -ro), (xe, -ro))]
    # arc decrit de -90 a 90 : extremites (xc, -ro) -> (xc, ro) ; les lignes ferment le contour
    inte = [("ligne", (xc, ri), (xc, -ri)), ("arc", (xc, 0.0), ri, -90.0, 90.0)]
    return ext, inte


def contour_o(centre, diametre_interieur, fil):
    return cercle(centre, diametre_interieur + 2 * fil), cercle(centre, diametre_interieur)


def point_arc(centre, r, a_deg):
    a = math.radians(a_deg)
    return (centre[0] + r * math.cos(a), centre[1] + r * math.sin(a))


def extremites(segment):
    t = segment[0]
    if t == "ligne":
        return segment[1], segment[2]
    if t == "arc":
        _, c, r, a0, a1 = segment
        return point_arc(c, r, a0), point_arc(c, r, a1)
    p = (segment[1][0] + segment[2], segment[1][1])
    return p, p


def longueur_segment(s):
    if s[0] == "ligne":
        return math.hypot(s[2][0] - s[1][0], s[2][1] - s[1][1])
    if s[0] == "arc":
        return math.radians(s[4] - s[3]) * s[2]
    return 2 * math.pi * s[2]


def perimetre(contour):
    return sum(longueur_segment(s) for s in contour)


def boite_englobante(contour):
    pts = []
    for s in contour:
        if s[0] == "ligne":
            pts += [s[1], s[2]]
        else:
            c, r = s[1], s[2]
            pts += [(c[0] - r, c[1] - r), (c[0] + r, c[1] + r)] if s[0] == "cercle" else \
                [point_arc(c, r, a) for a in _angles_arc(s[3], s[4])]
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    return min(xs), max(xs), min(ys), max(ys)


def _angles_arc(a0, a1, n=24):
    return [a0 + (a1 - a0) * i / float(n) for i in range(n + 1)]


def echantillonner(contour, pas, depart=None):
    """Points regulierement espaces (pas en mm) le long d'un contour (couture)."""
    pas = float(pas)
    total = perimetre(contour)
    n = max(1, int(round(total / pas)))
    pas_reel = total / n
    pts, cible, cumul = [], (depart if depart is not None else pas_reel / 2.0), 0.0
    for s in contour:
        l = longueur_segment(s)
        while cible <= cumul + l + 1e-9 and len(pts) < n:
            t = (cible - cumul) / l if l else 0.0
            pts.append(_point_sur(s, t))
            cible += pas_reel
        cumul += l
    return pts, pas_reel


def _point_sur(s, t):
    if s[0] == "ligne":
        return (s[1][0] + t * (s[2][0] - s[1][0]), s[1][1] + t * (s[2][1] - s[1][1]))
    if s[0] == "arc":
        return point_arc(s[1], s[2], s[3] + t * (s[4] - s[3]))
    return point_arc(s[1], s[2], 360.0 * t)


def distance_point_segment(p, s):
    if s[0] == "ligne":
        (x1, y1), (x2, y2) = s[1], s[2]
        dx, dy = x2 - x1, y2 - y1
        l2 = dx * dx + dy * dy
        t = 0.0 if l2 == 0 else max(0.0, min(1.0, ((p[0] - x1) * dx + (p[1] - y1) * dy) / l2))
        return math.hypot(p[0] - (x1 + t * dx), p[1] - (y1 + t * dy))
    c, r = s[1], s[2]
    d = math.hypot(p[0] - c[0], p[1] - c[1])
    if s[0] == "cercle":
        return abs(d - r)
    a = math.degrees(math.atan2(p[1] - c[1], p[0] - c[0]))
    for k in (-360.0, 0.0, 360.0):
        if s[3] - 1e-9 <= a + k <= s[4] + 1e-9:
            return abs(d - r)
    return min(math.hypot(p[0] - q[0], p[1] - q[1]) for q in extremites(s))


def distance_point_contour(p, contour):
    return min(distance_point_segment(p, s) for s in contour)


def point_dans_rect_arrondi(p, xmin, xmax, ymin, ymax, r):
    """Test d'inclusion (rayon identique aux 4 coins)."""
    x, y = p
    if not (xmin <= x <= xmax and ymin <= y <= ymax):
        return False
    cx = min(max(x, xmin + r), xmax - r)
    cy = min(max(y, ymin + r), ymax - r)
    return math.hypot(x - cx, y - cy) <= r + 1e-9


# ---------------------------------------------------------------------------
# Primitives
# ---------------------------------------------------------------------------
class Plaque(object):
    """Piece plane extrudee : contour exterieur (+ contours interieurs = jours)."""

    def __init__(self, nom, contour, z, epaisseur, apparence, categorie="cuir", trous=()):
        self.nom, self.contour, self.z, self.epaisseur = nom, contour, float(z), float(epaisseur)
        self.apparence, self.categorie, self.trous = apparence, categorie, [list(t) for t in trous]

    type = "plaque"


class Percage(object):
    """Enlevement de matiere (trou, fente) de z a z + hauteur dans les corps du composant."""

    def __init__(self, nom, contour, z, hauteur):
        self.nom, self.contour, self.z, self.hauteur = nom, contour, float(z), float(hauteur)

    type = "percage"


class Cylindre(object):
    def __init__(self, nom, centre, diametre, z, hauteur, apparence, categorie="quincaillerie"):
        self.nom, self.centre, self.diametre = nom, tuple(centre), float(diametre)
        self.z, self.hauteur, self.apparence, self.categorie = float(z), float(hauteur), apparence, categorie

    type = "cylindre"


class CheminCouture(object):
    """Ligne de couture (esquisse seule) + points de griffe espaces du pas."""

    def __init__(self, nom, contour, z, pas, ferme=True):
        self.nom, self.contour, self.z, self.pas, self.ferme = nom, contour, float(z), float(pas), ferme
        self.points, self.pas_reel = echantillonner(contour, pas)
        self.longueur = perimetre(contour)

    type = "couture"


class Composant(object):
    def __init__(self, nom, primitives=None):
        self.nom, self.primitives = nom, list(primitives or [])


class Plan(object):
    """Resultat d'une grammaire : composants, cotes calculees, constats de regles, notes."""

    def __init__(self, nom, params):
        self.nom, self.params = nom, params
        self.composants, self.cotes, self.constats, self.notes = [], {}, [], []

    def composant(self, nom):
        for c in self.composants:
            if c.nom == nom:
                return c
        raise KeyError(nom)

    def primitives(self, type_=None):
        return [p for c in self.composants for p in c.primitives if type_ is None or p.type == type_]

    def echecs(self):
        return [c for c in self.constats if c.niveau == "ECHEC"]

    def alertes(self):
        return [c for c in self.constats if c.niveau == "ALERTE"]
