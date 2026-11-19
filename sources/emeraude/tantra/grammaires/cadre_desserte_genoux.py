# -*- coding: utf-8 -*-
"""Grammaire — desserte → cadre à genoux (volet 3, deux états MEUBLE / CADRE).

**MEUBLE** : desserte de salon en chêne (plateau 750 mm, tablette basse).
Le bandeau arrière du plateau est en réalité la **barre haute** du cadre :
il est tenonné sur deux **montants télescopiques** en lamellé de hêtre qui
coulissent dans des **fourreaux** de chêne (pieds arrière).

**CADRE** (un geste par fonction, sans ajout de pièce) :

1. déverrouiller les deux doigts d'indexage et lever la barre de
   ``course`` mm (assistance par vérins à gaz) : les doigts se ré-enclenchent
   seuls, puis on engage les goupilles captives (double verrouillage) ;
2. faire basculer la tablette basse de 180° vers l'avant autour de son
   axe traversant Ø16 : sa face rembourrée vient dessus, deux pieds
   pivotants se déplient sous son nez ; doigt d'indexage + goupille.

La personne s'agenouille sur la tablette, buste sur le plateau (pupitre),
poignets à la barre haute, chevilles au nez de la tablette. Elle est
**sur** le meuble : les tractions sur les ancrages sont des efforts
internes. Le pantographe a été écarté (trop d'articulations à verrouiller,
jeu cumulé).
"""

from __future__ import annotations

from dataclasses import dataclass

from tantra.catalogues.mecanismes import AXE_16, DOIGT_INDEXAGE_12, DOIGT_INDEXAGE_16, GOUPILLE_CAPTIVE_10, GOUPILLE_CAPTIVE_12
from tantra.chiffrage import chiffrer
from tantra.courbes import rectangle, tourner
from tantra.geometrie import Ancrage, Assemblage, CasStabilite, GeometrieMeuble, piece_profil, prisme
from tantra.grammaires._cadre import CODE_ETAT, ETAT_CADRE, ETAT_MEUBLE, ETATS, etat_depuis_code, verifier_liaison_verrouillee
from tantra.grammaires._siege import COEFFICIENT_STABILITE_ACCIDENTEL_MIN, essais_communs, verifs_stabilite
from tantra.parametres import (CADRE_DESSERTE_GENOUX as TYPO, G, LAMELLE_HETRE, NIVEAU_AVERTISSEMENT,
                               PARAMETRES_DEFAUT, PREFIXE_FUSION, Essence, ParametresGlobaux)
from tantra.regles import (EFFORT_MANOEUVRE_MAX_N, cs_axe_traversant, cs_flexion, cs_tenon, effort_manoeuvre_n,
                           piece_loge_insert, recouvrement_telescope_ok, verif, verifier_deverrouillage_sous_charge,
                           verifier_pincement)

P_ = "desserte"


@dataclass(frozen=True)
class ParametresDesserteGenoux:
    longueur: float = 1000.0
    profondeur: float = 420.0
    hauteur_meuble: float = 750.0
    hauteur_cadre: float = 1150.0
    hauteur_agenouilloir: float = 180.0
    epaisseur_plateau: float = 25.0
    section_pied_avant: float = 45.0
    section_fourreau: float = 110.0
    section_montant: float = 70.0
    essence_montant: Essence = LAMELLE_HETRE
    section_barre: tuple[float, float] = (60.0, 70.0)
    """Barre haute : (épaisseur y, hauteur z)."""
    jeu_fin_course: float = 30.0
    """Ombre entre barre et haut des fourreaux en MEUBLE (anti-écrasement)."""
    jeu_cisaillement: float = 6.0
    """Jeu entre pièces qui glissent l'une devant l'autre (≤ 8 mm)."""
    profondeur_tablette: float = 300.0
    epaisseur_tablette: float = 25.0
    mousse_tablette: float = 40.0
    profondeur_nez: float = 70.0
    nombre_verins: int = 2
    assistance_verin_n: float = 30.0
    fixation_murale: bool = True
    """Tirant anti-basculement (patte murale à crochet derrière un fourreau, type kit EN 14749)."""
    globaux: ParametresGlobaux = PARAMETRES_DEFAUT

    @property
    def course(self) -> float:
        return self.hauteur_cadre - self.hauteur_meuble

    @property
    def z_haut_fourreau(self) -> float:
        return self.hauteur_meuble - self.section_barre[1] - self.jeu_fin_course

    @property
    def longueur_montant(self) -> float:
        """Montant le plus long possible : de 20 mm au-dessus du sol à la barre (en MEUBLE)."""
        return self.hauteur_meuble - self.section_barre[1] - 20.0

    @property
    def recouvrement_cadre(self) -> float:
        bas_cadre = self.hauteur_meuble - self.section_barre[1] - self.longueur_montant + self.course
        return self.z_haut_fourreau - bas_cadre


