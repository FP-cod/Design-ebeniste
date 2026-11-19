# -*- coding: utf-8 -*-
"""Outils geometriques et pont vers l'API Fusion 360.

Trois familles de corps (logique pure, testable sans Fusion) :

- ``Solide``      : profil plan (polygone, cercle ou *chemin* lignes + arcs,
  avec trous eventuels) extrude symetriquement le long de X, Y ou Z.
- ``BlocProfile`` : bloc moulure = intersection de « tranches » verticales,
  chacune definie par une trace de chant (d, z) dans une direction du plan
  horizontal (2 directions : rectangle/carre ; 4 : octogone ou carre a
  chanfreins arretes). Onglets exacts, moulures reelles (arcs). Alesage
  carre optionnel (fourreaux).
- ``Revolution``  : profil (r, z) revolu autour d'un axe vertical (tetes de
  rivets goutte de suif, boutons de capiton).

Construction Fusion (``adsk.core`` / ``adsk.fusion`` importes a l'appel) :
esquisses sur plans decales ou tournes, extrusions symetriques (nouveau
corps / intersection / enlevement), revolutions, deplacements.

CONVERSION D'UNITES : tout le paquet travaille en mm ; l'API Fusion attend
des cm pour ``Point3D`` et ``ValueInput.createByReal``. La conversion est
faite ICI ET SEULEMENT ICI (``mm_vers_cm``).
"""

import math

from . import profils as pf

try:  # Fusion 360 present ?
    import adsk.core  # noqa: F401
    FUSION_DISPONIBLE = True
except ImportError:  # hors Fusion (tests, apercu)
    FUSION_DISPONIBLE = False

MM_PAR_CM = 10.0


def mm_vers_cm(v):
    """Convertit une longueur interne (mm) vers l'unite interne Fusion (cm)."""
    return v / MM_PAR_CM


# ---------------------------------------------------------------------------
# Profils 2D
# ---------------------------------------------------------------------------
class Profil(object):
    """Profil plan ferme : ``poly`` (sommets), ``cercle`` (rayon) ou ``chemin`` (segments L/A)."""

    def __init__(self, type_, donnees):
        self.type, self.donnees = type_, donnees

    def points(self, n_cercle=16):
        if self.type == "cercle":
            r = self.donnees
            return [(r * math.cos(2 * math.pi * i / n_cercle), r * math.sin(2 * math.pi * i / n_cercle))
                    for i in range(n_cercle)]
        if self.type == "chemin":
            return pf.echantillonner(self.donnees, 8)[:-1]
        return list(self.donnees)

    def aire(self):
        if self.type == "cercle":
            return math.pi * self.donnees ** 2
        pts = self.points()
        s = 0.0
        for i in range(len(pts)):
            x1, y1 = pts[i]
            x2, y2 = pts[(i + 1) % len(pts)]
            s += x1 * y2 - x2 * y1
        return abs(s) / 2.0

    def etendue(self):
        pts = self.points()
        us, vs = [p[0] for p in pts], [p[1] for p in pts]
        return min(us), max(us), min(vs), max(vs)


def rectangle(du, dv, du0=0.0, dv0=0.0):
    a, b = du / 2.0, dv / 2.0
    return Profil("poly", [(du0 - a, dv0 - b), (du0 + a, dv0 - b), (du0 + a, dv0 + b), (du0 - a, dv0 + b)])


def octogone(sur_plats):
    r = sur_plats / 2.0 / math.cos(math.pi / 8.0)
    return Profil("poly", [(r * math.cos(math.pi / 8.0 + i * math.pi / 4.0),
                            r * math.sin(math.pi / 8.0 + i * math.pi / 4.0)) for i in range(8)])


def section_pied(section, cote):
    if section == "carre":
        return rectangle(cote, cote)
    if section == "octogonal":
        return octogone(cote)
    raise ValueError("section de pied inconnue : %r" % section)


def cercle(diametre):
    return Profil("cercle", diametre / 2.0)


def polygone(points):
    return Profil("poly", [tuple(p) for p in points])


def chemin(segments):
    if not pf.chemin_ferme(segments):
        raise ValueError("chemin non ferme")
    return Profil("chemin", list(segments))


AXES = {"x": ((0, 1, 0), (0, 0, 1)),   # axe X : u = Y, v = Z
        "y": ((1, 0, 0), (0, 0, 1)),   # axe Y : u = X, v = Z
        "z": ((1, 0, 0), (0, 1, 0))}   # axe Z : u = X, v = Y
INDICE_AXE = {"x": 0, "y": 1, "z": 2}


class _Corps(object):
    """Base commune : nom, piece (nomenclature), materiau, mobile."""
    genre = "?"

    def translate_z(self, dz):
        self.centre = (self.centre[0], self.centre[1], self.centre[2] + dz)
        return self


