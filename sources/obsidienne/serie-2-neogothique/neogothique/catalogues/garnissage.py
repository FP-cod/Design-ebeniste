# -*- coding: utf-8 -*-
"""Couche 2 - Catalogue des cuirs et doublures (identite : cuir noir).

Champs de chaque entree :

- ``nom``, ``famille``            : designation et famille
  ("cuir_veritable", "cuir_compose", "synthetique", "doublure").
- ``coloris``                     : coloris disponibles (la gamme impose
  "noir" ; ``parametres.valider`` verifie que ``garnissage.coloris`` y
  figure).
- ``epaisseur_mm``                : epaisseur standard de la peau / du
  complexe (mm) ; ``epaisseur_plage_mm`` : plage fournisseur.
- ``resistance_abrasion``         : echelle 1 (fragile) a 10 (tres resistant).
- ``resistance_traction_mpa``     : resistance a la rupture en traction de la
  matiere (MPa, ordre de grandeur) - verifie les sangles de manilles.
- ``ame_porteuse_n``              : capacite de l'ame textile cousue (N),
  0 si aucune. Si > 0, c'est l'ame qui porte l'effort de traction.
- ``densite_kg_m3``               : pour la masse.
- ``cout_categorie``              : "bas" | "moyen" | "eleve" | "tres_eleve"
  (indicatif, au m2 ou au metre de bande).
- ``entretien``                   : nettoyage, desinfection, graissage.
- ``usages``                      : "manille", "coussin", "doublure".
- ``fixation``                    : methode de fixation (sans vis).
- ``couture``                     : point, pas (mm), fil et diametre (mm),
  tranches - repris par les parametres ``sellerie.*`` via les regles.
- ``regles``                      : regles declaratives (voir ``regles.py``).

Style v0.2 : sellerie fine - point sellier double a la main (deux aiguilles,
fil de lin cire 0,55 mm, pas 3,2 mm), filet d'abattage a 3 mm du bord,
tranches teintees et lustrees, doublure agneau, rembourrage fin des manilles.
"""

#: Regles de sellerie communes aux cuirs fins
_SELLERIE_FINE = [
    {"id": "sellier_point", "cibles": ["sellerie.point"], "operation": "fixer", "valeur": "sellier_double",
     "explication": "Point sellier double a la main (indecousable : si un fil casse, l'autre tient)."},
    {"id": "sellier_pas", "cibles": ["sellerie.pas_point"], "operation": "fixer", "valeur": 3.2,
     "explication": "Pas 3,2 mm (8 points/pouce) : couture fine et reguliere."},
    {"id": "sellier_fil", "cibles": ["sellerie.fil_diametre"], "operation": "fixer", "valeur": 0.55,
     "explication": "Fil de lin cire 0,55 mm."},
]

