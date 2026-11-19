# -*- coding: utf-8 -*-
"""Catalogue électronique du pouf vibrant : ESP32, présence, AU, ADC.

Toutes les tensions dans le meuble restent en 24 V DC. L'alimentation
secteur certifiée est hors meuble. Les prix sont des ESTIMATIONS
datées de novembre 2026, à reprendre sur devis.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PrixEstime:
    minimum_eur: float
    maximum_eur: float
    date: str
    origine: str
    commentaire: str = ""


@dataclass(frozen=True)
class ModuleEsp32:
    nom: str
    nom_affiche: str
    famille: str
    ble: str
    wifi: str
    tension_logique_v: float
    encombrement_module_mm: tuple[float, float, float]
    encombrement_boitier_mm: tuple[float, float, float]
    flash_mo: float
    prix: PrixEstime
    source: str
    commentaire: str


@dataclass(frozen=True)
class ConvertisseurPont:
    nom: str
    nom_affiche: str
    bits: int
    frequence_echantillonnage_hz: tuple[float, ...]
    pga: bool
    filtre_anti_repli_interne: bool
    recommande: bool
    prix: PrixEstime
    commentaire: str


@dataclass(frozen=True)
class CelluleCharge:
    nom: str
    nom_affiche: str
    technologie: str
    capacite_kg: float
    pont: str
    sensibilite_mv_per_v: float
    encombrement_mm: tuple[float, float, float]
    prix_unitaire: PrixEstime
    commentaire: str


@dataclass(frozen=True)
class OrganeSecurite:
    nom: str
    nom_affiche: str
    role: str
    independant_esp32: bool
    prix: PrixEstime
    commentaire: str


ESP32_S3_WROOM1 = ModuleEsp32(
    nom="esp32_s3_wroom1",
    nom_affiche="ESP32-S3-WROOM-1 (Espressif) sur carte porteur",
    famille="ESP32-S3",
    ble="BLE 5.0, LE Secure Connections, bonding",
    wifi="Wi-Fi 802.11 b/g/n, WPA2/WPA3",
    tension_logique_v=3.3,
    encombrement_module_mm=(25.5, 18.0, 3.5),
    # Boîtier IP67 : module + ADC + alim 24→5 V + relais de sécurité + borniers
    encombrement_boitier_mm=(120.0, 80.0, 45.0),
    flash_mo=8.0,
    prix=PrixEstime(8.0, 18.0, "novembre 2026", "estimation_matiere",
                    "Module officiel ~4–8 €, carte porteur complète 8–18 €."),
    source="Fiches Espressif ESP32-S3-WROOM-1 ; boutiques modules, nov. 2026.",
    commentaire=(
        "Remplace la télécommande et la pédale. L'ESP32 reste alimenté "
        "quand le relais de sécurité coupe la puissance des drivers, afin "
        "de signaler l'état DEFAUT. Il ne fait PAS partie de la chaîne "
        "d'arrêt d'urgence."
    ),
)

ADS1220 = ConvertisseurPont(
    nom="ads1220",
    nom_affiche="ADS1220 (24 bits, PGA, jusqu'à 2 kSPS)",
    bits=24,
    frequence_echantillonnage_hz=(20.0, 90.0, 330.0, 600.0, 1000.0, 2000.0),
    pga=True,
    filtre_anti_repli_interne=True,
    recommande=True,
    prix=PrixEstime(8.0, 16.0, "novembre 2026", "estimation_matiere"),
    commentaire=(
        "Recommandé : échantillonnage ≥ 500 SPS, filtre anti-repli analogique "
        "en amont, puis passe-bas logiciel fc ≤ f_exc_min/10. Nyquist largement "
        "au-dessus de la bande 8–60 Hz, aliasing maîtrisable."
    ),
)

HX711 = ConvertisseurPont(
    nom="hx711",
    nom_affiche="HX711 (24 bits, 10 ou 80 SPS)",
    bits=24,
    frequence_echantillonnage_hz=(10.0, 80.0),
    pga=True,
    filtre_anti_repli_interne=False,
    recommande=False,
    prix=PrixEstime(1.5, 4.0, "novembre 2026", "estimation_matiere"),
    commentaire=(
        "Acceptable seulement avec un filtre anti-repli analogique strict "
        "devant l'ADC. À 80 SPS, Nyquist = 40 Hz : une vibration 8–40 Hz "
        "se replie dans la bande utile si l'anti-repli est absent. Pas le défaut."
    ),
)

CELLULE_50KG = CelluleCharge(
    nom="cellule_50kg_pont",
    nom_affiche="Cellule 50 kg, pont de Wheatstone (type TAL221 / équivalent)",
    technologie="jauge de contrainte, pont de Wheatstone complet",
    capacite_kg=50.0,
    pont="Wheatstone",
    sensibilite_mv_per_v=1.0,
    encombrement_mm=(55.0, 12.7, 12.7),
    prix_unitaire=PrixEstime(6.0, 15.0, "novembre 2026", "estimation_matiere"),
    commentaire=(
        "Quatre cellules sous la couronne, autour de la selle (zone centrale). "
        "Butée de surcharge à ~1,2–1,5 × la capacité, jeu ~0,3–0,5 mm après "
        "fléchissement nominal, pour protéger la cellule d'un appui brutal."
    ),
)

NOTE_FSR_ECARTE = (
    "Les capteurs FSR (résistances sensibles à la force) sont écartés pour "
    "la présence de sécurité : forte hystérésis, dérive à la chaleur et à "
    "l'humidité, mauvaise répétabilité à long terme, pas de diagnostic de "
    "pont (circuit ouvert / court-circuit), et une caractéristique force–résistance "
    "non linéaire peu fiable au seuil. Un pont de Wheatstone à jauges offre "
    "une mesure de force, un diagnostic de défaut capteur, et une tare. "
    "Ce n'est pas une redondance de catégorie ISO 13849 à lui seul : la "
    "coupure de puissance reste l'AU câblé, indépendant de l'ESP32."
)

AU_BOUTON = OrganeSecurite(
    nom="au_bouton_nf",
    nom_affiche="Bouton d'arrêt d'urgence, contact NF, Ø 22 mm, à accrochage",
    role="au_commande",
    independant_esp32=True,
    prix=PrixEstime(20.0, 45.0, "novembre 2026", "estimation_matiere",
                    "Type Schneider XB5-AS ou équivalent, tête protégée."),
    commentaire=(
        "Placement retenu : sous le chant avant de la couronne, côté droit "
        "(environ x = largeur − 90 mm, y ≈ 12 mm, sous la lèvre de 18 mm). "
        "Accessible assis : la main posée sur le chant avant, les doigts "
        "s'enroulent naturellement sous la lèvre, portée ~250 mm depuis "
        "l'axe. Discret : invisible sur la façade velours, seulement en "
        "passant la main sous le chant (ISO 13850 : identifiable au toucher, "
        "pas nécessairement exhibé en façade salon). La télécommande / "
        "pédale ne remplace pas cet organe."
    ),
)

RELAIS_SECURITE = OrganeSecurite(
    nom="relais_securite",
    nom_affiche="Relais de sécurité à contacts guidés, réarmement manuel",
    role="au_coupure_puissance",
    independant_esp32=True,
    prix=PrixEstime(80.0, 180.0, "novembre 2026", "estimation_matiere",
                    "Type relais à contacts guidés 24 V (Omron G7SA, Phoenix PSR ou équivalent)."),
    commentaire=(
        "La boucle AU (contact NF) alimente le relais. Les contacts de "
        "puissance coupent le 24 V des drivers des trois modules (vibration, "
        "piston, rotation). Le réarmement est manuel (sur le relais, dans le "
        "boîtier électronique) et n'autorise le redémarrage que depuis "
        "l'état ARRET : il ne relance pas le mouvement (ISO 13850). "
        "L'ESP32 n'est pas dans cette chaîne."
    ),
)

PRESENCE_ENABLE = OrganeSecurite(
    nom="presence_enable_materiel",
    nom_affiche="Enable matériel des drivers, commandé par la présence",
    role="presence_enable",
    independant_esp32=False,
    prix=PrixEstime(10.0, 25.0, "novembre 2026", "estimation_matiere",
                    "Comparateur + temporisation analogique + MOSFET / relais d'enable."),
    commentaire=(
        "La présence agit aussi sur l'enable matériel des drivers, en ET "
        "logique (câblé) avec les contacts du relais de sécurité. Chemin "
        "matériel : filtre analogique + comparateur à hystérésis + "
        "temporisation de levée 200–300 ms, sans passer par le firmware. "
        "L'ESP32 lit le même signal pour sa machine d'états, mais un plantage "
        "logiciel ne doit pas maintenir l'enable. Un chien de garde matériel "
        "externe (impulsion périodique) coupe l'enable si le firmware se fige."
    ),
)

ACCELEROMETRE_REF = OrganeSecurite(
    nom="accelerometre_reference",
    nom_affiche="Accéléromètre de référence sur le cadre (soustraction)",
    role="reference_vibration",
    independant_esp32=False,
    prix=PrixEstime(3.0, 15.0, "novembre 2026", "estimation_matiere"),
    commentaire=(
        "Zone de référence : accéléromètre (ou cellule hors de l'appui "
        "utilisateur) fixé au cadre / à la couronne, soustrait de la zone "
        "centrale pour rejeter le mode commun vibratoire."
    ),
)


@dataclass(frozen=True)
class LigneBudget:
    poste: str
    minimum_eur: float
    maximum_eur: float
    date: str
    origine: str
    commentaire: str


def budget_electronique_securite() -> tuple[LigneBudget, ...]:
    """ESP32, ADC, cellules, AU, relais — hors panneaux acoustiques."""
    return (
        LigneBudget("esp32_s3", 8, 18, "novembre 2026", "estimation_matiere", ESP32_S3_WROOM1.prix.commentaire),
        LigneBudget("ads1220", 8, 16, "novembre 2026", "estimation_matiere", "Convertisseur pont recommandé."),
        LigneBudget("cellules_4x50kg", 24, 60, "novembre 2026", "estimation_matiere", "4 cellules Wheatstone."),
        LigneBudget("accelerometre_ref", 3, 15, "novembre 2026", "estimation_matiere", "Référence de soustraction."),
        LigneBudget("au_bouton_nf", 20, 45, "novembre 2026", "estimation_matiere", AU_BOUTON.prix.commentaire),
        LigneBudget("relais_securite", 80, 180, "novembre 2026", "estimation_matiere", RELAIS_SECURITE.prix.commentaire),
        LigneBudget("enable_materiel_presence", 10, 25, "novembre 2026", "estimation_matiere", "Comparateur + temporisation."),
        LigneBudget("chien_garde_materiel", 5, 15, "novembre 2026", "estimation_matiere", "Watchdog externe, impulsion."),
        LigneBudget("boitier_ip67_presses_etoupes", 20, 45, "novembre 2026", "estimation_matiere", "Boîtier + évent ePTFE + glands."),
    )


def total_lignes(lignes: tuple[LigneBudget, ...]) -> tuple[float, float]:
    return (sum(l.minimum_eur for l in lignes), sum(l.maximum_eur for l in lignes))


# Masse typique de PETG à 40 % pour les panneaux (voir regles / impression).
PRIX_FILAMENT_PETG_EUR_PAR_KG = PrixEstime(18.0, 30.0, "novembre 2026", "estimation_matiere",
                                          "Filament PETG technique, nov. 2026.")


def budget_panneaux_acoustiques(
    masse_kg: float = 3.1,
) -> LigneBudget:
    """Filament PETG 40 % pour parois intérieures + capots (ESTIMATION nov. 2026).

    Masse typique ~3,1 kg (4 parois 12 mm, hauteur ~250 mm, 2 capots),
    hors fond (laissé libre pour la ventilation).
    """
    p = PRIX_FILAMENT_PETG_EUR_PAR_KG
    return LigneBudget(
        "panneaux_acoustiques_petg",
        round(masse_kg * p.minimum_eur + 5.0, 0),
        round(masse_kg * p.maximum_eur + 15.0, 0),
        "novembre 2026",
        "estimation_matiere",
        (
            f"~{masse_kg:.1f} kg de PETG à 40 % ({p.minimum_eur:.0f}–"
            f"{p.maximum_eur:.0f} €/kg) plus inserts. Impact sur la fourchette "
            "matière 900–1 500 € : +61 à +108 €, soit 5–9 % du milieu de "
            "fourchette (1 200 €) — marginal, le même ordre de grandeur est "
            "conservé (environ 960–1 610 € si on l'ajoute au bout à bout)."
        ),
    )


def budget_complet_ajouts() -> tuple[tuple[LigneBudget, ...], tuple[float, float]]:
    """Électronique / sécurité + panneaux, totaux min/max."""
    lignes = budget_electronique_securite() + (budget_panneaux_acoustiques(),)
    return lignes, total_lignes(lignes)
