# -*- coding: utf-8 -*-
"""Grammaire de la banquette Incognito (premier meuble de la gamme).

Banquette de salon classique : dossier, assise capitonnée, pieds
tournés / fuseaux, tissu sobre. Rien, à l'état fermé, ne trahit la
fonction. L'assise se soulève comme un coffre (charnières invisibles
type Soss + vérins de maintien) et un banc à fessée se déploie depuis
l'intérieur du caisson.

Deux états, calculés à partir des **mêmes** paramètres de base :

* ``Etat.FERMEE`` (0) : géométrie salon ;
* ``Etat.DEPLOYEE`` (1) : géométrie fonctionnelle (appui ~700 mm,
  longueur ~1150 mm, ancrages accessibles, cuir cognac ou noir).

Module Python pur, sans ``adsk``, testable hors Fusion.

Cotes du banc déployé : hypothèses documentées. Le squelette Equinox
disponible ne contenait pas les cotes du banc Feuille / Flore ; rien
n'a donc été repris.

Alternative écartée — dossier basculant ou coulissant
----------------------------------------------------
Un dossier qui bascule ou coulisse pour libérer le banc a été écarté
parce qu'il est moins solide et moins discret :

* le dossier est un cadre relativement léger (panneau mince + montants),
  pas une boîte de torsion comme le caisson ; les efforts de charnière
  s'appliqueraient à ce cadre, avec un bras de levier long, au risque
  de déverser les assemblages dossier / caisson ;
* un coulissement impose un jeu, un rail ou une lumière : indices
  visibles en façade, et section restante du traversin arrière
  affaiblie par le mécanisme ;
* le dossier ouvert ne fournit pas une base large et basse au banc
  déployé, contrairement au caisson qui reste en place.

L'ouverture en coffre conserve la boîte structurelle intacte, appuie
les charnières invisibles dans le traversin arrière (section généreuse)
et sort le couvercle du chemin de charge du banc.

Compromis et essais
-------------------
Voir ``docs/banquette.md``. En particulier : un rail d'assise de 28 mm
ne peut pas noyer une ancre 1500 N / CS 3 en conservant le retrait de
discrétion — d'où des blocs d'ancrage locaux masqués sous le cuir.
La stabilité au basculement sous traction horizontale sur un ancrage
est insuffisante sans béquille avant déployée (et même avec, un essai
réel reste obligatoire).
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum
from math import cos, radians, sin

from incognito.catalogues.essences import essence_par_nom
from incognito.catalogues.revetements import revetement_par_nom
from incognito.parametres import (
    ANCRE_DEFAUT,
    BANQUETTE,
    CHARGES_DEFAUT,
    CHENE,
    COEFFICIENT_SECURITE_MIN_RECOMMANDE,
    CUIR_COGNAC,
    DISCRETION_DEFAUT,
    NIVEAU_AVERTISSEMENT,
    NIVEAU_ESSAI_REQUIS,
    NIVEAU_NON_CONFORME,
    NIVEAU_OK,
    VELOURS,
    Essence,
    GeometrieAncre,
    ParametresCharge,
    ParametresDiscretion,
    ParametresGlobaux,
    Revetement,
    Signalement,
    valider_ancrage,
)
from incognito.regles import epaisseur_rail_insuffisante, recaler_bloc_ancrage


class Etat(IntEnum):
    """État géométrique de la banquette."""

    FERMEE = 0
    DEPLOYEE = 1


# Masse volumique indicative des mousses de garnissage (kg/m³).
MASSE_VOLUMIQUE_MOUSSE_KG_M3 = 40.0
# Acier du lest caché dans le fond du caisson.
MASSE_VOLUMIQUE_ACIER_KG_M3 = 7850.0
# Coefficient de stabilité au basculement en deçà duquel on signale.
COEFFICIENT_STABILITE_MIN = 1.5


@dataclass(frozen=True)
class ParametresBanquette:
    """Paramètres de base de la banquette (communs aux deux états).

    Toutes les longueurs sont en mm. Les cotes hors-tout d'apparence
    salon restent dans les plages de ``incognito.parametres.BANQUETTE``.
    """

    longueur: float = 1300.0
    profondeur: float = 680.0
    hauteur_assise: float = 430.0
    hauteur_dossier: float = 880.0
    hauteur_pieds: float = 120.0

    diametre_pied_haut: float = 55.0
    diametre_pied_bas: float = 32.0
    retrait_pieds: float = 40.0

    epaisseur_paroi: float = 22.0
    epaisseur_fond: float = 18.0
    epaisseur_couvercle: float = 22.0
    epaisseur_dossier_panneau: float = 22.0

    epaisseur_mousse_assise: float = 80.0
    epaisseur_mousse_dossier: float = 70.0

    longueur_appui: float = 1150.0
    largeur_appui: float = 320.0
    hauteur_appui: float = 700.0
    epaisseur_panneau_banc: float = 28.0
    epaisseur_mousse_banc: float = 30.0
    epaisseur_joue: float = 32.0
    largeur_joue: float = 280.0
    epaisseur_traverse: float = 22.0
    hauteur_traverse: float = 80.0

    appui_joues_au_sol: bool = True
    """Si True, les joues traversent le fond du caisson (trappes
    affleurantes) et prennent appui au sol : chemin de charge direct.
    Si False, elles reposent sur le fond du caisson (plus simple, mais
    le fond et ses assemblages doivent tout reprendre)."""

    avec_bequille_avant: bool = True
    """Béquille / appuie-genoux déployable vers l'avant, recommandé
    pour la stabilité au basculement. Entièrement rangé dans le caisson
    à l'état fermé."""

    portee_bequille: float = 400.0
    hauteur_appuie_genoux: float = 300.0
    epaisseur_appuie_genoux: float = 22.0
    profondeur_appuie_genoux: float = 300.0
    longueur_appuie_genoux: float = 800.0

    angle_ouverture_couvercle_deg: float = 95.0
    nombre_charnieres_soss: int = 3
    nombre_verins: int = 2
    nombre_ancrages: int = 4

    masse_lest_kg: float = 10.0
    """Lest acier caché sur le fond du caisson, invisible à l'état fermé."""

    essence: Essence = CHENE
    revetement_exterieur: Revetement = VELOURS
    revetement_banc: Revetement = CUIR_COGNAC
    discretion: ParametresDiscretion = DISCRETION_DEFAUT
    charges: ParametresCharge = CHARGES_DEFAUT
    ancre: GeometrieAncre = ANCRE_DEFAUT

    def __post_init__(self) -> None:
        # default_factory for VELOURS is awkward; if None slipped in, fail clearly.
        if self.longueur_appui + 2.0 * self.epaisseur_paroi > self.longueur:
            raise ValueError(
                f"Longueur hors-tout {self.longueur} mm insuffisante pour "
                f"loger un appui de {self.longueur_appui} mm plus deux parois "
                f"de {self.epaisseur_paroi} mm."
            )
        if self.hauteur_appui <= self.hauteur_assise:
            raise ValueError(
                "La hauteur d'appui du banc déployé doit dépasser la hauteur "
                "d'assise de la banquette."
            )
        if self.nombre_ancrages < 2:
            raise ValueError("Prévoir au moins deux ancrages.")


