# -*- coding: utf-8 -*-
"""Paramètres globaux de la gamme Incognito (couche 1).

Module Python pur, sans dépendance à ``adsk``, afin d'être testable hors
Fusion 360. Toutes les cotes sont en millimètres, les masses volumiques
en kg/m³, les modules et contraintes en MPa, les forces en N.

Les dataclasses sont figées (``frozen=True``) : on instancie une variante
plutôt que de muter un défaut.

Les valeurs d'essences, de charges et de sections sont des **hypothèses
de conception documentées**. Elles ne constituent pas un justificatif
Eurocode 5 ni une certification. Tout ancrage destiné à retenir une
personne exige le visa d'un ingénieur et un essai de charge réel.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

# ---------------------------------------------------------------------------
# Unités (rappel : tout le vocabulaire interne est en mm / N / MPa / kg)
# ---------------------------------------------------------------------------

UNITE_LONGUEUR = "mm"
UNITE_FORCE = "N"
UNITE_PRESSION = "MPa"
UNITE_MASSE_VOLUMIQUE = "kg/m^3"
UNITE_MASSE = "kg"
UNITE_ANGLE = "deg"


# ---------------------------------------------------------------------------
# Utilitaires de cote
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Plage:
    """Intervalle fermé [minimum, maximum] pour une cote ou une grandeur."""

    minimum: float
    maximum: float
    unite: str = UNITE_LONGUEUR

    def __post_init__(self) -> None:
        if self.maximum < self.minimum:
            raise ValueError(
                f"Plage invalide : maximum ({self.maximum}) < minimum ({self.minimum})."
            )

    def contient(self, valeur: float) -> bool:
        """Retourne True si ``valeur`` est dans l'intervalle fermé."""
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
                f"Cote « {self.nom} » : valeur {self.valeur} {self.unite} "
                f"hors plage [{self.plage.minimum}, {self.plage.maximum}]."
            )

    def avec(self, valeur: float) -> "Cote":
        """Retourne une copie figée avec une nouvelle valeur (validée)."""
        return Cote(
            nom=self.nom,
            valeur=valeur,
            plage=self.plage,
            commentaire=self.commentaire,
            unite=self.unite,
        )


@dataclass(frozen=True)
class TypologieSalon:
    """Ensemble de cotes d'un meuble de salon d'apparence classique."""

    nom: str
    description: str
    cotes: tuple[Cote, ...]

    def cote(self, nom: str) -> Cote:
        for cote in self.cotes:
            if cote.nom == nom:
                return cote
        raise KeyError(f"Cote inconnue « {nom} » pour la typologie {self.nom}.")

    def valeurs(self) -> dict[str, float]:
        return {cote.nom: cote.valeur for cote in self.cotes}


# ---------------------------------------------------------------------------
# Dimensions salon standard par typologie
# Sources d'hypothèse : usages européens courants (assise ~420-450 mm,
# tables basses ~400-450 mm). Ce ne sont pas des normes NF, simplement
# des proportions de salon classique.
# ---------------------------------------------------------------------------

PLAGE_HAUTEUR_ASSISE = Plage(420.0, 450.0)
PLAGE_HAUTEUR_TABLE_BASSE = Plage(400.0, 450.0)

CANAPE = TypologieSalon(
    nom="canape",
    description=(
        "Canapé de salon 2 ou 3 places, assise et dossier capitonnés, "
        "pieds tournés ou fuseaux. La fonction reste entièrement cachée "
        "dans le caisson et les accoudoirs."
    ),
    cotes=(
        Cote("hauteur_assise", 430.0, PLAGE_HAUTEUR_ASSISE,
             "Dessus de coussin, confort salon classique."),
        Cote("profondeur_hors_tout", 980.0, Plage(900.0, 1100.0),
             "Profondeur totale y compris dossier et coussin."),
        Cote("profondeur_assise", 560.0, Plage(520.0, 620.0),
             "Profondeur utile d'assise (hors dossier)."),
        Cote("hauteur_dossier", 900.0, Plage(820.0, 1000.0),
             "Sommet du dossier depuis le sol."),
        Cote("largeur_deux_places", 1700.0, Plage(1550.0, 1900.0),
             "Hors-tout d'un deux-places."),
        Cote("largeur_trois_places", 2200.0, Plage(2000.0, 2400.0),
             "Hors-tout d'un trois-places."),
        Cote("hauteur_accoudoir", 630.0, Plage(580.0, 680.0),
             "Dessus d'accoudoir depuis le sol."),
    ),
)

FAUTEUIL = TypologieSalon(
    nom="fauteuil",
    description="Fauteuil d'accompagnement assorti au canapé, une place.",
    cotes=(
        Cote("hauteur_assise", 430.0, PLAGE_HAUTEUR_ASSISE,
             "Dessus de coussin, aligné sur le canapé."),
        Cote("largeur_hors_tout", 820.0, Plage(750.0, 920.0),
             "Hors-tout y compris accoudoirs."),
        Cote("profondeur_hors_tout", 900.0, Plage(820.0, 1000.0),
             "Profondeur totale y compris dossier."),
        Cote("profondeur_assise", 560.0, Plage(520.0, 620.0),
             "Profondeur utile d'assise."),
        Cote("hauteur_dossier", 900.0, Plage(820.0, 1000.0),
             "Sommet du dossier depuis le sol."),
    ),
)

TABLE_BASSE = TypologieSalon(
    nom="table_basse",
    description=(
        "Table basse de salon, plateau plein d'apparence classique. "
        "Un tiroir ou un plateau basculant peut masquer un mécanisme, "
        "sans ferrure visible."
    ),
    cotes=(
        Cote("hauteur", 420.0, PLAGE_HAUTEUR_TABLE_BASSE,
             "Dessus de plateau. Plage 400-450 mm, salon classique."),
        Cote("longueur", 1200.0, Plage(1000.0, 1400.0),
             "Longueur du plateau."),
        Cote("largeur", 700.0, Plage(550.0, 850.0),
             "Largeur (profondeur) du plateau."),
        Cote("epaisseur_plateau", 28.0, Plage(22.0, 40.0),
             "Épaisseur du plateau massif ou plaqué."),
    ),
)

