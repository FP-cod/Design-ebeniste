# -*- coding: utf-8 -*-
"""Interface filetée des housses et état des lieux des marques.

L'embout retenu par conception est un filetage mâle **1" NPT conique**
(ASME B1.20.1), sur la partie mobile de l'actionneur (gamme haut) et,
pour rester interfaçable, au centre du plateau vibrant (gamme entrée).

IMPORTANT — compatibilité des marques : les housses officielles Sybian,
Motorbunny, The Cowgirl, Tremor, ainsi que les modèles Orb, G-Wave et
Smooth Flat Top (catalogue Sybian), n'utilisent **pas** un filetage
1" NPT d'après les sources publiques consultées. Elles s'emboîtent sur
un *contact piece* / platine à lèvres, avec tige ou ressort central, ou
sur un dock magnétique propriétaire (Cowgirl). Le 1" NPT est donc un
**choix d'interface** (standard de tuyauterie largement disponible, parfois
utilisé en adaptateurs DIY) et non le filetage d'origine de ces marques.
Voir ``COMPATIBILITES`` et ``docs/pouf_vibrant.md``.
"""

from __future__ import annotations

from dataclasses import dataclass


# Cotes ASME B1.20.1 pour 1" NPT, largement publiées
# (ex. https://sensorcatalog.com/threads/1-npt/ , tableaux ASME B1.20.1).
NPT_1_OD_MM = 33.401  # 1,315 in, diamètre extérieur nominal du filetage mâle
NPT_1_TPI = 11.5
NPT_1_PAS_MM = 25.4 / NPT_1_TPI  # ≈ 2,209 mm
NPT_1_TAPER = 1.0 / 16.0  # conicité 1:16
NPT_1_L1_MM = 10.160  # 0,4000 in, engagement à la main (hand-tight)
NPT_1_L2_MM = 17.343  # 0,6828 in, longueur utile de filet (effective, externe)

# Dépasse­ment recommandé au-dessus de la surface de selle pour visser une
# housse à la main : un peu plus que L2, pour offrir une prise et l'engagement.
NPT_1_DEPASSEMENT_RECOMMANDE_MM = 25.0

# Masse volumique pour le calcul de masse d'embout.
MASSE_VOL_INOX_316_KG_M3 = 8000.0
MASSE_VOL_LAITON_KG_M3 = 8500.0


@dataclass(frozen=True)
class FiletageHousse:
    """Description normalisée de l'embout."""

    designation: str
    norme: str
    conique: bool
    tpi: float
    diametre_exterieur_mm: float
    engagement_main_mm: float
    longueur_utile_mm: float
    depassement_recommande_mm: float
    commentaire: str


FILETAGE_1_NPT = FiletageHousse(
    designation='1" NPT mâle',
    norme="ASME B1.20.1",
    conique=True,
    tpi=NPT_1_TPI,
    diametre_exterieur_mm=NPT_1_OD_MM,
    engagement_main_mm=NPT_1_L1_MM,
    longueur_utile_mm=NPT_1_L2_MM,
    depassement_recommande_mm=NPT_1_DEPASSEMENT_RECOMMANDE_MM,
    commentaire=(
        "Filetage pipe conique, 11,5 filets au pouce, Ø ext. 33,40 mm. "
        "Ce n'est pas un filetage droit NPS/NPSM ni un UNS. Un capuchon "
        "fréquemment démonté gagne à s'appuyer sur un registre cylindrique "
        "et un joint torique plutôt que sur la seule étanchéité par coincement "
        "du NPT (usure, grippage)."
    ),
)


@dataclass(frozen=True)
class CompatibiliteHousse:
    """État des lieux d'une marque / d'un modèle, avec sources et degré de certitude."""

    nom: str
    famille: str
    interface_reelle: str
    compatible_1_npt_natif: bool
    certitude: str  # "etabli", "probable", "incertain"
    sources: tuple[str, ...]
    commentaire: str