def parametres_banquette_defaut(
    globaux: ParametresGlobaux | None = None,
    **override: object,
) -> ParametresBanquette:
    """Construit un jeu de paramètres banquette depuis les globaux de la couche 1."""
    typo = BANQUETTE
    globaux = globaux or ParametresGlobaux()
    valeurs = dict(
        longueur=typo.cote("longueur").valeur,
        profondeur=typo.cote("profondeur_hors_tout").valeur,
        hauteur_assise=typo.cote("hauteur_assise").valeur,
        hauteur_dossier=typo.cote("hauteur_dossier").valeur,
        hauteur_pieds=typo.cote("hauteur_pieds").valeur,
        longueur_appui=typo.cote("longueur_appui_banc").valeur,
        largeur_appui=typo.cote("largeur_appui_banc").valeur,
        hauteur_appui=typo.cote("hauteur_appui_banc").valeur,
        essence=globaux.essence,
        revetement_exterieur=globaux.revetement_exterieur,
        revetement_banc=globaux.revetement_interieur,
        discretion=globaux.discretion,
        charges=globaux.charges,
        ancre=globaux.ancre,
    )
    valeurs.update(override)
    return ParametresBanquette(**valeurs)  # type: ignore[arg-type]


@dataclass(frozen=True)
class Boite:
    """Boîte alignée sur les axes, en mm (coin inférieur avant-gauche + dimensions)."""

    x: float
    y: float
    z: float
    dx: float
    dy: float
    dz: float

    @property
    def coin_max(self) -> tuple[float, float, float]:
        return (self.x + self.dx, self.y + self.dy, self.z + self.dz)

    @property
    def centre(self) -> tuple[float, float, float]:
        return (self.x + self.dx / 2.0, self.y + self.dy / 2.0, self.z + self.dz / 2.0)

    def volume_mm3(self) -> float:
        return max(0.0, self.dx) * max(0.0, self.dy) * max(0.0, self.dz)

    def volume_m3(self) -> float:
        return self.volume_mm3() / 1e9

    def rentre_dans(self, contenant: "Boite", jeu: float = 0.0) -> bool:
        """Compare les encombrements (pas les positions)."""
        return (
            self.dx + jeu <= contenant.dx
            and self.dy + jeu <= contenant.dy
            and self.dz + jeu <= contenant.dz
        )


@dataclass(frozen=True)
class Piece:
    """Pièce de la grammaire, positionnée dans l'état courant."""

    nom: str
    role: str
    boite: Boite
    materiau: str
    visible_exterieur_si_fermee: bool
    angle_deg: float = 0.0
    axe_rotation: tuple[float, float, float] | None = None
    commentaire: str = ""


@dataclass(frozen=True)
class Assemblage:
    """Jonction, charnière, ancre ou lumière, décrite géométriquement."""

    nom: str
    type: str
    pieces: tuple[str, ...]
    origine: tuple[float, float, float]
    cotes_mm: tuple[tuple[str, float], ...]
    visible_etat_ferme: bool
    commentaire: str = ""


@dataclass(frozen=True)
class Verification:
    """Résultat d'une vérification de la grammaire."""

    code: str
    ok: bool
    niveau: str
    message: str
    compromis: bool = False


@dataclass(frozen=True)
class DimensionsDerivees:
    """Cotes dérivées du caisson, du couvercle et du banc."""

    hauteur_caisson: float
    hauteur_interieure: float
    longueur_interieure: float
    profondeur_interieure: float
    profondeur_caisson: float
    z_dessus_pieds: float
    z_dessus_fond: float
    z_dessus_caisson: float
    z_dessus_couvercle: float
    z_dessus_panneau_banc: float
    hauteur_joue: float
    epaisseur_cuir: float
    epaisseur_tissu: float
    axe_charniere: tuple[float, float, float]


def deriver(params: ParametresBanquette) -> DimensionsDerivees:
    """Calcule les cotes dérivées ; lève si la pile d'assise est incohérente."""
    ep_tissu = params.revetement_exterieur.epaisseur_mm
    ep_cuir = params.revetement_banc.epaisseur_mm
    hauteur_caisson = (
        params.hauteur_assise
        - params.epaisseur_mousse_assise
        - ep_tissu
        - params.epaisseur_couvercle
        - params.hauteur_pieds
    )
    if hauteur_caisson <= params.epaisseur_fond + 20.0:
        raise ValueError(
            f"Hauteur de caisson dérivée trop faible ({hauteur_caisson:.1f} mm). "
            "Réduire la mousse, les pieds ou le couvercle, ou monter l'assise."
        )
    profondeur_caisson = params.profondeur - params.epaisseur_dossier_panneau
    longueur_interieure = params.longueur - 2.0 * params.epaisseur_paroi
    profondeur_interieure = profondeur_caisson - params.epaisseur_paroi
    # Le panneau arrière (dossier) forme la paroi arrière : l'intérieur
    # s'arrête à sa face avant.
    hauteur_interieure = hauteur_caisson - params.epaisseur_fond
    z_dessus_pieds = params.hauteur_pieds
    z_dessus_fond = params.hauteur_pieds + params.epaisseur_fond
    z_dessus_caisson = params.hauteur_pieds + hauteur_caisson
    z_dessus_couvercle = z_dessus_caisson + params.epaisseur_couvercle
    ep_pad_banc = params.epaisseur_mousse_banc + ep_cuir
    z_dessus_panneau_banc = params.hauteur_appui - ep_pad_banc
    z_dessous_panneau_banc = z_dessus_panneau_banc - params.epaisseur_panneau_banc
    if params.appui_joues_au_sol:
        hauteur_joue = z_dessous_panneau_banc  # du sol au dessous du panneau
    else:
        hauteur_joue = z_dessous_panneau_banc - z_dessus_fond
        if hauteur_joue <= 40.0:
            raise ValueError("Joues trop courtes si elles reposent sur le fond.")
    axe_charniere = (
        params.longueur / 2.0,
        profondeur_caisson,  # face avant du panneau dossier = chant arrière du couvercle
        z_dessus_caisson,
    )
    return DimensionsDerivees(
        hauteur_caisson=hauteur_caisson,
        hauteur_interieure=hauteur_interieure,
        longueur_interieure=longueur_interieure,
        profondeur_interieure=profondeur_interieure,
        profondeur_caisson=profondeur_caisson,
        z_dessus_pieds=z_dessus_pieds,
        z_dessus_fond=z_dessus_fond,
        z_dessus_caisson=z_dessus_caisson,
        z_dessus_couvercle=z_dessus_couvercle,
        z_dessus_panneau_banc=z_dessus_panneau_banc,
        hauteur_joue=hauteur_joue,
        epaisseur_cuir=ep_cuir,
        epaisseur_tissu=ep_tissu,
        axe_charniere=axe_charniere,
    )


def caisson_interieur(params: ParametresBanquette, derivees: DimensionsDerivees | None = None) -> Boite:
    """Volume intérieur utile du caisson (sous le couvercle)."""
    d = derivees or deriver(params)
    return Boite(
        x=params.epaisseur_paroi,
        y=params.epaisseur_paroi,
        z=d.z_dessus_fond,
        dx=d.longueur_interieure,
        dy=d.profondeur_interieure,
        dz=d.hauteur_interieure,
    )