GARNISSAGE = {
    "cuir_sellier_fin_noir": {
        "nom": "Cuir sellier fin noir (vachette pleine fleur + ame + rembourrage + doublure agneau)",
        "famille": "cuir_compose",
        "coloris": ["noir"],
        "epaisseur_mm": 7.5,
        "epaisseur_plage_mm": (6.5, 9.0),
        "resistance_abrasion": 8,
        "resistance_traction_mpa": 22.0,
        "ame_porteuse_n": 6000.0,
        "densite_kg_m3": 900.0,
        "cout_categorie": "tres_eleve",
        "entretien": "Baume cuir 2 a 4 fois par an ; savon glycerine ; doublure : desinfectant doux sans "
                     "alcool pur ; secher a plat.",
        "usages": ["manille", "coussin"],
        "fixation": "Couture sellier double main, rivets cuivre a contre-rivet caches sous rabat, passants forges.",
        "description": "Exterieur vachette pleine fleur tannage vegetal 3 mm teinte noir, ame sangle "
                       "polyester 25 mm, mousse latex 3 mm, doublure agneau 1 mm ; tranches teintees et "
                       "lustrees, filet d'abattage.",
        "couture": {"point": "sellier_double", "pas_point_mm": 3.2, "fil": "lin_cire", "fil_diametre_mm": 0.55,
                    "tranches": "teintees_lustrees"},
        "regles": [
            {"id": "sellier_fin_epaisseur", "cibles": ["garnissage.epaisseur_manille"], "operation": "fixer",
             "valeur": 7.5, "explication": "Vachette 3 + ame ~0,5 + rembourrage 3 + doublure 1 = 7,5 mm : "
                                            "le diametre exterieur des manilles est recalcule."},
            {"id": "sellier_fin_rembourrage", "cibles": ["sellerie.rembourrage_manille"], "operation": "fixer",
             "valeur": 3.0, "explication": "Rembourrage fin 3 mm (latex haute densite)."},
            {"id": "sellier_fin_largeurs", "cibles": ["garnissage.largeur_manille_cou",
                                                      "garnissage.largeur_manille_poignet"],
             "operation": "depuis_defaut", "facteur": 1.0,
             "explication": "Ame porteuse : largeurs de reference (cou 60, poignets 50 mm)."},
        ] + _SELLERIE_FINE,
    },
    "cuir_renforce_double_noir": {
        "nom": "Cuir renforce double pour manilles (harnais + doublure + ame)",
        "famille": "cuir_compose",
        "coloris": ["noir"],
        "epaisseur_mm": 6.5,
        "epaisseur_plage_mm": (5.5, 8.0),
        "resistance_abrasion": 9,
        "resistance_traction_mpa": 20.0,
        "ame_porteuse_n": 6000.0,
        "densite_kg_m3": 950.0,
        "cout_categorie": "tres_eleve",
        "entretien": "Baume/graisse cuir 2 a 4 fois par an ; nettoyage savon glycerine ; "
                     "desinfectant doux sans alcool pur sur la doublure ; secher a l'air.",
        "usages": ["manille"],
        "fixation": "Couture sellier double (fil polyester cire), rivets cuivre a contre-rivet, "
                    "passants forges pour le pivot.",
        "couture": {"point": "sellier_double", "pas_point_mm": 4.0, "fil": "polyester_cire", "fil_diametre_mm": 0.8,
                    "tranches": "cirees"},
        "description": "Exterieur cuir de harnais tannage vegetal 4 mm teint noir dans la masse, "
                       "ame sangle polyester 25 mm cousue, doublure cuir d'agneau noir 1,5 mm "
                       "cote peau, bords tranche lissee et cires.",
        "regles": [
            {"id": "renforce_epaisseur", "cibles": ["garnissage.epaisseur_manille"], "operation": "fixer",
             "valeur": 6.5, "explication": "Complexe harnais 4 + doublure 1,5 + ame ~1 = 6,5 mm : "
                                            "le diametre exterieur des manilles est recalcule."},
            {"id": "renforce_largeurs", "cibles": ["garnissage.largeur_manille_cou", "garnissage.largeur_manille_poignet"],
             "operation": "depuis_defaut", "facteur": 1.0,
             "explication": "Ame porteuse : largeurs de reference de la gamme (cou 60, poignets 50 mm)."},
            {"id": "renforce_pas", "cibles": ["sellerie.pas_point"], "operation": "fixer", "valeur": 4.0,
             "explication": "Harnais 4 mm : pas 4 mm (6 points/pouce), fil 0,8 mm - plus robuste, moins fin."},
            {"id": "renforce_fil", "cibles": ["sellerie.fil_diametre"], "operation": "fixer", "valeur": 0.8,
             "explication": "Fil polyester cire 0,8 mm."},
            {"id": "renforce_rembourrage", "cibles": ["sellerie.rembourrage_manille"], "operation": "fixer",
             "valeur": 0.0, "explication": "Pas de rembourrage (la doublure 1,5 mm suffit)."},
        ],
    },
    "cuir_harnais_noir": {
        "nom": "Cuir de harnais tannage vegetal noir (simple epaisseur)",
        "famille": "cuir_veritable",
        "coloris": ["noir", "brun_fonce"],
        "epaisseur_mm": 4.0,
        "epaisseur_plage_mm": (3.5, 5.0),
        "resistance_abrasion": 9,
        "resistance_traction_mpa": 20.0,
        "ame_porteuse_n": 0.0,
        "densite_kg_m3": 950.0,
        "cout_categorie": "eleve",
        "entretien": "Graisse a harnais, savon glycerine ; patine avec le temps ; craint l'eau stagnante.",
        "usages": ["manille", "sangle"],
        "fixation": "Couture sellier, rivets a contre-rivet, boucles forgees.",
        "couture": {"point": "sellier_double", "pas_point_mm": 4.0, "fil": "lin_cire", "fil_diametre_mm": 0.8,
                    "tranches": "teintees_lustrees"},
        "description": "Cuir de bourrellerie epais, tres raide au debut, se forme a l'usage.",
        "regles": [
            {"id": "harnais_epaisseur", "cibles": ["garnissage.epaisseur_manille"], "operation": "fixer",
             "valeur": 4.0, "explication": "Simple epaisseur 4 mm, sans doublure."},
            {"id": "harnais_largeur", "cibles": ["garnissage.largeur_manille_cou", "garnissage.largeur_manille_poignet"],
             "operation": "depuis_defaut", "facteur": 1.2, "arrondi": 5.0,
             "explication": "Sans ame porteuse : largeur des manilles x1,2 (le cuir seul porte la traction "
                            "et la pression de contact augmente sans doublure)."},
            {"id": "harnais_doublure", "operation": "signaler",
             "explication": "Pas de doublure : contact direct cuir tannage vegetal / peau ; arrondir et "
                            "lisser les tranches (rayon >= {securite.arrondi_contact_peau} mm)."},
            {"id": "harnais_pas", "cibles": ["sellerie.pas_point"], "operation": "fixer", "valeur": 4.0,
             "explication": "Cuir de harnais epais : pas 4 mm (le pas 3,2 fendrait le cuir)."},
            {"id": "harnais_rembourrage", "cibles": ["sellerie.rembourrage_manille"], "operation": "fixer",
             "valeur": 0.0, "explication": "Simple epaisseur : pas de rembourrage."},
        ],
    },
    "cuir_synthetique_pu_noir": {
        "nom": "Cuir synthetique PU haute densite noir (sur ame sangle)",
        "famille": "synthetique",
        "coloris": ["noir"],
        "epaisseur_mm": 5.0,
        "epaisseur_plage_mm": (4.0, 6.0),
        "resistance_abrasion": 9,
        "resistance_traction_mpa": 8.0,
        "ame_porteuse_n": 6000.0,
        "densite_kg_m3": 1100.0,
        "cout_categorie": "moyen",
        "entretien": "Lavable, resiste a l'eau et aux desinfectants usuels (ammoniums quaternaires, "
                     "alcool dilue) ; pas de patine.",
        "usages": ["manille", "coussin"],
        "fixation": "Couture + collage contact sur ame, rivets a contre-rivet.",
        "couture": {"point": "piqure_machine", "pas_point_mm": 3.5, "fil": "polyester_cire", "fil_diametre_mm": 0.6,
                    "tranches": "cirees"},
        "description": "PU haute densite 1,2 mm x 2 faces + mousse 2,5 mm sur ame sangle 25 mm.",
        "regles": [
            {"id": "pu_epaisseur", "cibles": ["garnissage.epaisseur_manille"], "operation": "fixer",
             "valeur": 5.0, "explication": "Complexe PU 2 x 1,2 mm + mousse 2,5 mm = 5 mm."},
            {"id": "pu_largeur", "cibles": ["garnissage.largeur_manille_cou", "garnissage.largeur_manille_poignet"],
             "operation": "depuis_defaut", "ajout": 5.0,
             "explication": "PU plus souple : +5 mm de largeur pour garder la meme tenue sur l'ame."},
            {"id": "pu_point", "cibles": ["sellerie.point"], "operation": "fixer", "valeur": "piqure_machine",
             "explication": "PU : piqure machine (le point sellier main n'apporte rien sur un synthetique)."},
            {"id": "pu_pas", "cibles": ["sellerie.pas_point"], "operation": "fixer", "valeur": 3.5,
             "explication": "PU : pas 3,5 mm (au-dessous, la ligne de piqure se dechire)."},
            {"id": "pu_hygiene", "operation": "signaler",
             "explication": "Option hygiene : supporte les desinfectants ; contraste visuel moindre "
                            "avec le cuir veritable (pas de patine)."},
        ],
    },
    "cuir_pleine_fleur_noir": {
        "nom": "Cuir pleine fleur noir d'ameublement (coussinets, garnitures)",
        "famille": "cuir_veritable",
        "coloris": ["noir"],
        "epaisseur_mm": 1.8,
        "epaisseur_plage_mm": (1.5, 2.2),
        "resistance_abrasion": 8,
        "resistance_traction_mpa": 18.0,
        "ame_porteuse_n": 0.0,
        "densite_kg_m3": 900.0,
        "cout_categorie": "eleve",
        "entretien": "Lait nourrissant 2 fois par an, chiffon humide ; patine.",
        "usages": ["coussin"],
        "fixation": "Agrafage sous la piece support, ourlets cousus, clous tapissier forges en decor.",
        "couture": {"point": "sellier_double", "pas_point_mm": 3.2, "fil": "lin_cire", "fil_diametre_mm": 0.55,
                    "tranches": "teintees_lustrees"},
        "description": "Pour coussinets d'appui (genoux, avant-bras) des futures typologies.",
        "regles": [
            {"id": "pf_rembourrage", "cibles": ["garnissage.epaisseur_rembourrage"], "operation": "fixer",
             "valeur": 30.0, "explication": "Cuir pleine fleur : rembourrage de reference 30 mm."},
            {"id": "pf_usage", "operation": "signaler",
             "explication": "Usage coussin uniquement : ne pas l'utiliser seul pour des manilles."},
        ],
    },
    "doublure_agneau_noir": {
        "nom": "Doublure cuir d'agneau noir",
        "famille": "doublure",
        "coloris": ["noir"],
        "epaisseur_mm": 1.2,
        "epaisseur_plage_mm": (0.9, 1.5),
        "resistance_abrasion": 4,
        "resistance_traction_mpa": 12.0,
        "ame_porteuse_n": 0.0,
        "densite_kg_m3": 850.0,
        "cout_categorie": "moyen",
        "entretien": "Nettoyage doux, desinfectant sans alcool pur, sechage a plat.",
        "usages": ["doublure"],
        "fixation": "Cousue a la piece exterieure.",
        "description": "Doublure cote peau des manilles et coussinets.",
        "regles": [
            {"id": "doublure_seule", "operation": "signaler",
             "explication": "Une doublure n'est pas une manille : a associer a un cuir exterieur."},
        ],
    },
}


def coloris_disponibles(cle):
    """Liste des coloris d'une entree (KeyError si l'entree n'existe pas)."""
    return list(GARNISSAGE[cle]["coloris"])


def cuirs_pour_usage(usage):
    """Cles des entrees utilisables pour ``usage`` ("manille", "coussin"...)."""
    return sorted(k for k, v in GARNISSAGE.items() if usage in v["usages"])
