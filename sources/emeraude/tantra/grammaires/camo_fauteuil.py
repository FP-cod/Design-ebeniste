# -*- coding: utf-8 -*-
"""Grammaire — fauteuil bergère à repose-genoux escamotable (volet 2, camouflable).

État SALON : bergère classique (accoudoirs pleins, galette, pieds fuseaux).
État RÉVÉLÉ : la façade d'assise (bavette) pivote de 90° vers l'avant
autour de son chant bas ; sa face intérieure, rembourrée et gainée de cuir
lavable, devient un **repose-genoux** à ~215 mm du sol, porté par des
béquilles rabattables logées à plat contre la face intérieure. Une
personne à genoux, buste sur l'assise, peut être attachée aux deux
inserts de la traverse avant (chevilles/genoux) et aux deux inserts des
accoudoirs (poignets).

Les béquilles touchent le sol à l'état RÉVÉLÉ : elles élargissent
l'empreinte vers l'avant, ce qui rend le cas « à genoux » stable.
"""

from __future__ import annotations

from dataclasses import dataclass

from tantra.chiffrage import chiffrer
from tantra.geometrie import Assemblage, CasStabilite, GeometrieMeuble, prisme
from tantra.grammaires._salon import (
    CODE_ETAT, ETAT_REVELE, ETAT_SALON, ETATS, ParametresSalon, construire_salon, etat_depuis_code,
    verifier_discretion, verifs_communes,
)
from tantra.grammaires._siege import (COEFFICIENT_STABILITE_ACCIDENTEL_MIN, essais_communs,
                                      verif_traction_exterieure, verifs_stabilite)
from tantra.parametres import CAMO_FAUTEUIL as TYPO, PARAMETRES_DEFAUT, PREFIXE_FUSION, ParametresGlobaux
from tantra.regles import cs_flexion, nombre_supports_coque, verif, verifier_pincement

PREFIXE = "fauteuil"


@dataclass(frozen=True)
class ParametresFauteuil:
    largeur: float = 780.0
    profondeur: float = 820.0
    hauteur_assise: float = 440.0
    hauteur_dossier: float = 900.0
    hauteur_accoudoir: float = 640.0
    largeur_accoudoir: float = 130.0
    epaisseur_bavette: float = 25.0
    mousse_bavette: float = 50.0
    section_bequille: float = 40.0
    globaux: ParametresGlobaux = PARAMETRES_DEFAUT

    def salon(self) -> ParametresSalon:
        return ParametresSalon(self.largeur, self.profondeur, self.hauteur_assise, self.hauteur_dossier,
                               self.hauteur_accoudoir, largeur_accoudoir=self.largeur_accoudoir,
                               epaisseur_dossier=180.0, epaisseur_bavette=self.epaisseur_bavette,
                               mousse_bavette=self.mousse_bavette, nombre_galettes=1, ancrages_arriere=False,
                               section_rail=(50.0, 140.0))


def nombre_bequilles(p: ParametresFauteuil) -> int:
    """Béquilles sous le repose-genoux : panneau en flexion entre appuis (règle des coques)."""
    g = p.globaux
    largeur = p.largeur - 2 * p.largeur_accoudoir - 30.0
    f = g.charges.poids_personne_n * g.charges.facteur_dynamique
    return max(2, nombre_supports_coque(largeur, p.section_bequille, p.epaisseur_bavette, g.essence_courbe, f))


