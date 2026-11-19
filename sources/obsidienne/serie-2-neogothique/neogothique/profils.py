# -*- coding: utf-8 -*-
"""Geometrie pure des profils de la gamme : chants moulures, traces de pieds,
motifs gothiques (ogive, lobes), terminaisons forgees, proprietes de section.

Conventions
-----------
*Segment* : ``("L", p0, p1)`` (droite) ou ``("A", p0, pm, p1)`` (arc par trois
points : depart, point intermediaire, arrivee). Les points sont des tuples 2D.

*Trace de chant* : suite de segments dans le plan (d, z) ou ``d`` est le
RETRAIT vers l'interieur depuis la face exterieure de reference (d = 0) et
``z`` la hauteur absolue (mm). Une trace va toujours du HAUT vers le BAS. Dans
la direction de normale n, la matiere occupe |s| <= a_n - d(z) (``a_n`` :
demi-largeur de reference). Un bloc moulure = intersection de ces
« tranches » pour 2 directions (rectangle, carre) ou 4 (octogone, carre a
chanfreins arretes) : les onglets des moulures sont donc exacts.

Pas de courbe organique : uniquement des arcs de cercle de moulure
(quart-de-rond, cavet, tore, gorge, ogive, lobes) et des droites.
"""

import math

PHI = (1.0 + math.sqrt(5.0)) / 2.0


# ---------------------------------------------------------------------------
# Arcs
# ---------------------------------------------------------------------------
def _norm(v):
    n = math.hypot(v[0], v[1])
    return (v[0] / n, v[1] / n) if n else (0.0, 0.0)


def arc_centre(centre, p0, p1, petit=True):
    """Arc de centre donne entre p0 et p1 (rayon |p0-centre|) ; segment ('A', p0, pm, p1)."""
    r = math.hypot(p0[0] - centre[0], p0[1] - centre[1])
    m = ((p0[0] + p1[0]) / 2.0 - centre[0], (p0[1] + p1[1]) / 2.0 - centre[1])
    u = _norm(m)
    if u == (0.0, 0.0):
        raise ValueError("arc de 180 deg : point milieu indetermine")
    if not petit:
        u = (-u[0], -u[1])
    return ("A", tuple(p0), (centre[0] + r * u[0], centre[1] + r * u[1]), tuple(p1))


def quart(p0, p1, convexe):
    """Quart de cercle entre p0 et p1 (|du| = |dv|) dans le plan (d, z).

    ``convexe`` : centre du cote de la matiere (d le plus grand) -> arrondi ;
    sinon centre hors matiere -> creux (cavet, gorge).
    """
    if abs(abs(p1[0] - p0[0]) - abs(p1[1] - p0[1])) > 1e-6:
        raise ValueError("quart de cercle : |dd| doit egaler |dz| (%s -> %s)" % (p0, p1))
    c1, c2 = (p0[0], p1[1]), (p1[0], p0[1])
    centre = max(c1, c2, key=lambda c: c[0]) if convexe else min(c1, c2, key=lambda c: c[0])
    return arc_centre(centre, p0, p1)


def cercle_par_3_points(p0, pm, p1):
    ax, ay = p0
    bx, by = pm
    cx, cy = p1
    d = 2.0 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))
    if abs(d) < 1e-12:
        return None, None
    ux = ((ax ** 2 + ay ** 2) * (by - cy) + (bx ** 2 + by ** 2) * (cy - ay) + (cx ** 2 + cy ** 2) * (ay - by)) / d
    uy = ((ax ** 2 + ay ** 2) * (cx - bx) + (bx ** 2 + by ** 2) * (ax - cx) + (cx ** 2 + cy ** 2) * (bx - ax)) / d
    return (ux, uy), math.hypot(ax - ux, ay - uy)


