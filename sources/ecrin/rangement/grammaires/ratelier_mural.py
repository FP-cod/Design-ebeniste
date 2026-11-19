# -*- coding: utf-8 -*-
"""Grammaire de demonstration : ratelier mural modulaire.

Un ratelier = N modules juxtaposes, chacun compose de :

- un panneau dorsal massif (``panneaux.epaisseur_panneau_mural``) suspendu a un
  tasseau biseaute (french cleat) + une cale basse de meme epaisseur ;
- ``nombre_barres`` barres de suspension (systeme ``systemes.barre``) portees
  par deux consoles tenonnees dans le panneau (instruments d'impact, sangles) ;
- une rangee de crochets (``systemes.crochet``) sur inserts M8 (menottes,
  paddles, colliers) ;
- une rangee de ports Aboutissants (``systemes.port``) : plot bois rapporte +
  douille 1" NPT femelle collee + ergot Vac-U-Lock visse (arriere NPT male).

Repere (mm) : X le long du mur, Y vers la piece (0 = nu du mur), Z vertical
(0 = sol). Toutes les cotes viennent des couches 1 et 2 ; les cotes propres a
la grammaire (sous-schema ``ratelier``) sont au statut ``a_valider``.
"""

import math

from ..parametres import Parametres, Param, VAL
from ..catalogues import systemes as _sys, bois as _bois, quincaillerie as _quin
from ..geometrie import Boite, Cylindre, Composant, Jonction, Plan, Verification
from .. import regles

TYPOLOGIE = "ratelier_mural"
R = (TYPOLOGIE,)

SCHEMA_RATELIER = {
    "nombre_modules": Param(2, "", "Nombre de modules juxtaposes.", (1, 6), statut=VAL, utilise_par=R,
                            justification="Demonstration : 2 x 600 mm = 1,2 m."),
    "modules_hauteur": Param(3, "", "Hauteur du panneau en modules (x modules.module_hauteur).", (1, 6),
                             statut=VAL, utilise_par=R, justification="3 x 320 = 960 mm."),
    "hauteur_pose": Param(900.0, "mm", "Hauteur du bas du panneau au sol.", (300.0, 1500.0), statut=VAL,
                          utilise_par=R, justification="Haut a 1860 mm : barres atteignables debout."),
    "tasseau_hauteur": Param(90.0, "mm", "Hauteur de chaque demi-tasseau biseaute.", (50.0, 150.0), statut=VAL,
                             utilise_par=R, justification="Proposition."),
    "tasseau_epaisseur": Param(22.0, "mm", "Epaisseur des tasseaux et de la cale basse (ecart mur / panneau).",
                               (15.0, 30.0), statut=VAL, utilise_par=R, justification="Proposition."),
    "recul_tasseau": Param(40.0, "mm", "Distance du haut du panneau au haut du tasseau.", (0.0, 200.0),
                           statut=VAL, utilise_par=R, justification="Proposition."),
    "nombre_barres": Param(2, "", "Nombre de barres de suspension par module.", (0, 4), statut=VAL, utilise_par=R,
                           justification="Proposition."),
    "hauteur_premiere_barre": Param(680.0, "mm", "Axe de la barre la plus basse depuis le bas du panneau.",
                                    (100.0, 1800.0), statut=VAL, utilise_par=R, justification="Proposition."),
    "entraxe_barres": Param(180.0, "mm", "Entraxe vertical des barres.", (60.0, 600.0), statut=VAL,
                            utilise_par=R, justification="Proposition."),
    "saillie_barre": Param(110.0, "mm", "Distance axe de barre / face du panneau.", (40.0, 250.0), statut=VAL,
                           utilise_par=R, justification="Les instruments suspendus passent devant les crochets "
                                                        "(saillie crochet + 40 mm)."),
    "console_hauteur": Param(80.0, "mm", "Hauteur des consoles de barre.", (40.0, 200.0), statut=VAL,
                             utilise_par=R, justification="Proposition."),
    "marge_console": Param(regles.MARGE_CONSOLE, "mm", "Recul des consoles par rapport au bord du module.",
                           (0.0, 100.0), statut=VAL, utilise_par=R, justification="Proposition."),
    "crochets_par_module": Param(4, "", "Nombre de crochets par module.", (0, 8), statut=VAL, utilise_par=R,
                                 justification="Proposition."),
    "hauteur_crochets": Param(400.0, "mm", "Axe de la rangee de crochets depuis le bas du panneau.",
                              (50.0, 1800.0), statut=VAL, utilise_par=R, justification="Proposition."),
    "ports_par_module": Param(2, "", "Nombre de ports Aboutissants par module (au pas ports.pas_ports).",
                              (0, 4), statut=VAL, utilise_par=R, justification="Proposition."),
    "hauteur_ports": Param(130.0, "mm", "Axe de la rangee de ports depuis le bas du panneau.", (40.0, 1800.0),
                           statut=VAL, utilise_par=R, justification="Proposition."),
    "plot_largeur": Param(70.0, "mm", "Largeur (X) et hauteur (Z) du plot bois porte-douille.", (40.0, 150.0),
                          statut=VAL, utilise_par=R, justification=">= douille O41,4 + 2 x 12 mm (regles)."),
    "plot_profondeur": Param(40.0, "mm", "Profondeur (Y) du plot porte-douille.", (20.0, 120.0), statut=VAL,
                             utilise_par=R, justification=">= L4 25 + fond 6 mm (regles)."),
}

