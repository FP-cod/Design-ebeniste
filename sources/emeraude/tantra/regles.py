# -*- coding: utf-8 -*-
"""Règles de recalcul de la gamme Tantra (couche 2).

Toutes les règles sont des **modèles volontairement simplifiés** :

* résistance : on compare ``CS × effort de service`` à une résistance
  **caractéristique** (fm,k, fv,k, résistance d'une broche…) ; CS ≥ 3 ;
* stabilité : voir ``tantra.geometrie.coefficient_stabilite`` ;
* sécurité des mécanismes (volet 3) : double verrouillage, pincement,
  déverrouillage sous charge, effort de manœuvre.

Un résultat « ok » n'est pas une validation d'ingénieur et ne dispense
jamais d'un essai de charge réel.

Différence assumée avec Incognito : Incognito comparait CS × F à une
contrainte *admissible* (≈ fk / 2,8 à 3,5), soit un CS effectif proche
de 8 à 10 sur les blocs d'ancrage. Ici le CS est appliqué à la valeur
caractéristique (définition usuelle), mais des **minimums constructifs**
(bloc ≥ 50 × 80 × 80 mm, distance au bord ≥ max(25 mm, 2Ø)) maintiennent
des dimensions comparables.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import ceil, inf, pi, tan, radians

from tantra.catalogues.fixations import Fixation, INSERT_ANCRE_M12
from tantra.catalogues.mecanismes import AxeTraversant, Verrou
from tantra.geometrie import Verification
from tantra.parametres import (
    CHARGES_DEFAUT,
    COEFFICIENT_SECURITE_MIN,
    G,
    NIVEAU_AVERTISSEMENT,
    NIVEAU_ESSAI_REQUIS,
    NIVEAU_NON_CONFORME,
    NIVEAU_OK,
    Essence,
    ParametresCharge,
)


def _arrondir_dessus(valeur: float, pas: float = 2.0) -> float:
    return pas * ceil(valeur / pas - 1e-9)


def verif(code: str, ok: bool, message: str, compromis: bool = False,
          niveau_echec: str = NIVEAU_NON_CONFORME) -> Verification:
    """Fabrique une ``Verification`` : niveau ok si ``ok``, sinon ``niveau_echec``."""
    return Verification(code, ok, NIVEAU_OK if ok else niveau_echec, message, compromis)


def essai_requis(code: str, message: str) -> Verification:
    return Verification(code, True, NIVEAU_ESSAI_REQUIS, message)


# ---------------------------------------------------------------------------
# Ancrages
# ---------------------------------------------------------------------------

def arrachement_insert_n(diametre_mm: float, longueur_ef_mm: float, rho_k: float) -> float:
    """Résistance caractéristique à l'arrachement d'un insert fileté (N).

    Formule des vis de l'EN 1995-1-1 (§8.7.2, éq. 8.39–8.40a, n_ef = 1) :
    f_ax,k = 0,52 d^-0,5 l_ef^-0,1 ρk^0,8 ; F = f_ax,k × d × l_ef.
    Appliquée **par analogie** à un insert fileté ; ``d`` est plafonné à
    12 mm (domaine de validité de la formule), ce qui est conservateur.
    """
    if min(diametre_mm, longueur_ef_mm, rho_k) <= 0:
        raise ValueError("Diamètre, longueur et ρk doivent être > 0.")
    d = min(diametre_mm, 12.0)
    f_ax = 0.52 * d**-0.5 * longueur_ef_mm**-0.1 * rho_k**0.8
    return f_ax * d * longueur_ef_mm


@dataclass(frozen=True)
class BlocAncrage:
    """Bloc local de bois dur recevant un insert d'ancre."""

    epaisseur_mm: float
    largeur_mm: float
    longueur_mm: float
    paroi_mm: float
    distance_bord_mm: float
    recouvrement_mm: float
    cs_arrachement: float
    cs_cisaillement_paroi: float
    nombre_tourillons: int
    verifications: tuple[Verification, ...]