def calculer(p: ParametresDesserteGenoux | None = None, etat: str | int = ETAT_MEUBLE) -> GeometrieMeuble:
    p = p or ParametresDesserteGenoux()
    etat = etat_depuis_code(etat)
    for nom in ("longueur", "profondeur", "hauteur_meuble", "hauteur_cadre", "hauteur_agenouilloir"):
        TYPO.verifier(nom, getattr(p, nom))
    g = p.globaux
    ch = g.charges
    chene = g.essence_structure
    cadre = etat == ETAT_CADRE
    L, D, H = p.longueur, p.profondeur, p.hauteur_meuble
    a, f, m = p.section_pied_avant, p.section_fourreau, p.section_montant
    by, bz = p.section_barre
    dz = p.course if cadre else 0.0
    pieces, assemblages, ancrages = [], [], []
    # Pieds avant et fourreaux arrière
    for cote, x in (("g", 0.0), ("d", L - a)):
        pieces.append(prisme(f"{P_}_pied_avant_{cote}", "pied", chene.nom, x, 0.0, 0.0, a, a, H - p.epaisseur_plateau))
    yf = D - f
    for cote, x in (("g", 0.0), ("d", L - f)):
        pieces.append(prisme(f"{P_}_fourreau_{cote}", "montant", chene.nom, x, yf, 0.0, f, f, p.z_haut_fourreau,
                             "Pied arrière creux (contrecollé 4 faces, parois 20 mm), bague POM en tête."))
        xm = x + (f - m) / 2
        z_bas = H - bz - p.longueur_montant + dz
        pieces.append(prisme(f"{P_}_montant_tele_{cote}", "montant", p.essence_montant.nom, xm, yf + (f - m) / 2,
                             z_bas, m, m, p.longueur_montant,
                             "Montant télescopique ; perçages d'indexage aux deux positions."))
    y_barre = yf + (f - m) / 2  # face avant de la barre alignée sur la face avant des montants
    pieces.append(prisme(f"{P_}_barre_haute", "traverse", chene.nom, 0.0, y_barre, H - bz + dz, L, by, bz,
                         "Bandeau arrière du plateau en MEUBLE, barre haute du cadre en CADRE."))
    y_fin_plateau = y_barre - p.jeu_cisaillement
    pieces.append(prisme(f"{P_}_plateau", "plateau", chene.nom, 0.0, 0.0, H - p.epaisseur_plateau, L, y_fin_plateau,
                         p.epaisseur_plateau, "Plateau ; en CADRE, appui de buste (pupitre)."))
    hc = 100.0
    for cote, x in (("g", 0.0), ("d", L - 30.0)):
        pieces.append(prisme(f"{P_}_ceinture_{cote}", "ceinture", chene.nom, x, a, H - p.epaisseur_plateau - hc,
                             30.0, yf - a, hc))
        pieces.append(prisme(f"{P_}_entretoise_{cote}", "traverse", chene.nom, x, a, 40.0, 30.0, yf - a, 50.0))
    pieces.append(prisme(f"{P_}_ceinture_avant", "ceinture", chene.nom, a, 0.0, H - p.epaisseur_plateau - hc,
                         L - 2 * a, 25.0, hc))
    # Tablette / agenouilloir : pivot dans les pieds avant
    e_t, e_m = p.epaisseur_tablette, p.mousse_tablette
    z_b = p.hauteur_agenouilloir - e_t - e_m
    pivot = (a / 2, z_b + (e_t + e_m) / 2)
    y0, y1 = 5.0, 5.0 + p.profondeur_tablette
    ang = 180.0 if cadre else 0.0
    xt, lt = a + p.jeu_cisaillement, L - 2 * (a + p.jeu_cisaillement)

    def _t(nom, role, mat, prof, **kw):
        pieces.append(piece_profil(f"{P_}_{nom}", role, mat, xt, lt, tourner(prof, ang, pivot), **kw))

    _t("tablette", "repose_genoux", g.essence_courbe.nom, rectangle(y0, z_b + e_m, y1 - y0 - p.profondeur_nez, e_t),
       commentaire="Tablette contreplaqué ; dessous rembourré (devient le dessus en CADRE).")
    _t("tablette_mousse", "mousse", "mousse_hr55", rectangle(y0, z_b, y1 - y0 - p.profondeur_nez, e_m))
    _t("tablette_cuir", "revetement", g.revetement_tantra.nom, rectangle(y0, z_b - 1.3, y1 - y0 - p.profondeur_nez, 1.3),
       surface_revetement_m2=lt * (p.profondeur_tablette + 2 * e_m) * 1e-6)
    _t("nez_tablette", "traverse", chene.nom, rectangle(y1 - p.profondeur_nez, z_b, p.profondeur_nez, e_t + e_m),
       commentaire="Nez en chêne : reçoit les ancrages de chevilles et les pieds pivotants.")
    for k, xp in enumerate((xt + 60.0, xt + lt - 60.0 - a)):
        if cadre:
            y_n = 2 * pivot[0] - y1  # face avant du nez après retournement
            pieces.append(prisme(f"{P_}_pied_pivotant_{k + 1}", "pied", chene.nom, xp, y_n + 10.0, 0.0, a, a, z_b,
                                 "Pied pivotant déplié (arrêt à bille + butée de forme)."))
        else:
            pieces.append(prisme(f"{P_}_pied_pivotant_{k + 1}", "pied", chene.nom, xp, y1 - p.profondeur_nez - z_b,
                                 z_b + 2.0, a, z_b, 25.0, "Pied replié dans un logement de la mousse."))
    assemblages += [
        Assemblage(f"{P_}_ceinture_tenons", "mortaise_tenon", f"{P_}_ceinture_*", "pieds/fourreaux", 6),
        Assemblage(f"{P_}_entretoises_tenons", "mortaise_tenon", f"{P_}_entretoise_*", "pieds/fourreaux", 4),
        Assemblage(f"{P_}_barre_enfourchement", "enfourchement", f"{P_}_barre_haute", f"{P_}_montant_tele_*", 2),
        Assemblage(f"{P_}_plateau_tourillons", "tourillon_10", f"{P_}_plateau", f"{P_}_ceinture_*", 12),
        Assemblage(f"{P_}_tablette_tourillons", "tourillon_10", f"{P_}_tablette", f"{P_}_nez_tablette", 6),
        Assemblage(f"{P_}_pivots_tablette", "axe_16", f"{P_}_tablette", f"{P_}_pied_avant_*", 2),
        Assemblage(f"{P_}_verins", "verin_gaz", f"{P_}_montant_tele_*", f"{P_}_fourreau_*", p.nombre_verins),
        Assemblage(f"{P_}_tele_doigts", "doigt_indexage_16", f"{P_}_fourreau_*", f"{P_}_montant_tele_*", 2),
        Assemblage(f"{P_}_tele_goupilles", "goupille_captive_12", f"{P_}_fourreau_*", f"{P_}_montant_tele_*", 2),
        Assemblage(f"{P_}_tablette_doigts", "doigt_indexage_12", f"{P_}_tablette", f"{P_}_pied_avant_*", 1),
        Assemblage(f"{P_}_tablette_goupille", "goupille_captive_10", f"{P_}_tablette", f"{P_}_pied_avant_*", 1),
    ]
    # Ancrages
    for k, xa in enumerate((L / 2 - 250.0, L / 2 + 250.0)):
        ancrages.append(Ancrage(f"ancrage_poignet_{k + 1}", (xa, y_barre + by / 2, H + dz), f"{P_}_barre_haute",
                                False, "Insert vertical sur le dessus de la barre, cache affleurant en MEUBLE."))
    y_nez = (2 * pivot[0] - y1) if cadre else y1
    z_nez = pivot[1]
    for k, xa in enumerate((L / 2 - 150.0, L / 2 + 150.0)):
        ancrages.append(Ancrage(f"ancrage_cheville_{k + 1}", (xa, y_nez, z_nez), f"{P_}_nez_tablette", False,
                                "Insert horizontal dans le nez de la tablette (face cachée en MEUBLE)."))

    # ------------------------------------------------------------------ vérifications
    F = ch.charge_service_ancrage_n
    cs_min = ch.coefficient_securite
    v = []
    rec = p.recouvrement_cadre
    v.append(verif("telescope_recouvrement", recouvrement_telescope_ok(rec, m),
                   f"Recouvrement en CADRE {rec:.0f} mm pour une section de {m:g} mm (≥ 3 × section = {3 * m:.0f}). "
                   f"Course {p.course:.0f} mm. Au-delà, prévoir un télescope à deux étages (coût, jeu).",
                   compromis=not recouvrement_telescope_ok(rec, m)))
    bras = p.hauteur_cadre - p.z_haut_fourreau
    cs_mt = cs_flexion(bras, m, m, F, p.essence_montant, "console")
    v.append(verif("montant_flexion", cs_mt >= cs_min,
                   f"Montant {m:g}×{m:g} {p.essence_montant.nom} en console de {bras:.0f} mm, {F:.0f} N "
                   f"horizontal en tête : CS {cs_mt:.1f}."))
    v.append(verif("montant_appui_fourreau", rec > 0 and F * bras / rec / (m * min(rec, 60.0)) * 2 < chene.fm_k_mpa / cs_min,
                   f"Pression de contact montant/fourreau ≈ {F * bras / max(rec, 1) / (m * min(max(rec, 1), 60.0)) * 2:.1f} "
                   f"MPa (couple repris par le recouvrement, bagues POM)."))
    portee_barre = L - f
    cs_bv = cs_flexion(portee_barre, by, bz, 2 * F * 0.55, chene, "centree")
    cs_bh = cs_flexion(portee_barre, bz, by, 2 * F * 0.55, chene, "centree")
    v.append(verif("barre_flexion", min(cs_bv, cs_bh) >= cs_min,
                   f"Barre {by:g}×{bz:g} chêne, portée {portee_barre:.0f} mm, deux poignets à ±250 mm "
                   f"(2 × {F:.0f} N) : CS vertical {cs_bv:.1f}, horizontal {cs_bh:.1f}."))
    ok, txt = piece_loge_insert(by, bz, chene, ch, recouvrement_mm=g.retrait_ancre_sous_surface_mm)
    v.append(verif("insert_barre", ok, f"Insert vertical dans la barre : {txt}."))
    ok, txt = piece_loge_insert(e_t + e_m, p.profondeur_nez, chene, ch)
    v.append(verif("insert_nez_tablette", ok, f"Insert horizontal dans le nez de tablette : {txt}."))
    from tantra.catalogues.fixations import fixation_par_nom
    r_tour = 2 * fixation_par_nom("tourillon_12").resistance_caracteristique_n
    cs_enf = (cs_tenon(F, m / 3, bz - 10.0, chene) * F + r_tour) / F
    v.append(verif("enfourchement_barre", cs_enf >= cs_min,
                   f"Enfourchement barre/montant ({m / 3:.0f} × {bz - 10:.0f} mm) chevillé par 2 tourillons Ø12 "
                   f"traversants, {F:.0f} N : CS {cs_enf:.1f}."))
    v += verifier_liaison_verrouillee("telescope", F, [DOIGT_INDEXAGE_16, GOUPILLE_CAPTIVE_12], chene, 20.0)
    v.append(verifier_deverrouillage_sous_charge("telescope", F, DOIGT_INDEXAGE_16))
    f_genoux = ch.poids_personne_n * ch.facteur_dynamique * 0.6
    v += verifier_liaison_verrouillee("agenouilloir", F, [DOIGT_INDEXAGE_12, GOUPILLE_CAPTIVE_10], chene, a / 2)
    v.append(verifier_deverrouillage_sous_charge("agenouilloir", F, DOIGT_INDEXAGE_12))
    cs_ax, mode = cs_axe_traversant(f_genoux / 2 + F / 2, AXE_16, chene, a / 2, 2)
    v.append(verif("axe_tablette", cs_ax >= cs_min,
                   f"Axe Ø16 de la tablette dans le pied avant {a:g} mm : CS {cs_ax:.1f} ({mode})."))
    cs_tab = cs_flexion(lt - 120.0, p.profondeur_tablette, e_t, f_genoux, g.essence_courbe, "centree")
    v.append(verif("tablette_flexion", cs_tab >= cs_min,
                   f"Tablette {e_t:g} mm sur {lt - 120:.0f} mm entre pieds pivotants, {f_genoux:.0f} N : CS {cs_tab:.1f}.",
                   niveau_echec=NIVEAU_AVERTISSEMENT))
    cs_pl = cs_flexion(L - 60.0, y_fin_plateau, p.epaisseur_plateau, 0.4 * ch.poids_personne_n * ch.facteur_dynamique,
                       chene, "centree")
    v.append(verif("plateau_appui_buste", cs_pl >= cs_min, f"Plateau en appui de buste : CS {cs_pl:.1f}."))
    # Pincement et manœuvre
    v.append(verifier_pincement("barre_fourreau_fin_course", p.jeu_fin_course))
    v.append(verifier_pincement("barre_plateau_cisaillement", p.jeu_cisaillement))
    v.append(verifier_pincement("tablette_pieds_avant", p.jeu_cisaillement))
    v.append(verif("descente_amortie", p.nombre_verins >= 2,
                   "Descente de la barre freinée par vérins à gaz (pas de chute libre sur les mains)."))
    vol_mobile = (L * by * bz * chene.masse_volumique_kg_m3 + 2 * m * m * p.longueur_montant
                  * p.essence_montant.masse_volumique_kg_m3) * 1e-9
    f_lev = max(0.0, vol_mobile * G - p.nombre_verins * p.assistance_verin_n)
    v.append(verif("pas_de_montee_spontanee", vol_mobile * G > p.nombre_verins * p.assistance_verin_n,
                   f"Vérins ({p.nombre_verins} × {p.assistance_verin_n:.0f} N) moins forts que le poids mobile "
                   f"({vol_mobile * G:.0f} N) : la barre ne monte pas seule au déverrouillage."))
    v.append(verif("effort_levage_barre", f_lev <= EFFORT_MANOEUVRE_MAX_N,
                   f"Levage barre + montants ({vol_mobile:.1f} kg) : {f_lev:.0f} N à deux mains, vérins déduits."))
    m_tab = (lt * p.profondeur_tablette * (e_t * 680 + e_m * 55) + lt * p.profondeur_nez * (e_t + e_m)
             * (chene.masse_volumique_kg_m3 - 680)) * 1e-9
    f_tab = effort_manoeuvre_n(m_tab, p.profondeur_tablette / 2, p.profondeur_tablette)
    v.append(verif("effort_bascule_tablette", f_tab <= EFFORT_MANOEUVRE_MAX_N,
                   f"Bascule de la tablette ({m_tab:.1f} kg) : ≈ {f_tab:.0f} N en début de mouvement."))
    w = ch.poids_personne_n
    fh = ch.effort_horizontal_exterieur_n
    xm = L / 2
    if cadre:
        fd = w * ch.facteur_dynamique
        y_gen = 2 * pivot[0] - (y0 + y1) / 2
        cas = [
            CasStabilite("agenouille_pousse_avant", ((0.6 * fd, xm, y_gen), (0.4 * fd, xm, y_fin_plateau / 2)),
                         (fh, "+y", p.hauteur_cadre), 1.5,
                         "À genoux, buste sur le plateau, poussée de 300 N vers l'arrière en haut de la barre."),
            CasStabilite("agenouille_tire_vers_soi", ((0.6 * fd, xm, y_gen), (0.4 * fd, xm, y_fin_plateau / 2)),
                         (fh, "-y", p.hauteur_cadre), 1.5,
                         "À genoux, traction de 300 N vers l'avant en haut de la barre (partenaire)."),
            CasStabilite("lateral", ((w, xm, y_gen),), (fh, "-x", p.hauteur_cadre),
                         COEFFICIENT_STABILITE_ACCIDENTEL_MIN, "Poussée latérale 300 N en haut de la barre."),
        ]
    else:
        cas = [
            CasStabilite("desserte_appui_bord", ((300.0, xm, 0.0),), None, 1.5,
                         "Appui vertical de 300 N au bord avant du plateau (type EN 12521)."),
            CasStabilite("desserte_poussee", ((300.0, xm, 0.0),), (fh / 3, "-y", H),
                         COEFFICIENT_STABILITE_ACCIDENTEL_MIN, "Idem + 100 N horizontal vers l'avant."),
        ]
    v_stab, infos = verifs_stabilite(pieces, cas)
    v += v_stab
    if cadre:
        # Cadre vide, quelqu'un tire la barre vers soi : faut-il un tirant mural ?
        from tantra.geometrie import coefficient_stabilite
        cas_vide = CasStabilite("vide_traction_barre", (), (fh, "-y", p.hauteur_cadre), 1.5)
        coef, _ = coefficient_stabilite(cas_vide, infos["masse_kg"], infos["cdg"], infos["empreinte"])
        emp = infos["empreinte"]
        m_stab = infos["masse_kg"] * G * (infos["cdg"][1] - emp[2])
        z_tirant = p.z_haut_fourreau - 50.0
        bras_tirant = z_tirant  # tirant horizontal en tête de fourreau, pivot sur l'arête avant au sol
        f_tirant = max(0.0, (1.5 * fh * p.hauteur_cadre - m_stab) / bras_tirant)
        ok = coef >= 1.5 or p.fixation_murale
        v.append(verif("stabilite_vide_traction_barre", ok,
                       f"Cadre vide, traction de {fh:.0f} N vers l'avant en haut de la barre : coefficient propre "
                       f"{coef:.2f}. " + (f"Tirant mural requis ≈ {f_tirant:.0f} N (patte à crochet en tête de "
                                          "fourreau, cheville adaptée au mur) — prévu." if p.fixation_murale else
                                          "Sans tirant mural : interdire l'usage ou lester."),
                       compromis=coef < 1.5))
        infos["effort_tirant_mural_n"] = f_tirant
    v += essais_communs(P_)
    from tantra.regles import essai_requis
    v.append(essai_requis("essai_verrous", "Essai de chaque liaison verrouillée : 3 × charge, un verrou retiré, "
                          "puis 1000 cycles de manœuvre (usure des doigts/bagues)."))
    derivees = {**infos, "code_etat": CODE_ETAT[etat], "course_mm": p.course, "recouvrement_cadre_mm": rec,
                "z_agenouilloir": p.hauteur_agenouilloir}
    n = len(ancrages)
    return GeometrieMeuble(TYPO.nom, etat, tuple(pieces), tuple(assemblages), tuple(ancrages), tuple(v), derivees,
                           quincaillerie=(("insert_ancre_m12", n), ("anneau_rabattable", n), ("cache_aimante", 2)))


def calculer_etats(p: ParametresDesserteGenoux | None = None) -> dict[str, GeometrieMeuble]:
    return {e: calculer(p, e) for e in ETATS}


def vers_parametres_fusion_desserte(p: ParametresDesserteGenoux | None = None) -> dict:
    p = p or ParametresDesserteGenoux()
    P = f"{PREFIXE_FUSION}desserte_"
    return {
        f"{P}etat": (0, "", "0 = MEUBLE, 1 = CADRE."),
        f"{P}section_montant": (p.section_montant, "mm", "Section des montants télescopiques."),
        f"{P}section_fourreau": (p.section_fourreau, "mm", "Section des fourreaux (pieds arrière)."),
        f"{P}jeu_fin_course": (p.jeu_fin_course, "mm", "Ombre anti-écrasement barre / fourreaux."),
    }


def chiffrage(p: ParametresDesserteGenoux | None = None):
    return chiffrer(calculer(p, ETAT_MEUBLE))