# ---------------------------------------------------------------------------
# Solide extrude
# ---------------------------------------------------------------------------
class Solide(_Corps):
    """Profil (ext - int - trous) extrude de ``longueur`` le long de ``axe``.

    :param nom: nom unique du corps (repris dans Fusion).
    :param piece: type de piece (nomenclature).
    :param axe: "x", "y" ou "z".
    :param centre: (x, y, z) mm.
    :param longueur: longueur d'extrusion (mm), symetrique autour du centre.
    :param ext: ``Profil`` exterieur (coordonnees locales u, v).
    :param int_: ``Profil`` interieur (trou central) ou None.
    :param trous: liste de ``Profil`` (ajours) ou None.
    :param materiau: "bois" | "metal" | "acier" | "cuir".
    :param mobile: True si le corps suit la platine.
    """
    genre = "solide"

    def __init__(self, nom, piece, axe, centre, longueur, ext, int_=None, materiau="bois", mobile=False, trous=None):
        if axe not in AXES:
            raise ValueError("axe invalide %r" % axe)
        if longueur <= 0:
            raise ValueError("longueur nulle ou negative pour %s" % nom)
        self.nom, self.piece, self.axe = nom, piece, axe
        self.centre = tuple(float(c) for c in centre)
        self.longueur = float(longueur)
        self.ext, self.int = ext, int_
        self.trous = list(trous or [])
        self.materiau, self.mobile = materiau, mobile

    def __repr__(self):
        return "<Solide %s %s L=%.1f>" % (self.nom, self.axe, self.longueur)

    def boucles_interieures(self):
        return ([self.int] if self.int else []) + self.trous

    def volume_mm3(self):
        return (self.ext.aire() - sum(p.aire() for p in self.boucles_interieures())) * self.longueur

    def point(self, u, v, w):
        eu, ev = AXES[self.axe]
        ia = INDICE_AXE[self.axe]
        p = [self.centre[0] + u * eu[0] + v * ev[0], self.centre[1] + u * eu[1] + v * ev[1],
             self.centre[2] + u * eu[2] + v * ev[2]]
        p[ia] += w
        return tuple(p)

    def boite_englobante(self):
        u0, u1, v0, v1 = self.ext.etendue()
        coins = [self.point(u, v, w) for u in (u0, u1) for v in (v0, v1)
                 for w in (-self.longueur / 2, self.longueur / 2)]
        return (tuple(min(c[i] for c in coins) for i in range(3)), tuple(max(c[i] for c in coins) for i in range(3)))

    def facettes(self):
        h = self.longueur / 2.0
        res = []
        for prof in [self.ext] + self.boucles_interieures():
            pts = prof.points()
            for i in range(len(pts)):
                (u1, v1), (u2, v2) = pts[i], pts[(i + 1) % len(pts)]
                res.append([self.point(u1, v1, -h), self.point(u2, v2, -h), self.point(u2, v2, h), self.point(u1, v1, h)])
        pts = self.ext.points()
        if self.int is None:
            res.append([self.point(u, v, -h) for u, v in pts])
            res.append([self.point(u, v, h) for u, v in pts])
        else:
            ip = self.int.points()
            if len(ip) == len(pts):
                for w in (-h, h):
                    for i in range(len(pts)):
                        j = (i + 1) % len(pts)
                        res.append([self.point(pts[i][0], pts[i][1], w), self.point(pts[j][0], pts[j][1], w),
                                    self.point(ip[j][0], ip[j][1], w), self.point(ip[i][0], ip[i][1], w)])
        return res

    def facettes_trous(self, decalage=0.3):
        """Contours des ajours sur les deux faces (l'apercu les peint en couleur de fond)."""
        h = self.longueur / 2.0 + decalage
        return [[self.point(u, v, w) for u, v in t.points()] for t in self.trous for w in (-h, h)]


# ---------------------------------------------------------------------------
# Bloc moulure (intersection de tranches)
# ---------------------------------------------------------------------------
def _clip(poly, nx, ny, c):
    """Garde la partie nx.x + ny.y <= c d'un polygone convexe."""
    res = []
    for i in range(len(poly)):
        p, q = poly[i], poly[(i + 1) % len(poly)]
        fp, fq = nx * p[0] + ny * p[1] - c, nx * q[0] + ny * q[1] - c
        if fp <= 1e-12:
            res.append(p)
        if fp * fq < -1e-18:
            t = fp / (fp - fq)
            res.append((p[0] + t * (q[0] - p[0]), p[1] + t * (q[1] - p[1])))
    return res


