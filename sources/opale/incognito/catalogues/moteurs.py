# -*- coding: utf-8 -*-
"""Catalogue des actionneurs du pouf vibrant : voice coil (haut) et balourd (entrée).

Prix de vente indicatifs : fournis par Fabien (fourchettes). Les coûts
matière éventuels sont clairement marqués comme *estimations*.
"""

from __future__ import annotations

from dataclasses import dataclass

from incognito.parametres import (
    GAMME_SYBIAN_ENTREE,
    GAMME_SYBIAN_HAUT,
    TENSION_MODULE_V,
)


@dataclass(frozen=True)
class PrixIndicatif:
    """Prix associé à une variante.

    ``origine`` vaut ``vente_fabien`` (fourchette donnée par Fabien, prix
    vendu indicatif) ou ``estimation_matiere`` (ordre de grandeur BOM,
    non une offre fournisseur).
    """

    minimum_eur: float
    maximum_eur: float
    origine: str
    commentaire: str


@dataclass(frozen=True)
class VoiceCoil:
    """Actionneur linéaire voice coil (gamme haut)."""

    nom: str
    modele: str
    fabricant: str
    force_crete_n: float
    force_continue_25c_n: float
    course_totale_mm: float
    tension_nominale_v: float
    constante_fem_v_s_par_m: float
    masse_mobile_kg: float
    diametre_stator_mm: float
    longueur_mm: float
    frequence_min_hz: float
    frequence_max_hz: float
    source: str
    ecarts_catalogues: str
    hypotheses: str


@dataclass(frozen=True)
class MoteurBalourd:
    """Motoréducteur / moteur 24 V à balourd (gamme entrée)."""

    nom: str
    tension_v: float
    puissance_w: float
    masse_moteur_kg: float
    masse_balourd_kg: float
    excentricite_mm: float
    n_min_tr_min: float
    n_max_tr_min: float
    n_limite_logicielle_tr_min: float
    diametre_mm: float
    longueur_mm: float
    protection_thermique: bool
    source: str
    hypotheses: str

    @property
    def frequence_min_hz(self) -> float:
        return self.n_min_tr_min / 60.0

    @property
    def frequence_max_hz(self) -> float:
        return self.n_limite_logicielle_tr_min / 60.0


# --- Gamme haut : SUPT MOTION VCAR0105-0164-00A --------------------------------
# Specs relevées sur les catalogues publics SUPT / Unite Precision.
# Course : 16,1 mm (supt-motor.com) ou 16,4 mm (supt-motion.com / page EN).
# On retient 16,1 mm (la plus conservative pour le débattement) et on
# documente l'écart.

VCAR_0105 = VoiceCoil(
    nom="vcar_0105_0164",
    modele="VCAR0105-0164-00A",
    fabricant="SUPT MOTION / Suzhou Unite Precision Technology",
    force_crete_n=105.0,
    force_continue_25c_n=35.4,
    course_totale_mm=16.1,
    tension_nominale_v=20.1,
    constante_fem_v_s_par_m=11.5,
    masse_mobile_kg=0.150,
    diametre_stator_mm=60.4,
    longueur_mm=40.4,
    frequence_min_hz=8.0,
    frequence_max_hz=40.0,
    source=(
        "Catalogues publics SUPT MOTION : "
        "http://www.supt-motor.com/products/yzxyqd.html "
        "(force crête 105 N, force continue 35,4 N à 25 °C, course 16,1 mm, "
        "tension 20,1 V, FEM 11,5 V/m/s, masse mobile 150 g, stator Ø 60,4 mm, "
        "longueur 40,4 mm) ; "
        "http://supt-motion.com/en/productshow_21_76.html et "
        "http://www.supt-motion.com/productshow_30_139.html "
        "(mêmes forces, course indiquée 16,4 mm, mêmes masse et diamètre)."
    ),
    ecarts_catalogues=(
        "La course totale est donnée à 16,1 mm sur supt-motor.com et à "
        "16,4 mm sur les pages supt-motion.com (EN et ZH). Écart de 0,3 mm, "
        "non tranché. Valeur retenue : 16,1 mm (conservative pour les jeux). "
        "La tension catalogue (20,1 V) n'est pas 24 V : un driver à courant "
        "constant alimenté en 24 V DC est compatible à condition de limiter "
        "le courant au calibre de la bobine (fiche à demander au fabricant)."
    ),
    hypotheses=(
        "La plage 8–40 Hz n'est pas une spec constructeur : c'est une plage "
        "de pilotage retenue pour une selle (rumbles à basse fréquence, "
        "limitation haute pour l'isolation et le confort). À confirmer par "
        "essai (échauffement, force utile, bruit)."
    ),
)