def recaler_bloc_ancrage(essence: Essence, charges: ParametresCharge | None = None,
                         recouvrement_mm: float = 0.0,
                         insert: Fixation = INSERT_ANCRE_M12) -> BlocAncrage:
    """Dimensionne un bloc d'ancrage local (insert M12 noyé).

    * parois de part et d'autre de l'insert : F·CS = fv,k · L · t · 2 plans ;
    * arrachement : ``arrachement_insert_n`` ≥ F·CS ;
    * liaison bloc / structure : tourillons Ø12 + collage, n = ⌈F·CS / R_k⌉
      (le collage n'est pas compté : marge) ;
    * ``recouvrement_mm`` : bois ou cache masquant l'insert (volet 2),
      jamais compté comme section résistante.
    """
    charges = charges or CHARGES_DEFAUT
    if charges.coefficient_securite < COEFFICIENT_SECURITE_MIN:
        raise ValueError(
            f"CS {charges.coefficient_securite:g} < {COEFFICIENT_SECURITE_MIN:g} : "
            "recalage refusé plutôt que sous-dimensionné."
        )
    f_visee = charges.charge_rupture_visee_ancrage_n
    d = insert.cotes_mm["diametre_insert"]
    l_ef = insert.cotes_mm["longueur_encastrement"]
    paroi = f_visee / (essence.fv_k_mpa * l_ef * 2.0)
    bord = max(25.0, 2.0 * d)
    epaisseur = _arrondir_dessus(max(2.0 * paroi + d + recouvrement_mm, 50.0 + recouvrement_mm))
    largeur = _arrondir_dessus(max(d + 2.0 * bord, 60.0))
    longueur = _arrondir_dessus(max(l_ef + 20.0, 80.0))
    r_arr = arrachement_insert_n(d, l_ef, essence.masse_volumique_caracteristique_kg_m3)
    cs_arr = r_arr / charges.charge_service_ancrage_n
    paroi_reelle = (epaisseur - recouvrement_mm - d) / 2.0
    cs_paroi = (essence.fv_k_mpa * l_ef * paroi_reelle * 2.0) / charges.charge_service_ancrage_n
    from tantra.catalogues.fixations import TOURILLON_12
    n_tour = max(2, ceil(f_visee / TOURILLON_12.resistance_caracteristique_n))
    v = [
        verif("bloc_arrachement", cs_arr >= charges.coefficient_securite,
              f"Arrachement insert : R_k ≈ {r_arr / 1000:.1f} kN, CS {cs_arr:.1f} "
              f"(visé ≥ {charges.coefficient_securite:g}) — formule EC5 des vis, par analogie."),
        verif("bloc_paroi", cs_paroi >= charges.coefficient_securite,
              f"Parois {paroi_reelle:.1f} mm de part et d'autre de l'insert : CS cisaillement "
              f"{cs_paroi:.1f} (paroi mini calculée {paroi:.1f} mm)."),
        verif("bloc_essence", essence.famille != "contreplaque",
              f"Bloc en {essence.nom_affiche} : un contreplaqué tient mal un insert "
              "(cisaillement roulant) — bloc en massif ou lamellé exigé.",
              niveau_echec=NIVEAU_NON_CONFORME),
        essai_requis("bloc_essai", "Essai d'arrachement réel de l'insert dans le bloc (série et bois réels)."),
    ]
    return BlocAncrage(epaisseur, largeur, longueur, paroi, bord, recouvrement_mm,
                       cs_arr, cs_paroi, n_tour, tuple(v))


def piece_loge_insert(largeur_transverse_mm: float, profondeur_axiale_mm: float, essence: Essence,
                      charges: ParametresCharge | None = None, recouvrement_mm: float = 0.0,
                      insert: Fixation = INSERT_ANCRE_M12) -> tuple[bool, str]:
    """Une pièce courante peut-elle recevoir l'insert sans bloc rapporté ?

    * ``largeur_transverse_mm`` : largeur de bois perpendiculaire à l'axe de
      l'insert (doit loger 2 parois de cisaillement + Ø insert, et ≥ 50 mm) ;
    * ``profondeur_axiale_mm`` : bois disponible selon l'axe (encastrement +
      recouvrement de discrétion éventuel).
    """
    charges = charges or CHARGES_DEFAUT
    d = insert.cotes_mm["diametre_insert"]
    l_ef = insert.cotes_mm["longueur_encastrement"]
    paroi = charges.charge_rupture_visee_ancrage_n / (essence.fv_k_mpa * l_ef * 2.0)
    besoin_t = max(2.0 * paroi + d, 50.0)
    besoin_a = l_ef + recouvrement_mm
    ok = largeur_transverse_mm >= besoin_t and profondeur_axiale_mm >= besoin_a
    txt = (f"largeur {largeur_transverse_mm:g} mm (besoin {besoin_t:.0f}) × profondeur "
           f"{profondeur_axiale_mm:g} mm (besoin {besoin_a:.0f} = encastrement {l_ef:g} + "
           f"recouvrement {recouvrement_mm:g})")
    return ok, txt