BANC_ENTREE = TypologieSalon(
    nom="banc_entree",
    description=(
        "Banc d'entrée, avec ou sans dossier bas, éventuellement coffre. "
        "Distinct de la banquette de salon (premier meuble de la gamme)."
    ),
    cotes=(
        Cote("hauteur_assise", 430.0, PLAGE_HAUTEUR_ASSISE,
             "Dessus d'assise (coussin ou bois)."),
        Cote("longueur", 1200.0, Plage(1000.0, 1400.0),
             "Longueur hors-tout."),
        Cote("profondeur", 400.0, Plage(350.0, 480.0),
             "Profondeur hors-tout, typiquement plus étroite qu'une banquette."),
        Cote("hauteur_dossier", 800.0, Plage(0.0, 900.0),
             "Sommet du dossier ; 0 si banc sans dossier."),
    ),
)

POUF = TypologieSalon(
    nom="pouf",
    description=(
        "Pouf capitonné de salon classique (cube). Peut intégrer un module "
        "de selle vibrante (gamme entrée : balourd ; gamme haut : voice coil), "
        "entièrement masqué sous un coussin amovible à l'état pouf."
    ),
    cotes=(
        Cote("hauteur", 430.0, PLAGE_HAUTEUR_ASSISE,
             "Dessus de coussin, aligné sur l'assise du salon."),
        Cote("largeur", 500.0, Plage(400.0, 650.0),
             "Largeur ou diamètre hors-tout."),
        Cote("profondeur", 500.0, Plage(400.0, 650.0),
             "Profondeur hors-tout (égale à la largeur pour un cube)."),
    ),
)

BIBLIOTHEQUE = TypologieSalon(
    nom="bibliotheque",
    description=(
        "Bibliothèque d'apparence classique (montants, corniche, tablettes). "
        "Les montants et la plinthe peuvent masquer des ancrages."
    ),
    cotes=(
        Cote("hauteur", 2000.0, Plage(1800.0, 2300.0),
             "Hors-tout y compris corniche."),
        Cote("largeur", 1000.0, Plage(800.0, 1400.0),
             "Largeur hors-tout d'un corps."),
        Cote("profondeur", 350.0, Plage(300.0, 420.0),
             "Profondeur hors-tout, tablettes comprises."),
        Cote("epaisseur_montant", 22.0, Plage(18.0, 32.0),
             "Épaisseur des montants et côtés."),
        Cote("entraxe_tablettes", 320.0, Plage(250.0, 400.0),
             "Entraxe vertical typique des tablettes."),
    ),
)

BANQUETTE = TypologieSalon(
    nom="banquette",
    description=(
        "Banquette de salon classique (premier meuble de la gamme) : "
        "dossier, assise capitonnée, pieds tournés/fuseaux. L'assise se "
        "soulève comme un coffre et dissimule un banc déployable. "
        "Les cotes du banc fonctionnel (appui 700 × 1150 mm) sont des "
        "hypothèses documentées : le squelette Equinox ne contenait pas "
        "les cotes du banc Feuille/Flore."
    ),
    cotes=(
        Cote("hauteur_assise", 430.0, PLAGE_HAUTEUR_ASSISE,
             "Dessus du coussin d'assise, état fermé."),
        Cote("longueur", 1300.0, Plage(1200.0, 1600.0),
             "Longueur hors-tout ; doit loger le banc de 1150 mm plus parois."),
        Cote("profondeur_hors_tout", 680.0, Plage(600.0, 780.0),
             "Profondeur totale y compris dossier. Une profondeur trop faible "
             "compromet la stabilité au basculement une fois le banc déployé."),
        Cote("profondeur_assise", 540.0, Plage(500.0, 620.0),
             "Profondeur utile d'assise (hors dossier)."),
        Cote("hauteur_dossier", 880.0, Plage(800.0, 980.0),
             "Sommet du dossier depuis le sol."),
        Cote("hauteur_pieds", 120.0, Plage(90.0, 160.0),
             "Pieds tournés ou fuseaux, du sol au dessous du caisson."),
        Cote("hauteur_appui_banc", 700.0, Plage(650.0, 750.0),
             "Hauteur d'appui du banc déployé (dessus du cuir). Hypothèse."),
        Cote("longueur_appui_banc", 1150.0, Plage(1100.0, 1250.0),
             "Longueur d'appui du banc déployé. Hypothèse (Feuille/Flore absente)."),
        Cote("largeur_appui_banc", 320.0, Plage(280.0, 380.0),
             "Largeur (profondeur) du coussin d'appui du banc déployé."),
    ),
)

TYPOLOGIES: dict[str, TypologieSalon] = {
    typologie.nom: typologie
    for typologie in (
        CANAPE,
        FAUTEUIL,
        TABLE_BASSE,
        BANC_ENTREE,
        POUF,
        BIBLIOTHEQUE,
        BANQUETTE,
    )
}


def typologie_par_nom(nom: str) -> TypologieSalon:
    """Retourne une typologie par son identifiant ASCII."""
    try:
        return TYPOLOGIES[nom]
    except KeyError as exc:
        connues = ", ".join(sorted(TYPOLOGIES))
        raise KeyError(f"Typologie inconnue « {nom} ». Connues : {connues}.") from exc


# ---------------------------------------------------------------------------
# Essences classiques (vocabulaire de la couche 1)
# Valeurs approximatives à 12 % d'humidité, bois de fil. Voir sources.
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Essence:
    """Essence de feuillu classique, propriétés mécaniques approximatives.

    ``contrainte_admissible_flexion_mpa`` est une **hypothèse de mobilier**,
    pas une valeur de calcul réglementaire (Eurocode 5 : k_mod, γ_M, etc.).
    """

    nom: str
    nom_affiche: str
    nom_latin: str
    masse_volumique_kg_m3: float
    module_elasticite_mpa: float
    contrainte_caracteristique_flexion_mpa: float
    contrainte_admissible_flexion_mpa: float
    contrainte_admissible_cisaillement_mpa: float
    source: str
    hypotheses: str

    def __post_init__(self) -> None:
        for champ, valeur in (
            ("masse_volumique_kg_m3", self.masse_volumique_kg_m3),
            ("module_elasticite_mpa", self.module_elasticite_mpa),
            ("contrainte_caracteristique_flexion_mpa", self.contrainte_caracteristique_flexion_mpa),
            ("contrainte_admissible_flexion_mpa", self.contrainte_admissible_flexion_mpa),
            ("contrainte_admissible_cisaillement_mpa", self.contrainte_admissible_cisaillement_mpa),
        ):
            if valeur <= 0:
                raise ValueError(f"Essence {self.nom} : {champ} doit être > 0 (reçu {valeur}).")


