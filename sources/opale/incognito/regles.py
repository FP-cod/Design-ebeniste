# -*- coding: utf-8 -*-
"""Règles de recalcul de la gamme Incognito (couche 2).

Applique les règles déclaratives des catalogues aux paramètres de charge
et d'essence, et propose des ajustements géométriques (dimensions du
bloc d'ancrage, section minimale de bois restante).

Tous les modèles sont volontairement simplifiés. Un résultat « acceptable »
ici n'est pas une validation d'ingénieur et ne dispense pas d'un essai
de charge réel.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import ceil

from incognito.parametres import (
    COEFFICIENT_SECURITE_MIN_RECOMMANDE,
    ANCRE_DEFAUT,
    CHARGES_DEFAUT,
    DISCRETION_DEFAUT,
    Essence,
    GeometrieAncre,
    ParametresCharge,
    ParametresDiscretion,
    paroi_minimale_cisaillement_mm,
    section_nette_minimale_mm2,
    valider_ancrage,
    RapportValidation,
)


@dataclass(frozen=True)
class Ajustement:
    """Proposition de recalage géométrique issue d'une règle."""

    code: str
    cible: str
    valeur_mm: float
    message: str


@dataclass(frozen=True)
class RecalageAncrage:
    """Résultat du recalage d'un bloc d'ancrage."""

    geometrie: GeometrieAncre
    ajustements: tuple[Ajustement, ...]
    rapport: RapportValidation

    @property
    def conforme_modele_simplifie(self) -> bool:
        return self.rapport.conforme


def section_bois_minimale_mm2(
    essence: Essence,
    charges: ParametresCharge | None = None,
) -> float:
    """Section nette minimale (mm²) autour d'une ancre, modèle σ = F×CS / σ_adm."""
    charges = charges or CHARGES_DEFAUT
    return section_nette_minimale_mm2(
        charges.charge_service_ancrage_n,
        charges.coefficient_securite,
        essence.contrainte_admissible_flexion_mpa,
    )


def paroi_bois_minimale_mm(
    essence: Essence,
    charges: ParametresCharge | None = None,
    longueur_encastrement_mm: float = ANCRE_DEFAUT.longueur_encastrement_mm,
    nombre_plans: int = ANCRE_DEFAUT.nombre_plans_cisaillement,
) -> float:
    """Épaisseur minimale de bois par plan de cisaillement (mm)."""
    charges = charges or CHARGES_DEFAUT
    return paroi_minimale_cisaillement_mm(
        charges.charge_service_ancrage_n,
        charges.coefficient_securite,
        essence.contrainte_admissible_cisaillement_mpa,
        longueur_encastrement_mm,
        nombre_plans,
    )


def _arrondir_dessus(valeur: float, pas: float = 2.0) -> float:
    """Arrondit à l'incrément supérieur (ébénisterie, pas de 2 mm par défaut)."""
    return pas * ceil(valeur / pas)


def recaler_bloc_ancrage(
    essence: Essence,
    charges: ParametresCharge | None = None,
    discretion: ParametresDiscretion | None = None,
    diametre_insert_mm: float = ANCRE_DEFAUT.diametre_insert_mm,
    longueur_encastrement_mm: float = ANCRE_DEFAUT.longueur_encastrement_mm,
) -> RecalageAncrage:
    """Calcule un bloc d'ancrage local dimensionné pour la charge et l'essence.

    Le bloc est destiné à être masqué sous le coussin/cuir du banc : on
    l'épaissit plutôt que de réduire le recouvrement de discrétion ou
    d'alourdir tout le rail visible. C'est le bon côté du compromis
    discrétion / solidité.

    Hypothèses :
    * le recouvrement (cache) n'est pas compté comme section résistante ;
    * deux plans de cisaillement ;
    * distance au bord ≥ max(25 mm, 2×Ø).
    """
    charges = charges or CHARGES_DEFAUT
    discretion = discretion or DISCRETION_DEFAUT
    ajustements: list[Ajustement] = []

    if charges.coefficient_securite < COEFFICIENT_SECURITE_MIN_RECOMMANDE:
        raise ValueError(
            f"CS {charges.coefficient_securite:g} < "
            f"{COEFFICIENT_SECURITE_MIN_RECOMMANDE:g} recommandé : "
            "refuser le recalage plutôt que de sous-dimensionner le bloc."
        )

    recouvrement = max(
        discretion.retrait_min_ancre_sous_surface_mm,
        discretion.epaisseur_recouvrement_bois_mm,
    )
    paroi = paroi_bois_minimale_mm(
        essence, charges, longueur_encastrement_mm, nombre_plans=2
    )
    # Épaisseur utile = 2 parois + insert ; épaisseur totale = utile + cache
    epaisseur_utile = 2.0 * paroi + diametre_insert_mm
    epaisseur_totale = _arrondir_dessus(epaisseur_utile + recouvrement)
    ajustements.append(Ajustement(
        "epaisseur_bloc",
        "epaisseur_bloc_mm",
        epaisseur_totale,
        (
            f"Épaisseur de bloc {epaisseur_totale:g} mm "
            f"(2× paroi {paroi:.1f} mm + insert {diametre_insert_mm:g} mm "
            f"+ cache {recouvrement:g} mm, arrondi ébénisterie)."
        ),
    ))

    # Section nette : largeur × épaisseur utile − insert × épaisseur utile
    section_min = section_bois_minimale_mm2(essence, charges)
    epaisseur_utile_arrondie = epaisseur_totale - recouvrement
    largeur_min = section_min / max(epaisseur_utile_arrondie - diametre_insert_mm, 1.0)
    bord_min = max(25.0, 2.0 * diametre_insert_mm)
    largeur = _arrondir_dessus(max(largeur_min, diametre_insert_mm + 2.0 * bord_min, 60.0))
    ajustements.append(Ajustement(
        "largeur_bloc",
        "largeur_bloc_mm",
        largeur,
        f"Largeur de bloc {largeur:g} mm (section nette et distance au bord).",
    ))

    longueur = _arrondir_dessus(max(longueur_encastrement_mm, diametre_insert_mm + 2.0 * bord_min, 80.0))
    ajustements.append(Ajustement(
        "longueur_bloc",
        "longueur_bloc_mm",
        longueur,
        f"Longueur de bloc {longueur:g} mm (encastrement et distance au bord).",
    ))

    geometrie = GeometrieAncre(
        diametre_insert_mm=diametre_insert_mm,
        longueur_encastrement_mm=min(longueur_encastrement_mm, longueur),
        epaisseur_bloc_mm=epaisseur_totale,
        largeur_bloc_mm=largeur,
        longueur_bloc_mm=longueur,
        epaisseur_recouvrement_mm=recouvrement,
        recouvrement_est_structurel=False,
        nombre_plans_cisaillement=2,
        distance_au_bord_mm=bord_min,
    )
    rapport = valider_ancrage(essence, geometrie, charges, discretion)
    return RecalageAncrage(
        geometrie=geometrie,
        ajustements=tuple(ajustements),
        rapport=rapport,
    )


