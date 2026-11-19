# -*- coding: utf-8 -*-
"""Briques communes des sièges profilés du volet 1 (Python pur).

Principe constructif retenu pour les surfaces de soutien courbes :

* **coque** en contreplaqué de bouleau cintré (moulé sous presse) qui
  porte la mousse et suit le profil paramétrique ;
* **flasques** (joues) découpées à la CNC dans un panneau de lamellé-collé
  ou de chêne massif abouté, épousant la sous-face de la coque, en nombre
  calculé pour que la coque résiste à une charge de genou (CS ≥ 3) ;
* **traverses** en chêne assemblées par **tenons et mortaises** entre
  flasques (une pièce par travée), **tourillons** Ø10 coque/flasques et
  Ø12 socle/flasques — aucune vis apparente ;
* **socle** en retrait (plinthe) : effet « posé » moderne, protège le
  chant bas des flasques ;
* **mousse** HR 45 et **revêtement** lavable (cuir pigmenté par défaut).

Les ancrages du volet 1 (fonction assumée) sont des inserts M12 dans des
blocs de chêne collés-tourillonnés contre la face intérieure des flasques
extérieures, avec anneau rabattable affleurant côté extérieur.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from tantra.catalogues.couts import masses_volumiques
from tantra.catalogues.fixations import TOURILLON_10
from tantra.courbes import (
    Point2,
    decaler,
    est_monotone_y,
    longueur,
    polygone_entre,
    rayon_courbure_min,
    z_a,
)
from tantra.geometrie import (
    Ancrage,
    Assemblage,
    CasStabilite,
    Piece,
    Verification,
    coefficient_stabilite,
    empreinte_au_sol,
    masse_et_cdg,
    piece_profil,
    prisme,
)
from tantra.parametres import (
    NIVEAU_AVERTISSEMENT,
    NIVEAU_NON_CONFORME,
    Essence,
    ParametresGlobaux,
    Revetement,
)
from tantra.regles import (
    cs_tenon,
    essai_requis,
    nombre_supports_coque,
    rayon_cintrage_minimal_mm,
    recaler_bloc_ancrage,
    verif,
)

COEFFICIENT_STABILITE_MIN = 1.5
COEFFICIENT_STABILITE_ACCIDENTEL_MIN = 1.2


@dataclass(frozen=True)
class SurfaceSoutien:
    """Résultat de la construction d'une surface profilée."""

    pieces: tuple[Piece, ...]
    assemblages: tuple[Assemblage, ...]
    dessus_mousse: tuple[Point2, ...]
    dessous_coque: tuple[Point2, ...]
    positions_flasques: tuple[float, ...]
    rayon_min_mm: float
    longueur_developpee_mm: float
    infos: dict = field(default_factory=dict)


def _monotone(points: list[Point2], pas_min: float = 0.5) -> list[Point2]:
    """Supprime les points d'un décalé qui reviennent en arrière (zones très pentues)."""
    sortie = [points[0]]
    for p in points[1:]:
        if p[0] > sortie[-1][0] + pas_min:
            sortie.append(p)
    return sortie