def section_loge_insert(epaisseur_piece_mm: float, essence: Essence,
                        charges: ParametresCharge | None = None,
                        recouvrement_mm: float = 0.0,
                        insert: Fixation = INSERT_ANCRE_M12) -> bool:
    """True si une pièce courante d'épaisseur donnée peut loger l'insert sans bloc local."""
    bloc = recaler_bloc_ancrage(essence, charges, recouvrement_mm, insert)
    return epaisseur_piece_mm >= bloc.epaisseur_mm


# ---------------------------------------------------------------------------
# Flexion, tenons, tourillons
# ---------------------------------------------------------------------------

def contrainte_flexion_mpa(portee_mm: float, b_mm: float, h_mm: float, force_n: float,
                           cas: str = "centree") -> float:
    """Contrainte de flexion maxi d'une poutre sur deux appuis (MPa).

    ``cas`` : ``"centree"`` (M = FL/4) ou ``"repartie"`` (M = FL/8, F totale).
    """
    if min(portee_mm, b_mm, h_mm) <= 0 or force_n < 0:
        raise ValueError("Portée, b, h > 0 et force ≥ 0 requis.")
    if cas == "centree":
        m = force_n * portee_mm / 4.0
    elif cas == "repartie":
        m = force_n * portee_mm / 8.0
    elif cas == "console":
        m = force_n * portee_mm
    else:
        raise ValueError(f"Cas de charge inconnu « {cas} ».")
    w = b_mm * h_mm**2 / 6.0
    return m / w


def cs_flexion(portee_mm: float, b_mm: float, h_mm: float, force_n: float,
               essence: Essence, cas: str = "centree") -> float:
    """CS en flexion = fm,k / σ_service."""
    s = contrainte_flexion_mpa(portee_mm, b_mm, h_mm, force_n, cas)
    return inf if s == 0 else essence.fm_k_mpa / s


def fleche_mm(portee_mm: float, b_mm: float, h_mm: float, force_n: float,
              essence: Essence, cas: str = "centree") -> float:
    """Flèche élastique (mm) : FL³/48EI (centrée) ou 5FL³/384EI (répartie)."""
    i = b_mm * h_mm**3 / 12.0
    e = essence.module_elasticite_mpa
    if cas == "centree":
        return force_n * portee_mm**3 / (48.0 * e * i)
    if cas == "repartie":
        return 5.0 * force_n * portee_mm**3 / (384.0 * e * i)
    if cas == "console":
        return force_n * portee_mm**3 / (3.0 * e * i)
    raise ValueError(f"Cas de charge inconnu « {cas} ».")


def cs_tenon(effort_n: float, epaisseur_tenon_mm: float, hauteur_tenon_mm: float,
             essence: Essence) -> float:
    """CS au cisaillement d'un tenon : τ = 1,5 F / (e × h) comparé à fv,k."""
    if effort_n <= 0:
        return inf
    tau = 1.5 * effort_n / (epaisseur_tenon_mm * hauteur_tenon_mm)
    return essence.fv_k_mpa / tau


def nombre_tourillons(effort_n: float, fixation: Fixation,
                      cs: float = COEFFICIENT_SECURITE_MIN) -> int:
    """Nombre de tourillons pour reprendre ``effort_n × cs`` en cisaillement (≥ 2)."""
    if fixation.resistance_caracteristique_n <= 0:
        raise ValueError(f"{fixation.nom} n'a pas de résistance unitaire.")
    return max(2, ceil(effort_n * cs / fixation.resistance_caracteristique_n))


def nombre_supports_coque(largeur_mm: float, epaisseur_support_mm: float, epaisseur_coque_mm: float,
                          essence_coque: Essence, charge_ponctuelle_n: float,
                          largeur_diffusion_mm: float = 200.0,
                          cs: float = COEFFICIENT_SECURITE_MIN, n_min: int = 2) -> int:
    """Nombre de flasques (appuis) pour qu'une coque résiste à une charge de genou.

    Coque modélisée en bande de ``largeur_diffusion_mm`` (diffusion par la
    mousse) sur deux appuis, charge centrée. On augmente le nombre d'appuis
    jusqu'à CS ≥ ``cs``.
    """
    for n in range(n_min, 12):
        portee = (largeur_mm - n * epaisseur_support_mm) / (n - 1) + epaisseur_support_mm
        if cs_flexion(portee, largeur_diffusion_mm, epaisseur_coque_mm, charge_ponctuelle_n,
                      essence_coque) >= cs:
            return n
    raise ValueError("Coque trop mince : aucune répartition raisonnable d'appuis ne suffit.")


