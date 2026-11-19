# -*- coding: utf-8 -*-
"""Catalogue minimal des matériaux structurels Aboutissants.

Propriétés mécaniques reprises des catalogues de meubles lorsqu'elles y
figurent (source citée). L'aluminium n'apparaît dans aucun des trois dépôts :
valeurs d'ordre de grandeur de norme, clairement marquées à valider.
"""

METAUX = {
    "inox_316": {
        "nom": "Inox austénitique 316L (1.4404)",
        "famille": "inox",
        "usage": "structure, pièces en contact, ancrages, machine",
        "densite": 8000.0,
        "module_elasticite": 200000.0,
        "limite_elastique": 200.0,
        "unite_contrainte": "MPa",
        "source": "equinox/equinox/catalogues/metaux.py (inox_316, EN 10088-3 barres état recuit)",
        "notes": "Recommandé Equinox : résiste aux désinfectants chlorés et aux fluides corporels. "
                 "Re = 200 MPa est l'état recuit de barre/tôle, PAS la classe de visserie A4-70 "
                 "(Rp0,2 = 450 MPa, voir catalogues.visserie).",
        "hygiene": "apte au contact et au nettoyage (électropolissage / passivation conseillés).",
    },
    "inox_304": {
        "nom": "Inox austénitique 304 (1.4301)",
        "famille": "inox",
        "usage": "structure si pas de désinfectant chloré",
        "densite": 7900.0,
        "module_elasticite": 193000.0,
        "limite_elastique": 190.0,
        "unite_contrainte": "MPa",
        "source": "equinox/equinox/catalogues/metaux.py (inox_304, EN 10088-3)",
        "notes": "Piqûres possibles avec les désinfectants chlorés ; 316L conseillé.",
        "hygiene": "rinçage obligatoire si javellisant ; préférer 316L en pièces de contact.",
    },
    "laiton_cw614n": {
        "nom": "Laiton de décolletage CuZn39Pb3 (CW614N)",
        "famille": "laiton",
        "usage": "décor, capuchons, molettes, poignées (contact prolongé déconseillé : plomb)",
        "densite": 8470.0,
        "module_elasticite": 97000.0,
        "limite_elastique": 250.0,
        "unite_contrainte": "MPa",
        "source": "equinox/equinox/catalogues/metaux.py (laiton_cw614n, EN 12164 état R430 ordre de grandeur)",
        "notes": "Contient du plomb. Equinox recommande CW510L sans plomb si contact cutané prolongé.",
        "hygiene": "vernis ou remplacement par CW510L au contact de la peau.",
    },
    "laiton_cw510l": {
        "nom": "Laiton sans plomb CuZn42 (CW510L)",
        "famille": "laiton",
        "usage": "décor et contact cutané",
        "densite": 8400.0,
        "module_elasticite": 100000.0,
        "limite_elastique": 250.0,
        "unite_contrainte": "MPa",
        "source": "equinox/equinox/catalogues/metaux.py (laiton_cw510l, EN 12164)",
        "notes": "Option contact cutané (Equinox).",
        "hygiene": "poli + vernis possible.",
    },
    "alu_6082_t6": {
        "nom": "Aluminium 6082-T6 (EN AW-6082)",
        "famille": "aluminium",
        "usage": "châssis, rails, pièces usinées légères (hors ancrage de personne dans le bois)",
        "densite": 2700.0,
        "module_elasticite": 70000.0,
        "limite_elastique": 250.0,
        "unite_contrainte": "MPa",
        "source": "EN 755-2 (ordre de grandeur Rp0,2 mini barres, à confirmer certificat 3.1). "
                  "ABSENT des scripts Equinox / Néogothique / Incognito.",
        "notes": "VALEURS À VALIDER : ce matériau n'est pas au catalogue des meubles. "
                 "Rp0,2 typique 250–260 MPa en T6 selon produit. Sensible à la fatigue et à "
                 "la corrosion galvanique au contact de l'inox (isolant / pâte à prévoir).",
        "hygiene": "anodisation conseillée ; éviter les porosités de fonderie non usinées en zone de contact.",
        "a_valider": True,
    },
}

