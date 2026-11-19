# -*- coding: utf-8 -*-
"""Grammaire couche 3 — machine de mouvement mécanique (Aboutissants).

Module rapporté, destiné exclusivement à des adultes consentants. Il se fixe
sur un point d'ancrage de meuble de type œillet / anneau (interface M8 côté
accessoire) par une **bride / chape**, sans percer ni modifier la structure
visible du meuble.

Transmission (cette version) : manivelle (ou pédalier / treuil) + disque à
trous d'excentricité + bielle + coulisseau sur rail linéaire. Réglage
d'amplitude par choix du trou (course = 2 × e). Réglage de hauteur par
goupille sur une colonne. L'arbre commun et une platine réservée préfigurent
la motorisation électrique ultérieure.

Cinématique (bielle-manivelle alignée, axe du coulisseau passant par l'axe
du vilebrequin) ::

    x(θ) = e · cos(θ) + √(L² − (e · sin(θ))²)

    x(0)  = e + L
    x(π)  = −e + L
    course = x(0) − x(π) = 2e     (exactement)

Un excentrique (un seul excentrique, ou deux disques) obéit à la même
formule : la course reste 2 × excentricité résultante.

Le module s'importe hors Fusion (aucun ``import adsk`` au niveau module).
Point d'entrée Fusion : ``run(context)``.

Repère : origine au sol, dans l'axe de la bride (côté meuble). X = poussée
(vers l'extérieur du meuble, croissant en s'éloignant de l'œillet), Y =
latéral, Z = vertical.
"""

from __future__ import annotations

import math
import os
import sys
import traceback

# Racine du projet (/workspace/aboutissants) sur sys.path, pour Fusion et tests.
_RACINE = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _RACINE not in sys.path:
    sys.path.insert(0, _RACINE)

from common.params_globaux import Parametres, course_depuis_excentricite, Probleme
from catalogues.visserie import rapport_m8
from common import fusion_utils as FU
from interfaces.port_vac_u_lock import adapter_sur_tige, longueur_arriere_hors_ergot


# ---------------------------------------------------------------------------
# Cinématique pure (testable sans Fusion)
# ---------------------------------------------------------------------------
def position_coulisseau(theta_rad, excentricite, longueur_bielle):
    """Abscisse x du maneton de bielle côté coulisseau (mm), origine à l'axe vilebrequin.

    Bielle-manivelle alignée : ``x = e cos θ + √(L² − (e sin θ)²)``.
    Lève ``ValueError`` si la bielle est trop courte (L ≤ |e sin θ|).
    """
    e = float(excentricite)
    L = float(longueur_bielle)
    s = math.sin(theta_rad)
    sous = L * L - (e * s) ** 2
    if sous <= 1e-12:
        raise ValueError(
            "Bielle trop courte ou position morte : L=%g, e=%g, θ=%g rad (L²−(e sin θ)²=%g)"
            % (L, e, theta_rad, sous)
        )
    return e * math.cos(theta_rad) + math.sqrt(sous)


def course_cinematique(excentricite, longueur_bielle, n=360):
    """Course numérique = max(x) − min(x) sur un tour (doit valoir 2e)."""
    xs = [
        position_coulisseau(2.0 * math.pi * i / n, excentricite, longueur_bielle)
        for i in range(n)
    ]
    return max(xs) - min(xs), min(xs), max(xs)


def hauteur_au_cran(hauteur_min, pas, cran):
    """Hauteur d'axe de tige = hauteur_min + cran × pas."""
    return float(hauteur_min) + int(cran) * float(pas)


def cran_pour_hauteur(hauteur, hauteur_min, pas, hauteur_max):
    """Cran le plus proche de ``hauteur``, borné dans la plage."""
    if pas <= 0:
        raise ValueError("pas_hauteur doit être > 0")
    cran = int(round((float(hauteur) - float(hauteur_min)) / float(pas)))
    cran_max = int(round((float(hauteur_max) - float(hauteur_min)) / float(pas)))
    return max(0, min(cran, cran_max))


# ---------------------------------------------------------------------------
# Géométrie (pavés / cylindres décrits en mm, testable hors Fusion)
# ---------------------------------------------------------------------------
def _boite(nom, x, y, z, dx, dy, dz, materiau, role, note=""):
    return {
        "type": "boite",
        "nom": nom,
        "origine": (float(x), float(y), float(z)),
        "dimensions": (float(dx), float(dy), float(dz)),
        "materiau": materiau,
        "role": role,
        "note": note,
    }


