# -*- coding: utf-8 -*-
"""Grammaire — banquette inclinée à deux niveaux (volet 1, meuble fixe).

Banquette profonde (≈ 1500 × 1050 mm) dont le profil, extrudé sur toute
la longueur, comporte :

* un **niveau bas** horizontal (assise ou agenouilloir, ~420 mm) ;
* une **contremarche arrondie** (rayon généreux, pas d'arête vive sous les
  genoux ni sous le ventre) ;
* un **niveau haut incliné** (~640 mm côté contremarche) qui descend vers
  l'arrière de ``inclinaison_niveau_haut`` : appui ventral quand on est
  agenouillé sur le niveau bas, accoudoir / dossier bas quand on est assis.

Toutes les positions combinent les deux niveaux : assis bas + appui haut,
agenouillé bas + buste sur le haut, allongé sur le haut le bassin au bord
de la contremarche, etc. Six ancrages (trois par flasque extérieure).

La longueur impose plusieurs flasques intérieures (coque portée tous les
~450 mm) : c'est le premier poste de coût de cette typologie.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import radians, tan

from tantra.chiffrage import chiffrer
from tantra.courbes import PointCle, profil_hermite
from tantra.geometrie import CasStabilite, GeometrieMeuble
from tantra.grammaires._siege import (
    ancrages_flasques,
    construire_surface,
    essais_communs,
    verif_traction_exterieure,
    verifs_stabilite,
    verifs_structure,
)
from tantra.parametres import (
    LAMELLE_HETRE,
    NIVEAU_AVERTISSEMENT,
    PARAMETRES_DEFAUT,
    PREFIXE_FUSION,
    TANTRA_BANQUETTE_DEUX_NIVEAUX as TYPO,
    Essence,
    ParametresGlobaux,
)
from tantra.regles import nombre_supports_coque, verif

ETAT_FIXE = "FIXE"


@dataclass(frozen=True)
class ParametresBanquetteDeuxNiveaux:
    longueur: float = 1500.0
    profondeur: float = 1050.0
    hauteur_niveau_bas: float = 420.0
    hauteur_niveau_haut: float = 640.0
    inclinaison_niveau_haut: float = 12.0
    profondeur_niveau_bas: float = 480.0
    """Profondeur utile du niveau bas (avant → pied de contremarche)."""
    pente_contremarche: float = 72.0
    epaisseur_flasque: float = 30.0
    epaisseur_coque: float = 18.0
    hauteur_socle: float = 60.0
    retrait_socle: float = 40.0
    n_flasques: int | None = None
    """None : calculé (coque portée par assez de flasques pour CS ≥ 3)."""
    nombre_personnes: int = 2
    essence_flasque: Essence = LAMELLE_HETRE
    globaux: ParametresGlobaux = PARAMETRES_DEFAUT

    def __post_init__(self) -> None:
        for nom in ("longueur", "profondeur", "hauteur_niveau_bas", "hauteur_niveau_haut",
                    "inclinaison_niveau_haut"):
            TYPO.verifier(nom, getattr(self, nom))
        if self.hauteur_niveau_haut - self.hauteur_niveau_bas < 120.0:
            raise ValueError("Les deux niveaux doivent différer d'au moins 120 mm.")
        if not (300.0 <= self.profondeur_niveau_bas <= self.profondeur - 350.0):
            raise ValueError("profondeur_niveau_bas hors plage (≥ 300 mm et laisse ≥ 350 mm au niveau haut).")


def points_cles(p: ParametresBanquetteDeuxNiveaux) -> tuple[PointCle, ...]:
    hb, hh = p.hauteur_niveau_bas, p.hauteur_niveau_haut
    db = p.profondeur_niveau_bas
    dz = hh - hb
    dy_cm = dz / tan(radians(p.pente_contremarche))
    y_haut = db + dy_cm + 120.0
    z_fin = hh - (p.profondeur - 60.0 - y_haut) * tan(radians(p.inclinaison_niveau_haut))
    return (
        PointCle(0.0, hb - 40.0, 45.0, "nez"),
        PointCle(80.0, hb, 0.0, "niveau_bas_debut"),
        PointCle(db - 60.0, hb, 0.0, "niveau_bas_fin"),
        PointCle(db + dy_cm / 2.0 + 30.0, (hb + hh) / 2.0, p.pente_contremarche, "contremarche"),
        PointCle(y_haut, hh, -p.inclinaison_niveau_haut, "niveau_haut_debut"),
        PointCle(p.profondeur - 60.0, z_fin, -p.inclinaison_niveau_haut, "niveau_haut_fin"),
        PointCle(p.profondeur, z_fin - 35.0, -60.0, "retombee"),
    )


def profil(p: ParametresBanquetteDeuxNiveaux) -> list[tuple[float, float]]:
    return profil_hermite(points_cles(p), n_par_segment=16, tension=0.9)


def profil_structure(p: ParametresBanquetteDeuxNiveaux) -> list[tuple[float, float]]:
    """Dessus de coque : profil adouci (nez, arêtes et retombée formés en mousse).

    La coque cintrée ne suit que les grandes inflexions (rayons ≥ 150 mm) ;
    les arrondis serrés (nez, retombée) sont donnés par la mousse HR 55.
    """
    from tantra.courbes import decaler
    hb, hh = p.hauteur_niveau_bas, p.hauteur_niveau_haut
    db = p.profondeur_niveau_bas
    dy_cm = (hh - hb) / tan(radians(p.pente_contremarche))
    y_mid = db + dy_cm / 2.0 + 30.0
    y_haut = db + dy_cm + 120.0
    z_fin = hh - (p.profondeur - y_haut - 140.0) * tan(radians(p.inclinaison_niveau_haut))
    pc = (
        PointCle(10.0, hb, 0.0, "s_avant"),
        PointCle(db - 240.0, hb, 0.0, "s_bas"),
        PointCle(y_haut + 140.0, hh, -p.inclinaison_niveau_haut, "s_haut"),
        PointCle(p.profondeur - 10.0, z_fin - 10.0, -p.inclinaison_niveau_haut, "s_arriere"),
    )
    ep = p.globaux.epaisseur_mousse_assise_mm + p.globaux.revetement_tantra.epaisseur_mm
    return decaler(profil_hermite(pc, n_par_segment=16, tension=1.0), -ep)


def n_flasques_requis(p: ParametresBanquetteDeuxNiveaux) -> int:
    c = p.globaux.charges
    return nombre_supports_coque(p.longueur, p.epaisseur_flasque, p.epaisseur_coque,
                                 p.globaux.essence_courbe, c.poids_personne_n * c.facteur_dynamique,
                                 cs=c.coefficient_securite)


def _ergonomie(p: ParametresBanquetteDeuxNiveaux) -> list:
    a = p.globaux.anthropometrie
    marche = p.hauteur_niveau_haut - p.hauteur_niveau_bas
    return [
        verif("ergo_niveau_bas_assise",
              a.hauteur_poplitee.p5 <= p.hauteur_niveau_bas <= a.hauteur_poplitee.p95,
              f"Niveau bas {p.hauteur_niveau_bas:g} mm dans la plage poplitée P5–P95 "
              f"({a.hauteur_poplitee.p5:g}–{a.hauteur_poplitee.p95:g} mm) : utilisable en assise.",
              niveau_echec=NIVEAU_AVERTISSEMENT),
        verif("ergo_profondeur_bas", p.profondeur_niveau_bas >= a.longueur_fesse_poplite.p5,
              f"Profondeur du niveau bas {p.profondeur_niveau_bas:g} mm ≥ fesse-poplité P5 "
              f"{a.longueur_fesse_poplite.p5:g} mm.", niveau_echec=NIVEAU_AVERTISSEMENT),
        verif("ergo_hauteur_marche",
              a.hauteur_coude_assis.p5 <= marche <= a.hauteur_coude_assis.p95 + 30.0,
              f"Contremarche {marche:g} mm ≈ hauteur coude assis P5–P95 ({a.hauteur_coude_assis.p5:g}–"
              f"{a.hauteur_coude_assis.p95:g} mm) : le niveau haut sert d'accoudoir assis, et d'appui "
              "ventral (hanches au bord) agenouillé sur le niveau bas.", niveau_echec=NIVEAU_AVERTISSEMENT),
        verif("ergo_profondeur_haut", p.profondeur - p.profondeur_niveau_bas >= 450.0,
              f"Niveau haut {p.profondeur - p.profondeur_niveau_bas:.0f} mm de profondeur (≥ 450 mm pour "
              "y poser le buste ou s'y asseoir).", niveau_echec=NIVEAU_AVERTISSEMENT),
        verif("ergo_longueur_allonge", p.longueur >= a.stature.p50 * 0.85,
              f"Longueur {p.longueur:g} mm : allongé en travers sur le niveau haut, tête et jambes "
              "dépassent pour un grand gabarit (choix d'encombrement, pas un lit).",
              compromis=True, niveau_echec=NIVEAU_AVERTISSEMENT),
    ]


def calculer(p: ParametresBanquetteDeuxNiveaux | None = None) -> GeometrieMeuble:
    p = p or ParametresBanquetteDeuxNiveaux()
    g = p.globaux
    n = p.n_flasques or n_flasques_requis(p)
    pts = profil(p)
    pc = {k.nom: k for k in points_cles(p)}
    surf = construire_surface(
        "banquette", pts, 0.0, p.longueur, n, p.epaisseur_flasque, p.epaisseur_coque,
        g.epaisseur_mousse_assise_mm, p.hauteur_socle, g, g.revetement_tantra, p.essence_flasque,
        traverses_y=(pc["niveau_bas_fin"].y - 120.0, pc["niveau_haut_debut"].y + 140.0),
        retrait_socle=p.retrait_socle,
        dessus_structure=profil_structure(p),
    )
    blocs, ancrages, ass_anc, v_anc = ancrages_flasques(
        "banquette", surf, (pc["niveau_bas_debut"].y + 120.0, pc["niveau_haut_debut"].y + 60.0,
                            pc["niveau_haut_fin"].y - 60.0),
        p.epaisseur_flasque, g, 0.0, p.longueur)
    pieces = list(surf.pieces) + blocs
    v = _ergonomie(p)
    v += verifs_structure("banquette", surf, g, p.longueur, p.epaisseur_flasque, p.epaisseur_coque,
                          p.nombre_personnes)
    v += v_anc
    c = g.charges
    f1 = c.poids_personne_n * c.facteur_dynamique
    xm = p.longueur / 2.0
    cas = [
        CasStabilite("agenouille_au_nez", ((f1, xm, 20.0),), None, 1.5,
                     "Une personne (dynamique) agenouillée sur l'arête avant."),
        CasStabilite("assis_retombee", ((f1, xm, p.profondeur - 20.0),), None, 1.5,
                     "Une personne assise sur l'arête arrière du niveau haut."),
        CasStabilite("poussee_longitudinale", ((c.poids_personne_n, 60.0, pc["niveau_bas_fin"].y),),
                     (c.effort_horizontal_exterieur_n, "-x", p.hauteur_niveau_haut), 1.5,
                     "Une personne assise en bout + poussée de 300 N."),
    ]
    v_stab, infos = verifs_stabilite(pieces, cas)
    v += v_stab
    v.append(verif_traction_exterieure(max(a.position[2] for a in ancrages), infos["masse_kg"],
                                       p.longueur / 2.0 - p.retrait_socle, c.charge_service_ancrage_n))
    v += essais_communs("banquette")
    derivees = {"points_cles": points_cles(p), "rayon_min_coque_mm": surf.rayon_min_mm,
                "n_flasques": n, **infos}
    return GeometrieMeuble(TYPO.nom, ETAT_FIXE, tuple(pieces), tuple(list(surf.assemblages) + ass_anc),
                           tuple(ancrages), tuple(v), derivees,
                           quincaillerie=(("insert_ancre_m12", len(ancrages)), ("anneau_rabattable", len(ancrages))))


def calculer_etats(p: ParametresBanquetteDeuxNiveaux | None = None) -> dict[str, GeometrieMeuble]:
    return {ETAT_FIXE: calculer(p)}


def vers_parametres_fusion_banquette(p: ParametresBanquetteDeuxNiveaux | None = None) -> dict:
    p = p or ParametresBanquetteDeuxNiveaux()
    P = f"{PREFIXE_FUSION}banquette2n_"
    return {
        f"{P}profondeur_niveau_bas": (p.profondeur_niveau_bas, "mm", "Profondeur utile du niveau bas."),
        f"{P}pente_contremarche": (p.pente_contremarche, "deg", "Pente de la contremarche arrondie."),
        f"{P}n_flasques": (float(p.n_flasques or n_flasques_requis(p)), "", "Nombre de flasques (calculé)."),
    }


def chiffrage(p: ParametresBanquetteDeuxNiveaux | None = None):
    return chiffrer(calculer(p))