def echantillonner_arc(p0, pm, p1, n=8):
    """Points de l'arc (p0 exclu, p1 inclus)."""
    c, r = cercle_par_3_points(p0, pm, p1)
    if c is None:
        return [tuple(p1)]
    a0 = math.atan2(p0[1] - c[1], p0[0] - c[0])
    am = math.atan2(pm[1] - c[1], pm[0] - c[0])
    a1 = math.atan2(p1[1] - c[1], p1[0] - c[0])

    def norm(a):
        while a < 0:
            a += 2 * math.pi
        return a
    d1, dm = norm(a1 - a0), norm(am - a0)
    sweep = d1 if dm <= d1 else d1 - 2 * math.pi
    return [(c[0] + r * math.cos(a0 + sweep * k / n), c[1] + r * math.sin(a0 + sweep * k / n))
            for k in range(1, n + 1)]


def echantillonner(segments, n_arc=8):
    """Polyligne (liste de points) d'une suite de segments, premier point inclus."""
    if not segments:
        return []
    pts = [tuple(segments[0][1])]
    for s in segments:
        if s[0] == "L":
            pts.append(tuple(s[2]))
        else:
            pts.extend(echantillonner_arc(s[1], s[2], s[3], n_arc))
    return pts


def inverser(segments):
    res = []
    for s in reversed(segments):
        res.append(("L", s[2], s[1]) if s[0] == "L" else ("A", s[3], s[2], s[1]))
    return res


def transformer(segments, f):
    return [tuple([s[0]] + [f(p) for p in s[1:]]) for s in segments]


def chemin_ferme(segments, tol=1e-6):
    """Vrai si les segments sont chaines et la boucle fermee."""
    for a, b in zip(segments, segments[1:] + segments[:1]):
        fin, deb = a[-1], b[1]
        if math.hypot(fin[0] - deb[0], fin[1] - deb[1]) > tol:
            return False
    return True


# ---------------------------------------------------------------------------
# Traces (d, z)
# ---------------------------------------------------------------------------
class Trace(object):
    """Constructeur de trace (d, z) du haut vers le bas."""

    def __init__(self, d, z):
        self.segments = []
        self.p = (float(d), float(z))
        self.debut = self.p

    def _ajout(self, seg):
        p1 = seg[-1]
        if math.hypot(p1[0] - self.p[0], p1[1] - self.p[1]) > 1e-9:
            self.segments.append(seg)
            self.p = (float(p1[0]), float(p1[1]))
        return self

    def ligne(self, d, z):
        if z > self.p[1] + 1e-9:
            raise ValueError("une trace descend : z %g > %g" % (z, self.p[1]))
        return self._ajout(("L", self.p, (float(d), float(z))))

    def vers(self, z):
        return self.ligne(self.p[0], z)

    def palier(self, d):
        return self.ligne(d, self.p[1])

    def quart(self, d, z, convexe):
        if abs(d - self.p[0]) < 1e-9:
            return self
        return self._ajout(quart(self.p, (float(d), float(z)), convexe))

    def arc(self, pm, p1):
        return self._ajout(("A", self.p, tuple(pm), (float(p1[0]), float(p1[1]))))

    def chant(self, segments_locaux, position):
        """Ajoute un chant (coordonnees locales u = retrait, v = distance a la face).

        ``position`` "haut" : la trace part de la face superieure ; "bas" : la
        trace descend le long du cote puis rejoint la face inferieure.
        """
        if position == "haut":
            z0 = self.p[1]
            for s in segments_locaux:
                self._ajout(tuple([s[0]] + [(p[0], z0 - p[1]) for p in s[1:]]))
        else:
            raise ValueError("utiliser ajouter_chant_bas")
        return self