def _cylindre(nom, base, axe, diametre, longueur, materiau, role, note=""):
    return {
        "type": "cylindre",
        "nom": nom,
        "base": tuple(float(c) for c in base),
        "axe": axe,  # "x" | "y" | "z"
        "diametre": float(diametre),
        "longueur": float(longueur),
        "materiau": materiau,
        "role": role,
        "note": note,
    }


def calculer(params=None, theta_deg=0.0, cran_hauteur=None):
    """Calcule la géométrie et la cinématique à un angle et un cran donnés.

    :returns: dict avec cles ``params``, ``e``, ``L``, ``course``, ``x_coulisseau``,
              ``hauteur``, ``solides``, ``jonctions``, ``verifications``, ``notes``.
    """
    p = params if isinstance(params, Parametres) else Parametres(params or {})
    problemes = p.valider()
    erreurs = [pr for pr in problemes if pr.niveau == "erreur"]
    if erreurs:
        raise ValueError("Paramètres invalides :\n" + "\n".join(str(e) for e in erreurs))

    e = p.excentricite()
    L = p.get("mouvement.longueur_bielle")
    course = course_depuis_excentricite(e)
    theta = math.radians(theta_deg)
    x_rel = position_coulisseau(theta, e, L)  # depuis l'axe vilebrequin, vers +X

    hmin = p.get("mouvement.hauteur_min")
    hmax = p.get("mouvement.hauteur_max")
    pas_h = p.get("mouvement.pas_hauteur")
    if cran_hauteur is None:
        cran_hauteur = cran_pour_hauteur(p.get("mouvement.hauteur"), hmin, pas_h, hmax)
    hauteur = hauteur_au_cran(hmin, pas_h, cran_hauteur)
    if not (hmin - 1e-9 <= hauteur <= hmax + 1e-9):
        raise ValueError("Hauteur dérivée %g hors plage" % hauteur)

    # Layout
    long_ch = p.get("mouvement.chassis_longueur")
    larg_ch = p.get("mouvement.chassis_largeur")
    ht_ch = p.get("mouvement.chassis_hauteur_poutre")
    d_col = p.get("mouvement.diametre_colonne")
    rail_L = p.get("mouvement.rail_longueur")
    chariot_L = p.get("mouvement.longueur_chariot")
    butee = p.get("mouvement.butee_course")
    maniv_L = p.get("mouvement.manivelle_longueur")
    arbre_d = p.get("mouvement.moteur_arbre_diametre")
    arbre_L = p.get("mouvement.moteur_arbre_longueur")
    axe_petit = p.get("mouvement.bride_diametre_axe_petit_oeil")
    axe_anneau = p.get("mouvement.bride_diametre_axe_anneau")
    ouv = p.get("mouvement.bride_ouverture_chape")

    # Origine X=0 : plan de la bride (œillet). Le châssis s'étend vers +X.
    # Axe vilebrequin : au-dessus du châssis, à x_vil, z = hauteur.
    # Le rail est centré sur l'axe vilebrequin en X, pour que la course 2e tienne
    # avec butées de chaque côté.
    ep_semelle = 12.0
    x_vil = 180.0  # recul de l'axe vilebrequin par rapport à la bride
    y0 = -larg_ch / 2.0

    # x_coulisseau_abs : position de l'axe de tête de bielle (chariot).
    # x_rel vaut L+e à θ=0 (tige la plus loin) et L−e à θ=π (la plus près).
    # On oriente le coulisseau vers +X (loin du meuble).
    x_tete = x_vil + x_rel

    solides = []

    # Châssis : deux longerons + deux traverses + semelle.
    solides.append(_boite(
        "semelle_chassis", 20.0, y0, 0.0, long_ch, larg_ch, ep_semelle,
        "alu_6082_t6", "chassis",
        "Empreinte au sol : la stabilité ne repose pas sur le seul œillet.",
    ))
    for nom, y in (("longeron_g", y0), ("longeron_d", y0 + larg_ch - 30.0)):
        solides.append(_boite(
            nom, 20.0, y, ep_semelle, long_ch, 30.0, ht_ch,
            "alu_6082_t6", "chassis",
        ))
    solides.append(_boite(
        "traverse_av", 20.0, y0 + 30.0, ep_semelle, 30.0, larg_ch - 60.0, ht_ch,
        "alu_6082_t6", "chassis",
    ))
    solides.append(_boite(
        "traverse_ar", 20.0 + long_ch - 30.0, y0 + 30.0, ep_semelle, 30.0, larg_ch - 60.0, ht_ch,
        "alu_6082_t6", "chassis",
    ))
    if p.get("mouvement.lest"):
        solides.append(_boite(
            "lest", 40.0, -80.0, ep_semelle, 160.0, 160.0, 30.0,
            "inox_316", "lest",
            "Lest %g kg (paramètre), volume indicatif." % p.get("mouvement.lest"),
        ))

    # Colonne + collier de hauteur (tube, goupille).
    z_col_bas = ep_semelle + ht_ch
    h_tube = hmax + 40.0 - z_col_bas
    solides.append(_cylindre(
        "colonne", (x_vil, 0.0, z_col_bas), "z", d_col, h_tube,
        "inox_316", "hauteur",
        "Réglage de hauteur par trous au pas de %g mm, de %g à %g mm."
        % (pas_h, hmin, hmax),
    ))
    # Collier / chariot de hauteur (bague autour de la colonne).
    solides.append(_boite(
        "collier_hauteur", x_vil - 30.0, -30.0, hauteur - 30.0, 60.0, 60.0, 50.0,
        "alu_6082_t6", "hauteur",
        "Collier goupillé : cran %d, hauteur d'axe %g mm." % (cran_hauteur, hauteur),
    ))
    solides.append(_cylindre(
        "goupille_hauteur", (x_vil - 40.0, 0.0, hauteur - 5.0), "x", 8.0, 80.0,
        "inox_316", "hauteur",
        "Goupille de réglage (filetage / clip). Pas un serrage seul.",
    ))

    # Paliers + arbre commun (interface manivelle / moteur réservé).
    solides.append(_boite(
        "palier_g", x_vil - 20.0, -90.0, hauteur - 25.0, 40.0, 24.0, 50.0,
        "alu_6082_t6", "transmission",
    ))
    solides.append(_boite(
        "palier_d", x_vil - 20.0, 66.0, hauteur - 25.0, 40.0, 24.0, 50.0,
        "alu_6082_t6", "transmission",
    ))
    largeur_arbre = 90.0 + 90.0 + arbre_L
    solides.append(_cylindre(
        "arbre_commun", (x_vil, -90.0, hauteur), "y", arbre_d, largeur_arbre,
        "inox_316", "transmission",
        "Arbre commun Ø%g : manivelle aujourd'hui, moteur plus tard (TODO entraxe platine)."
        % arbre_d,
    ))

    # Disque à trous d'excentricité (dans le plan Y = −40, tourne autour de Y).
    d_disque = 2.0 * max(p.get("mouvement.trous_excentricite")) + 30.0
    solides.append(_cylindre(
        "disque_excentrique", (x_vil, -36.0, hauteur), "y", d_disque, 12.0,
        "inox_316", "amplitude",
        "Trous aux rayons %s mm → courses %s mm (course = 2×e)."
        % (p.get("mouvement.trous_excentricite"), p.courses_reglables()),
    ))
    # Maneton au trou courant.
    mx = x_vil + e * math.cos(theta)
    mz = hauteur + e * math.sin(theta)
    solides.append(_cylindre(
        "maneton", (mx, -40.0, mz), "y", 8.0, 20.0,
        "inox_316", "amplitude",
        "Maneton dans le trou e=%g mm." % e,
    ))

    # Bielle (pavé approximant l'enveloppe, de maneton à tête).
    # On place un pavé aligné X entre maneton et tête, plus une note.
    x_a, x_b = sorted((mx, x_tete))
    solides.append(_boite(
        "bielle", x_a - 8.0, -18.0, min(mz, hauteur) - 8.0,
        (x_b - x_a) + 16.0, 16.0, abs(mz - hauteur) + 16.0,
        "inox_316", "transmission",
        "Bielle L=%g mm, enveloppe à θ=%g° (géométrie Fusion à raffiner en barre)."
        % (L, theta_deg),
    ))

    # Rail + butées + chariot + tige de sortie.
    rail_x0 = x_vil + L - p.get("mouvement.course_max") / 2.0 - butee
    solides.append(_boite(
        "rail", rail_x0, -20.0, hauteur - 18.0, rail_L, 40.0, 16.0,
        "inox_316", "guidage",
        "Longueur utile %g mm ≥ course_max + chariot + 2 butées." % rail_L,
    ))
    solides.append(_boite(
        "butee_proche", rail_x0, -20.0, hauteur - 18.0, butee, 40.0, 22.0,
        "alu_6082_t6", "securite",
        "Butée de fin de course (côté meuble).",
    ))
    solides.append(_boite(
        "butee_loin", rail_x0 + rail_L - butee, -20.0, hauteur - 18.0, butee, 40.0, 22.0,
        "alu_6082_t6", "securite",
        "Butée de fin de course (côté tige).",
    ))
    solides.append(_boite(
        "chariot", x_tete - chariot_L / 2.0, -22.0, hauteur - 8.0, chariot_L, 44.0, 28.0,
        "alu_6082_t6", "guidage",
    ))
    tige_L = 180.0
    solides.append(_cylindre(
        "tige_sortie", (x_tete, 0.0, hauteur), "x", 16.0, tige_L,
        "inox_316", "sortie",
        "Tige de sortie (contact éventuel : inox 316, arêtes ≥ rayon min peau, démontable pour nettoyage).",
    ))

    # Port Vac-U-Lock en bout de tige : l'ergot se visse (filetage côté machine,
    # défaut M8x1.25, cohérent Equinox) dans la tige Ø16. Sans modifier le meuble.
    # Le NPT 1 pouce n'est plus le montage arrière par défaut (option filete_et_npt).
    L_vul = p.get("vac_u_lock.plug_longueur")
    l_arriere_vul = longueur_arriere_hors_ergot(p)
    l_fil = p.get("vac_u_lock.filetage_cote_machine_longueur")
    solides.append(_cylindre(
        "raccord_filete_tige_vul",
        (x_tete + tige_L - l_fil, 0.0, hauteur), "x", 16.0, l_fil + 4.0,
        "inox_316", "interface",
        "Embout de tige Ø16, taraudé %s pour recevoir la tige filetée de l'ergot "
        "(marché : le Vac-U-Lock se visse, vaculocks.com). Pas un raccord 1 pouce NPT."
        % p.get("vac_u_lock.filetage_cote_machine"),
    ))
    origine_pointe_vul = (
        x_tete + tige_L + l_arriere_vul + L_vul,
        0.0,
        hauteur,
    )
    port_vul = adapter_sur_tige(p, origine_pointe_vul, axe="x", prefixe="vul_")
    solides.extend(port_vul["solides"])

    # Manivelle (côté +Y de l'arbre) + poignée.
    # Position angulaire : même θ, bras opposé ou identique — on met le bras selon θ.
    hx = x_vil + maniv_L * math.cos(theta)
    hz = hauteur + maniv_L * math.sin(theta)
    solides.append(_boite(
        "manivelle", min(x_vil, hx) - 6.0, 90.0, min(hauteur, hz) - 6.0,
        abs(hx - x_vil) + 12.0, 10.0, abs(hz - hauteur) + 12.0,
        "inox_316", "entrainement",
        "Manivelle %g mm. Débrayage par goupille sur l'arbre : %s."
        % (maniv_L, "oui" if p.get("mouvement.debrayage") else "NON — à corriger"),
    ))
    solides.append(_cylindre(
        "poignee", (hx, 90.0, hz), "y", 25.0, 80.0,
        "laiton_cw510l", "entrainement",
        "Poignée (laiton sans plomb ou inox), rayon d'arêtes à respecter.",
    ))
    if p.get("mouvement.debrayage"):
        solides.append(_cylindre(
            "goupille_debrayage", (x_vil - 6.0, 80.0, hauteur), "x", 4.0, 20.0,
            "inox_316", "securite",
            "Goupille d'arrêt d'urgence / débrayage : retire la manivelle de l'arbre.",
        ))

    # Platine moteur réservée (face en +Y, rien de monté).
    solides.append(_boite(
        "platine_moteur_reservee", x_vil - 40.0, 90.0 + arbre_L, hauteur - 40.0,
        80.0, 8.0, 80.0,
        "alu_6082_t6", "interface_moteur",
        "Platine d'adaptation future. Entraxe des vis : TODO (moteur non choisi). "
        "Filetage hypothèse %s, %s vis."
        % (p.get("mouvement.moteur_filetage_bride"), p.get("mouvement.moteur_nombre_vis")),
    ))

    # Bride / chape sur l'œillet existant, SANS modifier le meuble.
    # Deux joues + axe (on fournit les deux axes possibles, le petit est monté par défaut).
    solides.append(_boite(
        "bride_joue_g", -12.0, -ouv / 2.0 - 8.0, 8.0, 24.0, 8.0, 40.0,
        "inox_316", "fixation_meuble",
        "Joue de chape : enserrer l'œil existant, aucun perçage du meuble.",
    ))
    solides.append(_boite(
        "bride_joue_d", -12.0, ouv / 2.0, 8.0, 24.0, 8.0, 40.0,
        "inox_316", "fixation_meuble",
    ))
    solides.append(_boite(
        "bride_dos", 8.0, -ouv / 2.0 - 8.0, 8.0, 16.0, ouv + 16.0, 40.0,
        "inox_316", "fixation_meuble",
        "Dos de chape, serré par vis M8, relie la bride au châssis.",
    ))
    solides.append(_cylindre(
        "axe_bride_petit_oeil", (0.0, -ouv / 2.0 - 10.0, 28.0), "y",
        axe_petit, ouv + 20.0,
        "inox_316", "fixation_meuble",
        "Axe Ø%g pour œillet bas Equinox (DI 12 mm). Charge << M8 : voir rapport de sécurité."
        % axe_petit,
    ))
    solides.append(_cylindre(
        "axe_bride_anneau_reserve", (0.0, -ouv / 2.0 - 10.0, 28.0), "y",
        axe_anneau, ouv + 20.0,
        "inox_316", "fixation_meuble",
        "Axe alternatif Ø%g pour anneau Equinox DI 40 mm (préférer cet accrochage).",
    ))
    # Vis M8 de serrage de la chape (interface normalisée).
    solides.append(_cylindre(
        "vis_serre_bride_m8", (16.0, -ouv / 2.0 - 12.0, 20.0), "y", 8.0, ouv + 24.0,
        "inox_316", "fixation_meuble",
        "Vis de serrage M8 (interface normalisée Aboutissants).",
    ))
    # Bras de liaison bride → châssis (ne perce pas le meuble).
    solides.append(_boite(
        "bras_liaison_bride", 16.0, -20.0, 10.0, 80.0, 40.0, 24.0,
        "inox_316", "fixation_meuble",
        "Liaison bride–châssis. Le meuble n'est pas modifié.",
    ))

    jonctions = [
        {
            "nom": "bride_sur_oeillet_meuble",
            "type": "chape_axe",
            "pieces": ("bride", "oeillet_ou_anneau_existant"),
            "details": {
                "filetage_serrage": p.get("interface_oeillet_m8.filetage"),
                "modification_meuble": False,
                "axe_petit_oeil_mm": axe_petit,
                "axe_anneau_mm": axe_anneau,
                "jeu_mm": p.get("interface_oeillet_m8.jeu_fixation_bride"),
                "note": "Clamp uniquement. Pas de perçage, pas d'insert ajouté, pas de modification visible.",
            },
        },
        {
            "nom": "maneton_trou_excentrique",
            "type": "axe_goupille",
            "pieces": ("disque_excentrique", "bielle"),
            "details": {"e_mm": e, "course_mm": course, "formule": "course = 2 * e"},
        },
        {
            "nom": "collier_colonne",
            "type": "goupille",
            "pieces": ("colonne", "collier_hauteur"),
            "details": {"cran": cran_hauteur, "pas_mm": pas_h, "hauteur_mm": hauteur},
        },
        {
            "nom": "debrayage_manivelle",
            "type": "goupille_arbre",
            "pieces": ("arbre_commun", "manivelle"),
            "details": {"present": bool(p.get("mouvement.debrayage")), "arbre_mm": arbre_d},
        },
        {
            "nom": "platine_moteur_future",
            "type": "bride_moteur_reservee",
            "pieces": ("platine_moteur_reservee", "arbre_commun"),
            "details": {
                "entraxe": p.get("mouvement.moteur_entraxe_fixation"),
                "filetage": p.get("mouvement.moteur_filetage_bride"),
                "todo": "entraxe et couple nominal non choisis",
            },
        },
        {
            "nom": "port_vac_u_lock_bout_de_tige",
            "type": "ergot_vac_u_lock",
            "pieces": ("tige_sortie", "raccord_filete_tige_vul", "vul_ergot_enveloppe_tete"),
            "details": {
                "modification_meuble": False,
                "origine_pointe_mm": origine_pointe_vul,
                "verrouillage": port_vul["verrouillage"],
                "montage_arriere": p.get("vac_u_lock.montage_arriere"),
                "filetage_cote_machine": p.get("vac_u_lock.filetage_cote_machine"),
            },
        },
    ]

    verifications = _verifier(p, course, e, L, hauteur, x_tete, rail_x0, rail_L, chariot_L, butee, problemes)

    notes = [
        "Formule d'amplitude : course = 2 × excentricité (bielle-manivelle alignée ou excentrique).",
        "x(θ) = e cos θ + √(L² − (e sin θ)²) ; course = x(0) − x(π) = 2e (exact).",
        "Réglage d'amplitude : trous e = %s mm → courses %s mm."
        % (p.get("mouvement.trous_excentricite"), p.courses_reglables()),
        "Réglage de hauteur : cran %d, h = %g + cran × %g = %g mm."
        % (cran_hauteur, hmin, pas_h, hauteur),
        "Fixation meuble : bride/chape sur œillet ou anneau existant, sans modifier la structure visible.",
        "Interface moteur réservée (arbre Ø%g, platine, entraxe TODO)." % arbre_d,
        "Les charges et CMU de vis sont des hypothèses (catalogues.visserie) : essai réel obligatoire.",
        "Port Vac-U-Lock en bout de tige (ergot L=%g mm, variante tête %s, Ø %g mm), "
        "filetage côté machine %s, arrière %s, verrouillage %s. "
        "Vide théorique max ≈ %.0f N << 800 N (poussée nominale validée 400 N × k_dyn 2) ; "
        "le collier reste requis. Deux Ø de tête paramétrés + cales d'ajustement "
        "(on ne tranche pas). Forme étoilée / cône / Ø milieu : TODO."
        % (L_vul, p.get("vac_u_lock.variante_tete"), p.get("vac_u_lock.plug_diametre_tete_max"),
           p.get("vac_u_lock.filetage_cote_machine"),
           p.get("vac_u_lock.montage_arriere"), port_vul["verrouillage"],
           port_vul["arrachement"]["vide_theorique_max_N"]),
    ]

    return {
        "params": p,
        "e": e,
        "L": L,
        "course": course,
        "theta_deg": theta_deg,
        "x_relatif": x_rel,
        "x_tete": x_tete,
        "x_vilebrequin": x_vil,
        "hauteur": hauteur,
        "cran_hauteur": cran_hauteur,
        "solides": solides,
        "jonctions": jonctions,
        "verifications": verifications,
        "notes": notes,
        "problemes_params": problemes,
        "port_vac_u_lock": port_vul,
        "origine_pointe_vul": origine_pointe_vul,
    }