COMPATIBILITES: tuple[CompatibiliteHousse, ...] = (
    CompatibiliteHousse(
        nom="Sybian (platine officielle)",
        famille="sybian",
        interface_reelle=(
            "Platine « contact piece » : la housse s'agrafe par une lèvre "
            "avant sous la platine, se centre, puis se tire vers l'arrière. "
            "Une tige plastique ou un ressort se loge dans un orifice central "
            "pour la rotation. Pas de filetage pipe décrit dans le manuel."
        ),
        compatible_1_npt_natif=False,
        certitude="etabli",
        sources=(
            "Manuel officiel Sybian, 2014 : "
            "https://sybian.com/wp-content/uploads/2014/04/SybianManualRevise2014-1.pdf "
            "(« anchoring the front lip under the contact piece, positioning "
            "the center and pulling down the back » ; springs & plastic stems).",
            "Fiche technique marketplace : "
            "https://usedsybian.com/sybian-101/sybian-technical-specifications/",
        ),
        commentaire=(
            "Une housse Sybian d'origine ne se visse pas sur un 1\" NPT. "
            "Il faudrait un adaptateur platine-à-lèvres + puits de tige, "
            "non fourni dans cette version."
        ),
    ),
    CompatibiliteHousse(
        nom="Smooth Flat Top",
        famille="sybian",
        interface_reelle="Housse officielle Sybian, même platine à lèvres (sans tige pour le modèle plat).",
        compatible_1_npt_natif=False,
        certitude="etabli",
        sources=(
            "Manuel Sybian 2014 (Smooth Flat Top listé comme accessoire officiel).",
            "https://sybian.com/attachments/",
            "Masse indiquée 0,200 kg sur "
            "https://thekinksters.co.uk/product/1385/smooth-flat-top-beige-sybian-attachment.html "
            "(rubrique Weight ; peut inclure un peu d'emballage, non tranché).",
        ),
        commentaire="Modèle official Sybian, pas un filetage 1\" NPT.",
    ),
    CompatibiliteHousse(
        nom="Orb",
        famille="sybian",
        interface_reelle="Housse officielle silicone Sybian, même platine (pas d'orifice de tige selon un essai publié).",
        compatible_1_npt_natif=False,
        certitude="etabli",
        sources=(
            "https://sybian.com/attachments/",
            "https://www.sexmachinereviews.co.uk/silicone-sybian-attachments-review.html",
            "https://joanprice.com/2016/02/sybian-update-new-silicone-attachments.html",
        ),
        commentaire="Catalogue silicone Sybian. Masse exacte non trouvée sur les fiches publiques.",
    ),
    CompatibiliteHousse(
        nom="G-Wave",
        famille="sybian",
        interface_reelle="Housse officielle silicone Sybian, platine + tige/ressort (modèle insertable).",
        compatible_1_npt_natif=False,
        certitude="etabli",
        sources=(
            "https://sybian.com/attachments/",
            "https://joanprice.com/2016/02/sybian-update-new-silicone-attachments.html",
        ),
        commentaire="Catalogue silicone Sybian. Masse exacte non trouvée sur les fiches publiques.",
    ),
    CompatibiliteHousse(
        nom="Motorbunny Original",
        famille="motorbunny",
        interface_reelle=(
            "Récepteur (attachment receiver) : la housse se tend par-dessus "
            "la platine ; un ressort ou une tige se place dans un puits. "
            "Certaines housses Motorbunny sont annoncées « cross-compatible "
            "with Sybian » — au sens de cette platine, pas d'un filetage."
        ),
        compatible_1_npt_natif=False,
        certitude="etabli",
        sources=(
            "Guide de démarrage Motorbunny Original (2021), étapes 4 et 6 "
            "(spring/rod mounts, stretch over the attachment receiver) : "
            "stockage public du centre d'aide Motorbunny (PDF Starter Guide).",
            "https://motorbunny.com/collections/all/products/attachment "
            "(mention « Cross-compatible with Sybian »).",
        ),
        commentaire=(
            "Le Motorbunny Buck est un autre système encore (adaptateur "
            "Vac-U-Lock Doc Johnson, non interchangeable avec l'Original) : "
            "https://motorbunny.com/pages/original-vs-buck — ce n'est pas non "
            "plus un 1\" NPT."
        ),
    ),
    CompatibiliteHousse(
        nom="The Cowgirl / Unicorn",
        famille="cowgirl",
        interface_reelle=(
            "Dock magnétique / tiges plastiques et ressorts acier propriétaires. "
            "Les housses ne sont pas interchangeables avec Sybian ni avec un NPT."
        ),
        compatible_1_npt_natif=False,
        certitude="etabli",
        sources=(
            "https://ridethecowgirl.com/products/additional-springs-and-plastic-stems-set-4",
            "https://ridethecowgirl.com/blogs/the-cowgirl-blog/the-complete-guide-to-the-cowgirl-attachments",
            "https://www.thewhiteunicorn.com/collections/sex-machines "
            "(« The Cowgirl machines use their own magnetic dock » ; "
            "« Attachments do not cross between machines »).",
        ),
        commentaire="Système fermé. Aucune source trouvée mentionnant un filetage 1\" NPT.",
    ),
    CompatibiliteHousse(
        nom="Tremor",
        famille="tremor",
        interface_reelle=(
            "Housses 100 % silicone annoncées compatibles Sybian et Motorbunny "
            "(même logique platine + tige/ressort), pas un filetage pipe."
        ),
        compatible_1_npt_natif=False,
        certitude="etabli",
        sources=(
            "https://thetremor.com/collections/attachments "
            "(« 100% silicone and compatible with Sybian® and Motorbunny® »).",
        ),
        commentaire="Compatibilité croisée au sens des platines Sybian/Motorbunny, pas du NPT.",
    ),
)