def calculer(p: ParametresFauteuil | None = None, etat: str | int = ETAT_SALON) -> GeometrieMeuble:
    p = p or ParametresFauteuil()
    etat = etat_depuis_code(etat)
    g = p.globaux
    for nom in ("largeur", "profondeur", "hauteur_assise", "hauteur_dossier"):
        TYPO.verifier(nom, getattr(p, nom))
    s = p.salon()
    c = construire_salon(s, g, etat, PREFIXE)
    hp, hc = s.hauteur_pieds, s.hauteur_ceinture
    x0, x1 = p.largeur_accoudoir, p.largeur - p.largeur_accoudoir
    n_b = nombre_bequilles(p)
    b = p.section_bequille
    depl = hc - hp  # longueur de la bavette = porte-à-faux du repose-genoux
    for k in range(n_b):
        xb = x0 + 20.0 + k * (x1 - x0 - 40.0 - b) / (n_b - 1)
        if etat == ETAT_REVELE:
            pc = prisme(f"{PREFIXE}_bequille_{k + 1}", "bequille", "hetre", xb, -depl + 10.0, 0.0, b, b, hp,
                        "Béquille dépliée sous le chant avant du repose-genoux.")
        else:
            pc = prisme(f"{PREFIXE}_bequille_{k + 1}", "bequille", "hetre", xb, s.epaisseur_bavette, hp + 10.0,
                        b, 20.0, hp - 20.0, "Béquille repliée à plat, dans l'épaisseur de mousse de la bavette.")
        c.pieces.append(pc)
    c.assemblages.append(Assemblage(f"{PREFIXE}_bequilles_pivots", "charniere_soss", f"{PREFIXE}_bequille_*",
                                    f"{PREFIXE}_bavette", n_b, "Pivot + arrêt à bille en position dépliée."))
    v = verifier_discretion(c, etat)
    v += verifs_communes(s, g, c, etat, PREFIXE)
    ch = g.charges
    f_genoux = ch.poids_personne_n * ch.facteur_dynamique * 0.6
    portee = (x1 - x0 - 40.0) / (n_b - 1)
    cs_b = cs_flexion(portee, depl, p.epaisseur_bavette, f_genoux, g.essence_courbe, "centree")
    v.append(verif("repose_genoux_flexion", cs_b >= ch.coefficient_securite,
                   f"Repose-genoux contreplaqué {p.epaisseur_bavette:g} mm, {n_b} béquilles (portée {portee:.0f} mm), "
                   f"60 % du poids dynamique ({f_genoux:.0f} N) : CS {cs_b:.1f}."))
    v.append(verif("charnieres_bavette_effort", True,
                   "Bavette-genoux : l'effort vertical passe par les béquilles et le chant bas en appui sur la "
                   "traverse ; les charnières Soss ne guident que la rotation (à confirmer à l'essai).",
                   niveau_echec="avertissement"))
    v.append(verifier_pincement("bequille_repliage", 30.0))
    w = ch.poids_personne_n
    xm = p.largeur / 2
    z_genoux = hp + p.epaisseur_bavette + p.mousse_bavette
    cas = [
        CasStabilite("assis_pousse_dossier", ((w, xm, 300.0),),
                     (ch.effort_horizontal_exterieur_n, "+y", p.hauteur_dossier), 1.5,
                     "Personne assise, poussée de 300 N en haut du dossier."),
        CasStabilite("assis_sur_accoudoir", ((w * ch.facteur_dynamique, 30.0, p.profondeur / 2),), None,
                     COEFFICIENT_STABILITE_ACCIDENTEL_MIN, "Assis brusquement sur l'accoudoir."),
    ]
    if etat == ETAT_REVELE:
        f = w * ch.facteur_dynamique
        cas.append(CasStabilite("a_genoux", ((0.6 * f, xm, -depl / 2), (0.4 * f, xm, 200.0)),
                                (ch.effort_horizontal_exterieur_n, "-y", z_genoux + 500.0), 1.5,
                                "À genoux sur le repose-genoux, buste sur l'assise, poussée vers l'avant."))
    v_stab, infos = verifs_stabilite(list(c.pieces), cas)
    v += v_stab
    v.append(verif_traction_exterieure(c.infos["z_traverse_accoudoir"] + 60.0, infos["masse_kg"],
                                       p.profondeur / 2, ch.charge_service_ancrage_n))
    v += essais_communs(PREFIXE)
    n = len(c.ancrages)
    return GeometrieMeuble(TYPO.nom, etat, tuple(c.pieces), tuple(c.assemblages), tuple(c.ancrages), tuple(v),
                           {**c.infos, **infos, "code_etat": CODE_ETAT[etat], "nombre_bequilles": n_b,
                            "z_repose_genoux": z_genoux},
                           quincaillerie=(("insert_ancre_m12", n), ("anneau_rabattable", n)))


def calculer_etats(p: ParametresFauteuil | None = None) -> dict[str, GeometrieMeuble]:
    return {e: calculer(p, e) for e in ETATS}


def vers_parametres_fusion_fauteuil(p: ParametresFauteuil | None = None) -> dict:
    p = p or ParametresFauteuil()
    P = f"{PREFIXE_FUSION}bergere_"
    return {
        f"{P}etat": (0, "", "0 = SALON, 1 = RÉVÉLÉ."),
        f"{P}mousse_bavette": (p.mousse_bavette, "mm", "Rembourrage du repose-genoux."),
        f"{P}largeur_accoudoir": (p.largeur_accoudoir, "mm", "Largeur d'un accoudoir."),
    }


def chiffrage(p: ParametresFauteuil | None = None):
    return chiffrer(calculer(p, ETAT_SALON))
