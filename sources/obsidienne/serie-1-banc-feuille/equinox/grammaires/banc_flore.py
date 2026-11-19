# -*- coding: utf-8 -*-
"""Grammaire du banc « Feuille » / « Flore » (premiere typologie Equinox).

Position d'usage : levrette dans le sens de la longueur. Repere : X = 0 au
bout ARRIERE du plateau (bassin, genoux), X croissant vers l'AVANT (epaules,
coudes) ; Y lateral (G = +Y) ; Z vertical, sol = 0.

Composants generes :

- ``plateau`` : support contreplaque + mousse/cuir, contour feuille
  (superellipse), longueur ``longueur_plateau`` ou bassin-epaules, incline ;
- ``ceinture`` : 2 longerons + 2 traverses hautes sous plateau ;
- ``pied_AR_G/D``, ``pied_AV_G/D`` : fuseaux frene, splay, galbe 'branche'
  (noeud 50 -> 40 -> noeud 50 -> extremite 30) ;
- ``capuchon_*`` : embouts laiton sous chaque pied ;
- ``traverse_arriere`` : enveloppe frene + tube inox 40x40 + lest ;
- ``helice_G/D`` : helice inox depuis un collier pivotant sur le pied
  ARRIERE, s'enroulant vers l'avant jusqu'a l'ellipse d'appui genou ;
- ``repose_genou_G/D`` : glissiere + coussin mobile ;
- ``branche_coude_G/D`` + ``repose_coude_G/D`` : bras fins type branche
  depuis les pieds avant ;
- ancrages (module ``ancrages``) : oeillets sous semelles arriere, anneau
  arriere a mi-hauteur de traverse.

Lancement Fusion : voir README (``scripts_fusion/EquinoxBancFlore``).
"""

import math

from ..calculs import (G, stabilite, verifier_flambement_rond, verifier_flexion_rond, verifier_glissement,
                       verifier_helice, verifier_poutre_rect, verifier_stabilite)
from ..catalogues.attaches import ATTACHES
from ..geometrie import (Boite, Composant, Disque, Fuseau, Jonction, Plan, PlaqueContour, TubeCarre, TubeSpline,
                         Verification, branche, contour_superellipse, distance_point_segment, fuseaux_le_long,
                         helice_elliptique, lerp, norme, rayon_courbure_min_polyligne, rotation_y, sub)
from ..parametres import Param, Parametres
from ..regles import appliquer_materiaux_actifs, capacite_lest_kg_par_m
from . import ancrages

TYPOLOGIE = "banc_flore"
VAL = "a_valider"

