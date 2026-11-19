# -*- coding: utf-8 -*-
"""Grammaire — fauteuil bas à cale fessière et appui lombaire intégrés (volet 1).

Fauteuil sans accoudoirs, assise basse et large (deux personnes assises
enlacées face à face, ou une personne assise en tailleur), en coque
continue assise + dossier.

Profil défini par points-clés (courbe d'Hermite, y vers l'arrière) :

* ``nez`` → ``cale`` : la **cale fessière** est une bosse transversale
  arrondie à l'avant de l'assise (``hauteur_cale`` au-dessus de la ligne
  d'assise). Assis normalement, elle soutient le dessous des cuisses et
  empêche de glisser ; assis à califourchon ou à rebours, elle relève le
  bassin (même rôle que la petite courbe de la chaise tantrique) ;
* ``ischions`` : point d'assise de référence, ``hauteur_assise`` ;
* ``pli`` : raccord assise / dossier (rayon généreux) ;
* ``lombaire`` : bombé de ``saillie_lombaire`` vers l'avant, centré à
  ``hauteur_lombaire`` au-dessus de l'assise (150–250 mm, Pheasant) ;
* ``sommet`` : haut du dossier.

Les flasques extérieures, pleines jusqu'au sol, dessinent la silhouette ;
une flasque intérieure (non vue) soutient la coque au centre.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import cos, radians, sin, tan

from tantra.chiffrage import chiffrer
from tantra.courbes import PointCle, profil_hermite, z_a
from tantra.geometrie import CasStabilite, GeometrieMeuble
from tantra.grammaires._siege import (
    COEFFICIENT_STABILITE_ACCIDENTEL_MIN,
    ancrages_flasques,
    construire_surface,
    essais_communs,
    verif_traction_exterieure,
    verifs_stabilite,
    verifs_structure,
)
from tantra.parametres import (
    CHENE,
    NIVEAU_AVERTISSEMENT,
    PARAMETRES_DEFAUT,
    PREFIXE_FUSION,
    TANTRA_FAUTEUIL_LOMBAIRE as TYPO,
    Essence,
    ParametresGlobaux,
)
from tantra.regles import verif

ETAT_FIXE = "FIXE"


@dataclass(frozen=True)
class ParametresFauteuilLombaire:
    largeur: float = 760.0
    hauteur_assise: float = 340.0
    profondeur_assise: float = 440.0
    """Distance horizontale nez de cale → ischions + 130 mm (assise utile)."""
    inclinaison_assise: float = 12.0
    angle_dossier: float = 108.0
    hauteur_dossier: float = 820.0
    hauteur_cale: float = 45.0
    """Saillie de la cale fessière au-dessus de la ligne d'assise prolongée."""
    hauteur_lombaire: float = 200.0
    saillie_lombaire: float = 25.0
    epaisseur_flasque: float = 32.0
    epaisseur_coque: float = 21.0
    hauteur_socle: float = 50.0
    retrait_socle: float = 20.0
    n_flasques: int = 3
    nombre_personnes: int = 2
    essence_flasque: Essence = CHENE
    globaux: ParametresGlobaux = PARAMETRES_DEFAUT

    def __post_init__(self) -> None:
        for nom in ("largeur", "hauteur_assise", "profondeur_assise", "inclinaison_assise",
                    "angle_dossier", "hauteur_dossier"):
            TYPO.verifier(nom, getattr(self, nom))
        if not (0.0 <= self.hauteur_cale <= 80.0):
            raise ValueError("hauteur_cale attendue entre 0 et 80 mm.")

    @property
    def inclinaison_dossier(self) -> float:
        """Angle du dossier sur l'horizontale (degrés)."""
        return 180.0 - self.angle_dossier - self.inclinaison_assise


def points_cles(p: ParametresFauteuilLombaire) -> tuple[PointCle, ...]:
    th = p.inclinaison_assise
    phi = p.inclinaison_dossier
    y_isch = p.profondeur_assise - 130.0 + 60.0  # nez de cale à y = 60
    y_cale = 120.0
    z_cale = p.hauteur_assise + (y_isch - y_cale) * tan(radians(th)) + p.hauteur_cale
    # Pied (virtuel) du dossier : 130 mm derrière les ischions, sur la ligne d'assise.
    # Le raccord assise/dossier n'a pas de point-clé : la cubique d'Hermite entre
    # « ischions » et « lombaire » donne un pli de grand rayon (cintrable).
    y_pli = y_isch + 130.0
    z_pli = p.hauteur_assise - 130.0 * tan(radians(th))
    # Point lombaire : sur la ligne de dossier, puis saillie vers l'avant (normale)
    d_lomb = p.hauteur_lombaire / sin(radians(phi))
    y_l = y_pli + d_lomb * cos(radians(phi)) - p.saillie_lombaire * sin(radians(phi))
    z_l = z_pli + d_lomb * sin(radians(phi)) + p.saillie_lombaire * cos(radians(phi))
    y_top = y_pli + (p.hauteur_dossier - z_pli) / tan(radians(phi))
    return (
        PointCle(0.0, z_cale - 45.0, 40.0, "nez"),
        PointCle(y_cale, z_cale, -th, "cale"),
        PointCle(y_isch, p.hauteur_assise, -th, "ischions"),
        PointCle(y_l, z_l, phi, "lombaire"),
        PointCle(y_top, p.hauteur_dossier, phi + 15.0, "sommet"),
    )


