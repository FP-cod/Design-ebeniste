# -*- coding: utf-8 -*-
"""Cuirs exterieurs, doublures, rembourrages et teintes de la GammeCuir.

Les teintes portent un rendu RVB INDICATIF (pour l'apparence Fusion, pas une
reference colorimetrique fournisseur) et la quincaillerie conseillee. Leur
correspondance avec les meubles est dans ``correspondances_meubles``.

Valeurs mecaniques : reprises de Neogothique quand elles existent (ordre de
grandeur, source indiquee) ; sinon ``None`` (pas d'invention).
"""

SRC_NEO_G = "neogothique/neogothique/catalogues/garnissage.py"
SRC_EQ_G = "equinox/equinox/catalogues/garnissage.py"

CUIRS = {
    "vachette_vegetale_pleine_fleur": {
        "nom": "Vachette pleine fleur tannage vegetal (croupon)",
        "tannage": "vegetal", "epaisseur_plage": (2.0, 5.0),
        "teintes": ["cognac", "tan", "havane", "noir", "brun_fonce", "bordeaux", "vert_bouteille", "bleu_nuit"],
        "resistance_traction_mpa": 20.0,
        "source_traction": SRC_NEO_G + " (cuir_harnais_noir / renforce : 20 MPa, ordre de grandeur)",
        "tranche_lissable": True, "cout": "eleve",
        "notes": "Cuir de reference : se teinte, se lisse a la tranche, se patine comme le cuir Equinox "
                 "cuir_classique_pleine_fleur. Fleur a garder cote exterieur.",
    },
    "cuir_harnais_vegetal": {
        "nom": "Cuir de harnais tannage vegetal, nourri (graisse)",
        "tannage": "vegetal", "epaisseur_plage": (3.5, 5.0),
        "teintes": ["noir", "brun_fonce", "havane", "cognac"],
        "resistance_traction_mpa": 20.0,
        "source_traction": SRC_NEO_G + " (cuir_harnais_noir, ordre de grandeur)",
        "tranche_lissable": True, "cout": "eleve",
        "notes": "Meme famille que cuir_harnais_noir de l'Entrave : le plus solide, moins souple, "
                 "a reserver aux sangles de contention et aux harnais.",
    },
    "vachette_chrome_pleine_fleur": {
        "nom": "Vachette pleine fleur tannage chrome (souple)",
        "tannage": "chrome", "epaisseur_plage": (2.0, 3.5),
        "teintes": ["noir", "cognac", "bordeaux", "bleu_nuit"],
        "resistance_traction_mpa": None, "source_traction": "",
        "tranche_lissable": False, "cout": "moyen",
        "notes": "Plus souple et moins cher ; la tranche se lisse mal (peinture de tranche ou rembordage). "
                 "Rendu different du cuir vegetal des meubles : assortiment de teinte a controler sur echantillon.",
    },
}

DOUBLURES = {
    "agneau_pleine_fleur": {
        "nom": "Doublure agneau pleine fleur", "epaisseur_plage": (0.8, 1.5),
        "teintes": ["noir", "cognac", "tan", "havane", "bordeaux"],
        "reference_meuble": SRC_NEO_G + " (doublure_agneau_noir, 1,2 mm)",
        "notes": "Douce cote peau ; ne porte pas l'effort.",
    },
    "veau_velours": {
        "nom": "Veau velours (croute retournee)", "epaisseur_plage": (1.0, 2.0),
        "teintes": ["noir", "brun_fonce", "tan", "bordeaux"],
        "reference_meuble": "", "notes": "Accroche la peau (moins de glissement) ; se salit plus vite.",
    },
}