def _verifier(p, course, e, L, hauteur, x_tete, rail_x0, rail_L, chariot_L, butee, problemes):
    verifs = []

    def add(nom, ok, message, niveau="ok"):
        verifs.append({"nom": nom, "ok": bool(ok), "niveau": "ok" if ok and niveau == "ok" else (niveau if not ok else niveau),
                       "message": message})

    course_num, xmin, xmax = course_cinematique(e, L)
    add("course_egale_2e",
        abs(course_num - 2.0 * e) < 0.05,
        "Course cinématique %.3f mm vs 2e = %.3f mm (θ parcours 360°)." % (course_num, 2.0 * e))

    add("bielle_plus_longue_que_e",
        L > e,
        "L=%g mm, e=%g mm (L/e=%.2f)." % (L, e, L / e if e else float("inf")))

    # Le chariot reste entre les butées sur tout le tour.
    xs = [p.get("mouvement.x_vilebrequin", 180.0) + position_coulisseau(2 * math.pi * i / 72, e, L)
          for i in range(72)]
    # x_vilebrequin is not a param - use 180 as in calculer
    x_vil = 180.0
    xs = [x_vil + position_coulisseau(2 * math.pi * i / 72, e, L) for i in range(72)]
    x_ch_min = min(xs) - chariot_L / 2.0
    x_ch_max = max(xs) + chariot_L / 2.0
    limite_p = rail_x0 + butee
    limite_l = rail_x0 + rail_L - butee
    ok_but = (x_ch_min + 1e-6 >= limite_p) and (x_ch_max - 1e-6 <= limite_l)
    add("chariot_dans_butees",
        ok_but,
        "Chariot parcours [%g, %g] mm, butées intérieures [%g, %g] mm."
        % (x_ch_min, x_ch_max, limite_p, limite_l),
        niveau="erreur" if not ok_but else "ok")

    # Charge poussée vs CMU meuble / vis
    f = p.get("securite.charge_service_poussee_machine") * p.get("securite.coefficient_dynamique")
    cmu_oeil = p.get("securite.eq_cmu_oeillet")
    add("poussee_vs_cmu_oeillet",
        f <= cmu_oeil,
        "Effort de calcul poussée × k_dyn = %.0f N vs CMU catalogue œillet Equinox %.0f N. "
        "La bride ne doit reprendre cet effort que si le châssis est calé au sol ; "
        "sinon réduire la charge ou accrocher l'anneau (CMU 2500 N)." % (f, cmu_oeil),
        niveau="alerte" if f > cmu_oeil else "ok")

    r = rapport_m8(p.get("securite.coefficient_ancrage"), "A4-70")
    add("vis_m8_traction",
        f <= r["traction_admissible_N"],
        "Effort %.0f N vs CMU calcul M8 A4-70 traction %.0f N (CS=%g, hypothèses norme). "
        "La limite meuble (2000 N œillet) reste déterminante."
        % (f, r["traction_admissible_N"], r["coefficient_securite"]))

    f_axe6 = r["axe6_cisaillement_fut_admissible_N"]
    add("axe_petit_oeil_cisaillement",
        f <= f_axe6,
        "Axe Ø6 dans l'œillet bas : CMU cisaillement fût A4-70 / CS3 ≈ %.0f N (hypothèse). "
        "Effort de calcul %.0f N. Préférer l'anneau DI 40 + axe Ø10."
        % (f_axe6, f),
        niveau="alerte" if f > f_axe6 * 0.8 else "ok")

    # Stabilité sommaire : moment poussée horizontale à `hauteur` vs poids × demi-longueur
    poids = 15.0 * 9.81 + p.get("mouvement.lest") * 9.81  # 15 kg hypothèse masse propre
    ms = poids * (p.get("mouvement.chassis_longueur") / 2.0) / 1000.0  # N.m
    mr = f * (hauteur / 1000.0)
    ratio = (ms / mr) if mr else float("inf")
    cs_renv = p.get("securite.coefficient_renversement")
    add("renversement_chassis",
        ratio >= cs_renv,
        "Ms/Mr = %.2f (cible ≥ %g). Masse propre hypothèse 15 kg + lest %g kg, "
        "poussée de calcul %.0f N à %g mm. Sans la bride et sans essai, c'est indicatif."
        % (ratio, cs_renv, p.get("mouvement.lest"), f, hauteur),
        niveau="alerte" if ratio < cs_renv else "ok")

    add("debrayage_present",
        bool(p.get("mouvement.debrayage")),
        "Débrayage / goupille de manivelle : %s." % (
            "présent" if p.get("mouvement.debrayage") else "ABSENT — ajouter un arrêt d'urgence mécanique"),
        niveau="erreur" if not p.get("mouvement.debrayage") else "ok")

    n_err = sum(1 for pr in problemes if pr.niveau == "erreur")
    add("params_sans_erreur",
        n_err == 0,
        "%d alerte(s), %d todo(s) dans les paramètres (les erreurs auraient déjà levé une exception)."
        % (sum(1 for pr in problemes if pr.niveau == "alerte"),
           sum(1 for pr in problemes if pr.niveau == "todo")))

    return verifs


