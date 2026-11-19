# -*- coding: utf-8 -*-
"""Grammaire — siège à assise inclinée avec repose-genoux (volet 1, meuble fixe).

Dérivé élargi de la chaise « assis-genoux » (assise inclinée vers l'avant,
tibias en appui sur des coussins) : la position ouvre l'angle tronc-cuisse
(~115–120°), bascule le bassin en antéversion et laisse le dos libre —
position chevauchée stable pour une personne assise face à une autre, ou
assise sur les genoux de l'autre.

Structure : deux **cadres latéraux** en frêne (patin traîneau cintré,
montant d'assise, montant de genoux, écharpe de triangulation) reliés par
des **traverses à tenons** ; assise et repose-genoux en contreplaqué
rembourré. Pas de coque : c'est la typologie la plus légère et la moins
chère de la gamme, mais aussi la plus exigeante en réglage (un seul jeu
de cotes ne convient pas à tous les gabarits, voir compromis).

Source ergonomique de principe : A. C. Mandal, « The seated man (Homo
sedens) », Applied Ergonomics 12(1), 1981 (assises inclinées vers l'avant).
"""

from __future__ import annotations

from dataclasses import dataclass
from math import atan2, cos, degrees, hypot, radians, sin

from tantra.chiffrage import chiffrer
from tantra.courbes import PointCle, decaler, polygone_entre, profil_hermite, rectangle, tourner
from tantra.geometrie import Ancrage, Assemblage, CasStabilite, GeometrieMeuble, piece_profil, prisme
from tantra.grammaires._siege import (
    COEFFICIENT_STABILITE_ACCIDENTEL_MIN,
    essais_communs,
    verif_traction_exterieure,
    verifs_stabilite,
)
from tantra.parametres import (
    FRENE,
    NIVEAU_AVERTISSEMENT,
    PARAMETRES_DEFAUT,
    PREFIXE_FUSION,
    TANTRA_SIEGE_REPOSE_GENOUX as TYPO,
    Essence,
    ParametresGlobaux,
)
from tantra.regles import cs_flexion, cs_tenon, rayon_cintrage_minimal_mm, recaler_bloc_ancrage, verif
from tantra.courbes import rayon_courbure_min

ETAT_FIXE = "FIXE"


@dataclass(frozen=True)
class ParametresSiegeReposeGenoux:
    largeur: float = 620.0
    hauteur_assise: float = 560.0
    inclinaison_assise: float = 22.0
    hauteur_repose_genoux: float = 320.0
    distance_assise_genoux: float = 470.0
    profondeur_assise: float = 380.0
    profondeur_genoux: float = 170.0
    inclinaison_genoux: float = 30.0
    """Pente du coussin de genoux (descend vers l'arrière, parallèle aux tibias)."""
    longueur_patin: float = 1060.0
    epaisseur_cadre: float = 50.0
    """Épaisseur (selon x) des montants et patins : ≥ épaisseur du bloc d'ancrage."""
    section_montant: float = 70.0
    hauteur_patin: float = 44.0
    epaisseur_panneau: float = 18.0
    mousse_assise: float = 70.0
    mousse_genoux: float = 60.0
    nombre_personnes: int = 2
    essence_cadre: Essence = FRENE
    globaux: ParametresGlobaux = PARAMETRES_DEFAUT

    def __post_init__(self) -> None:
        for nom in ("largeur", "hauteur_assise", "inclinaison_assise", "hauteur_repose_genoux",
                    "distance_assise_genoux"):
            TYPO.verifier(nom, getattr(self, nom))

    @property
    def y_genoux(self) -> float:
        """Centre du coussin de genoux (le siège est orienté vers −y)."""
        return 180.0

    @property
    def y_assise(self) -> float:
        return self.y_genoux + self.distance_assise_genoux