ECART_BRANCHES = 12.0   # demi-entraxe des deux branches d'un crochet double [mm]


def preparer(params=None, overrides=None, json_utilisateur=True):
    """Parametres de typologie + sous-schema ratelier + grandeurs derivees."""
    p = params.copie() if params is not None else Parametres.pour_typologie(TYPOLOGIE, json_utilisateur=json_utilisateur)
    p.typologie = TYPOLOGIE
    p.etendre("ratelier", SCHEMA_RATELIER)
    if overrides:
        p.fusionner(overrides)
    ajust = regles.recalculer_derives(p)
    erreurs = p.erreurs()
    if erreurs:
        raise ValueError("Parametres invalides :\n" + "\n".join(str(e) for e in erreurs))
    return p, ajust


def _densite_metal(cle):
    return _quin.METAUX[cle]["densite"]


def concevoir(params=None, overrides=None, json_utilisateur=True):
    p, ajust = preparer(params, overrides, json_utilisateur)
    g = p.get
    plan = Plan(TYPOLOGIE, p)
    plan.notes += [str(a) for a in ajust]

    ess = g("bois.essence")
    rho_bois = _bois.ESSENCES[ess]["densite"]
    n_mod, L = int(g("ratelier.nombre_modules")), g("modules.module_largeur")
    H = int(g("ratelier.modules_hauteur")) * g("modules.module_hauteur")
    z0, jeu = g("ratelier.hauteur_pose"), g("discretion.jeu_mecanique")
    e_p, e_t, h_t = g("panneaux.epaisseur_panneau_mural"), g("ratelier.tasseau_epaisseur"), g("ratelier.tasseau_hauteur")
    y_face = e_t + e_p
    plan.repere.update({"hauteur_panneau": H, "y_face": y_face, "z_bas": z0})

    cle_barre, cle_crochet, cle_port = g("systemes.barre"), g("systemes.crochet"), g("systemes.port")
    geo_b, geo_c = _sys.SYSTEMES[cle_barre]["geometrie"], _sys.SYSTEMES[cle_crochet]["geometrie"]
    port_geo = _sys.SYSTEMES[cle_port]["geometrie"]
    mat_b = geo_b["materiau"]
    rho_b = rho_bois if mat_b == "bois" else _densite_metal(mat_b)
    met_c = geo_c["metal"]
    rho_c = rho_bois if met_c is None else _densite_metal(met_c)
    rho_inox = _densite_metal("inox_316")

    marge, h_cons = g("ratelier.marge_console"), g("ratelier.console_hauteur")
    saillie_b, d_b = g("ratelier.saillie_barre"), geo_b["diametre"]
    prof_cons = saillie_b + d_b / 2.0 + 20.0
    n_barres = int(g("ratelier.nombre_barres"))
    z_barres = [z0 + g("ratelier.hauteur_premiere_barre") + k * g("ratelier.entraxe_barres") for k in range(n_barres)]
    n_cro, z_cro = int(g("ratelier.crochets_par_module")), z0 + g("ratelier.hauteur_crochets")
    n_ports, z_port = int(g("ratelier.ports_par_module")), z0 + g("ratelier.hauteur_ports")
    pas = g("ports.pas_ports")
    lp, pp = g("ratelier.plot_largeur"), g("ratelier.plot_profondeur")
    l4 = g("ports.npt_longueur_totale")
    d_douille = regles.diametre_douille_npt(p)
    avec_ergot = bool(g("ports.vac_u_lock")) and port_geo.get("montage_arriere") is not None
    filete = port_geo.get("montage_arriere") == "filete_machine"
    ports_actifs = bool(n_ports) and ((filete and bool(g("ports.vac_u_lock"))) or (not filete and bool(g("ports.npt"))))
    charges_kg, moment_charges = 0.0, 0.0

    for i in range(n_mod):
        x0 = i * (L + jeu)
        x1, xc = x0 + L, x0 + L / 2.0
        pre = "module_%d_" % (i + 1)
        # -- panneau + tasseaux -------------------------------------------------
        plan.ajouter(Composant(pre + "panneau", [Boite(pre + "panneau", (xc, e_t + e_p / 2.0, z0 + H / 2.0), L, e_p, H,
                                                       ess, rho_bois)], "Panneau dorsal massif"))
        z_haut_t = z0 + H - g("ratelier.recul_tasseau")
        tas = [Boite(pre + "tasseau_panneau", (xc, e_t / 2.0, z_haut_t - h_t / 2.0), L, e_t, h_t, ess, rho_bois),
               Boite(pre + "tasseau_mural", (xc, e_t / 2.0, z_haut_t - 1.5 * h_t), L, e_t, h_t, ess, rho_bois),
               Boite(pre + "cale_basse", (xc, e_t / 2.0, z0 + h_t / 4.0), L, e_t, h_t / 2.0, ess, rho_bois)]
        plan.ajouter(Composant(pre + "tasseaux", tas, "Tasseau biseaute 45 deg (modelise droit) + cale basse"))
        plan.jonctions.append(Jonction(pre + "tasseau_mur", "tasseau_biseaute", (xc, 0.0, z_haut_t - 1.5 * h_t),
                                       (pre + "tasseau_mural", "mur"),
                                       {"angle": 45.0, "fixation_mur": "TODO (support inconnu)"}))
        # -- barres ---------------------------------------------------------------
        portee = L - 2.0 * (marge + e_p)
        for k, zb in enumerate(z_barres):
            nb = pre + "barre_%d" % (k + 1)
            prims = [Cylindre(nb, (x0 + marge, y_face + saillie_b, zb), "x", d_b, L - 2.0 * marge, mat_b, rho_b,
                              paroi=geo_b["paroi"])]
            for cote, xcons in (("G", x0 + marge + e_p / 2.0), ("D", x1 - marge - e_p / 2.0)):
                prims.append(Boite(nb + "_console_" + cote, (xcons, y_face + prof_cons / 2.0, zb), e_p, prof_cons, h_cons,
                                   ess, rho_bois))
                plan.jonctions.append(Jonction(nb + "_console_" + cote, "tenon_mortaise", (xcons, y_face, zb),
                                               (nb + "_console_" + cote, pre + "panneau"),
                                               {"epaisseur_tenon": g("jonctions.epaisseur_tenon"),
                                                "profondeur_mortaise": g("jonctions.profondeur_mortaise")}))
            plan.ajouter(Composant(nb, prims, "Barre de suspension %s sur deux consoles" % cle_barre))
            q_kg = g("charges.charge_lineaire_barre") * portee / 1000.0
            charges_kg += q_kg
            moment_charges += q_kg * (y_face + saillie_b)
        # -- crochets ---------------------------------------------------------------
        if n_cro:
            prims = []
            pe = geo_c["platine_epaisseur"] or 0.0
            for k in range(n_cro):
                xk = x0 + (k + 0.5) * L / n_cro
                nk = pre + "crochet_%d" % (k + 1)
                if geo_c["platine_diametre"]:
                    prims.append(Cylindre(nk + "_platine", (xk, y_face, z_cro), "y", geo_c["platine_diametre"], pe,
                                          met_c, rho_c))
                decal = [0.0] if geo_c["branches"] == 1 else [-ECART_BRANCHES, ECART_BRANCHES]
                for b, dx in enumerate(decal):
                    prims.append(Cylindre(nk + "_tige_%d" % (b + 1), (xk + dx, y_face + pe, z_cro), "y",
                                          geo_c["diametre_tige"], geo_c["saillie"] - pe, met_c or ess, rho_c))
                plan.jonctions.append(Jonction(nk, "insert_filete_m8" if met_c else "cheville_collee",
                                               (xk, y_face, z_cro), (nk, pre + "panneau"),
                                               {"longueur_insert": g("quincaillerie.longueur_insert"),
                                                "filetage": g("quincaillerie.filetage_insert")}))
                charges_kg += g("charges.charge_crochet")
                moment_charges += g("charges.charge_crochet") * (y_face + geo_c["saillie"])
            plan.ajouter(Composant(pre + "crochets", prims, "Rangee de crochets %s" % cle_crochet))
        # -- ports Aboutissants -------------------------------------------------------
        if ports_actifs:
            prims = []
            for k in range(n_ports):
                xp = xc + (k - (n_ports - 1) / 2.0) * pas
                npn = pre + "port_%d" % (k + 1)
                ep_e = g("ports.epaulement_epaisseur")
                if filete:
                    # ergot a tige M8 visse dans un insert du panneau : pas de plot
                    y_appui = y_face
                    plan.jonctions.append(Jonction(npn + "_insert", "insert_filete_m8", (xp, y_face, z_port),
                                                   (npn + "_ergot_vac_u_lock", pre + "panneau"),
                                                   {"filetage": g("ports.filetage_ergot"),
                                                    "longueur_insert": g("quincaillerie.longueur_insert"),
                                                    "longueur_tige": g("ports.filetage_ergot_longueur"),
                                                    "collage": "epoxy", "montage_arriere": "filete_machine"}))
                else:
                    y_appui = y_face + pp
                    prims.append(Boite(npn + "_plot", (xp, y_face + pp / 2.0, z_port), lp, pp, lp, ess, rho_bois))
                    prims.append(Cylindre(npn + "_douille_npt", (xp, y_face + pp - l4, z_port), "y", d_douille, l4,
                                          "inox_316", rho_inox, paroi=g("ports.npt_paroi_douille")))
                    plan.jonctions.append(Jonction(npn + "_plot", "tourillons", (xp, y_face, z_port),
                                                   (npn + "_plot", pre + "panneau"),
                                                   {"nombre": 2, "diametre": g("jonctions.diametre_tourillon"),
                                                    "longueur": g("jonctions.longueur_tourillon")}))
                    plan.jonctions.append(Jonction(npn + "_douille", "douille_npt_1_femelle", (xp, y_face + pp, z_port),
                                                   (npn + "_douille_npt", npn + "_plot"),
                                                   {"profondeur": l4, "diametre_percage": d_douille,
                                                    "collage": "epoxy", "ergot": avec_ergot,
                                                    "montage_arriere": g("ports.montage_arriere")}))
                if avec_ergot:
                    prims.append(Cylindre(npn + "_epaulement", (xp, y_appui, z_port), "y",
                                          g("ports.epaulement_diametre"), ep_e, "inox_316", rho_inox))
                    prims.append(Cylindre(npn + "_ergot_vac_u_lock", (xp, y_appui + ep_e, z_port), "y",
                                          g("ports.plug_diametre_tete"), g("ports.plug_longueur"), "inox_316", rho_inox))
                charges_kg += g("charges.charge_crochet")
                moment_charges += g("charges.charge_crochet") * (y_appui + 100.0)
            plan.ajouter(Composant(pre + "ports", prims, "Ports Aboutissants (%s)" % cle_port))
        if i > 0:
            plan.jonctions.append(Jonction(pre + "juxtaposition", "jeu", (x0 - jeu / 2.0, y_face, z0 + H / 2.0),
                                           ("module_%d_panneau" % i, pre + "panneau"), {"jeu": jeu}))

    _verifier(plan, p, H, z0, z_barres, z_cro, z_port, charges_kg, moment_charges, n_mod, ports_actifs, filete)
    return plan


