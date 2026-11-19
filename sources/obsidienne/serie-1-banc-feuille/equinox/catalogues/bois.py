# -*- coding: utf-8 -*-
"""Catalogue des essences de bois.

Proprietes (bois sec a 12 % d'humidite, valeurs moyennes) :

- ``densite`` : masse volumique [kg/m3]
- ``module_elasticite`` : MOE en flexion [MPa]
- ``resistance_flexion`` : MOR, module de rupture [MPa]
- ``aptitude_cintrage`` : note 1 (mauvais) a 5 (excellent) au cintrage vapeur
- ``ratio_vapeur`` : rayon mini / epaisseur, cintrage vapeur avec feuillard
  (ordre de grandeur d'atelier, A VALIDER PAR ESSAI)
- ``ratio_lamelle`` : rayon mini / epaisseur de lamelle, lamelle-colle
  (ordre de grandeur d'atelier, A VALIDER PAR ESSAI)
- ``tenue_vis`` : note 1-5 (le frene « n'aime pas les vis » : avant-trou + cire)

Sources des MOE/MOR/densites : The Wood Database (wood-database.com, fiches
consultees le 18/11/2026), qui reprend pour les essences americaines
l'USDA FPL *Wood Handbook* (FPL-GTR-282, 2021, tableau 5-3a). Pour un
dimensionnement contractuel, recouper avec les fiches CIRAD / EN 338
(classes D) du fournisseur.
"""

SOURCE_WDB = "The Wood Database (wood-database.com), consulte le 18/11/2026"
SOURCE_WH = "USDA FPL Wood Handbook FPL-GTR-282 (2021) tab. 5-3a, via The Wood Database"

_REGLES_STRUCTURE = [
    {"cible": "bois.section_noeud", "calcul": "section_equivalente",
     "args": {"reference": "frene", "valeur_reference": 50.0},
     "raison": "conserver rigidite (E.d^4) et resistance (MOR.d^3) du frene de reference au noeud"},
    {"cible": "bois.section_extremite", "calcul": "section_equivalente",
     "args": {"reference": "frene", "valeur_reference": 30.0},
     "raison": "conserver rigidite et resistance du frene de reference aux extremites"},
    {"cible": "bois.section_entre_noeuds", "calcul": "section_equivalente",
     "args": {"reference": "frene", "valeur_reference": 40.0},
     "raison": "conserver rigidite et resistance du frene de reference entre noeuds"},
    {"cible": "bois.rayon_courbure_min", "calcul": "rayon_cintrage",
     "raison": "rayon mini de cintrage propre a l'essence et a la methode"},
    {"cible": "jonctions.longueur_insert", "calcul": "longueur_insert",
     "raison": "longueur d'insert filete selon la densite (arrachement)"},
]