BOIS = {
    "frene": {
        "nom": "Frêne (Fraxinus excelsior)",
        "famille": "bois",
        "usage": "châssis / pièces d'ébénisterie, gamme Equinox",
        "densite": 690.0,
        "source": "incognito/incognito/parametres.py (essence frene, ρ 690, σ_adm flexion 14 MPa) ; "
                  "Equinox utilise le frêne comme essence par défaut (catalogues.bois).",
        "contrainte_adm_flexion_mpa": 14.0,
        "notes": "Valeurs Incognito : hypothèses de conception, pas un justificatif Eurocode 5.",
    },
    "chene": {
        "nom": "Chêne (Quercus robur / petraea)",
        "famille": "bois",
        "usage": "ébénisterie massive, défaut Incognito, disponible Néogothique",
        "densite": 710.0,
        "source": "incognito/incognito/parametres.py (chene, ρ 710, σ_adm 14 MPa)",
        "contrainte_adm_flexion_mpa": 14.0,
        "notes": "Tanins : peuvent tacher le fer au contact de l'humidité (Néogothique).",
    },
    "noyer": {
        "nom": "Noyer (Juglans regia)",
        "famille": "bois",
        "usage": "Entrave Néogothique (essence imposée de typologie)",
        "densite": 650.0,
        "source": "incognito/incognito/parametres.py (noyer, ρ 650, σ_adm 12 MPa) ; "
                  "neogothique (essence noyer, classe D27 hypothèse prudente, à confirmer)",
        "contrainte_adm_flexion_mpa": 12.0,
        "notes": "Pas de classe EN 1912 pour le noyer : hypothèse D27 côté Entrave, à confirmer fournisseur.",
    },
}




# ---------------------------------------------------------------------------
# Polymères non poreux et joints — contact fluides (urine, nettoyage)
# ---------------------------------------------------------------------------
# Sources : fiches de tenue chimique courantes (Collecteur d'urine / labo) et
# pratique sanitaire. Ce ne sont pas des certificats d'alimentarité.

POLYMERES = {
    "pp_homopolymere": {
        "nom": "Polypropylène homopolymère (PP-H)",
        "famille": "polymere",
        "usage": "cuves, entonnoirs, réservoirs amovibles au contact de l'urine",
        "densite": 910.0,
        "poreux": False,
        "tenue_uree": "bonne",
        "tenue_ammoniac_dilue": "bonne",
        "tenue_desinfectants": (
            "Bonne vis-à-vis des solutions diluées d'eau de Javel, d'alcool, "
            "d'acides organiques faibles. À confirmer sur la fiche du grade "
            "et du désinfectant réellement utilisés (concentration, température, durée)."
        ),
        "usinabilite": "Usinage possible ; préférer le moulage / le tour pour les grands rayons intérieurs. Soudures miroir possibles.",
        "etat_surface_recommandee": "Ra ≤ 1,6 µm côté mouillé, sans porosité, rincable.",
        "source": "Pratique des plastiques sanitaires / labo (PP-H). Absent des catalogues de meubles.",
        "a_valider": True,
        "notes": "Alternative légère à l'inox 316L. Recyclable. Sensible aux oxydants très concentrés et aux hydrocarbures.",
    },
    "pehd": {
        "nom": "Polyéthylène haute densité (PE-HD / PE 100)",
        "famille": "polymere",
        "usage": "réservoirs amovibles, tubulures",
        "densite": 950.0,
        "poreux": False,
        "tenue_uree": "bonne",
        "tenue_ammoniac_dilue": "bonne",
        "tenue_desinfectants": (
            "Bonne aux solutions aqueuses diluées. Moins rigide que le PP ; "
            "éviter les solvants chlorés concentrés. Fiche grade à consulter."
        ),
        "usinabilite": "Usinage possible, plutôt rotomoulage ou soudure pour les cuves.",
        "etat_surface_recommandee": "Ra ≤ 1,6 µm côté mouillé.",
        "source": "Pratique des cuves PE-HD. Absent des catalogues de meubles.",
        "a_valider": True,
        "notes": "Très inerte. Plus tendre : rayer moins facilement qu'un inox, mais les rayures profondes se nettoient moins bien.",
    },
}