_SOURCE_ESSENCES = (
    "Ordres de grandeur à 12 % d'humidité : USDA Forest Products Laboratory, "
    "Wood Handbook (FPL-GTR-282) pour les moyennes de masse volumique, MOE et MOR ; "
    "classes NF EN 338 (feuillus D30/D40) pour l'ordre de grandeur des contraintes "
    "caractéristiques de flexion fm,k ; fiches CIRAD/FCBA pour les feuillus européens."
)

_HYPOTHESES_ESSENCES = (
    "fm,k est une hypothèse d'ordre de grandeur (5e centile), nettement inférieure "
    "au MOR moyen de la littérature. La contrainte admissible retenue vaut environ "
    "fm,k / 2,8 à / 3,5 et sert uniquement aux vérifications simplifiées de ce "
    "package. Elle n'inclut pas k_mod, γ_M, l'humidité de service, les nœuds ni "
    "le fil dévié. Un ingénieur doit reprendre le calcul (Eurocode 5 ou équivalent) "
    "et un essai de charge réel reste obligatoire pour tout ancrage."
)

CHENE = Essence(
    nom="chene",
    nom_affiche="Chêne",
    nom_latin="Quercus robur / Quercus petraea",
    masse_volumique_kg_m3=710.0,
    module_elasticite_mpa=12500.0,
    contrainte_caracteristique_flexion_mpa=40.0,
    contrainte_admissible_flexion_mpa=14.0,
    contrainte_admissible_cisaillement_mpa=2.0,
    source=_SOURCE_ESSENCES,
    hypotheses=_HYPOTHESES_ESSENCES,
)

NOYER = Essence(
    nom="noyer",
    nom_affiche="Noyer",
    nom_latin="Juglans regia",
    masse_volumique_kg_m3=650.0,
    module_elasticite_mpa=11600.0,
    contrainte_caracteristique_flexion_mpa=36.0,
    contrainte_admissible_flexion_mpa=12.0,
    contrainte_admissible_cisaillement_mpa=1.8,
    source=_SOURCE_ESSENCES,
    hypotheses=_HYPOTHESES_ESSENCES,
)

HETRE = Essence(
    nom="hetre",
    nom_affiche="Hêtre",
    nom_latin="Fagus sylvatica",
    masse_volumique_kg_m3=720.0,
    module_elasticite_mpa=14000.0,
    contrainte_caracteristique_flexion_mpa=40.0,
    contrainte_admissible_flexion_mpa=14.0,
    contrainte_admissible_cisaillement_mpa=2.0,
    source=_SOURCE_ESSENCES,
    hypotheses=_HYPOTHESES_ESSENCES,
)

FRENE = Essence(
    nom="frene",
    nom_affiche="Frêne",
    nom_latin="Fraxinus excelsior",
    masse_volumique_kg_m3=690.0,
    module_elasticite_mpa=13000.0,
    contrainte_caracteristique_flexion_mpa=40.0,
    contrainte_admissible_flexion_mpa=14.0,
    contrainte_admissible_cisaillement_mpa=2.0,
    source=_SOURCE_ESSENCES,
    hypotheses=_HYPOTHESES_ESSENCES,
)

MERISIER = Essence(
    nom="merisier",
    nom_affiche="Merisier",
    nom_latin="Prunus avium",
    masse_volumique_kg_m3=610.0,
    module_elasticite_mpa=10300.0,
    contrainte_caracteristique_flexion_mpa=30.0,
    contrainte_admissible_flexion_mpa=10.0,
    contrainte_admissible_cisaillement_mpa=1.6,
    source=_SOURCE_ESSENCES,
    hypotheses=_HYPOTHESES_ESSENCES,
)

ESSENCES_BASE: dict[str, Essence] = {
    essence.nom: essence
    for essence in (CHENE, NOYER, HETRE, FRENE, MERISIER)
}

ESSENCE_DEFAUT = CHENE


# ---------------------------------------------------------------------------
# Revêtements discrets
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Revetement:
    """Revêtement d'apparence salon, ou cuir réservé à l'intérieur caché."""

    nom: str
    nom_affiche: str
    famille: str  # "tissu" ou "cuir"
    epaisseur_mm: float
    usage: str  # "exterieur_visible", "interieur_cache", "exterieur_derogation"
    couleurs_typiques: tuple[str, ...]
    commentaire: str

    def __post_init__(self) -> None:
        if self.epaisseur_mm <= 0:
            raise ValueError(f"Revêtement {self.nom} : épaisseur doit être > 0.")
        if self.famille not in {"tissu", "cuir"}:
            raise ValueError(f"Revêtement {self.nom} : famille inconnue {self.famille}.")
        usages = {"exterieur_visible", "interieur_cache", "exterieur_derogation"}
        if self.usage not in usages:
            raise ValueError(f"Revêtement {self.nom} : usage inconnu {self.usage}.")

    def visible_en_facade(self) -> bool:
        """True si le revêtement apparaît sur l'extérieur du meuble fermé."""
        return self.usage in {"exterieur_visible", "exterieur_derogation"}

    def conforme_discretions_defaut(self) -> bool:
        """La règle de gamme « zéro cuir visible » n'autorise le cuir qu'à l'intérieur."""
        if self.famille == "cuir":
            return self.usage == "interieur_cache"
        return True


VELOURS = Revetement(
    nom="velours",
    nom_affiche="Velours",
    famille="tissu",
    epaisseur_mm=2.0,
    usage="exterieur_visible",
    couleurs_typiques=("gris_souris", "vert_sauge", "creme", "marine", "taupe"),
    commentaire="Tissu de salon classique, mat, aucun éclat métallique.",
)

LIN = Revetement(
    nom="lin",
    nom_affiche="Lin",
    famille="tissu",
    epaisseur_mm=1.5,
    usage="exterieur_visible",
    couleurs_typiques=("naturel", "ivoire", "gris_clair", "terre"),
    commentaire="Tissu sobre, aspect naturel, discret dans un salon.",
)

LAINE_BOUCLEE = Revetement(
    nom="laine_bouclee",
    nom_affiche="Laine bouclée",
    famille="tissu",
    epaisseur_mm=3.5,
    usage="exterieur_visible",
    couleurs_typiques=("ivoire", "grege", "charbon", "camel"),
    commentaire="Bouclé contemporain-classique ; masque bien les capitons discrets.",
)

TISSU_CHINE = Revetement(
    nom="tissu_chine",
    nom_affiche="Tissu chiné",
    famille="tissu",
    epaisseur_mm=2.0,
    usage="exterieur_visible",
    couleurs_typiques=("gris_chine", "beige_chine", "bleu_gris"),
    commentaire="Chiné uni en apparence, très « mobilier de salon ».",
)