BOIS = {
    "frene": {
        "nom": "Frene europeen", "nom_latin": "Fraxinus excelsior",
        "densite": 680.0, "module_elasticite": 12310.0, "resistance_flexion": 103.6,
        "aptitude_cintrage": 5, "ratio_vapeur": 6.0, "ratio_lamelle": 80.0, "tenue_vis": 3,
        "teinte": "clair, blond", "source": SOURCE_WDB,
        "notes": "Essence de reference Equinox. Excellent au cintrage vapeur, resilient aux chocs. "
                 "Vis : avant-trou obligatoire, cirer les vis.",
        "regles": _REGLES_STRUCTURE,
    },
    "frene_blanc": {
        "nom": "Frene blanc d'Amerique", "nom_latin": "Fraxinus americana",
        "densite": 675.0, "module_elasticite": 12000.0, "resistance_flexion": 103.5,
        "aptitude_cintrage": 5, "ratio_vapeur": 6.0, "ratio_lamelle": 80.0, "tenue_vis": 3,
        "teinte": "clair", "source": SOURCE_WH,
        "notes": "Equivalent americain ; espece menacee (agrile du frene) : verifier la provenance.",
        "regles": _REGLES_STRUCTURE,
    },
    "chene": {
        "nom": "Chene pedoncule", "nom_latin": "Quercus robur",
        "densite": 675.0, "module_elasticite": 10600.0, "resistance_flexion": 97.1,
        "aptitude_cintrage": 4, "ratio_vapeur": 7.0, "ratio_lamelle": 90.0, "tenue_vis": 4,
        "teinte": "blond a brun clair, maillure", "source": SOURCE_WDB,
        "notes": "Tanins : tache au contact de l'acier non inox humide ; inox 316 ou laiton conseilles.",
        "regles": _REGLES_STRUCTURE + [
            {"cible": "inox.nuance", "calcul": "fixer", "args": {"valeur": "inox_316", "si_parmi": ["inox_304", "acier_s235"]},
             "raison": "tanins du chene : eviter l'acier et l'inox 304 au contact (taches noires)"}],
    },
    "noyer": {
        "nom": "Noyer commun", "nom_latin": "Juglans regia",
        "densite": 640.0, "module_elasticite": 10810.0, "resistance_flexion": 111.5,
        "aptitude_cintrage": 4, "ratio_vapeur": 7.0, "ratio_lamelle": 90.0, "tenue_vis": 4,
        "teinte": "brun, contraste fort avec cuir cognac", "source": SOURCE_WDB,
        "notes": "Rompt avec le 'frene clair' de la gamme : variante sombre.",
        "regles": _REGLES_STRUCTURE + [
            {"cible": None, "calcul": "alerte",
             "args": {"message": "noyer : teinte foncee, l'identite 'frene clair' Equinox change ; valider le cuir"},
             "raison": "esthetique"}],
    },
    "hetre": {
        "nom": "Hetre europeen", "nom_latin": "Fagus sylvatica",
        "densite": 710.0, "module_elasticite": 14310.0, "resistance_flexion": 110.1,
        "aptitude_cintrage": 5, "ratio_vapeur": 5.0, "ratio_lamelle": 70.0, "tenue_vis": 4,
        "teinte": "clair rosé", "source": SOURCE_WDB,
        "notes": "Tres bon cintrage (chaises Thonet). Retrait important : sensible aux variations d'humidite.",
        "regles": _REGLES_STRUCTURE,
    },
    "erable_sycomore": {
        "nom": "Erable sycomore", "nom_latin": "Acer pseudoplatanus",
        "densite": 615.0, "module_elasticite": 9920.0, "resistance_flexion": 98.1,
        "aptitude_cintrage": 3, "ratio_vapeur": 10.0, "ratio_lamelle": 100.0, "tenue_vis": 4,
        "teinte": "tres clair, blanc creme", "source": SOURCE_WDB,
        "notes": "Moins rigide que le frene (-19 % de MOE) : sections a augmenter.",
        "regles": _REGLES_STRUCTURE,
    },
    "erable_dur": {
        "nom": "Erable dur (a sucre)", "nom_latin": "Acer saccharum",
        "densite": 705.0, "module_elasticite": 12620.0, "resistance_flexion": 109.0,
        "aptitude_cintrage": 3, "ratio_vapeur": 10.0, "ratio_lamelle": 100.0, "tenue_vis": 5,
        "teinte": "tres clair", "source": SOURCE_WH,
        "notes": "Rigide et dur ; cintrage vapeur moyen, preferer le lamelle-colle.",
        "regles": _REGLES_STRUCTURE,
    },
    "noyer_noir": {
        "nom": "Noyer noir d'Amerique", "nom_latin": "Juglans nigra",
        "densite": 610.0, "module_elasticite": 11590.0, "resistance_flexion": 100.7,
        "aptitude_cintrage": 4, "ratio_vapeur": 7.0, "ratio_lamelle": 90.0, "tenue_vis": 4,
        "teinte": "brun chocolat", "source": SOURCE_WH,
        "notes": "Variante sombre.", "regles": _REGLES_STRUCTURE,
    },
}