def encombrement_banc_replie(params: ParametresBanquette, derivees: DimensionsDerivees | None = None) -> Boite:
    """Encombrement (dimensions seules) du banc et de ses joues une fois repliés.

    Les deux joues sont couchées sur le panneau, éventuellement
    superposées au milieu ; la traverse se loge dans l'épaisseur des joues.
    L'origine est conventionnelle (0, 0, 0) : on compare les dimensions
    avec ``Boite.rentre_dans``.
    """
    d = derivees or deriver(params)
    jeu = params.discretion.jeu_mecanique_mm
    # Chevauchement éventuel des joues : 2 × hauteur_joue peut dépasser
    # longueur_appui, d'où une surépaisseur locale d'une joue.
    chevauchement = 2.0 * d.hauteur_joue - params.longueur_appui
    sur_hauteur_joue = params.epaisseur_joue if chevauchement > 0 else 0.0
    dx = max(params.longueur_appui, d.hauteur_joue) + jeu
    dy = max(params.largeur_appui, params.largeur_joue) + jeu
    dz = (
        params.epaisseur_panneau_banc
        + params.epaisseur_mousse_banc
        + d.epaisseur_cuir
        + params.epaisseur_joue
        + sur_hauteur_joue
        + jeu
    )
    return Boite(0.0, 0.0, 0.0, dx, dy, dz)


def encombrement_bequille_repliee(params: ParametresBanquette) -> Boite:
    """Encombrement de la béquille / appuie-genoux replié."""
    jeu = params.discretion.jeu_mecanique_mm
    return Boite(
        0.0, 0.0, 0.0,
        params.longueur_appuie_genoux + jeu,
        params.profondeur_appuie_genoux + jeu,
        params.epaisseur_appuie_genoux + 2.0 * params.epaisseur_paroi + jeu,
    )


def _tourner_yz(
    y: float,
    z: float,
    y0: float,
    z0: float,
    angle_deg: float,
) -> tuple[float, float]:
    """Rotation autour d'un axe parallèle à X (signe : ouverture du couvercle)."""
    theta = radians(angle_deg)
    dy, dz = y - y0, z - z0
    # Signe négatif : le chant avant (y < y0) se lève vers +Z puis vers l'arrière.
    c, s = cos(theta), sin(theta)
    # Rotation d'angle -theta dans le plan (y, z).
    y2 = y0 + dy * c + dz * s
    z2 = z0 - dy * s + dz * c
    return y2, z2


def _aabb_couvercle_ouvert(couvercle: Boite, axe: tuple[float, float, float], angle_deg: float) -> Boite:
    """AABB du couvercle après rotation autour de l'axe de charnière."""
    coins = [
        (couvercle.y, couvercle.z),
        (couvercle.y + couvercle.dy, couvercle.z),
        (couvercle.y, couvercle.z + couvercle.dz),
        (couvercle.y + couvercle.dy, couvercle.z + couvercle.dz),
    ]
    transformes = [_tourner_yz(y, z, axe[1], axe[2], angle_deg) for y, z in coins]
    ys = [p[0] for p in transformes]
    zs = [p[1] for p in transformes]
    y_min, z_min = min(ys), min(zs)
    return Boite(
        x=couvercle.x,
        y=y_min,
        z=z_min,
        dx=couvercle.dx,
        dy=max(ys) - y_min,
        dz=max(zs) - z_min,
    )


