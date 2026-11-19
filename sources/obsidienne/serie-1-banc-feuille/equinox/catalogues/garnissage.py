# -*- coding: utf-8 -*-
"""Catalogue des revetements (garnissages) de la gamme Equinox.

Chaque entree (une famille de revetement) contient :

- ``nom`` : nom lisible ; ``famille`` : 'cuir' | 'cuir_vegan' | 'tissu' |
  'cuir_synthetique' | 'tissu_enduit'
- ``coloris`` : coloris disponibles ; ``coloris_defaut`` : coloris pris si le
  coloris courant n'existe pas dans la famille
- ``epaisseur_matiere`` : epaisseur standard du revetement [mm] ;
  ``epaisseur_plage`` : (mini, maxi) [mm]
- ``abrasion`` : resistance a l'abrasion sur l'echelle Equinox 1-10
  (``ECHELLE_ABRASION``) ; ``abrasion_martindale`` : cycles EN ISO 12947-2
  indicatifs en complement (None pour le cuir, teste en EN ISO 17076)
- ``cout_m2`` : categorie de cout au m2 (``CATEGORIES_COUT``) - aucun prix
- ``entretien`` : proprietes d'entretien ; ``desinfection``
- ``epaisseur_rembourrage_recommandee`` [mm], ``methode_fixation``,
  ``finition_bords``, ``rayon_bord_min`` [mm]
- ``regles`` : regles declaratives appliquees par ``equinox.regles``

Toutes les valeurs d'abrasion et de cout sont qualitatives : A VALIDER sur la
fiche technique de la reference fournisseur retenue.
"""

#: Echelle d'abrasion Equinox (1-10) et correspondance avec les qualificatifs.
ECHELLE_ABRASION = {
    "faible": (1, 3),        # < ~15 000 cycles Martindale / cuirs tres fins
    "moyenne": (4, 6),       # ~15 000 - 40 000 cycles, usage domestique
    "elevee": (7, 8),        # ~40 000 - 80 000 cycles, usage intensif
    "tres_elevee": (9, 10),  # > ~80 000 cycles, usage professionnel / medical
}

#: Categories de cout au m2 (ordre croissant), sans prix.
CATEGORIES_COUT = ("bas", "bas_moyen", "moyen", "eleve")

#: Methodes de fixation et finitions possibles (choix du parametre).
METHODES_FIXATION = ("agrafage_sous_plateau", "agrafage_ou_scratch", "collage_et_agrafage")
FINITIONS_BORDS = ("ourlets_cousus", "rembordage_sans_couture", "rembordage_colle")

#: Regle commune : verifier que le coloris courant existe dans la famille.
_REGLE_COLORIS = {"cible": "garnissage.couleur", "calcul": "coloris_disponible",
                  "raison": "coloris non disponible dans cette famille : coloris par defaut de la famille"}


def _regles_base(raison_rembourrage, raison_fixation, raison_bord, rembourrage=None):
    """Regles communes : coloris, rembourrage, fixation, finition, rayon de bord."""
    regles = [dict(_REGLE_COLORIS)]
    regles.append(rembourrage or {"cible": "garnissage.epaisseur_rembourrage", "calcul": "copier",
                                  "args": {"propriete": "epaisseur_rembourrage_recommandee"},
                                  "raison": raison_rembourrage})
    regles += [
        {"cible": "garnissage.methode_fixation", "calcul": "copier", "args": {"propriete": "methode_fixation"},
         "raison": raison_fixation},
        {"cible": "garnissage.finition_bords", "calcul": "copier", "args": {"propriete": "finition_bords"},
         "raison": "finition des bords propre a la famille"},
        {"cible": "garnissage.rayon_bord", "calcul": "copier", "args": {"propriete": "rayon_bord_min"},
         "raison": raison_bord},
    ]
    return regles


GARNISSAGE_REFERENCE = "cuir_classique_pleine_fleur"


class _CatalogueAvecAlias(dict):
    """dict dont les anciennes cles (alias) restent accessibles sans etre iterees."""

    def __init__(self, donnees, alias):
        dict.__init__(self, donnees)
        self.alias = dict(alias)

    def resoudre(self, cle):
        return self.alias.get(cle, cle)

    def __missing__(self, cle):
        if cle in self.alias:
            return dict.__getitem__(self, self.alias[cle])
        raise KeyError(cle)

    def __contains__(self, cle):
        return dict.__contains__(self, cle) or cle in self.alias

    def get(self, cle, defaut=None):
        return self[cle] if cle in self else defaut