def chant_local(type_, taille, hauteur=None, profondeur=None):
    """Segments locaux d'un chant, de la face (u = retrait, v = 0) vers le cote (u = 0).

    :param type_: "droit", "chanfrein", "conge", "quart_de_rond", "cavet",
        "bec_de_corbin".
    :param taille: rayon / cote principal (mm).
    :param hauteur, profondeur: pour "bec_de_corbin" (zone moulee totale).
    :return: (segments, point_face, point_cote).
    """
    t = float(taille)
    if type_ == "droit" or t <= 0:
        return [], (0.0, 0.0), (0.0, 0.0)
    if type_ == "chanfrein":
        return [("L", (t, 0.0), (0.0, t))], (t, 0.0), (0.0, t)
    if type_ == "conge":
        return [quart((t, 0.0), (0.0, t), True)], (t, 0.0), (0.0, t)
    if type_ == "quart_de_rond":
        f = max(1.0, round(t * 0.2, 1))  # listel
        segs = [quart((t + f, 0.0), (f, t), True), ("L", (f, t), (0.0, t)), ("L", (0.0, t), (0.0, t + f))]
        return segs, (t + f, 0.0), (0.0, t + f)
    if type_ == "cavet":
        return [quart((t, 0.0), (0.0, t), False)], (t, 0.0), (0.0, t)
    if type_ == "bec_de_corbin":
        h = float(hauteur or 2 * t)
        p = float(profondeur or t)
        rt = min(0.35 * h, 0.5 * p)
        rg = min(0.3 * h, p - rt)
        v1 = h - rt - rg
        segs = []
        if v1 > 1e-9:
            segs.append(("L", (p, 0.0), (p, v1)))
        segs.append(quart((p, v1), (p - rg, v1 + rg), False))
        if p - rg - rt > 1e-9:
            segs.append(("L", (p - rg, v1 + rg), (rt, v1 + rg)))
        segs.append(quart((rt, v1 + rg), (0.0, h), True))
        return segs, (p, 0.0), (0.0, h)
    raise ValueError("type de chant inconnu : %r" % type_)


TYPES_CHANT = ("droit", "chanfrein", "conge", "quart_de_rond", "cavet", "bec_de_corbin")


def trace_bloc(z_haut, z_bas, chant_haut=("droit", 0), chant_bas=("droit", 0)):
    """Trace d'un bloc droit (d = 0) avec un chant en haut et un chant en bas.

    ``chant_*`` : (type, taille[, hauteur, profondeur]).
    """
    sh, fh, ch = chant_local(*chant_haut)
    sb, fb, cb = chant_local(*chant_bas)
    if ch[1] + cb[1] > (z_haut - z_bas) + 1e-6:
        raise ValueError("chants plus hauts que la piece (%g + %g > %g)" % (ch[1], cb[1], z_haut - z_bas))
    tr = Trace(fh[0], z_haut)
    for s in sh:
        tr._ajout(tuple([s[0]] + [(p[0], z_haut - p[1]) for p in s[1:]]))
    tr.vers(z_bas + cb[1])
    # chant bas : coordonnees locales v mesurees depuis la face inferieure, parcours inverse
    for s in inverser(sb):
        tr._ajout(tuple([s[0]] + [(p[0], z_bas + p[1]) for p in s[1:]]))
    return tr


def evaluer(trace_segments, z, cote="dessus"):
    """Retrait d(z) d'une trace (polyligne echantillonnee).

    En cas de palier horizontal a la cote z, ``cote`` choisit la valeur juste
    au-dessus ("dessus") ou juste au-dessous ("dessous").
    """
    pts = echantillonner(trace_segments, 12)
    if z >= pts[0][1] - 1e-9:
        return pts[0][0]
    if z <= pts[-1][1] + 1e-9:
        return pts[-1][0]
    cand = []
    for (d0, z0), (d1, z1) in zip(pts, pts[1:]):
        if z1 - 1e-9 <= z <= z0 + 1e-9:
            if abs(z0 - z1) < 1e-9:
                cand.append(d0 if cote == "dessus" else d1)
            else:
                cand.append(d0 + (d1 - d0) * (z0 - z) / (z0 - z1))
    return cand[0] if cote == "dessus" else cand[-1]


def cotes_z(trace_segments):
    return [p[1] for p in echantillonner(trace_segments, 6)]


