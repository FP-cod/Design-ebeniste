# -*- coding: utf-8 -*-
"""Grammaire couche 3 — cadres de contention modulaires.

L'aboutissant *est* la structure : montants et poutres, avec des ports
standard Vac-U-Lock et 1 pouce NPT répartis, plus des anneaux / points
M8 pour les accessoires à venir (sangles, colliers, manilles).

Typologies :
  - cadre_mural : portique ou échelle contre un mur (support de bâtiment = TODO)
  - cadre_sol   : portique autoportant (défaut) — n'exige pas le bâtiment
  - poutre_suspendue : poutre accrochée au plafond / aux solives
                      (capacité du support = TODO si inconnue)

Jonctions : tenon-mortaise, queue d'aronde, tenon à clé (ébénisterie),
ou raccords métalliques démontables.

Le module s'importe hors Fusion (aucun ``import adsk`` au niveau module).
Point d'entrée Fusion : ``run(context)``. Les dépôts de meubles ne sont
pas modifiés.
"""

from __future__ import annotations

import math
import os
import sys
import traceback

_RACINE = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _RACINE not in sys.path:
    sys.path.insert(0, _RACINE)

from common.params_globaux import Parametres, G, effort_retenue
from catalogues.materiaux import BOIS, materiau
from catalogues.jonctions_cadre import JONCTIONS, cotes_tenon, jonction
from catalogues.visserie import rapport_m8
from interfaces.port_vac_u_lock import calculer_port, longueur_arriere_hors_ergot
from common import fusion_utils as FU

TYPOLOGIES = ("cadre_mural", "cadre_sol", "poutre_suspendue")

ABOUTISSANTS_MATRICE = (
    "sex_machine_mecanique",
    "port_vac_u_lock",
    "collecteur_urine",
    "sangles",
    "colliers",
    "manilles",
    "anneaux",
)
ANCRAGES_MEUBLES_MATRICE = ("equinox", "neogothique", "incognito", "tantra", "rangement")


def _boite(nom, x, y, z, dx, dy, dz, materiau_cle, role, note=""):
    return {
        "type": "boite", "nom": nom,
        "origine": (float(x), float(y), float(z)),
        "dimensions": (float(dx), float(dy), float(dz)),
        "materiau": materiau_cle, "role": role, "note": note,
    }


def efforts_hypotheses(params=None):
    """Charges chiffrées, avec hypothèses explicites (pas des CMU certifiées).

    - Utilisateur 120 kg, g = 9,81 m/s², k_dyn = 2, CS ancrage / bois = 3,
      CS métal = 1,8, CS renversement = 1,5 (vocabulaire déjà en couche 1).
    - Effort de retenue Equinox : F_ret = k_dyn × 0,5 × m × g = 1177 N.
    - Poids entier dynamique (hypothèse pessimiste, poutre suspendue) :
      F_susp = k_dyn × m × g = 2354 N.
    - Poussée machine : 400 N (nominale validée) × k_dyn = 800 N.
    - Efforts de calcul (avec CS 3) : F × 3.
    """
    p = params if isinstance(params, Parametres) else Parametres(params or {})
    m = p.get("securite.charge_utilisateur")
    k = p.get("securite.coefficient_dynamique")
    g = p.get("unites.g") or G
    cs_bois = p.get("securite.coefficient_bois")
    cs_metal = p.get("securite.coefficient_metal")
    cs_anc = p.get("securite.coefficient_ancrage")
    cs_renv = p.get("securite.coefficient_renversement")
    poussee = p.get("securite.charge_service_poussee_machine")
    poids = m * g
    f_ret = effort_retenue(m, k, g)
    f_susp = k * m * g
    f_poussee = poussee * k
    return {
        "masse_kg": m,
        "g": g,
        "k_dyn": k,
        "cs_bois": cs_bois,
        "cs_metal": cs_metal,
        "cs_ancrage": cs_anc,
        "cs_renversement": cs_renv,
        "poids_N": poids,
        "F_retenue_N": f_ret,
        "F_suspension_N": f_susp,
        "F_poussee_dyn_N": f_poussee,
        "F_retenue_calcul_CS3_N": f_ret * cs_anc,
        "F_suspension_calcul_CS3_N": f_susp * cs_anc,
        "F_poussee_calcul_CS3_N": f_poussee * cs_anc,
        "poussee_service_N": poussee,
        "hypotheses": (
            "m=120 kg, k_dyn=2, CS ancrage=3, poussée machine nominale validée 400 N. "
            "F_retenue = k_dyn×0,5×m×g (formule Equinox déjà au vocabulaire). "
            "F_suspension = k_dyn×m×g (poids entier, hypothèse pessimiste pour une poutre suspendue). "
            "Ce ne sont pas des CMU certifiées ; essai réel obligatoire. "
            "σ_adm bois du catalogue (14 MPa frêne/chêne) est déjà une contrainte admissible "
            "d'hypothèse, distincte du CS d'ancrage : ne pas les multiplier sans le dire."
        ),
    }