def _proj_segment(p, a, b):
    ax, ay = b[0] - a[0], b[1] - a[1]
    L2 = ax * ax + ay * ay
    t = 0.0 if L2 == 0 else max(0.0, min(1.0, ((p[0] - a[0]) * ax + (p[1] - a[1]) * ay) / L2))
    return (a[0] + t * ax, a[1] + t * ay)


class BlocProfile(_Corps):
    """Bloc a chants moulures : intersection de tranches |n_k . (p - c) - o_k| <= a_k - d_k(z).

    :param directions: liste de (angle_deg, a, trace[, decalage]) ; ``trace`` =
        segments (d, z) du haut vers le bas (voir ``profils``) ; ``decalage``
        (defaut 0) decentre la tranche le long de sa normale (cellules de
        matelassage rognees par le contour du coussin). Toutes les traces
        couvrent la meme hauteur [z_bas, z_haut].
    :param centre_xy: (x, y) du centre du bloc (mm).
    :param alesage: None ou (cote_x, cote_y, z_bas, z_haut) : alesage
        rectangulaire centre (fourreaux), enleve par extrusion-enlevement.
    :param enlevements: boites (x0, x1, y0, y1, z0, z1) en coordonnees LOCALES
        (lumieres de cremaillere...), enlevees par extrusion-enlevement.
    :param ajours: (indice_direction_epaisseur, [Profil...]) : ajours traversant
        l'epaisseur de la tranche indiquee ; profils dans le plan (t, z), t
        mesure le long de la direction (angle - 90 deg) depuis le centre.
    """
    genre = "bloc"

    def __init__(self, nom, piece, centre_xy, directions, alesage=None, materiau="bois", mobile=False,
                 enlevements=None, ajours=None):
        self.nom, self.piece = nom, piece
        self.directions = []
        for dr in directions:
            ang, a, t = dr[0], dr[1], dr[2]
            off = dr[3] if len(dr) > 3 else 0.0
            self.directions.append((float(ang), float(a), list(t), float(off)))
        self.materiau, self.mobile = materiau, mobile
        zh = [pf.echantillonner(d[2], 2)[0][1] for d in self.directions]
        zb = [pf.echantillonner(d[2], 2)[-1][1] for d in self.directions]
        if max(zh) - min(zh) > 1e-6 or max(zb) - min(zb) > 1e-6:
            raise ValueError("%s : traces de hauteurs differentes" % nom)
        self.z_haut, self.z_bas = zh[0], zb[0]
        self.centre = (float(centre_xy[0]), float(centre_xy[1]), (self.z_haut + self.z_bas) / 2.0)
        self.alesage = alesage
        self.enlevements = []
        if alesage:
            ax, ay, z0, z1 = alesage
            self.enlevements.append((-ax / 2.0, ax / 2.0, -ay / 2.0, ay / 2.0, z0, z1))
        self.enlevements += [tuple(float(v) for v in bx) for bx in (enlevements or [])]
        self.ajours = ajours

    def __repr__(self):
        return "<BlocProfile %s %d dir.>" % (self.nom, len(self.directions))

    @property
    def longueur(self):
        return self.z_haut - self.z_bas

    # -- sections -------------------------------------------------------------------
    def _demi(self, z, cote="dessus"):
        return [a - pf.evaluer(t, z, cote) for _, a, t, _ in self.directions]

    def niveaux(self):
        """Liste de (z, [s_k]) du haut vers le bas, paliers dedoubles."""
        zs = set()
        for d in self.directions:
            zs.update(round(z, 6) for z in pf.cotes_z(d[2]))
        res = []
        for z in sorted(zs, reverse=True):
            dessus, dessous = self._demi(z, "dessus"), self._demi(z, "dessous")
            res.append((z, dessus))
            if any(abs(p - q) > 1e-9 for p, q in zip(dessus, dessous)):
                res.append((z, dessous))
        return res

    def _demi_plans(self, s_list):
        """Demi-plans (angle, c) : n(angle) . p <= c, pour chaque tranche (deux par tranche)."""
        res = []
        for (ang, _, _, off), s in zip(self.directions, s_list):
            res.append((ang, off + s))
            res.append((ang + 180.0, s - off))
        return res

    def polygone(self, s_list):
        """Section horizontale (polygone convexe, coordonnees locales) pour des demi-largeurs donnees."""
        R = 1e5
        poly = [(-R, -R), (R, -R), (R, R), (-R, R)]
        for ang, c in self._demi_plans(s_list):
            poly = _clip(poly, math.cos(math.radians(ang)), math.sin(math.radians(ang)), c)
            if not poly:
                return []
        return poly

    def _sommets_fixes(self, s_list):
        """2N sommets a correspondance stable d'un niveau a l'autre (aretes degenerees permises)."""
        poly = self.polygone(s_list)
        if not poly:
            return []
        plans = sorted(self._demi_plans(s_list), key=lambda t: t[0] % 360.0)
        res = []
        for (a1, c1), (a2, c2) in zip(plans, plans[1:] + plans[:1]):
            n1 = (math.cos(math.radians(a1)), math.sin(math.radians(a1)))
            n2 = (math.cos(math.radians(a2)), math.sin(math.radians(a2)))
            det = n1[0] * n2[1] - n1[1] * n2[0]
            if abs(det) < 1e-12:
                continue
            p = ((c1 * n2[1] - c2 * n1[1]) / det, (n1[0] * c2 - n2[0] * c1) / det)
            best = min((_proj_segment(p, poly[i], poly[(i + 1) % len(poly)]) for i in range(len(poly))),
                       key=lambda q: (q[0] - p[0]) ** 2 + (q[1] - p[1]) ** 2)
            res.append(best)
        return res

    @staticmethod
    def _aire(poly):
        if len(poly) < 3:
            return 0.0
        return abs(sum(poly[i][0] * poly[(i + 1) % len(poly)][1] - poly[(i + 1) % len(poly)][0] * poly[i][1]
                       for i in range(len(poly)))) / 2.0

    def _aire_z(self, z, cote="dessus", boite=None):
        poly = self.polygone(self._demi(z, cote))
        if boite and poly:
            x0, x1, y0, y1 = boite[:4]
            for nx, ny, c in ((1, 0, x1), (-1, 0, -x0), (0, 1, y1), (0, -1, -y0)):
                poly = _clip(poly, nx, ny, c)
                if not poly:
                    break
        return self._aire(poly)

    def _integrer(self, boite=None):
        zs = sorted(set(z for z, _ in self.niveaux()))
        if boite:
            z0, z1 = max(boite[4], self.z_bas), min(boite[5], self.z_haut)
            if z1 <= z0:
                return 0.0
            zs = sorted(set([z for z in zs if z0 < z < z1] + [z0, z1]))
        v = 0.0
        for za, zb in zip(zs, zs[1:]):
            # trapezes entre niveaux (exact pour des traces rectilignes ; arcs echantillonnes)
            v += (self._aire_z(za, "dessus", boite) + self._aire_z(zb, "dessous", boite)) / 2.0 * (zb - za)
        return v

    def volume_mm3(self):
        v = self._integrer()
        for bx in self.enlevements:
            v -= self._integrer(bx)
        if self.ajours:
            k, profils_aj = self.ajours
            v -= sum(p.aire() for p in profils_aj) * 2.0 * self.directions[k][1]
        return v

    def section_a(self, z):
        """Polygone (coordonnees absolues) de la section a la cote z."""
        return [(x + self.centre[0], y + self.centre[1]) for x, y in self.polygone(self._demi(z))]

    def demi_largeur(self, z, k=0):
        """Demi-largeur de la tranche k a la cote z (mm)."""
        ang, a, t, _ = self.directions[k]
        return a - pf.evaluer(t, z)

    def boite_englobante(self):
        xs, ys = [], []
        for z, s in self.niveaux():
            for x, y in self.polygone(s):
                xs.append(x)
                ys.append(y)
        cx, cy = self.centre[0], self.centre[1]
        return ((min(xs) + cx, min(ys) + cy, self.z_bas), (max(xs) + cx, max(ys) + cy, self.z_haut))

    def facettes(self):
        cx, cy = self.centre[0], self.centre[1]
        nv = [(z, self._sommets_fixes(s)) for z, s in self.niveaux()]
        nv = [(z, p) for z, p in nv if p]
        res = []
        for (z0, p0), (z1, p1) in zip(nv, nv[1:]):
            n = min(len(p0), len(p1))
            for i in range(n):
                j = (i + 1) % n
                f = [(p0[i][0] + cx, p0[i][1] + cy, z0), (p0[j][0] + cx, p0[j][1] + cy, z0),
                     (p1[j][0] + cx, p1[j][1] + cy, z1), (p1[i][0] + cx, p1[i][1] + cy, z1)]
                if math.hypot(f[0][0] - f[1][0], f[0][1] - f[1][1]) + math.hypot(f[2][0] - f[3][0], f[2][1] - f[3][1]) > 1e-6:
                    res.append(f)
        for z, p in (nv[0], nv[-1]):
            res.append([(x + cx, y + cy, z) for x, y in p])
        if self.alesage:
            ax, ay, zb, zh = self.alesage
            zb, zh = max(zb, self.z_bas), min(zh, self.z_haut)
            c = [(-ax / 2, -ay / 2), (ax / 2, -ay / 2), (ax / 2, ay / 2), (-ax / 2, ay / 2)]
            for i in range(4):
                a, b = c[i], c[(i + 1) % 4]
                res.append([(a[0] + cx, a[1] + cy, zb), (b[0] + cx, b[1] + cy, zb), (b[0] + cx, b[1] + cy, zh),
                            (a[0] + cx, a[1] + cy, zh)])
        return res

    def _vers_3d_ajour(self, k, decalage_n=0.0):
        ang = self.directions[k][0]
        n = (math.cos(math.radians(ang)), math.sin(math.radians(ang)))
        t = (math.cos(math.radians(ang - 90.0)), math.sin(math.radians(ang - 90.0)))
        cx, cy = self.centre[0], self.centre[1]
        return lambda u, v: (cx + u * t[0] + decalage_n * n[0], cy + u * t[1] + decalage_n * n[1], v)

    def facettes_trous(self, decalage=0.3):
        if not self.ajours:
            return []
        k, profils_aj = self.ajours
        a = self.directions[k][1]
        res = []
        for sgn in (-1.0, 1.0):
            f = self._vers_3d_ajour(k, sgn * (a + decalage))
            for p in profils_aj:
                res.append([f(u, v) for u, v in p.points()])
        return res

    def contour_section(self, k):
        """Boucle fermee (segments) de la tranche k dans son plan (s, z), s de off-a a off+a."""
        ang, a, trace, off = self.directions[k]
        droite = pf.transformer(trace, lambda p: (off + a - p[0], p[1]))
        gauche = pf.inverser(pf.transformer(trace, lambda p: (off - (a - p[0]), p[1])))
        bas_d, bas_g = droite[-1][-1], gauche[0][1]
        haut_g, haut_d = gauche[-1][-1], droite[0][1]
        res = list(droite)
        if math.hypot(bas_d[0] - bas_g[0], bas_d[1] - bas_g[1]) > 1e-9:
            res.append(("L", bas_d, bas_g))
        res += gauche
        if math.hypot(haut_g[0] - haut_d[0], haut_g[1] - haut_d[1]) > 1e-9:
            res.append(("L", haut_g, haut_d))
        return res


