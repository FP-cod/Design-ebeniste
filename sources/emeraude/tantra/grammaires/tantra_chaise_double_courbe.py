# -*- coding: utf-8 -*-
"""Grammaire — chaise longue tantrique à double courbe (volet 1, meuble fixe).

Profil en S défini par cinq points-clés (courbe d'Hermite) :

1. ``nez`` — départ avant arrondi ;
2. ``petite_bosse`` — sommet de la cale fessière (relève le bassin quand on
   s'allonge dessus sur le dos ou sur le ventre ; appui de cuisses quand on
   s'assoit dans le creux face à l'avant) ;
3. ``creux`` — point bas, assise principale ;
4. ``flanc`` — point d'inflexion de la grande courbe (appui lombaire/dorsal) ;
5. ``sommet`` — sommet de la grande courbe, puis ``retombee`` (appui-tête
   ou appui ventral selon le sens d'usage).

Fonction assumée : meuble fixe, non camouflé, quatre anneaux rabattables
affleurants (deux à hauteur du creux, deux près du sommet).

Compromis principaux (voir ``docs/tantra_chaise_double_courbe.md``) :
une largeur faible (≈ 600 mm) est plus enveloppante et plus élégante mais
réduit la stabilité latérale ; une petite bosse haute ouvre plus le bassin
mais rend l'assise dans le creux moins confortable pour les petits gabarits.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace

from tantra.catalogues.couts import masses_volumiques
from tantra.chiffrage import chiffrer
from tantra.courbes import PointCle, angle_a, extremum_local, longueur, profil_hermite, z_a
from tantra.geometrie import CasStabilite, GeometrieMeuble, masse_et_cdg
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
    LAMELLE_HETRE,
    NIVEAU_AVERTISSEMENT,
    PARAMETRES_DEFAUT,
    PREFIXE_FUSION,
    TANTRA_CHAISE_DOUBLE_COURBE as TYPO,
    Essence,
    ParametresGlobaux,
)
from tantra.regles import verif

ETAT_FIXE = "FIXE"


@dataclass(frozen=True)
class ParametresChaiseDoubleCourbe:
    """Paramètres de la chaise double courbe (mm, degrés).

    Les cinq premières cotes sont bornées par ``parametres.TANTRA_CHAISE_DOUBLE_COURBE``.
    """

    longueur: float = 1850.0
    largeur: float = 600.0
    hauteur_petite_bosse: float = 470.0
    hauteur_creux: float = 330.0
    hauteur_grande_courbe: float = 760.0
    position_petite_bosse: float = 300.0
    """Abscisse du sommet de la petite bosse depuis l'avant."""
    position_creux: float = 760.0
    position_flanc: float = 1200.0
    hauteur_nez: float = 300.0
    retombee: float = 110.0
    """Hauteur perdue par l'appui-tête après le sommet."""
    angle_flanc: float = 38.0
    """Pente de la grande courbe au point d'inflexion (degrés)."""
    epaisseur_flasque: float = 30.0
    epaisseur_coque: float = 18.0
    hauteur_socle: float = 60.0
    retrait_socle: float = 40.0
    n_flasques: int = 3
    nombre_personnes: int = 2
    positions_ancrages: tuple[float, ...] = (760.0, 1560.0)
    essence_flasque: Essence = LAMELLE_HETRE
    globaux: ParametresGlobaux = PARAMETRES_DEFAUT

    def __post_init__(self) -> None:
        for nom in ("longueur", "largeur", "hauteur_petite_bosse", "hauteur_creux", "hauteur_grande_courbe"):
            TYPO.verifier(nom, getattr(self, nom))
        if not (0 < self.position_petite_bosse < self.position_creux < self.position_flanc < self.longueur - 150):
            raise ValueError("Ordre attendu : 0 < petite bosse < creux < flanc < longueur − 150 mm.")
        if not (self.hauteur_creux < self.hauteur_petite_bosse < self.hauteur_grande_courbe):
            raise ValueError("Il faut creux < petite bosse < grande courbe.")