def module_flexion(base_mm, hauteur_mm):
    """Module de flexion W = b h² / 6 d'une section rectangulaire (mm³)."""
    return float(base_mm) * float(hauteur_mm) ** 2 / 6.0


def contrainte_travée_simple(F_N, portee_mm, base_mm, hauteur_mm):
    """σ = M / W avec M = F L / 4 (charge concentrée en milieu de travée)."""
    M = float(F_N) * float(portee_mm) / 4.0  # N.mm
    W = module_flexion(base_mm, hauteur_mm)
    sigma = M / W if W else float("inf")
    return {"M_Nmm": M, "W_mm3": W, "sigma_mpa": sigma}


def positions_ports(longueur_utile_mm, pas_mm, marge_mm=80.0):
    """Abscisses de plots le long d'une membrure, hors zones d'assemblage."""
    L = float(longueur_utile_mm) - 2.0 * float(marge_mm)
    if L <= 0 or pas_mm <= 0:
        return []
    n = max(1, int(math.floor(L / float(pas_mm))) + 1)
    # Recaler pour rester dans [marge, longueur-marge]
    if n == 1:
        return [float(longueur_utile_mm) / 2.0]
    span = min(L, (n - 1) * float(pas_mm))
    x0 = (float(longueur_utile_mm) - span) / 2.0
    return [x0 + i * float(pas_mm) for i in range(n)]


def _verifier_flexion(p, typ, efforts, essence):
    verifs = []
    sigma_adm = materiau(essence)["contrainte_adm_flexion_mpa"]
    b = p.get("cadre_modulaire.section_poutre_base")
    h = p.get("cadre_modulaire.section_poutre_hauteur")
    if typ == "poutre_suspendue":
        L = p.get("cadre_modulaire.longueur_poutre")
        # Pessimiste : poids entier dynamique en milieu de travée.
        r = contrainte_travée_simple(efforts["F_suspension_N"], L, b, h)
        ok = r["sigma_mpa"] <= sigma_adm + 1e-9
        verifs.append({
            "nom": "flexion_poutre_suspendue",
            "ok": ok,
            "message": (
                "Poutre suspendue L=%g mm, section %g×%g, F_susp=%g N (k_dyn·m·g) : "
                "σ=%.1f MPa %s σ_adm %g MPa (%s). Hypothèse travée simple, charge au milieu. "
                "Le support de solive n'est pas vérifié (TODO)."
                % (L, b, h, efforts["F_suspension_N"], r["sigma_mpa"],
                   "<=" if ok else ">", sigma_adm, essence)
            ),
            "details": r,
        })
    else:
        L = p.get("cadre_modulaire.largeur")
        r = contrainte_travée_simple(efforts["F_retenue_N"], L, b, h)
        ok = r["sigma_mpa"] <= sigma_adm + 1e-9
        verifs.append({
            "nom": "flexion_traverse",
            "ok": ok,
            "message": (
                "Traverse L=%g mm, section %g×%g, F_ret=%g N (k_dyn×0,5×m×g) : "
                "σ=%.1f MPa %s σ_adm %g MPa (%s)."
                % (L, b, h, efforts["F_retenue_N"], r["sigma_mpa"],
                   "<=" if ok else ">", sigma_adm, essence)
            ),
            "details": r,
        })
    return verifs