# ---------------------------------------------------------------------------
# Revolution
# ---------------------------------------------------------------------------
class Revolution(_Corps):
    """Profil (r, z) revolu autour de la verticale passant par (x, y).

    :param profil_rz: segments fermes dans le plan (r, z), r >= 0, comprenant
        le segment sur l'axe (r = 0).
    """
    genre = "revolution"

    def __init__(self, nom, piece, centre_xy, profil_rz, materiau="metal", mobile=False):
        if not pf.chemin_ferme(profil_rz):
            raise ValueError("profil de revolution non ferme : %s" % nom)
        self.nom, self.piece, self.profil = nom, piece, list(profil_rz)
        self.materiau, self.mobile = materiau, mobile
        pts = pf.echantillonner(self.profil, 8)
        self.z_bas, self.z_haut = min(p[1] for p in pts), max(p[1] for p in pts)
        self.rmax = max(p[0] for p in pts)
        self.centre = (float(centre_xy[0]), float(centre_xy[1]), (self.z_bas + self.z_haut) / 2.0)

    @property
    def longueur(self):
        return self.z_haut - self.z_bas

    def volume_mm3(self):
        pts = pf.echantillonner(self.profil, 12)[:-1]
        # theoreme de Guldin : V = 2 pi . r_G . A
        A = Sx = 0.0
        for i in range(len(pts)):
            (x0, y0), (x1, y1) = pts[i], pts[(i + 1) % len(pts)]
            cr = x0 * y1 - x1 * y0
            A += cr
            Sx += (x0 + x1) * cr
        A /= 2.0
        return abs(2 * math.pi * (Sx / 6.0))

    def boite_englobante(self):
        x, y = self.centre[0], self.centre[1]
        return ((x - self.rmax, y - self.rmax, self.z_bas), (x + self.rmax, y + self.rmax, self.z_haut))

    def facettes(self, n=12):
        x, y = self.centre[0], self.centre[1]
        pts = pf.echantillonner(self.profil, 6)
        res = []
        for k in range(n):
            a0, a1 = 2 * math.pi * k / n, 2 * math.pi * (k + 1) / n
            for (r0, z0), (r1, z1) in zip(pts, pts[1:]):
                if r0 < 1e-9 and r1 < 1e-9:
                    continue
                res.append([(x + r0 * math.cos(a0), y + r0 * math.sin(a0), z0), (x + r1 * math.cos(a0), y + r1 * math.sin(a0), z1),
                            (x + r1 * math.cos(a1), y + r1 * math.sin(a1), z1), (x + r0 * math.cos(a1), y + r0 * math.sin(a1), z0)])
        return res

    def facettes_trous(self, decalage=0.3):
        return []