def epaisseur_rail_insuffisante(
    epaisseur_rail_mm: float,
    essence: Essence,
    charges: ParametresCharge | None = None,
    discretion: ParametresDiscretion | None = None,
    diametre_insert_mm: float = ANCRE_DEFAUT.diametre_insert_mm,
) -> bool:
    """True si un rail courant (sans bloc local) ne peut pas loger l'ancre.

    C'est le compromis typique : un rail élégant de 22–28 mm ne suffit
    jamais à noyer une ancre de service 1500 N / CS 3 tout en conservant
    le retrait de discrétion. D'où le bloc d'ancrage local masqué.
    """
    charges = charges or CHARGES_DEFAUT
    discretion = discretion or DISCRETION_DEFAUT
    paroi = paroi_bois_minimale_mm(essence, charges)
    recouvrement = discretion.retrait_min_ancre_sous_surface_mm
    besoin = 2.0 * paroi + diametre_insert_mm + recouvrement
    return epaisseur_rail_mm < besoin


# ---------------------------------------------------------------------------
# Règles du pouf vibrant : isolation, balourd, voice coil, housse, fixations
# ---------------------------------------------------------------------------

from math import pi, sqrt  # noqa: E402  — import tardif accepté, module déjà chargé

from incognito.parametres import (  # noqa: E402
    GAMME_SYBIAN_ENTREE,
    GAMME_SYBIAN_HAUT,
)
from incognito.catalogues.silentblocs import (  # noqa: E402
    Silentbloc,
    silentblocs_pour_gamme,
)
from incognito.catalogues.moteurs import (  # noqa: E402
    BALOURD_24V,
    VCAR_0105,
    variante_par_gamme,
)
from incognito.catalogues.housses import (  # noqa: E402
    FILETAGE_1_NPT,
    MASSE_HOUSSE_DEFAUT_KG,
    MASSE_HOUSSE_MAX_DOCUMENTEE_KG,
    masse_embout_kg,
)


# Isolation : f0 ≤ f_exc_min / k. Le minimum réglementaire du brief est √2 ;
# la cible « idéale » est 3.
RAPPORT_ISOLATION_MIN = sqrt(2.0)
RAPPORT_ISOLATION_IDEAL = 3.0

# Jeu minimal entre l'équipage suspendu et la structure (mm).
JEU_DEBATTEMENT_MIN_MM = 6.0

# Coefficient de sécurité de charge des silentblocs (statique + dynamique).
CS_SILENTBLOC_MIN = 1.5


def omega_rad_s(tr_min: float) -> float:
    """Vitesse angulaire ω = 2π n / 60, n en tr/min."""
    if tr_min < 0:
        raise ValueError("La vitesse de rotation ne peut pas être négative.")
    return 2.0 * pi * tr_min / 60.0


def force_centrifuge_n(masse_balourd_kg: float, excentricite_mm: float, tr_min: float) -> float:
    """Force centrifuge du balourd : F = m · e · ω², en newtons.

    ``excentricite_mm`` est convertie en mètres. Modèle d'un balourd
    ponctuel en rotation à vitesse constante.
    """
    if masse_balourd_kg < 0 or excentricite_mm < 0:
        raise ValueError("Masse et excentricité doivent être ≥ 0.")
    e_m = excentricite_mm / 1000.0
    omega = omega_rad_s(tr_min)
    return masse_balourd_kg * e_m * omega * omega


def frequence_propre_hz(raideur_eq_n_par_m: float, masse_suspendue_kg: float) -> float:
    """Fréquence propre d'un système 1 ddl : f0 = 1/(2π) √(k/m)."""
    if raideur_eq_n_par_m <= 0 or masse_suspendue_kg <= 0:
        raise ValueError("Raideur et masse doivent être > 0.")
    return (1.0 / (2.0 * pi)) * sqrt(raideur_eq_n_par_m / masse_suspendue_kg)


def transmissibilite(rapport_f_sur_f0: float, zeta: float) -> float:
    """Transmissibilité d'un isolateur visqueux 1 ddl (module).

    T = √(1 + (2ζr)²) / √((1 − r²)² + (2ζr)²), avec r = f / f0.
    """
    if zeta < 0:
        raise ValueError("L'amortissement zeta doit être ≥ 0.")
    r = rapport_f_sur_f0
    deux_zr = 2.0 * zeta * r
    num = sqrt(1.0 + deux_zr * deux_zr)
    den = sqrt((1.0 - r * r) ** 2 + deux_zr * deux_zr)
    if den == 0:
        return float("inf")
    return num / den


def amplitude_sinus_mm(force_n: float, masse_kg: float, frequence_hz: float) -> float:
    """Amplitude de déplacement (mm) d'une masse forcée, hors raideur : x = F / (m ω²).

    Utile comme ordre de grandeur du débattement de l'équipage à r ≫ 1
    (la raideur devient négligeable). La course d'un voice coil reste
    limitée par sa course constructive.
    """
    if masse_kg <= 0 or frequence_hz <= 0:
        raise ValueError("Masse et fréquence doivent être > 0.")
    omega = 2.0 * pi * frequence_hz
    return (force_n / (masse_kg * omega * omega)) * 1000.0