def _patin(p: ParametresSiegeReposeGenoux) -> list[tuple[float, float]]:
    """Ligne moyenne du patin traîneau (relevé aux deux bouts, rayon cintrable)."""
    h = p.hauteur_patin / 2.0
    L = p.longueur_patin
    return profil_hermite((
        PointCle(0.0, h + 45.0, -32.0, "nez_patin"),
        PointCle(180.0, h, 0.0, "plat_avant"),
        PointCle(L - 180.0, h, 0.0, "plat_arriere"),
        PointCle(L, h + 45.0, 32.0, "talon_patin"),
    ), n_par_segment=14, tension=1.0)


def _quadrilatere(y_bas: float, y_haut: float, z_bas: float, z_haut: float, s: float) -> list[tuple[float, float]]:
    """Montant incliné de section ``s`` (selon y) entre deux hauteurs."""
    return [(y_bas - s / 2, z_bas), (y_bas + s / 2, z_bas), (y_haut + s / 2, z_haut), (y_haut - s / 2, z_haut)]


def _ergonomie(p: ParametresSiegeReposeGenoux) -> list:
    a = p.globaux.anthropometrie
    d = hypot(p.distance_assise_genoux, p.hauteur_assise - p.hauteur_repose_genoux)
    angle_cuisse = degrees(atan2(p.hauteur_assise - p.hauteur_repose_genoux, p.distance_assise_genoux))
    return [
        verif("ergo_longueur_cuisse", a.longueur_fesse_poplite.p5 <= d <= a.longueur_fesse_genou.p95,
              f"Distance assise → genoux {d:.0f} mm dans [fesse-poplité P5 {a.longueur_fesse_poplite.p5:g} ; "
              f"fesse-genou P95 {a.longueur_fesse_genou.p95:g}] mm : tibias en appui juste sous la rotule.",
              niveau_echec=NIVEAU_AVERTISSEMENT),
        verif("ergo_angle_cuisse", 20.0 <= angle_cuisse <= 35.0,
              f"Cuisses inclinées de {angle_cuisse:.0f}° sous l'horizontale (20–35° : angle tronc-cuisse "
              "≈ 110–125°, bassin en antéversion ; Mandal 1981).", niveau_echec=NIVEAU_AVERTISSEMENT),
        verif("ergo_inclinaison_assise", 12.0 <= p.inclinaison_assise <= 30.0,
              f"Assise inclinée de {p.inclinaison_assise:g}° vers l'avant (12–30°).",
              niveau_echec=NIVEAU_AVERTISSEMENT),
        verif("ergo_tibias", p.hauteur_repose_genoux <= a.hauteur_genou.p5 - 60.0,
              f"Repose-genoux à {p.hauteur_repose_genoux:g} mm ≤ hauteur genou P5 {a.hauteur_genou.p5:g} − 60 : "
              "les pointes de pied touchent le sol derrière le coussin pour tous les gabarits.",
              niveau_echec=NIVEAU_AVERTISSEMENT),
        verif("ergo_reglage_unique", False,
              "Un seul jeu de cotes ne couvre pas confortablement P5 et P95 sur cette typologie "
              "(écart de cuisse ~120 mm) : prévoir deux tailles ou un coussin de genoux déplaçable "
              "(rail à index, ±60 mm).", compromis=True, niveau_echec=NIVEAU_AVERTISSEMENT),
        verif("ergo_largeur", p.largeur >= a.largeur_hanches_assis.p95 + 2 * 80.0,
              f"Largeur {p.largeur:g} mm ≥ hanches P95 + 2 × 80 mm.", niveau_echec=NIVEAU_AVERTISSEMENT),
    ]