def profil(p: ParametresFauteuilLombaire) -> list[tuple[float, float]]:
    return profil_hermite(points_cles(p), n_par_segment=18, tension=1.1)


def profil_structure(p: ParametresFauteuilLombaire) -> list[tuple[float, float]]:
    """Dessus de coque : même profil sans la cale (formée en mousse HR 55), décalé.

    La cale fessière est une surépaisseur de mousse : la coque reste cintrable
    (rayons ≥ 150 mm) et la cale peut être refaite sans toucher au bois.
    """
    from tantra.courbes import decaler
    pc = list(points_cles(p))
    isch = pc[2]
    z0 = isch.z + isch.y * tan(radians(p.inclinaison_assise)) - 10.0
    # Avant de la coque : droite dans le prolongement de l'assise, cale et nez en mousse.
    pc = [PointCle(0.0, z0, -p.inclinaison_assise, "nez_structure")] + pc[2:]
    ep = p.globaux.epaisseur_mousse_assise_mm + p.globaux.revetement_tantra.epaisseur_mm
    return decaler(profil_hermite(pc, n_par_segment=18, tension=1.1), -ep)


def _ergonomie(p: ParametresFauteuilLombaire) -> list:
    a = p.globaux.anthropometrie
    v = [
        verif("ergo_hauteur_assise", p.hauteur_assise <= a.hauteur_poplitee.p5 + 20.0,
              f"Assise {p.hauteur_assise:g} mm ≤ poplité P5 {a.hauteur_poplitee.p5:g} + 20 mm : pieds au sol "
              f"pour tous ; volontairement bas (genoux au-dessus des hanches pour P95 "
              f"{a.hauteur_poplitee.p95:g} mm, posture enveloppée recherchée).",
              niveau_echec=NIVEAU_AVERTISSEMENT),
        verif("ergo_profondeur", p.profondeur_assise <= a.longueur_fesse_poplite.p5 + 10.0,
              f"Profondeur utile {p.profondeur_assise:g} mm ≤ fesse-poplité P5 {a.longueur_fesse_poplite.p5:g} "
              "+ 10 mm : un petit gabarit atteint le dossier sans compression du creux poplité.",
              compromis=p.profondeur_assise > a.longueur_fesse_poplite.p5 + 10.0,
              niveau_echec=NIVEAU_AVERTISSEMENT),
        verif("ergo_lombaire", a.appui_lombaire_min_mm <= p.hauteur_lombaire <= a.appui_lombaire_max_mm,
              f"Centre du bombé lombaire à {p.hauteur_lombaire:g} mm au-dessus de l'assise "
              f"(plage {a.appui_lombaire_min_mm:g}–{a.appui_lombaire_max_mm:g} mm).",
              niveau_echec=NIVEAU_AVERTISSEMENT),
        verif("ergo_angle_dossier", 100.0 <= p.angle_dossier <= 115.0,
              f"Angle assise/dossier {p.angle_dossier:g}° (100–115° : détente sans perdre le soutien "
              "lombaire ; au-delà, le bassin glisse en rétroversion).", niveau_echec=NIVEAU_AVERTISSEMENT),
        verif("ergo_hauteur_dossier",
              p.hauteur_dossier - p.hauteur_assise >= a.hauteur_epaules_assis.p5 - 50.0,
              f"Dossier {p.hauteur_dossier - p.hauteur_assise:.0f} mm au-dessus de l'assise ≥ épaules P5 "
              f"{a.hauteur_epaules_assis.p5:g} − 50 mm : omoplates soutenues ; nuque libre (pas d'appui-tête).",
              niveau_echec=NIVEAU_AVERTISSEMENT),
        verif("ergo_largeur_duo", p.largeur >= a.largeur_hanches_assis.p95 + 2 * 100.0,
              f"Largeur {p.largeur:g} mm ≥ hanches P95 {a.largeur_hanches_assis.p95:g} + 2 × 100 mm "
              "(genoux de la personne assise à califourchon de part et d'autre).",
              niveau_echec=NIVEAU_AVERTISSEMENT),
    ]
    return v