def force_requise_voice_coil_n(masse_mobile_kg: float, amplitude_mm: float, frequence_hz: float) -> float:
    """Force crête requise pour une amplitude sinusoïdale : F = m · ω² · x."""
    if masse_mobile_kg <= 0 or frequence_hz <= 0:
        raise ValueError("Masse et fréquence doivent être > 0.")
    if amplitude_mm < 0:
        raise ValueError("L'amplitude doit être ≥ 0.")
    omega = 2.0 * pi * frequence_hz
    return masse_mobile_kg * omega * omega * (amplitude_mm / 1000.0)


@dataclass(frozen=True)
class ChoixSilentblocs:
    """Résultat du recalage des silentblocs pour une variante."""

    silentbloc: Silentbloc
    nombre: int
    raideur_eq_n_par_mm: float
    masse_suspendue_kg: float
    frequence_propre_hz: float
    frequence_exc_min_hz: float
    rapport_fmin_sur_f0: float
    transmissibilite_a_fmin: float
    transmissibilite_a_fmax: float
    deflexion_statique_mm: float
    charge_statique_par_plot_n: float
    charge_dynamique_crete_estimee_n: float
    charge_totale_par_plot_n: float
    isole_au_minimum: bool  # r ≥ √2
    isole_ideal: bool  # r ≥ 3
    messages: tuple[str, ...]


def choisir_silentblocs(
    gamme: str,
    masse_suspendue_kg: float,
    frequence_exc_min_hz: float,
    frequence_exc_max_hz: float,
    force_dynamique_crete_n: float,
    nombres_candidats: tuple[int, ...] = (4, 6, 8),
) -> ChoixSilentblocs:
    """Choisit un plot et un nombre de points pour viser f0 ≤ f_min / 3.

    Si l'idéal (rapport 3) est inatteignable avec le catalogue, on retient
    la meilleure solution qui passe au moins le rapport √2, sinon la moins
    défavorable avec un avertissement.
    """
    if masse_suspendue_kg <= 0 or frequence_exc_min_hz <= 0:
        raise ValueError("Masse suspendue et fréquence d'excitation min doivent être > 0.")
    candidats_bloc = silentblocs_pour_gamme(gamme)
    if not candidats_bloc:
        raise ValueError(f"Aucun silentbloc au catalogue pour la gamme {gamme}.")

    def evalue(bloc: Silentbloc, n: int) -> ChoixSilentblocs:
        k_eq_n_mm = n * bloc.raideur_axiale_n_par_mm
        k_eq_n_m = k_eq_n_mm * 1000.0
        f0 = frequence_propre_hz(k_eq_n_m, masse_suspendue_kg)
        r_min = frequence_exc_min_hz / f0
        r_max = frequence_exc_max_hz / f0 if frequence_exc_max_hz > 0 else r_min
        t_min = transmissibilite(r_min, bloc.amortissement_zeta)
        t_max = transmissibilite(r_max, bloc.amortissement_zeta)
        poids = masse_suspendue_kg * 9.81
        defl = poids / k_eq_n_mm
        charge_stat = poids / n
        # Répartition uniforme approximative de la force dynamique.
        charge_dyn = abs(force_dynamique_crete_n) / n
        charge_tot = charge_stat + charge_dyn
        msgs: list[str] = []
        isole_min = r_min >= RAPPORT_ISOLATION_MIN
        isole_id = r_min >= RAPPORT_ISOLATION_IDEAL
        if not isole_min:
            msgs.append(
                f"Rapport f_min/f0 = {r_min:.2f} < √2 : le système n'est pas "
                "en zone d'isolation à la fréquence minimale (risque d'amplifier "
                "la vibration du meuble). Monter f_min, assouplir ou alourdir."
            )
        elif not isole_id:
            msgs.append(
                f"Rapport f_min/f0 = {r_min:.2f} ≥ √2 mais < 3 (cible idéale). "
                "Isolation acceptable au sens du brief, perfectible."
            )
        if charge_tot > bloc.charge_nominale_n:
            msgs.append(
                f"Charge par plot {charge_tot:.1f} N > charge nominale "
                f"{bloc.charge_nominale_n:.1f} N (statique + dynamique estimée)."
            )
        if defl > 0.8 * bloc.hauteur_libre_mm:
            msgs.append(
                f"Déflexion statique {defl:.1f} mm trop proche de la hauteur "
                f"libre {bloc.hauteur_libre_mm:.1f} mm."
            )
        return ChoixSilentblocs(
            silentbloc=bloc,
            nombre=n,
            raideur_eq_n_par_mm=k_eq_n_mm,
            masse_suspendue_kg=masse_suspendue_kg,
            frequence_propre_hz=f0,
            frequence_exc_min_hz=frequence_exc_min_hz,
            rapport_fmin_sur_f0=r_min,
            transmissibilite_a_fmin=t_min,
            transmissibilite_a_fmax=t_max,
            deflexion_statique_mm=defl,
            charge_statique_par_plot_n=charge_stat,
            charge_dynamique_crete_estimee_n=charge_dyn,
            charge_totale_par_plot_n=charge_tot,
            isole_au_minimum=isole_min,
            isole_ideal=isole_id,
            messages=tuple(msgs),
        )

    evalues = [evalue(b, n) for b in candidats_bloc for n in nombres_candidats]
    # Préférer : isole_ideal, puis isole_min, puis plus grand rapport, puis charge OK.
    def cle(c: ChoixSilentblocs) -> tuple:
        charge_ok = c.charge_totale_par_plot_n <= c.silentbloc.charge_nominale_n
        return (
            c.isole_ideal,
            c.isole_au_minimum,
            charge_ok,
            c.rapport_fmin_sur_f0,
            -c.nombre,  # à rapport égal, moins de plots (simplicité)
        )

    evalues.sort(key=cle, reverse=True)
    return evalues[0]