def calculer(p: ParametresSiegeReposeGenoux | None = None) -> GeometrieMeuble:
    p = p or ParametresSiegeReposeGenoux()
    g = p.globaux
    e = p.epaisseur_cadre
    s = p.section_montant
    mat = p.essence_cadre.nom
    pieces = []
    assemblages = []
    # --- Assise inclinée (panneau + mousse + revêtement) autour de son centre
    th = p.inclinaison_assise
    z_dessus = p.hauteur_assise
    ep_tot = p.epaisseur_panneau + p.mousse_assise
    cy, cz = p.y_assise, z_dessus - ep_tot / 2.0
    def plaque(z0: float, ep: float) -> list[tuple[float, float]]:
        r = rectangle(cy - p.profondeur_assise / 2, cz + z0, p.profondeur_assise, ep)
        return tourner(r, th, (cy, cz))  # +th : l'avant (−y) descend
    x_int = e
    l_int = p.largeur - 2 * e
    pieces.append(piece_profil("assise_panneau", "assise", g.essence_courbe.nom, x_int - 10, l_int + 20,
                               plaque(-ep_tot / 2, p.epaisseur_panneau)))
    pieces.append(piece_profil("assise_mousse", "mousse", "mousse_hr45", x_int - 10, l_int + 20,
                               plaque(-ep_tot / 2 + p.epaisseur_panneau, p.mousse_assise)))
    surf_a = (p.profondeur_assise + 2 * p.mousse_assise) * (l_int + 20 + 2 * p.mousse_assise) * 1e-6
    pieces.append(piece_profil("assise_revetement", "revetement", g.revetement_tantra.nom, x_int - 10, l_int + 20,
                               plaque(ep_tot / 2, g.revetement_tantra.epaisseur_mm), surface_revetement_m2=surf_a))
    # --- Repose-genoux (deux coussins, un par jambe), inclinés vers l'arrière
    tg = -p.inclinaison_genoux
    ep_g = p.epaisseur_panneau + p.mousse_genoux
    gy, gz = p.y_genoux, p.hauteur_repose_genoux - ep_g / 2.0
    def plaque_g(z0: float, ep: float) -> list[tuple[float, float]]:
        r = rectangle(gy - p.profondeur_genoux / 2, gz + z0, p.profondeur_genoux, ep)
        return tourner(r, tg, (gy, gz))
    largeur_coussin = (l_int - 60.0) / 2.0
    for k, xg in enumerate((x_int, x_int + largeur_coussin + 60.0)):
        pieces.append(piece_profil(f"genoux_panneau_{k + 1}", "repose_genoux", g.essence_courbe.nom, xg,
                                   largeur_coussin, plaque_g(-ep_g / 2, p.epaisseur_panneau)))
        pieces.append(piece_profil(f"genoux_mousse_{k + 1}", "mousse", "mousse_hr55", xg, largeur_coussin,
                                   plaque_g(-ep_g / 2 + p.epaisseur_panneau, p.mousse_genoux)))
        surf_g = (p.profondeur_genoux + 2 * p.mousse_genoux) * (largeur_coussin + 2 * p.mousse_genoux) * 1e-6
        pieces.append(piece_profil(f"genoux_revetement_{k + 1}", "revetement", g.revetement_tantra.nom, xg,
                                   largeur_coussin, plaque_g(ep_g / 2, g.revetement_tantra.epaisseur_mm),
                                   surface_revetement_m2=surf_g))
    # --- Cadres latéraux
    ligne = _patin(p)
    bande = polygone_entre(decaler(ligne, p.hauteur_patin / 2), decaler(ligne, -p.hauteur_patin / 2))
    z_sous_assise = min(z for _, z in pieces[0].profil) - 4.0
    z_sous_genoux = min(z for _, z in pieces[3].profil) - 4.0
    z_pat = p.hauteur_patin
    for cote, xc in (("g", 0.0), ("d", p.largeur - e)):
        pieces.append(piece_profil(f"patin_{cote}", "patin", mat, xc, e, bande,
                                   "Patin traîneau en frêne lamellé cintré (lames de 4 mm)."))
        pieces.append(piece_profil(f"montant_assise_{cote}", "montant", mat, xc, e,
                                   _quadrilatere(p.y_assise + 90.0, p.y_assise + 20.0, z_pat, z_sous_assise, s)))
        pieces.append(piece_profil(f"montant_genoux_{cote}", "montant", mat, xc, e,
                                   _quadrilatere(p.y_genoux + 10.0, p.y_genoux + 20.0, z_pat, z_sous_genoux, s)))
        z1 = z_sous_genoux - 40.0
        z2 = z_pat + (z_sous_assise - z_pat) * 0.62
        pieces.append(piece_profil(f"echarpe_{cote}", "contrefiche", mat, xc, e,
                                   [(p.y_genoux + 40.0, z1 - 25.0), (p.y_genoux + 40.0, z1 + 25.0),
                                    (p.y_assise + 30.0, z2 + 25.0), (p.y_assise + 30.0, z2 - 25.0)],
                                   "Écharpe de triangulation genoux → assise (enfourchée aux montants)."))
        assemblages += [
            Assemblage(f"montants_patin_{cote}", "mortaise_tenon", f"montant_*_{cote}", f"patin_{cote}", 2),
            Assemblage(f"echarpe_{cote}", "mortaise_tenon", f"echarpe_{cote}", f"montant_*_{cote}", 2),
        ]
    # --- Traverses
    sec = (32.0, 70.0)
    traverses = (("traverse_assise_av", p.y_assise - 60.0, z_sous_assise - sec[1] - 5.0),
                 ("traverse_assise_ar", p.y_assise + 110.0, z_sous_assise - sec[1] + 30.0),
                 ("traverse_genoux", p.y_genoux - 10.0, z_sous_genoux - sec[1] - 5.0),
                 ("traverse_basse", (p.y_genoux + p.y_assise) / 2.0, z_pat + 20.0))
    for nom, y, z in traverses:
        pieces.append(prisme(nom, "traverse", mat, e, y, z, p.largeur - 2 * e, sec[0], sec[1]))
        assemblages.append(Assemblage(f"{nom}_tenons", "mortaise_tenon", nom, "cadres", 2))
    assemblages.append(Assemblage("panneaux_tourillons", "tourillon_10", "assise/genoux", "traverses", 12))
    # --- Ancrages : dans les montants (épaisseur e ≥ bloc), 2 par côté
    bloc = recaler_bloc_ancrage(g.essence_structure, g.charges)
    ancrages = []
    for cote, xa in (("g", 0.0), ("d", p.largeur)):
        ancrages.append(Ancrage(f"ancrage_genoux_{cote}", (xa, p.y_genoux + 15.0, z_pat + 90.0),
                                f"montant_genoux_{cote}", True, "Chevilles (insert M12 + anneau rabattable)."))
        ancrages.append(Ancrage(f"ancrage_assise_{cote}", (xa, p.y_assise + 60.0, z_sous_assise - 120.0),
                                f"montant_assise_{cote}", True, "Poignets / taille."))
    # --- Vérifications
    c = g.charges
    v = _ergonomie(p)
    v.append(verif("montant_loge_insert", e >= bloc.epaisseur_mm,
                   f"Montants de {e:g} mm (selon x) ≥ bloc d'ancrage requis {bloc.epaisseur_mm:g} mm : "
                   "l'insert est noyé directement dans le montant de frêne, sans bloc rapporté. "
                   "Compromis : montants plus massifs qu'un siège ordinaire (35–40 mm).",
                   compromis=True))
    v += list(bloc.verifications)
    r_pat = rayon_courbure_min(decaler(ligne, -p.hauteur_patin / 2))
    r_min = rayon_cintrage_minimal_mm(4.0, 40.0)
    v.append(verif("patin_cintrage", r_pat >= r_min,
                   f"Rayon mini du patin ≈ {r_pat:.0f} mm ≥ {r_min:.0f} mm (lamellé-cintré, lames de 4 mm, "
                   "règle R ≥ 40 × épaisseur de lame pour le frêne).", niveau_echec=NIVEAU_AVERTISSEMENT))
    f_assise = c.poids_personne_n * c.facteur_dynamique * p.nombre_personnes
    cs_panneau = cs_flexion(l_int, p.profondeur_assise, p.epaisseur_panneau, f_assise, g.essence_courbe, "repartie")
    v.append(verif("assise_flexion", cs_panneau >= c.coefficient_securite,
                   f"Panneau d'assise {p.epaisseur_panneau:g} mm sur {l_int:.0f} mm de portée, {f_assise:.0f} N "
                   f"répartis : CS {cs_panneau:.1f} (sans compter les deux traverses intermédiaires).",
                   niveau_echec=NIVEAU_AVERTISSEMENT))
    cs_t = cs_tenon(f_assise / 4.0, e / 3.0, s - 10.0, p.essence_cadre)
    v.append(verif("tenons_montants", cs_t >= c.coefficient_securite,
                   f"Tenons des montants d'assise ({e / 3:.0f} × {s - 10:.0f} mm) : {f_assise / 4:.0f} N chacun, CS {cs_t:.1f}."))
    xm = p.largeur / 2.0
    w = c.poids_personne_n
    f1 = w * c.facteur_dynamique
    cas = [
        CasStabilite("penche_avant", ((0.6 * f1, xm, p.y_assise), (0.4 * f1, xm, p.y_genoux - p.profondeur_genoux / 2)),
                     (c.effort_horizontal_exterieur_n, "-y", p.hauteur_assise), 1.5,
                     "Assis, penché en avant, + poussée de 300 N vers l'avant à hauteur d'assise."),
        CasStabilite("bascule_arriere", ((f1, xm, p.y_assise + p.profondeur_assise / 2),),
                     (c.effort_horizontal_exterieur_n, "+y", p.hauteur_assise + 300.0), 1.5,
                     "Assis au bord arrière, poussée de 300 N vers l'arrière à hauteur d'épaules."),
        CasStabilite("chevauchement_lateral", ((2 * w, xm, p.y_assise),),
                     (c.effort_horizontal_exterieur_n, "-x", p.hauteur_assise + 300.0),
                     COEFFICIENT_STABILITE_ACCIDENTEL_MIN,
                     "Deux personnes (l'une sur l'autre), balancement latéral 300 N à hauteur de buste."),
    ]
    v_stab, infos = verifs_stabilite(pieces, cas)
    v += v_stab
    v.append(verif_traction_exterieure(max(a.position[2] for a in ancrages), infos["masse_kg"],
                                       p.largeur / 2.0, c.charge_service_ancrage_n))
    v += essais_communs("siege")
    derivees = {"rayon_min_patin_mm": r_pat, "z_sous_assise": z_sous_assise, **infos}
    return GeometrieMeuble(TYPO.nom, ETAT_FIXE, tuple(pieces), tuple(assemblages), tuple(ancrages),
                           tuple(v), derivees,
                           quincaillerie=(("insert_ancre_m12", len(ancrages)), ("anneau_rabattable", len(ancrages))))


def calculer_etats(p: ParametresSiegeReposeGenoux | None = None) -> dict[str, GeometrieMeuble]:
    return {ETAT_FIXE: calculer(p)}


def vers_parametres_fusion_siege(p: ParametresSiegeReposeGenoux | None = None) -> dict:
    p = p or ParametresSiegeReposeGenoux()
    P = f"{PREFIXE_FUSION}siege_"
    return {
        f"{P}profondeur_assise": (p.profondeur_assise, "mm", "Profondeur du coussin d'assise."),
        f"{P}inclinaison_genoux": (p.inclinaison_genoux, "deg", "Pente des coussins de genoux."),
        f"{P}longueur_patin": (p.longueur_patin, "mm", "Longueur des patins traîneau."),
        f"{P}ep_cadre": (p.epaisseur_cadre, "mm", "Épaisseur des cadres latéraux (frêne)."),
    }


def chiffrage(p: ParametresSiegeReposeGenoux | None = None):
    return chiffrer(calculer(p))