def proprietes_section(a, trace_segments, n=400):
    """Aire, centre de gravite et inertie de la section |s| <= a - d(z) (plan s, z).

    :return: dict(aire, zg, inertie, w_inf, w_sup) en mm2 / mm / mm4 / mm3.
    """
    pts = echantillonner(trace_segments, 16)
    z_h, z_b = pts[0][1], pts[-1][1]
    dz = (z_h - z_b) / n
    A = Sz = Szz = 0.0
    for k in range(n):
        z = z_b + (k + 0.5) * dz
        b = max(0.0, 2.0 * (a - evaluer(trace_segments, z)))
        A += b * dz
        Sz += b * dz * z
        Szz += b * dz * z * z
    zg = Sz / A
    I = Szz - A * zg * zg
    return {"aire": A, "zg": zg, "inertie": I, "w_inf": I / (zg - z_b), "w_sup": I / (z_h - zg),
            "z_haut": z_h, "z_bas": z_b}


# ---------------------------------------------------------------------------
# Motifs gothiques (boucles fermees, coordonnees 2D quelconques)
# ---------------------------------------------------------------------------
def ogive(cx, base, largeur, hauteur, ratio_rayon=1.0):
    """Baie en arc brise : piedroits verticaux + deux arcs de rayon ratio x largeur.

    ``ratio_rayon`` = 1 : ogive equilaterale ; < 1 : surbaissee (>= 0,5) ;
    > 1 : lancette. Retourne une boucle fermee (base en bas).
    """
    w = float(largeur)
    R = max(0.5, ratio_rayon) * w
    xg, xd = cx - w / 2.0, cx + w / 2.0
    fleche = math.sqrt(R ** 2 - (R - w / 2.0) ** 2)  # hauteur de l'arc
    z_nais = base + hauteur - fleche
    if z_nais < base - 1e-9:
        raise ValueError("ogive trop haute pour la hauteur disponible")
    sommet = (cx, base + hauteur)
    # arc droit : centre sur la naissance gauche decale de R
    cd = (xd - R, z_nais)
    cg = (xg + R, z_nais)
    segs = [("L", (xg, base), (xd, base))]
    if z_nais > base + 1e-9:
        segs.append(("L", (xd, base), (xd, z_nais)))
    segs.append(arc_centre(cd, (xd, z_nais), sommet))
    segs.append(arc_centre(cg, sommet, (xg, z_nais)))
    if z_nais > base + 1e-9:
        segs.append(("L", (xg, z_nais), (xg, base)))
    return segs


def lobes(cx, cz, rayon_total, n=3, angle0=90.0):
    """Trilobe / quadrilobe : contour exterieur de n cercles disposes en couronne.

    ``rayon_total`` : rayon du cercle circonscrit au motif. Boucle fermee.
    """
    a = math.pi / n
    # cercles de rayon r centres a rho : r = rho . sin(a) . k, contact a ~ 2 r
    rho = rayon_total / (1.0 + math.sin(a) * 1.15)
    r = rho * math.sin(a) * 1.15
    centres = [(cx + rho * math.cos(math.radians(angle0) + 2 * a * i),
                cz + rho * math.sin(math.radians(angle0) + 2 * a * i)) for i in range(n)]
    # points de rebroussement entre lobes voisins (intersection exterieure... interieure au motif)
    cusps = []
    for i in range(n):
        c1, c2 = centres[i], centres[(i + 1) % n]
        mx, mz = (c1[0] + c2[0]) / 2.0, (c1[1] + c2[1]) / 2.0
        dd = math.hypot(c2[0] - c1[0], c2[1] - c1[1]) / 2.0
        h = math.sqrt(max(r * r - dd * dd, 0.0))
        nx, nz = mx - cx, mz - cz
        L = math.hypot(nx, nz)
        cusps.append((mx + h * nx / L, mz + h * nz / L))
    segs = []
    for i in range(n):
        c = centres[(i + 1) % n]
        p0, p1 = cusps[i], cusps[(i + 1) % n]
        # milieu exterieur du lobe
        ux, uz = c[0] - cx, c[1] - cz
        L = math.hypot(ux, uz)
        pm = (c[0] + r * ux / L, c[1] + r * uz / L)
        segs.append(("A", p0, pm, p1))
    return segs


