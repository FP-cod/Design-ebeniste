# -*- coding: utf-8 -*-
"""Grammaire : menottes / bracelets en cuir (poignet ou cheville).

Modele A PLAT (patron de coupe) le long de +X, largeur selon Y, epaisseurs
selon +Z ; la quincaillerie est posee a son emplacement de montage au-dessus
du patron (representation simplifiee : cadres extrudes a section carree).

Implantation le long de la bande (origine = bout cote boucle) ::

    0 ........ repli ............ repli + C/2 .......... repli + C ..... L
    |  rabat   |pli (fente,     |  patte + anneau D     | trou central  | pointe
    |  boucle  | barre boucle)  |  (oppose a la boucle) | (taille)      |

- C (circonference neutre) = tour + jeu_doigt + pi x epaisseur_totale
  (fibre neutre d'un anneau d'epaisseur e : 2 pi (r + e/2) = C_int + pi e) ;
- recouvrement = repli_boucle + (n_trous - 1) / 2 x entraxe + bout_apres_dernier_trou ;
- longueur developpee L = C + recouvrement.

Couches (de la peau vers l'exterieur) : doublure, rembourrage (zones de contact,
interrompu sous la patte et loin des percages), exterieur. Couture sellier :
chemin a ``retrait_bord`` de la tranche + points de griffe au pas.
"""

import math

from .. import regles
from ..catalogues import cuirs, quincaillerie as q
from ..geometrie import (Composant, CheminCouture, Cylindre, Percage, Plan, Plaque, cercle, contour_bande,
                         contour_d, contour_o, rect_arrondi)
from ..parametres import Parametres

TYPOLOGIE = "menottes"


def cotes_bande(p):
    """Calcule toutes les cotes de la bande (mm) sans rien construire."""
    g = p.get
    w = p.largeur_bande()
    e_tot = p.epaisseur_totale()
    tour = p.tour()
    jeu = g("securite.jeu_doigt")
    c_int = tour + jeu
    c_neutre = c_int + math.pi * e_tot
    n, pas_t = int(g("ardillon.nb_trous")), g("ardillon.entraxe_trous")
    demi = (n - 1) / 2.0
    repli = g("jonctions.repli_boucle")
    x_centre = repli + c_neutre
    x_trous = [x_centre + (k - demi) * pas_t for k in range(n)]
    recouvrement = repli + demi * pas_t + g("ardillon.bout_apres_dernier_trou")
    L = c_neutre + recouvrement
    c = {
        "membre": g("produit.membre"), "taille": g("produit.taille"), "largeur": w, "tour": tour, "jeu_doigt": jeu,
        "epaisseur_totale": e_tot, "epaisseur_cuir_seul": p.epaisseur_cuir_seul(),
        "circonference_interieure": c_int, "circonference_neutre": c_neutre,
        "recouvrement": recouvrement, "longueur_developpee": L, "x_pli_boucle": repli, "x_trous": x_trous,
        "rayon_extremite": g("extremites.rayon_ratio") * w,
        "tour_mini_reglable": tour - demi * pas_t, "tour_maxi_reglable": tour + demi * pas_t,
        "points_par_cm": p.points_par_cm(),
    }
    # rivets du rabat de boucle : dans le rabat (x_f) et en vis-a-vis sur la bande (2 repli - x_f)
    c["rivets_repli"] = []
    if g("jonctions.fixation_repli") in ("rivets", "rivets_et_couture"):
        x_f = repli / 2.0 - g("ardillon.longueur_fente") / 4.0
        for x in (x_f, 2 * repli - x_f):
            c["rivets_repli"] += [(x, -w / 4.0), (x, w / 4.0)]
    # patte d'anneau
    c["rivets_patte"], c["zone_patte"] = [], None
    if g("anneau_d.present"):
        a = q.ANNEAUX[g("anneau_d.reference")]
        x_d = repli + c_neutre / 2.0
        demi_patte = g("anneau_d.longueur_patte") / 2.0
        c["x_anneau"] = x_d
        c["zone_patte"] = (x_d - demi_patte, x_d)
        centre = (x_d - demi_patte + x_d - a["fil"]) / 2.0
        er = g("anneau_d.entraxe_rivets_patte") / 2.0
        c["rivets_patte"] = [(centre - er, 0.0), (centre + er, 0.0)]
    # rembourrage : apres le rabat, avant le premier trou, interrompu sous la patte
    c["zones_rembourrage"] = []
    if dict(p.couches()).get("rembourrage"):
        m = g("cuir.marge_rembourrage")
        debut = 2 * repli + m
        fin = x_trous[0] - g("ardillon.diametre_trou") / 2.0 - m
        coupures = []
        if c["zone_patte"]:
            coupures.append((c["zone_patte"][0] - m, c["zone_patte"][1] + m))
        zones, x = [], debut
        for a0, a1 in coupures:
            if a0 > x:
                zones.append((x, min(a0, fin)))
            x = max(x, a1)
        if fin > x:
            zones.append((x, fin))
        c["zones_rembourrage"] = [z for z in zones if z[1] - z[0] > 10.0]
        c["largeur_rembourrage"] = w - 2 * (g("couture.retrait_bord") + g("cuir.retrait_rembourrage"))
    # passant : perimetre interieur autour de deux epaisseurs de bande, fibre neutre, + recouvrement de couture
    e_cs = p.epaisseur_cuir_seul()
    ep = g("sangles.epaisseur_passant")
    perim_int = 2 * (w + g("sangles.jeu_passant")) + 2 * (2 * e_cs + g("sangles.jeu_passant"))
    c["longueur_passant"] = perim_int + math.pi * ep + 10.0
    # couture
    rb = g("couture.retrait_bord")
    c["contour_couture"] = contour_bande(rb, L - rb, w - 2 * rb, max(c["rayon_extremite"] - rb, 0.0))
    return c