def calculer_cadre(params=None, typologie=None):
    """Géométrie d'un cadre (testable hors Fusion)."""
    p = params if isinstance(params, Parametres) else Parametres(params or {})
    typ = typologie or p.get("cadre_modulaire.typologie")
    if typ not in TYPOLOGIES:
        raise ValueError("typologie de cadre inconnue : %s" % typ)
    problemes = [x for x in p.valider() if x.niveau == "erreur"]
    if problemes:
        raise ValueError("Paramètres invalides :\n" + "\n".join(str(e) for e in problemes))

    essence = p.get("cadre_modulaire.essence")
    jon_cle = p.get("cadre_modulaire.jonction")
    jon = jonction(jon_cle)
    a = p.get("cadre_modulaire.section_montant_cote")
    b = p.get("cadre_modulaire.section_poutre_base")
    h = p.get("cadre_modulaire.section_poutre_hauteur")
    largeur = p.get("cadre_modulaire.largeur")
    profondeur = p.get("cadre_modulaire.profondeur")
    hauteur = p.get("cadre_modulaire.hauteur")
    L_poutre = p.get("cadre_modulaire.longueur_poutre")
    pas = p.get("cadre_modulaire.pas_ports")
    avec_vul = bool(p.get("cadre_modulaire.ports_vac_u_lock"))
    avec_npt = bool(p.get("cadre_modulaire.ports_npt"))
    n_susp = int(p.get("cadre_modulaire.nombre_suspentes") or 2)
    efforts = efforts_hypotheses(p)
    tenon = cotes_tenon(b, a)

    solides = []
    ports = []
    jonctions = []
    notes = []
    todos = []

    def ajouter_plot_port(nom_prefixe, x, y, z, axe):
        """Plot rapporté + ergot VUL et/ou raccord NPT, sans percer la fibre tendue."""
        ep_plot = 24.0
        cote_plot = 70.0
        # Plot : petite boîte centrée sur le point.
        if axe == "z":
            solides.append(_boite(
                nom_prefixe + "plot", x - cote_plot / 2, y - cote_plot / 2, z,
                cote_plot, cote_plot, ep_plot, "inox_316", "plot_port",
                "Plot rapporté (pas un perçage de la poutre). Porte le port standard.",
            ))
            origine_vul = (x, y, z + ep_plot + 8.0 + (p.get("vac_u_lock.plug_longueur") if avec_vul else 0))
            axe_vul = "z"
        elif axe == "x":
            solides.append(_boite(
                nom_prefixe + "plot", x, y - cote_plot / 2, z - cote_plot / 2,
                ep_plot, cote_plot, cote_plot, "inox_316", "plot_port",
                "Plot rapporté (pas un perçage de la poutre).",
            ))
            origine_vul = (x + ep_plot + 8.0 + (p.get("vac_u_lock.plug_longueur") if avec_vul else 0), y, z)
            axe_vul = "x"
        else:
            solides.append(_boite(
                nom_prefixe + "plot", x - cote_plot / 2, y, z - cote_plot / 2,
                cote_plot, ep_plot, cote_plot, "inox_316", "plot_port",
                "Plot rapporté (pas un perçage de la poutre).",
            ))
            origine_vul = (x, y + ep_plot + 8.0 + (p.get("vac_u_lock.plug_longueur") if avec_vul else 0), z)
            axe_vul = "y"
        info = {"prefixe": nom_prefixe, "origine": (x, y, z), "axe": axe}
        if avec_vul:
            port = calculer_port(p, origine=origine_vul, axe=axe_vul, avec_cache=True,
                                 prefixe=nom_prefixe + "vul_")
            solides.extend(port["solides"])
            info["vac_u_lock"] = True
            info["verrouillage"] = port["verrouillage"]
        if avec_npt and not avec_vul:
            # NPT seul (si VUL déjà là, le raccord arrière du port le porte déjà).
            d = p.get("npt_1.diametre_exterieur") + 8.0
            l = p.get("npt_1.depassement_recommande")
            base = origine_vul
            solides.append({
                "type": "cylindre", "nom": nom_prefixe + "npt",
                "base": base, "axe": axe_vul, "diametre": d, "longueur": l,
                "materiau": "inox_316", "role": "npt",
                "note": "Raccord 1 pouce NPT (ASME B1.20.1), distinct du Vac-U-Lock.",
            })
            info["npt"] = True
        elif avec_npt and avec_vul:
            info["npt"] = "arriere_du_port_vul"
        ports.append(info)

    if typ == "cadre_sol":
        # Quatre montants, quatre traverses hautes formant un rectangle, deux
        # longrines basses (stabilité). Origine au sol, coin -X -Y.
        x0, y0 = 0.0, 0.0
        pieds = (
            ("av_g", x0, y0),
            ("av_d", x0 + largeur - a, y0),
            ("ar_g", x0, y0 + profondeur - a),
            ("ar_d", x0 + largeur - a, y0 + profondeur - a),
        )
        for nom, x, y in pieds:
            solides.append(_boite(
                "montant_" + nom, x, y, 0.0, a, a, hauteur, essence, "montant",
                "Montant %g×%g mm, %s. Jonction %s." % (a, a, essence, jon["nom"]),
            ))
        # Traverses hautes (fibre h verticale).
        z_tr = hauteur - h
        solides.append(_boite("traverse_haut_av", x0, y0, z_tr, largeur, b, h, essence, "poutre",
                              "Traverse avant, portée %g mm." % largeur))
        solides.append(_boite("traverse_haut_ar", x0, y0 + profondeur - b, z_tr, largeur, b, h,
                              essence, "poutre", "Traverse arrière."))
        solides.append(_boite("traverse_haut_g", x0, y0, z_tr, b, profondeur, h, essence, "poutre",
                              "Traverse gauche."))
        solides.append(_boite("traverse_haut_d", x0 + largeur - b, y0, z_tr, b, profondeur, h,
                              essence, "poutre", "Traverse droite."))
        # Longrines basses de stabilité.
        solides.append(_boite("longrine_bas_av", x0, y0, 0.0, largeur, b, h, essence, "semelle",
                              "Longrine basse, stabilité au renversement (CS %g)."
                              % efforts["cs_renversement"]))
        solides.append(_boite("longrine_bas_ar", x0, y0 + profondeur - b, 0.0, largeur, b, h,
                              essence, "semelle", "Longrine basse arrière."))
        # Ports sur la traverse avant et les montants avant (faces intérieures).
        for i, xp in enumerate(positions_ports(largeur, pas)):
            ajouter_plot_port("port_tr_av_%d_" % i, x0 + xp, y0 + b, z_tr + h / 2.0, "y")
        for i, zp in enumerate(positions_ports(hauteur, pas, marge_mm=120.0)):
            ajouter_plot_port("port_mt_av_g_%d_" % i, x0 + a, y0 + a / 2.0, zp, "x")
        notes.append(
            "Cadre au sol autoportant %g×%g×%g mm, section montants %g, poutres %g×%g, essence %s."
            % (largeur, profondeur, hauteur, a, b, h, essence)
        )
        notes.append(
            "Aucune descente de charge vers le bâtiment au-delà du plancher (charges verticales "
            "et moment de renversement repris par les longrines et, en option, par des ancrages "
            "de meuble existants — voir matrice)."
        )

    elif typ == "cadre_mural":
        # Deux montants + traverses haute et basse, contre le mur (Y=0 = mur).
        for nom, x in (("g", 0.0), ("d", largeur - a)):
            solides.append(_boite("montant_" + nom, x, 0.0, 0.0, a, a, hauteur, essence, "montant",
                                  "Montant mural %g×%g. La fixation au mur n'est pas dessinée : "
                                  "capacité du support = TODO." % (a, a)))
        z_tr = hauteur - h
        solides.append(_boite("traverse_haute", 0.0, 0.0, z_tr, largeur, b, h, essence, "poutre",
                              "Traverse haute murale, portée %g mm." % largeur))
        solides.append(_boite("traverse_basse", 0.0, 0.0, 0.0, largeur, b, h, essence, "poutre",
                              "Traverse basse (répartition vers les appuis muraux, non cotés)."))
        for i, xp in enumerate(positions_ports(largeur, pas)):
            ajouter_plot_port("port_tr_h_%d_" % i, xp, a, z_tr + h / 2.0, "y")
        for i, zp in enumerate(positions_ports(hauteur, pas, marge_mm=120.0)):
            ajouter_plot_port("port_mt_g_%d_" % i, a, a / 2.0, zp, "x")
        cap = p.get("cadre_modulaire.capacite_support_mur")
        todos.append(
            "Capacité du support mural inconnue (%s). Pas d'installation sans relevé "
            "(chevilles, ossature, béton, entraxe)." % cap
        )
        notes.append(
            "Cadre mural %g×%g mm. Discrétion meilleure qu'un portique au sol (applique au mur) "
            "mais la solidité est *gouvernée par le bâtiment*, aujourd'hui TODO."
            % (largeur, hauteur)
        )

    else:  # poutre_suspendue
        # Poutre selon X, suspentes vers +Z (plafond non dessiné).
        solides.append(_boite(
            "poutre", 0.0, 0.0, 0.0, L_poutre, b, h, essence, "poutre",
            "Poutre suspendue L=%g mm, section %g×%g. Appuis = suspentes, pas les solives "
            "(section et entraxe des solives = TODO)." % (L_poutre, b, h),
        ))
        # Suspentes également réparties.
        for i in range(n_susp):
            x = 40.0 if i == 0 else (L_poutre - 40.0 - a if i == n_susp - 1 else
                                     40.0 + i * (L_poutre - 80.0 - a) / (n_susp - 1))
            solides.append(_boite(
                "suspente_%d" % (i + 1), x, (b - a) / 2.0, h, a, a, 300.0, "inox_316", "suspente",
                "Suspente métallique (longueur d'atelier 300 mm, pas une hauteur sous plafond). "
                "Ancrage solive / plafond : capacité TODO.",
            ))
        f_par = efforts["F_suspension_N"] / float(n_susp)
        f_par_cs = efforts["F_suspension_calcul_CS3_N"] / float(n_susp)
        notes.append(
            "Descente de charge par suspente (hypothèse équipartition, F_susp=%g N, %d suspentes) : "
            "%.0f N service dynamique, %.0f N avec CS %g. À comparer à la capacité *inconnue* du support."
            % (efforts["F_suspension_N"], n_susp, f_par, f_par_cs, efforts["cs_ancrage"])
        )
        for i, xp in enumerate(positions_ports(L_poutre, pas)):
            ajouter_plot_port("port_poutre_%d_" % i, xp, b, h / 2.0, "y")
        todos.append("Capacité du support de plafond / solive inconnue — pas d'installation sans relevé.")
        todos.append("Entraxe et section des solives inconnus (cadre_modulaire.entraxe_solives, section_solive).")
        notes.append(
            "Poutre suspendue : typologie la plus discrète (une membrure) et la plus dépendante "
            "du bâtiment. Un aboutissant lourd (machine) ou un collecteur n'appartiennent pas à la poutre."
        )

    # Jonctions déclaratives (une par nœud typique).
    jonctions.append({
        "type": jon_cle,
        "nom": jon["nom"],
        "demontable": jon["demontable"],
        "discretion": jon["discretion"],
        "modularite": jon["modularite"],
        "cotes_tenon": tenon if jon_cle != "raccord_metallique" else None,
        "capacite_service_N": jon["capacite_service_N"],
        "source": jon["source"],
        "modification_meuble": False,
    })

    verifs = _verifier_flexion(p, typ, efforts, essence)
    # Support bâtiment
    if typ == "cadre_mural":
        verifs.append({
            "nom": "support_mur_connu",
            "ok": p.get("cadre_modulaire.capacite_support_mur") is not None,
            "message": "Support mural : %s" % (
                "capacité %s N" % p.get("cadre_modulaire.capacite_support_mur")
                if p.get("cadre_modulaire.capacite_support_mur") is not None
                else "TODO — inconnu, pas d'installation"
            ),
        })
    if typ == "poutre_suspendue":
        verifs.append({
            "nom": "support_plafond_connu",
            "ok": p.get("cadre_modulaire.capacite_support_plafond") is not None,
            "message": "Support plafond / solive : %s" % (
                "capacité %s N" % p.get("cadre_modulaire.capacite_support_plafond")
                if p.get("cadre_modulaire.capacite_support_plafond") is not None
                else "TODO — inconnu, pas d'installation"
            ),
        })
    verifs.append({
        "nom": "modification_meuble",
        "ok": True,
        "message": "Le cadre est un aboutissant autonome : aucun meuble Equinox / Néogothique / Incognito n'est modifié.",
    })
    if avec_vul:
        verifs.append({
            "nom": "ports_vul_presents",
            "ok": any("vac_u_lock" in pr for pr in ports),
            "message": "%d emplacement(s) de port, Vac-U-Lock demandé." % len(ports),
        })

    notes.append("Jonction %s — discrétion %s, modularité %s, démontable=%s. %s"
                 % (jon["nom"], jon["discretion"], jon["modularite"], jon["demontable"], jon["hypothese"]))
    notes.append(efforts["hypotheses"])
    notes.append(
        "Compromis typologie : le cadre au sol est le plus solide *sans* dépendre du bâtiment, "
        "le moins discret. Le cadre mural est plus plat, mais tributaire du mur (TODO). "
        "La poutre suspendue est la plus discrète et la plus critique (solives TODO, flexion, "
        "suspentes). Compromis jonction : voir catalogues.jonctions_cadre."
    )

    return {
        "params": p,
        "typologie": typ,
        "essence": essence,
        "jonction": jon,
        "cotes_tenon": tenon,
        "efforts": efforts,
        "solides": solides,
        "ports": ports,
        "jonctions": jonctions,
        "verifications": verifs,
        "notes": notes,
        "todos": todos,
        "matrice": matrice_compatibilite(),
        "modification_meuble": False,
    }