CUIR_COGNAC = Revetement(
    nom="cuir_cognac",
    nom_affiche="Cuir cognac",
    famille="cuir",
    epaisseur_mm=2.0,
    usage="interieur_cache",
    couleurs_typiques=("cognac",),
    commentaire=(
        "Réservé au banc déployable et aux surfaces uniquement visibles "
        "après ouverture du coffre. Interdit en façade selon la règle "
        "« zéro cuir visible »."
    ),
)

CUIR_NOIR = Revetement(
    nom="cuir_noir",
    nom_affiche="Cuir noir",
    famille="cuir",
    epaisseur_mm=2.0,
    usage="interieur_cache",
    couleurs_typiques=("noir",),
    commentaire=(
        "Même règle que le cuir cognac : intérieur caché uniquement "
        "(banc déployé, caches d'ancrage)."
    ),
)

CUIR_SOBRE_FACADE = Revetement(
    nom="cuir_sobre_facade",
    nom_affiche="Cuir sobre de façade (dérogation)",
    famille="cuir",
    epaisseur_mm=2.0,
    usage="exterieur_derogation",
    couleurs_typiques=("cognac_clair", "havane", "noir_mat"),
    commentaire=(
        "Dérogation documentée : un club en cuir uni peut passer pour un "
        "meuble de salon classique, mais il enfreint la règle de gamme "
        "« zéro cuir visible ». Non retenu par défaut."
    ),
)

REVETEMENTS_BASE: dict[str, Revetement] = {
    revetement.nom: revetement
    for revetement in (
        VELOURS,
        LIN,
        LAINE_BOUCLEE,
        TISSU_CHINE,
        CUIR_COGNAC,
        CUIR_NOIR,
        CUIR_SOBRE_FACADE,
    )
}

REVETEMENT_EXTERIEUR_DEFAUT = VELOURS
REVETEMENT_BANC_DEFAUT = CUIR_COGNAC


# ---------------------------------------------------------------------------
# Paramètres de discrétion
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ParametresDiscretion:
    """Retraits, jeux et épaisseurs qui garantissent qu'aucune ferrure,
    anneau ou cuir n'est visible à l'état fermé.

    Augmenter un retrait améliore la discrétion mais réduit la section
    de bois utile autour d'une ancre — voir ``valider_ancrage``.
    """

    retrait_min_ancre_sous_surface_mm: float = 10.0
    """Épaisseur minimale de bois (ou cache affleurant) entre l'ancre
    métallique et toute surface visible à l'état fermé."""

    jeu_mecanique_mm: float = 2.0
    """Jeu fonctionnel des mécanismes (charnières, joues, trappes)."""

    jeu_repli_mm: float = 4.0
    """Marge supplémentaire pour que le banc replié rentre dans le caisson
    malgré le tissu, les tolérances et l'hygrométrie."""

    epaisseur_recouvrement_bois_mm: float = 10.0
    """Épaisseur typique d'un cache bois affleurant sur ancre ou charnière."""

    epaisseur_recouvrement_tissu_mm: float = 2.0
    """Épaisseur typique du seul tissu de façade (hors mousse)."""

    epaisseur_min_paroi_visible_mm: float = 18.0
    """Épaisseur minimale d'une paroi vue de l'extérieur (ébénisterie classique)."""

    mortaise_charniere_recul_bord_mm: float = 8.0
    """Distance minimale entre une mortaise de charnière invisible (Soss)
    et le chant visible, pour éviter un « témoin » ou un éclaté."""

    def __post_init__(self) -> None:
        for champ, valeur in (
            ("retrait_min_ancre_sous_surface_mm", self.retrait_min_ancre_sous_surface_mm),
            ("jeu_mecanique_mm", self.jeu_mecanique_mm),
            ("jeu_repli_mm", self.jeu_repli_mm),
            ("epaisseur_recouvrement_bois_mm", self.epaisseur_recouvrement_bois_mm),
            ("epaisseur_recouvrement_tissu_mm", self.epaisseur_recouvrement_tissu_mm),
            ("epaisseur_min_paroi_visible_mm", self.epaisseur_min_paroi_visible_mm),
            ("mortaise_charniere_recul_bord_mm", self.mortaise_charniere_recul_bord_mm),
        ):
            if valeur < 0:
                raise ValueError(f"{champ} ne peut pas être négatif ({valeur}).")


DISCRETION_DEFAUT = ParametresDiscretion()


# ---------------------------------------------------------------------------
# Paramètres de charge des ancrages
# ---------------------------------------------------------------------------

COEFFICIENT_SECURITE_MIN_RECOMMANDE = 3.0


@dataclass(frozen=True)
class ParametresCharge:
    """Charges de service et de rupture visées pour les ancrages.

    Ces valeurs sont des **cibles de conception**, pas des charges certifiées.
    Un mouvement brusque, une chute ou un effet de levier peut dépasser
    la charge de service. Essai de charge réel obligatoire.
    """

    charge_service_ancrage_n: float = 1500.0
    """Charge de service par point d'ancrage (adulte, traction, hypothèse)."""

    charge_service_appui_n: float = 1500.0
    """Charge de service verticale sur l'appui du banc (un adulte + marge)."""

    coefficient_securite: float = COEFFICIENT_SECURITE_MIN_RECOMMANDE
    """Coefficient de sécurité appliqué à la charge de service (≥ 3 recommandé)."""

    def __post_init__(self) -> None:
        if self.charge_service_ancrage_n <= 0:
            raise ValueError("charge_service_ancrage_n doit être > 0.")
        if self.charge_service_appui_n <= 0:
            raise ValueError("charge_service_appui_n doit être > 0.")
        if self.coefficient_securite <= 0:
            raise ValueError("coefficient_securite doit être > 0.")

    @property
    def charge_rupture_visee_ancrage_n(self) -> float:
        """Charge de rupture visée = charge de service × coefficient de sécurité."""
        return self.charge_service_ancrage_n * self.coefficient_securite

    @property
    def charge_rupture_visee_appui_n(self) -> float:
        return self.charge_service_appui_n * self.coefficient_securite


CHARGES_DEFAUT = ParametresCharge()