def _pieces_et_assemblages(
    etat: Etat,
    params: ParametresBanquette,
    derivees: DimensionsDerivees,
) -> tuple[tuple[Piece, ...], tuple[Assemblage, ...]]:
    d = derivees
    essence = params.essence.nom
    tissus = params.revetement_exterieur.nom
    cuir = params.revetement_banc.nom
    interieur = caisson_interieur(params, d)
    ouvert = etat is Etat.DEPLOYEE
    pieces: list[Piece] = []
    assemblages: list[Assemblage] = []

    def ajouter(
        nom: str,
        role: str,
        boite: Boite,
        materiau: str,
        visible_fermee: bool,
        commentaire: str = "",
        angle: float = 0.0,
        axe: tuple[float, float, float] | None = None,
    ) -> None:
        pieces.append(Piece(
            nom=nom, role=role, boite=boite, materiau=materiau,
            visible_exterieur_si_fermee=visible_fermee,
            angle_deg=angle, axe_rotation=axe, commentaire=commentaire,
        ))

    # --- Pieds tournés / fuseaux (enveloppe cylindrique) --------------------
    r = params.retrait_pieds
    emprises = (
        ("pied_avg", r - params.diametre_pied_haut / 2.0, r - params.diametre_pied_haut / 2.0),
        ("pied_avd", params.longueur - r - params.diametre_pied_haut / 2.0, r - params.diametre_pied_haut / 2.0),
        ("pied_arg", r - params.diametre_pied_haut / 2.0, d.profondeur_caisson - r - params.diametre_pied_haut / 2.0),
        ("pied_ard", params.longueur - r - params.diametre_pied_haut / 2.0,
         d.profondeur_caisson - r - params.diametre_pied_haut / 2.0),
    )
    for nom, x, y in emprises:
        ajouter(
            nom, "pied",
            Boite(x, y, 0.0, params.diametre_pied_haut, params.diametre_pied_haut, params.hauteur_pieds),
            essence, True,
            "Pied tourné / fuseau ; l'enveloppe est le diamètre supérieur. "
            "Le profil de tournage (bagues, conicité) est laissé à l'ébénisterie.",
        )
        assemblages.append(Assemblage(
            nom=f"tourillons_{nom}",
            type="tourillon",
            pieces=(nom, "caisson_panneau_g" if "g" in nom else "caisson_panneau_d"),
            origine=(x + params.diametre_pied_haut / 2.0, y + params.diametre_pied_haut / 2.0, d.z_dessus_pieds),
            cotes_mm=(("diametre", 12.0), ("longueur", 50.0), ("nombre", 2.0)),
            visible_etat_ferme=False,
            commentaire="Deux tourillons Ø12 encollés, pied dans le caisson.",
        ))

    # --- Caisson ------------------------------------------------------------
    ajouter(
        "caisson_panneau_av", "caisson",
        Boite(0.0, 0.0, d.z_dessus_pieds, params.longueur, params.epaisseur_paroi, d.hauteur_caisson),
        essence, True, "Paroi avant du caisson.",
    )
    ajouter(
        "caisson_panneau_g", "caisson",
        Boite(0.0, 0.0, d.z_dessus_pieds, params.epaisseur_paroi, d.profondeur_caisson, d.hauteur_caisson),
        essence, True, "Paroi gauche du caisson.",
    )
    ajouter(
        "caisson_panneau_d", "caisson",
        Boite(params.longueur - params.epaisseur_paroi, 0.0, d.z_dessus_pieds,
              params.epaisseur_paroi, d.profondeur_caisson, d.hauteur_caisson),
        essence, True, "Paroi droite du caisson.",
    )
    # Panneau arrière continu : caisson + dossier (plus solide qu'un raccord).
    ajouter(
        "panneau_arriere_dossier", "dossier",
        Boite(
            0.0, d.profondeur_caisson, d.z_dessus_pieds,
            params.longueur, params.epaisseur_dossier_panneau,
            params.hauteur_dossier - params.hauteur_pieds,
        ),
        essence, True,
        "Panneau arrière unique (paroi de caisson et dossier). "
        "Évite un raccord faible au niveau de l'assise.",
    )
    ajouter(
        "caisson_fond", "caisson",
        Boite(
            params.epaisseur_paroi, params.epaisseur_paroi, d.z_dessus_pieds,
            d.longueur_interieure, d.profondeur_interieure, params.epaisseur_fond,
        ),
        essence, False,
        "Fond du caisson, rainé dans les parois. Non visible de face ; "
        "vu du sol seulement si l'on se penche sous le meuble.",
    )

    assemblages.append(Assemblage(
        nom="assemblage_caisson_av_g",
        type="tourillon",
        pieces=("caisson_panneau_av", "caisson_panneau_g"),
        origine=(params.epaisseur_paroi, params.epaisseur_paroi, d.z_dessus_pieds + d.hauteur_caisson / 2.0),
        cotes_mm=(("diametre", 10.0), ("longueur", 40.0), ("nombre", 3.0)),
        visible_etat_ferme=False,
        commentaire="Tourillons Ø10 parois avant / côté, encollés.",
    ))
    assemblages.append(Assemblage(
        nom="mortaise_fond",
        type="mortaise_tenon",
        pieces=("caisson_fond", "caisson_panneau_av", "caisson_panneau_g", "caisson_panneau_d", "panneau_arriere_dossier"),
        origine=(params.epaisseur_paroi, params.epaisseur_paroi, d.z_dessus_pieds),
        cotes_mm=(("profondeur_raine", 8.0), ("epaisseur_fond", params.epaisseur_fond)),
        visible_etat_ferme=False,
        commentaire="Fond rainé dans les parois (équivalent mortaise continue).",
    ))

    # --- Lest caché ---------------------------------------------------------
    if params.masse_lest_kg > 0:
        # Plaque posée sur le fond, à l'intérieur, moins large que le banc replié.
        surface_m2 = 0.8 * 0.35
        ep_lest_m = (params.masse_lest_kg / MASSE_VOLUMIQUE_ACIER_KG_M3) / surface_m2
        ep_lest = ep_lest_m * 1000.0
        ajouter(
            "lest", "lest",
            Boite(
                (params.longueur - 800.0) / 2.0,
                params.epaisseur_paroi + 20.0,
                d.z_dessus_fond,
                800.0, 350.0, max(ep_lest, 2.0),
            ),
            "acier", False,
            f"Lest acier d'environ {params.masse_lest_kg:g} kg, invisible à l'état fermé.",
        )

    # --- Couvercle et capiton d'assise --------------------------------------
    couvercle_ferme = Boite(
        0.0, 0.0, d.z_dessus_caisson,
        params.longueur, d.profondeur_caisson, params.epaisseur_couvercle,
    )
    mousse_assise_fermee = Boite(
        0.0, 0.0, d.z_dessus_couvercle,
        params.longueur, d.profondeur_caisson,
        params.epaisseur_mousse_assise + d.epaisseur_tissu,
    )
    if ouvert:
        angle = params.angle_ouverture_couvercle_deg
        couvercle_boite = _aabb_couvercle_ouvert(couvercle_ferme, d.axe_charniere, angle)
        mousse_boite = _aabb_couvercle_ouvert(mousse_assise_fermee, d.axe_charniere, angle)
        axe = d.axe_charniere
    else:
        angle = 0.0
        couvercle_boite = couvercle_ferme
        mousse_boite = mousse_assise_fermee
        axe = d.axe_charniere
    ajouter(
        "assise_couvercle", "couvercle",
        couvercle_boite, essence, True,
        "Panneau d'assise formant couvercle de coffre. Charnières Soss au chant arrière.",
        angle=angle, axe=axe,
    )
    ajouter(
        "coussin_assise", "coussin_exterieur",
        mousse_boite, tissus, True,
        "Capiton d'assise et tissu de façade, solidaires du couvercle.",
        angle=angle, axe=axe,
    )

    # Charnières Soss : réparties sur la longueur, dans le chant arrière.
    for i in range(params.nombre_charnieres_soss):
        fraction = (i + 1) / (params.nombre_charnieres_soss + 1)
        x_s = fraction * params.longueur
        assemblages.append(Assemblage(
            nom=f"charniere_soss_{i + 1}",
            type="charniere_soss",
            pieces=("assise_couvercle", "panneau_arriere_dossier"),
            origine=(x_s, d.axe_charniere[1], d.axe_charniere[2]),
            cotes_mm=(("longueur_boitier", 118.0), ("profondeur_mortaise", 19.0)),
            visible_etat_ferme=False,
            commentaire="Charnière invisible entièrement mortaisée.",
        ))
    for i in range(params.nombre_verins):
        x_v = params.epaisseur_paroi + 80.0 if i == 0 else params.longueur - params.epaisseur_paroi - 80.0
        assemblages.append(Assemblage(
            nom=f"verin_{i + 1}",
            type="verin",
            pieces=("assise_couvercle", "caisson_panneau_g" if i == 0 else "caisson_panneau_d"),
            origine=(x_v, params.epaisseur_paroi + 40.0, d.z_dessus_fond + 40.0),
            cotes_mm=(("course", 150.0),),
            visible_etat_ferme=False,
            commentaire="Vérin ou compas de maintien, entièrement dans le caisson à l'état fermé.",
        ))

    # --- Dossier capitonné (au-dessus de l'assise) --------------------------
    ajouter(
        "coussin_dossier", "coussin_exterieur",
        Boite(
            0.0,
            d.profondeur_caisson - params.epaisseur_mousse_dossier - d.epaisseur_tissu,
            params.hauteur_assise,
            params.longueur,
            params.epaisseur_mousse_dossier + d.epaisseur_tissu,
            params.hauteur_dossier - params.hauteur_assise,
        ),
        tissus, True,
        "Capiton de dossier, tissu de façade. Rien n'y est ancré.",
    )

    # --- Banc déployable ----------------------------------------------------
    # Position FERMEE : pack centré dans le caisson, au-dessus du lest.
    pack = encombrement_banc_replie(params, d)
    x_pack = interieur.x + (interieur.dx - pack.dx) / 2.0
    y_pack = interieur.y + 10.0
    z_pack = interieur.z + 8.0  # au-dessus du lest

    x_banc_centre = (params.longueur - params.longueur_appui) / 2.0
    y_banc_centre = (
        params.epaisseur_paroi
        + (d.profondeur_interieure - params.largeur_appui) / 2.0
    )
    x_joue_g = x_banc_centre
    x_joue_d = x_banc_centre + params.longueur_appui - params.epaisseur_joue
    y_joue = y_banc_centre + (params.largeur_appui - params.largeur_joue) / 2.0
    z_joue_deployee = 0.0 if params.appui_joues_au_sol else d.z_dessus_fond

    if ouvert:
        boite_panneau = Boite(
            x_banc_centre, y_banc_centre,
            d.z_dessus_panneau_banc - params.epaisseur_panneau_banc,
            params.longueur_appui, params.largeur_appui, params.epaisseur_panneau_banc,
        )
        boite_coussin = Boite(
            x_banc_centre, y_banc_centre,
            d.z_dessus_panneau_banc,
            params.longueur_appui, params.largeur_appui,
            params.epaisseur_mousse_banc + d.epaisseur_cuir,
        )
        boite_joue_g = Boite(
            x_joue_g, y_joue, z_joue_deployee,
            params.epaisseur_joue, params.largeur_joue, d.hauteur_joue,
        )
        boite_joue_d = Boite(
            x_joue_d, y_joue, z_joue_deployee,
            params.epaisseur_joue, params.largeur_joue, d.hauteur_joue,
        )
        z_traverse = z_joue_deployee + d.hauteur_joue * 0.45
        boite_traverse = Boite(
            x_joue_g + params.epaisseur_joue, y_joue + 20.0, z_traverse,
            params.longueur_appui - 2.0 * params.epaisseur_joue,
            params.epaisseur_traverse, params.hauteur_traverse,
        )
    else:
        # Replié : panneau au fond du pack, coussin dessus, joues couchées.
        boite_panneau = Boite(x_pack, y_pack, z_pack, params.longueur_appui, params.largeur_appui, params.epaisseur_panneau_banc)
        z_c = z_pack + params.epaisseur_panneau_banc
        boite_coussin = Boite(
            x_pack, y_pack, z_c,
            params.longueur_appui, params.largeur_appui,
            params.epaisseur_mousse_banc + d.epaisseur_cuir,
        )
        z_j = z_c + params.epaisseur_mousse_banc + d.epaisseur_cuir
        # Joues couchées (hauteur_joue selon X, épaisseur selon Z).
        boite_joue_g = Boite(x_pack, y_pack, z_j, d.hauteur_joue, params.largeur_joue, params.epaisseur_joue)
        boite_joue_d = Boite(
            x_pack + params.longueur_appui - d.hauteur_joue,
            y_pack, z_j, d.hauteur_joue, params.largeur_joue, params.epaisseur_joue,
        )
        boite_traverse = Boite(
            x_pack + 20.0, y_pack + 10.0, z_j,
            params.longueur_appui - 40.0, params.epaisseur_traverse, params.epaisseur_traverse,
        )

    ajouter("banc_panneau", "banc", boite_panneau, essence, False, "Panneau d'appui du banc déployable.")
    ajouter(
        "banc_coussin_cuir", "coussin_interieur", boite_coussin, cuir, False,
        "Coussin cuir du banc (cognac ou noir), uniquement visible une fois déployé.",
    )
    ajouter("banc_joue_g", "banc", boite_joue_g, essence, False, "Joue gauche du banc, appui au sol ou sur le fond.")
    ajouter("banc_joue_d", "banc", boite_joue_d, essence, False, "Joue droite du banc.")
    ajouter(
        "banc_traverse", "banc", boite_traverse, essence, False,
        "Traverse haute entre les joues, mortaisée, contre le déversement du cadre.",
    )

    assemblages.append(Assemblage(
        nom="mortaise_traverse_joue_g",
        type="mortaise_tenon",
        pieces=("banc_traverse", "banc_joue_g"),
        origine=(boite_joue_g.x + boite_joue_g.dx, boite_traverse.y, boite_traverse.z),
        cotes_mm=(("epaisseur_tenon", 10.0), ("longueur_tenon", 24.0)),
        visible_etat_ferme=False,
        commentaire="Tenon de traverse dans la joue gauche.",
    ))
    assemblages.append(Assemblage(
        nom="mortaise_traverse_joue_d",
        type="mortaise_tenon",
        pieces=("banc_traverse", "banc_joue_d"),
        origine=(boite_joue_d.x, boite_traverse.y, boite_traverse.z),
        cotes_mm=(("epaisseur_tenon", 10.0), ("longueur_tenon", 24.0)),
        visible_etat_ferme=False,
        commentaire="Tenon de traverse dans la joue droite.",
    ))

    if params.appui_joues_au_sol:
        for nom_lum, x_l in (("lumiere_fond_g", x_joue_g), ("lumiere_fond_d", x_joue_d)):
            assemblages.append(Assemblage(
                nom=nom_lum,
                type="lumiere_fond",
                pieces=("caisson_fond", "banc_joue_g" if nom_lum.endswith("_g") else "banc_joue_d"),
                origine=(x_l, y_joue, d.z_dessus_pieds),
                cotes_mm=(
                    ("dx", params.epaisseur_joue + 2.0 * params.discretion.jeu_mecanique_mm),
                    ("dy", params.largeur_joue + 2.0 * params.discretion.jeu_mecanique_mm),
                ),
                visible_etat_ferme=False,
                commentaire=(
                    "Lumière dans le fond, obturée par une trappe affleurante "
                    "à l'état fermé. Permet l'appui de la joue au sol."
                ),
            ))
            if not ouvert:
                ajouter(
                    f"trappe_{nom_lum}", "trappe",
                    Boite(
                        x_l, y_joue, d.z_dessus_pieds,
                        params.epaisseur_joue, params.largeur_joue, params.epaisseur_fond,
                    ),
                    essence, False,
                    "Trappe affleurante obturant la lumière du fond à l'état fermé.",
                )

    # --- Blocs d'ancrage et ancrages ----------------------------------------
    # Recalage recommandé : on place 4 blocs sous le coussin, près des coins.
    recalage = recaler_bloc_ancrage(params.essence, params.charges, params.discretion)
    bloc = recalage.geometrie
    # Positions locales sur le panneau (inset).
    inset_x = max(bloc.distance_au_bord_mm, 40.0)
    inset_y = max((params.largeur_appui - bloc.largeur_bloc_mm) / 2.0, 10.0)
    positions_blocs = (
        ("av_g", inset_x, inset_y),
        ("av_d", inset_x, params.largeur_appui - inset_y - bloc.largeur_bloc_mm),
        ("ar_g", params.longueur_appui - inset_x - bloc.longueur_bloc_mm, inset_y),
        ("ar_d", params.longueur_appui - inset_x - bloc.longueur_bloc_mm,
         params.largeur_appui - inset_y - bloc.largeur_bloc_mm),
    )
    for suffixe, dx_b, dy_b in positions_blocs[: params.nombre_ancrages]:
        if ouvert:
            boite_bloc = Boite(
                boite_panneau.x + dx_b,
                boite_panneau.y + dy_b,
                boite_panneau.z - (bloc.epaisseur_bloc_mm - params.epaisseur_panneau_banc),
                bloc.longueur_bloc_mm, bloc.largeur_bloc_mm, bloc.epaisseur_bloc_mm,
            )
        else:
            # Sous le panneau rangé, toujours dans le caisson.
            boite_bloc = Boite(
                boite_panneau.x + dx_b,
                boite_panneau.y + dy_b,
                boite_panneau.z,  # dans l'épaisseur / juste contre, masqué
                bloc.longueur_bloc_mm, bloc.largeur_bloc_mm,
                min(bloc.epaisseur_bloc_mm, params.epaisseur_panneau_banc),
            )
        ajouter(
            f"bloc_ancrage_{suffixe}", "ancrage",
            boite_bloc, essence, False,
            "Bloc d'ancrage local recalculé, masqué sous le cuir du banc.",
        )
        assemblages.append(Assemblage(
            nom=f"ancre_{suffixe}",
            type="ancre",
            pieces=(f"bloc_ancrage_{suffixe}", "banc_panneau"),
            origine=boite_bloc.centre,
            cotes_mm=(
                ("diametre_insert", bloc.diametre_insert_mm),
                ("encastrement", bloc.longueur_encastrement_mm),
                ("recouvrement", bloc.epaisseur_recouvrement_mm),
            ),
            visible_etat_ferme=False,
            commentaire="Insert métallique noyé, cache affleurant, invisible à l'état fermé.",
        ))
        assemblages.append(Assemblage(
            nom=f"tourillons_bloc_{suffixe}",
            type="tourillon",
            pieces=(f"bloc_ancrage_{suffixe}", "banc_panneau"),
            origine=boite_bloc.centre,
            cotes_mm=(("diametre", 12.0), ("longueur", 50.0), ("nombre", 4.0)),
            visible_etat_ferme=False,
            commentaire="Tourillons Ø12 et collage du bloc sous le panneau d'appui.",
        ))

    # --- Béquille / appuie-genoux ------------------------------------------
    if params.avec_bequille_avant:
        if ouvert:
            # y = -portée : l'appuie-genoux s'étend de -portée à -portée + profondeur,
            # donc bien 400 mm en avant de la face avant (y = 0).
            y_beq = -params.portee_bequille
            ajouter(
                "appuie_genoux", "bequille",
                Boite(
                    (params.longueur - params.longueur_appuie_genoux) / 2.0,
                    y_beq,
                    params.hauteur_appuie_genoux - params.epaisseur_appuie_genoux,
                    params.longueur_appuie_genoux, params.profondeur_appuie_genoux,
                    params.epaisseur_appuie_genoux,
                ),
                essence, False,
                "Appuie-genoux déployé en avant de la banquette.",
            )
            for nom_p, x_p in (
                ("bequille_pied_g", (params.longueur - params.longueur_appuie_genoux) / 2.0 + 30.0),
                ("bequille_pied_d", (params.longueur + params.longueur_appuie_genoux) / 2.0 - 30.0 - 32.0),
            ):
                ajouter(
                    nom_p, "bequille",
                    Boite(x_p, y_beq + 20.0, 0.0, 32.0, 32.0, params.hauteur_appuie_genoux - params.epaisseur_appuie_genoux),
                    essence, False,
                    "Pied de béquille avant, appui au sol.",
                )
        else:
            beq = encombrement_bequille_repliee(params)
            # Rangement dans le volume intérieur restant, derrière ou à côté du pack.
            ajouter(
                "appuie_genoux", "bequille",
                Boite(
                    interieur.x + (interieur.dx - params.longueur_appuie_genoux) / 2.0,
                    interieur.y + interieur.dy - params.profondeur_appuie_genoux - 8.0,
                    interieur.z + 8.0,
                    params.longueur_appuie_genoux, params.profondeur_appuie_genoux,
                    params.epaisseur_appuie_genoux,
                ),
                essence, False,
                "Appuie-genoux replié dans le caisson.",
            )
            for nom_p, x_p in (
                ("bequille_pied_g", interieur.x + 40.0),
                ("bequille_pied_d", interieur.x + interieur.dx - 40.0 - 32.0),
            ):
                ajouter(
                    nom_p, "bequille",
                    Boite(x_p, interieur.y + interieur.dy - 80.0, interieur.z + 8.0 + params.epaisseur_appuie_genoux,
                          beq.dz if False else 32.0, 32.0, 80.0),
                    essence, False,
                    "Pied de béquille rangé à plat dans le caisson.",
                )

    return tuple(pieces), tuple(assemblages)