def matrice_compatibilite():
    """Matrice croisée typologies de cadre × aboutissants, et × ancrages de meubles."""
    def cell(statut, note):
        return {"statut": statut, "note": note}

    # statut : compatible | compatible_adaptateur | limite | incompatible | a_venir
    aboutissants = {
        "cadre_sol": {
            "sex_machine_mecanique": cell(
                "compatible",
                "La machine se bride sur un anneau / œillet M8 porté par le cadre (même logique "
                "qu'Equinox) ou sur un montant, sans modifier un meuble. Le châssis repose au sol "
                "dans l'emprise du cadre : meilleur cas pour la stabilité déjà juste de la machine "
                "(800 N à 700 mm). Prévoir un point d'accroche à hauteur réglable.",
            ),
            "port_vac_u_lock": cell(
                "compatible",
                "Ports natifs sur traverses et montants (plots rapportés + ergot, verrouillage collier, "
                "arrière 1 pouce NPT, cache à l'état fermé).",
            ),
            "collecteur_urine": cell(
                "compatible",
                "Caisson au sol sous / à l'arrière du portique, entonnoir ou gouttière, cuve amovible "
                "500 mL, éventuellement NPT de fond. Rien de visible si tiroir / panneau bas dans une "
                "longrine. Ne pas utiliser l'ergot Vac-U-Lock comme raccord de fluide.",
            ),
            "sangles": cell("a_venir", "Points d'accroche / anneaux sur montants et traverses (grammaire sangles à venir)."),
            "colliers": cell("a_venir", "Idem, hauteur typique cou / poignets à caler sur la hauteur du cadre (2000 mm défaut)."),
            "manilles": cell("a_venir", "Manilles sur anneaux ou inserts M8 du cadre ; CMU à caler (hyp. CS 3)."),
            "anneaux": cell(
                "compatible",
                "Anneaux DI 40 / fil Ø8 (famille Equinox, CMU catalogue 2500 N) ou œillets CMU 2000 N "
                "peuvent être portés par le cadre lui-même, sans percer un meuble.",
            ),
        },
        "cadre_mural": {
            "sex_machine_mecanique": cell(
                "limite",
                "Possible si un anneau mural est à la bonne hauteur, mais la machine développe 800 N "
                "de poussée dynamique et un moment que le mur doit reprendre (capacité murale TODO). "
                "Sans relevé du support, ne pas compter sur cette typologie pour la machine.",
            ),
            "port_vac_u_lock": cell(
                "compatible",
                "Ports natifs sur traverse haute et montants, cache affleurant — bien adapté au mur.",
            ),
            "collecteur_urine": cell(
                "limite",
                "Entonnoir déployable en pied de cadre, cuve dans un tiroir bas. Pas de gouttière sous "
                "siège (pas d'assise). Dépend d'un dégagement au sol contre le mur. Compatible en principe, "
                "moins naturel que le cadre au sol.",
            ),
            "sangles": cell("a_venir", "Ancrages muraux du cadre (à venir), sous réserve du support de bâtiment."),
            "colliers": cell("a_venir", "Idem."),
            "manilles": cell("a_venir", "Idem ; la descente de charge va au mur (TODO)."),
            "anneaux": cell(
                "compatible_adaptateur",
                "Anneaux portés par le cadre. Liaison éventuelle à un ancrage de meuble existant par "
                "adaptateur, sans modifier le meuble. Le mur reste le maillon TODO.",
            ),
        },
        "poutre_suspendue": {
            "sex_machine_mecanique": cell(
                "incompatible",
                "La machine a besoin d'un appui au sol (stabilité au renversement déjà juste, "
                "Ms/Mr faible sous 800 N à 700 mm). La suspendre à une poutre aggraverait le moment "
                "et ferait porter F_poussée + poids sur des solives non relevées. Machine au sol "
                "indépendante seulement, pas accrochée à la poutre.",
            ),
            "port_vac_u_lock": cell(
                "compatible",
                "Ports sous / sur la face de la poutre (plots). Le cache fermé préserve une certaine discrétion. "
                "La charge d'un accessoire s'ajoute à F_susp — rester dans les efforts déclarés, support TODO.",
            ),
            "collecteur_urine": cell(
                "incompatible",
                "Pas de structure au sol : le collecteur ne peut pas être « dans » la poutre. Un caisson "
                "indépendant au sol reste possible, mais ce n'est plus un aboutissant de la poutre "
                "(le traiter à part, comme un collecteur de typologie aboutissants).",
            ),
            "sangles": cell("a_venir", "Sangles / suspentes depuis la poutre ; effort renvoyé aux solives (TODO)."),
            "colliers": cell("a_venir", "Idem, hauteur sous poutre à caler (hauteur sous plafond non cotée)."),
            "manilles": cell("a_venir", "Manille sur anneau de poutre ; descente de charge vers le plafond TODO."),
            "anneaux": cell(
                "compatible",
                "Anneaux sous la poutre (famille Equinox). Capacité limitée par le *support de solive* (TODO), "
                "pas seulement par la CMU d'anneau 2500 N.",
            ),
        },
    }

    meubles = {
        "cadre_sol": {
            "equinox": cell(
                "compatible_adaptateur",
                "Le cadre est autonome. Option : le relier sans perçage à un anneau DI 40 ou un œillet "
                "de semelle (DI 12, saillie 18 mm) par une chape, pour l'immobiliser au sol. M8 côté accessoire. "
                "Les CMU catalogue (œillet 2000 N, anneau 2500 N) peuvent gouverner si on s'y ancre.",
            ),
            "neogothique": cell(
                "compatible_adaptateur",
                "Bride sur plaques 40×40×6 (x=±315, y typ. ±235 mm Entrave défaut, capacité 2000 N) "
                "sans percage. Filetage et DI d'anneau des plaques : TODO. Le cadre peut aussi rester "
                "indépendant dans le rectangle des plaques.",
            ),
            "incognito": cell(
                "limite",
                "Un portique au sol contredit la règle « rien de visible à l'état fermé ». On ne l'installe "
                "pas dans le même salon qu'une banquette Incognito si la discrétion de gamme doit tenir, "
                "sauf démontage complet. Adaptateur sur insert Ø12 (filetage TODO) possible en théorie, "
                "sans modifier le meuble, mais la présence du cadre reste visible. Pouf vibrant : hors sujet "
                "collecte ; on ne le cible pas, on ne le modifie pas.",
            ),
            "tantra": cell(
                "compatible_adaptateur",
                "Le cadre est autonome. Option : le relier sans perçage à un anneau rabattable / à épaulement "
                "vissé dans l'insert M12 (Ø ext. 16, encastrement 60 mm, 1500 N, CS 3). Filetage M12 ≠ M8 : "
                "adaptateur requis. DI et fil de l'anneau : TODO. Volet camouflable : un portique au sol "
                "n'est admissible qu'à l'état RÉVÉLÉ (comme Incognito). La typologie table inclinée n'a "
                "pas de grammaire ; sa note d'étude demande déjà une fixation au sol ou au mur.",
            ),
            "rangement": cell(
                "limite",
                "Cohabitation possible dans la pièce, sans liaison. Les inserts M8 du râtelier ne sont "
                "pas des points d'ancrage de personne : on n'y bride pas le cadre. Support mural du "
                "râtelier et du cadre : TODO s'ils partagent le même mur.",
            ),
        },
        "cadre_mural": {
            "equinox": cell(
                "compatible_adaptateur",
                "Peut cohabiter avec une typologie murale (croix de Saint-André) en s'appuyant sur des "
                "anneaux d'extrémité *sans les modifier*, ou rester un cadre indépendant fixé au mur "
                "(support mural TODO, distinct des ancrages Equinox).",
            ),
            "neogothique": cell(
                "limite",
                "L'Entrave est déjà un meuble au sol à plaques. Un cadre mural est un second dispositif ; "
                "pas de cote d'accroche murale dans la grammaire Entrave. Pas de percage du meuble.",
            ),
            "incognito": cell(
                "limite",
                "Un cadre mural apparent casse la discrétion Incognito (canapé, banquette, bibliothèque…). "
                "Une bibliothèque pourrait *masquer* un cadre (plinthe / montants) : typologie salon sans "
                "grammaire livrée, ancrages TODO. Ne pas modifier /workspace/incognito, ne pas cibler le pouf.",
            ),
            "tantra": cell(
                "limite",
                "Les typologies Tantra livrées sont des meubles au sol (sièges, canapé, desserte qui *devient* "
                "elle-même un cadre à genoux). Pas de cote d'accroche murale, hors la table inclinée non "
                "livrée (fixation murale évoquée dans la note d'étude, sans cote). Pas de perçage du meuble.",
            ),
            "rangement": cell(
                "limite",
                "Deux dispositifs muraux peuvent cohabiter (râtelier + cadre), mais on ne lie pas le cadre "
                "aux inserts M8 de crochets / ports : ce ne sont pas des ancrages de personne. Capacité "
                "du support de bâtiment TODO pour les deux. Pas de modification de /workspace/rangement.",
            ),
        },
        "poutre_suspendue": {
            "equinox": cell(
                "limite",
                "Pas d'ancrage plafond dans Equinox (œillets au sol, anneau de traverse). La poutre est un "
                "aboutissant de bâtiment, pas un accessoire du meuble. Cohabitation possible sans liaison.",
            ),
            "neogothique": cell(
                "limite",
                "Pas d'ancrage plafond relevé. Même logique : pas de liaison inventée vers les plaques au sol.",
            ),
            "incognito": cell(
                "limite",
                "Une poutre apparente sous plafond heurte la discrétion de salon, sauf si elle se fait "
                "oublier en solive habillée (hors scripts actuels). Support de plafond TODO. Pas de modification "
                "des meubles, pouf non ciblé.",
            ),
            "tantra": cell(
                "limite",
                "Pas d'ancrage plafond dans Tantra (inserts M12 dans les flasques, traverses, accoudoirs, "
                "barre haute / nez de tablette). La poutre est un aboutissant de bâtiment ; cohabitation "
                "possible sans liaison. Ne pas inventorier de point de solive.",
            ),
            "rangement": cell(
                "limite",
                "Le râtelier est mural, pas un ancrage de personne, et n'a pas de point plafond. "
                "Pas de liaison inventée vers les inserts M8 de crochets / ports.",
            ),
        },
    }

    # Complétude
    for typ in TYPOLOGIES:
        for a in ABOUTISSANTS_MATRICE:
            if a not in aboutissants[typ]:
                raise RuntimeError("matrice aboutissants incomplète : %s × %s" % (typ, a))
        for g in ANCRAGES_MEUBLES_MATRICE:
            if g not in meubles[typ]:
                raise RuntimeError("matrice meubles incomplète : %s × %s" % (typ, g))

    return {
        "aboutissants": aboutissants,
        "meubles": meubles,
        "statuts": ("compatible", "compatible_adaptateur", "limite", "incompatible", "a_venir"),
        "legende": {
            "compatible": "Usage prévu, sans adapter le meuble.",
            "compatible_adaptateur": "Usage prévu via un adaptateur rapporté, sans modifier le meuble.",
            "limite": "Possible sous conditions (support, discrétion, géométrie) ou partiellement adapté.",
            "incompatible": "Ne pas combiner (raison structurelle ou de typologie).",
            "a_venir": "Accessoire de contention non encore grammatisé ; le point d'accroche est prévu.",
        },
    }