def rapport_texte(res):
    """Rapport lisible (cinématique, pièces, vérifs)."""
    lignes = [
        "Machine de mouvement mécanique — Aboutissants",
        "course = 2 × e = 2 × %g = %g mm ; L bielle = %g mm ; θ = %g° ; x_tete = %.1f mm"
        % (res["e"], res["course"], res["L"], res["theta_deg"], res["x_tete"]),
        "hauteur d'axe = %g mm (cran %d)" % (res["hauteur"], res["cran_hauteur"]),
        "",
        "Solides (%d) :" % len(res["solides"]),
    ]
    for s in res["solides"]:
        lignes.append("  - %s [%s / %s] %s" % (s["nom"], s["type"], s["materiau"], s.get("note") or s["role"]))
    lignes.append("\nJonctions :")
    for j in res["jonctions"]:
        lignes.append("  - %s [%s] %s" % (j["nom"], j["type"], j["details"]))
    lignes.append("\nVérifications :")
    for v in res["verifications"]:
        marque = "OK" if v["ok"] else v["niveau"].upper()
        lignes.append("  - [%s] %s : %s" % (marque, v["nom"], v["message"]))
    lignes.append("\nNotes :")
    lignes.extend("  - %s" % n for n in res["notes"])
    return "\n".join(lignes)