def rectangle_chemin(x0, z0, x1, z1):
    return [("L", (x0, z0), (x1, z0)), ("L", (x1, z0), (x1, z1)), ("L", (x1, z1), (x0, z1)), ("L", (x0, z1), (x0, z0))]


def ajours_arcature(longueur, hauteur, n, motif="ogive", marge=8.0, ratio_largeur=0.55, ratio_rayon=1.0):
    """Ajours d'une ceinture : n baies regulierement espacees (repere local x centre, z depuis le bas).

    :return: (liste de boucles, largeur_baie, montant_entre_baies)
    """
    pas = longueur / float(n)
    w = pas * ratio_largeur
    hdisp = hauteur - 2 * marge
    if motif == "ogive":
        R = max(0.5, ratio_rayon) * w
        fleche = math.sqrt(R ** 2 - (R - w / 2.0) ** 2)
        if fleche > hdisp:
            w = w * hdisp / fleche
        boucles = [ogive(-longueur / 2.0 + pas * (i + 0.5), marge, w, hdisp, ratio_rayon) for i in range(n)]
    elif motif in ("trilobe", "quadrilobe"):
        nl = 3 if motif == "trilobe" else 4
        rt = min(w, hdisp) / 2.0
        w = 2 * rt
        boucles = [lobes(-longueur / 2.0 + pas * (i + 0.5), marge + hdisp / 2.0, rt, nl,
                         90.0 if nl == 3 else 45.0) for i in range(n)]
    else:
        raise ValueError("motif d'ajour inconnu : %r" % motif)
    return boucles, w, pas - w


# ---------------------------------------------------------------------------
# Terminaisons forgees des pentures (repere : axe de la bande = u, bout en u = 0)
# ---------------------------------------------------------------------------
TERMINAISONS_FORMES = ("droite", "fleur_de_lys", "queue_d_aronde", "trilobe")


def _arc_exterieur(c, r, p, q, o):
    """Arc de centre c, rayon r, de p a q en passant par le cote oppose au point o (exterieur du lobe)."""
    ap, aq = math.atan2(p[1] - c[1], p[0] - c[0]), math.atan2(q[1] - c[1], q[0] - c[0])
    av = math.atan2(c[1] - o[1], c[0] - o[0])
    tau = 2 * math.pi
    ccw = (aq - ap) % tau
    contient = (av - ap) % tau <= ccw
    am = ap + ccw / 2.0 if contient else ap - (tau - ccw) / 2.0
    return ("A", tuple(p), (c[0] + r * math.cos(am), c[1] + r * math.sin(am)), tuple(q))