# --- Gamme entrée : moteur 24 V à balourd (hypothèse de conception) ------------

BALOURD_24V = MoteurBalourd(
    nom="balourd_24v_60w",
    tension_v=TENSION_MODULE_V,
    puissance_w=60.0,
    masse_moteur_kg=1.10,
    masse_balourd_kg=0.045,
    excentricite_mm=12.0,
    n_min_tr_min=1500.0,
    n_max_tr_min=6000.0,
    n_limite_logicielle_tr_min=4500.0,
    diametre_mm=70.0,
    longueur_mm=110.0,
    protection_thermique=True,
    source=(
        "Moteur DC 24 V à balourd, typique des vibreurs industriels légers. "
        "Aucune référence constructeur figée : hypothèse de conception, à "
        "remplacer par une fiche réelle (masse, excentricité, courbe N-M, "
        "classe thermique, IP)."
    ),
    hypotheses=(
        "L'excentricité et la masse du balourd sont choisies pour produire "
        "une force centrifuge de l'ordre de 50–150 N dans la plage utile "
        "(voir incognito.regles.force_centrifuge). La limite logicielle "
        "(4500 tr/min) est inférieure au maximum mécanique déclaré, par "
        "sécurité (échauffement, bruit, fatigue). Démarrage progressif et "
        "arrêt d'urgence imposés, comme en gamme haut."
    ),
)


PRIX_VENTE_HAUT = PrixIndicatif(
    minimum_eur=800.0,
    maximum_eur=1000.0,
    origine="vente_fabien",
    commentaire="Prix vendu indicatif de la variante haut, fourni par Fabien.",
)

PRIX_VENTE_ENTREE = PrixIndicatif(
    minimum_eur=300.0,
    maximum_eur=400.0,
    origine="vente_fabien",
    commentaire="Prix vendu indicatif de la variante entrée, fourni par Fabien.",
)

# Estimations de coût matière (BOM), clairement distinctes du prix de vente.
COUT_MATIERE_HAUT_ESTIME = PrixIndicatif(
    minimum_eur=250.0,
    maximum_eur=450.0,
    origine="estimation_matiere",
    commentaire=(
        "ESTIMATION de coût matière (actionneur VCAR, driver courant, "
        "guidage, silentblocs silicone, embout 1\" NPT, bois, garnissage, "
        "câbles, alim. externe). Ce n'est pas un devis fournisseur."
    ),
)

COUT_MATIERE_ENTREE_ESTIME = PrixIndicatif(
    minimum_eur=80.0,
    maximum_eur=150.0,
    origine="estimation_matiere",
    commentaire=(
        "ESTIMATION de coût matière (moteur 24 V + balourd, variateur, "
        "carter mousse, silentblocs caoutchouc, bois, garnissage, alim. "
        "externe). Ce n'est pas un devis fournisseur."
    ),
)


@dataclass(frozen=True)
class VarianteGamme:
    """Fiche regroupée d'une variante (haut ou entrée)."""

    gamme: str
    nom_affiche: str
    actionneur: object
    prix_vente: PrixIndicatif
    cout_matiere_estime: PrixIndicatif
    materiau_silentblocs: str
    driver: str
    guidage: str


VARIANTE_HAUT = VarianteGamme(
    gamme=GAMME_SYBIAN_HAUT,
    nom_affiche="Haut — voice coil SUPT VCAR",
    actionneur=VCAR_0105,
    prix_vente=PRIX_VENTE_HAUT,
    cout_matiere_estime=COUT_MATIERE_HAUT_ESTIME,
    materiau_silentblocs="silicone",
    driver="Driver à courant constant, rampe de démarrage, limitation de fréquence/courant, arrêt d'urgence.",
    guidage="Guidage à ressorts / flexures reprenant la charge statique de l'équipage mobile (pas le poids assis complet, voir docs).",
)

VARIANTE_ENTREE = VarianteGamme(
    gamme=GAMME_SYBIAN_ENTREE,
    nom_affiche="Entrée — moteur à balourd 24 V",
    actionneur=BALOURD_24V,
    prix_vente=PRIX_VENTE_ENTREE,
    cout_matiere_estime=COUT_MATIERE_ENTREE_ESTIME,
    materiau_silentblocs="caoutchouc",
    driver="Variateur 24 V, rampe de démarrage, limitation de vitesse, arrêt d'urgence (mêmes exigences de sécurité que le haut).",
    guidage="Carter fermé en mousse dense autour des pièces tournantes ; pas de course linéaire guidée.",
)