def points_cles(p: ParametresChaiseDoubleCourbe) -> tuple[PointCle, ...]:
    """Points-clés du profil fini (dessus revêtement)."""
    y_sommet = p.longueur - 300.0
    z_flanc = (p.hauteur_creux + p.hauteur_grande_courbe) / 2.0 + 20.0
    return (
        PointCle(0.0, p.hauteur_nez, 55.0, "nez"),
        PointCle(p.position_petite_bosse, p.hauteur_petite_bosse, 0.0, "petite_bosse"),
        PointCle(p.position_creux, p.hauteur_creux, 0.0, "creux"),
        PointCle(p.position_flanc, z_flanc, p.angle_flanc, "flanc"),
        PointCle(y_sommet, p.hauteur_grande_courbe, 0.0, "sommet"),
        PointCle(p.longueur, p.hauteur_grande_courbe - p.retombee, -38.0, "retombee"),
    )


def profil(p: ParametresChaiseDoubleCourbe) -> list[tuple[float, float]]:
    return profil_hermite(points_cles(p), n_par_segment=20, tension=0.9)


def _ergonomie(p: ParametresChaiseDoubleCourbe, pts: list[tuple[float, float]]) -> list:
    a = p.globaux.anthropometrie
    v = []
    # 1. Longueur d'assise dans le creux (entre la petite bosse et le point où la
    #    grande courbe s'est élevée de 150 mm) : doit loger fesses + cuisses P95.
    z_seuil = p.hauteur_creux + 150.0
    y_seuil = next(y for y, z in pts if y > p.position_creux and z >= z_seuil)
    longueur_creux = y_seuil - p.position_petite_bosse
    v.append(verif("ergo_longueur_creux",
                   a.longueur_fesse_poplite.p5 <= longueur_creux,
                   f"Creux d'assise {longueur_creux:.0f} mm (petite bosse → +150 mm de grande courbe) "
                   f"≥ fesse-poplité P5 {a.longueur_fesse_poplite.p5:g} mm : assise possible dans le creux, "
                   f"cuisses sur la petite bosse.", niveau_echec=NIVEAU_AVERTISSEMENT))
    # 2. Élévation du bassin par la petite bosse
    elev = p.hauteur_petite_bosse - p.hauteur_creux
    v.append(verif("ergo_elevation_bassin", 100.0 <= elev <= 200.0,
                   f"Petite bosse {elev:.0f} mm au-dessus du creux (plage de conception 100–200 mm : "
                   "en dessous l'effet de bascule du bassin est faible, au-delà l'assise dans le creux "
                   "comprime l'arrière des cuisses).", compromis=not (100.0 <= elev <= 200.0),
                   niveau_echec=NIVEAU_AVERTISSEMENT))
    # 3. Pente de la grande courbe à hauteur lombaire
    y_lomb = next(y for y, z in pts if y > p.position_creux and z >= p.hauteur_creux + 200.0)
    pente = angle_a(pts, y_lomb)
    v.append(verif("ergo_pente_lombaire", 25.0 <= pente <= 55.0,
                   f"Pente de la grande courbe à 200 mm au-dessus du creux : {pente:.0f}° (plage 25–55° : "
                   "assez redressée pour soutenir le dos assis, assez couchée pour s'y allonger).",
                   niveau_echec=NIVEAU_AVERTISSEMENT))
    # 4. Longueur développée du creux au bout : tronc + tête P95
    i_creux = min(range(len(pts)), key=lambda i: abs(pts[i][0] - p.position_creux))
    l_dos = longueur(pts[i_creux:])
    v.append(verif("ergo_longueur_dos", l_dos >= a.hauteur_assis.p95,
                   f"Longueur développée creux → extrémité {l_dos:.0f} mm ≥ hauteur assis P95 "
                   f"{a.hauteur_assis.p95:g} mm (tronc et tête soutenus allongé).",
                   niveau_echec=NIVEAU_AVERTISSEMENT))
    # 5. Largeur
    mini = a.largeur_hanches_assis.p95 + 2 * 50.0
    v.append(verif("ergo_largeur", p.largeur >= mini,
                   f"Largeur {p.largeur:g} mm ≥ hanches assis P95 {a.largeur_hanches_assis.p95:g} + 2 × 50 = "
                   f"{mini:g} mm. Au-delà de ~650 mm, l'appui des genoux de part et d'autre devient "
                   "difficile pour les petits gabarits (compromis enveloppement / stabilité).",
                   niveau_echec=NIVEAU_AVERTISSEMENT))
    return v