# ---------------------------------------------------------------------------
# Point d'entrée Fusion
# ---------------------------------------------------------------------------
def construire_fusion(design, res, nom_composant="Aboutissants_sex_machine_mecanique"):
    """Construit les pavés dans ``design`` et exporte les User Parameters."""
    core = __import__("adsk.core", fromlist=["core"]).core if False else None
    import adsk.core
    import adsk.fusion

    crees, maj = res["params"].exporter_user_parameters(design)
    racine = design.rootComponent
    comp = FU.nouveau_composant(adsk.core, racine, nom_composant)
    n = 0
    for s in res["solides"]:
        if s["type"] != "boite":
            # Cylindres : approximés par leur boîte enveloppante pour cette version.
            if s["axe"] == "z":
                d, L = s["diametre"], s["longueur"]
                ox, oy, oz = s["base"][0] - d / 2.0, s["base"][1] - d / 2.0, s["base"][2]
                corps = FU.ajouter_boite(comp, adsk.core, adsk.fusion, s["nom"], (ox, oy, oz), d, d, L)
            elif s["axe"] == "y":
                d, L = s["diametre"], s["longueur"]
                ox = s["base"][0] - d / 2.0
                oy = s["base"][1]
                oz = s["base"][2] - d / 2.0
                corps = FU.ajouter_boite(comp, adsk.core, adsk.fusion, s["nom"], (ox, oy, oz), d, L, d)
            else:  # x
                d, L = s["diametre"], s["longueur"]
                ox, oy, oz = s["base"][0], s["base"][1] - d / 2.0, s["base"][2] - d / 2.0
                corps = FU.ajouter_boite(comp, adsk.core, adsk.fusion, s["nom"], (ox, oy, oz), L, d, d)
        else:
            o, dim = s["origine"], s["dimensions"]
            corps = FU.ajouter_boite(comp, adsk.core, adsk.fusion, s["nom"], o, dim[0], dim[1], dim[2])
        if corps is not None:
            n += 1
    return {"composant": comp, "nb_corps": n, "user_params_crees": crees, "user_params_maj": maj}