def calculer(p: ParametresFauteuilLombaire | None = None) -> GeometrieMeuble:
    p = p or ParametresFauteuilLombaire()
    g = p.globaux
    pts = profil(p)
    pc = {k.nom: k for k in points_cles(p)}
    surf = construire_surface(
        "fauteuil", pts, 0.0, p.largeur, p.n_flasques, p.epaisseur_flasque, p.epaisseur_coque,
        g.epaisseur_mousse_assise_mm, p.hauteur_socle, g, g.revetement_tantra, p.essence_flasque,
        traverses_y=(pc["cale"].y - 20.0, pc["ischions"].y - 30.0),
        retrait_socle=p.retrait_socle,
        dessus_structure=profil_structure(p),
    )
    blocs, ancrages, ass_anc, v_anc = ancrages_flasques(
        "fauteuil", surf, (pc["cale"].y + 40.0,), p.epaisseur_flasque, g, 0.0, p.largeur)
    pieces = list(surf.pieces) + blocs
    v = _ergonomie(p)
    v += verifs_structure("fauteuil", surf, g, p.largeur, p.epaisseur_flasque, p.epaisseur_coque,
                          p.nombre_personnes)
    v += v_anc
    c = g.charges
    f1 = c.poids_personne_n * c.facteur_dynamique
    xm = p.largeur / 2.0
    y_top = pc["sommet"].y
    cas = [
        CasStabilite("duo_assis_poussee_dossier",
                     ((2 * c.poids_personne_n, xm, pc["ischions"].y),),
                     (c.effort_horizontal_exterieur_n, "+y", p.hauteur_dossier), 1.5,
                     "Deux personnes assises + poussée de 300 N vers l'arrière en haut du dossier."),
        CasStabilite("assis_sur_le_nez", ((f1, xm, 20.0),), None, 1.5,
                     "Une personne (dynamique) assise sur l'extrême avant de la cale."),
        CasStabilite("appui_sommet_dossier", ((f1, xm, y_top - 20.0),), None, 1.5,
                     "Une personne appuyée sur le haut du dossier (par derrière)."),
        CasStabilite("assis_bord_lateral", ((c.poids_personne_n, 60.0, pc["ischions"].y),),
                     (c.effort_horizontal_exterieur_n, "-x", p.hauteur_assise),
                     COEFFICIENT_STABILITE_ACCIDENTEL_MIN, "Assis au bord + poussée latérale accidentelle."),
    ]
    v_stab, infos = verifs_stabilite(pieces, cas)
    v += v_stab
    v.append(verif_traction_exterieure(ancrages[0].position[2], infos["masse_kg"],
                                       p.largeur / 2.0 - p.retrait_socle, c.charge_service_ancrage_n))
    v += essais_communs("fauteuil")
    derivees = {"points_cles": points_cles(p), "rayon_min_coque_mm": surf.rayon_min_mm,
                "inclinaison_dossier_deg": p.inclinaison_dossier,
                "n_flasques": len(surf.positions_flasques), **infos}
    return GeometrieMeuble(TYPO.nom, ETAT_FIXE, tuple(pieces), tuple(list(surf.assemblages) + ass_anc),
                           tuple(ancrages), tuple(v), derivees,
                           quincaillerie=(("insert_ancre_m12", len(ancrages)), ("anneau_rabattable", len(ancrages))))


def calculer_etats(p: ParametresFauteuilLombaire | None = None) -> dict[str, GeometrieMeuble]:
    return {ETAT_FIXE: calculer(p)}


def vers_parametres_fusion_fauteuil(p: ParametresFauteuilLombaire | None = None) -> dict:
    p = p or ParametresFauteuilLombaire()
    P = f"{PREFIXE_FUSION}lombaire_"
    return {
        f"{P}hauteur_cale": (p.hauteur_cale, "mm", "Saillie de la cale fessière."),
        f"{P}hauteur_lombaire": (p.hauteur_lombaire, "mm", "Centre du bombé lombaire au-dessus de l'assise."),
        f"{P}saillie_lombaire": (p.saillie_lombaire, "mm", "Saillie du bombé lombaire."),
        f"{P}ep_flasque": (p.epaisseur_flasque, "mm", "Épaisseur des flasques chêne."),
        f"{P}ep_coque": (p.epaisseur_coque, "mm", "Épaisseur de la coque cintrée."),
    }


def chiffrage(p: ParametresFauteuilLombaire | None = None):
    return chiffrer(calculer(p))