@dataclass(frozen=True)
class DiagnosticHousse:
    """Vérification de la masse de housse vis-à-vis de l'actionneur."""

    masse_housse_kg: float
    masse_mobile_totale_kg: float
    force_disponible_n: float
    force_requise_pour_demi_course_a_fmin_n: float
    amplitude_max_a_fmin_mm: float
    amplitude_max_a_f_typ_mm: float
    frequence_typ_hz: float
    hors_capacite: bool
    messages: tuple[str, ...]


def diagnostiquer_housse_haut(
    masse_housse_kg: float,
    masse_equipage_hors_housse_kg: float,
    course_totale_mm: float = VCAR_0105.course_totale_mm,
    force_crete_n: float = VCAR_0105.force_crete_n,
    force_continue_n: float = VCAR_0105.force_continue_25c_n,
    frequence_min_hz: float = VCAR_0105.frequence_min_hz,
    frequence_typ_hz: float = 15.0,
) -> DiagnosticHousse:
    """Compare 105 N crête à la force requise avec la housse ajoutée à la masse mobile."""
    if masse_housse_kg < 0:
        raise ValueError("masse_housse_kg doit être ≥ 0.")
    m = masse_equipage_hors_housse_kg + masse_housse_kg
    demi = course_totale_mm / 2.0
    f_req = force_requise_voice_coil_n(m, demi, frequence_min_hz)
    # Amplitude atteignable en crête (limitée par la course et par F = m ω² x).
    x_fmin = min(demi, (force_crete_n / (m * (2 * pi * frequence_min_hz) ** 2)) * 1000.0)
    x_ftyp = min(demi, (force_crete_n / (m * (2 * pi * frequence_typ_hz) ** 2)) * 1000.0)
    msgs: list[str] = []
    hors = False
    if masse_housse_kg > MASSE_HOUSSE_MAX_DOCUMENTEE_KG:
        msgs.append(
            f"Masse de housse {masse_housse_kg:.2f} kg au-delà de la plage "
            f"documentée (≤ {MASSE_HOUSSE_MAX_DOCUMENTEE_KG:.2f} kg). Peser et revalider."
        )
        hors = True
    f_req_15_8 = force_requise_voice_coil_n(m, 8.0, frequence_typ_hz)
    if f_req_15_8 > force_crete_n:
        msgs.append(
            f"Hors capacité au point typique {frequence_typ_hz:.0f} Hz / 8 mm : "
            f"{f_req_15_8:.1f} N > {force_crete_n:.1f} N crête (masse mobile "
            f"{m:.2f} kg). Réduire la masse de housse, l'amplitude ou la fréquence."
        )
        hors = True
    if f_req > force_crete_n:
        msgs.append(
            f"Hors capacité : pour viser la demi-course ({demi:.1f} mm) à "
            f"{frequence_min_hz:.1f} Hz, il faut {f_req:.1f} N > {force_crete_n:.1f} N "
            f"crête (VCAR, masse mobile totale {m:.2f} kg). Amplitude max estimée "
            f"{x_fmin:.1f} mm à cette fréquence."
        )
        hors = True
    f_req_cont = force_requise_voice_coil_n(m, min(demi, x_ftyp), frequence_typ_hz)
    if f_req_cont > force_continue_n:
        msgs.append(
            f"La force continue catalogue ({force_continue_n:.1f} N à 25 °C) "
            f"est inférieure à {f_req_cont:.1f} N pour tenir {x_ftyp:.1f} mm à "
            f"{frequence_typ_hz:.1f} Hz en régime. Risque d'échauffement : "
            "réduire l'amplitude, la durée, ou la masse."
        )
    if not msgs:
        msgs.append(
            f"Housse {masse_housse_kg:.2f} kg dans la capacité crête pour la "
            f"demi-course à {frequence_min_hz:.1f} Hz (F requise {f_req:.1f} N "
            f"≤ {force_crete_n:.1f} N). Amplitude typique à {frequence_typ_hz:.1f} Hz : "
            f"{x_ftyp:.1f} mm (limitée par F et par la course)."
        )
    return DiagnosticHousse(
        masse_housse_kg=masse_housse_kg,
        masse_mobile_totale_kg=m,
        force_disponible_n=force_crete_n,
        force_requise_pour_demi_course_a_fmin_n=f_req,
        amplitude_max_a_fmin_mm=x_fmin,
        amplitude_max_a_f_typ_mm=x_ftyp,
        frequence_typ_hz=frequence_typ_hz,
        hors_capacite=hors,
        messages=tuple(msgs),
    )


@dataclass(frozen=True)
class FixationsModule:
    """Fixations du module sur les ancrages internes du pouf."""

    nombre: int
    diametre_mm: float
    entraxe_x_mm: float
    entraxe_y_mm: float
    type_assemblage: str
    commentaire: str