def rayon_cintrage_minimal_mm(epaisseur_pli_mm: float = 1.5, facteur: float = 100.0) -> float:
    """Rayon intérieur minimal de cintrage d'un contreplaqué moulé (mm).

    Règle d'atelier : R_min ≈ 100 × épaisseur de pli (plis de 1,5 mm →
    ~150 mm). Hypothèse à confirmer avec le fournisseur de placage ; les
    rayons plus serrés imposent des plis de 0,6–1 mm ou un cintrage vapeur
    du massif (frêne, hêtre).
    """
    if epaisseur_pli_mm <= 0 or facteur <= 0:
        raise ValueError("Épaisseur de pli et facteur > 0 requis.")
    return facteur * epaisseur_pli_mm


# ---------------------------------------------------------------------------
# Mécanismes (volet 3) : axes, verrous, pincement, manœuvre
# ---------------------------------------------------------------------------

def portance_bois_mpa(diametre_mm: float, essence: Essence) -> float:
    """Portance locale caractéristique, perçage préalable : f_h,0,k = 0,082 (1 − 0,01 d) ρk.

    EN 1995-1-1, éq. 8.32 (effort parallèle au fil). Pour un effort
    perpendiculaire au fil, la portance est plus faible : on applique ici
    un facteur 0,7 forfaitaire dans ``cs_axe_traversant`` (hypothèse).
    """
    return 0.082 * (1.0 - 0.01 * diametre_mm) * essence.masse_volumique_caracteristique_kg_m3


def cs_axe_traversant(effort_n: float, axe: AxeTraversant, essence: Essence,
                      epaisseur_joue_mm: float, n_joues: int = 2) -> tuple[float, str]:
    """CS d'une charnière à axe traversant : min(cisaillement axe, portance des joues)."""
    if effort_n <= 0:
        return inf, "aucun effort"
    r_axe = axe.resistance_caracteristique_n
    r_bois = 0.7 * portance_bois_mpa(axe.diametre_mm, essence) * epaisseur_joue_mm * axe.diametre_mm * n_joues
    r = min(r_axe, r_bois)
    mode = "cisaillement de l'axe" if r_axe <= r_bois else "portance du bois des joues"
    return r / effort_n, mode


def verifier_double_verrouillage(nom_liaison: str, effort_n: float, verrous: list[Verrou],
                                 cs: float = COEFFICIENT_SECURITE_MIN) -> list[Verification]:
    """Double sécurité obligatoire sur chaque liaison qui maintient l'état CADRE.

    Règles de la gamme :

    1. au moins **deux** verrous **de forme** indépendants (une came seule ne compte pas) ;
    2. **chacun seul** reprend ``effort × CS`` (la défaillance d'un verrou est tolérée) ;
    3. au moins un verrou s'enclenche **seul** (ressort) en fin de course ;
    4. tous les verrous sont **imperdables** (captifs).
    """
    forme = [v for v in verrous if v.verrou_de_forme]
    out = [
        verif(f"{nom_liaison}_double_securite", len(forme) >= 2,
              f"{nom_liaison} : {len(forme)} verrou(s) de forme indépendants (2 exigés)."),
    ]
    for i, v in enumerate(forme):
        cs_v = v.resistance_caracteristique_n / effort_n if effort_n > 0 else inf
        out.append(verif(f"{nom_liaison}_verrou_{i + 1}_seul", cs_v >= cs,
                         f"{nom_liaison} — {v.nom_affiche} seul : R_k ≈ {v.resistance_caracteristique_n / 1000:.1f} kN "
                         f"pour {effort_n:.0f} N, CS {cs_v:.1f} (≥ {cs:g} exigé, verrou seul)."))
    out.append(verif(f"{nom_liaison}_auto_enclenchement",
                     any(v.force_ressort_n > 0 for v in forme),
                     f"{nom_liaison} : au moins un verrou à ressort qui s'enclenche seul en fin de course."))
    out.append(verif(f"{nom_liaison}_imperdables", all(v.imperdable for v in verrous),
                     f"{nom_liaison} : verrous captifs (aucune pièce volante)."))
    return out


