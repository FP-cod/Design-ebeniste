# -*- coding: utf-8 -*-
"""Couche 2 — Catalogues matériaux & fixations, et règles de recalcul.

Pur Python (pas d'``adsk``). Les règles sont volontairement simples,
explicites et prudentes : ce sont des règles d'atelier et de pré-
dimensionnement, PAS un calcul réglementaire. Toute pièce critique d'un
prototype doit être validée par essai (ex. protocoles EN 1728 majorés).

Unités : mm, N, MPa, €, m³, m². Voir ``params_globaux`` pour les conventions.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple

try:  # import relatif (dans l'add-in) ou absolu (tests)
    from . import params_globaux as pg
except ImportError:  # pragma: no cover
    import params_globaux as pg  # type: ignore


# ---------------------------------------------------------------------------
# Coefficients de calcul bois (inspirés EN 1995 / Eurocode 5)
# ---------------------------------------------------------------------------
KMOD: float = 0.9
"""— coefficient de modification, charge court terme, classe de service 1 (intérieur)."""
GAMMA_M: float = 1.3
"""— coefficient partiel du matériau bois massif."""


def resistance_calcul(fk: float) -> float:
    """MPa — résistance de calcul fd = kmod·fk/γM."""
    return KMOD * fk / GAMMA_M


def _arrondi_sup(valeur: float, pas: float) -> float:
    """Arrondi supérieur au multiple de ``pas``."""
    return math.ceil(valeur / pas - 1e-9) * pas


def _standard_le_plus_proche(cible: float, standards: Sequence[float], plafond: Optional[float] = None) -> float:
    """Valeur standard la plus proche de ``cible`` sans dépasser ``plafond``."""
    candidats = [s for s in standards if plafond is None or s <= plafond]
    if not candidats:
        return min(standards)
    return min(candidats, key=lambda s: (abs(s - cible), -s))


# ---------------------------------------------------------------------------
# Tourillons
# ---------------------------------------------------------------------------
DIAMETRES_TOURILLON: Tuple[int, ...] = (6, 8, 10, 12, 14, 16, 20)
"""mm — diamètres de tourillons hêtre cannelés du commerce."""


@dataclass(frozen=True)
class SpecTourillon:
    """Résultat de dimensionnement d'une jonction tourillonnée."""

    diametre: float          # mm
    longueur: float          # mm, longueur totale du tourillon
    profondeur_par_piece: float  # mm, perçage de chaque côté (+1 mm de réserve colle)
    nombre: int              # —
    entraxe: float           # mm
    distance_bord: float     # mm


def diametre_tourillon(epaisseur_piece: float) -> float:
    """Diamètre de tourillon (mm) = f(épaisseur de la pièce la plus mince).

    Règle d'atelier : d ≈ e/3, plafonné à e/2.5 pour garder ≥ 0,3·e de paroi
    de chaque côté. Plage d'usage : e de 18 à 60 mm.
    """
    if epaisseur_piece < 12:
        raise ValueError("Épaisseur < 12 mm : tourillon déconseillé.")
    return _standard_le_plus_proche(epaisseur_piece / 3.0, DIAMETRES_TOURILLON,
                                    plafond=epaisseur_piece / 2.5)