JOINTS = {
    "epdm": {
        "nom": "Joint EPDM (éthylène-propylène-diène)",
        "famille": "joint",
        "usage": "couvercles, raccords de vidange, lèvre de réservoir",
        "tenue_uree": "bonne",
        "tenue_ammoniac_dilue": "bonne",
        "tenue_desinfectants": "Bonne à l'eau, à la vapeur, à beaucoup de détergents. Éviter les huiles et certains hydrocarbures.",
        "source": "Classes d'usage courantes EPDM sanitaire. À valider sur fiche fabricant.",
        "a_valider": True,
    },
    "silicone_platine": {
        "nom": "Silicone vulcanisé platine",
        "famille": "joint",
        "usage": "joints de couvercle, lèvres, pièces démontables au contact cutané occasionnel",
        "tenue_uree": "bonne",
        "tenue_ammoniac_dilue": "bonne à moyenne",
        "tenue_desinfectants": "Bonne à l'eau et à l'alcool. Les huiles silicone et certains désinfectants lipidiques peuvent gonfler la matière.",
        "notes": "Ne pas confondre avec un lubrifiant silicone sur un accessoire en silicone (dégradation — rappel des guides Vac-U-Lock).",
        "source": "Pratique des joints alimentaires / médicaux. À valider.",
        "a_valider": True,
    },
    "fkm": {
        "nom": "Joint FKM (fluoroélastomère, type Viton)",
        "famille": "joint",
        "usage": "raccords chimiques, si désinfectants agressifs",
        "tenue_uree": "bonne",
        "tenue_ammoniac_dilue": "moyenne à confirmer (les bases fortes peuvent être limites selon le grade)",
        "tenue_desinfectants": "Très bonne à de nombreux oxydants et solvants. Vérifier le grade vs ammoniac.",
        "source": "Tables de compatibilité FKM. À valider.",
        "a_valider": True,
    },
}

# Compléments d'usage pour les métaux déjà catalogués, au contact des fluides
# et des accessoires silicone / PVC (Vac-U-Lock).
METAUX["inox_316"].update({
    "poreux": False,
    "tenue_uree": "excellente",
    "tenue_ammoniac_dilue": "bonne (316L préférable au 304 en milieu chloré / javellisé)",
    "tenue_desinfectants": (
        "Bonne aux désinfectants couramment dilués, y compris chlorés si rinçage "
        "(déjà noté Equinox : résiste mieux que le 304)."
    ),
    "usinabilite_cavite": (
        "Usinable (tour, fraise). Pour un ergot Vac-U-Lock : finition soignée des "
        "épaulements, pas d'arête vive (déchirure du PVC/silicone). "
        "État de surface recommandé Ra ≤ 0,8 µm sur l'ergot (emboîtement, nettoyage, pas d'accroche du film)."
    ),
    "contact_silicone_pvc": (
        "Chimiquement compatible. Éviter les arêtes et une rugosité trop forte qui "
        "abîmeraient la cavité souple. Nettoyer l'ergot sans laisser de résidu gras."
    ),
})
METAUX["laiton_cw510l"].update({
    "poreux": False,
    "tenue_uree": "moyenne (le laiton peut se ternir / se dezincifier en milieu ammoniacal)",
    "tenue_ammoniac_dilue": "déconseillée en contact prolongé (fissuration sous tension / dezincification possibles)",
    "contact_silicone_pvc": "Possible en pièce sèche (poignée). Ne pas l'utiliser en collecteur d'urine.",
    "notes_fluide": "CW510L : contact cutané OK (Equinox). Hors zone urine.",
})
METAUX["alu_6082_t6"].update({
    "poreux": False,
    "tenue_uree": "médiocre à moyenne sans anodisation fermée (corrosion, piqûres)",
    "tenue_ammoniac_dilue": "à éviter en contact prolongé",
    "contact_silicone_pvc": "Possible si anodisé, plutôt pour le châssis que pour l'ergot ou le collecteur.",
})

HABILLAGE_HORS_ZONE_HUMIDE = {
    "cuir": "Habillage uniquement, hors zone mouillée (poreux, tanins, irréversiblement taché / dégradé par l'urine).",
    "sangle": "Habillage ou sanglage uniquement, hors zone mouillée (tissage capillaire, difficile à désinfecter).",
}


def materiau(cle):
    """Retourne l'entrée de catalogue (métal, bois, polymère ou joint) par clé."""
    if cle in METAUX:
        return METAUX[cle]
    if cle in BOIS:
        return BOIS[cle]
    if cle in POLYMERES:
        return POLYMERES[cle]
    if cle in JOINTS:
        return JOINTS[cle]
    raise KeyError("Matériau inconnu : %s" % cle)