def penture(longueur, largeur, terminaison="fleur_de_lys"):
    """Contour d'une branche de penture : bande de ``largeur`` sur ``longueur``.

    La bande part de u = 0 (angle de la platine) et se termine en u = longueur
    par la terminaison forgee. Repere local (u le long de la bande, v en
    travers, centre v = 0). Retourne une boucle fermee.
    """
    w, L = float(largeur), float(longueur)
    h = w / 2.0
    if terminaison == "droite":
        c = min(3.0, h * 0.4)
        return [("L", (0, -h), (L - c, -h)), ("L", (L - c, -h), (L, -h + c)), ("L", (L, -h + c), (L, h - c)),
                ("L", (L, h - c), (L - c, h)), ("L", (L - c, h), (0, h)), ("L", (0, h), (0, -h))]
    if terminaison == "queue_d_aronde":
        lt = 1.2 * w
        u0 = L - lt
        e = 0.8 * w
        return [("L", (0, -h), (u0, -h)), ("L", (u0, -h), (L, -h - e / 2.0)), ("L", (L, -h - e / 2.0), (L - 0.45 * w, 0.0)),
                ("L", (L - 0.45 * w, 0.0), (L, h + e / 2.0)), ("L", (L, h + e / 2.0), (u0, h)), ("L", (u0, h), (0, h)),
                ("L", (0, h), (0, -h))]
    if terminaison == "trilobe":
        # trefle de trois lobes (rayon total R = largeur), un lobe en pointe, raccorde a la bande
        R = w
        O = (L - R, 0.0)
        rho = R / (1.0 + math.sin(math.pi / 3.0) * 1.15)
        r = rho * math.sin(math.pi / 3.0) * 1.15
        cen = [(O[0] + rho * math.cos(math.radians(120.0 * i)), O[1] + rho * math.sin(math.radians(120.0 * i)))
               for i in range(3)]
        cusp = []
        for i in range(3):
            c1, c2 = cen[i], cen[(i + 1) % 3]
            mx, my = (c1[0] + c2[0]) / 2.0, (c1[1] + c2[1]) / 2.0
            dd = math.hypot(c2[0] - c1[0], c2[1] - c1[1]) / 2.0
            hh = math.sqrt(max(r * r - dd * dd, 0.0))
            nx, ny = mx - O[0], my - O[1]
            n = math.hypot(nx, ny)
            cusp.append((mx + hh * nx / n, my + hh * ny / n))
        if h >= abs(cen[2][1]) + r - 1e-6:
            raise ValueError("trilobe trop petit pour la largeur de bande")

        def jonction(c, signe):
            dv = signe * h - c[1]
            return (c[0] - math.sqrt(r * r - dv * dv), signe * h)

        J2, J1 = jonction(cen[2], -1.0), jonction(cen[1], 1.0)
        segs = [("L", (0, -h), J2),
                _arc_exterieur(cen[2], r, J2, cusp[2], O),
                _arc_exterieur(cen[0], r, cusp[2], cusp[0], O),
                _arc_exterieur(cen[1], r, cusp[0], J1, O),
                ("L", J1, (0, h)), ("L", (0, h), (0, -h))]
        return segs
    if terminaison == "fleur_de_lys":
        lt = 2.0 * w
        u0 = L - lt
        # bague (collier) puis petale central en ogive et deux petales lateraux en crosse
        ub = u0 + 0.22 * w
        ep = 0.75 * w     # envergure laterale des petales
        segs = [("L", (0, -h), (u0, -h)), ("L", (u0, -h), (u0, -h - 0.12 * w)), ("L", (u0, -h - 0.12 * w), (ub, -h - 0.12 * w)),
                ("L", (ub, -h - 0.12 * w), (ub, -0.28 * w))]
        # petale lateral droit (v < 0) : arc vers l'exterieur et retour vers l'axe
        segs.append(("A", (ub, -0.28 * w), (ub + 0.55 * w, -h - ep * 0.6), (ub + 0.95 * w, -h - ep * 0.15)))
        segs.append(("A", (ub + 0.95 * w, -h - ep * 0.15), (ub + 0.70 * w, -0.45 * w), (ub + 0.55 * w, -0.16 * w)))
        # petale central (ogive)
        segs.append(("A", (ub + 0.55 * w, -0.16 * w), (L - 0.35 * w, -0.17 * w), (L, 0.0)))
        segs.append(("A", (L, 0.0), (L - 0.35 * w, 0.17 * w), (ub + 0.55 * w, 0.16 * w)))
        segs.append(("A", (ub + 0.55 * w, 0.16 * w), (ub + 0.70 * w, 0.45 * w), (ub + 0.95 * w, h + ep * 0.15)))
        segs.append(("A", (ub + 0.95 * w, h + ep * 0.15), (ub + 0.55 * w, h + ep * 0.6), (ub, 0.28 * w)))
        segs += [("L", (ub, 0.28 * w), (ub, h + 0.12 * w)), ("L", (ub, h + 0.12 * w), (u0, h + 0.12 * w)),
                 ("L", (u0, h + 0.12 * w), (u0, h)), ("L", (u0, h), (0, h)), ("L", (0, h), (0, -h))]
        return segs
    raise ValueError("terminaison inconnue : %r" % terminaison)
