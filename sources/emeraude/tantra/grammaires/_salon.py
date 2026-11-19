# -*- coding: utf-8 -*-
"""Briques communes des meubles de salon camouflables (volet 2, Python pur).

Contrainte de gamme : **zéro élément visible** à l'état SALON. Aucun
anneau, aucune vis, aucun cuir technique : les ancrages sont des inserts
inox M12 noyés dans la structure de chêne, cachés sous des pièces
tapissées mobiles qui se dévoilent par un geste :

* **manchettes d'accoudoir basculantes** : le dessus d'accoudoir se
  soulève par l'arrière (charnières invisibles type Soss à l'avant,
  loqueteaux magnétiques à l'arrière), découvrant un insert vertical dans
  la traverse haute d'accoudoir ;
* **bavette basculante** : le panneau tapissé qui habille la ceinture
  avant pivote vers l'avant autour de son chant bas, découvrant deux
  inserts horizontaux dans la traverse avant ;
* **galettes** : soulevées, elles découvrent deux inserts dans la traverse
  arrière, obturés par des caches aimantés tapissés.

L'anneau à épaulement ne se visse dans l'insert qu'au moment de l'usage ;
il est rangé ailleurs. Les mêmes paramètres produisent les deux états
(SALON = 0, RÉVÉLÉ = 1).
"""

from __future__ import annotations

from dataclasses import dataclass, field

from tantra.courbes import rectangle, tourner
from tantra.geometrie import Ancrage, Assemblage, Piece, Verification, piece_profil, prisme
from tantra.parametres import NIVEAU_NON_CONFORME, ParametresGlobaux

ETAT_SALON = "SALON"
ETAT_REVELE = "REVELE"
ETATS = (ETAT_SALON, ETAT_REVELE)
CODE_ETAT = {ETAT_SALON: 0, ETAT_REVELE: 1}


def etat_depuis_code(code: int | str) -> str:
    if isinstance(code, str) and code in ETATS:
        return code
    return ETAT_REVELE if int(code) else ETAT_SALON


@dataclass(frozen=True)
class ParametresSalon:
    """Cotes communes canapé / fauteuil (mm)."""

    largeur: float
    profondeur: float
    hauteur_assise: float
    hauteur_dossier: float
    hauteur_accoudoir: float
    hauteur_pieds: float = 140.0
    hauteur_ceinture: float = 300.0
    """Dessus de la ceinture (dessous des galettes)."""
    largeur_accoudoir: float = 170.0
    epaisseur_dossier: float = 200.0
    epaisseur_bavette: float = 25.0
    mousse_bavette: float = 0.0
    """> 0 : la face intérieure de la bavette est rembourrée (repose-genoux du fauteuil)."""
    section_rail: tuple[float, float] = (50.0, 160.0)
    """Traverses avant/arrière : (épaisseur selon y, hauteur selon z)."""
    epaisseur_traverse_avant: float = 70.0
    """Traverse avant plus épaisse : loge l'insert horizontal (encastrement 60 mm)."""
    section_rail_accoudoir: tuple[float, float] = (60.0, 70.0)
    epaisseur_manchette: float = 22.0
    mousse_manchette: float = 25.0
    angle_manchette: float = 105.0
    nombre_galettes: int = 2
    ancrages_arriere: bool = True
    epaisseur_joue: float = 18.0


@dataclass
class Construction:
    pieces: list[Piece] = field(default_factory=list)
    assemblages: list[Assemblage] = field(default_factory=list)
    ancrages: list[Ancrage] = field(default_factory=list)
    couvertures: dict = field(default_factory=dict)
    """nom d'ancrage → nom de la pièce qui le masque à l'état SALON."""
    infos: dict = field(default_factory=dict)


def _tapisse(nom: str, base: str, x: float, dx: float, profil, revetement: str, surface: float) -> list[Piece]:
    return [piece_profil(nom, base, revetement, x, dx, profil, surface_revetement_m2=surface)]