def matrice_markdown():
    """Deux tableaux Markdown pour le rapport."""
    m = matrice_compatibilite()
    lignes = ["### Cadres × aboutissants", "",
              "| Typologie | " + " | ".join(ABOUTISSANTS_MATRICE) + " |",
              "|" + "---|" * (1 + len(ABOUTISSANTS_MATRICE))]
    for typ in TYPOLOGIES:
        cells = [typ]
        for a in ABOUTISSANTS_MATRICE:
            c = m["aboutissants"][typ][a]
            cells.append("**%s** — %s" % (c["statut"], c["note"]))
        lignes.append("| " + " | ".join(cells) + " |")
    from catalogues.compatibilite import NOMS_GAMMES
    lignes += ["", "### Cadres × ancrages de meubles", "",
               "| Typologie | " + " | ".join(NOMS_GAMMES[g] for g in ANCRAGES_MEUBLES_MATRICE) + " |",
               "|" + "---|" * (1 + len(ANCRAGES_MEUBLES_MATRICE))]
    for typ in TYPOLOGIES:
        cells = [typ]
        for g in ANCRAGES_MEUBLES_MATRICE:
            c = m["meubles"][typ][g]
            cells.append("**%s** — %s" % (c["statut"], c["note"]))
        lignes.append("| " + " | ".join(cells) + " |")
    return "\n".join(lignes)