# ---------------------------------------------------------------------------
# Géométrie d'une ancre encastrée (pour la validation)
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class GeometrieAncre:
    """Géométrie simplifiée d'une ancre métallique noyée dans le bois.

    L'ancre est un insert (cylindre ou platine) logé dans un bloc ou un
    rail. ``epaisseur_recouvrement_mm`` est le bois (ou cache) qui cache
    l'ancre ; ce recouvrement ne doit en général **pas** être compté dans
    la section résistante si c'est un cache rapporté ou un voile mince.
    """

    diametre_insert_mm: float = 12.0
    longueur_encastrement_mm: float = 80.0
    epaisseur_bloc_mm: float = 54.0
    largeur_bloc_mm: float = 70.0
    longueur_bloc_mm: float = 80.0
    epaisseur_recouvrement_mm: float = 10.0
    recouvrement_est_structurel: bool = False
    nombre_plans_cisaillement: int = 2
    distance_au_bord_mm: float = 30.0

    def __post_init__(self) -> None:
        for champ, valeur in (
            ("diametre_insert_mm", self.diametre_insert_mm),
            ("longueur_encastrement_mm", self.longueur_encastrement_mm),
            ("epaisseur_bloc_mm", self.epaisseur_bloc_mm),
            ("largeur_bloc_mm", self.largeur_bloc_mm),
            ("longueur_bloc_mm", self.longueur_bloc_mm),
            ("nombre_plans_cisaillement", float(self.nombre_plans_cisaillement)),
        ):
            if valeur <= 0:
                raise ValueError(f"{champ} doit être > 0.")
        if self.epaisseur_recouvrement_mm < 0 or self.distance_au_bord_mm < 0:
            raise ValueError("Les distances de recouvrement et de bord doivent être ≥ 0.")


ANCRE_DEFAUT = GeometrieAncre()


# ---------------------------------------------------------------------------
# Validation : discrétion vs solidité
# ---------------------------------------------------------------------------

NIVEAU_OK = "ok"
NIVEAU_AVERTISSEMENT = "avertissement"
NIVEAU_NON_CONFORME = "non_conforme"
NIVEAU_ESSAI_REQUIS = "essai_requis"


@dataclass(frozen=True)
class Signalement:
    """Message de validation, éventuellement un compromis discrétion/solidité."""

    niveau: str
    code: str
    message: str
    compromis: bool = False


@dataclass(frozen=True)
class RapportValidation:
    """Rapport d'une validation d'ancrage ou de paramètre de charge."""

    signalements: tuple[Signalement, ...]

    @property
    def conforme(self) -> bool:
        """True s'il n'y a aucun signalement bloquant ``non_conforme``."""
        return all(s.niveau != NIVEAU_NON_CONFORME for s in self.signalements)

    @property
    def compromis(self) -> tuple[Signalement, ...]:
        return tuple(s for s in self.signalements if s.compromis)

    @property
    def essais_requis(self) -> tuple[Signalement, ...]:
        return tuple(s for s in self.signalements if s.niveau == NIVEAU_ESSAI_REQUIS)

    def plus_grave(self) -> str:
        ordre = (NIVEAU_OK, NIVEAU_AVERTISSEMENT, NIVEAU_ESSAI_REQUIS, NIVEAU_NON_CONFORME)
        return max((s.niveau for s in self.signalements), key=ordre.index, default=NIVEAU_OK)


def section_nette_minimale_mm2(
    charge_service_n: float,
    coefficient_securite: float,
    contrainte_admissible_mpa: float,
) -> float:
    """Section nette minimale (mm²) sous l'hypothèse simplifiée σ = F / A.

    ``contrainte_admissible_mpa`` est en MPa = N/mm².
    """
    if charge_service_n <= 0 or coefficient_securite <= 0:
        raise ValueError("La charge et le coefficient de sécurité doivent être > 0.")
    if contrainte_admissible_mpa <= 0:
        raise ValueError("La contrainte admissible doit être > 0.")
    return (charge_service_n * coefficient_securite) / contrainte_admissible_mpa


def paroi_minimale_cisaillement_mm(
    charge_service_n: float,
    coefficient_securite: float,
    contrainte_cisaillement_mpa: float,
    longueur_encastrement_mm: float,
    nombre_plans: int,
) -> float:
    """Épaisseur minimale de bois par plan de cisaillement (modèle très simplifié).

    F × CS = τ_adm × L_encastrement × t × n_plans, d'où t.
    Ce modèle ignore le fendage, l'orientation du fil et les concentrations.
    """
    if min(charge_service_n, coefficient_securite, contrainte_cisaillement_mpa,
           longueur_encastrement_mm, nombre_plans) <= 0:
        raise ValueError("Tous les arguments de paroi_minimale_cisaillement_mm doivent être > 0.")
    return (charge_service_n * coefficient_securite) / (
        contrainte_cisaillement_mpa * longueur_encastrement_mm * nombre_plans
    )