_ENTREES = {
    # 2. Cuir classique pleine fleur (le cuir cognac de base de la gamme)
    "cuir_classique_pleine_fleur": {
        "nom": "Cuir classique pleine fleur", "famille": "cuir",
        "coloris": ["noir", "cognac", "havane", "vert_bouteille", "bleu_nuit"], "coloris_defaut": "cognac",
        "epaisseur_matiere": 1.8, "epaisseur_plage": (1.5, 2.0),
        "abrasion": 8, "abrasion_martindale": None,
        "abrasion_note": "cuir : EN ISO 17076-1 / Veslic, pas de Martindale ; 'elevee' -> 8/10",
        "cout_m2": "eleve",
        "entretien": "patine avec le temps ; nettoyant doux pH neutre + nourrissant 2 a 4 fois/an ; "
                     "eviter alcool et chlore",
        "desinfection": "limitee (produits doux) ; finition semi-aniline protegee conseillee",
        "epaisseur_rembourrage_recommandee": 30.0,
        "methode_fixation": "agrafage_sous_plateau", "finition_bords": "ourlets_cousus", "rayon_bord_min": 12.0,
        "notes": "Revetement de reference Equinox (cognac). Valeur de rembourrage de reference des autres familles.",
        "regles": _regles_base("le cuir classique, epais et tenu, se tend sur 30 mm de mousse HR",
                               "agrafage sous le plateau (support contreplaque)",
                               "rayon mini des aretes pour ne pas casser la fleur"),
    },
    # 1. Cuir vegan
    "cuir_vegan": {
        "nom": "Cuir vegan (sans cuir veritable)", "famille": "cuir_vegan",
        "coloris": ["noir", "blanc", "cognac", "vert_olive", "bordeaux"], "coloris_defaut": "cognac",
        "epaisseur_matiere": 1.35, "epaisseur_plage": (1.2, 1.5),
        "abrasion": 5, "abrasion_martindale": 30000,
        "abrasion_note": "'moyenne' -> 5/10 ; Martindale indicatif a valider",
        "cout_m2": "moyen",
        "entretien": "entretien facile : chiffon humide + savon doux ; pas de nourrissant",
        "desinfection": "desinfectants doux sans solvant",
        "epaisseur_rembourrage_recommandee": None,  # calcule relativement au cuir classique (+5 mm)
        "ecart_rembourrage": 5.0,
        "methode_fixation": "agrafage_sous_plateau", "finition_bords": "ourlets_cousus", "rayon_bord_min": 10.0,
        "notes": "Aucun cuir veritable. Moins de tenue au molletonnage que le cuir : rembourrage +5 mm.",
        "regles": _regles_base(None, "agrafage sous le plateau", "matiere souple, aretes un peu plus vives possibles",
                               rembourrage={"cible": "garnissage.epaisseur_rembourrage", "calcul": "rembourrage_relatif",
                                            "args": {"reference": GARNISSAGE_REFERENCE, "ecart": 5.0},
                                            "raison": "moins de tenue au molletonnage : rembourrage du cuir classique "
                                                      "+ 5 mm"}),
    },
    # 3. Tissu Krypton
    "tissu_krypton": {
        "nom": "Tissu Krypton (tissu technique dense, type velours cotele renforce)", "famille": "tissu",
        "coloris": ["noir", "gris_anthracite", "bordeaux", "bleu_marine"], "coloris_defaut": "noir",
        "epaisseur_matiere": 2.5, "epaisseur_plage": (2.0, 3.0),
        "abrasion": 8, "abrasion_martindale": 60000,
        "abrasion_note": "'elevee' -> 8/10 ; Martindale indicatif a valider",
        "cout_m2": "bas_moyen",
        "entretien": "lavable ; brossage dans le sens des cotes ; detachage a l'eau savonneuse",
        "desinfection": "absorbe les fluides : membrane PU sous le tissu recommandee",
        "epaisseur_rembourrage_recommandee": 40.0,
        "methode_fixation": "agrafage_ou_scratch", "finition_bords": "rembordage_sans_couture", "rayon_bord_min": 20.0,
        "notes": "Tissu technique dense type velours cotele renforce, utilise en ameublement et habillement "
                 "technique. Cotes a orienter dans le sens de la longueur.",
        "regles": _regles_base("tissu dense : rembourrage plus epais (40 mm)",
                               "fixation par agrafage ou par bande auto-agrippante (scratch)",
                               "le velours cotele s'ecrase et luit sur les aretes : rayon >= 20 mm") + [
            {"cible": None, "calcul": "alerte_si", "args": {"parametre": "garnissage.coutures_sur_courbes", "valeur": True,
                                                            "message": "tissu Krypton : pas de couture apparente "
                                                                       "recommandee sur les courbes"},
             "raison": "les coutures apparentes vrillent sur les courbes"},
            {"cible": None, "calcul": "alerte",
             "args": {"message": "Recommandation : membrane PU impermeable sous le tissu Krypton"},
             "raison": "hygiene"},
        ],
    },
    # 4. Cuir synthetique haute qualite
    "cuir_synthetique_hq": {
        "nom": "Cuir synthetique haute qualite (polyurethane haute densite)", "famille": "cuir_synthetique",
        "coloris": ["noir", "cognac", "gris"], "coloris_defaut": "cognac",
        "epaisseur_matiere": 1.1, "epaisseur_plage": (1.0, 1.2),
        "abrasion": 9, "abrasion_martindale": 100000,
        "abrasion_note": "'tres elevee' -> 9/10 ; Martindale indicatif a valider",
        "cout_m2": "moyen",
        "entretien": "resistant a l'eau ; nettoyage a l'eau savonneuse",
        "desinfection": "resistant aux desinfectants usuels (ammoniums quaternaires, alcool dilue)",
        "epaisseur_rembourrage_recommandee": 30.0,
        "methode_fixation": "collage_et_agrafage", "finition_bords": "rembordage_colle", "rayon_bord_min": 6.0,
        "compatible_toutes_geometries": True,
        "notes": "Compatible avec toutes les geometries (souple, colle sur les courbes).",
        "regles": _regles_base("PU haute densite : tenue proche du cuir, 30 mm", "collage + agrafage",
                               "compatible toutes geometries : aretes vives possibles"),
    },
    # Conserve : tissu technique enduit (option hygiene maximale)
    "tissu_technique_enduit": {
        "nom": "Tissu technique enduit PU (type medical)", "famille": "tissu_enduit",
        "coloris": ["noir", "cognac"], "coloris_defaut": "noir",
        "epaisseur_matiere": 0.7, "epaisseur_plage": (0.6, 0.9),
        "abrasion": 9, "abrasion_martindale": 100000, "abrasion_note": "'tres elevee' -> 9/10",
        "cout_m2": "moyen",
        "entretien": "lessivable", "desinfection": "desinfectants hospitaliers",
        "epaisseur_rembourrage_recommandee": 30.0,
        "methode_fixation": "agrafage_sous_plateau", "finition_bords": "rembordage_sans_couture", "rayon_bord_min": 8.0,
        "notes": "Le plus hygienique ; aspect moins noble.",
        "regles": _regles_base("enduit fin, tenue type cuir", "agrafage sous le plateau", "aretes vives possibles"),
    },
}

#: Anciennes cles conservees pour ne rien casser.
ALIAS = {"cuir_pleine_fleur": "cuir_classique_pleine_fleur", "cuir_synthetique_pu": "cuir_synthetique_hq"}

GARNISSAGES = _CatalogueAvecAlias(_ENTREES, ALIAS)


def resoudre(cle):
    """Cle canonique d'un garnissage (resout les alias)."""
    return GARNISSAGES.resoudre(cle)


def rembourrage_recommande(cle):
    """Rembourrage recommande [mm], y compris les valeurs relatives (cuir vegan)."""
    ent = GARNISSAGES[cle]
    if ent.get("epaisseur_rembourrage_recommandee") is not None:
        return ent["epaisseur_rembourrage_recommandee"]
    return GARNISSAGES[GARNISSAGE_REFERENCE]["epaisseur_rembourrage_recommandee"] + ent.get("ecart_rembourrage", 0.0)


def coloris_valide(cle, coloris):
    return cle in GARNISSAGES and coloris in GARNISSAGES[cle]["coloris"]