def construire_surface(
    prefixe: str,
    dessus_mousse: list[Point2],
    x0: float,
    largeur: float,
    n_flasques: int,
    epaisseur_flasque: float,
    epaisseur_coque: float,
    epaisseur_mousse: float,
    z_base: float,
    globaux: ParametresGlobaux,
    revetement: Revetement,
    essence_flasque: Essence,
    mousse: str = "mousse_hr45",
    traverses_y: tuple[float, ...] = (),
    section_traverse: tuple[float, float] = (32.0, 70.0),
    retrait_socle: float = 40.0,
    hauteur_socle: float | None = None,
    dessus_structure: list[Point2] | None = None,
) -> SurfaceSoutien:
    """Construit coque, mousse, revêtement, flasques, traverses et socle d'un profil.

    ``dessus_mousse`` : profil fini (dessus du revêtement ≈ dessus mousse), y croissant.
    ``z_base`` : hauteur du dessous des flasques (dessus du socle).
    ``traverses_y`` : abscisses des traverses hautes (sous la coque) ; deux traverses
    basses sont toujours ajoutées près des extrémités du socle.
    ``dessus_structure`` : profil du dessus de coque s'il diffère du simple décalé du
    profil fini (ex. cale fessière formée par une surépaisseur de mousse HR 55 sur une
    coque plus lisse, cintrable).
    """
    if n_flasques < 2:
        raise ValueError("Il faut au moins deux flasques.")
    if not est_monotone_y(dessus_mousse):
        raise ValueError(f"{prefixe} : le profil doit être strictement croissant en y.")
    ep_rev = revetement.epaisseur_mm
    dessous_rev = decaler(dessus_mousse, -ep_rev)
    if dessus_structure is None:
        dessus_coque = _monotone(decaler(dessus_mousse, -(ep_rev + epaisseur_mousse)))
    else:
        dessus_coque = _monotone(list(dessus_structure))
    dessous_coque = _monotone(decaler(dessus_coque, -epaisseur_coque))
    if len(dessous_coque) < 0.6 * len(dessus_coque):
        raise ValueError(f"{prefixe} : courbure trop forte pour l'épaisseur mousse + coque.")
    l_dev = longueur(dessus_mousse)
    pieces: list[Piece] = []
    assemblages: list[Assemblage] = []
    mat_coque = globaux.essence_courbe.nom
    pieces.append(piece_profil(f"{prefixe}_coque", "coque", mat_coque, x0, largeur,
                               polygone_entre(dessus_coque, dessous_coque),
                               "Coque en contreplaqué de bouleau cintré, moulée sous presse."))
    pieces.append(piece_profil(f"{prefixe}_mousse", "mousse", mousse, x0, largeur,
                               polygone_entre(_monotone(dessous_rev), dessus_coque),
                               "Mousse HR collée sur la coque, ouatinage sous revêtement."))
    surface = (l_dev * (largeur + 2.0 * epaisseur_mousse) + 2.0 * l_dev * epaisseur_mousse) * 1e-6
    pieces.append(piece_profil(f"{prefixe}_revetement", "revetement", revetement.nom, x0, largeur,
                               polygone_entre(dessus_mousse, _monotone(dessous_rev)),
                               f"Revêtement {revetement.nom_affiche} (retours compris).",
                               surface_revetement_m2=surface))
    # Flasques
    pas = (largeur - epaisseur_flasque) / (n_flasques - 1)
    xs = tuple(x0 + i * pas for i in range(n_flasques))
    y_av, y_ar = dessous_coque[0][0], dessous_coque[-1][0]
    profil_flasque = list(dessous_coque) + [(y_ar, z_base), (y_av, z_base)]
    for i, xf in enumerate(xs):
        exterieure = i in (0, n_flasques - 1)
        pieces.append(piece_profil(
            f"{prefixe}_flasque_{i + 1}", "flasque", essence_flasque.nom, xf, epaisseur_flasque,
            profil_flasque,
            "Flasque extérieure (vue, chants arrondis R6)." if exterieure else
            "Flasque intérieure (nervure de soutien de la coque, non vue).",
        ))
    n_tour_coque = max(4, int(longueur(dessous_coque) // 150))
    assemblages.append(Assemblage(f"{prefixe}_coque_flasques", "tourillon_10", f"{prefixe}_coque",
                                  f"{prefixe}_flasque_*", n_tour_coque * n_flasques,
                                  "Coque collée et tourillonnée sur chaque flasque (pas ~150 mm)."))
    # Traverses : basses (2) + hautes (sous la coque)
    b_tr, h_tr = section_traverse
    y_bas = (y_av + retrait_socle + 40.0, y_ar - retrait_socle - 40.0 - b_tr)
    positions = [(f"basse_{k + 1}", y, z_base + 30.0) for k, y in enumerate(y_bas)]
    for k, y in enumerate(traverses_y):
        z_haut = min(z_a(list(dessous_coque), y), z_a(list(dessous_coque), y + b_tr)) - h_tr - 8.0
        if z_haut > z_base + 30.0 + h_tr + 20.0:
            positions.append((f"haute_{k + 1}", y, z_haut))
    for nom_pos, y, z in positions:
        for i in range(n_flasques - 1):
            xa = xs[i] + epaisseur_flasque
            dxt = xs[i + 1] - xa
            nom_t = f"{prefixe}_traverse_{nom_pos}_{i + 1}"
            pieces.append(prisme(nom_t, "traverse", globaux.essence_structure.nom, xa, y, z, dxt, b_tr, h_tr,
                                 "Traverse chêne, tenons encollés dans les flasques."))
            assemblages.append(Assemblage(f"{nom_t}_tenons", "mortaise_tenon", nom_t,
                                          f"{prefixe}_flasque_{i + 1}/{i + 2}", 2,
                                          "Tenon e = 1/3 de la section, longueur ≥ 30 mm."))
    # Socle en retrait
    if z_base > 0:
        h_soc = hauteur_socle if hauteur_socle is not None else z_base
        xs_min = x0 + retrait_socle
        xs_max = x0 + largeur - retrait_socle
        ys_min = y_av + retrait_socle
        ys_max = y_ar - retrait_socle
        e = 30.0
        mat = globaux.essence_structure.nom
        pieces += [
            prisme(f"{prefixe}_socle_avant", "socle", mat, xs_min, ys_min, 0.0, xs_max - xs_min, e, h_soc),
            prisme(f"{prefixe}_socle_arriere", "socle", mat, xs_min, ys_max - e, 0.0, xs_max - xs_min, e, h_soc),
            prisme(f"{prefixe}_socle_gauche", "socle", mat, xs_min, ys_min + e, 0.0, e, ys_max - ys_min - 2 * e, h_soc),
            prisme(f"{prefixe}_socle_droit", "socle", mat, xs_max - e, ys_min + e, 0.0, e, ys_max - ys_min - 2 * e, h_soc),
        ]
        assemblages.append(Assemblage(f"{prefixe}_socle_angles", "mortaise_tenon", f"{prefixe}_socle_*",
                                      f"{prefixe}_socle_*", 4, "Angles du socle à tenons."))
        assemblages.append(Assemblage(f"{prefixe}_socle_flasques", "tourillon_12", f"{prefixe}_socle_*",
                                      f"{prefixe}_flasque_*", 4 * n_flasques,
                                      "Flasques posées sur le socle, tourillons Ø12 encollés."))
    return SurfaceSoutien(
        pieces=tuple(pieces), assemblages=tuple(assemblages), dessus_mousse=tuple(dessus_mousse),
        dessous_coque=tuple(dessous_coque), positions_flasques=xs,
        rayon_min_mm=rayon_courbure_min(list(dessus_coque)), longueur_developpee_mm=l_dev,
        infos={"n_traverses_positions": len(positions), "section_traverse": section_traverse},
    )


def ancrages_flasques(prefixe: str, surface: SurfaceSoutien, positions_y: tuple[float, ...],
                      epaisseur_flasque: float, globaux: ParametresGlobaux,
                      x0: float, largeur: float) -> tuple[list[Piece], list[Ancrage], list[Assemblage], list[Verification]]:
    """Blocs d'ancrage contre les flasques extérieures, à chaque ``y``, des deux côtés."""
    bloc = recaler_bloc_ancrage(globaux.essence_structure, globaux.charges, 0.0)
    pieces: list[Piece] = []
    ancrages: list[Ancrage] = []
    dessous = list(surface.dessous_coque)
    for k, y in enumerate(positions_y):
        z_haut = min(z_a(dessous, y - bloc.longueur_mm / 2), z_a(dessous, y + bloc.longueur_mm / 2))
        z_bloc = z_haut - bloc.largeur_mm - 15.0
        for cote, xb, xa in (("g", x0 + epaisseur_flasque, x0),
                             ("d", x0 + largeur - epaisseur_flasque - bloc.epaisseur_mm, x0 + largeur)):
            nom = f"{prefixe}_bloc_ancrage_{k + 1}{cote}"
            pieces.append(prisme(nom, "bloc_ancrage", globaux.essence_structure.nom, xb,
                                 y - bloc.longueur_mm / 2, z_bloc, bloc.epaisseur_mm,
                                 bloc.longueur_mm, bloc.largeur_mm,
                                 "Bloc de chêne fil long, collé + tourillons Ø12 contre la flasque."))
            ancrages.append(Ancrage(f"ancrage_{k + 1}{cote}", (xa, y, z_bloc + bloc.largeur_mm / 2), nom, True,
                                    "Insert inox M12 traversant la flasque, anneau rabattable affleurant."))
    assemblages = [
        Assemblage(f"{prefixe}_blocs_tourillons", "tourillon_12", f"{prefixe}_bloc_ancrage_*",
                   f"{prefixe}_flasque_ext", bloc.nombre_tourillons * len(ancrages)),
    ]
    verifs = list(bloc.verifications)
    verifs.append(verif("bloc_ancrage_dimensions", True,
                        f"Bloc d'ancrage recalculé : {bloc.epaisseur_mm:g} × {bloc.largeur_mm:g} × "
                        f"{bloc.longueur_mm:g} mm, {bloc.nombre_tourillons} tourillons Ø12, "
                        f"+ {epaisseur_flasque:g} mm de flasque traversée."))
    return pieces, ancrages, assemblages, verifs


def verifs_structure(prefixe: str, surface: SurfaceSoutien, globaux: ParametresGlobaux,
                     largeur: float, epaisseur_flasque: float, epaisseur_coque: float,
                     n_personnes: int, epaisseur_pli: float = 1.5) -> list[Verification]:
    """Vérifications communes : coque, cintrage, tenons des traverses."""
    c = globaux.charges
    v: list[Verification] = []
    f_genou = c.poids_personne_n * c.facteur_dynamique
    n_req = nombre_supports_coque(largeur, epaisseur_flasque, epaisseur_coque, globaux.essence_courbe,
                                  f_genou, cs=c.coefficient_securite)
    n = len(surface.positions_flasques)
    v.append(verif("coque_flexion", n >= n_req,
                   f"Coque {epaisseur_coque:g} mm : {n_req} flasques nécessaires pour une charge de genou "
                   f"{f_genou:.0f} N (bande 200 mm, CS {c.coefficient_securite:g}) ; {n} prévues."))
    r_min = rayon_cintrage_minimal_mm(epaisseur_pli)
    v.append(verif("coque_cintrage", surface.rayon_min_mm >= r_min,
                   f"Rayon mini de la coque ≈ {surface.rayon_min_mm:.0f} mm pour un rayon de cintrage mini "
                   f"{r_min:.0f} mm (plis de {epaisseur_pli:g} mm). "
                   + ("Faisable." if surface.rayon_min_mm >= r_min else
                      "Trop serré : plis plus minces, rayon plus grand ou pièce massive cintrée vapeur."),
                   compromis=surface.rayon_min_mm < r_min, niveau_echec=NIVEAU_AVERTISSEMENT))
    b_tr, h_tr = surface.infos["section_traverse"]
    n_pos = max(1, surface.infos["n_traverses_positions"])
    # Hypothèse pessimiste : toute la charge passe par les traverses (la coque
    # et le socle ne participent pas), répartie sur les travées, 2 tenons par travée,
    # et un tenon peut reprendre deux fois sa part (charge excentrée).
    effort = 2.0 * c.charge_surface_service_n(n_personnes) / (n_pos * (n - 1) * 2.0)
    cs_t = cs_tenon(effort, b_tr / 3.0, h_tr - 10.0, globaux.essence_structure)
    v.append(verif("tenons_traverses", cs_t >= c.coefficient_securite,
                   f"Tenons des traverses ({b_tr / 3:.0f} × {h_tr - 10:.0f} mm) : {effort:.0f} N par tenon "
                   f"(toute la charge de {n_personnes} personne(s) par les traverses, part doublée pour "
                   f"l'excentrement), CS {cs_t:.1f}."))
    return v


def verifs_stabilite(geo_pieces: list[Piece], cas: list[CasStabilite]) -> tuple[list[Verification], dict]:
    """Applique ``coefficient_stabilite`` à chaque cas, renvoie vérifications et infos."""
    masse, cdg = masse_et_cdg(geo_pieces, masses_volumiques())
    emp = empreinte_au_sol(geo_pieces)
    out: list[Verification] = []
    for c in cas:
        coef, arete = coefficient_stabilite(c, masse, cdg, emp)
        if coef >= c.coefficient_min:
            niveau_ok = True
            niveau = NIVEAU_NON_CONFORME
        else:
            niveau_ok = False
            niveau = NIVEAU_NON_CONFORME if coef < 1.0 else NIVEAU_AVERTISSEMENT
        txt = "∞" if coef == float("inf") else f"{coef:.2f}"
        out.append(verif(f"stabilite_{c.nom}", niveau_ok,
                         f"Stabilité « {c.nom} » : coefficient {txt} (arête {arete or '—'}, minimum "
                         f"{c.coefficient_min:g}). {c.commentaire}",
                         compromis=not niveau_ok, niveau_echec=niveau))
    return out, {"masse_kg": masse, "cdg": cdg, "empreinte": emp}


def verif_traction_exterieure(ancrage_z: float, masse_kg: float, bras_mm: float,
                              charge_ancrage_n: float) -> Verification:
    """Information : traction extérieure pleine (1500 N) sur un ancrage, meuble à vide.

    Un ancrage est dimensionné pour retenir une personne **installée sur le
    meuble** (effort interne). Une traction extérieure de cette intensité
    renverserait tout meuble posé ; on le signale comme compromis.
    """
    m_stab = masse_kg * 9.81 * bras_mm
    m_renv = charge_ancrage_n * ancrage_z
    coef = m_stab / m_renv if m_renv else float("inf")
    return verif("traction_exterieure_ancrage", coef >= COEFFICIENT_STABILITE_MIN,
                 f"Traction extérieure de {charge_ancrage_n:.0f} N à {ancrage_z:.0f} mm, meuble vide : "
                 f"coefficient {coef:.2f}. Les ancrages servent à retenir une personne installée sur le "
                 "meuble ; ne jamais les relier à un point extérieur ni tirer depuis l'extérieur.",
                 compromis=coef < COEFFICIENT_STABILITE_MIN, niveau_echec=NIVEAU_AVERTISSEMENT)


def essais_communs(prefixe: str) -> list[Verification]:
    return [
        essai_requis("essai_statique", "Essai statique de la surface : 3 × charge de service, 10 min, "
                     "sans rupture ni déformation permanente (type EN 1728 adapté)."),
        essai_requis("essai_fatigue", "Essai de fatigue des assemblages (cycles d'assise/rythme) — "
                     "référence EN 1728 / EN 12520, à adapter à l'usage."),
        essai_requis("essai_ancrages", "Essai de traction de chaque ancrage à 3 × 1500 N, sur prototype."),
        essai_requis("visa_ingenieur", "Modèles simplifiés : visa d'un ingénieur structure avant série."),
    ]