def valider_ancrage(
    essence: Essence,
    geometrie: GeometrieAncre,
    charges: ParametresCharge,
    discretion: ParametresDiscretion,
) -> RapportValidation:
    """Valide une ancre encastrée et signale les compromis discrétion / solidité.

    Vérifications (toutes **simplifiées**, à reprendre par un ingénieur) :

    * coefficient de sécurité ≥ 3 recommandé ;
    * recouvrement de discrétion ≥ retrait minimal ;
    * le recouvrement plus l'insert tiennent dans l'épaisseur du bloc ;
    * section nette du bloc (hors insert) ≥ F×CS / σ_adm en traction/compression ;
    * paroi de bois de part et d'autre de l'insert ≥ paroi minimale de cisaillement ;
    * distance au bord suffisante pour limiter le fendage.

    Un signalement ``essai_requis`` est **toujours** émis : aucun résultat
    de cette fonction ne dispense d'un essai de charge réel.
    """
    signalements: list[Signalement] = []

    if charges.coefficient_securite < COEFFICIENT_SECURITE_MIN_RECOMMANDE:
        signalements.append(Signalement(
            NIVEAU_NON_CONFORME,
            "cs_insuffisant",
            (
                f"Coefficient de sécurité {charges.coefficient_securite:g} < "
                f"{COEFFICIENT_SECURITE_MIN_RECOMMANDE:g} recommandé. "
                "Augmenter le CS ou réduire la charge de service."
            ),
        ))
    elif charges.coefficient_securite == COEFFICIENT_SECURITE_MIN_RECOMMANDE:
        signalements.append(Signalement(
            NIVEAU_AVERTISSEMENT,
            "cs_minimal",
            (
                f"Coefficient de sécurité égal au minimum recommandé "
                f"({COEFFICIENT_SECURITE_MIN_RECOMMANDE:g}). Un usage dynamique "
                "(à-coups) peut nécessiter davantage."
            ),
        ))

    if geometrie.epaisseur_recouvrement_mm < discretion.retrait_min_ancre_sous_surface_mm:
        signalements.append(Signalement(
            NIVEAU_NON_CONFORME,
            "retrait_discretion_insuffisant",
            (
                f"Recouvrement {geometrie.epaisseur_recouvrement_mm:g} mm < "
                f"retrait minimal de discrétion "
                f"{discretion.retrait_min_ancre_sous_surface_mm:g} mm. "
                "L'ancre risquerait d'être devinée (témoin, son, ou perçage apparent)."
            ),
            compromis=True,
        ))

    # Empilement recouvrement + insert dans l'épaisseur du bloc
    if geometrie.recouvrement_est_structurel:
        epaisseur_utile = geometrie.epaisseur_bloc_mm
        recouvrement_compte = geometrie.epaisseur_recouvrement_mm
    else:
        # Cache rapporté ou voile non compté dans la section résistante.
        epaisseur_utile = geometrie.epaisseur_bloc_mm - geometrie.epaisseur_recouvrement_mm
        recouvrement_compte = 0.0

    empilement = recouvrement_compte + geometrie.diametre_insert_mm
    # De part et d'autre de l'insert il faut encore deux parois.
    # Si le recouvrement n'est pas structurel, il a déjà été retiré de epaisseur_utile.
    if empilement >= geometrie.epaisseur_bloc_mm:
        signalements.append(Signalement(
            NIVEAU_NON_CONFORME,
            "insert_ne_rentre_pas",
            (
                f"L'insert Ø {geometrie.diametre_insert_mm:g} mm plus le recouvrement "
                f"({geometrie.epaisseur_recouvrement_mm:g} mm) dépassent l'épaisseur "
                f"du bloc ({geometrie.epaisseur_bloc_mm:g} mm). Compromis typique : "
                "soit on réduit le recouvrement (discrétion en baisse), soit on "
                "épaissit le bloc (encombrement, éventuellement visible)."
            ),
            compromis=True,
        ))

    paroi_dispo = (epaisseur_utile - geometrie.diametre_insert_mm) / 2.0
    paroi_min = paroi_minimale_cisaillement_mm(
        charges.charge_service_ancrage_n,
        charges.coefficient_securite,
        essence.contrainte_admissible_cisaillement_mpa,
        geometrie.longueur_encastrement_mm,
        geometrie.nombre_plans_cisaillement,
    )

    if paroi_dispo <= 0:
        signalements.append(Signalement(
            NIVEAU_NON_CONFORME,
            "section_restante_nulle",
            (
                f"Aucune section de bois restante autour de l'insert dans le bloc "
                f"(épaisseur utile {epaisseur_utile:g} mm, insert "
                f"{geometrie.diametre_insert_mm:g} mm). Le rail ou le bloc est trop "
                "mince pour loger une ancre discrète et résistante. Recaler un bloc "
                "d'ancrage local plus volumineux, masqué sous le cuir du banc."
            ),
            compromis=True,
        ))
    elif paroi_dispo < paroi_min:
        signalements.append(Signalement(
            NIVEAU_NON_CONFORME,
            "paroi_cisaillement_insuffisante",
            (
                f"Paroi de bois restante {paroi_dispo:.1f} mm < minimum simplifié "
                f"{paroi_min:.1f} mm (cisaillement, {essence.nom_affiche}, "
                f"F×CS = {charges.charge_rupture_visee_ancrage_n:.0f} N). "
                "Compromis discrétion / solidité : augmenter l'encastrement ou "
                "l'épaisseur du bloc (mieux, sous le coussin caché) plutôt que "
                "de réduire le recouvrement visible."
            ),
            compromis=True,
        ))

    # Section nette (traction / compression simplifiée)
    section_nette = max(0.0, geometrie.largeur_bloc_mm * epaisseur_utile
                        - geometrie.diametre_insert_mm * epaisseur_utile)
    section_min = section_nette_minimale_mm2(
        charges.charge_service_ancrage_n,
        charges.coefficient_securite,
        essence.contrainte_admissible_flexion_mpa,
    )
    if section_nette < section_min:
        signalements.append(Signalement(
            NIVEAU_NON_CONFORME,
            "section_nette_insuffisante",
            (
                f"Section nette {section_nette:.0f} mm² < minimum simplifié "
                f"{section_min:.0f} mm² (σ_adm flexion {essence.contrainte_admissible_flexion_mpa:g} "
                f"MPa, {essence.nom_affiche}). Agrandir le bloc d'ancrage."
            ),
            compromis=True,
        ))

    # Distance au bord (fendage) : hypothèse conservative 2 × Ø ou 25 mm
    bord_min = max(25.0, 2.0 * geometrie.diametre_insert_mm)
    if geometrie.distance_au_bord_mm < bord_min:
        signalements.append(Signalement(
            NIVEAU_NON_CONFORME,
            "distance_bord_insuffisante",
            (
                f"Distance au bord {geometrie.distance_au_bord_mm:g} mm < "
                f"{bord_min:.0f} mm (hypothèse 2×Ø ou 25 mm, risque de fendage). "
                "Rapprocher l'ancre du bord améliore parfois l'ergonomie des "
                "bracelets mais affaiblit le bois : compromis à traiter par un "
                "bloc plus long, pas par un déplacement vers le chant visible."
            ),
            compromis=True,
        ))

    signalements.append(Signalement(
        NIVEAU_ESSAI_REQUIS,
        "essai_charge_reel",
        (
            "Modèle de validation simplifié (section uniforme, cisaillement "
            "à plans parallèles, valeurs d'essence approximatives, pas de k_mod "
            "ni de γ_M, pas d'effet dynamique). Un ingénieur doit reprendre le "
            "justificatif, et un essai de charge réel (statique puis avec à-coups, "
            "sur prototype, jusqu'à la charge de rupture visée au minimum) est "
            "obligatoire avant tout usage des ancrages."
        ),
    ))

    if all(s.niveau in {NIVEAU_OK, NIVEAU_AVERTISSEMENT, NIVEAU_ESSAI_REQUIS}
           for s in signalements):
        signalements.insert(0, Signalement(
            NIVEAU_OK,
            "ancrage_geometrie_acceptable",
            (
                f"Géométrie acceptable au sens du modèle simplifié "
                f"({essence.nom_affiche}, F_service={charges.charge_service_ancrage_n:.0f} N, "
                f"CS={charges.coefficient_securite:g}, "
                f"F_rupture visée={charges.charge_rupture_visee_ancrage_n:.0f} N, "
                f"paroi restante {paroi_dispo:.1f} mm ≥ {paroi_min:.1f} mm)."
            ),
        ))

    return RapportValidation(signalements=tuple(signalements))