def calculer(p: ParametresChaiseDoubleCourbe | None = None) -> GeometrieMeuble:
    """Géométrie complète (meuble fixe : un seul état)."""
    p = p or ParametresChaiseDoubleCourbe()
    g = p.globaux
    pts = profil(p)
    surf = construire_surface(
        "chaise", pts, 0.0, p.largeur, p.n_flasques, p.epaisseur_flasque, p.epaisseur_coque,
        g.epaisseur_mousse_assise_mm, p.hauteur_socle, g, g.revetement_tantra, p.essence_flasque,
        traverses_y=(p.position_petite_bosse - 40.0, p.position_creux - 40.0, p.position_flanc),
        retrait_socle=p.retrait_socle,
    )
    blocs, ancrages, ass_anc, v_anc = ancrages_flasques("chaise", surf, p.positions_ancrages,
                                                        p.epaisseur_flasque, g, 0.0, p.largeur)
    pieces = list(surf.pieces) + blocs
    assemblages = list(surf.assemblages) + ass_anc
    v = _ergonomie(p, pts)
    v += verifs_structure("chaise", surf, g, p.largeur, p.epaisseur_flasque, p.epaisseur_coque,
                          p.nombre_personnes)
    v += v_anc
    c = g.charges
    f1 = c.poids_personne_n * c.facteur_dynamique
    x_mil = p.largeur / 2.0
    cas = [
        CasStabilite("assis_sur_le_nez", ((f1, x_mil, 30.0),), None, 1.5,
                     "Une personne (charge dynamique) assise sur l'extrême avant."),
        CasStabilite("appui_sur_la_retombee", ((f1, x_mil, p.longueur - 30.0),), None, 1.5,
                     "Une personne appuyée sur l'extrémité de l'appui-tête."),
        CasStabilite("assis_bord_lateral", ((c.poids_personne_n, 60.0, p.position_creux),),
                     (c.effort_horizontal_exterieur_n, "-x", p.hauteur_creux), COEFFICIENT_STABILITE_ACCIDENTEL_MIN,
                     "Une personne assise au bord du creux + poussée latérale accidentelle."),
        CasStabilite("vide_poussee_sommet", (), (c.effort_horizontal_exterieur_n / 2, "-x", p.hauteur_grande_courbe),
                     COEFFICIENT_STABILITE_ACCIDENTEL_MIN,
                     "Meuble vide, poussée latérale de 150 N au sommet."),
    ]
    v_stab, infos = verifs_stabilite(pieces, cas)
    v += v_stab
    z_anc = max(a.position[2] for a in ancrages)
    v.append(verif_traction_exterieure(z_anc, infos["masse_kg"], p.largeur / 2.0 - p.retrait_socle,
                                       c.charge_service_ancrage_n))
    v += essais_communs("chaise")
    derivees = {
        "points_cles": points_cles(p),
        "rayon_min_coque_mm": surf.rayon_min_mm,
        "longueur_developpee_mm": surf.longueur_developpee_mm,
        "n_flasques": len(surf.positions_flasques),
        **infos,
    }
    return GeometrieMeuble(TYPO.nom, ETAT_FIXE, tuple(pieces), tuple(assemblages), tuple(ancrages),
                           tuple(v), derivees, quincaillerie=(("insert_ancre_m12", len(ancrages)),
                                                              ("anneau_rabattable", len(ancrages))))


def calculer_etats(p: ParametresChaiseDoubleCourbe | None = None) -> dict[str, GeometrieMeuble]:
    return {ETAT_FIXE: calculer(p)}


def vers_parametres_fusion_chaise(p: ParametresChaiseDoubleCourbe | None = None) -> dict:
    p = p or ParametresChaiseDoubleCourbe()
    P = f"{PREFIXE_FUSION}chaise_"
    return {
        f"{P}position_petite_bosse": (p.position_petite_bosse, "mm", "Abscisse du sommet de la cale fessière."),
        f"{P}position_creux": (p.position_creux, "mm", "Abscisse du point bas."),
        f"{P}position_flanc": (p.position_flanc, "mm", "Abscisse de l'inflexion de la grande courbe."),
        f"{P}angle_flanc": (p.angle_flanc, "deg", "Pente au point d'inflexion."),
        f"{P}ep_flasque": (p.epaisseur_flasque, "mm", "Épaisseur des flasques (lamellé-collé)."),
        f"{P}ep_coque": (p.epaisseur_coque, "mm", "Épaisseur de la coque cintrée."),
        f"{P}n_flasques": (float(p.n_flasques), "", "Nombre de flasques. Sans unité."),
    }


def chiffrage(p: ParametresChaiseDoubleCourbe | None = None):
    return chiffrer(calculer(p))
