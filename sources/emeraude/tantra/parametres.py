# -*- coding: utf-8 -*-
"""Paramètres globaux de la gamme Tantra & Bien-être (couche 1).

Module Python pur, sans dépendance à ``adsk``, testable hors Fusion 360.
Mêmes conventions qu'Incognito :

* toutes les cotes en millimètres, forces en N, contraintes en MPa
  (= N/mm²), masses volumiques en kg/m³, angles en degrés ;
* dataclasses figées (``frozen=True``) : on instancie une variante avec
  ``dataclasses.replace`` plutôt que de muter un défaut ;
* les valeurs mécaniques sont des **hypothèses de conception
  documentées**, pas un justificatif Eurocode 5 ni une certification.

Ce module porte le vocabulaire partagé par les trois volets :

1. typologies et cotes (plages admissibles) ;
2. anthropométrie 5e–95e centile (sources citées) ;
3. essences et matériaux bois (massif, lamellé-collé, contreplaqué cintré) ;
4. revêtements (cuir, simili lavable, tissu technique déperlant, tissus
   « salon » pour le volet camouflable) ;
5. charges de service et coefficient de sécurité ;
6. export vers les paramètres utilisateur Fusion (préfixe ``tan_``).

Tout ancrage destiné à retenir une personne exige le visa d'un
ingénieur et un essai de charge réel.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping

# ---------------------------------------------------------------------------
# Unités
# ---------------------------------------------------------------------------

UNITE_LONGUEUR = "mm"
UNITE_FORCE = "N"
UNITE_PRESSION = "MPa"
UNITE_MASSE_VOLUMIQUE = "kg/m^3"
UNITE_MASSE = "kg"
UNITE_ANGLE = "deg"

PREFIXE_FUSION = "tan_"
"""Préfixe des paramètres utilisateur Fusion de la gamme (évite les collisions
avec ``inc_`` d'Incognito si les deux gammes cohabitent dans un document)."""

G = 9.81
"""Accélération de la pesanteur (m/s²)."""

# ---------------------------------------------------------------------------
# Niveaux de signalement (identiques à Incognito)
# ---------------------------------------------------------------------------

NIVEAU_OK = "ok"
NIVEAU_AVERTISSEMENT = "avertissement"
NIVEAU_ESSAI_REQUIS = "essai_requis"
NIVEAU_NON_CONFORME = "non_conforme"
ORDRE_NIVEAUX = (NIVEAU_OK, NIVEAU_AVERTISSEMENT, NIVEAU_ESSAI_REQUIS, NIVEAU_NON_CONFORME)

# Volets de la gamme
VOLET_TANTRA = "tantra"
VOLET_CAMOUFLABLE = "camouflable"
VOLET_CADRE = "cadre"
VOLETS = (VOLET_TANTRA, VOLET_CAMOUFLABLE, VOLET_CADRE)


# ---------------------------------------------------------------------------
# Cotes et plages
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Plage:
    """Intervalle fermé [minimum, maximum]."""

    minimum: float
    maximum: float
    unite: str = UNITE_LONGUEUR

    def __post_init__(self) -> None:
        if self.maximum < self.minimum:
            raise ValueError(
                f"Plage invalide : maximum ({self.maximum}) < minimum ({self.minimum})."
            )

    def contient(self, valeur: float) -> bool:
        """True si ``valeur`` est dans l'intervalle fermé."""
        return self.minimum <= valeur <= self.maximum

    def borner(self, valeur: float) -> float:
        """Ramène ``valeur`` dans la plage."""
        return min(self.maximum, max(self.minimum, valeur))


@dataclass(frozen=True)
class Cote:
    """Cote typologique : valeur par défaut, plage admissible, commentaire."""

    nom: str
    valeur: float
    plage: Plage
    commentaire: str
    unite: str = UNITE_LONGUEUR

    def __post_init__(self) -> None:
        if not self.plage.contient(self.valeur):
            raise ValueError(
                f"Cote « {self.nom} » : valeur {self.valeur} {self.unite} hors plage "
                f"[{self.plage.minimum}, {self.plage.maximum}]."
            )


@dataclass(frozen=True)
class TypologieMeuble:
    """Typologie : identifiant ASCII, volet, description, cotes de référence."""

    nom: str
    volet: str
    nom_affiche: str
    description: str
    cotes: tuple[Cote, ...]

    def __post_init__(self) -> None:
        if self.volet not in VOLETS:
            raise ValueError(f"Volet inconnu « {self.volet} » pour {self.nom}.")

    def cote(self, nom: str) -> Cote:
        for c in self.cotes:
            if c.nom == nom:
                return c
        raise KeyError(f"Cote inconnue « {nom} » pour la typologie {self.nom}.")

    def valeurs(self) -> dict[str, float]:
        return {c.nom: c.valeur for c in self.cotes}

    def verifier(self, nom: str, valeur: float) -> None:
        """Lève ``ValueError`` si ``valeur`` sort de la plage de la cote ``nom``."""
        c = self.cote(nom)
        if not c.plage.contient(valeur):
            raise ValueError(
                f"{self.nom}.{nom} = {valeur:g} {c.unite} hors plage "
                f"[{c.plage.minimum:g}, {c.plage.maximum:g}]."
            )


def _c(nom: str, valeur: float, mini: float, maxi: float, commentaire: str,
       unite: str = UNITE_LONGUEUR) -> Cote:
    return Cote(nom, valeur, Plage(mini, maxi, unite), commentaire, unite)


# ---------------------------------------------------------------------------
# Anthropométrie (5e centile femme — 95e centile homme)
# ---------------------------------------------------------------------------

SOURCE_ANTHROPOMETRIE = (
    "Pheasant S. & Haslegrave C. M., « Bodyspace — Anthropometry, Ergonomics and "
    "the Design of Work », 3e éd., CRC Press, 2006 : tableau des adultes "
    "britanniques 19–65 ans (valeurs reprises par les tableaux de conception "
    "courants : designingforpeople.org.uk « Case study: seating » ; City University "
    "of Hong Kong, « Online anthropometry », ch. 2 ; Metric Handbook, « People and "
    "space »). Contrôle croisé conseillé sur DINED (TU Delft, adultes néerlandais "
    "2004, https://dined.nl), population plus grande : les 95e centiles hommes y "
    "sont supérieurs d'environ 3 à 5 %."
)


@dataclass(frozen=True)
class Mesure:
    """Mesure anthropométrique : borne basse (P5) et haute (P95) de conception.

    ``p5`` est le 5e centile le plus petit des deux sexes, ``p95`` le 95e
    centile le plus grand des deux sexes (pour la largeur des hanches assis,
    c'est le 95e centile **femme** qui est le plus grand).
    """

    nom: str
    p5: float
    p50: float
    p95: float
    commentaire: str

    def __post_init__(self) -> None:
        if not (0 < self.p5 <= self.p50 <= self.p95):
            raise ValueError(f"Mesure {self.nom} : il faut 0 < P5 ≤ P50 ≤ P95.")


@dataclass(frozen=True)
class Anthropometrie:
    """Jeu de mesures de conception (mm). P50 = moyenne mixte approximative."""

    stature: Mesure = Mesure("stature", 1505.0, 1675.0, 1855.0,
                             "P5 femme 1505, P95 homme 1855.")
    hauteur_poplitee: Mesure = Mesure("hauteur_poplitee", 355.0, 420.0, 490.0,
                                      "Sol → creux poplité, assis, pieds nus.")
    longueur_fesse_poplite: Mesure = Mesure("longueur_fesse_poplite", 435.0, 488.0, 550.0,
                                            "Profondeur d'assise maximale (P5) sans compression du creux poplité.")
    longueur_fesse_genou: Mesure = Mesure("longueur_fesse_genou", 520.0, 583.0, 645.0,
                                          "Dégagement des genoux.")
    largeur_hanches_assis: Mesure = Mesure("largeur_hanches_assis", 310.0, 368.0, 435.0,
                                           "P95 = femme (435 mm).")
    hauteur_assis: Mesure = Mesure("hauteur_assis", 795.0, 880.0, 965.0,
                                   "Assise → sommet du crâne.")
    hauteur_epaules_assis: Mesure = Mesure("hauteur_epaules_assis", 505.0, 575.0, 645.0,
                                           "Assise → acromion.")
    hauteur_genou: Mesure = Mesure("hauteur_genou", 455.0, 522.0, 595.0,
                                   "Sol → dessus du genou, assis.")
    hauteur_coude_assis: Mesure = Mesure("hauteur_coude_assis", 185.0, 235.0, 295.0,
                                         "Assise → dessous du coude.")
    source: str = SOURCE_ANTHROPOMETRIE

    # Recommandations ergonomiques dérivées (ordres de grandeur, même source)
    appui_lombaire_min_mm: float = 150.0
    """Centre de l'appui lombaire au-dessus de l'assise comprimée : borne basse."""
    appui_lombaire_max_mm: float = 250.0
    """Centre de l'appui lombaire au-dessus de l'assise comprimée : borne haute."""

    def mesures(self) -> tuple[Mesure, ...]:
        return (
            self.stature, self.hauteur_poplitee, self.longueur_fesse_poplite,
            self.longueur_fesse_genou, self.largeur_hanches_assis, self.hauteur_assis,
            self.hauteur_epaules_assis, self.hauteur_genou, self.hauteur_coude_assis,
        )


ANTHROPOMETRIE_DEFAUT = Anthropometrie()


# ---------------------------------------------------------------------------
# Essences et matériaux bois
# ---------------------------------------------------------------------------

FAMILLE_MASSIF = "massif"
FAMILLE_LAMELLE_COLLE = "lamelle_colle"
FAMILLE_CONTREPLAQUE = "contreplaque"

_SOURCE_BOIS = (
    "Ordres de grandeur : USDA FPL Wood Handbook (FPL-GTR-282) pour ρ et E moyens ; "
    "NF EN 338 (classes D30–D40) pour fm,k, fv,k et ρk des feuillus massifs ; "
    "Pollmeier, fiche technique BauBuche GL75 (lamellé-collé de hêtre) ; "
    "manuels de contreplaqué de bouleau (UPM / Koskisen) pour le bouleau."
)
_HYPOTHESES_BOIS = (
    "Valeurs caractéristiques (5e centile) d'ordre de grandeur. Les vérifications "
    "de ce package comparent CS × contrainte de service à fm,k / fv,k : elles "
    "n'incluent ni k_mod, ni γ_M, ni l'humidité, les nœuds ou le fil dévié. "
    "Un ingénieur doit reprendre le calcul (Eurocode 5) ; essai réel obligatoire."
)


@dataclass(frozen=True)
class Essence:
    """Essence ou matériau bois, propriétés mécaniques caractéristiques."""

    nom: str
    nom_affiche: str
    famille: str
    masse_volumique_kg_m3: float
    masse_volumique_caracteristique_kg_m3: float
    module_elasticite_mpa: float
    fm_k_mpa: float
    fv_k_mpa: float
    commentaire: str
    source: str = _SOURCE_BOIS
    hypotheses: str = _HYPOTHESES_BOIS

    def __post_init__(self) -> None:
        for champ in ("masse_volumique_kg_m3", "masse_volumique_caracteristique_kg_m3",
                      "module_elasticite_mpa", "fm_k_mpa", "fv_k_mpa"):
            if getattr(self, champ) <= 0:
                raise ValueError(f"Essence {self.nom} : {champ} doit être > 0.")
        if self.famille not in (FAMILLE_MASSIF, FAMILLE_LAMELLE_COLLE, FAMILLE_CONTREPLAQUE):
            raise ValueError(f"Essence {self.nom} : famille inconnue {self.famille}.")


CHENE = Essence("chene", "Chêne massif", FAMILLE_MASSIF, 710.0, 550.0, 12500.0, 40.0, 4.0,
                "Référence structurelle (pieds, traverses, blocs d'ancrage). Tanins : "
                "éviter l'acier non inox au contact (taches noires).")
HETRE = Essence("hetre", "Hêtre massif", FAMILLE_MASSIF, 720.0, 550.0, 14000.0, 40.0, 4.0,
                "Excellent pour tourillons, pieds tournés, traverses ; sensible à "
                "l'humidité (stabilité dimensionnelle moyenne).")
FRENE = Essence("frene", "Frêne massif", FAMILLE_MASSIF, 690.0, 550.0, 13000.0, 40.0, 4.0,
                "Très bonne résilience aux chocs, se cintre à la vapeur : idéal pour "
                "les pièces courbes en massif.")
NOYER = Essence("noyer", "Noyer massif", FAMILLE_MASSIF, 650.0, 520.0, 11600.0, 35.0, 3.4,
                "Essence de prestige, moins résistante : à réserver aux pièces vues "
                "peu chargées ou à surdimensionner.")
LAMELLE_HETRE = Essence("lamelle_hetre", "Lamellé-collé de hêtre (type BauBuche GL75)",
                        FAMILLE_LAMELLE_COLLE, 800.0, 730.0, 16800.0, 75.0, 4.5,
                        "Lamibois de hêtre très résistant : poutres et longerons fins, "
                        "flasques droites. Aspect « chant lamellé » assumé ou plaqué.")
CONTREPLAQUE_BOULEAU = Essence("contreplaque_bouleau", "Contreplaqué de bouleau cintré",
                               FAMILLE_CONTREPLAQUE, 680.0, 630.0, 9000.0, 35.0, 3.0,
                               "Plis de bouleau 1,5 mm collés sous presse sur moule : "
                               "coques et flasques courbes. Rayon mini lié à l'épaisseur "
                               "de pli (voir regles.rayon_cintrage_minimal_mm).")

ESSENCES: dict[str, Essence] = {
    e.nom: e for e in (CHENE, HETRE, FRENE, NOYER, LAMELLE_HETRE, CONTREPLAQUE_BOULEAU)
}


def essence_par_nom(nom: str) -> Essence:
    """Retourne une essence par identifiant ASCII."""
    try:
        return ESSENCES[nom]
    except KeyError as exc:
        raise KeyError(f"Essence inconnue « {nom} ». Connues : {', '.join(sorted(ESSENCES))}.") from exc


# ---------------------------------------------------------------------------
# Revêtements
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Revetement:
    """Revêtement d'assise ou de façade.

    ``aspect_salon`` : True si le revêtement passe pour un meuble de salon
    ordinaire (condition du volet camouflable). ``lavable`` : nettoyage à
    l'eau savonneuse / désinfectant doux sans dommage (condition du volet
    Tantra, usage avec fluides corporels et lubrifiants).
    """

    nom: str
    nom_affiche: str
    famille: str
    epaisseur_mm: float
    lavable: bool
    deperlant: bool
    aspect_salon: bool
    prix_indicatif_eur_m2: float
    entretien: str
    commentaire: str

    def __post_init__(self) -> None:
        if self.epaisseur_mm <= 0 or self.prix_indicatif_eur_m2 <= 0:
            raise ValueError(f"Revêtement {self.nom} : épaisseur et prix doivent être > 0.")


CUIR_COGNAC = Revetement(
    "cuir_cognac", "Cuir pleine fleur pigmenté cognac", "cuir", 1.3, True, True, True, 95.0,
    "Eau savonneuse (pH neutre), nourrir 2×/an. Proscrire alcool et lubrifiants huileux "
    "non essuyés (auréoles).",
    "Cuir pigmenté (finition protectrice) et non aniline : seul le pigmenté résiste "
    "durablement aux fluides. Accepte un capitonnage.",
)
CUIR_NOIR = Revetement(
    "cuir_noir", "Cuir pleine fleur pigmenté noir", "cuir", 1.3, True, True, True, 90.0,
    "Idem cuir cognac.", "Masque mieux les marques que le cognac.",
)
SIMILI_PU_MEDICAL = Revetement(
    "simili_pu_medical", "Simili-cuir PU qualité médicale", "simili", 1.0, True, True, False, 38.0,
    "Désinfectant sans alcool, eau savonneuse. Résiste aux lubrifiants eau et silicone.",
    "Type revêtement de table de massage (traité antibactérien, classement feu "
    "EN 1021-1/-2 à exiger). Aspect « technique » : réservé au volet Tantra.",
)
SIMILI_VINYLE_MARINE = Revetement(
    "simili_vinyle_marine", "Vinyle marine grainé", "simili", 1.1, True, True, False, 30.0,
    "Eau savonneuse, désinfectant. Très robuste.",
    "Le plus résistant aux fluides et aux UV ; toucher moins noble. Entrée de gamme Tantra.",
)
TISSU_TECHNIQUE_DEPERLANT = Revetement(
    "tissu_technique_deperlant", "Tissu technique déperlant (type Crypton / Aquaclean)",
    "tissu", 1.2, True, True, True, 55.0,
    "Eau + savon doux ; déhoussable de préférence (lavage 30 °C).",
    "Barrière anti-humidité intégrée : l'aspect d'un tissu d'ameublement avec la "
    "lavabilité d'un simili. Double usage Tantra / camouflable.",
)
VELOURS_DEPERLANT = Revetement(
    "velours_deperlant", "Velours ras déperlant", "tissu", 1.4, True, True, True, 48.0,
    "Brossage, eau savonneuse sur taches fraîches.",
    "Façade « salon classique » du volet camouflable.",
)
BOUCLETTE = Revetement(
    "bouclette", "Laine bouclée (bouclette)", "tissu", 2.5, False, False, True, 62.0,
    "Aspiration, nettoyage à sec.",
    "Très tendance salon ; non lavable : à ne jamais mettre en zone de contact intime.",
)

REVETEMENTS: dict[str, Revetement] = {
    r.nom: r for r in (CUIR_COGNAC, CUIR_NOIR, SIMILI_PU_MEDICAL, SIMILI_VINYLE_MARINE,
                       TISSU_TECHNIQUE_DEPERLANT, VELOURS_DEPERLANT, BOUCLETTE)
}


def revetement_par_nom(nom: str) -> Revetement:
    try:
        return REVETEMENTS[nom]
    except KeyError as exc:
        raise KeyError(f"Revêtement inconnu « {nom} ». Connus : {', '.join(sorted(REVETEMENTS))}.") from exc


# ---------------------------------------------------------------------------
# Charges
# ---------------------------------------------------------------------------

COEFFICIENT_SECURITE_MIN = 3.0
"""Coefficient de sécurité minimal exigé par la gamme (brief : CS ≥ 3)."""


@dataclass(frozen=True)
class ParametresCharge:
    """Charges de service (hypothèses) et coefficient de sécurité.

    * ``charge_service_ancrage_n`` : 1500 N par ancrage (même hypothèse
      qu'Incognito, traction d'un bracelet tendu avec à-coup) ;
    * ``poids_personne_n`` : 1100 N ≈ 112 kg (au-delà du P95 homme, marge) ;
    * ``facteur_dynamique`` : 1,5 sur le poids (mouvements rythmés) ;
    * ``coefficient_securite`` : appliqué aux résistances caractéristiques.
    """

    charge_service_ancrage_n: float = 1500.0
    poids_personne_n: float = 1100.0
    facteur_dynamique: float = 1.5
    coefficient_securite: float = COEFFICIENT_SECURITE_MIN
    effort_horizontal_exterieur_n: float = 300.0
    """Poussée horizontale accidentelle d'une personne (appui, chute contre le
    meuble) utilisée pour la stabilité des états « posés ». Hypothèse."""

    def __post_init__(self) -> None:
        for champ in ("charge_service_ancrage_n", "poids_personne_n", "facteur_dynamique",
                      "coefficient_securite", "effort_horizontal_exterieur_n"):
            if getattr(self, champ) <= 0:
                raise ValueError(f"{champ} doit être > 0.")

    def charge_surface_service_n(self, nombre_personnes: int) -> float:
        """Charge verticale de service : n personnes × poids × facteur dynamique."""
        if nombre_personnes < 1:
            raise ValueError("nombre_personnes doit être ≥ 1.")
        return nombre_personnes * self.poids_personne_n * self.facteur_dynamique

    @property
    def charge_rupture_visee_ancrage_n(self) -> float:
        return self.charge_service_ancrage_n * self.coefficient_securite


CHARGES_DEFAUT = ParametresCharge()


# ---------------------------------------------------------------------------
# Typologies des trois volets
# ---------------------------------------------------------------------------

TANTRA_CHAISE_DOUBLE_COURBE = TypologieMeuble(
    "tantra_chaise_double_courbe", VOLET_TANTRA, "Chaise longue tantrique à double courbe",
    "Profil en S : petite bosse avant (cale fessière, ~470 mm), creux d'assise "
    "(~330 mm), grande courbe dorsale montant à ~760 mm. Flasques en contreplaqué "
    "de bouleau cintré, traverses en chêne à tenons et mortaises.",
    (
        _c("longueur", 1850.0, 1650.0, 2000.0, "Longueur hors-tout (repère : 1880 mm pour la Tantra Chair US)."),
        _c("largeur", 600.0, 520.0, 700.0, "Largeur de la surface de soutien."),
        _c("hauteur_petite_bosse", 470.0, 400.0, 560.0, "Sommet de la cale fessière avant (dessus mousse)."),
        _c("hauteur_creux", 330.0, 260.0, 400.0, "Point bas du creux d'assise (dessus mousse)."),
        _c("hauteur_grande_courbe", 760.0, 650.0, 850.0, "Sommet de la grande courbe dorsale (dessus mousse)."),
    ),
)
TANTRA_FAUTEUIL_LOMBAIRE = TypologieMeuble(
    "tantra_fauteuil_lombaire", VOLET_TANTRA, "Fauteuil bas à cale fessière et appui lombaire intégrés",
    "Fauteuil sans accoudoirs, assise basse inclinée vers l'arrière, cale fessière "
    "sculptée dans l'assise, bombé lombaire intégré au dossier. Assise large (deux "
    "personnes face à face, position assise enlacée).",
    (
        _c("largeur", 760.0, 650.0, 900.0, "Largeur hors-tout."),
        _c("hauteur_assise", 340.0, 300.0, 420.0, "Hauteur du point d'assise (dessus mousse, compressée ~20 mm)."),
        _c("profondeur_assise", 440.0, 420.0, 520.0, "Profondeur utile d'assise ≤ fesse-poplité P5 + marge."),
        _c("inclinaison_assise", 12.0, 5.0, 20.0, "Inclinaison arrière de l'assise.", UNITE_ANGLE),
        _c("angle_dossier", 108.0, 100.0, 120.0, "Angle assise / dossier.", UNITE_ANGLE),
        _c("hauteur_dossier", 820.0, 700.0, 950.0, "Sommet du dossier depuis le sol."),
    ),
)
TANTRA_BANQUETTE_DEUX_NIVEAUX = TypologieMeuble(
    "tantra_banquette_deux_niveaux", VOLET_TANTRA, "Banquette inclinée à deux niveaux",
    "Banquette profonde : niveau bas d'agenouillement / assise (~420 mm), contremarche "
    "arrondie, niveau haut incliné (~640 mm) servant d'appui ventral ou dorsal.",
    (
        _c("longueur", 1500.0, 1200.0, 1900.0, "Longueur (le long de la contremarche)."),
        _c("profondeur", 1050.0, 900.0, 1250.0, "Profondeur totale bas + haut."),
        _c("hauteur_niveau_bas", 420.0, 380.0, 480.0, "Dessus mousse du niveau bas."),
        _c("hauteur_niveau_haut", 640.0, 560.0, 720.0, "Dessus mousse du niveau haut, côté contremarche."),
        _c("inclinaison_niveau_haut", 12.0, 0.0, 20.0, "Pente du niveau haut (descend vers l'arrière).", UNITE_ANGLE),
    ),
)
TANTRA_SIEGE_REPOSE_GENOUX = TypologieMeuble(
    "tantra_siege_repose_genoux", VOLET_TANTRA, "Siège à assise inclinée avec repose-genoux",
    "Siège de type assis-genoux élargi : assise inclinée vers l'avant, deux "
    "repose-genoux rembourrés, piètement traîneau en frêne. Position chevauchée "
    "stable, bassin ouvert, dos libre.",
    (
        _c("largeur", 620.0, 520.0, 760.0, "Largeur hors-tout."),
        _c("hauteur_assise", 560.0, 500.0, 640.0, "Hauteur du centre de l'assise."),
        _c("inclinaison_assise", 22.0, 12.0, 30.0, "Inclinaison avant de l'assise.", UNITE_ANGLE),
        _c("hauteur_repose_genoux", 320.0, 260.0, 380.0, "Centre du coussin de genoux."),
        _c("distance_assise_genoux", 470.0, 400.0, 560.0, "Distance horizontale centre assise → centre genoux."),
    ),
)
CAMO_CANAPE = TypologieMeuble(
    "camo_canape", VOLET_CAMOUFLABLE, "Canapé deux places à ancrages escamotés",
    "Canapé de salon classique (dossier, galettes, accoudoirs pleins, pieds fuseaux). "
    "Six ancrages masqués : un par accoudoir sous une manchette basculante, deux dans "
    "la traverse avant sous la bavette tapissée, deux dans la traverse arrière sous les galettes.",
    (
        _c("largeur", 1750.0, 1550.0, 1900.0, "Hors-tout d'un deux-places."),
        _c("profondeur", 900.0, 850.0, 1000.0, "Profondeur hors-tout."),
        _c("hauteur_assise", 440.0, 420.0, 460.0, "Dessus galette."),
        _c("hauteur_dossier", 860.0, 780.0, 950.0, "Sommet du dossier."),
        _c("hauteur_accoudoir", 620.0, 580.0, 680.0, "Dessus d'accoudoir."),
    ),
)
CAMO_FAUTEUIL = TypologieMeuble(
    "camo_fauteuil", VOLET_CAMOUFLABLE, "Fauteuil bergère à repose-genoux escamotable",
    "Bergère d'apparence classique. La façade d'assise bascule vers l'avant en "
    "repose-genoux rembourré ; deux ancrages bas sous la façade, deux dans les "
    "montants d'accoudoir sous les manchettes.",
    (
        _c("largeur", 780.0, 720.0, 880.0, "Hors-tout."),
        _c("profondeur", 820.0, 760.0, 900.0, "Hors-tout."),
        _c("hauteur_assise", 440.0, 420.0, 460.0, "Dessus galette."),
        _c("hauteur_dossier", 900.0, 820.0, 1000.0, "Sommet du dossier."),
    ),
)
CADRE_DESSERTE_GENOUX = TypologieMeuble(
    "cadre_desserte_genoux", VOLET_CADRE, "Desserte → cadre à genoux",
    "Desserte de salon à deux plateaux. Les montants arrière sont télescopiques : la "
    "traverse arrière (bandeau du plateau) monte avec eux et devient la barre haute du "
    "cadre ; la tablette basse pivote de 180° vers l'avant autour d'un axe traversant et "
    "présente sa face rembourrée (agenouilloir), portée par deux pieds pivotants. L'usager est sur "
    "le meuble : les tractions sur les ancrages sont des efforts internes.",
    (
        _c("longueur", 1000.0, 900.0, 1200.0, "Longueur de la desserte = largeur du cadre."),
        _c("profondeur", 420.0, 380.0, 480.0, "Profondeur de la desserte."),
        _c("hauteur_meuble", 750.0, 700.0, 800.0, "Hauteur du plateau (état MEUBLE)."),
        _c("hauteur_cadre", 1150.0, 1100.0, 1300.0, "Dessus de la barre haute (état CADRE). "
           "Au-delà de ~1150 mm, le recouvrement télescopique (≥ 3 × section) n'est plus "
           "tenu avec une desserte de 750 mm : la grammaire le signale."),
        _c("hauteur_agenouilloir", 180.0, 150.0, 220.0, "Dessus de la tablette basse (structure)."),
    ),
)
CADRE_TABLE_INCLINEE = TypologieMeuble(
    "cadre_table_inclinee", VOLET_CADRE, "Table basse → cadre incliné",
    "Table basse dont le plateau-cadre (deux vantaux en portefeuille) se déplie puis "
    "se redresse autour d'un axe traversant pour former un cadre incliné à ~78°, "
    "contreventé par la ceinture de la table qui devient piètement en A.",
    (
        _c("longueur", 1100.0, 1000.0, 1200.0, "Longueur de la table (état MEUBLE)."),
        _c("largeur", 700.0, 600.0, 800.0, "Largeur de la table = largeur du cadre."),
        _c("hauteur_meuble", 420.0, 380.0, 450.0, "Hauteur de la table basse."),
        _c("angle_cadre", 78.0, 70.0, 82.0, "Inclinaison du cadre sur l'horizontale (état CADRE).", UNITE_ANGLE),
    ),
)

TYPOLOGIES: dict[str, TypologieMeuble] = {
    t.nom: t for t in (
        TANTRA_CHAISE_DOUBLE_COURBE, TANTRA_FAUTEUIL_LOMBAIRE, TANTRA_BANQUETTE_DEUX_NIVEAUX,
        TANTRA_SIEGE_REPOSE_GENOUX, CAMO_CANAPE, CAMO_FAUTEUIL,
        CADRE_DESSERTE_GENOUX, CADRE_TABLE_INCLINEE,
    )
}


def typologie_par_nom(nom: str) -> TypologieMeuble:
    try:
        return TYPOLOGIES[nom]
    except KeyError as exc:
        raise KeyError(f"Typologie inconnue « {nom} ». Connues : {', '.join(sorted(TYPOLOGIES))}.") from exc


# ---------------------------------------------------------------------------
# Jeu de paramètres globaux
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Signalement:
    """Message de validation de la couche 1."""

    niveau: str
    code: str
    message: str
    compromis: bool = False


@dataclass(frozen=True)
class ParametresGlobaux:
    """Paramètres globaux de la gamme (couche 1), figés."""

    essence_structure: Essence = CHENE
    """Pieds, traverses, ceintures, blocs d'ancrage."""
    essence_courbe: Essence = CONTREPLAQUE_BOULEAU
    """Flasques et coques courbes (volet 1)."""
    revetement_tantra: Revetement = CUIR_COGNAC
    revetement_salon: Revetement = VELOURS_DEPERLANT
    charges: ParametresCharge = CHARGES_DEFAUT
    anthropometrie: Anthropometrie = ANTHROPOMETRIE_DEFAUT
    epaisseur_mousse_assise_mm: float = 60.0
    epaisseur_mousse_dossier_mm: float = 40.0
    jeu_mecanique_mm: float = 2.0
    retrait_ancre_sous_surface_mm: float = 10.0
    """Bois (ou cache) minimal au-dessus d'un insert d'ancre masqué (volet 2)."""

    def valider(self) -> tuple[Signalement, ...]:
        s: list[Signalement] = []
        if self.charges.coefficient_securite < COEFFICIENT_SECURITE_MIN:
            s.append(Signalement(NIVEAU_NON_CONFORME, "cs_insuffisant",
                                 f"CS {self.charges.coefficient_securite:g} < {COEFFICIENT_SECURITE_MIN:g}."))
        if not self.revetement_tantra.lavable:
            s.append(Signalement(NIVEAU_NON_CONFORME, "revetement_tantra_non_lavable",
                                 f"« {self.revetement_tantra.nom_affiche} » n'est pas lavable : "
                                 "interdit en zone de contact (fluides, lubrifiants)."))
        if not self.revetement_salon.aspect_salon:
            s.append(Signalement(NIVEAU_AVERTISSEMENT, "revetement_salon_technique",
                                 f"« {self.revetement_salon.nom_affiche} » trahit un usage "
                                 "technique : contraire à la discrétion du volet camouflable.",
                                 compromis=True))
        if not self.revetement_salon.lavable:
            s.append(Signalement(NIVEAU_AVERTISSEMENT, "revetement_salon_non_lavable",
                                 "Revêtement de façade non lavable : le réserver aux zones sans contact.",
                                 compromis=True))
        if self.essence_structure.famille == FAMILLE_CONTREPLAQUE:
            s.append(Signalement(NIVEAU_AVERTISSEMENT, "structure_contreplaque",
                                 "Contreplaqué en structure : les mortaises et ancrages y tiennent "
                                 "mal (cisaillement roulant). Préférer un massif ou un lamellé."))
        s.append(Signalement(NIVEAU_ESSAI_REQUIS, "essai_reel",
                             "Modèles simplifiés : visa d'ingénieur et essai de charge réel obligatoires."))
        return tuple(s)


PARAMETRES_DEFAUT = ParametresGlobaux()


# ---------------------------------------------------------------------------
# Export Fusion : dict nom -> (valeur, unité, commentaire)
# ---------------------------------------------------------------------------

def _entree(valeur: float, unite: str, commentaire: str) -> tuple[float, str, str]:
    return (float(valeur), unite, commentaire)


def vers_parametres_fusion(
    parametres: ParametresGlobaux | None = None,
    typologies: Mapping[str, TypologieMeuble] | None = None,
) -> dict[str, tuple[float, str, str]]:
    """Convertit la couche 1 en paramètres utilisateur Fusion (préfixe ``tan_``).

    Les longueurs restent en mm (unité utilisateur Fusion) ; la conversion en
    cm (unité interne de l'API) est faite dans ``tantra.fusion_outils``.
    """
    p = parametres or PARAMETRES_DEFAUT
    typologies = dict(typologies) if typologies is not None else TYPOLOGIES
    P = PREFIXE_FUSION
    out: dict[str, tuple[float, str, str]] = {}
    for cle, ess in (("structure", p.essence_structure), ("courbe", p.essence_courbe)):
        out[f"{P}essence_{cle}_rho"] = _entree(ess.masse_volumique_kg_m3, UNITE_MASSE_VOLUMIQUE,
                                               f"Masse volumique — {ess.nom_affiche}.")
        out[f"{P}essence_{cle}_fmk"] = _entree(ess.fm_k_mpa, UNITE_PRESSION,
                                               f"fm,k flexion caractéristique (hypothèse) — {ess.nom_affiche}.")
    out[f"{P}mousse_assise_ep"] = _entree(p.epaisseur_mousse_assise_mm, UNITE_LONGUEUR,
                                          "Épaisseur de mousse des surfaces d'assise.")
    out[f"{P}mousse_dossier_ep"] = _entree(p.epaisseur_mousse_dossier_mm, UNITE_LONGUEUR,
                                           "Épaisseur de mousse des dossiers.")
    out[f"{P}revetement_tantra_ep"] = _entree(p.revetement_tantra.epaisseur_mm, UNITE_LONGUEUR,
                                              f"Revêtement volet Tantra — {p.revetement_tantra.nom_affiche}.")
    out[f"{P}revetement_salon_ep"] = _entree(p.revetement_salon.epaisseur_mm, UNITE_LONGUEUR,
                                             f"Revêtement de façade — {p.revetement_salon.nom_affiche}.")
    out[f"{P}jeu_mecanique"] = _entree(p.jeu_mecanique_mm, UNITE_LONGUEUR, "Jeu fonctionnel des mécanismes.")
    out[f"{P}retrait_ancre"] = _entree(p.retrait_ancre_sous_surface_mm, UNITE_LONGUEUR,
                                       "Bois minimal au-dessus d'un insert masqué (volet camouflable).")
    c = p.charges
    out[f"{P}charge_ancrage"] = _entree(c.charge_service_ancrage_n, UNITE_FORCE,
                                        "Charge de service par ancrage (hypothèse, essai réel obligatoire).")
    out[f"{P}poids_personne"] = _entree(c.poids_personne_n, UNITE_FORCE, "Poids de service d'une personne.")
    out[f"{P}facteur_dynamique"] = _entree(c.facteur_dynamique, "", "Facteur dynamique sur le poids. Sans unité.")
    out[f"{P}coefficient_securite"] = _entree(c.coefficient_securite, "", "Coefficient de sécurité (≥ 3). Sans unité.")
    a = p.anthropometrie
    for m in a.mesures():
        out[f"{P}anthropo_{m.nom}_p5"] = _entree(m.p5, UNITE_LONGUEUR, f"{m.nom} P5 — {m.commentaire}")
        out[f"{P}anthropo_{m.nom}_p95"] = _entree(m.p95, UNITE_LONGUEUR, f"{m.nom} P95 — {m.commentaire}")
    for typo in typologies.values():
        for cote in typo.cotes:
            out[f"{P}{typo.nom}_{cote.nom}"] = _entree(
                cote.valeur, cote.unite,
                f"{typo.nom} — {cote.commentaire} Plage [{cote.plage.minimum:g}–{cote.plage.maximum:g}] {cote.unite}.",
            )
    return out