def valider_charges(charges: ParametresCharge) -> RapportValidation:
    """Valide un jeu de paramètres de charge, hors géométrie d'ancre."""
    signalements: list[Signalement] = []
    if charges.coefficient_securite < COEFFICIENT_SECURITE_MIN_RECOMMANDE:
        signalements.append(Signalement(
            NIVEAU_NON_CONFORME,
            "cs_insuffisant",
            (
                f"Coefficient de sécurité {charges.coefficient_securite:g} < "
                f"{COEFFICIENT_SECURITE_MIN_RECOMMANDE:g} recommandé."
            ),
        ))
    signalements.append(Signalement(
        NIVEAU_ESSAI_REQUIS,
        "essai_charge_reel",
        (
            "Les charges de service (ancrage et appui) sont des hypothèses. "
            "Elles ne couvrent pas une chute, un effet de levier ou un usage "
            "dynamique sévère. Essai de charge réel obligatoire."
        ),
    ))
    return RapportValidation(signalements=tuple(signalements))


# ---------------------------------------------------------------------------
# Module de selle vibrante (pouf) : niveau de gamme
# ---------------------------------------------------------------------------

GAMME_SYBIAN_ENTREE = "entree"
GAMME_SYBIAN_HAUT = "haut"
TENSION_MODULE_V = 24.0
"""Tension unique autorisée dans le meuble : 24 V DC. L'alimentation
secteur certifiée reste *hors* du meuble. Aucun 230 V dans le caisson."""


@dataclass(frozen=True)
class ParametresSybian:
    """Niveau de gamme du module de selle vibrante intégré au pouf.

    ``gamme`` vaut ``entree`` (moteur à balourd 24 V sous carter mousse)
    ou ``haut`` (voice coil SUPT VCAR, silentblocs silicone, guidage à
    ressorts). Le basculement, via ``incognito.regles`` et la grammaire
    ``pouf_vibrant``, recalcule le logement moteur, les silentblocs
    (raideur, fréquence propre, transmissibilité) et les fixations
    (nombre, diamètre, entraxe) sur les ancrages internes.

    Dans Fusion, ``inc_sybian_gamme`` vaut 0 (entrée) ou 1 (haut).
    """

    gamme: str = GAMME_SYBIAN_HAUT
    tension_v: float = TENSION_MODULE_V

    def __post_init__(self) -> None:
        if self.gamme not in {GAMME_SYBIAN_ENTREE, GAMME_SYBIAN_HAUT}:
            raise ValueError(
                f"Gamme Sybian inconnue « {self.gamme} ». "
                f"Attendue : {GAMME_SYBIAN_ENTREE!r} ou {GAMME_SYBIAN_HAUT!r}."
            )
        if self.tension_v <= 0:
            raise ValueError("tension_v doit être > 0.")
        if self.tension_v > 48.0:
            raise ValueError(
                "Interdiction de faire entrer une tension réseau (230 V) "
                "dans le meuble. Rester en très basse tension (24 V DC, "
                "48 V max. de conception)."
            )

    @property
    def code_fusion(self) -> int:
        """0 = entrée, 1 = haut (paramètre utilisateur Fusion)."""
        return 1 if self.gamme == GAMME_SYBIAN_HAUT else 0

    @property
    def est_haut(self) -> bool:
        return self.gamme == GAMME_SYBIAN_HAUT

    @classmethod
    def depuis_code_fusion(cls, code: int, tension_v: float = TENSION_MODULE_V) -> "ParametresSybian":
        """Construit le paramètre depuis la valeur Fusion 0/1."""
        gamme = GAMME_SYBIAN_HAUT if int(code) else GAMME_SYBIAN_ENTREE
        return cls(gamme=gamme, tension_v=tension_v)


SYBIAN_DEFAUT = ParametresSybian()


# ---------------------------------------------------------------------------
# Jeu de paramètres globaux de la gamme
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ParametresGlobaux:
    """Jeu complet des paramètres de la couche 1, figé."""

    essence: Essence = CHENE
    revetement_exterieur: Revetement = VELOURS
    revetement_interieur: Revetement = CUIR_COGNAC
    discretion: ParametresDiscretion = DISCRETION_DEFAUT
    charges: ParametresCharge = CHARGES_DEFAUT
    ancre: GeometrieAncre = ANCRE_DEFAUT
    sybian: ParametresSybian = SYBIAN_DEFAUT

    def __post_init__(self) -> None:
        if not self.revetement_exterieur.conforme_discretions_defaut():
            # On autorise l'instanciation (dérogation) mais le rapport de
            # validation la signalera. Rien à lever ici.
            pass

    def valider(self) -> RapportValidation:
        """Valide charges, ancre, et la règle « zéro cuir visible »."""
        rapport_ancre = valider_ancrage(
            self.essence, self.ancre, self.charges, self.discretion
        )
        signaux = list(rapport_ancre.signalements)
        if not self.revetement_exterieur.conforme_discretions_defaut():
            signaux.append(Signalement(
                NIVEAU_AVERTISSEMENT,
                "cuir_visible_derogation",
                (
                    f"Le revêtement extérieur « {self.revetement_exterieur.nom_affiche} » "
                    "enfreint la règle de gamme « zéro cuir visible ». "
                    "Dérogation club classique uniquement, non retenue par défaut."
                ),
                compromis=True,
            ))
        if self.revetement_interieur.famille != "cuir":
            signaux.append(Signalement(
                NIVEAU_AVERTISSEMENT,
                "interieur_non_cuir",
                "Le revêtement du banc déployé n'est pas un cuir du catalogue "
                "(cognac ou noir). Vérifier le confort et l'entretien.",
            ))
        return RapportValidation(signalements=tuple(signaux))


PARAMETRES_DEFAUT = ParametresGlobaux()


# ---------------------------------------------------------------------------
# Export vers paramètres utilisateur Fusion 360
# dict nom -> (valeur, unité, commentaire)
# ---------------------------------------------------------------------------

def _entree(valeur: float, unite: str, commentaire: str) -> tuple[float, str, str]:
    return (float(valeur), unite, commentaire)