def tete_goutte_de_suif(z_assise, diametre, hauteur):
    """Profil (r, z) d'une tete de rivet goutte de suif (calotte spherique)."""
    r = diametre / 2.0
    pm_r = r * 0.62
    # calotte : arc par (r, z0), (pm_r, z0 + 0.79h), (0, z0 + h)
    R = (r * r + hauteur * hauteur) / (2.0 * hauteur)
    zc = z_assise + hauteur - R
    pm = (R * math.sin(math.asin(min(1.0, r / R)) / 2.0), zc + R * math.cos(math.asin(min(1.0, r / R)) / 2.0))
    del pm_r
    return [("L", (0.0, z_assise), (r, z_assise)), ("A", (r, z_assise), pm, (0.0, z_assise + hauteur)),
            ("L", (0.0, z_assise + hauteur), (0.0, z_assise))]


# ---------------------------------------------------------------------------
# Construction dans Fusion
# ---------------------------------------------------------------------------
def _adsk():
    import adsk.core
    import adsk.fusion
    return adsk.core, adsk.fusion


def _point(core, xyz_mm):
    return core.Point3D.create(mm_vers_cm(xyz_mm[0]), mm_vers_cm(xyz_mm[1]), mm_vers_cm(xyz_mm[2]))


class ConstructeurFusion(object):
    """Construit ``Solide``, ``BlocProfile`` et ``Revolution`` dans un composant Fusion.

    - Plans decales des plans d'origine (sens reel controle par
      ``plane.geometry`` et corrige si besoin), plans verticaux tournes autour
      de l'axe Z (``setByAngle``) pour les tranches a 45 deg.
    - Chemins dessines avec de VRAIS arcs (``sketchArcs.addByThreePoints``).
    """

    def __init__(self, composant):
        self.comp = composant
        self.core, self.fusion = _adsk()
        self._plans = {}
        self.journal = []

    # -- plans -----------------------------------------------------------------
    def plan(self, axe, decalage_mm):
        cle = (axe, round(decalage_mm, 4))
        if cle in self._plans:
            return self._plans[cle]
        base = {"z": self.comp.xYConstructionPlane, "x": self.comp.yZConstructionPlane,
                "y": self.comp.xZConstructionPlane}[axe]
        if abs(decalage_mm) < 1e-9:
            self._plans[cle] = base
            return base
        ia = INDICE_AXE[axe]
        plan = self._creer_plan(base, decalage_mm)
        try:
            o = plan.geometry.origin
            reel = (o.x, o.y, o.z)[ia] * MM_PAR_CM
            if abs(reel - decalage_mm) > 1e-3 and abs(reel + decalage_mm) < 1e-3:
                plan.deleteMe()
                plan = self._creer_plan(base, -decalage_mm)
        except AttributeError:
            pass
        self._plans[cle] = plan
        return plan

    def _creer_plan(self, base, decalage_mm):
        planes = self.comp.constructionPlanes
        entree = planes.createInput()
        entree.setByOffset(base, self.core.ValueInput.createByReal(mm_vers_cm(decalage_mm)))
        return planes.add(entree)

    def plan_vertical(self, angle_deg, cx=0.0, cy=0.0):
        """Plan vertical contenant la direction ``angle_deg`` et passant par (cx, cy) (mm).

        Base : plan XZ (0 deg), YZ (90 deg) ou plan tourne autour de l'axe Z
        (``setByAngle``, sens verifie par la normale) ; puis decalage le long
        de la normale REELLE du plan de base (sens verifie par ``geometry``).
        """
        a = angle_deg % 180.0
        cle = ("v", round(a, 4), round(cx, 4), round(cy, 4))
        if cle in self._plans:
            return self._plans[cle]
        base = self._plan_vertical_origine(a)
        n = base.geometry.normal
        dist = n.x * cx + n.y * cy
        if abs(dist) < 1e-9:
            plan = base
        else:
            plan = self._creer_plan(base, dist)
            try:
                g = plan.geometry
                cst = (g.normal.x * g.origin.x + g.normal.y * g.origin.y + g.normal.z * g.origin.z) * MM_PAR_CM
                cible = g.normal.x * cx + g.normal.y * cy
                if abs(cst - cible) > 1e-3:
                    plan.deleteMe()
                    plan = self._creer_plan(base, -dist)
            except AttributeError:
                pass
        self._plans[cle] = plan
        return plan

    def _plan_vertical_origine(self, a):
        cle = ("v0", round(a, 4))
        if cle in self._plans:
            return self._plans[cle]
        if abs(a) < 1e-9:
            plan = self.comp.xZConstructionPlane
        elif abs(a - 90.0) < 1e-9:
            plan = self.comp.yZConstructionPlane
        else:
            plan = self._plan_angle(a)
            n = plan.geometry.normal
            dx, dy = math.cos(math.radians(a)), math.sin(math.radians(a))
            if abs(n.x * dx + n.y * dy) > 1e-3:
                plan.deleteMe()
                plan = self._plan_angle(-a)
        self._plans[cle] = plan
        return plan

    def _plan_angle(self, a):
        planes = self.comp.constructionPlanes
        entree = planes.createInput()
        entree.setByAngle(self.comp.zConstructionAxis, self.core.ValueInput.createByString("%.6f deg" % a),
                          self.comp.xZConstructionPlane)
        return planes.add(entree)

    # -- esquisses ----------------------------------------------------------------
    def _dessiner_boucle(self, esquisse, profil, vers_3d):
        """Dessine une boucle ; ``vers_3d(u, v)`` donne le point modele (mm)."""
        P = lambda u, v: esquisse.modelToSketchSpace(_point(self.core, vers_3d(u, v)))
        courbes = esquisse.sketchCurves
        if profil.type == "cercle":
            courbes.sketchCircles.addByCenterRadius(P(0.0, 0.0), mm_vers_cm(profil.donnees))
            return
        if profil.type == "chemin":
            for s in profil.donnees:
                if s[0] == "L":
                    courbes.sketchLines.addByTwoPoints(P(*s[1]), P(*s[2]))
                else:
                    courbes.sketchArcs.addByThreePoints(P(*s[1]), P(*s[2]), P(*s[3]))
            return
        pts = [P(u, v) for u, v in profil.points()]
        for i in range(len(pts)):
            courbes.sketchLines.addByTwoPoints(pts[i], pts[(i + 1) % len(pts)])

    @staticmethod
    def _choisir_profil(esquisse, n_boucles):
        profils = esquisse.profiles
        if profils.count == 0:
            raise RuntimeError("Esquisse sans profil ferme : %s" % esquisse.name)
        if n_boucles == 1:
            return profils.item(0)
        for i in range(profils.count):
            if profils.item(i).profileLoops.count == n_boucles:
                return profils.item(i)
        raise RuntimeError("Profil a %d boucles introuvable dans %s" % (n_boucles, esquisse.name))

    def _extruder(self, profil, longueur_mm, operation, participants=None, expression=None):
        ex = self.comp.features.extrudeFeatures
        entree = ex.createInput(profil, operation)
        val = (self.core.ValueInput.createByString(expression) if expression
               else self.core.ValueInput.createByReal(mm_vers_cm(longueur_mm)))
        entree.setSymmetricExtent(val, True)
        if participants:
            entree.participantBodies = list(participants)
        return ex.add(entree)

    # -- corps ----------------------------------------------------------------------
    def construire(self, corps):
        if isinstance(corps, BlocProfile):
            return self.construire_bloc(corps)
        if isinstance(corps, Revolution):
            return self.construire_revolution(corps)
        return self.construire_solide(corps)

    def construire_solide(self, solide):
        ia = INDICE_AXE[solide.axe]
        plan = self.plan(solide.axe, solide.centre[ia])
        esq = self.comp.sketches.add(plan)
        esq.name = "esq_" + solide.nom
        vers = lambda u, v: solide.point(u, v, 0.0)
        self._dessiner_boucle(esq, solide.ext, vers)
        for b in solide.boucles_interieures():
            self._dessiner_boucle(esq, b, vers)
        prof = self._choisir_profil(esq, 1 + len(solide.boucles_interieures()))
        feat = self._extruder(prof, solide.longueur, self.fusion.FeatureOperations.NewBodyFeatureOperation)
        body = feat.bodies.item(0)
        body.name = solide.nom
        self.journal.append(solide.nom)
        return body

    def construire_bloc(self, bloc):
        """Tranches successives (1re = nouveau corps, suivantes = intersection), puis alesage (enlevement).

        Chaque tranche est esquissee EN PLACE sur le plan vertical passant par
        le centre du bloc : aucun deplacement n'est necessaire.
        """
        ops = self.fusion.FeatureOperations
        body = None
        cx, cy = bloc.centre[0], bloc.centre[1]
        bb = bloc.boite_englobante()
        portee = 2.0 * max(abs(bb[0][0] - cx), abs(bb[1][0] - cx), abs(bb[0][1] - cy), abs(bb[1][1] - cy)) + 40.0
        for k, (ang, a, trace, off) in enumerate(bloc.directions):
            plan = self.plan_vertical(ang, cx, cy)
            esq = self.comp.sketches.add(plan)
            esq.name = "esq_%s_t%d" % (bloc.nom, k)
            c, s = math.cos(math.radians(ang)), math.sin(math.radians(ang))
            self._dessiner_boucle(esq, chemin(bloc.contour_section(k)), lambda u, v: (cx + u * c, cy + u * s, v))
            prof = self._choisir_profil(esq, 1)
            if body is None:
                feat = self._extruder(prof, portee, ops.NewBodyFeatureOperation)
                body = feat.bodies.item(0)
            else:
                self._extruder(prof, portee, ops.IntersectFeatureOperation, [body])
        for k, (x0, x1, y0, y1, z0, z1) in enumerate(bloc.enlevements):
            z0, z1 = max(z0, bloc.z_bas) - 1.0, min(z1, bloc.z_haut) + 1.0
            zm = (z0 + z1) / 2.0
            esq = self.comp.sketches.add(self.plan("z", zm))
            esq.name = "esq_%s_enl%d" % (bloc.nom, k)
            self._dessiner_boucle(esq, rectangle(x1 - x0, y1 - y0, (x0 + x1) / 2.0, (y0 + y1) / 2.0),
                                  lambda u, v: (cx + u, cy + v, zm))
            self._extruder(self._choisir_profil(esq, 1), z1 - z0, ops.CutFeatureOperation, [body])
        if bloc.ajours:
            k, profils_aj = bloc.ajours
            ang = bloc.directions[k][0]
            esq = self.comp.sketches.add(self.plan_vertical(ang - 90.0, cx, cy))
            esq.name = "esq_%s_ajours" % bloc.nom
            f = bloc._vers_3d_ajour(k)
            for p in profils_aj:
                self._dessiner_boucle(esq, p, f)
            for i in range(esq.profiles.count):
                self._extruder(esq.profiles.item(i), 2.0 * bloc.directions[k][1] + 10.0, ops.CutFeatureOperation, [body])
        body.name = bloc.nom
        self.journal.append(bloc.nom)
        return body

    def construire_revolution(self, rev):
        plan = self.plan("y", rev.centre[1])
        esq = self.comp.sketches.add(plan)
        esq.name = "esq_" + rev.nom
        x0, y0 = rev.centre[0], rev.centre[1]
        P = lambda r, z: esq.modelToSketchSpace(_point(self.core, (x0 + r, y0, z)))
        courbes = esq.sketchCurves
        axe = None
        for sg in rev.profil:
            if sg[0] == "L":
                ligne = courbes.sketchLines.addByTwoPoints(P(*sg[1]), P(*sg[2]))
                if abs(sg[1][0]) < 1e-9 and abs(sg[2][0]) < 1e-9:
                    axe = ligne
            else:
                courbes.sketchArcs.addByThreePoints(P(*sg[1]), P(*sg[2]), P(*sg[3]))
        if axe is None:
            raise RuntimeError("profil de revolution sans segment d'axe : %s" % rev.nom)
        rv = self.comp.features.revolveFeatures
        entree = rv.createInput(self._choisir_profil(esq, 1), axe, self.fusion.FeatureOperations.NewBodyFeatureOperation)
        entree.setAngleExtent(False, self.core.ValueInput.createByString("360 deg"))
        feat = rv.add(entree)
        body = feat.bodies.item(0)
        body.name = rev.nom
        self.journal.append(rev.nom)
        return body

    def construire_tous(self, corps):
        return [self.construire(c) for c in corps]

    # -- deplacements ------------------------------------------------------------------
    def translater(self, corps, dx, dy, dz):
        coll = self.core.ObjectCollection.create()
        for c in corps:
            coll.add(c)
        moves = self.comp.features.moveFeatures
        entree = moves.createInput2(coll)
        V = lambda v: self.core.ValueInput.createByReal(mm_vers_cm(v))
        entree.defineAsTranslateXYZ(V(dx), V(dy), V(dz), True)
        return moves.add(entree)

    def deplacer_z(self, corps, expression):
        """Translation Z liee a une EXPRESSION Fusion (le cran pilote la hauteur)."""
        coll = self.core.ObjectCollection.create()
        for c in corps:
            coll.add(c)
        moves = self.comp.features.moveFeatures
        entree = moves.createInput2(coll)
        zero = self.core.ValueInput.createByReal(0.0)
        entree.defineAsTranslateXYZ(zero, zero, self.core.ValueInput.createByString(expression), True)
        return moves.add(entree)


def ecrire_user_parameters(design, lignes):
    """Cree ou met a jour des User Parameters ; lignes = (nom, expression, unite, commentaire)."""
    core, _ = _adsk()
    ups = design.userParameters
    crees, maj = [], []
    for nom, expression, unite, commentaire in lignes:
        existant = ups.itemByName(nom)
        if existant:
            existant.expression = expression
            existant.comment = commentaire
            maj.append(nom)
        else:
            ups.add(nom, core.ValueInput.createByString(expression), unite, commentaire)
            crees.append(nom)
    return crees, maj


def lire_user_parameter(design, nom, defaut=None):
    """Valeur d'un User Parameter (unite interne Fusion : cm pour une longueur !) ou ``defaut``."""
    p = design.userParameters.itemByName(nom)
    return p.value if p else defaut