def spec_tourillons(epaisseur_piece: float, largeur_jonction: float) -> SpecTourillon:
    """Dimensionne une ligne de tourillons sur une jonction.

    * longueur = 5·d (arrondi à 5 mm), moitié dans chaque pièce ;
    * distance au bord ≥ 2·d ; entraxe recommandé ≈ 6·d (min 4·d) ;
    * au moins 2 tourillons (anti-rotation).
    """
    d = diametre_tourillon(epaisseur_piece)
    longueur = _arrondi_sup(5 * d, 5)
    bord = 2 * d
    utile = max(largeur_jonction - 2 * bord, 0.0)
    n = max(2, int(utile // (6 * d)) + 1)
    entraxe = utile / (n - 1) if n > 1 else 0.0
    if entraxe and entraxe < 4 * d:
        n = max(2, int(utile // (4 * d)) + 1)
        entraxe = utile / (n - 1)
    return SpecTourillon(d, longueur, longueur / 2 + 1, n, round(entraxe, 1), bord)


# ---------------------------------------------------------------------------
# Mortaises-tenons
# ---------------------------------------------------------------------------
LARGEURS_BEDANE: Tuple[int, ...] = (6, 8, 10, 12, 14, 16, 18, 20, 22, 25)
"""mm — largeurs de mortaise usuelles (bédanes, mèches de mortaiseuse)."""


@dataclass(frozen=True)
class SpecTenon:
    """Résultat de dimensionnement d'un assemblage tenon-mortaise."""

    epaisseur: float      # mm
    largeur: float        # mm (hauteur du tenon, épaulements déduits)
    longueur: float       # mm (profondeur dans la mortaise)
    double_tenon: bool    # True si la traverse est trop haute pour un tenon unique
    cheville_diametre: float  # mm, cheville traversante (tire-fort)
    paroi_mortaise: float     # mm, paroi restante de chaque côté du montant
    alerte: str = ""


def spec_tenon(epaisseur_traverse: float, largeur_traverse: float,
               epaisseur_montant: float, epaulement: float = 10.0) -> SpecTenon:
    """Tenon = f(traverse, montant).

    * épaisseur = e_traverse/3 → largeur de bédane standard ;
    * longueur = 2/3 de l'épaisseur du montant (arrondi inférieur au mm), plafonnée à 5·épaisseur tenon ;
    * largeur = largeur traverse − épaulement (haut) − épaulement (bas) ;
      au-delà de 6·épaisseur → double tenon (limite le retrait et la fente) ;
    * cheville Ø ≈ 0,8·épaisseur tenon, mini 6 mm (montage à tire-fort).
    """
    t = _standard_le_plus_proche(epaisseur_traverse / 3.0, LARGEURS_BEDANE,
                                 plafond=epaisseur_traverse / 2.0)
    longueur = min(epaisseur_montant * 2.0 / 3.0, 5 * t)
    largeur = largeur_traverse - 2 * epaulement
    double = largeur > 6 * t
    paroi = (epaisseur_montant - t) / 2.0
    alerte = ""
    if paroi < t:
        alerte = "Paroi de mortaise < épaisseur du tenon : grossir le montant."
    if largeur <= 0:
        raise ValueError("Traverse trop étroite pour les épaulements demandés.")
    return SpecTenon(t, largeur, float(math.floor(longueur)), double,
                     max(6.0, _standard_le_plus_proche(0.8 * t, (6, 8, 10, 12))),
                     paroi, alerte)


# ---------------------------------------------------------------------------
# Inserts, vis et ancrages
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class Insert:
    """Insert fileté à visser dans le bois dur."""

    filetage: str
    percage_feuillus: float  # mm — Ø de perçage indicatif en bois dur (vérifier fabricant)
    longueur: float          # mm
    prix_unitaire: float     # € HT
    usage: str


INSERTS: Dict[str, Insert] = {
    "M6": Insert("M6", 8.0, 13, 0.6, "Fixation des coussins/plateaux garnis démontables."),
    "M8": Insert("M8", 10.5, 15, 0.9, "Plans de soutien, boudin lombaire."),
    "M10": Insert("M10", 14.0, 18, 1.4, "Liaisons porteuses démontables (livraison)."),
}

ECROU_BARILLET: Dict[str, float] = {"M8": 1.8, "M10": 2.5}
"""€ HT/u — boulon de lit + écrou-barillet (liaison traverse/pied démontable)."""


@dataclass(frozen=True)
class Vis:
    """Vis à bois (type tête fraisée, filetage partiel)."""

    diametre: float     # mm
    prix_unitaire: float  # € HT


VIS: Dict[str, Vis] = {
    "4x40": Vis(4, 0.06), "5x50": Vis(5, 0.10), "6x80": Vis(6, 0.20), "8x120": Vis(8, 0.55),
}


def avant_trou_vis(diametre_vis: float, essence: pg.Essence) -> float:
    """Ø d'avant-trou (mm) dans le filetage : 0,7·d en feuillu dense (ρ ≥ 600), sinon 0,6·d."""
    k = 0.7 if essence.masse_volumique >= 600 else 0.6
    return round(k * diametre_vis * 2) / 2  # arrondi au 0,5 mm


def resistance_arrachement_vis(diametre: float, longueur_ancrage: float,
                               essence: pg.Essence, nombre: int = 1) -> float:
    """N — résistance de calcul indicative à l'arrachement axial (EC5 §8.7.2 simplifié).

    f_ax,k = 0,52·d^-0,5·l_ef^-0,1·ρk^0,8 (MPa), ρk ≈ 0,8·ρ moyen ;
    F = n^0,9 · f_ax,k · d · l_ef · k_d · kmod / γM, k_d = min(d/8, 1).
    Valide pour 6 ≤ d ≤ 12 mm ; hors plage : ordre de grandeur seulement.
    """
    rho_k = 0.8 * essence.masse_volumique
    f_ax = 0.52 * diametre ** -0.5 * longueur_ancrage ** -0.1 * rho_k ** 0.8
    kd = min(diametre / 8.0, 1.0)
    return nombre ** 0.9 * f_ax * diametre * longueur_ancrage * kd * KMOD / GAMMA_M


# ---------------------------------------------------------------------------
# Colles
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class Colle:
    """Colle d'ébénisterie."""

    nom: str
    classe: str
    temps_ouvert_min: float   # min
    serrage_min: float        # min de serrage avant manipulation
    prix_kg: float            # € HT/kg
    consommation_g_m2: float  # g/m² de surface encollée
    usage: str


COLLES: Dict[str, Colle] = {
    "PVA_D3": Colle("Vinylique D3", "EN 204 D3", 8, 45, 12, 180,
                    "Tenons, tourillons, aboutages : colle par défaut."),
    "PU_D4": Colle("Polyuréthane D4", "EN 204 D4", 20, 90, 25, 200,
                   "Joints peu ajustés, chêne tannique, laminés."),
    "EPOXY": Colle("Époxy structurelle", "—", 30, 360, 45, 400,
                   "Collage des inserts filetés, réparations, bois gras."),
    "PEAU": Colle("Colle de peau (chaude ou liquide)", "réversible", 5, 120, 30, 200,
                  "Restauration/démontage futur : esprit ébénisterie classique."),
    "UREE": Colle("Urée-formol", "EN 204 D3/D4", 25, 240, 15, 250,
                  "Lamellé-cintré (faible fluage sous contrainte)."),
}

_COLLE_PAR_JONCTION = {
    "tenon": "PVA_D3", "tourillon": "PVA_D3", "faux_tenon": "PVA_D3",
    "aboutage": "PVA_D3", "lamelle_cintre": "UREE", "insert": "EPOXY",
    "mal_ajuste": "PU_D4", "reversible": "PEAU",
}


def recommandation_colle(type_jonction: str) -> Colle:
    """Colle conseillée pour un type de jonction (clé de ``_COLLE_PAR_JONCTION``)."""
    try:
        return COLLES[_COLLE_PAR_JONCTION[type_jonction]]
    except KeyError as exc:
        raise ValueError(f"Type de jonction inconnu : {type_jonction!r}") from exc


# ---------------------------------------------------------------------------
# Dimensionnement des pièces porteuses
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class ResultatSection:
    """Résultat d'un dimensionnement de section (mm)."""

    cote: float              # mm — retenu (arrondi, mini esthétique/assemblage inclus)
    cote_resistance: float   # mm — exigé par la résistance seule
    cote_stabilite: float    # mm — exigé par flambement / flèche
    critere: str             # critère déterminant


def section_pied(charge_totale_N: float, hauteur: float, essence: pg.Essence,
                 nb_pieds: int = 4, coef_repartition: float = 2.0,
                 k_flambement: float = 1.0, coef_securite: float = 3.0,
                 section_min: float = 40.0, epaisseur_tenon: float = 0.0) -> ResultatSection:
    """Côté (mm) d'un pied de section carrée = f(charge).

    * effort par pied N = charge·coef_repartition/nb_pieds ;
    * compression : a² ≥ N / fc0d ;
    * flambement Euler : a⁴ ≥ 12·cs·N·(k·L)² / (π²·E) ;
      k = 1 pied tenu haut et bas (traverses), 2 pied libre en tête ;
    * assemblage : a ≥ 3·épaisseur de tenon (paroi ≥ tenon de chaque côté) ;
    * plancher esthétique ``section_min`` (mm) ; arrondi au 5 mm supérieur.

    NB : en mobilier, la compression n'est quasi jamais dimensionnante : ce
    sont le contreventement (raideur des nœuds) et l'assemblage.
    """
    n = charge_totale_N * coef_repartition / nb_pieds
    a_res = math.sqrt(n / resistance_calcul(essence.fc0k))
    a_flamb = (12 * coef_securite * n * (k_flambement * hauteur) ** 2
               / (math.pi ** 2 * essence.E0_mean)) ** 0.25
    a_assemblage = 3 * epaisseur_tenon
    candidats = {"compression": a_res, "flambement": a_flamb,
                 "assemblage": a_assemblage, "esthétique/minimum": section_min}
    critere = max(candidats, key=candidats.get)
    return ResultatSection(_arrondi_sup(candidats[critere], 5), round(a_res, 1),
                           round(a_flamb, 1), critere)


def hauteur_traverse(portee: float, charge_repartie_N: float, largeur: float,
                     essence: pg.Essence, fleche_relative_max: float = 300.0,
                     charge_service_N: Optional[float] = None,
                     hauteur_min: float = 40.0) -> ResultatSection:
    """Hauteur (mm) d'une traverse/latte sur deux appuis, charge uniformément répartie.

    * flexion : M = W·L/8, h ≥ √(6·M / (b·fmd)) avec W = charge de conception ;
    * flèche : δ = 5·W·L³/(384·E·I) ≤ L/fleche_relative_max avec W = charge de
      service (par défaut charge de conception / 2, i.e. sans majoration dynamique).
    """
    w_service = charge_service_N if charge_service_N is not None else charge_repartie_N / 2.0
    m = charge_repartie_N * portee / 8.0
    h_res = math.sqrt(6 * m / (largeur * resistance_calcul(essence.fmk)))
    h_fleche = (60 * w_service * portee ** 2 * fleche_relative_max
                / (384 * essence.E0_mean * largeur)) ** (1 / 3)
    candidats = {"flexion": h_res, "flèche": h_fleche, "minimum": hauteur_min}
    critere = max(candidats, key=candidats.get)
    return ResultatSection(_arrondi_sup(candidats[critere], 5), round(h_res, 1),
                           round(h_fleche, 1), critere)


def marge_basculement(x_centre_charge: float, x_appui_min: float, x_appui_max: float) -> float:
    """mm — distance (signée) du point de charge au bord le plus proche du polygone d'appui (1D).

    Négatif = basculement. Viser ≥ 100 mm sur le cas de charge le plus excentré
    (ex. occupant assis en bout de chaise longue).
    """
    return min(x_centre_charge - x_appui_min, x_appui_max - x_centre_charge)


# ---------------------------------------------------------------------------
# Chiffrage
# ---------------------------------------------------------------------------
def prix_bois(volume_net_m3: float, essence: pg.Essence, cintre: bool = False,
              tarifs: pg.Tarifs = pg.Tarifs()) -> Tuple[float, float]:
    """€ HT (bas, haut) — prix = volume net × coef. déchet × prix/m³ de l'essence."""
    coef = tarifs.coef_dechet_cintre if cintre else tarifs.coef_dechet_droit
    brut = volume_net_m3 * coef
    return (brut * essence.prix_m3_bas, brut * essence.prix_m3_haut)


def prix_mousse(volume_m3: float, mousse: pg.Mousse) -> float:
    """€ HT — volume de mousse × prix/m³."""
    return volume_m3 * mousse.prix_m3


def prix_revetement(surface_utile_m2: float, rev: pg.Revetement) -> Tuple[float, float]:
    """€ HT (bas, haut) — surface utile × coef. de chute × prix/m²."""
    s = surface_utile_m2 * rev.coef_chute
    return (s * rev.prix_m2_bas, s * rev.prix_m2_haut)


@dataclass
class Nomenclature:
    """Quantités d'une typologie pour le chiffrage (saisies par la couche 3)."""

    nom: str
    bois_droit_m3: float          # m³ net, pièces droites
    bois_cintre_m3: float         # m³ net, pièces chantournées
    mousses_m3: Dict[str, float]  # {clé MOUSSES: m³}
    revetement_m2: float          # m² utiles
    surface_finition_m2: float    # m² de bois apparent
    quincaillerie_eur: float      # € HT (inserts, vis, patins, sangles, colle)
    heures_ebeniste: Tuple[float, float]   # (bas, haut)
    heures_tapissier: Tuple[float, float]  # (bas, haut)
    fournitures_garnissage_eur: float = 0.0  # € HT (contreplaqué de fond, ouate, toile)


def chiffrage(nom: Nomenclature, essence_cle: str,
              revetement_cle: str = "cuir_pigmente", finition_cle: str = "vernis_pu_mat",
              tarifs: pg.Tarifs = pg.Tarifs()) -> Dict[str, Tuple[float, float]]:
    """Fourchette de coût de revient (€ HT, (bas, haut)) poste par poste.

    Bas = prix matière bas + heures basses × taux bas ; haut = l'inverse.
    """
    ess = pg.ESSENCES[essence_cle]
    b1 = prix_bois(nom.bois_droit_m3, ess, False, tarifs)
    b2 = prix_bois(nom.bois_cintre_m3, ess, True, tarifs)
    bois = (b1[0] + b2[0], b1[1] + b2[1])
    mousse = sum(prix_mousse(v, pg.MOUSSES[k]) for k, v in nom.mousses_m3.items())
    rev = prix_revetement(nom.revetement_m2, pg.REVETEMENTS[revetement_cle])
    garn = (mousse + rev[0] + nom.fournitures_garnissage_eur,
            mousse + rev[1] + nom.fournitures_garnissage_eur)
    fin = nom.surface_finition_m2 * pg.FINITIONS[finition_cle].prix_m2
    quinc = nom.quincaillerie_eur + fin
    mo = (nom.heures_ebeniste[0] * tarifs.taux_ebeniste_bas + nom.heures_tapissier[0] * tarifs.taux_tapissier_bas,
          nom.heures_ebeniste[1] * tarifs.taux_ebeniste_haut + nom.heures_tapissier[1] * tarifs.taux_tapissier_haut)
    k = tarifs.coef_frais_generaux
    total = (k * (bois[0] + garn[0] + quinc + mo[0]), k * (bois[1] + garn[1] + quinc + mo[1]))
    return {"bois": bois, "garnissage": garn, "quincaillerie_finition": (quinc, quinc),
            "main_oeuvre": mo, "total": total,
            "volume_brut_m3": (nom.bois_droit_m3 * tarifs.coef_dechet_droit
                               + nom.bois_cintre_m3 * tarifs.coef_dechet_cintre,) * 2}