#: Parametres specifiques au banc Flore (sous-arbre ``flore``).
SCHEMA_FLORE = {
    "sens_inclinaison": Param("avant_bas", "texte", "'avant_bas' : bassin haut, epaules basses (classique) ; "
                              "'avant_haut' : l'inverse.", choix=["avant_bas", "avant_haut"], statut=VAL,
                              utilise_par=("banc_flore",)),
    "splay_double": Param(True, "bool", "Splay de 7 deg aussi dans le sens longitudinal (pieds AR vers l'arriere, "
                          "AV vers l'avant) : meilleure tenue a la poussee.", statut=VAL, utilise_par=("banc_flore",)),
    "cambrure_pieds": Param(15.0, "mm", "Fleche du galbe 'branche' des pieds (vers l'exterieur).", (0.0, 60.0),
                            statut=VAL, utilise_par=("banc_flore",)),
    "exposant_contour": Param(4.0, "", "Exposant de la superellipse du contour de plateau (2 = ellipse, "
                              "grand = rectangle).", (2.0, 10.0), statut=VAL, utilise_par=("banc_flore",)),
    "genou_longueur": Param(200.0, "mm", "Longueur du coussin de genou.", (120.0, 300.0), statut=VAL,
                            utilise_par=("banc_flore",)),
    "genou_largeur": Param(110.0, "mm", "Largeur du coussin de genou.", (80.0, 180.0), statut=VAL,
                           utilise_par=("banc_flore",)),
    "course_glissiere": Param(150.0, "mm", "Course des glissieres de genou.", (50.0, 300.0), statut=VAL,
                              utilise_par=("banc_flore",)),
    "hauteur_glissiere": Param(20.0, "mm", "Hauteur de la glissiere sous coussin.", (10.0, 40.0), statut=VAL,
                               utilise_par=("banc_flore",)),
    "coude_longueur": Param(220.0, "mm", "Longueur du coussin de coude.", (120.0, 320.0), statut=VAL,
                            utilise_par=("banc_flore",)),
    "coude_largeur": Param(90.0, "mm", "Largeur du coussin de coude.", (60.0, 150.0), statut=VAL,
                           utilise_par=("banc_flore",)),
    "hauteur_noeud_branche": Param(380.0, "mm", "Hauteur du noeud de depart des branches de coude sur les pieds avant.",
                                   (150.0, 600.0), statut=VAL, utilise_par=("banc_flore",)),
    "fleche_branche": Param(15.0, "mm", "Fleche (arc) des branches de coude, vers le haut.", (0.0, 120.0), statut=VAL,
                            utilise_par=("banc_flore",)),
    "helice_demi_axe_x": Param(120.0, "mm", "Demi-axe longitudinal de l'ellipse d'appui genou.", (60.0, 200.0),
                               statut=VAL, utilise_par=("banc_flore",)),
    "helice_demi_axe_y": Param(110.0, "mm", "Demi-axe lateral de l'ellipse d'appui genou.", (40.0, 160.0),
                               statut=VAL, utilise_par=("banc_flore",)),
    "jeu_helice_pied": Param(6.0, "mm", "Jeu radial entre helice et pied (collier).", (2.0, 20.0), statut=VAL,
                             utilise_par=("banc_flore",)),
    "part_plateau": Param(0.55, "", "Part du poids utilisateur sur le plateau (levrette).", (0.2, 0.9), statut=VAL,
                          utilise_par=("banc_flore",)),
    "part_genoux": Param(0.30, "", "Part du poids sur les deux genoux.", (0.05, 0.6), statut=VAL,
                         utilise_par=("banc_flore",)),
    "part_coudes": Param(0.15, "", "Part du poids sur les deux coudes.", (0.0, 0.5), statut=VAL,
                         utilise_par=("banc_flore",)),
}


def parametres_flore(params=None, overrides=None):
    p = params.copie() if params is not None else Parametres.pour_typologie(TYPOLOGIE)
    if p.meta("flore.sens_inclinaison") is None:
        p.etendre("flore", SCHEMA_FLORE)
    if overrides:
        p.fusionner(overrides)
    return p


def _interp_polyligne_z(points, z):
    """Point (x, y) d'une polyligne descendante a la hauteur z."""
    for a, b in zip(points[:-1], points[1:]):
        if (a[2] - z) * (b[2] - z) <= 0 and a[2] != b[2]:
            t = (a[2] - z) / (a[2] - b[2])
            return lerp(a, b, t), t
    return points[-1], 1.0


def _profil_pied(z_top, z_noeud2, d_n, d_mid, d_ext, z_sol=0.0):
    """Diametre le long d'un pied en fonction de z (noeud haut, noeud bas, extremite)."""
    def d(z):
        if z >= z_noeud2:
            zm = (z_top + z_noeud2) / 2.0
            if z >= zm:
                return d_mid + (d_n - d_mid) * (z - zm) / (z_top - zm)
            return d_mid + (d_n - d_mid) * (zm - z) / (zm - z_noeud2)
        return d_ext + (d_n - d_ext) * max(0.0, z - z_sol) / max(z_noeud2 - z_sol, 1e-6)
    return d


