# -*- coding: utf-8 -*-
"""Étude d'opportunité d'impression 3D, pièce par pièce (pouf vibrant).

Règles de gamme :
* TPU (FDM 85A–95A ou SLS flexible) : silentblocs, joints plats,
  accouplements flexibles, patins — **non exposés** (pas de contact peau).
* Un joint torique TPU FDM n'est en général **pas** un moyen fiable
  d'obtenir l'IP67 (porosité inter-couches, rugosité) : joints toriques
  du commerce pour l'étanchéité, TPU pour joints plats / amortisseurs,
  ou SLS + post-traitement, à valider par essai.
* PETG ou ABS : pièces structurelles *rigides du module* (pas
  l'ébénisterie bois, qui reste tourillons / mortaises).
* Selle en contact peau : silicone platine coulé (Dragon Skin 10 ou 20)
  dans un moule imprimé, **jamais de TPU FDM exposé**.

Chiffre acoustique cité par Fabien (treillis TPU imprimé : 20,6 dBA de
réduction vs 16,9 dBA en TPU brut) : **non retrouvé** dans les sources
ouvertes consultées en novembre 2026 — à traiter comme « chiffre fourni
par Fabien, non vérifié ». Des travaux proches existent (métamatériaux
TPU imprimés, perte par transmission), sans ces deux valeurs exactes.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ConsigneImpression:
    """Paramètres d'impression indicatifs, à calibrer machine par machine."""

    procede: str
    materiau: str
    diametre_buse_mm: float | None
    hauteur_couche_mm: float | None
    remplissage_pct: float | None
    parois: int | None
    temperature_buse_c: float | None
    temperature_plateau_c: float | None
    commentaire: str


@dataclass(frozen=True)
class PieceImprimable:
    """Ligne du tableau pièce → procédé / matériau / raison."""

    piece: str
    role: str
    procede: str
    materiau: str
    exposee: bool
    raison: str
    consigne: ConsigneImpression
    export_stl: bool


_TPU_FLEX = ConsigneImpression(
    procede="FDM",
    materiau="TPU 85A–95A (ou SLS flexible : TPU 88A/90A)",
    diametre_buse_mm=0.4,
    hauteur_couche_mm=0.16,
    remplissage_pct=30.0,
    parois=3,
    temperature_buse_c=230.0,
    temperature_plateau_c=50.0,
    commentaire=(
        "Impression lente, retraction faible, enceinte si possible. "
        "Pour un treillis absorbant, le taux et la topologie (gyroid / "
        "nid d'abeille) se caractérisent par essai (raideur, fluage, "
        "température). Un silentbloc TPU n'a pas de raideur catalogue "
        "fiable tant qu'il n'a pas été mesuré."
    ),
)

_PETG = ConsigneImpression(
    procede="FDM",
    materiau="PETG (préféré) ou ABS (enceinte)",
    diametre_buse_mm=0.4,
    hauteur_couche_mm=0.20,
    remplissage_pct=40.0,
    parois=4,
    temperature_buse_c=245.0,
    temperature_plateau_c=80.0,
    commentaire="Pièces rigides de module, pas de contact peau, pas de structure bois.",
)

_MOULE_PETG = ConsigneImpression(
    procede="FDM",
    materiau="PETG ou résine technique (SLA) pour un meilleur état de surface",
    diametre_buse_mm=0.4,
    hauteur_couche_mm=0.12,
    remplissage_pct=30.0,
    parois=4,
    temperature_buse_c=245.0,
    temperature_plateau_c=80.0,
    commentaire=(
        "Moule en 2 parties, face utile poncée / vernie avant coulée. "
        "Évents et puits de coulée prévus dans la CAO. Démoulant adapté "
        "au silicone platine."
    ),
)


_PETG_ACOUSTIQUE = ConsigneImpression(
    procede="FDM",
    materiau="PETG (préféré) ; PLA possible en proto uniquement",
    diametre_buse_mm=0.4,
    hauteur_couche_mm=0.20,
    remplissage_pct=40.0,
    parois=2,
    temperature_buse_c=245.0,
    temperature_plateau_c=80.0,
    commentaire=(
        "Panneau aérien, topologie labyrinthe, nid d'abeille ou Schwarz-P, "
        "remplissage 40 %, épaisseur typique 12 mm. Le PLA est sensible "
        "à la température (Tg ≈ 55–65 °C, proche d'un capot de driver) "
        "et à l'humidité (gonflement, fluage) : déconseillé en service, "
        "PETG retenu. Ce n'est PAS un silentbloc."
    ),
)