VARIANTES: dict[str, VarianteGamme] = {
    GAMME_SYBIAN_HAUT: VARIANTE_HAUT,
    GAMME_SYBIAN_ENTREE: VARIANTE_ENTREE,
}


def variante_par_gamme(gamme: str) -> VarianteGamme:
    try:
        return VARIANTES[gamme]
    except KeyError as exc:
        raise KeyError(
            f"Gamme inconnue « {gamme} ». Attendue : {', '.join(sorted(VARIANTES))}."
        ) from exc


# --- Étage piston (gamme haut, 3 modules) ------------------------------------
# Retenu : second voice coil longue course de la même famille SUPT, 24 V
# compatible via driver à courant, beaucoup plus silencieux et plus compact
# qu'un vérin à vis (Actuonix P16 : 12 V, 62 dB, encombrement trop long).

PISTON_VCAR_0110 = VoiceCoil(
    nom="vcar_0110_0380",
    modele="VCAR0110-0380-00A",
    fabricant="SUPT MOTION / Suzhou Unite Precision Technology",
    force_crete_n=110.0,
    force_continue_25c_n=37.4,
    course_totale_mm=38.0,
    tension_nominale_v=23.2,
    constante_fem_v_s_par_m=9.0,
    masse_mobile_kg=0.150,
    diametre_stator_mm=60.4,
    longueur_mm=60.4,
    frequence_min_hz=1.0,
    frequence_max_hz=8.0,
    source=(
        "Catalogues publics SUPT MOTION : "
        "http://www.supt-motor.com/products/yzxyqd.html "
        "(force crête 110 N, force continue 37,4 N à 25 °C, course 38 mm, "
        "tension 23,2 V, FEM 9 V/m/s, masse mobile 150 g, stator Ø 60,4 mm, "
        "longueur 60,4 mm)."
    ),
    ecarts_catalogues=(
        "La course 38 mm et la tension 23,2 V sont celles de la fiche "
        "supt-motor.com (modèle VCAR0110-0380-00A). Idéalement proche de "
        "24 V DC. Plage 1–8 Hz : hypothèse de pilotage « piston », pas une "
        "spec constructeur."
    ),
    hypotheses=(
        "La force continue (37,4 N) ne porte pas un usager. Comme pour le "
        "voice coil de vibration, le poids assis doit reposer sur la couronne "
        "structurelle du pouf. Le piston anime la selle / le chariot, pas le "
        "corps entier. Course utile typique retenue : 25–30 mm (marge de butée)."
    ),
)


@dataclass(frozen=True)
class MoteurLineaireAlternatif:
    """Vérin à vis documenté comme alternative (non retenue par défaut)."""

    nom: str
    modele: str
    fabricant: str
    course_mm: float
    force_max_n: float
    vitesse_max_mm_s: float
    tension_v: float
    masse_kg: float
    longueur_ferme_mm: float
    niveau_bruit_db_constructeur: float
    prix_indicatif_eur: float
    source: str
    pourquoi_non_retenu: str


P16_ALTERNATIVE = MoteurLineaireAlternatif(
    nom="actuonix_p16_50_22",
    modele="P16-50-22-12-P",
    fabricant="Actuonix Motion Devices",
    course_mm=50.0,
    force_max_n=50.0,  # 22:1 ; 64:1 → 90 N / 18 mm/s ; 256:1 → 300 N / 4,8 mm/s
    vitesse_max_mm_s=46.0,
    tension_v=12.0,
    masse_kg=0.11,
    longueur_ferme_mm=97.0,  # ordre de grandeur (trou à trou, course 50 mm)
    niveau_bruit_db_constructeur=62.0,
    prix_indicatif_eur=90.0 * 0.92,  # USD 90, conversion indicative
    source=(
        "https://www.actuonix.com/p16 et fiche "
        "https://www.actuonix.com/assets/images/datasheets/ActuonixP16Datasheet.pdf "
        "; tableau comparatif 2025 "
        "https://www.actuonix.com/assets/images/ACX_Product_Table_MASTER_2025_OUT_10-20%20(1).pdf "
        "(12 V, jusqu'à 46 mm/s et 300 N selon le rapport, 62 dB, IP54, 20 % "
        "de facteur de marche). Prix unitaire 90 USD (P16-P) / 80 USD (P16-S) "
        "sur actuonix.com, consulté novembre 2026 — ESTIMATION / prix public."
    ),
    pourquoi_non_retenu=(
        "12 V (il faudrait un convertisseur depuis le 24 V du meuble), "
        "niveau constructeur 62 dB supérieur à l'objectif 50 dB(A) à 1 m, "
        "facteur de marche 20 %, encombrement longitudinal trop grand pour "
        "un pouf de 430 mm si on l'empile, bruit d'engrenages. Conservé au "
        "catalogue uniquement comme alternative bas coût, non recommandée."
    ),
)