def concevoir(params=None, overrides=None):
    """Construit le ``Plan`` du banc Flore (logique pure, sans Fusion)."""
    p0 = parametres_flore(params, overrides)
    erreurs = p0.erreurs()
    if erreurs:
        raise ValueError("Parametres invalides : %s" % erreurs)
    p, ajustements = appliquer_materiaux_actifs(p0)
    g = p.get
    plan = Plan(TYPOLOGIE, p)
    plan.ajustements = ajustements

    essence = g("bois.essence")
    nuance = g("inox.nuance")
    laiton = g("laiton.nuance")
    L = p.longueur_plateau_effective()
    W = g("dimensions.largeur_plateau")
    H = g("dimensions.hauteur_assise")
    r = g("garnissage.epaisseur_rembourrage")
    es = g("garnissage.epaisseur_support")
    inc = g("garnissage.inclinaison_plateau")
    avant_bas = g("flore.sens_inclinaison") == "avant_bas"
    pivot_plateau = (0.0, 0.0, H) if avant_bas else (L, 0.0, H)
    angle = inc if avant_bas else -inc
    d_n, d_mid, d_ext = g("bois.section_noeud"), g("bois.section_entre_noeuds"), g("bois.section_extremite")
    splay = math.radians(g("bois.angle_splay"))
    paf, retrait = g("dimensions.porte_a_faux"), g("dimensions.retrait_lateral_pieds")
    lb, lh = g("bois.longeron_largeur"), g("bois.longeron_hauteur")
    d_cap, e_cap = g("laiton.diametre_capuchon"), g("laiton.epaisseur_capuchon")
    if g("dimensions.mode_longueur") == "bassin_epaules":
        plan.notes.append("Plateau raccourci a bassin-epaules : %.0f + %.0f + %.0f = %.0f mm (au lieu de %.0f)"
                          % (g("dimensions.longueur_bassin_epaules"), g("dimensions.marge_bassin"),
                             g("dimensions.marge_epaules"), L, g("dimensions.longueur_plateau")))

    def rot(pt):
        return rotation_y(pt, pivot_plateau, angle)

    # --- plateau ------------------------------------------------------------
    # hauteur de structure derivee (regles) : l'assise reste a H quel que soit le rembourrage
    hs = g("dimensions.hauteur_structure")
    contour = contour_superellipse(L, W, g("flore.exposant_contour"))
    plan.ajouter(Composant("plateau", [
        PlaqueContour("plateau_support", contour, hs, es, "contreplaque_bouleau", angle, pivot_plateau, "bois"),
        PlaqueContour("plateau_garnissage", contour, hs + es, r, "mousse_hr", angle, pivot_plateau, "garnissage"),
    ], "Plateau %s %s, %.0f x %.0f, rembourrage %.0f mm, fixation %s, bords %s"
       % (g("garnissage.materiau"), g("garnissage.couleur"), L, W, r, g("garnissage.methode_fixation"),
          g("garnissage.finition_bords"))))
    if abs(hs + es + r - H) > 0.5:
        raise ValueError("hauteur de structure incoherente avec l'assise")

    # --- ceinture (longerons + traverses hautes) -----------------------------
    yl = W / 2.0 - retrait
    z_long = hs - lh / 2.0
    x_av, x_ar = L - paf, paf
    ceinture = []
    for cote, s in (("G", 1), ("D", -1)):
        ceinture.append(Boite("longeron_" + cote, (L / 2.0, s * yl, z_long), (x_av - x_ar) + 2 * 40.0, lb, lh,
                              essence, angle, pivot_plateau))
    for nom, x in (("traverse_haute_AR", x_ar), ("traverse_haute_AV", x_av)):
        ceinture.append(Boite(nom, (x, 0.0, z_long), lb, 2 * yl - lb, lh * 0.8, essence, angle, pivot_plateau))
    plan.ajouter(Composant("ceinture", ceinture, "Ceinture sous plateau (nervure de feuille)"))

    # --- pieds -----------------------------------------------------------------
    sx = (lambda av: (1 if av else -1)) if g("flore.splay_double") else (lambda av: 0)
    pieds = {}
    for nom, x, av in (("AR", x_ar, False), ("AV", x_av, True)):
        for cote, s in (("G", 1), ("D", -1)):
            noeud = rot((x, s * yl, hs - lh))
            h = noeud[2] - e_cap
            pied = (noeud[0] + sx(av) * h * math.tan(splay), noeud[1] + s * h * math.tan(splay), e_cap)
            direction = (sx(av) * 0.5, s * 1.0, 0.0)
            axe = branche(noeud, pied, g("flore.cambrure_pieds"), direction, n=9)
            pieds["%s_%s" % (nom, cote)] = {"noeud": noeud, "pied": pied, "axe": axe, "s": s, "av": av}

    z_trav = g("traverse.hauteur_axe")
    z_noeud_bas = {"AR": z_trav, "AV": g("flore.hauteur_noeud_branche")}
    for cle, info in sorted(pieds.items()):
        z2 = z_noeud_bas[cle[:2]]
        prof = _profil_pied(info["noeud"][2], z2, d_n, d_mid, d_ext, e_cap)
        prims = []
        pts = info["axe"]
        for i in range(len(pts) - 1):
            prims.append(Fuseau("pied_%s_%d" % (cle, i + 1), pts[i], pts[i + 1], prof(pts[i][2]), prof(pts[i + 1][2]),
                                essence))
        info["profil"] = prof
        plan.ajouter(Composant("pied_" + cle, prims, "Pied frene fuseau %g->%g->%g->%g, splay %g deg"
                               % (d_n, d_mid, d_n, d_ext, g("bois.angle_splay"))))
        plan.ajouter(Composant("capuchon_" + cle, [Disque("capuchon_%s" % cle, (info["pied"][0], info["pied"][1], 0.0),
                                                          d_cap, e_cap, laiton, "laiton")],
                               "Embout laiton d%g x %g (jupe %g mm sur le bois)" % (d_cap, e_cap, g("laiton.hauteur_jupe"))))
        plan.points_appui.append((info["pied"][0], info["pied"][1]))
        plan.jonctions.append(Jonction("mortaise_%s" % cle, "tenon_mortaise", info["noeud"], ("pied_" + cle, "longeron"),
                                       {"tenon": "%g mm" % g("jonctions.epaisseur_tenon"),
                                        "profondeur": "%g mm" % g("jonctions.profondeur_mortaise"),
                                        "cheville": "tourillon d%g x %g tire-fort" % (g("jonctions.diametre_tourillon"),
                                                                                     g("jonctions.longueur_tourillon"))}))
        plan.jonctions.append(Jonction("capuchon_%s_fixation" % cle, "taraudage", info["pied"], ("pied_" + cle, "capuchon"),
                                       {"insert": "%s x %g" % (g("jonctions.filetage_insert"), g("jonctions.longueur_insert")),
                                        "colle": "epoxy", "jupe": "%g mm" % g("laiton.hauteur_jupe")}))
    for nom in ("traverse_haute_AR", "traverse_haute_AV"):
        plan.jonctions.append(Jonction(nom + "_tourillons", "tourillons", (x_ar if "AR" in nom else x_av, 0.0, z_long),
                                       (nom, "longerons"), {"nombre": 2, "diametre": g("jonctions.diametre_tourillon"),
                                                            "longueur": g("jonctions.longueur_tourillon")}))
    plan.jonctions.append(Jonction("plateau_sur_ceinture", "taraudage", (L / 2.0, 0.0, hs), ("plateau", "ceinture"),
                                   {"inserts": "6 x %s dans longerons" % g("jonctions.filetage_insert"),
                                    "demontable": True}))

    # --- traverse arriere lestee ------------------------------------------------
    pts_tr = {}
    for cote in ("G", "D"):
        pt, _ = _interp_polyligne_z(pieds["AR_" + cote]["axe"], z_trav)
        pts_tr[cote] = pt
    x_tr = (pts_tr["G"][0] + pts_tr["D"][0]) / 2.0
    y_tr = (pts_tr["G"][1] - pts_tr["D"][1]) / 2.0
    st, ct, ep_t = g("bois.section_traverse"), g("traverse.cote_tube"), g("traverse.epaisseur_paroi")
    l_tube = 2 * y_tr - 2 * (d_n / 2.0 + 10.0)
    kgpm = capacite_lest_kg_par_m(p)
    capacite = kgpm * (l_tube - 2 * 10.0) / 1000.0
    m_lest = min(g("traverse.lest_nominal"), capacite)
    l_lest = m_lest / kgpm * 1000.0
    ci = ct - 2 * ep_t
    plan.ajouter(Composant("traverse_arriere", [
        Boite("traverse_enveloppe", (x_tr, 0.0, z_trav), st, 2 * y_tr - d_n, st, essence, rayon_bord=8.0),
        TubeCarre("traverse_tube", (x_tr, -l_tube / 2.0, z_trav), (x_tr, l_tube / 2.0, z_trav), ct, ep_t, nuance),
        Boite("traverse_lest", (x_tr, 0.0, z_trav), ci, l_lest, ci, g("traverse.materiau_lest"), categorie="lest"),
    ], "Traverse arriere : frene %gx%g autour d'un tube inox %gx%gx%g, lest %s %.1f kg"
       % (st, st, ct, ct, ep_t, g("traverse.materiau_lest"), m_lest)))
    for cote in ("G", "D"):
        plan.jonctions.append(Jonction("traverse_%s" % cote, "tenon_barillet", pts_tr[cote], ("traverse_arriere", "pied_AR_" + cote),
                                       {"tenon": "%g mm" % g("jonctions.epaisseur_tenon"),
                                        "boulon": "M8 traversant le noeud, visse dans bouchon taraude soude en bout de tube",
                                        "barillet": ATTACHES["vis_barillet_m8"]["nom"]}))
    plan.repere["lest"] = (x_tr, 0.0, z_trav)
    niv = "ok" if capacite >= g("traverse.lest_min") else "echec"
    plan.verifications.append(Verification(
        "lest_integrable", niv, capacite, g("traverse.lest_min"), "kg",
        "tube %gx%g utile %.0f mm : %.2f kg/m de %s -> %.1f kg logeables (lest vise %g kg, mini %g kg). %s"
        % (ct, ct, l_tube - 20, kgpm, g("traverse.materiau_lest"), capacite, g("traverse.lest_nominal"),
           g("traverse.lest_min"),
           "" if niv == "ok" else "LEST INSUFFISANT : un tube 40x40 de %.0f mm ne loge pas 15-20 kg ; "
           "il faut ~%.0f mm de tube plein de %s (options : lest reparti dans une 2e traverse basse avant ou des "
           "longerons bas, tube 60x60, ou lest additionnel amovible)" % (l_tube, g("traverse.lest_min") / kgpm * 1000,
                                                                        g("traverse.materiau_lest")))))

    # --- ancrages ---------------------------------------------------------------
    comps, jonc, verifs = ancrages.oeillets_sous_semelles(
        p, [("AR_" + c, (pieds["AR_" + c]["pied"][0], pieds["AR_" + c]["pied"][1]), (-1.0, 0.5 * pieds["AR_" + c]["s"]))
            for c in ("G", "D")])
    comps2, jonc2, verifs2 = ancrages.anneau_traverse(p, (x_tr - st / 2.0, 0.0, z_trav), (-1.0, 0.0, 0.0))
    for c in comps + comps2:
        plan.ajouter(c)
    plan.jonctions += jonc + jonc2
    plan.verifications += verifs + verifs2

    # --- helices + repose-genoux -----------------------------------------------
    d_h = g("inox.diametre_tube_helice")
    paroi_h = g("inox.epaisseur_paroi_helice") if g("inox.section_helice") == "tube" else None
    a_h, b_h = g("flore.helice_demi_axe_x"), g("flore.helice_demi_axe_y")
    z_pad_top = g("dimensions.hauteur_appui_genoux")
    h_gl = g("flore.hauteur_glissiere")
    z_ell = z_pad_top - (r + es) - h_gl - d_h / 2.0
    zp = g("inox.hauteur_pivot")
    for cote in ("G", "D"):
        info = pieds["AR_" + cote]
        s = info["s"]
        c_dep, _ = _interp_polyligne_z(info["axe"], zp)
        r_dep = info["profil"](zp) / 2.0 + d_h / 2.0 + g("flore.jeu_helice_pied")
        c_arr = (g("dimensions.recul_genoux"), s * g("dimensions.entraxe_genoux") / 2.0, z_ell)
        # depart cote avant du collier, extremite libre pointant vers l'avant ;
        # sens d'enroulement miroir entre G et D
        pts = helice_elliptique(c_dep, c_arr, r_dep, a_h, b_h, g("inox.nombre_tours_helice"),
                                angle_depart_deg=0.0, sens=-s)
        plan.ajouter(Composant("helice_" + cote, [
            TubeSpline("helice_%s_spire" % cote, pts, d_h, nuance, paroi=paroi_h),
            Boite("helice_%s_collier" % cote, (c_dep[0], c_dep[1], zp), 2 * r_dep + d_h, 2 * r_dep + d_h, 30.0, nuance,
                  categorie="inox"),
        ], "Helice inox d%g %s, %g tours, collier pivotant %d crans" % (d_h, g("inox.section_helice"),
                                                                          g("inox.nombre_tours_helice"),
                                                                          g("inox.crans_verrouillage"))))
        plan.repere["helice_" + cote] = pts
        plan.jonctions.append(Jonction("pivot_helice_%s" % cote, "pivot_crans", (c_dep[0], c_dep[1], zp),
                                       ("pied_AR_" + cote, "helice_" + cote),
                                       {"axe": "d%g inox + bague bronze" % g("inox.diametre_axe_pivot"),
                                        "crans": g("inox.crans_verrouillage"),
                                        "angles": [i * g("inox.angle_entre_crans") for i in range(int(g("inox.crans_verrouillage")))],
                                        "indexage": "doigt a ressort M10, trous dans le collier"}))
        # glissiere posee sur l'ellipse (points avant/arriere) + coussin
        gl = Boite("glissiere_%s" % cote, (c_arr[0], c_arr[1], z_ell + d_h / 2.0 + h_gl / 2.0), 2 * a_h, 25.0, h_gl, nuance,
                   categorie="inox")
        coussin = Boite("coussin_genou_%s" % cote, (c_arr[0], c_arr[1], z_pad_top - (r + es) / 2.0),
                        g("flore.genou_longueur"), g("flore.genou_largeur"), r + es, "mousse_hr", categorie="garnissage",
                        rayon_bord=g("garnissage.rayon_bord"))
        plan.ajouter(Composant("repose_genou_" + cote, [gl, coussin],
                               "Repose-genou mobile sur glissiere, course %g mm" % g("flore.course_glissiere")))
        plan.jonctions.append(Jonction("glissiere_%s_fixation" % cote, "taraudage", (c_arr[0], c_arr[1], z_ell),
                                       ("helice_" + cote, "repose_genou_" + cote),
                                       {"brides": "2 brides inox soudees sur l'ellipse, vis M6",
                                        "indexage": "doigt pas %g mm" % ATTACHES["glissiere_inox_genou"]["pas_indexage"]}))
        # interference helice / pied
        jeu_min = float("inf")
        axe = info["axe"]
        for pt in pts[4:]:
            dmin = float("inf")
            for a_, b_ in zip(axe[:-1], axe[1:]):
                dd, t = distance_point_segment(pt, a_, b_)
                zz = a_[2] + (b_[2] - a_[2]) * t
                dmin = min(dmin, dd - info["profil"](zz) / 2.0 - d_h / 2.0)
            jeu_min = min(jeu_min, dmin)
        plan.verifications.append(Verification(
            "interference_helice_%s" % cote, "ok" if jeu_min >= 3.0 else "echec", jeu_min, 3.0, "mm",
            "jeu mini helice / pied hors collier : %.1f mm" % jeu_min))
        plan.repere["genou_" + cote] = (c_arr[0], c_arr[1], z_pad_top)

    # --- branches + repose-coudes ------------------------------------------------
    z_b = g("flore.hauteur_noeud_branche")
    for cote in ("G", "D"):
        info = pieds["AV_" + cote]
        s = info["s"]
        dep, _ = _interp_polyligne_z(info["axe"], z_b)
        z_top_coude = g("dimensions.hauteur_appui_coudes")
        bout = (L + g("dimensions.avance_coudes"), s * g("dimensions.entraxe_coudes") / 2.0, z_top_coude - (r + es) - 2.0)
        pts = branche(dep, bout, g("flore.fleche_branche"), (0.0, 0.0, 1.0), n=7)
        prims = fuseaux_le_long("branche_%s" % cote, pts, d_n, d_ext, essence)
        plan.ajouter(Composant("branche_coude_" + cote, prims, "Branche frene %g->%g" % (d_n, d_ext)))
        plan.ajouter(Composant("repose_coude_" + cote, [
            Disque("platine_coude_%s" % cote, (bout[0], bout[1], bout[2]), d_cap, g("inox.epaisseur_plaque"), nuance, "inox"),
            Boite("coussin_coude_%s" % cote, (bout[0], bout[1], z_top_coude - (r + es) / 2.0), g("flore.coude_longueur"),
                  g("flore.coude_largeur"), r + es, "mousse_hr", categorie="garnissage", rayon_bord=g("garnissage.rayon_bord")),
        ], "Repose-coude"))
        plan.jonctions.append(Jonction("branche_%s_noeud" % cote, "tenon_mortaise", dep, ("pied_AV_" + cote, "branche_coude_" + cote),
                                       {"type": "enfourchement colle", "tourillon": "d%g" % g("jonctions.diametre_tourillon")}))
        plan.jonctions.append(Jonction("coude_%s_platine" % cote, "taraudage", bout, ("branche_coude_" + cote, "repose_coude_" + cote),
                                       {"insert": g("jonctions.filetage_insert"), "platine": "%g mm" % g("inox.epaisseur_plaque")}))
        rc = rayon_courbure_min_polyligne(pts)
        plan.verifications.append(Verification("courbure_branche_%s" % cote,
                                               "ok" if rc >= g("bois.rayon_courbure_min") else "echec", rc,
                                               g("bois.rayon_courbure_min"), "mm",
                                               "rayon mini branche %.0f mm (mini %g)" % (rc, g("bois.rayon_courbure_min"))))
        plan.repere["coude_" + cote] = (bout[0], bout[1], z_top_coude)
        plan.repere["branche_" + cote] = (pts, dep, bout)
    rc_p = min(rayon_courbure_min_polyligne(i["axe"]) for i in pieds.values())
    plan.verifications.append(Verification("courbure_pieds", "ok" if rc_p >= g("bois.rayon_courbure_min") else "echec",
                                           rc_p, g("bois.rayon_courbure_min"), "mm",
                                           "rayon mini des pieds galbes %.0f mm (mini %g)" % (rc_p, g("bois.rayon_courbure_min"))))
    plan.repere["pieds"] = pieds
    plan.repere["plateau_contour"] = contour

    _verifier_mecanique(plan, pieds, L, H)
    return plan