PIECES_IMPRIMABLES: tuple[PieceImprimable, ...] = (
    PieceImprimable(
        "silentbloc_tpu", "isolation", "FDM TPU ou SLS flexible",
        "TPU 85A–95A, éventuellement treillis", False,
        "Isolation *solidienne* 8–60 Hz : élastomère uniquement "
        "(silicone du commerce ou TPU 85A–95A). Un treillis PETG/PLA, "
        "même à 40 %, est trop raide (f0 trop haute, T ≈ 1). Raideur, "
        "fluage et température du TPU à caractériser par essai.",
        _TPU_FLEX, True,
    ),
    PieceImprimable(
        "joint_plat_tpu", "etancheite_secondaire", "FDM TPU",
        "TPU 90A–95A", False,
        "Joint plat / amortisseur d'appui. Pas un joint torique d'IP67.",
        _TPU_FLEX, True,
    ),
    PieceImprimable(
        "joint_torique", "etancheite_IP67", "Commerce (ISO 3601)",
        "NBR ou silicone VMQ du commerce", False,
        "Ne pas imprimer en TPU FDM si l'on vise l'IP67 : porosité "
        "inter-couches et rugosité. Un TPU SLS post-traité reste à valider "
        "par essai, ce n'est pas le défaut.",
        ConsigneImpression("commerce", "NBR/VMQ ISO 3601", None, None, None, None, None, None,
                            "Gorge usinée ou imprimée PETG selon ISO 3601-2, joint du commerce."),
        False,
    ),
    PieceImprimable(
        "accouplement_flexible", "transmission", "FDM TPU",
        "TPU 85A–95A", False,
        "Accouplement ou découplage de couple (limiteur souple, silent-bloc de liaison).",
        _TPU_FLEX, True,
    ),
    PieceImprimable(
        "patin_amortisseur", "appui", "FDM TPU",
        "TPU 85A–95A", False,
        "Patins sous le cadre du module, non visibles, non exposés.",
        _TPU_FLEX, True,
    ),
    PieceImprimable(
        "carter_module", "structure_module", "FDM PETG/ABS",
        "PETG ou ABS", False,
        "Coques, flasques, guides, capots du module — pas l'ébénisterie.",
        _PETG, True,
    ),
    PieceImprimable(
        "embout_filetage_corps", "interface", "Usinage (inox 316)",
        "Inox 316 (pièce rapportée)", False,
        "Le filetage 1\" NPT porteur reste usiné (précision, tenue du couple "
        "de vissage). Un corps d'adaptateur PETG n'est acceptable que pour "
        "un prototype de platine-lèvre, pas pour l'embout porteur.",
        ConsigneImpression("usinage", "Inox 316", None, None, None, None, None, None,
                            "Térage, méplats, butée, collage/freinage vis."),
        False,
    ),
    PieceImprimable(
        "adaptateur_platine_levre", "interface", "FDM PETG (proto) / usinage",
        "PETG ou aluminium", False,
        "Adaptateur 1\" NPT femelle → platine à lèvres type Sybian/Motorbunny "
        "(prototype imprimable, série usinée).",
        _PETG, True,
    ),
    PieceImprimable(
        "capuchon_filetage", "discretion", "FDM PETG + insert",
        "PETG, insert laiton, joint torique commerce", False,
        "Capuchon affleurant sous le coussin. Filetage femelle : insert laiton "
        "pour éviter le grippage inox-inox. Joint torique du commerce.",
        _PETG, True,
    ),
    PieceImprimable(
        "moule_selle_2_parties", "outillage", "FDM PETG ou SLA",
        "PETG / résine", False,
        "Moule négatif en 2 parties, évents et puits de coulée, pour silicone "
        "platine Dragon Skin 10 ou 20.",
        _MOULE_PETG, True,
    ),
    PieceImprimable(
        "selle_peau", "contact_peau", "Coulée silicone platine",
        "Dragon Skin 10 ou 20 (Smooth-On ou équivalent)", True,
        "Jamais de TPU FDM au contact de la peau (porosité, hygiène, "
        "biocompatibility non établie pour cet usage). Silicone platine coulé, "
        "lavable, non poreux.",
        ConsigneImpression(
            "coulee", "Silicone platine Dragon Skin 10 ou 20",
            None, None, None, None, None, None,
            "Dégazage recommandé, rapport de mélange constructeur, démoulage après polymérisation complète.",
        ),
        False,
    ),
    PieceImprimable(
        "panneau_acoustique", "acoustique_aerien", "FDM PETG (labyrinthe / treillis 40 %)",
        "PETG (PLA : proto uniquement, sensible T/humidité)", False,
        "Bruit aérien (moteur, réducteur, 100 Hz–plusieurs kHz). Tapisse "
        "l'intérieur du caisson et les capots de modules. N'isole pas le "
        "meuble des vibrations 8–60 Hz.",
        _PETG_ACOUSTIQUE, True,
    ),
    PieceImprimable(
        "boitier_electronique", "electronique", "FDM PETG",
        "PETG, joints toriques commerce, évent ePTFE", False,
        "Boîtier IP67 de l'ESP32, ADC et relais de sécurité. Antenne sous "
        "une fenêtre plastique, non masquée par du métal.",
        _PETG, True,
    ),
    PieceImprimable(
        "logement_cellule_butee", "capteur", "FDM PETG + TPU (patin)",
        "PETG (logement, butée) ; TPU uniquement en patin d'appui", False,
        "Logement de cellule Wheatstone, butée de surcharge. Pas de contact peau.",
        _PETG, True,
    ),
    PieceImprimable(
        "bois_caisson", "ebenisterie", "Ébénisterie",
        "Chêne (ou essence de gamme), tourillons / mortaises", True,
        "Pas d'impression 3D structurelle en façade. Le bois reste le vocabulaire visible du salon.",
        ConsigneImpression("ebenisterie", "feuillu de la gamme", None, None, None, None, None, None,
                            "Assemblages bois uniquement."),
        False,
    ),
)