def recaler_fixations_module(
    gamme: str,
    force_dynamique_crete_n: float,
    largeur_logement_mm: float,
    profondeur_logement_mm: float,
) -> FixationsModule:
    """Nombre, diamètre et entraxe des fixations internes, selon la gamme.

    Assemblage prévu : tourillons et/ou inserts noyés dans des blocs
    d'ancrage internes — rien de visible en façade. Dimensionnement
    simplifié (effort dynamique + CS 3), à reprendre par un ingénieur.
    """
    # Effort de cisaillement unitaire visé : ~15 MPa admissible acier, on
    # reste très en dessous (bois / insert). On dimensionne plutôt au bois.
    from incognito.parametres import CHENE, CHARGES_DEFAUT  # local to avoid clutter
    # On utilise une charge de service égale à la force dynamique.
    if force_dynamique_crete_n <= 80:
        nombre, diametre = 4, 8.0
    elif force_dynamique_crete_n <= 200:
        nombre, diametre = 4, 10.0
    else:
        nombre, diametre = 6, 10.0
    if gamme == GAMME_SYBIAN_HAUT:
        # Voice coil : efforts surtout axiaux, un peu moins de cisaillement global.
        # On garde 4 points, entraxe large pour le moment de porte-à-faux d'une housse.
        nombre = max(nombre, 4)
    else:
        # Balourd : effort tournant, 4 à 6 points.
        nombre = max(nombre, 4)
    marge = 30.0
    if nombre == 4:
        entraxe_x = max(largeur_logement_mm - 2 * marge, 80.0)
        entraxe_y = max(profondeur_logement_mm - 2 * marge, 80.0)
    else:
        entraxe_x = max(largeur_logement_mm - 2 * marge, 80.0)
        entraxe_y = max((profondeur_logement_mm - 2 * marge) / 2.0, 60.0)
    return FixationsModule(
        nombre=nombre,
        diametre_mm=diametre,
        entraxe_x_mm=entraxe_x,
        entraxe_y_mm=entraxe_y,
        type_assemblage="insert_noye_et_tourillon",
        commentaire=(
            f"Gamme {gamme} : {nombre} inserts Ø {diametre:g} mm, "
            f"entraxes {entraxe_x:.0f} × {entraxe_y:.0f} mm, dans des blocs "
            "d'ancrage internes (tourillons + collage). Invisibles en façade. "
            f"Force dynamique de calage ≈ {force_dynamique_crete_n:.0f} N. "
            "Le couple de vissage d'une housse ne doit pas passer dans ces "
            "fixations : l'embout a un blocage en rotation propre."
        ),
    )


@dataclass(frozen=True)
class LogementMoteur:
    """Encombrement interne du logement (intérieur caisson, hors silentblocs de calage)."""

    largeur_mm: float
    profondeur_mm: float
    hauteur_mm: float
    jeu_lateral_mm: float
    commentaire: str


def recaler_logement(
    gamme: str,
    choix: ChoixSilentblocs,
    debattement_mm: float,
) -> LogementMoteur:
    """Recalcule le logement selon l'actionneur, les plots et le débattement."""
    jeu = max(JEU_DEBATTEMENT_MIN_MM, debattement_mm + 4.0, choix.deflexion_statique_mm + 4.0)
    if gamme == GAMME_SYBIAN_HAUT:
        # Stator 60,4 + carter + ressorts de guidage + courses.
        largeur = VCAR_0105.diametre_stator_mm + 80.0 + 2 * jeu
        profondeur = VCAR_0105.diametre_stator_mm + 80.0 + 2 * jeu
        hauteur = (
            VCAR_0105.longueur_mm
            + VCAR_0105.course_totale_mm
            + FILETAGE_1_NPT.depassement_recommande_mm
            + choix.silentbloc.hauteur_libre_mm
            + jeu
            + 40.0  # ressorts + platine
        )
        commentaire = (
            "Logement voice coil : stator, guidage à ressorts, embout 1\" NPT, "
            f"plots {choix.silentbloc.nom_affiche} (×{choix.nombre}), jeu {jeu:.1f} mm."
        )
    else:
        largeur = BALOURD_24V.longueur_mm + 60.0 + 2 * jeu  # moteur souvent couché
        profondeur = BALOURD_24V.diametre_mm + 70.0 + 2 * jeu  # carter mousse dense
        hauteur = (
            BALOURD_24V.diametre_mm
            + 40.0  # mousse de carter
            + choix.silentbloc.hauteur_libre_mm
            + jeu
            + 30.0
        )
        commentaire = (
            "Logement balourd : moteur sous carter mousse dense (pièces tournantes "
            f"inaccessibles), plots {choix.silentbloc.nom_affiche} (×{choix.nombre}), "
            f"jeu {jeu:.1f} mm."
        )
    return LogementMoteur(
        largeur_mm=largeur,
        profondeur_mm=profondeur,
        hauteur_mm=hauteur,
        jeu_lateral_mm=jeu,
        commentaire=commentaire,
    )


@dataclass(frozen=True)
class RecalageModule:
    """Recalage complet d'un module (logement, plots, fixations, housse)."""

    gamme: str
    choix_silentblocs: ChoixSilentblocs
    logement: LogementMoteur
    fixations: FixationsModule
    diagnostic_housse: DiagnosticHousse | None
    force_dynamique_crete_n: float
    masse_suspendue_kg: float
    frequence_exc_min_hz: float
    frequence_exc_max_hz: float