def _verifier(plan, p, H, z0, z_barres, z_cro, z_port, charges_kg, moment_charges, n_mod, ports_actifs=True,
              filete=False):
    g = p.get
    V = plan.verifications
    geo_c = _sys.SYSTEMES[g("systemes.crochet")]["geometrie"]
    if z_barres:
        V += regles.verifier_barre(p, regles.portee_barre(p, g("ratelier.marge_console")))
        haut = max(z_barres) + g("ratelier.console_hauteur") / 2.0
        V.append(Verification("barres_dans_panneau", "ok" if haut <= z0 + H else "echec", haut - z0, H, "mm",
                              "haut de console a %.0f mm du bas du panneau (H = %.0f)" % (haut - z0, H)))
        bas_instr = min(z_barres) - g("charges.longueur_instrument_suspendu")
        devant = g("ratelier.saillie_barre") >= geo_c["saillie"] + 40.0
        masque = bas_instr < z_cro and not devant
        V.append(Verification("instruments_vs_crochets", "alerte" if masque else "ok", bas_instr - z0, z_cro - z0, "mm",
                              "instruments suspendus jusqu'a %.0f mm ; crochets a %.0f mm ; saillie barre %g vs crochet %g"
                              % (bas_instr - z0, z_cro - z0, g("ratelier.saillie_barre"), geo_c["saillie"])))
    if int(g("ratelier.crochets_par_module")):
        V += regles.verifier_crochet(p)
        entraxe = g("modules.module_largeur") / int(g("ratelier.crochets_par_module"))
        mini = (geo_c["platine_diametre"] or geo_c["diametre_tige"]) + 2.0 * ECART_BRANCHES * (geo_c["branches"] - 1) \
            + 2.0 * g("discretion.jeu_mecanique")
        V.append(Verification("entraxe_crochets", "ok" if entraxe >= mini else "echec", entraxe, mini, "mm",
                              "entraxe des crochets %.0f mm >= %.0f mm" % (entraxe, mini)))
    if ports_actifs:
        if filete:
            lp = g("ports.epaulement_diametre")
            V += regles.verifier_port_filete(p, g("panneaux.epaisseur_panneau_mural"))
        else:
            lp = g("ratelier.plot_largeur")
            V += regles.verifier_port_npt(p, g("ratelier.plot_profondeur"), lp)
        V += regles.verifier_pas_ports(p, largeur_plot=lp)
        emprise = (int(g("ratelier.ports_par_module")) - 1) * g("ports.pas_ports") + lp
        V.append(Verification("ports_dans_module", "ok" if emprise <= g("modules.module_largeur") else "echec", emprise,
                              g("modules.module_largeur"), "mm", "emprise de la rangee de ports %.0f mm" % emprise))
        ecart = z_cro - z_port
        dg = g("ports.degagement_accessoire")
        V.append(Verification("ports_vs_crochets", "ok" if ecart >= dg else "alerte", ecart, dg, "mm",
                              "ecart vertical ports / crochets %.0f mm >= degagement %g mm" % (ecart, dg)))
        V.append(Verification("ports_dans_panneau", "ok" if z_port - z0 >= lp / 2.0 else "echec", z_port - z0, lp / 2.0,
                              "mm", "plot / epaulement entierement sur le panneau"))
    # support mural (par module)
    cg, m_struct = plan.cg_structure()
    m_tot = m_struct + charges_kg
    levier = (m_struct * cg[1] + moment_charges) / m_tot
    bras = g("ratelier.modules_hauteur") * g("modules.module_hauteur") - g("ratelier.recul_tasseau") \
        - g("ratelier.tasseau_hauteur") - g("ratelier.tasseau_hauteur") / 4.0
    V += regles.verifier_support_mural(p, m_tot / n_mod, levier, bras, nom="support_mural_par_module")
    plan.repere.update({"masse_structure": m_struct, "charges_service": charges_kg})
    V += [v for v in regles.verifier_discretion_materiaux(p) if v.nom != "npt_dans_panneau"]
    V += regles.verifier_montage_port(p)
    plan.notes.append("Tasseaux modelises droits : usiner le biseau 45 deg.")
    if ports_actifs and filete:
        plan.notes.append("Ports : insert M8 x %g mm a coller a l'epoxy dans le panneau, ergot a tige %s x %g mm."
                          % (g("quincaillerie.longueur_insert"), g("ports.filetage_ergot"),
                             g("ports.filetage_ergot_longueur")))
    elif ports_actifs:
        plan.notes.append("Douilles NPT : percer O%.1f x %.1f mm dans les plots (combiner/couper dans Fusion), "
                          "coller a l'epoxy." % (regles.diametre_douille_npt(p), g("ports.npt_longueur_totale")))
    plan.notes.append("Ergot Vac-U-Lock modelise par son enveloppe (O tete x longueur) : profil reel a calibrer "
                      "sur piece (Aboutissants vac_u_lock.avertissement_calibration).")


def run(context):
    from ..fusion_outils import executer
    return executer(context, concevoir, TYPOLOGIE)


def stop(context):
    pass