@dataclass(frozen=True)
class MasseHousseReference:
    """Référence de masse, avec degré de confiance."""

    nom: str
    masse_kg: float
    certitude: str
    source: str
    commentaire: str


MASSES_HOUSSES: tuple[MasseHousseReference, ...] = (
    MasseHousseReference(
        nom="Smooth Flat Top (beige, détaillant UK)",
        masse_kg=0.200,
        certitude="probable",
        source="https://thekinksters.co.uk/product/1385/smooth-flat-top-beige-sybian-attachment.html (Weight: 0.200 Kgs, consulté pour ce projet).",
        commentaire=(
            "Seule masse chiffrée trouvée sur une fiche publique. La rubrique "
            "peut correspondre au poids d'expédition. Ordre de grandeur d'une "
            "housse plate non insertable."
        ),
    ),
    MasseHousseReference(
        nom="Plage typique (hypothèse de conception)",
        masse_kg=0.50,
        certitude="hypothese",
        source="Fourchette de conception 0,3–1,5 kg, retenue en l'absence de masses officielles pour Orb, G-Wave, Tremor, etc.",
        commentaire=(
            "Les housses insertables en silicone plein pèsent typiquement "
            "plusieurs centaines de grammes à plus d'un kilogramme. La valeur "
            "0,50 kg est le défaut de la grammaire ; 1,5 kg est le haut de "
            "plage à vérifier par pesée."
        ),
    ),
)

MASSE_HOUSSE_DEFAUT_KG = 0.50
MASSE_HOUSSE_MIN_KG = 0.0
MASSE_HOUSSE_MAX_DOCUMENTEE_KG = 1.50