def recaler_module_vibrant(
    gamme: str,
    masse_housse_kg: float = MASSE_HOUSSE_DEFAUT_KG,
    masse_plateau_kg: float = 0.35,
    masse_cadre_kg: float | None = None,
) -> RecalageModule:
    """Recalcule tout le module à partir de la gamme et de la masse de housse.

    C'est le point d'entrée utilisé par la grammaire : changer ``gamme``
    doit changer logement, silentblocs et fixations.
    """
    variante = variante_par_gamme(gamme)
    embout = masse_embout_kg("inox_316")
    if gamme == GAMME_SYBIAN_HAUT:
        vc = VCAR_0105
        masse_mobile = vc.masse_mobile_kg + embout + masse_plateau_kg + masse_housse_kg
        # Cadre suspendu : stator + carter + driver local (hypothèse).
        masse_cadre = 2.8 if masse_cadre_kg is None else masse_cadre_kg
        masse_suspendue = masse_cadre + masse_mobile
        # Fréquence min d'isolement : 18 Hz (rapport 3 visé pour f0 ≈ 6 Hz).
        # La bobine peut descendre à 8 Hz, mais alors T peut dépasser 1 (le meuble vibre).
        f_min, f_max = max(vc.frequence_min_hz, 18.0), vc.frequence_max_hz
        # Force dynamique vue par les plots : réaction du stator ≈ force du coil
        # (plus un transitoire). On prend la crête catalogue.
        force_dyn = vc.force_crete_n
        diag = diagnostiquer_housse_haut(
            masse_housse_kg=masse_housse_kg,
            masse_equipage_hors_housse_kg=vc.masse_mobile_kg + embout + masse_plateau_kg,
        )
        # Débattement : course du coil + déflexion plots (l'utilisateur ne
        # doit pas faire taper le carter).
        debattement = vc.course_totale_mm / 2.0
    else:
        bal = BALOURD_24V
        # En entrée, la housse est solidaire du plateau vibrant (tout le
        # module vibre). Elle s'ajoute à la masse suspendue, pas à une
        # « masse mobile de coil ».
        masse_moteur = bal.masse_moteur_kg + bal.masse_balourd_kg
        masse_cadre = 1.6 if masse_cadre_kg is None else masse_cadre_kg
        masse_suspendue = masse_cadre + masse_moteur + masse_plateau_kg + embout + masse_housse_kg
        f_min, f_max = bal.frequence_min_hz, bal.frequence_max_hz
        force_dyn = force_centrifuge_n(
            bal.masse_balourd_kg, bal.excentricite_mm, bal.n_limite_logicielle_tr_min
        )
        # Diagnostic housse spécifique entrée : on vérifie le décalage de f0
        # et la charge des plots, pas une course linéaire.
        diag = None
        debattement = 4.0  # ordre de grandeur, raffiné après le choix des plots

    choix = choisir_silentblocs(
        gamme=gamme,
        masse_suspendue_kg=masse_suspendue,
        frequence_exc_min_hz=f_min,
        frequence_exc_max_hz=f_max,
        force_dynamique_crete_n=force_dyn,
    )
    if gamme == GAMME_SYBIAN_ENTREE:
        # Amplitude typique du module isolé à r ≫ 1 : x ≈ (m e) / M.
        bal = BALOURD_24V
        debattement = max(
            4.0,
            (bal.masse_balourd_kg * (bal.excentricite_mm / 1000.0) / masse_suspendue) * 1000.0 * 3.0,
        )
    logement = recaler_logement(gamme, choix, debattement)
    fixations = recaler_fixations_module(
        gamme, force_dyn, logement.largeur_mm, logement.profondeur_mm
    )
    return RecalageModule(
        gamme=gamme,
        choix_silentblocs=choix,
        logement=logement,
        fixations=fixations,
        diagnostic_housse=diag,
        force_dynamique_crete_n=force_dyn,
        masse_suspendue_kg=masse_suspendue,
        frequence_exc_min_hz=f_min,
        frequence_exc_max_hz=f_max,
    )


# ---------------------------------------------------------------------------
# Architecture 3 modules (gamme haut) : masses, empilement, encombrement
# ---------------------------------------------------------------------------

from incognito.catalogues.moteurs import (  # noqa: E402
    PISTON_VCAR_0110,
    ROTATION_EC45,
    budget_electrique_haut,
)


ARCHITECTURE_PARALLELE = "parallele_decouple"
ARCHITECTURE_SERIE = "empile_serie"

# Dimensionnement housse demandé : 0,5–1 kg (défaut au milieu).
MASSE_HOUSSE_DIMENSIONNEMENT_MIN_KG = 0.50
MASSE_HOUSSE_DIMENSIONNEMENT_MAX_KG = 1.00
MASSE_HOUSSE_DIMENSIONNEMENT_KG = 0.75


@dataclass(frozen=True)
class AnalyseMasses:
    """Compare l'architecture série (VC en bas qui porte tout) et le découplage."""

    architecture: str
    masse_mobile_vibration_kg: float
    force_requise_15hz_8mm_n: float
    force_disponible_n: float
    hors_capacite_15hz_8mm: bool
    masse_mobile_piston_kg: float
    force_piston_requise_2hz_15mm_n: float
    recommendation: str
    messages: tuple[str, ...]


def analyser_masses_empilement(
    masse_housse_kg: float = MASSE_HOUSSE_DIMENSIONNEMENT_KG,
    modules_actifs: tuple[str, ...] = ("vibration", "piston", "rotation"),
    architecture: str = ARCHITECTURE_PARALLELE,
) -> AnalyseMasses:
    """Analyse la masse mobile vue par chaque étage selon l'architecture.

    En série (voice coil en bas) : le VC devrait accélérer piston + plateau
    + selle + housse — typiquement hors capacité à 15 Hz / 8 mm.
    En parallèle découplé (retenu) : le VC n'anime que l'embout + la housse
    (et une petite platine), le piston anime le chariot (rotation + VC stator
    + selle), le poids assis reste sur la couronne du pouf.
    """
    embout = masse_embout_kg("inox_316")
    platine = 0.20
    stator_vc = 0.35  # stator + carter local, hypothèse
    piston_stator = 0.45
    rotation = (
        ROTATION_EC45.masse_moteur_kg + 0.35  # réducteur estimé
        + 0.15  # plateau + roulement de butée
    )
    msgs: list[str] = []

    if architecture == ARCHITECTURE_SERIE:
        # VC en bas porte tout ce qui est au-dessus.
        m_vib = VCAR_0105.masse_mobile_kg + embout + platine
        if "piston" in modules_actifs:
            m_vib += piston_stator + PISTON_VCAR_0110.masse_mobile_kg
        if "rotation" in modules_actifs:
            m_vib += rotation
        m_vib += masse_housse_kg
        rec = (
            "Architecture série déconseillée : la masse mobile du voice coil "
            "inclut les étages supérieurs. Passer en parallèle découplé, ou "
            "placer le voice coil tout en haut sous la selle."
        )
    else:
        # Découplé : VC en haut, ne porte que platine + embout + housse.
        m_vib = VCAR_0105.masse_mobile_kg + embout + platine + masse_housse_kg
        rec = (
            "Architecture retenue : parallèle découplé. Voice coil en haut "
            "sous la selle (masse mobile = équipage + housse). Piston en "
            "retrait, relié par un palonnier, anime le chariot (rotation + "
            "stator du VC). Filetage 1\" NPT au sommet de l'étage le plus haut."
        )

    f_vib = force_requise_voice_coil_n(m_vib, 8.0, 15.0)
    hors = f_vib > VCAR_0105.force_crete_n
    if hors:
        msgs.append(
            f"Vibration hors capacité à 15 Hz / 8 mm : {f_vib:.0f} N > "
            f"{VCAR_0105.force_crete_n:.0f} N (masse mobile {m_vib:.2f} kg)."
        )
    else:
        msgs.append(
            f"Vibration à 15 Hz / 8 mm : {f_vib:.0f} N ≤ "
            f"{VCAR_0105.force_crete_n:.0f} N crête (masse {m_vib:.2f} kg). "
            f"Force continue catalogue {VCAR_0105.force_continue_25c_n:.1f} N "
            "à surveiller en régime prolongé."
        )

    # Masse vue par le piston (chariot : rotation + stator VC + platine, pas l'usager).
    m_pis = PISTON_VCAR_0110.masse_mobile_kg + 0.25  # tige / palonnier
    if "rotation" in modules_actifs:
        m_pis += rotation
    if "vibration" in modules_actifs:
        m_pis += stator_vc + VCAR_0105.masse_mobile_kg + embout + platine
    m_pis += masse_housse_kg
    f_pis = force_requise_voice_coil_n(m_pis, 15.0, 2.0)
    msgs.append(
        f"Piston à 2 Hz / 15 mm : force requise {f_pis:.1f} N pour une masse "
        f"de chariot {m_pis:.2f} kg (disponible {PISTON_VCAR_0110.force_crete_n:.0f} N "
        f"crête, {PISTON_VCAR_0110.force_continue_25c_n:.1f} N continu)."
    )
    return AnalyseMasses(
        architecture=architecture,
        masse_mobile_vibration_kg=m_vib,
        force_requise_15hz_8mm_n=f_vib,
        force_disponible_n=VCAR_0105.force_crete_n,
        hors_capacite_15hz_8mm=hors,
        masse_mobile_piston_kg=m_pis,
        force_piston_requise_2hz_15mm_n=f_pis,
        recommendation=rec,
        messages=tuple(msgs),
    )