def _verifier_mecanique(plan, pieds, L, H):
    p = plan.params
    g = p.get
    u = g("securite.charge_utilisateur")
    dyn = g("securite.coefficient_dynamique")
    essence = g("bois.essence")
    sb = g("securite.securite_bois")
    cg_s, m_s = plan.cg_structure()
    x_torse = g("dimensions.marge_bassin") + 0.45 * (L - g("dimensions.marge_bassin"))
    masses = [(m_s, cg_s), (u * g("flore.part_plateau"), (x_torse, 0.0, H + 120.0))]
    for c in ("G", "D"):
        masses.append((u * g("flore.part_genoux") / 2.0, plan.repere["genou_" + c]))
        masses.append((u * g("flore.part_coudes") / 2.0, plan.repere["coude_" + c]))
    f_long = g("securite.coefficient_horizontal_long") * u * G
    f_lat = g("securite.coefficient_horizontal_lat") * u * G
    z_bassin = H + 50.0
    forces = [("poussee_vers_avant", (f_long, 0.0), z_bassin), ("traction_vers_arriere", (-f_long, 0.0), z_bassin),
              ("lateral_G", (0.0, f_lat), H + 150.0), ("lateral_D", (0.0, -f_lat), H + 150.0)]
    st = stabilite(masses, forces, plan.points_appui, plan.repere["lest"][:2], g("securite.securite_renversement"))
    plan.stabilite = st
    plan.verifications += verifier_stabilite(st, g("securite.securite_renversement"))
    if st["lest_additionnel_kg"] > 0:
        plan.notes.append("Lest insuffisant pour la stabilite : +%.1f kg requis a la traverse arriere."
                          % st["lest_additionnel_kg"])
    plan.verifications.append(verifier_glissement(f_long, st["masse_totale"], g("securite.frottement_sol")))
    # pieds : flexion au noeud (pied encastre en tete, articule au sol), flambement
    h = pieds["AR_G"]["noeud"][2]
    plan.verifications.append(verifier_flexion_rond("pied_flexion_noeud", f_long / 4.0 * h, g("bois.section_noeud"),
                                                    essence, sb))
    plan.verifications.append(verifier_flexion_rond("pied_flexion_entre_noeuds", f_long / 4.0 * h * 0.6,
                                                    g("bois.section_entre_noeuds"), essence, sb))
    n_pied = (u * dyn + m_s) * G / 4.0 * 1.3
    plan.verifications.append(verifier_flambement_rond("pied_flambement", n_pied, g("bois.section_entre_noeuds"), h,
                                                       essence, 2.0, sb))
    # longerons
    portee = (L - 2 * g("dimensions.porte_a_faux"))
    f_longeron = g("flore.part_plateau") * u * dyn * G / 2.0
    plan.verifications.append(verifier_poutre_rect("longerons", f_longeron, portee, g("bois.longeron_largeur"),
                                                   g("bois.longeron_hauteur"), essence, sb,
                                                   g("securite.fleche_admissible")))
    # helice
    f_genou = g("flore.part_genoux") / 2.0 * u * dyn * G
    paroi = g("inox.epaisseur_paroi_helice") if g("inox.section_helice") == "tube" else None
    vh, d_req = verifier_helice(f_genou, g("flore.helice_demi_axe_x") + g("flore.helice_demi_axe_y"),
                                g("inox.diametre_tube_helice"), g("inox.nombre_tours_helice"), g("inox.nuance"),
                                g("securite.securite_metal"), paroi)
    plan.verifications += vh
    if vh[0].niveau != "ok":
        plan.notes.append(
            "Helice d%g : insuffisante comme seul support du genou (d plein requis ~%.0f mm). Options : "
            "(a) passer a d16-18 plein ; (b) garder d%g et reprendre la charge par une bequille frene sous la "
            "glissiere (l'helice devient guide + pivot) ; (c) reduire l'ellipse." % (g("inox.diametre_tube_helice"), d_req,
                                                                                   g("inox.diametre_tube_helice")))
    cap_gl = ATTACHES["glissiere_inox_genou"]["capacite_service"]
    plan.verifications.append(Verification("glissiere_genou", "ok" if cap_gl >= f_genou else "echec", f_genou, cap_gl,
                                           "N", "effort genou %.0f N vs capacite glissiere %.0f N" % (f_genou, cap_gl)))
    # branches de coude
    f_coude = g("flore.part_coudes") / 2.0 * u * dyn * G
    pts, dep, bout = plan.repere["branche_G"]
    bras = math.hypot(bout[0] - dep[0], bout[1] - dep[1])
    plan.verifications.append(verifier_flexion_rond("branche_coude_racine", f_coude * bras, g("bois.section_noeud"),
                                                    essence, sb))
    plan.verifications.append(verifier_flexion_rond("branche_coude_mi_longueur", f_coude * bras / 2.0,
                                                    (g("bois.section_noeud") + g("bois.section_extremite")) / 2.0,
                                                    essence, sb))


def run(context):
    """Point d'entree Fusion 360 (Utilitaires > Scripts et complements)."""
    from ..fusion_outils import executer
    return executer(context, concevoir, "banc_flore")


def stop(context):
    pass