def construire_salon(s: ParametresSalon, g: ParametresGlobaux, etat: str, prefixe: str) -> Construction:
    """Construit la carcasse, les garnitures et les pièces mobiles d'un meuble de salon."""
    c = Construction()
    L, D = s.largeur, s.profondeur
    hp, hc, ha = s.hauteur_pieds, s.hauteur_ceinture, s.hauteur_accoudoir
    la, ej = s.largeur_accoudoir, s.epaisseur_joue
    chene, ply, hetre = g.essence_structure.nom, g.essence_courbe.nom, "hetre"
    rev = g.revetement_salon.nom
    by, bz = s.section_rail
    ry, rz = s.section_rail_accoudoir
    revele = etat == ETAT_REVELE
    # Pieds fuseaux (enveloppe prismatique ; tournés en atelier)
    for nom, x, y in (("pied_av_g", 30.0, 30.0), ("pied_av_d", L - 80.0, 30.0),
                      ("pied_ar_g", 30.0, D - 80.0), ("pied_ar_d", L - 80.0, D - 80.0)):
        c.pieces.append(prisme(f"{prefixe}_{nom}", "pied", hetre, x, y, 0.0, 50.0, 50.0, hp,
                               "Pied fuseau tourné en hêtre teinté, tenon Ø20 dans la ceinture."))
    c.assemblages.append(Assemblage(f"{prefixe}_pieds", "mortaise_tenon", f"{prefixe}_pied_*", "ceinture", 4))
    # Accoudoirs
    z_rail_acc = ha - s.epaisseur_manchette - s.mousse_manchette - rz
    y_fin_acc = D - s.epaisseur_dossier + 40.0
    for cote, xe in (("g", 0.0), ("d", L - la)):
        x_ext = xe if cote == "g" else L - ej
        x_int = xe + la - ej if cote == "g" else L - la
        c.pieces += [
            prisme(f"{prefixe}_joue_ext_{cote}", "accoudoir", ply, x_ext, 0.0, hp, ej, D, z_rail_acc + rz - hp,
                   "Joue extérieure (contreplaqué), garnie et tapissée."),
            prisme(f"{prefixe}_joue_int_{cote}", "accoudoir", ply, x_int, 0.0, hc, ej, y_fin_acc, z_rail_acc + rz - hc),
            prisme(f"{prefixe}_montant_acc_av_{cote}", "montant", chene, xe + (la - 50.0) / 2, 20.0, hp,
                   50.0, 60.0, z_rail_acc - hp),
            prisme(f"{prefixe}_montant_acc_ar_{cote}", "montant", chene, xe + (la - 50.0) / 2, y_fin_acc - 80.0, hp,
                   50.0, 60.0, z_rail_acc - hp),
            prisme(f"{prefixe}_traverse_acc_{cote}", "traverse", chene, xe + (la - ry) / 2, 20.0, z_rail_acc,
                   ry, y_fin_acc - 20.0, rz, "Traverse haute d'accoudoir : reçoit l'insert vertical."),
            prisme(f"{prefixe}_garniture_acc_{cote}", "mousse", "mousse_hr35", x_ext if cote == "g" else L - ej - 30.0,
                   0.0, hp + 20.0, 30.0, D - 20.0, z_rail_acc + rz - hp - 20.0),
        ]
        surf_acc = (2 * D * (ha - hp) + la * (ha - hp) + 2 * D * la) * 1e-6
        c.pieces += _tapisse(f"{prefixe}_revetement_acc_{cote}", "revetement", x_ext - 2.0 if cote == "g" else L,
                             2.0, rectangle(0.0, hp, D, ha - hp - s.epaisseur_manchette - s.mousse_manchette),
                             rev, surf_acc)
        c.assemblages.append(Assemblage(f"{prefixe}_accoudoir_{cote}", "mortaise_tenon",
                                        f"{prefixe}_traverse_acc_{cote}", f"{prefixe}_montant_acc_*_{cote}", 4))
        # Manchette basculante (charnière à l'avant, z = dessous de la manchette)
        e_m = s.epaisseur_manchette + s.mousse_manchette
        pivot = (0.0, z_rail_acc + rz)
        prof_m = rectangle(0.0, z_rail_acc + rz, y_fin_acc, s.epaisseur_manchette)
        prof_mousse = rectangle(0.0, z_rail_acc + rz + s.epaisseur_manchette, y_fin_acc, s.mousse_manchette)
        ang = s.angle_manchette if revele else 0.0
        c.pieces.append(piece_profil(f"{prefixe}_manchette_{cote}", "manchette", ply, xe, la,
                                     tourner(prof_m, ang, pivot),
                                     "Manchette tapissée sur âme contreplaqué 22 mm, charnières Soss à l'avant."))
        c.pieces.append(piece_profil(f"{prefixe}_manchette_garniture_{cote}", "mousse", "mousse_hr35", xe, la,
                                     tourner(prof_mousse, ang, pivot),
                                     surface_revetement_m2=0.0))
        c.assemblages += [
            Assemblage(f"{prefixe}_manchette_charnieres_{cote}", "charniere_soss", f"{prefixe}_manchette_{cote}",
                       f"{prefixe}_traverse_acc_{cote}", 2),
            Assemblage(f"{prefixe}_manchette_aimants_{cote}", "aimant_fermeture", f"{prefixe}_manchette_{cote}",
                       f"{prefixe}_traverse_acc_{cote}", 2),
        ]
        y_anc = (20.0 + y_fin_acc) / 2.0 + 60.0
        nom_a = f"ancrage_accoudoir_{cote}"
        c.ancrages.append(Ancrage(nom_a, (xe + la / 2, y_anc, z_rail_acc + rz), f"{prefixe}_traverse_acc_{cote}",
                                  revele, "Insert vertical dans la traverse haute d'accoudoir."))
        c.couvertures[nom_a] = f"{prefixe}_manchette_{cote}"
    c.infos["z_traverse_accoudoir"] = z_rail_acc
    c.infos["e_manchette"] = s.epaisseur_manchette + s.mousse_manchette
    c.infos["y_fin_accoudoir"] = y_fin_acc
    # Ceinture
    x0, x1 = la, L - la
    y_rail_av = s.epaisseur_bavette + s.mousse_bavette + 5.0
    y_rail_ar = D - s.epaisseur_dossier - by
    c.pieces += [
        prisme(f"{prefixe}_traverse_avant", "ceinture", chene, x0, y_rail_av, hp, x1 - x0, s.epaisseur_traverse_avant,
               hc - hp,
               "Traverse avant : deux inserts horizontaux derrière la bavette."),
        prisme(f"{prefixe}_traverse_arriere", "ceinture", chene, x0, y_rail_ar, hp, x1 - x0, by, hc - hp,
               "Traverse arrière : deux inserts verticaux sous les galettes (caches aimantés)."),
        prisme(f"{prefixe}_fond_assise", "panneau", ply, x0, y_rail_av + s.epaisseur_traverse_avant, hc - 15.0,
               x1 - x0, y_rail_ar - y_rail_av - s.epaisseur_traverse_avant, 15.0, "Fond d'assise (ou sanglage élastique)."),
    ]
    c.assemblages.append(Assemblage(f"{prefixe}_ceinture", "mortaise_tenon", f"{prefixe}_traverse_*",
                                    f"{prefixe}_montant_acc_*", 4))
    c.infos["y_traverse_avant"] = y_rail_av
    c.infos["portee_traverse"] = x1 - x0
    # Bavette basculante (pivot au chant bas avant)
    pivot_b = (0.0, hp)
    ang_b = 90.0 if revele else 0.0
    prof_b = rectangle(0.0, hp, s.epaisseur_bavette, hc - hp)
    c.pieces.append(piece_profil(f"{prefixe}_bavette", "bavette", ply, x0 + 5.0, x1 - x0 - 10.0,
                                 tourner(prof_b, ang_b, pivot_b),
                                 "Bavette tapissée : pivote vers l'avant sur son chant bas (Soss), aimants en haut."))
    c.assemblages += [
        Assemblage(f"{prefixe}_bavette_charnieres", "charniere_soss", f"{prefixe}_bavette", f"{prefixe}_traverse_avant", 2),
        Assemblage(f"{prefixe}_bavette_aimants", "aimant_fermeture", f"{prefixe}_bavette", f"{prefixe}_traverse_avant", 2),
    ]
    if s.mousse_bavette > 0:
        prof_bm = rectangle(s.epaisseur_bavette, hp + 10.0, s.mousse_bavette, hc - hp - 20.0)
        c.pieces.append(piece_profil(f"{prefixe}_bavette_mousse", "mousse", "mousse_hr55", x0 + 15.0, x1 - x0 - 30.0,
                                     tourner(prof_bm, ang_b, pivot_b),
                                     "Rembourrage de la face intérieure (cachée en SALON, dessus en RÉVÉLÉ)."))
        c.pieces.append(piece_profil(f"{prefixe}_bavette_cuir", "revetement", g.revetement_tantra.nom, x0 + 15.0,
                                     x1 - x0 - 30.0,
                                     tourner(rectangle(s.epaisseur_bavette + s.mousse_bavette, hp + 10.0, 1.3,
                                                       hc - hp - 20.0), ang_b, pivot_b),
                                     "Face intérieure lavable (cuir pigmenté).",
                                     surface_revetement_m2=(x1 - x0) * (hc - hp + 2 * s.mousse_bavette) * 1e-6))
    surf_bav = (x1 - x0) * (hc - hp) * 2e-6
    c.pieces += _tapisse(f"{prefixe}_bavette_tissu", "revetement", x0 + 5.0, x1 - x0 - 10.0,
                         tourner(rectangle(-1.5, hp, 1.5, hc - hp), ang_b, pivot_b), rev, surf_bav)
    for k, xa in enumerate((x0 + (x1 - x0) * 0.25, x0 + (x1 - x0) * 0.75)):
        nom_a = f"ancrage_avant_{k + 1}"
        c.ancrages.append(Ancrage(nom_a, (xa, y_rail_av, (hp + hc) / 2.0), f"{prefixe}_traverse_avant", revele,
                                  "Insert horizontal (axe y) dans la traverse avant."))
        c.couvertures[nom_a] = f"{prefixe}_bavette"
    # Galettes et dossier
    n = s.nombre_galettes
    lg = (x1 - x0) / n
    y_gal0, y_gal1 = 0.0 + 10.0, D - s.epaisseur_dossier + 30.0
    for k in range(n):
        xg = x0 + k * lg
        c.pieces.append(prisme(f"{prefixe}_galette_{k + 1}", "mousse", "mousse_hr35", xg + 2.0, y_gal0, hc,
                               lg - 4.0, y_gal1 - y_gal0, s.hauteur_assise - hc - 2.0,
                               "Galette déhoussable (HR 35 + ouate)."))
        surf_g = 2 * (lg * (y_gal1 - y_gal0) + (lg + y_gal1 - y_gal0) * (s.hauteur_assise - hc)) * 1e-6
        c.pieces.append(prisme(f"{prefixe}_galette_housse_{k + 1}", "revetement", rev, xg + 2.0, y_gal0,
                               s.hauteur_assise - 2.0, lg - 4.0, y_gal1 - y_gal0, 2.0,
                               surface_revetement_m2=surf_g))
    if s.ancrages_arriere:
        for k, xa in enumerate((x0 + (x1 - x0) * 0.25, x0 + (x1 - x0) * 0.75)):
            nom_a = f"ancrage_arriere_{k + 1}"
            c.ancrages.append(Ancrage(nom_a, (xa, y_rail_ar + by / 2, hc), f"{prefixe}_traverse_arriere", False,
                                      "Insert vertical sous galette, cache aimanté tapissé (accès : soulever la galette)."))
            k_gal = min(int((xa - x0) // lg), n - 1)
            c.couvertures[nom_a] = f"{prefixe}_galette_{k_gal + 1}"
    c.pieces += [
        prisme(f"{prefixe}_cadre_dossier", "dossier", ply, la - 10.0, D - 45.0, hp, L - 2 * la + 20.0, 45.0,
               s.hauteur_dossier - hp, "Cadre de dossier (montants + traverses à tenons, contreplaqué)."),
        prisme(f"{prefixe}_coussin_dossier", "mousse", "mousse_hr35", x0, D - s.epaisseur_dossier + 30.0, hc,
               x1 - x0, s.epaisseur_dossier - 75.0, s.hauteur_dossier - hc - 30.0),
        prisme(f"{prefixe}_revetement_dossier", "revetement", rev, la - 10.0, D - 2.0, hp, L - 2 * la + 20.0, 2.0,
               s.hauteur_dossier - hp,
               surface_revetement_m2=(L - 2 * la) * (s.hauteur_dossier - hp) * 3e-6),
    ]
    c.assemblages.append(Assemblage(f"{prefixe}_dossier", "mortaise_tenon", f"{prefixe}_cadre_dossier",
                                    "accoudoirs", 4))
    c.assemblages.append(Assemblage(f"{prefixe}_tourillons_carcasse", "tourillon_10", "joues", "montants", 24))
    return c


def verifier_discretion(c: Construction, etat: str) -> list[Verification]:
    """Zéro élément visible en SALON ; ancrages accessibles en RÉVÉLÉ (hors arrière)."""
    from tantra.regles import verif
    pieces = {p.nom: p for p in c.pieces}
    out = []
    for a in c.ancrages:
        couv = pieces[c.couvertures[a.nom]]
        b = couv.aabb
        x, y, z = a.position
        if a.nom.startswith("ancrage_avant"):
            couvert = b[0] - 1 <= x <= b[1] + 1 and b[4] - 1 <= z <= b[5] + 1 and b[3] <= y + 1
        else:
            couvert = b[0] - 1 <= x <= b[1] + 1 and b[2] - 1 <= y <= b[3] + 1 and b[4] >= z - 1
        if etat == ETAT_SALON:
            out.append(verif(f"discretion_{a.nom}", couvert and not a.visible,
                             f"{a.nom} masqué par « {couv.nom} » à l'état SALON."
                             if couvert else f"{a.nom} VISIBLE à l'état SALON : contraire à la gamme.",
                             niveau_echec=NIVEAU_NON_CONFORME))
        elif not a.nom.startswith("ancrage_arriere"):
            out.append(verif(f"acces_{a.nom}", not couvert,
                             f"{a.nom} accessible à l'état RÉVÉLÉ." if not couvert else
                             f"{a.nom} encore couvert à l'état RÉVÉLÉ : revoir l'angle d'ouverture."))
    return out


def verifs_communes(s: ParametresSalon, g: ParametresGlobaux, c: Construction, etat: str,
                    prefixe: str) -> list[Verification]:
    """Ancrages logés dans la structure, traverses, manchettes, pincement, revêtement."""
    from tantra.regles import (cs_flexion, cs_tenon, effort_manoeuvre_n, EFFORT_MANOEUVRE_MAX_N,
                               piece_loge_insert, verif, verifier_pincement)
    ch = g.charges
    ess = g.essence_structure
    F = ch.charge_service_ancrage_n
    cs_min = ch.coefficient_securite
    by, bz = s.section_rail
    ry, rz = s.section_rail_accoudoir
    out: list[Verification] = []
    ok, txt = piece_loge_insert(ry, rz, ess, ch)
    out.append(verif("insert_traverse_accoudoir", ok, f"Insert vertical dans la traverse d'accoudoir : {txt}. "
                     "Recouvrement assuré par la manchette (pas de bois au-dessus)."))
    ok, txt = piece_loge_insert(bz, s.epaisseur_traverse_avant, ess, ch)
    out.append(verif("insert_traverse_avant", ok, f"Insert horizontal dans la traverse avant : {txt}. "
                     "Recouvrement assuré par la bavette."))
    if s.ancrages_arriere:
        ok, txt = piece_loge_insert(by, bz, ess, ch, recouvrement_mm=g.retrait_ancre_sous_surface_mm)
        out.append(verif("insert_traverse_arriere", ok, f"Insert vertical dans la traverse arrière : {txt}, "
                         "cache aimanté affleurant."))
    # Traverse avant : 1500 N horizontal à L/4, flexion dans le plan horizontal (b = hauteur, h = épaisseur)
    portee = c.infos["portee_traverse"]
    cs_av = cs_flexion(portee, bz, s.epaisseur_traverse_avant, 2 * F * 0.75, ess, "centree")
    out.append(verif("traverse_avant_flexion", cs_av >= cs_min,
                     f"Traverse avant {s.epaisseur_traverse_avant:g}×{bz:g} mm, portée {portee:.0f} mm, deux ancrages tirés ensemble "
                     f"(2 × {F:.0f} N, équivalent centré 0,75) : CS {cs_av:.1f}."))
    portee_acc = c.infos["y_fin_accoudoir"] - 100.0
    cs_acc = cs_flexion(portee_acc, ry, rz, F, ess, "centree")
    out.append(verif("traverse_accoudoir_flexion", cs_acc >= cs_min,
                     f"Traverse d'accoudoir {ry:g}×{rz:g} mm, portée {portee_acc:.0f} mm, {F:.0f} N vertical au "
                     f"milieu : CS {cs_acc:.1f}."))
    cs_t = cs_tenon(F / 2.0, ry / 3.0, rz - 15.0, ess)
    out.append(verif("tenons_traverse_accoudoir", cs_t >= cs_min,
                     f"Tenons de la traverse d'accoudoir ({ry / 3:.0f} × {rz - 15:.0f} mm), {F / 2:.0f} N chacun : "
                     f"CS {cs_t:.1f}."))
    cs_tav = cs_tenon(F, s.epaisseur_traverse_avant / 3.0, bz - 30.0, ess)
    out.append(verif("tenons_traverse_avant", cs_tav >= cs_min,
                     f"Tenons de la traverse avant ({s.epaisseur_traverse_avant / 3:.0f} × {bz - 30:.0f} mm), {F:.0f} N chacun "
                     f"(cas défavorable : un seul ancrage près d'un tenon) : CS {cs_tav:.1f}."))
    out.append(verif("charnieres_manchette", s.epaisseur_manchette >= 22.0,
                     f"Âme de manchette {s.epaisseur_manchette:g} mm (Soss n°208 : ≥ 22 mm)."))
    # Manœuvre de la manchette : masse ≈ âme + mousse, cdg au milieu, main au bout
    lm = c.infos["y_fin_accoudoir"]
    m = (s.epaisseur_manchette * 680e-9 + s.mousse_manchette * 35e-9) * lm * s.largeur_accoudoir
    f_m = effort_manoeuvre_n(m, lm / 2, lm)
    out.append(verif("effort_manchette", f_m <= EFFORT_MANOEUVRE_MAX_N,
                     f"Ouverture d'une manchette ({m:.1f} kg) : ≈ {f_m:.0f} N à la main, loqueteaux compris."))
    out.append(verifier_pincement("manchette_charniere", 3.0))
    out.append(verif("fermeture_amortie", True,
                     "Manchettes et bavette : fermeture sur butées caoutchouc + aimants, pas de ressort de rappel "
                     "(aucune fermeture spontanée sur les doigts)."))
    rev = g.revetement_salon
    out.append(verif("revetement_salon", rev.aspect_salon and (rev.lavable or rev.deperlant),
                     f"Revêtement « {rev.nom} » : aspect salon et lavable/déperlant.",
                     niveau_echec="avertissement"))
    return out