def run(context):
    """Point d'entrée script Fusion 360."""
    import adsk.core
    import adsk.fusion

    app = adsk.core.Application.get()
    ui = app.userInterface
    try:
        design = adsk.fusion.Design.cast(app.activeProduct)
        if not design:
            ui.messageBox(
                "Aboutissants : ouvrir un design (espace Design) avant de lancer "
                "la machine de mouvement mécanique."
            )
            return None
        try:
            design.designType = adsk.fusion.DesignTypes.ParametricDesignType
        except Exception:
            pass
        res = calculer()
        info = construire_fusion(design, res)
        texte = rapport_texte(res)
        chemin = "(non écrit)"
        try:
            chemin = os.path.join(os.path.expanduser("~"), "aboutissants_rapport_sex_machine_mecanique.txt")
            with open(chemin, "w", encoding="utf-8") as f:
                f.write(texte)
        except Exception:
            pass
        echecs = [v for v in res["verifications"] if not v["ok"]]
        resume = (
            "Aboutissants — machine mécanique construite : %d corps, %d User Parameters créés, "
            "%d mis à jour. Vérifications en échec : %d.\nRapport : %s"
            % (info["nb_corps"], len(info["user_params_crees"]), len(info["user_params_maj"]),
               len(echecs), chemin)
        )
        ui.messageBox(resume + "\n\n" + "\n".join(v["message"] for v in echecs)[:1500])
        return res, info
    except Exception:
        ui.messageBox("Aboutissants — erreur :\n%s" % traceback.format_exc())
        return None


if __name__ == "__main__":
    # Exécution hors Fusion : imprime le rapport cinématique.
    resultat = calculer()
    print(rapport_texte(resultat))