@dataclass(frozen=True)
class MoteurRotation:
    """Brushless plat + réducteur pour l'étage de rotation sous selle."""

    nom: str
    moteur_modele: str
    fabricant: str
    tension_v: float
    puissance_w: float
    couple_moteur_continu_nm: float
    regime_nominal_tr_min: float
    masse_moteur_kg: float
    diametre_mm: float
    reducteur_rapport: float
    couple_sortie_continu_nm: float
    regime_sortie_max_tr_min: float
    rendement_reducteur: float
    prix_moteur_eur: float
    prix_reducteur_estime_eur: float
    charge_axiale_moteur_n: float
    source: str
    hypotheses: str


ROTATION_EC45 = MoteurRotation(
    nom="maxon_ec45_flat_70w_gp",
    moteur_modele="EC 45 flat 70 W, réf. 411812",
    fabricant="maxon",
    tension_v=24.0,
    puissance_w=70.0,
    couple_moteur_continu_nm=0.128,
    regime_nominal_tr_min=4860.0,
    masse_moteur_kg=0.141,
    diametre_mm=45.0,
    reducteur_rapport=26.0,
    couple_sortie_continu_nm=0.128 * 26.0 * 0.70,
    regime_sortie_max_tr_min=4860.0 / 26.0,  # ≈ 187 tr/min
    rendement_reducteur=0.70,
    prix_moteur_eur=226.94,
    prix_reducteur_estime_eur=280.0,
    charge_axiale_moteur_n=3.8,
    source=(
        "Boutique maxon, EC 45 flat Ø45 mm, 70 W, 24 V, réf. 411812 : "
        "https://www.maxongroup.com/maxon/view/product/motor/ecmotor/ecflat/ecflat45/411812 "
        "(128 mNm continu, 3,21 A, 4860 tr/min, 226,94 € HT par 1–4 pièces, "
        "charge axiale dynamique max. 3,8 N, masse 141 g). Consulté novembre 2026."
    ),
    hypotheses=(
        "Le réducteur planétaire ~26:1 n'est pas figé sur une référence : "
        "couple de sortie ≈ 2,3 N·m et régime ≈ 190 tr/min sont des "
        "hypothèses (rendement 0,70). Prix réducteur ~280 € HT : ESTIMATION. "
        "La charge axiale admissible du moteur (3,8 N) est très inférieure "
        "au poids d'un usager : un roulement de butée séparé (type 51106 "
        "ou équivalent) est obligatoire. Un limiteur de couple (embrayage "
        "à rupture ou coupure driver) est obligatoire (pincement)."
    ),
)


# Budget électrique 24 V (estimations, à mesurer sur prototype)
# Dates : novembre 2026.

@dataclass(frozen=True)
class BudgetElectrique:
    nom: str
    courant_continu_a: float
    courant_crete_a: float
    puissance_continue_w: float
    puissance_crete_w: float
    commentaire: str


def budget_electrique_haut(modules_actifs: tuple[str, ...]) -> BudgetElectrique:
    """Somme des budgets 24 V par module actif (estimations)."""
    table = {
        "vibration": BudgetElectrique("vibration", 2.0, 6.0, 48.0, 140.0, "Driver courant, VCAR0105, régime typique."),
        "piston": BudgetElectrique("piston", 1.5, 5.0, 36.0, 120.0, "Driver courant, VCAR0110, 1–8 Hz."),
        "rotation": BudgetElectrique("rotation", 2.0, 8.0, 48.0, 190.0, "BLDC 70 W + démarrage, courant de blocage à limiter."),
    }
    cc = cr = pc = pp = 0.0
    for nom in modules_actifs:
        b = table[nom]
        cc += b.courant_continu_a
        cr += b.courant_crete_a
        pc += b.puissance_continue_w
        pp += b.puissance_crete_w
    # Alim. recommandée : marge 1,3 sur la crête, arrondie.
    return BudgetElectrique(
        nom="+".join(modules_actifs) or "aucun",
        courant_continu_a=cc,
        courant_crete_a=cr,
        puissance_continue_w=pc,
        puissance_crete_w=pp,
        commentaire=(
            f"Alimentation 24 V certifiée hors meuble, dimensionnée ≥ "
            f"{cr * 1.3:.0f} A / {pp * 1.3:.0f} W de crête (marge 30 %). "
            "Les courants sont des ESTIMATIONS (novembre 2026), à mesurer."
        ),
    )
