# -*- coding: utf-8 -*-
"""Catalogue des metaux (structure, quincaillerie, lest).

Proprietes :

- ``densite`` [kg/m3], ``module_elasticite`` [MPa], ``limite_elastique``
  Rp0,2 mini a l'etat recuit / standard [MPa] (EN 10088-3, EN 12164,
  EN 10025-2 ; valeurs mini de norme, les barres etirees sont souvent
  plus elevees : utiliser le certificat matiere 3.1 pour affiner)
- ``sections_standards`` : sections courantes du commerce (mm)
- ``traitements`` : finitions possibles
- ``usage`` : 'structure' | 'decor' | 'lest'
"""

METAUX = {
    "inox_316": {
        "nom": "Inox austenitique 316L (1.4404)", "usage": "structure",
        "densite": 8000.0, "module_elasticite": 200000.0, "limite_elastique": 200.0,
        "sections_standards": {"rond_plein": [8, 10, 12, 14, 16, 20], "tube_rond": ["12x1", "12x1.5", "12x2", "16x2", "20x2"],
                               "tube_carre": ["40x40x2", "40x40x3"], "toles": [1.5, 2, 3, 4]},
        "traitements": ["brosse grain 240", "electropolissage", "passivation", "microbillage"],
        "source": "EN 10088-3 (barres, etat recuit)",
        "notes": "Recommande : resiste aux desinfectants chlores et aux fluides corporels.",
        "regles": [],
    },
    "inox_304": {
        "nom": "Inox austenitique 304 (1.4301)", "usage": "structure",
        "densite": 7900.0, "module_elasticite": 193000.0, "limite_elastique": 190.0,
        "sections_standards": {"rond_plein": [8, 10, 12, 14, 16, 20], "tube_rond": ["12x1", "12x1.5", "16x1.5"],
                               "tube_carre": ["40x40x1.5", "40x40x2"], "toles": [1.5, 2, 3]},
        "traitements": ["brosse", "electropolissage", "passivation"],
        "source": "EN 10088-3 (barres, etat recuit)",
        "notes": "Piqures possibles avec les desinfectants chlores.",
        "regles": [
            {"cible": None, "calcul": "alerte",
             "args": {"message": "inox 304 : proscrire les desinfectants chlores, rincer ; 316L conseille"},
             "raison": "corrosion par piqures"},
            {"cible": "inox.diametre_axe_pivot", "calcul": "section_metal_equivalente",
             "args": {"reference": "inox_316", "valeur_reference": 16.0},
             "raison": "limite elastique plus faible : axe de pivot a recalculer"},
        ],
    },
    "acier_s235": {
        "nom": "Acier S235 (zingue + peint)", "usage": "structure",
        "densite": 7850.0, "module_elasticite": 210000.0, "limite_elastique": 235.0,
        "sections_standards": {"rond_plein": [10, 12, 16, 20], "tube_carre": ["40x40x2", "40x40x3", "40x40x4"]},
        "traitements": ["zingage + thermolaquage", "noircissage (interieur seulement)"],
        "source": "EN 10025-2",
        "notes": "A reserver aux pieces cachees (ame de traverse).",
        "regles": [
            {"cible": None, "calcul": "alerte",
             "args": {"message": "acier : traitement anticorrosion obligatoire, ne pas laisser apparent"},
             "raison": "corrosion"}],
    },
    "laiton_cw614n": {
        "nom": "Laiton de decolletage CuZn39Pb3 (CW614N)", "usage": "decor",
        "densite": 8470.0, "module_elasticite": 97000.0, "limite_elastique": 250.0,
        "sections_standards": {"rond_plein": [30, 40, 45, 50], "toles": [1, 2, 3]},
        "traitements": ["poli + vernis", "brosse", "patine naturelle", "PVD"],
        "source": "EN 12164 (etat R430, ordre de grandeur)",
        "notes": "Contient du plomb (decolletage) : CW510L sans plomb si contact cutane prolonge.",
        "regles": [],
    },
    "laiton_cw510l": {
        "nom": "Laiton sans plomb CuZn42 (CW510L)", "usage": "decor",
        "densite": 8400.0, "module_elasticite": 100000.0, "limite_elastique": 250.0,
        "sections_standards": {"rond_plein": [30, 40, 50]},
        "traitements": ["poli + vernis", "brosse"], "source": "EN 12164 (ordre de grandeur)",
        "notes": "Option contact cutane.", "regles": [],
    },
    # --- materiaux de lest (remplissage du tube 40x40) -----------------------
    "plomb": {
        "nom": "Plomb coule / barre", "usage": "lest", "densite": 11340.0, "taux_remplissage": 1.0,
        "notes": "Toxique a l'usinage ; enfermer hermetiquement (bouchons soudes).",
        "regles": [{"cible": None, "calcul": "capacite_lest", "raison": "capacite du tube selon densite"}],
    },
    "acier_plein": {
        "nom": "Barre acier pleine 36x36 (dans tube 40x40x2)", "usage": "lest", "densite": 7850.0,
        "taux_remplissage": 1.0, "notes": "Sans toxicite.",
        "regles": [{"cible": None, "calcul": "capacite_lest", "raison": "capacite du tube selon densite"}],
    },
    "grenaille_acier": {
        "nom": "Grenaille d'acier en vrac", "usage": "lest", "densite": 7850.0, "taux_remplissage": 0.58,
        "notes": "Masse apparente ~4,5 t/m3 ; bruit si mal tassee : noyer dans resine.",
        "regles": [{"cible": None, "calcul": "capacite_lest", "raison": "capacite du tube selon densite"}],
    },
}