def _masse_et_cdg(pieces: tuple[Piece, ...], params: ParametresBanquette) -> tuple[float, tuple[float, float, float]]:
    """Masse totale (kg) et centre de gravité (mm), approximation par boîtes."""
    densites = {
        params.essence.nom: params.essence.masse_volumique_kg_m3,
        "acier": MASSE_VOLUMIQUE_ACIER_KG_M3,
        params.revetement_exterieur.nom: MASSE_VOLUMIQUE_MOUSSE_KG_M3,
        params.revetement_banc.nom: MASSE_VOLUMIQUE_MOUSSE_KG_M3,
    }
    masse_tot = 0.0
    mx = my = mz = 0.0
    for piece in pieces:
        rho = densites.get(piece.materiau, params.essence.masse_volumique_kg_m3)
        m = piece.boite.volume_m3() * rho
        cx, cy, cz = piece.boite.centre
        masse_tot += m
        mx += m * cx
        my += m * cy
        mz += m * cz
    if masse_tot <= 0:
        return 0.0, (0.0, 0.0, 0.0)
    return masse_tot, (mx / masse_tot, my / masse_tot, mz / masse_tot)


def _verifications(
    etat: Etat,
    params: ParametresBanquette,
    derivees: DimensionsDerivees,
    pieces: tuple[Piece, ...],
    assemblages: tuple[Assemblage, ...],
) -> tuple[Verification, ...]:
    verifs: list[Verification] = []
    interieur = caisson_interieur(params, derivees)
    pack = encombrement_banc_replie(params, derivees)
    jeu = params.discretion.jeu_repli_mm

    rentre = pack.rentre_dans(interieur, jeu=jeu)
    verifs.append(Verification(
        "banc_rentre_dans_caisson",
        rentre,
        NIVEAU_OK if rentre else NIVEAU_NON_CONFORME,
        (
            f"Encombrement du banc replié {pack.dx:.0f}×{pack.dy:.0f}×{pack.dz:.0f} mm "
            f"contre intérieur {interieur.dx:.0f}×{interieur.dy:.0f}×{interieur.dz:.0f} mm "
            f"(jeu de repli {jeu:g} mm)."
            + ("" if rentre else " Le banc ne rentre pas : réduire le pack ou agrandir le caisson.")
        ),
        compromis=not rentre,
    ))

    if params.avec_bequille_avant:
        beq = encombrement_bequille_repliee(params)
        # La béquille se loge dans le volume intérieur ; on vérifie au moins
        # que chaque cote passe, en tenant compte du pack déjà présent en Y ou Z.
        reste_z = interieur.dz - pack.dz - jeu
        rentre_beq = beq.dx + jeu <= interieur.dx and beq.dy + jeu <= interieur.dy and (
            beq.dz + jeu <= interieur.dz and (beq.dz + jeu <= reste_z or beq.dy + pack.dy + jeu <= interieur.dy)
        )
        verifs.append(Verification(
            "bequille_rentre_dans_caisson",
            rentre_beq,
            NIVEAU_OK if rentre_beq else NIVEAU_NON_CONFORME,
            (
                f"Béquille repliée {beq.dx:.0f}×{beq.dy:.0f}×{beq.dz:.0f} mm "
                f"dans le caisson (reste de hauteur au-dessus du pack : {reste_z:.0f} mm)."
            ),
            compromis=not rentre_beq,
        ))

    # Cohérence de l'appui déployé
    coussin = next(p for p in pieces if p.nom == "banc_coussin_cuir")
    if etat is Etat.DEPLOYEE:
        z_appui = coussin.boite.z + coussin.boite.dz
        ok_h = abs(z_appui - params.hauteur_appui) <= 1.0
        ok_l = abs(coussin.boite.dx - params.longueur_appui) <= 1.0
        verifs.append(Verification(
            "cotes_appui_deploye",
            ok_h and ok_l,
            NIVEAU_OK if (ok_h and ok_l) else NIVEAU_NON_CONFORME,
            (
                f"Appui déployé : hauteur {z_appui:.1f} mm "
                f"(cible {params.hauteur_appui:g}), "
                f"longueur {coussin.boite.dx:.1f} mm (cible {params.longueur_appui:g})."
            ),
        ))
    else:
        z_assise = max(p.boite.z + p.boite.dz for p in pieces if p.nom == "coussin_assise")
        ok_a = abs(z_assise - params.hauteur_assise) <= 1.0
        verifs.append(Verification(
            "hauteur_assise_fermee",
            ok_a,
            NIVEAU_OK if ok_a else NIVEAU_NON_CONFORME,
            f"Hauteur d'assise fermée {z_assise:.1f} mm (cible {params.hauteur_assise:g}).",
        ))

    # Invisibilité des ancrages, cuir fonctionnel, mécanismes à l'état fermé
    if etat is Etat.FERMEE:
        fautifs = [
            p for p in pieces
            if p.visible_exterieur_si_fermee and p.role in {"ancrage", "coussin_interieur", "bequille", "trappe"}
        ]
        ferrures_visibles = [a for a in assemblages if a.visible_etat_ferme]
        ok_disc = not fautifs and not ferrures_visibles
        verifs.append(Verification(
            "ancrages_invisibles_en_fermee",
            ok_disc,
            NIVEAU_OK if ok_disc else NIVEAU_NON_CONFORME,
            (
                "À l'état fermé, aucun ancrage, cuir de banc, béquille ni ferrure "
                "n'est exposé en façade."
                if ok_disc
                else f"Éléments indûment visibles : "
                     f"{[p.nom for p in fautifs]} {[a.nom for a in ferrures_visibles]}."
            ),
        ))
        if not params.revetement_exterieur.conforme_discretions_defaut():
            verifs.append(Verification(
                "cuir_visible_derogation",
                False,
                NIVEAU_AVERTISSEMENT,
                "Revêtement de façade en cuir : dérogation, règle « zéro cuir visible » enfreinte.",
                compromis=True,
            ))

    # Rail trop mince sans bloc local
    rail_insuffisant = epaisseur_rail_insuffisante(
        params.epaisseur_panneau_banc, params.essence, params.charges, params.discretion
    )
    verifs.append(Verification(
        "rail_necessite_bloc_local",
        True,  # ce n'est pas un échec si le bloc local est prévu (il l'est)
        NIVEAU_AVERTISSEMENT if rail_insuffisant else NIVEAU_OK,
        (
            f"Le panneau d'appui ({params.epaisseur_panneau_banc:g} mm) est trop mince "
            "pour noyer à lui seul une ancre à la charge de service et au CS visés "
            "tout en conservant le retrait de discrétion. Compromis retenu : blocs "
            "d'ancrage locaux recalculés, masqués sous le cuir du banc. Un rail assez "
            "épais pour tout loger ne rentrerait probablement plus dans le caisson "
            "ou alourdirait visuellement le meuble fermé."
            if rail_insuffisant
            else "Le panneau d'appui suffit à lui seul à loger l'ancre (cas atypique)."
        ),
        compromis=rail_insuffisant,
    ))

    rapport = valider_ancrage(params.essence, recaler_bloc_ancrage(
        params.essence, params.charges, params.discretion
    ).geometrie, params.charges, params.discretion)
    verifs.append(Verification(
        "validation_ancrage",
        rapport.conforme,
        NIVEAU_OK if rapport.conforme else NIVEAU_NON_CONFORME,
        "Ancrage (bloc recalculé) : " + " | ".join(s.message for s in rapport.signalements),
        compromis=bool(rapport.compromis),
    ))
    verifs.append(Verification(
        "essai_charge_reel",
        True,
        NIVEAU_ESSAI_REQUIS,
        (
            "Toute cette grammaire est un modèle de conception. Un ingénieur doit "
            "reprendre les justificatifs (Eurocode 5 ou équivalent, assemblages, "
            "dynamique), et un essai de charge réel (appui et chaque ancrage, "
            "statique puis à-coups, jusqu'à la charge de rupture visée au minimum) "
            "est obligatoire avant tout usage."
        ),
    ))

    # Stabilité au basculement, uniquement significative en déployé.
    if etat is Etat.DEPLOYEE:
        verifs.extend(_verifications_stabilite(params, derivees, pieces))

    if params.charges.coefficient_securite < COEFFICIENT_SECURITE_MIN_RECOMMANDE:
        verifs.append(Verification(
            "cs_insuffisant",
            False,
            NIVEAU_NON_CONFORME,
            f"CS {params.charges.coefficient_securite:g} < {COEFFICIENT_SECURITE_MIN_RECOMMANDE:g} recommandé.",
        ))

    return tuple(verifs)


