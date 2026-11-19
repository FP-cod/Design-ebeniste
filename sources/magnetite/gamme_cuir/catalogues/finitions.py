# -*- coding: utf-8 -*-
"""Finitions de tranche et fils de couture.

``arete_vive`` : True si la finition laisse une arete coupante (refusee par
les regles de securite pour tout accessoire porte). Couts = categories.
"""

SRC_NEO_G = "neogothique/neogothique/catalogues/garnissage.py"

TRANCHES = {
    "brute": {"nom": "Tranche brute (coupe seule)", "arete_vive": True, "cout": "bas", "temps": "nul",
              "cuirs": ["vachette_vegetale_pleine_fleur", "cuir_harnais_vegetal", "vachette_chrome_pleine_fleur"],
              "notes": "Refusee pour un accessoire porte : arete vive et fibres qui peluchent."},
    "teintee_lissee_cire": {"nom": "Abat-carre + teinte + lissage (gomme / cire) + cire", "arete_vive": False,
                            "cout": "moyen", "temps": "long",
                            "cuirs": ["vachette_vegetale_pleine_fleur", "cuir_harnais_vegetal"],
                            "reference_meuble": SRC_NEO_G + " (tranches 'teintees_lustrees' / 'cirees')",
                            "notes": "Finition sellier de reference (Entrave). Exige un tannage vegetal."},
    "peinte_edge_paint": {"nom": "Abat-carre + peinture de tranche (edge paint) en couches", "arete_vive": False,
                          "cout": "moyen", "temps": "moyen",
                          "cuirs": ["vachette_vegetale_pleine_fleur", "cuir_harnais_vegetal",
                                    "vachette_chrome_pleine_fleur"],
                          "notes": "Seule finition propre pour le chrome ; peut s'ecailler a la flexion."},
    "rembordee": {"nom": "Rembordage (bord replie colle-cousu)", "arete_vive": False, "cout": "eleve",
                  "temps": "long", "cuirs": ["vachette_chrome_pleine_fleur", "vachette_vegetale_pleine_fleur"],
                  "notes": "Bord le plus doux ; ajoute de l'epaisseur, exige un cuir refendu (<= 2,5 mm) au bord."},
}

FILS = {
    "lin_cire_055": {"nom": "Fil de lin cire 0,55 mm", "diametre": 0.55, "matiere": "lin",
                     "pas_conseille": (2.7, 3.85), "reference_meuble": SRC_NEO_G + " (sellerie fine, 0,55 mm)",
                     "notes": "Finesse sellerie ; moins resistant a l'humidite que le polyester."},
    "polyester_cire_080": {"nom": "Fil polyester cire 0,8 mm", "diametre": 0.8, "matiere": "polyester",
                           "pas_conseille": (3.85, 5.0), "reference_meuble": SRC_NEO_G + " (cuir renforce, 0,8 mm)",
                           "notes": "Robuste, imputrescible ; point plus visible."},
    "polyester_tresse_060": {"nom": "Fil polyester tresse cire 0,6 mm", "diametre": 0.6, "matiere": "polyester",
                             "pas_conseille": (3.0, 4.0), "reference_meuble": "",
                             "notes": "Compromis : finesse proche du lin, tenue du polyester."},
}