def force_retrait_sous_charge_n(effort_cisaillement_n: float, verrou: Verrou,
                                coefficient_frottement: float = 0.3) -> float:
    """Force pour retirer un doigt/goupille chargé en cisaillement : μ·F + ressort."""
    return coefficient_frottement * effort_cisaillement_n + verrou.force_ressort_n


FORCE_MAIN_RETRAIT_MAX_N = 60.0
"""Effort de traction aisé sur un bouton de doigt d'indexage (hypothèse)."""


def verifier_deverrouillage_sous_charge(nom: str, effort_service_n: float, verrou: Verrou,
                                        coefficient_frottement: float = 0.3) -> Verification:
    """Le verrou ne doit pas pouvoir être retiré à la main tant que la liaison est chargée.

    On vérifie à **charge de service réduite** (poids propre + un appui
    léger, 25 % de l'effort de service) : si la force de retrait dépasse
    alors l'effort aisé d'une main, un déverrouillage intempestif sous
    charge est improbable. Sinon, il faut une séquence imposée
    (décharger d'abord) et une forme anti-retrait (gorge, bouton à cran).
    """
    f_reduit = 0.25 * effort_service_n
    f_retrait = force_retrait_sous_charge_n(f_reduit, verrou, coefficient_frottement)
    ok = f_retrait > FORCE_MAIN_RETRAIT_MAX_N
    return verif(
        f"{nom}_deverrouillage_sous_charge", ok,
        f"{nom} — {verrou.nom_affiche} : force de retrait ≈ {f_retrait:.0f} N sous 25 % de la charge "
        f"de service ({f_reduit:.0f} N, μ = {coefficient_frottement:g}). "
        + ("Retrait à la main improbable sous charge." if ok else
           "Retrait possible sous charge : imposer la séquence « décharger puis déverrouiller » et un "
           "bouton à cran / goupille à verrouillage positif."),
        compromis=not ok, niveau_echec=NIVEAU_AVERTISSEMENT,
    )


# EN ISO 13854:2019 (ex-EN 349) : écartements minimaux pour éviter l'écrasement
JEU_DOIGT_SUR_MM = 25.0
"""Écartement minimal pour qu'un doigt ne soit pas écrasé (EN ISO 13854)."""
JEU_INACCESSIBLE_MM = 8.0
"""En dessous, le doigt n'entre pas (règle usuelle des normes mobilier, à vérifier
dans la norme applicable au produit)."""


def verifier_pincement(nom: str, jeu_mm: float) -> Verification:
    """Jeu d'une zone de cisaillement/écrasement en mouvement : ≤ 8 mm ou ≥ 25 mm."""
    ok = jeu_mm <= JEU_INACCESSIBLE_MM or jeu_mm >= JEU_DOIGT_SUR_MM
    return verif(
        f"pincement_{nom}", ok,
        f"Jeu « {nom} » = {jeu_mm:g} mm : zone interdite ]{JEU_INACCESSIBLE_MM:g} ; "
        f"{JEU_DOIGT_SUR_MM:g}[ mm (doigts, EN ISO 13854). "
        + ("Conforme." if ok else "Modifier le jeu ou carter la zone."),
    )


EFFORT_MANOEUVRE_MAX_N = 150.0
"""Effort de manœuvre manuel acceptable, ordre de grandeur (EN 1005-3 / ISO 11228-2)."""


def effort_manoeuvre_n(masse_kg: float, bras_cdg_mm: float, bras_main_mm: float,
                       assistance_nmm: float = 0.0) -> float:
    """Effort à la main pour lever une pièce pivotante : (m g d − assistance) / bras main."""
    if bras_main_mm <= 0:
        raise ValueError("bras_main_mm doit être > 0.")
    return max(0.0, masse_kg * G * bras_cdg_mm - assistance_nmm) / bras_main_mm


def recouvrement_telescope_ok(recouvrement_mm: float, cote_section_mm: float,
                              facteur: float = 3.0) -> bool:
    """Recouvrement minimal d'un montant télescopique : ≥ facteur × côté de section."""
    return recouvrement_mm >= facteur * cote_section_mm


def charge_laterale_personne_inclinee_n(poids_n: float, angle_deg: float = 25.0) -> float:
    """Traction horizontale d'une personne debout penchée : W × tan(angle)."""
    return poids_n * tan(radians(angle_deg))