@dataclass(frozen=True)
class EncombrementVertical:
    """Hauteur d'empilement vs intérieur du pouf."""

    architecture: str
    hauteur_modules_mm: float
    hauteur_interieure_disponible_mm: float
    rentre: bool
    hauteur_pouf_recommandee_mm: float
    commentaire: str


def encombrement_vertical_haut(
    architecture: str,
    hauteur_pouf_mm: float,
    hauteur_coussin_mm: float,
    hauteur_pieds_mm: float,
    epaisseur_fond_mm: float,
    epaisseur_couronne_mm: float,
    hauteur_silentblocs_mm: float,
    modules_actifs: tuple[str, ...] = ("vibration", "piston", "rotation"),
) -> EncombrementVertical:
    """Vérifie que les modules rentrent sous le coussin d'un pouf ~430–450 mm."""
    interieur = (
        hauteur_pouf_mm
        - hauteur_pieds_mm
        - epaisseur_fond_mm
        - hauteur_coussin_mm
        - epaisseur_couronne_mm
    )
    h_sb = hauteur_silentblocs_mm + 8.0  # flèche + semelle
    h_piston = (PISTON_VCAR_0110.longueur_mm + PISTON_VCAR_0110.course_totale_mm + 20.0)
    h_rot = 20.0 + 45.0 + 18.0  # moteur plat + réducteur + butée (ordres de grandeur)
    h_vib = VCAR_0105.longueur_mm + VCAR_0105.course_totale_mm + FILETAGE_1_NPT.depassement_recommande_mm + 10.0
    if architecture == ARCHITECTURE_SERIE:
        h = h_sb
        if "piston" in modules_actifs:
            h += h_piston
        if "rotation" in modules_actifs:
            h += h_rot
        if "vibration" in modules_actifs:
            h += h_vib
        elif "rotation" in modules_actifs or "piston" in modules_actifs:
            h += FILETAGE_1_NPT.depassement_recommande_mm
    else:
        # Piston à côté : n'ajoute pas sa longueur à la pile axiale.
        col_centrale = h_sb
        if "rotation" in modules_actifs:
            col_centrale += h_rot
        if "vibration" in modules_actifs:
            col_centrale += h_vib
        elif "rotation" in modules_actifs:
            col_centrale += FILETAGE_1_NPT.depassement_recommande_mm
        h = max(col_centrale, h_sb + (h_piston if "piston" in modules_actifs else 0.0))
    rentre = h + 8.0 <= interieur
    if rentre:
        reco = hauteur_pouf_mm
        com = (
            f"Hauteur modules {h:.0f} mm pour {interieur:.0f} mm disponibles "
            f"dans un pouf de {hauteur_pouf_mm:.0f} mm (architecture {architecture}). "
            "Ça rentre, avec une marge à confirmer en CAO."
        )
    else:
        manque = h + 8.0 - interieur
        reco = hauteur_pouf_mm + manque
        reco = 10.0 * ((reco + 9.0) // 10.0)
        com = (
            f"Hauteur modules {h:.0f} mm > intérieur {interieur:.0f} mm "
            f"(pouf {hauteur_pouf_mm:.0f} mm). Déclinaison recommandée : "
            f"hauteur hors-tout ≈ {reco:.0f} mm, ou réduction du coussin, "
            f"ou architecture parallèle si ce n'est pas déjà le cas."
        )
    return EncombrementVertical(
        architecture=architecture,
        hauteur_modules_mm=h,
        hauteur_interieure_disponible_mm=interieur,
        rentre=rentre,
        hauteur_pouf_recommandee_mm=reco,
        commentaire=com,
    )


# ---------------------------------------------------------------------------
# Bruit aérien vs isolation solidienne : treillis rigide ≠ silentbloc
# ---------------------------------------------------------------------------

# Module d'Young typique du PETG imprimé (hypothèse, 20 °C).
MODULE_YOUNG_PETG_MPA = 2000.0
MODULE_YOUNG_PLA_MPA = 3200.0
REMPLISSAGE_TREILLIS_DEFAUT = 0.40


@dataclass(frozen=True)
class ComparaisonTreillisSilentbloc:
    """Raideur d'un plot treillis PETG/PLA 40 % vs silentbloc silicone.

    Le treillis est évalué sur le *même enveloppe* que le plot silicone
    très souple (Ø 32 × 36 mm). Deux bornes d'homogénéisation :

    * traction/compression (étirement des barres) : E_eff ≈ E × φ ;
    * flexion (treillis à nœuds) : E_eff ≈ E × φ².

    Même la borne la plus souple reste des ordres de grandeur trop raide
    pour isoler dès 8–60 Hz. Ce n'est pas un calcul éléments finis.
    """

    materiau_treillis: str
    module_e_mpa: float
    remplissage: float
    diametre_mm: float
    hauteur_mm: float
    nombre_plots: int
    masse_suspendue_kg: float
    frequence_exc_min_hz: float
    raideur_solide_n_par_mm: float
    raideur_treillis_traction_n_par_mm: float
    raideur_treillis_flexion_n_par_mm: float
    raideur_silentbloc_n_par_mm: float
    rapport_raideur_flexion: float
    f0_silentbloc_hz: float
    f0_treillis_flexion_hz: float
    transmissibilite_silentbloc: float
    transmissibilite_treillis_flexion: float
    treillis_adapte_isolation_solidienne: bool
    commentaire: str


def raideur_colonne_n_par_mm(module_e_mpa: float, diametre_mm: float, hauteur_mm: float) -> float:
    """k = E A / L d'une colonne circulaire, en N/mm."""
    if module_e_mpa <= 0 or diametre_mm <= 0 or hauteur_mm <= 0:
        raise ValueError("Géométrie / module invalides.")
    rayon_m = (diametre_mm / 2.0) / 1000.0
    aire_m2 = 3.141592653589793 * rayon_m * rayon_m
    hauteur_m = hauteur_mm / 1000.0
    module_pa = module_e_mpa * 1e6
    return (module_pa * aire_m2 / hauteur_m) / 1000.0  # N/m → N/mm


def comparer_treillis_et_silentbloc(
    raideur_silentbloc_n_par_mm: float = 1.5,
    nombre_plots: int = 4,
    masse_suspendue_kg: float = 4.224,
    frequence_exc_min_hz: float = 18.0,
    diametre_mm: float = 32.0,
    hauteur_mm: float = 36.0,
    materiau: str = "PETG",
    remplissage: float = REMPLISSAGE_TREILLIS_DEFAUT,
    zeta_treillis: float = 0.03,
    zeta_silentbloc: float = 0.08,
) -> ComparaisonTreillisSilentbloc:
    """Montre qu'un treillis PETG/PLA 40 % ne peut pas servir de silentbloc."""
    e_mpa = MODULE_YOUNG_PETG_MPA if materiau.upper() == "PETG" else MODULE_YOUNG_PLA_MPA
    k_solide = raideur_colonne_n_par_mm(e_mpa, diametre_mm, hauteur_mm)
    k_traction = k_solide * remplissage
    k_flexion = k_solide * (remplissage ** 2)
    rapport = k_flexion / raideur_silentbloc_n_par_mm
    k_eq_s = nombre_plots * raideur_silentbloc_n_par_mm * 1000.0  # N/m
    k_eq_t = nombre_plots * k_flexion * 1000.0
    f0_s = frequence_propre_hz(k_eq_s, masse_suspendue_kg)
    f0_t = frequence_propre_hz(k_eq_t, masse_suspendue_kg)
    r_s = frequence_exc_min_hz / f0_s if f0_s > 0 else 0.0
    r_t = frequence_exc_min_hz / f0_t if f0_t > 0 else 0.0
    t_s = transmissibilite(r_s, zeta_silentbloc)
    t_t = transmissibilite(r_t, zeta_treillis)
    adapte = bool(f0_t <= frequence_exc_min_hz / 2.0 ** 0.5 and t_t < 1.0)
    com = (
        f"Plot {materiau} {remplissage:.0%} Ø{diametre_mm:.0f}×{hauteur_mm:.0f} mm : "
        f"même en borne flexion, k ≈ {k_flexion:.0f} N/mm "
        f"({rapport:.0f}× le silentbloc silicone {raideur_silentbloc_n_par_mm} N/mm). "
        f"f0 treillis ≈ {f0_t:.0f} Hz vs f0 silicone ≈ {f0_s:.2f} Hz. "
        f"À {frequence_exc_min_hz:.0f} Hz, T_treillis ≈ {t_t:.2f} "
        f"(pas d'isolation, r ≪ 1) contre T_silicone ≈ {t_s:.3f}. "
        "Les silentblocs restent en élastomère (silicone du commerce ou TPU). "
        "Le treillis PETG/PLA est réservé aux panneaux de bruit *aérien*."
    )
    return ComparaisonTreillisSilentbloc(
        materiau_treillis=materiau,
        module_e_mpa=e_mpa,
        remplissage=remplissage,
        diametre_mm=diametre_mm,
        hauteur_mm=hauteur_mm,
        nombre_plots=nombre_plots,
        masse_suspendue_kg=masse_suspendue_kg,
        frequence_exc_min_hz=frequence_exc_min_hz,
        raideur_solide_n_par_mm=k_solide,
        raideur_treillis_traction_n_par_mm=k_traction,
        raideur_treillis_flexion_n_par_mm=k_flexion,
        raideur_silentbloc_n_par_mm=raideur_silentbloc_n_par_mm,
        rapport_raideur_flexion=rapport,
        f0_silentbloc_hz=f0_s,
        f0_treillis_flexion_hz=f0_t,
        transmissibilite_silentbloc=t_s,
        transmissibilite_treillis_flexion=t_t,
        treillis_adapte_isolation_solidienne=adapte,
        commentaire=com,
    )