REMBOURRAGES = {
    "mousse_latex": {"nom": "Mousse latex haute densite", "epaisseur_plage": (2.0, 8.0),
                     "allergene": "latex", "reference_meuble": SRC_NEO_G + " (sellier fin : latex 3 mm)",
                     "notes": "Reprend sa forme ; a eviter pour les personnes allergiques au latex."},
    "feutre_laine": {"nom": "Feutre de laine", "epaisseur_plage": (2.0, 6.0), "allergene": "",
                     "reference_meuble": "", "notes": "Ferme, se tasse a la forme du membre ; traditionnel."},
    "neoprene": {"nom": "Neoprene ferme", "epaisseur_plage": (3.0, 10.0), "allergene": "possible (chloroprene)",
                 "reference_meuble": "", "notes": "Ne retient pas l'humidite ; aspect moins noble."},
}

#: Teintes : rgb = rendu indicatif ; apparences = noms candidats dans la
#: bibliotheque d'apparences Fusion (a verifier sur l'installation : la
#: grammaire retombe sur une copie teintee si aucun nom n'est trouve).
TEINTES = {
    "cognac": {"nom": "Cognac", "rgb": (154, 82, 36), "famille_chromatique": "chaude",
               "quincaillerie_conseillee": ["laiton_massif_cw510l", "laiton_patine"],
               "quincaillerie_possible": ["inox_316"], "fil_conseille": "naturel_ou_ton_sur_ton",
               "apparences": ["Leather - Brown", "Cuir - Marron", "Leather"]},
    "tan": {"nom": "Tan (naturel clair)", "rgb": (196, 140, 86), "famille_chromatique": "chaude",
            "quincaillerie_conseillee": ["laiton_massif_cw510l"], "quincaillerie_possible": ["inox_316"],
            "fil_conseille": "naturel", "apparences": ["Leather - Tan", "Leather - Brown", "Leather"]},
    "havane": {"nom": "Havane", "rgb": (110, 62, 33), "famille_chromatique": "chaude",
               "quincaillerie_conseillee": ["laiton_massif_cw510l", "laiton_patine"],
               "quincaillerie_possible": ["inox_316"], "fil_conseille": "ton_sur_ton",
               "apparences": ["Leather - Brown", "Leather"]},
    "brun_fonce": {"nom": "Brun fonce", "rgb": (72, 42, 25), "famille_chromatique": "chaude",
                   "quincaillerie_conseillee": ["laiton_patine", "laiton_massif_cw510l"],
                   "quincaillerie_possible": ["inox_316_pvd_noir"], "fil_conseille": "ton_sur_ton",
                   "apparences": ["Leather - Brown", "Leather"]},
    "noir": {"nom": "Noir", "rgb": (22, 22, 24), "famille_chromatique": "neutre",
             "quincaillerie_conseillee": ["inox_316", "inox_316_pvd_noir"],
             "quincaillerie_possible": ["laiton_massif_cw510l", "laiton_patine"], "fil_conseille": "noir_ou_contraste",
             "apparences": ["Leather - Black", "Cuir - Noir", "Leather"]},
    "bordeaux": {"nom": "Bordeaux", "rgb": (94, 24, 36), "famille_chromatique": "chaude",
                 "quincaillerie_conseillee": ["laiton_massif_cw510l"], "quincaillerie_possible": ["inox_316"],
                 "fil_conseille": "ton_sur_ton", "apparences": ["Leather - Red", "Leather"]},
    "vert_bouteille": {"nom": "Vert bouteille", "rgb": (24, 62, 40), "famille_chromatique": "froide",
                       "quincaillerie_conseillee": ["laiton_massif_cw510l"], "quincaillerie_possible": ["inox_316"],
                       "fil_conseille": "ton_sur_ton", "apparences": ["Leather - Green", "Leather"]},
    "bleu_nuit": {"nom": "Bleu nuit", "rgb": (22, 30, 58), "famille_chromatique": "froide",
                  "quincaillerie_conseillee": ["inox_316"], "quincaillerie_possible": ["laiton_massif_cw510l"],
                  "fil_conseille": "ton_sur_ton", "apparences": ["Leather - Blue", "Leather"]},
}


def teinte_disponible(matiere, teinte):
    return matiere in CUIRS and teinte in CUIRS[matiere]["teintes"]
