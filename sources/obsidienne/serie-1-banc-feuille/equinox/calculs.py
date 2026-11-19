# -*- coding: utf-8 -*-
"""Calculs mecaniques simples (ordre de grandeur, pas une note de calcul).

- stabilite au renversement (centre de gravite, polygone de sustentation,
  efforts horizontaux dynamiques), lest requis ;
- glissement au sol ;
- flexion / flambement de sections bois rondes (MOR, MOE du catalogue) ;
- poutre bois rectangulaire (longerons) ;
- helice inox (modele ressort helicoidal, facteur de Wahl).

Unites : mm, kg, N, MPa (N/mm2), N.mm.
"""

import math

from .catalogues.bois import BOIS
from .catalogues.metaux import METAUX
from .geometrie import Verification

G = 9.81


def _niveau(ratio, seuil_ok=1.0, seuil_alerte=None):
    """ratio = capacite / sollicitation."""
    if ratio >= seuil_ok:
        return "ok"
    if seuil_alerte is not None and ratio >= seuil_alerte:
        return "alerte"
    return "echec"


def enveloppe_convexe(points):
    """Enveloppe convexe 2D (sens trigonometrique), algorithme monotone."""
    pts = sorted(set((round(x, 6), round(y, 6)) for x, y in points))
    if len(pts) <= 2:
        return pts

    def cr(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    bas, haut = [], []
    for p in pts:
        while len(bas) >= 2 and cr(bas[-2], bas[-1], p) <= 0:
            bas.pop()
        bas.append(p)
    for p in reversed(pts):
        while len(haut) >= 2 and cr(haut[-2], haut[-1], p) <= 0:
            haut.pop()
        haut.append(p)
    return bas[:-1] + haut[:-1]


def aretes_basculement(polygone):
    """Pour chaque arete : (a, b, normale sortante unitaire)."""
    res = []
    n = len(polygone)
    for i in range(n):
        a, b = polygone[i], polygone[(i + 1) % n]
        dx, dy = b[0] - a[0], b[1] - a[1]
        l = math.hypot(dx, dy)
        res.append((a, b, (dy / l, -dx / l)))  # polygone CCW -> normale sortante a droite
    return res


def distance_interieure(p, a, normale):
    """Distance signee de p a l'arete (positive = a l'interieur)."""
    return -((p[0] - a[0]) * normale[0] + (p[1] - a[1]) * normale[1])


def stabilite(masses, forces_horizontales, points_appui, position_lest=None, securite=1.5):
    """Verifie le renversement autour de chaque arete du polygone de sustentation.

    :param masses: liste (masse_kg, (x, y, z)) : structure, lest, utilisateur reparti
    :param forces_horizontales: liste (nom, (Fx, Fy) [N], z_application [mm])
    :param points_appui: contacts au sol (x, y)
    :param position_lest: (x, y) du lest pour calculer un lest additionnel requis
    :returns: dict avec cg, polygone, cas (un par force et arete critique), lest_requis_kg
    """
    m_tot = sum(m for m, _ in masses)
    cg = tuple(sum(m * p[i] for m, p in masses) / m_tot for i in range(3))
    poly = enveloppe_convexe(points_appui)
    aretes = aretes_basculement(poly)
    marge_cg = min(distance_interieure(cg, a, n) for a, b, n in aretes)
    cas, lest_requis = [], 0.0
    for nom, (fx, fy), z in forces_horizontales:
        pire = None
        for a, b, n in aretes:
            f_n = fx * n[0] + fy * n[1]
            if f_n <= 0:
                continue
            m_renv = f_n * z
            d_cg = distance_interieure(cg, a, n)
            m_stab = m_tot * G * d_cg
            ratio = m_stab / m_renv if m_renv > 0 else float("inf")
            requis = 0.0
            if position_lest is not None and ratio < securite:
                d_l = distance_interieure(position_lest, a, n)
                requis = (securite * m_renv - m_stab) / (G * d_l) if d_l > 1e-6 else float("inf")
            if pire is None or ratio < pire["ratio"]:
                pire = {"force": nom, "arete": (a, b), "ratio": ratio, "m_renv": m_renv, "m_stab": m_stab,
                        "lest_additionnel_kg": requis}
        if pire:
            cas.append(pire)
            lest_requis = max(lest_requis, pire["lest_additionnel_kg"])
    return {"cg": cg, "masse_totale": m_tot, "polygone": poly, "marge_cg_mm": marge_cg, "cas": cas,
            "lest_additionnel_kg": lest_requis}


def verifier_stabilite(resultat, securite):
    """Transforme le resultat de ``stabilite`` en ``Verification``."""
    res = []
    res.append(Verification("cg_dans_polygone", "ok" if resultat["marge_cg_mm"] > 0 else "echec",
                            resultat["marge_cg_mm"], 0.0, "mm",
                            "CG (%.0f, %.0f, %.0f) a %.0f mm du bord du polygone de sustentation"
                            % (resultat["cg"] + (resultat["marge_cg_mm"],))))
    for c in resultat["cas"]:
        niv = _niveau(c["ratio"] / securite, 1.0, 1.0 / securite)
        txt = ("%s : M stabilisant %.0f N.m / M renversant %.0f N.m = %.2f (exige %.2f)"
               % (c["force"], c["m_stab"] / 1000, c["m_renv"] / 1000, c["ratio"], securite))
        if c["lest_additionnel_kg"] > 0:
            txt += " -> lest additionnel requis %.1f kg" % c["lest_additionnel_kg"]
        res.append(Verification("renversement_" + c["force"], niv, c["ratio"], securite, "", txt))
    return res


def verifier_glissement(effort_h, masse_totale, mu):
    cap = mu * masse_totale * G
    r = cap / effort_h if effort_h else float("inf")
    return Verification("glissement", _niveau(r, 1.2, 1.0), r, 1.2, "",
                        "frottement %.0f N vs effort horizontal %.0f N (ratio %.2f) ; au-dessous de 1,2 : "
                        "ancrer au sol via les oeillets bas" % (cap, effort_h, r))


# ---------------------------------------------------------------------------
# Bois
# ---------------------------------------------------------------------------
def module_flexion_rond(d):
    return math.pi * d ** 3 / 32.0


def inertie_rond(d):
    return math.pi * d ** 4 / 64.0


def verifier_flexion_rond(nom, moment_nmm, d, essence, securite):
    mor = BOIS[essence]["resistance_flexion"]
    sigma = moment_nmm / module_flexion_rond(d)
    adm = mor / securite
    r = adm / sigma if sigma else float("inf")
    return Verification(nom, _niveau(r, 1.0, 1.0 / securite * 1.5), sigma, adm, "MPa",
                        "sigma %.1f MPa pour d %.0f mm (M %.1f N.m) ; admissible MOR/%.1f = %.1f MPa"
                        % (sigma, d, moment_nmm / 1000, securite, adm))


def verifier_flambement_rond(nom, effort_n, d_min, longueur, essence, k=2.0, securite=3.0):
    e = BOIS[essence]["module_elasticite"]
    p_cr = math.pi ** 2 * e * inertie_rond(d_min) / (k * longueur) ** 2
    r = p_cr / (effort_n * securite)
    return Verification(nom, _niveau(r, 1.0, 0.7), p_cr, effort_n * securite, "N",
                        "Euler P_cr %.0f N (d mini %.0f, L %.0f, K %.1f) vs %.0f N x %.1f"
                        % (p_cr, d_min, longueur, k, effort_n, securite))


def verifier_poutre_rect(nom, effort_n, portee, b, h, essence, securite, fleche_div):
    """Poutre bi-appuyee, charge ponctuelle centree (cas defavorable)."""
    bo = BOIS[essence]
    m = effort_n * portee / 4.0
    sigma = m / (b * h * h / 6.0)
    adm = bo["resistance_flexion"] / securite
    i = b * h ** 3 / 12.0
    fleche = effort_n * portee ** 3 / (48.0 * bo["module_elasticite"] * i)
    f_adm = portee / fleche_div
    r = min(adm / sigma, f_adm / fleche)
    return Verification(nom, _niveau(r, 1.0, 0.8), sigma, adm, "MPa",
                        "sigma %.1f / %.1f MPa ; fleche %.2f / %.2f mm (portee %.0f, %gx%g)"
                        % (sigma, adm, fleche, f_adm, portee, b, h))


# ---------------------------------------------------------------------------
# Metal : helice
# ---------------------------------------------------------------------------
def verifier_helice(effort_n, diametre_moyen, d_fil, n_spires, nuance, securite, paroi=None):
    """Helice d'appui genou vue comme un ressort helicoidal charge en bout.

    tau = K_w . 8 F D / (pi d^3) (rond plein) ; fleche = 8 F D^3 n / (G d^4).
    Admissible en torsion : 0,577 Re / securite. Renvoie (verifs, d_requis).
    """
    met = METAUX[nuance]
    gmod = met["module_elasticite"] / 2.6
    c = diametre_moyen / d_fil
    kw = (4 * c - 1) / (4 * c - 4) + 0.615 / c
    if paroi:
        di = d_fil - 2 * paroi
        j_fact = (1 - (di / d_fil) ** 4)
    else:
        j_fact = 1.0
    tau = kw * 8 * effort_n * diametre_moyen / (math.pi * d_fil ** 3 * j_fact)
    tau_adm = 0.577 * met["limite_elastique"] / securite
    fleche = 8 * effort_n * diametre_moyen ** 3 * n_spires / (gmod * d_fil ** 4 * j_fact)
    d_req = (kw * 8 * effort_n * diametre_moyen / (math.pi * tau_adm)) ** (1 / 3.0)
    v1 = Verification("helice_torsion", _niveau(tau_adm / tau, 1.0, 0.75), tau, tau_adm, "MPa",
                      "tau %.0f MPa vs %.0f admissible (F %.0f N, D moyen %.0f, d %.0f%s, Wahl %.2f) ; "
                      "d plein requis %.1f mm" % (tau, tau_adm, effort_n, diametre_moyen, d_fil,
                                                   " tube" if paroi else " plein", kw, d_req))
    v2 = Verification("helice_fleche", "ok" if fleche <= 5 else ("alerte" if fleche <= 15 else "echec"), fleche, 5.0,
                      "mm", "fleche sous genou %.1f mm (confort : <= 5 mm, alerte <= 15 mm)" % fleche)
    return [v1, v2], d_req