def _verifications_stabilite(
    params: ParametresBanquette,
    derivees: DimensionsDerivees,
    pieces: tuple[Piece, ...],
) -> list[Verification]:
    verifs: list[Verification] = []
    masse, cdg = _masse_et_cdg(pieces, params)
    # Axe de basculement avant : devant des pieds avant (ou de la béquille).
    y_pieds_av = min(p.boite.y for p in pieces if p.role == "pied")
    if params.avec_bequille_avant:
        y_appui_av = min(
            (p.boite.y for p in pieces if p.role == "bequille"),
            default=y_pieds_av,
        )
    else:
        y_appui_av = y_pieds_av
    bras_resistant = cdg[1] - y_appui_av  # mm ; doit être > 0 (CDG derrière l'appui avant)
    poids_n = masse * 9.81
    moment_resistant = poids_n * (bras_resistant / 1000.0)  # N·m

    # Charge verticale sur l'appui du banc.
    # y augmente vers l'arrière : une charge descendante ne renverse vers
    # l'avant que si elle est *devant* l'appui au sol (y < y_appui_av).
    # Sur une banquette classique, le banc reste en arrière des pieds avant
    # (et a fortiori de la béquille) : la charge verticale est stabilisante.
    coussin = next(p for p in pieces if p.nom == "banc_coussin_cuir")
    y_avant_appui = coussin.boite.y
    if y_avant_appui >= y_appui_av:
        cs_vert = float("inf")
        moment_vert = 0.0
        commentaire_vert = (
            f"Charge verticale {params.charges.charge_service_appui_n:.0f} N à l'avant "
            f"de l'appui (y = {y_avant_appui:.0f} mm) reste en arrière de l'appui au sol "
            f"(y = {y_appui_av:.0f} mm) : pas de basculement avant. "
            f"Moment résistant du poids propre {moment_resistant:.0f} N·m "
            f"(masse {masse:.1f} kg, bras {bras_resistant:.0f} mm)."
        )
    else:
        moment_vert = params.charges.charge_service_appui_n * ((y_appui_av - y_avant_appui) / 1000.0)
        cs_vert = moment_resistant / moment_vert if moment_vert else float("inf")
        commentaire_vert = (
            f"Basculement avant sous charge verticale {params.charges.charge_service_appui_n:.0f} N "
            f"devant l'appui au sol : moment résistant {moment_resistant:.0f} N·m "
            f"(masse {masse:.1f} kg, bras {bras_resistant:.0f} mm) contre "
            f"{moment_vert:.0f} N·m, coefficient {cs_vert if cs_vert != float('inf') else '∞'}. "
            f"Minimum visé {COEFFICIENT_STABILITE_MIN:g}."
        )
    ok_vert = cs_vert >= COEFFICIENT_STABILITE_MIN and bras_resistant > 0
    verifs.append(Verification(
        "stabilite_verticale",
        ok_vert,
        NIVEAU_OK if ok_vert else NIVEAU_NON_CONFORME,
        commentaire_vert,
        compromis=not ok_vert,
    ))

        # Traction horizontale vers l'avant sur un ancrage, meuble à vide, puis avec usager.
    moment_horizontal = params.charges.charge_service_ancrage_n * (params.hauteur_appui / 1000.0)
    cs_h_vide = moment_resistant / moment_horizontal if moment_horizontal else float("inf")
    # Usager assis / accoudé au centre de l'appui, charge verticale de service.
    y_usager = coussin.boite.centre[1]
    bras_usager = y_usager - y_appui_av
    moment_usager = params.charges.charge_service_appui_n * max(bras_usager, 0.0) / 1000.0
    cs_h_charge = (moment_resistant + moment_usager) / moment_horizontal if moment_horizontal else float("inf")

    if not params.avec_bequille_avant:
        verifs.append(Verification(
            "stabilite_horizontale_sans_bequille",
            False,
            NIVEAU_NON_CONFORME if cs_h_charge < COEFFICIENT_STABILITE_MIN else NIVEAU_AVERTISSEMENT,
            (
                f"Sans béquille avant, traction horizontale de "
                f"{params.charges.charge_service_ancrage_n:.0f} N à {params.hauteur_appui:g} mm "
                f"(moment {moment_horizontal:.0f} N·m) : coefficient à vide {cs_h_vide:.2f}, "
                f"avec usager {cs_h_charge:.2f}. Une banquette de salon, même lestée de "
                f"{params.masse_lest_kg:g} kg, ne peut typiquement pas s'opposer seule à "
                "cette traction. Compromis : activer la béquille avant (recommandé), "
                "alourdir fortement, ou ancrer discrètement le caisson au sol / au mur — "
                "ce dernier geste sort de l'apparence « meuble posé »."
            ),
            compromis=True,
        ))
    else:
        ok_h = cs_h_charge >= COEFFICIENT_STABILITE_MIN
        verifs.append(Verification(
            "stabilite_horizontale_avec_bequille",
            ok_h,
            NIVEAU_OK if ok_h else NIVEAU_AVERTISSEMENT,
            (
                f"Avec béquille avant (portée {params.portee_bequille:g} mm), traction "
                f"horizontale {params.charges.charge_service_ancrage_n:.0f} N à "
                f"{params.hauteur_appui:g} mm : coefficient à vide {cs_h_vide:.2f}, "
                f"avec usager {cs_h_charge:.2f} (minimum visé {COEFFICIENT_STABILITE_MIN:g}). "
                "À vide, ne pas solliciter les ancrages. Les forces d'ancrage et le poids "
                "de l'usager ne se compensent que partiellement : essai réel obligatoire."
            ),
            compromis=cs_h_vide < COEFFICIENT_STABILITE_MIN,
        ))

    verifs.append(Verification(
        "essai_stabilite_reel",
        True,
        NIVEAU_ESSAI_REQUIS,
        (
            "Le modèle de basculement ignore le glissement des pieds, la souplesse "
            "du cadre, le dynamisme d'un à-coup et le positionnement réel de l'usager. "
            "Un essai de stabilité (meuble déployé, charges progressive et dynamique) "
            "est obligatoire."
        ),
    ))
    return verifs