def rapport_texte(res):
    e = res["efforts"]
    lignes = [
        "Cadre modulaire — Aboutissants",
        "Typologie %s, essence %s, jonction %s, %d solides, %d ports."
        % (res["typologie"], res["essence"], res["jonction"]["nom"],
           len(res["solides"]), len(res["ports"])),
        "Efforts (hypothèses) : F_ret=%.0f N, F_susp=%.0f N, F_poussée_dyn=%.0f N ; "
        "avec CS3 : %.0f / %.0f / %.0f N."
        % (e["F_retenue_N"], e["F_suspension_N"], e["F_poussee_dyn_N"],
           e["F_retenue_calcul_CS3_N"], e["F_suspension_calcul_CS3_N"], e["F_poussee_calcul_CS3_N"]),
        "Vérifications :",
    ]
    for v in res["verifications"]:
        lignes.append("  [%s] %s — %s" % ("ok" if v["ok"] else "KO", v["nom"], v["message"]))
    if res["todos"]:
        lignes.append("TODO :")
        lignes.extend("  - %s" % t for t in res["todos"])
    lignes.append("Notes :")
    lignes.extend("  - %s" % n for n in res["notes"])
    return "\n".join(lignes)


def construire_fusion(design, res, nom_composant="Aboutissants_cadre_modulaire"):
    import adsk.core
    import adsk.fusion
    crees, maj = res["params"].exporter_user_parameters(design)
    racine = design.rootComponent
    comp = FU.nouveau_composant(adsk.core, racine, nom_composant)
    n = 0
    for s in res["solides"]:
        if s["type"] == "boite":
            o, d = s["origine"], s["dimensions"]
            corps = FU.ajouter_boite(comp, adsk.core, adsk.fusion, s["nom"], o, d[0], d[1], d[2])
        else:
            d, L = s["diametre"], s["longueur"]
            b, ax = s["base"], s["axe"]
            if ax == "z":
                corps = FU.ajouter_boite(comp, adsk.core, adsk.fusion, s["nom"],
                                         (b[0] - d / 2, b[1] - d / 2, b[2]), d, d, L)
            elif ax == "y":
                corps = FU.ajouter_boite(comp, adsk.core, adsk.fusion, s["nom"],
                                         (b[0] - d / 2, b[1], b[2] - d / 2), d, L, d)
            else:
                corps = FU.ajouter_boite(comp, adsk.core, adsk.fusion, s["nom"],
                                         (b[0], b[1] - d / 2, b[2] - d / 2), L, d, d)
        if corps is not None:
            n += 1
    return {"composant": comp, "nb_corps": n, "user_params_crees": crees, "user_params_maj": maj}


def run(context):
    import adsk.core
    import adsk.fusion
    app = adsk.core.Application.get()
    ui = app.userInterface
    try:
        design = adsk.fusion.Design.cast(app.activeProduct)
        if not design:
            ui.messageBox("Aboutissants : ouvrir un design avant de lancer le cadre modulaire.")
            return None
        res = calculer_cadre()
        info = construire_fusion(design, res)
        ui.messageBox("Cadre modulaire (%s) : %d corps, %d ports."
                      % (res["typologie"], info["nb_corps"], len(res["ports"])))
        return res, info
    except Exception:
        ui.messageBox("Aboutissants — erreur :\n%s" % traceback.format_exc())
        return None


if __name__ == "__main__":
    print(rapport_texte(calculer_cadre()))