def _apparence_doublure(p):
    t = p.get("finition.teinte")
    dispo = cuirs.DOUBLURES[p.get("cuir.doublure_matiere")]["teintes"]
    return ("cuir", t if t in dispo else dispo[0])


def concevoir(surcharges=None, params=None):
    """Construit le ``Plan`` des menottes (aucun appel Fusion)."""
    p = params.copie() if params is not None else Parametres(surcharges)
    if params is not None and surcharges:
        p.fusionner(surcharges)
    erreurs = p.erreurs()
    if erreurs:
        raise ValueError("parametres invalides :\n" + "\n".join(map(repr, erreurs)))
    g = p.get
    c = cotes_bande(p)
    plan = Plan("menottes_%s_%s_%s" % (c["membre"], c["taille"], g("finition.teinte")), p)
    plan.cotes = c
    w, L, r = c["largeur"], c["longueur_developpee"], c["rayon_extremite"]
    teinte, metal = g("finition.teinte"), g("finition.quincaillerie")
    app_cuir, app_metal = ("cuir", teinte), ("metal", metal)

    # --- cuir : couches empilees -------------------------------------------------
    cuir = Composant("menotte_cuir")
    z = 0.0
    for nom, e in p.couches():
        if nom == "rembourrage":
            wr = c["largeur_rembourrage"]
            for i, (x0, x1) in enumerate(c["zones_rembourrage"]):
                cuir.primitives.append(Plaque("rembourrage_%d" % (i + 1), rect_arrondi(x0, x1, -wr / 2, wr / 2, 2.0),
                                              z, e, ("rembourrage", g("cuir.rembourrage_materiau")), "rembourrage"))
        else:
            cuir.primitives.append(Plaque("bande_" + nom, contour_bande(0.0, L, w, r), z, e,
                                          app_cuir if nom == "exterieur" else _apparence_doublure(p), "cuir"))
        z += e
    z_haut = z
    e_ext = g("cuir.epaisseur_exterieure")
    if g("anneau_d.present"):
        x0, x1 = c["zone_patte"]
        wp = g("anneau_d.largeur_patte")
        cuir.primitives.append(Plaque("patte_anneau_repliee", rect_arrondi(x0, x1, -wp / 2, wp / 2, min(4.0, wp / 2)),
                                      z_haut, 2 * e_ext, app_cuir, "cuir"))
    h_percage = z_haut + 2 * e_ext + 1.0
    for i, x in enumerate(c["x_trous"]):
        cuir.primitives.append(Percage("trou_ardillon_%d" % (i + 1), cercle((x, 0.0), g("ardillon.diametre_trou")),
                                       -0.5, h_percage))
    b = q.BOUCLES[g("finition.boucle")]
    lf, wf = g("ardillon.longueur_fente"), b["ardillon_diametre"] + g("tolerances.jeu_trou_ardillon")
    xr = c["x_pli_boucle"]
    cuir.primitives.append(Percage("fente_ardillon", rect_arrondi(xr - lf / 2, xr + lf / 2, -wf / 2, wf / 2, wf / 2),
                                   -0.5, h_percage))
    d_r = g("jonctions.diametre_trou_rivet")
    for i, pt in enumerate(c["rivets_repli"] + c["rivets_patte"]):
        cuir.primitives.append(Percage("trou_rivet_%d" % (i + 1), cercle(pt, d_r), -0.5, h_percage))
    cuir.primitives.append(CheminCouture("couture_perimetre", c["contour_couture"], z_haut, g("couture.pas_point")))
    if g("jonctions.fixation_repli") in ("couture", "rivets_et_couture"):
        xs = 2 * xr - 4.0
        rb = g("couture.retrait_bord")
        cuir.primitives.append(CheminCouture("couture_rabat", [("ligne", (xs, -w / 2 + rb), (xs, w / 2 - rb))],
                                             z_haut, g("couture.pas_point"), ferme=False))
    if g("anneau_d.present") and g("anneau_d.fixation_patte") == "rivets_et_couture":
        x0, x1 = c["zone_patte"]
        wp, rb = g("anneau_d.largeur_patte"), 2.5
        a = q.ANNEAUX[g("anneau_d.reference")]
        cuir.primitives.append(CheminCouture("couture_patte", rect_arrondi(x0 + rb, x1 - a["fil"] - 1.0, -wp / 2 + rb,
                                                                           wp / 2 - rb, 2.0),
                                             z_haut + 2 * e_ext, g("couture.pas_point")))
    plan.composants.append(cuir)

    # --- patrons a plat des petites pieces -----------------------------------------
    pieces = Composant("patrons_pieces")
    y0 = w / 2.0 + 20.0
    lp, wpa = c["longueur_passant"], g("sangles.largeur_passant")
    pieces.primitives.append(Plaque("passant_a_plat", rect_arrondi(0.0, lp, y0, y0 + wpa, 1.0), 0.0,
                                    g("sangles.epaisseur_passant"), app_cuir, "cuir"))
    if g("anneau_d.present"):
        y1 = y0 + wpa + 15.0
        wp = g("anneau_d.largeur_patte")
        pieces.primitives.append(Plaque("patte_a_plat", rect_arrondi(0.0, g("anneau_d.longueur_patte"), y1, y1 + wp,
                                                                     min(4.0, wp / 2)), 0.0, e_ext, app_cuir, "cuir"))
    plan.composants.append(pieces)

    # --- quincaillerie --------------------------------------------------------------
    qc = Composant("menotte_quincaillerie")
    fil_b, prof = b["cadre_fil"], b["profondeur"]
    yb = b["passage"] / 2.0 + fil_b
    qc.primitives.append(Plaque("boucle_cadre", rect_arrondi(xr - prof / 2, xr + prof / 2, -yb, yb, fil_b),
                                z_haut, fil_b, ("metal", b["metal"]), "quincaillerie",
                                trous=[rect_arrondi(xr - prof / 2 + fil_b, xr + prof / 2 - fil_b, -yb + fil_b,
                                                    yb - fil_b, 1.0)]))
    da = b["ardillon_diametre"]
    qc.primitives.append(Plaque("boucle_ardillon", rect_arrondi(xr - prof / 2, xr + prof / 2 + 4.0, -da / 2, da / 2,
                                                                da / 2), z_haut + fil_b, da, ("metal", b["metal"]),
                                "quincaillerie"))
    if g("anneau_d.present"):
        a = q.ANNEAUX[g("anneau_d.reference")]
        z_a = z_haut + 2 * e_ext
        if a["forme"] == "D":
            ext, inte = contour_d(c["x_anneau"], a["passage"], a["fil"])
        else:
            ext, inte = contour_o((c["x_anneau"] + a["passage"] / 2.0, 0.0), a["passage"], a["fil"])
        qc.primitives.append(Plaque("anneau_" + a["forme"].lower(), ext, z_a, a["fil"], ("metal", a["metal"]),
                                    "quincaillerie", trous=[inte]))
    rv = q.RIVETS[g("jonctions.rivet")]
    metal_rivet = metal if metal in rv["metaux"] else rv["metaux"][0]
    for nom, pts, haut in (("repli", c["rivets_repli"][2:], z_haut), ("patte", c["rivets_patte"], z_haut + 2 * e_ext)):
        for i, pt in enumerate(pts):
            # tetes de rivet (calottes) : sous la doublure et au-dessus de l'empilement
            qc.primitives.append(Cylindre("rivet_%s_%d_tete_bas" % (nom, i + 1), pt, rv["tete"], -1.5, 1.5,
                                          ("metal", metal_rivet)))
            qc.primitives.append(Cylindre("rivet_%s_%d_tete_haut" % (nom, i + 1), pt, rv["tete"], haut, 1.5,
                                          ("metal", metal_rivet)))
    plan.composants.append(qc)

    # --- longueurs de couture et de fil ---------------------------------------------
    coutures = plan.primitives("couture")
    c["longueur_couture"] = sum(s.longueur for s in coutures)
    c["nb_points_couture"] = sum(len(s.points) for s in coutures)
    c["longueur_fil"] = c["longueur_couture"] * g("couture.facteur_fil")

    plan.constats = regles.evaluer(p, c)
    plan.notes += [
        "Patron a plat : la bande est modelisee developpee ; la mise en forme (cintrage) est faite a l'atelier.",
        "Empilement nominal des couches (le cuir exterieur est represente plan au-dessus du rembourrage).",
        "Quincaillerie simplifiee (sections carrees) posee a son emplacement de montage ; rivets du rabat cote "
        "bande seulement.",
        "Charges de quincaillerie : estimations a verifier fournisseur (voir catalogues/quincaillerie.py).",
    ]
    return plan


def run(context):
    from ..fusion_outils import executer
    return executer(context, concevoir, TYPOLOGIE)


def stop(context):
    pass