def masse_embout_kg(
    materiau: str = "inox_316",
    longueur_mm: float = 35.0,
    diametre_interieur_mm: float = 18.0,
) -> float:
    """Masse approximative d'un embout tubulaire (couronne)."""
    if materiau == "inox_316":
        rho = MASSE_VOL_INOX_316_KG_M3
    elif materiau == "laiton":
        rho = MASSE_VOL_LAITON_KG_M3
    else:
        raise ValueError(f"Matériau d'embout inconnu : {materiau}")
    r_ext = (NPT_1_OD_MM / 2.0) * 1e-3
    r_int = (diametre_interieur_mm / 2.0) * 1e-3
    if r_int >= r_ext:
        raise ValueError("Le diamètre intérieur doit être < Ø extérieur NPT.")
    volume = 3.141592653589793 * (r_ext * r_ext - r_int * r_int) * (longueur_mm * 1e-3)
    return volume * rho


@dataclass(frozen=True)
class AdaptateurHousse:
    """Adaptateur depuis l'embout 1\" NPT mâle vers une autre interface."""

    nom: str
    vers: str
    certitude_cotes: str
    imprimable_prototype: bool
    commentaire: str
    sources: tuple[str, ...]


ADAPTATEURS: tuple[AdaptateurHousse, ...] = (
    AdaptateurHousse(
        nom="npt_vers_nps_droit",
        vers='1" NPS / NPSM (filetage droit, même pas 11,5 TPI, Ø 33,4 mm)',
        certitude_cotes="etabli",
        imprimable_prototype=False,
        commentaire=(
            "Si une housse aftermarket est taraudée droit (NPS) plutôt que "
            "conique (NPT), un mamelon/adaptateur NPT mâle × NPS mâle, ou un "
            "embout interchangeable droit, rétablit l'engagement. L'étanchéité "
            "se fait alors par joint torique sur un registre, pas par le coincement "
            "NPT. Cotes ASME B1.20.1 (même Ø et pas que le NPT, sans conicité)."
        ),
        sources=("ASME B1.20.1 (NPT vs NPS/NPSM).",),
    ),
    AdaptateurHousse(
        nom="npt_vers_platine_levre_sybian",
        vers="Platine à lèvres + puits de tige/ressort (Sybian, Motorbunny Original, Tremor)",
        certitude_cotes="incertain",
        imprimable_prototype=True,
        commentaire=(
            "Les housses officielles ne se vissent pas : elles s'agrafent sur "
            "une platine. Un adaptateur (1\" NPT femelle dans le dessous, "
            "lèvre et puits sur le dessus) rendrait ces housses mécaniquement "
            "approchables. Les cotes exactes de la platine Sybian (diamètre, "
            "épaisseur de lèvre, entraxe et profondeur du puits) n'ont pas été "
            "trouvées dans les sources publiques — le prototype imprimable doit "
            "être calé par relevé physique avant une pièce de série."
        ),
        sources=(
            "Manuel Sybian 2014 (principe d'agrafage, sans cotes).",
            "Guide Motorbunny Original 2021 (receiver + spring/rod, sans cotes).",
        ),
    ),
    AdaptateurHousse(
        nom="npt_vers_dock_cowgirl",
        vers="Dock magnétique / tiges The Cowgirl",
        certitude_cotes="incertain",
        imprimable_prototype=False,
        commentaire=(
            "Système propriétaire, non documenté en cotes publiques. Pas "
            "d'adaptateur livré tant que les cotes n'ont pas été relevées ou "
            "fournies. Ne pas prétendre à la compatibilité Cowgirl."
        ),
        sources=("https://ridethecowgirl.com/ ; https://www.thewhiteunicorn.com/collections/sex-machines",),
    ),
    AdaptateurHousse(
        nom="npt_vers_vaculock",
        vers="Vac-U-Lock (Doc Johnson) — Motorbunny Buck notamment",
        certitude_cotes="probable",
        imprimable_prototype=True,
        commentaire=(
            "Le Vac-U-Lock est un standard ouvert d'attache, distinct du 1\" NPT "
            "et de la platine Sybian. Un adaptateur NPT → ergot Vac-U-Lock est "
            "envisageable (cotes à caler sur une pièce commerciale). Utile en "
            "option, hors brief des housses « platine »."
        ),
        sources=("https://motorbunny.com/pages/original-vs-buck",),
    ),
)