@dataclass(frozen=True)
class GeometrieBanquette:
    """Géométrie complète d'un état de la banquette."""

    etat: Etat
    parametres: ParametresBanquette
    derivees: DimensionsDerivees
    pieces: tuple[Piece, ...]
    assemblages: tuple[Assemblage, ...]
    verifications: tuple[Verification, ...]

    def piece(self, nom: str) -> Piece:
        for piece in self.pieces:
            if piece.nom == nom:
                return piece
        raise KeyError(f"Pièce inconnue « {nom} ».")

    @property
    def conforme(self) -> bool:
        return all(v.niveau != NIVEAU_NON_CONFORME for v in self.verifications)

    @property
    def compromis(self) -> tuple[Verification, ...]:
        return tuple(v for v in self.verifications if v.compromis)

    @property
    def essais_requis(self) -> tuple[Verification, ...]:
        return tuple(v for v in self.verifications if v.niveau == NIVEAU_ESSAI_REQUIS)

    def encombrement(self) -> Boite:
        """AABB hors-tout de toutes les pièces (l'état déployé déborde en avant et en haut)."""
        xs = [p.boite.x for p in self.pieces]
        ys = [p.boite.y for p in self.pieces]
        zs = [p.boite.z for p in self.pieces]
        xm = [p.boite.x + p.boite.dx for p in self.pieces]
        ym = [p.boite.y + p.boite.dy for p in self.pieces]
        zm = [p.boite.z + p.boite.dz for p in self.pieces]
        x0, y0, z0 = min(xs), min(ys), min(zs)
        return Boite(x0, y0, z0, max(xm) - x0, max(ym) - y0, max(zm) - z0)