# Acoustique : mention de Fabien + sources proches, sans confondre les chiffres.
NOTE_ACOUSTIQUE_TREILLIS = (
    "Deux sources, telles que fournies par Fabien, vérifiées en novembre 2026 "
    "pour l'identité des articles (DOI, auteurs, dates). "
    "1) Faci, Mezache et al., « TPU-based labyrinth metamaterials for "
    "architectural applications: integrated optimization of mechanical "
    "properties and acoustic performance through additive manufacturing », "
    "The International Journal of Advanced Manufacturing Technology, "
    "en ligne le 5 mars 2026 (print avril 2026, vol. issues 9–10, "
    "p. 4933–4955), doi:10.1007/s00170-026-17663-z. Fabien en tire les "
    "chiffres 20,6 dBA (métamatériau TPU labyrinthique, 40 % de remplissage) "
    "contre 16,9 dBA (TPU massif) : une seule étude, comparaison "
    "métamatériau optimisé vs brut. Le texte intégral est derrière paywall ; "
    "ces deux valeurs n'apparaissent pas dans le résumé ouvert et n'ont "
    "pas été relues dans le PDF — chiffres tels que fournis par Fabien, "
    "attribués à cet article. "
    "2) Öztürk S., « Acoustical performance of additively manufactured "
    "metamaterials: sound absorption and transmission loss », Engineering "
    "Research Express 7 0455a1, publié le 27 novembre 2025, "
    "doi:10.1088/2631-8695/ae1791. FDM PLA vs TPU, topologies solid / "
    "honeycomb / Schwarz-P, bande 100–6100 Hz (confirmée dans l'article). "
    "L'article indique que, en comparaison FEM, le PLA donne une absorption "
    "et une perte par transmission plus élevées que le TPU sur la plus grande "
    "partie de la bande ; les mesures TPU reproduisent le même ordre "
    "qualitatif des topologies, avec des amplitudes un peu plus faibles. "
    "Conclusion retenue (et confirmée par l'article) : c'est surtout la "
    "géométrie qui fait la performance acoustique. "
    "Décision de gamme : distinguer bruit *aérien* (panneaux treillis / "
    "labyrinthe PETG dans le caisson et les capots) et isolation "
    "*solidienne* (silentblocs élastomère, 8–60 Hz, f0 ≈ 6 Hz). "
    "Le TPU imprimé reste là où l'élasticité est requise (joints plats, "
    "patins, amortisseurs, option de plot). Selle et contact peau : "
    "silicone platine Dragon Skin coulé ; le TPU peut servir au moule."
)


def pieces_exportables_stl() -> tuple[PieceImprimable, ...]:
    return tuple(p for p in PIECES_IMPRIMABLES if p.export_stl)