def vers_parametres_fusion(
    parametres: ParametresGlobaux | None = None,
    typologies: Mapping[str, TypologieSalon] | None = None,
) -> dict[str, tuple[float, str, str]]:
    """Convertit le vocabulaire Incognito en paramètres utilisateur Fusion.

    Les noms sont ASCII, préfixés par ``inc_`` pour éviter les collisions.
    Les longueurs restent en mm (Fusion accepte cette unité utilisateur ;
    la conversion en cm, unité interne de l'API, se fait dans
    ``incognito.fusion_outils`` et dans les scripts ``scripts_fusion/``).
    """
    parametres = parametres or PARAMETRES_DEFAUT
    typologies = dict(typologies) if typologies is not None else TYPOLOGIES

    out: dict[str, tuple[float, str, str]] = {}

    out["inc_essence_masse_volumique"] = _entree(
        parametres.essence.masse_volumique_kg_m3, UNITE_MASSE_VOLUMIQUE,
        f"Masse volumique approximative — {parametres.essence.nom_affiche}.",
    )
    out["inc_essence_E"] = _entree(
        parametres.essence.module_elasticite_mpa, UNITE_PRESSION,
        f"Module d'élasticité moyen approximatif — {parametres.essence.nom_affiche}.",
    )
    out["inc_essence_sigma_adm_flexion"] = _entree(
        parametres.essence.contrainte_admissible_flexion_mpa, UNITE_PRESSION,
        "Contrainte admissible en flexion (hypothèse mobilier, non réglementaire).",
    )
    out["inc_essence_tau_adm"] = _entree(
        parametres.essence.contrainte_admissible_cisaillement_mpa, UNITE_PRESSION,
        "Contrainte admissible en cisaillement (hypothèse mobilier, non réglementaire).",
    )

    out["inc_revetement_ext_epaisseur"] = _entree(
        parametres.revetement_exterieur.epaisseur_mm, UNITE_LONGUEUR,
        f"Épaisseur du revêtement de façade ({parametres.revetement_exterieur.nom_affiche}).",
    )
    out["inc_revetement_int_epaisseur"] = _entree(
        parametres.revetement_interieur.epaisseur_mm, UNITE_LONGUEUR,
        f"Épaisseur du revêtement caché ({parametres.revetement_interieur.nom_affiche}).",
    )

    d = parametres.discretion
    out["inc_retrait_min_ancre"] = _entree(
        d.retrait_min_ancre_sous_surface_mm, UNITE_LONGUEUR,
        "Retrait minimal de l'ancre sous toute surface visible à l'état fermé.",
    )
    out["inc_jeu_mecanique"] = _entree(
        d.jeu_mecanique_mm, UNITE_LONGUEUR,
        "Jeu fonctionnel des mécanismes (charnières, joues, trappes).",
    )
    out["inc_jeu_repli"] = _entree(
        d.jeu_repli_mm, UNITE_LONGUEUR,
        "Marge de repli du banc dans le caisson.",
    )
    out["inc_epaisseur_recouvrement_bois"] = _entree(
        d.epaisseur_recouvrement_bois_mm, UNITE_LONGUEUR,
        "Épaisseur typique d'un cache bois affleurant.",
    )
    out["inc_epaisseur_min_paroi_visible"] = _entree(
        d.epaisseur_min_paroi_visible_mm, UNITE_LONGUEUR,
        "Épaisseur minimale d'une paroi vue de l'extérieur.",
    )
    out["inc_charniere_recul_bord"] = _entree(
        d.mortaise_charniere_recul_bord_mm, UNITE_LONGUEUR,
        "Recul minimal d'une mortaise de charnière invisible par rapport au chant visible.",
    )

    c = parametres.charges
    out["inc_charge_service_ancrage"] = _entree(
        c.charge_service_ancrage_n, UNITE_FORCE,
        "Charge de service par ancrage (hypothèse, essai réel obligatoire).",
    )
    out["inc_charge_service_appui"] = _entree(
        c.charge_service_appui_n, UNITE_FORCE,
        "Charge de service verticale sur l'appui (hypothèse, essai réel obligatoire).",
    )
    out["inc_coefficient_securite"] = _entree(
        c.coefficient_securite, "",
        "Coefficient de sécurité (≥ 3 recommandé). Sans unité.",
    )
    out["inc_charge_rupture_visee_ancrage"] = _entree(
        c.charge_rupture_visee_ancrage_n, UNITE_FORCE,
        "Charge de rupture visée par ancrage = service × CS (cible, non certifiée).",
    )

    a = parametres.ancre
    out["inc_ancre_diametre"] = _entree(
        a.diametre_insert_mm, UNITE_LONGUEUR,
        "Diamètre de l'insert métallique d'ancrage.",
    )
    out["inc_ancre_encastrement"] = _entree(
        a.longueur_encastrement_mm, UNITE_LONGUEUR,
        "Longueur d'encastrement de l'insert dans le bloc.",
    )
    out["inc_ancre_bloc_epaisseur"] = _entree(
        a.epaisseur_bloc_mm, UNITE_LONGUEUR,
        "Épaisseur du bloc d'ancrage local (masqué sous le coussin caché).",
    )
    out["inc_ancre_bloc_largeur"] = _entree(
        a.largeur_bloc_mm, UNITE_LONGUEUR,
        "Largeur du bloc d'ancrage local.",
    )
    out["inc_ancre_bloc_longueur"] = _entree(
        a.longueur_bloc_mm, UNITE_LONGUEUR,
        "Longueur du bloc d'ancrage local.",
    )
    out["inc_ancre_recouvrement"] = _entree(
        a.epaisseur_recouvrement_mm, UNITE_LONGUEUR,
        "Épaisseur de recouvrement (cache) sur l'ancre.",
    )
    out["inc_ancre_distance_bord"] = _entree(
        a.distance_au_bord_mm, UNITE_LONGUEUR,
        "Distance de l'ancre au bord du bloc (anti-fendage).",
    )

    s = parametres.sybian
    out["inc_sybian_gamme"] = _entree(
        float(s.code_fusion), "",
        "Niveau de gamme du pouf vibrant : 0 entrée (balourd), 1 haut (voice coil). Sans unité.",
    )
    out["inc_sybian_tension"] = _entree(
        s.tension_v, "V",
        "Tension d'alimentation du module dans le meuble (24 V DC). Alim. secteur hors meuble.",
    )

    # Cotes typologiques, préfixe inc_<typologie>_<cote>
    for typo in typologies.values():
        for cote in typo.cotes:
            nom = f"inc_{typo.nom}_{cote.nom}"
            commentaire = (
                f"{typo.nom} — {cote.commentaire} "
                f"Plage [{cote.plage.minimum:g}–{cote.plage.maximum:g}] {cote.unite}."
            )
            out[nom] = _entree(cote.valeur, cote.unite, commentaire)

    return out