def calculer(etat: Etat | int, params: ParametresBanquette | None = None) -> GeometrieBanquette:
    """Calcule la géométrie d'un état (FERMEE ou DEPLOYEE) à partir des paramètres de base."""
    if not isinstance(etat, Etat):
        etat = Etat(etat)
    params = params or parametres_banquette_defaut()
    derivees = deriver(params)
    pieces, assemblages = _pieces_et_assemblages(etat, params, derivees)
    verifications = _verifications(etat, params, derivees, pieces, assemblages)
    return GeometrieBanquette(
        etat=etat,
        parametres=params,
        derivees=derivees,
        pieces=pieces,
        assemblages=assemblages,
        verifications=verifications,
    )


def calculer_deux_etats(params: ParametresBanquette | None = None) -> dict[Etat, GeometrieBanquette]:
    """Calcule les deux états à partir du même jeu de paramètres."""
    params = params or parametres_banquette_defaut()
    return {etat: calculer(etat, params) for etat in Etat}


def vers_parametres_fusion_banquette(
    params: ParametresBanquette | None = None,
) -> dict[str, tuple[float, str, str]]:
    """Paramètres utilisateur Fusion propres à la banquette, y compris l'état."""
    params = params or parametres_banquette_defaut()
    d = deriver(params)
    out: dict[str, tuple[float, str, str]] = {
        "inc_etat_deploiement": (
            float(Etat.FERMEE),
            "",
            "État de la banquette : 0 fermée (salon), 1 déployée (banc sorti). Sans unité.",
        ),
        "inc_banq_longueur": (params.longueur, "mm", "Longueur hors-tout de la banquette."),
        "inc_banq_profondeur": (params.profondeur, "mm", "Profondeur hors-tout y compris dossier."),
        "inc_banq_hauteur_assise": (params.hauteur_assise, "mm", "Hauteur d'assise (dessus de coussin), état fermé."),
        "inc_banq_hauteur_dossier": (params.hauteur_dossier, "mm", "Sommet du dossier depuis le sol."),
        "inc_banq_hauteur_pieds": (params.hauteur_pieds, "mm", "Hauteur des pieds tournés / fuseaux."),
        "inc_banq_epaisseur_paroi": (params.epaisseur_paroi, "mm", "Épaisseur des parois du caisson."),
        "inc_banq_epaisseur_fond": (params.epaisseur_fond, "mm", "Épaisseur du fond du caisson."),
        "inc_banq_epaisseur_couvercle": (params.epaisseur_couvercle, "mm", "Épaisseur du panneau d'assise-couvercle."),
        "inc_banq_mousse_assise": (params.epaisseur_mousse_assise, "mm", "Épaisseur de mousse d'assise."),
        "inc_banq_longueur_appui": (params.longueur_appui, "mm", "Longueur d'appui du banc déployé (hypothèse)."),
        "inc_banq_largeur_appui": (params.largeur_appui, "mm", "Largeur d'appui du banc déployé."),
        "inc_banq_hauteur_appui": (params.hauteur_appui, "mm", "Hauteur d'appui du banc déployé (dessus du cuir)."),
        "inc_banq_epaisseur_panneau_banc": (params.epaisseur_panneau_banc, "mm", "Épaisseur du panneau d'appui."),
        "inc_banq_epaisseur_joue": (params.epaisseur_joue, "mm", "Épaisseur des joues du banc."),
        "inc_banq_largeur_joue": (params.largeur_joue, "mm", "Largeur (profondeur) des joues déployées."),
        "inc_banq_angle_couvercle": (
            params.angle_ouverture_couvercle_deg, "deg",
            "Angle d'ouverture du couvercle à l'état déployé.",
        ),
        "inc_banq_portee_bequille": (params.portee_bequille, "mm", "Portée vers l'avant de la béquille / appuie-genoux."),
        "inc_banq_hauteur_caisson": (d.hauteur_caisson, "mm", "Hauteur extérieure du caisson (dérivée)."),
        "inc_banq_hauteur_interieure": (d.hauteur_interieure, "mm", "Hauteur intérieure du caisson (dérivée)."),
        "inc_banq_longueur_interieure": (d.longueur_interieure, "mm", "Longueur intérieure du caisson (dérivée)."),
        "inc_banq_profondeur_interieure": (d.profondeur_interieure, "mm", "Profondeur intérieure du caisson (dérivée)."),
    }
    return out
