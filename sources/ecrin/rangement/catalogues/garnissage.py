# -*- coding: utf-8 -*-
"""Catalogue cuirs et garnissages (fonds de tiroir garnis, portes capitonnees,
passants et sangles des rateliers, doublures).

REGLE : familles et teintes reprises EXACTEMENT des autres gammes (Equinox,
Neogothique, Incognito, Tantra, GammeCuir), avec leur source. Les cles
Tantra qui entrent en collision avec Incognito (cuir_cognac, cuir_noir) sont
prefixees ``tantra_``. Aucune teinte n'est ajoutee. ``TEINTES_CUIR`` est calcule a partir
des familles « cuir » (veritable, vegan, synthetique, compose, doublure) ;
les tissus (Incognito, Equinox) sont conserves pour les fonds et habillages
mais ne fournissent pas de teinte de cuir.

Champs : ``nom``, ``famille``, ``coloris`` (cles de teinte, reprises telles
quelles), ``epaisseur`` [mm], ``cout`` (categorie de la gamme source),
``usage_rangement`` (proposition, À VALIDER), ``gamme``, ``source``.
"""

from .. import sources as S

#: Familles considerees comme « cuir » pour les teintes de cuir.
FAMILLES_CUIR = ("cuir", "cuir_vegan", "cuir_synthetique", "cuir_veritable", "cuir_compose",
                 "synthetique", "doublure", "simili")

GARNISSAGES = {
    # --- Equinox (EQ_GARN) -------------------------------------------------
    "cuir_classique_pleine_fleur": {
        "nom": "Cuir classique pleine fleur", "famille": "cuir", "gamme": "Equinox",
        "coloris": ["noir", "cognac", "havane", "vert_bouteille", "bleu_nuit"], "coloris_defaut": "cognac",
        "epaisseur": 1.8, "cout": "eleve", "source": S.EQ_GARN + " (cuir_classique_pleine_fleur)",
        "usage_rangement": "portes capitonnees, fonds de tiroir garnis, dessus de coffre",
    },
    "cuir_vegan": {
        "nom": "Cuir vegan (sans cuir veritable)", "famille": "cuir_vegan", "gamme": "Equinox",
        "coloris": ["noir", "blanc", "cognac", "vert_olive", "bordeaux"], "coloris_defaut": "cognac",
        "epaisseur": 1.35, "cout": "moyen", "source": S.EQ_GARN + " (cuir_vegan)",
        "usage_rangement": "fonds de tiroir, habillage de portes",
    },
    "tissu_krypton": {
        "nom": "Tissu Krypton (tissu technique dense)", "famille": "tissu", "gamme": "Equinox",
        "coloris": ["noir", "gris_anthracite", "bordeaux", "bleu_marine"], "coloris_defaut": "noir",
        "epaisseur": 2.5, "cout": "bas_moyen", "source": S.EQ_GARN + " (tissu_krypton)",
        "usage_rangement": "fonds de tiroir (absorbe : membrane PU recommandee par Equinox)",
    },
    "cuir_synthetique_hq": {
        "nom": "Cuir synthetique haute qualite (PU haute densite)", "famille": "cuir_synthetique",
        "gamme": "Equinox", "coloris": ["noir", "cognac", "gris"], "coloris_defaut": "cognac",
        "epaisseur": 1.1, "cout": "moyen", "source": S.EQ_GARN + " (cuir_synthetique_hq)",
        "usage_rangement": "fonds lessivables (resiste aux desinfectants usuels)",
    },
    "tissu_technique_enduit": {
        "nom": "Tissu technique enduit PU (type medical)", "famille": "tissu_enduit", "gamme": "Equinox",
        "coloris": ["noir", "cognac"], "coloris_defaut": "noir",
        "epaisseur": 0.7, "cout": "moyen", "source": S.EQ_GARN + " (tissu_technique_enduit)",
        "usage_rangement": "fonds de tiroir hygieniques (instruments au contact de la peau)",
    },
    # --- Neogothique (NEO_GARN) --------------------------------------------
    "cuir_sellier_fin_noir": {
        "nom": "Cuir sellier fin noir (vachette + ame + rembourrage + doublure agneau)", "famille": "cuir_compose",
        "gamme": "Neogothique", "coloris": ["noir"], "coloris_defaut": "noir",
        "epaisseur": 7.5, "cout": "tres_eleve", "source": S.NEO_GARN + " (cuir_sellier_fin_noir)",
        "usage_rangement": "berceaux / supports d'exposition rembourres",
    },
    "cuir_renforce_double_noir": {
        "nom": "Cuir renforce double (harnais + doublure + ame)", "famille": "cuir_compose",
        "gamme": "Neogothique", "coloris": ["noir"], "coloris_defaut": "noir",
        "epaisseur": 6.5, "cout": "tres_eleve", "source": S.NEO_GARN + " (cuir_renforce_double_noir)",
        "usage_rangement": "passants porteurs (ratelier a sangles)",
    },
    "cuir_harnais_noir": {
        "nom": "Cuir de harnais tannage vegetal noir", "famille": "cuir_veritable", "gamme": "Neogothique",
        "coloris": ["noir", "brun_fonce"], "coloris_defaut": "noir",
        "epaisseur": 4.0, "cout": "eleve", "source": S.NEO_GARN + " (cuir_harnais_noir)",
        "usage_rangement": "passants, boucles de suspension des instruments, tirettes de tiroir",
    },
    "cuir_synthetique_pu_noir": {
        "nom": "Cuir synthetique PU haute densite noir (sur ame sangle)", "famille": "synthetique",
        "gamme": "Neogothique", "coloris": ["noir"], "coloris_defaut": "noir",
        "epaisseur": 5.0, "cout": "moyen", "source": S.NEO_GARN + " (cuir_synthetique_pu_noir)",
        "usage_rangement": "passants lessivables",
    },
    "cuir_pleine_fleur_noir": {
        "nom": "Cuir pleine fleur noir d'ameublement", "famille": "cuir_veritable", "gamme": "Neogothique",
        "coloris": ["noir"], "coloris_defaut": "noir",
        "epaisseur": 1.8, "cout": "eleve", "source": S.NEO_GARN + " (cuir_pleine_fleur_noir)",
        "usage_rangement": "portes capitonnees, fonds de tiroir",
    },
    "doublure_agneau_noir": {
        "nom": "Doublure cuir d'agneau noir", "famille": "doublure", "gamme": "Neogothique",
        "coloris": ["noir"], "coloris_defaut": "noir",
        "epaisseur": 1.2, "cout": "moyen", "source": S.NEO_GARN + " (doublure_agneau_noir)",
        "usage_rangement": "garniture interieure des alveoles (bijoux, petits accessoires)",
    },
    # --- Incognito (INC_PARAM, REVETEMENTS_BASE) ----------------------------
    "velours": {
        "nom": "Velours", "famille": "tissu", "gamme": "Incognito",
        "coloris": ["gris_souris", "vert_sauge", "creme", "marine", "taupe"], "coloris_defaut": "gris_souris",
        "epaisseur": 2.0, "cout": None, "source": S.INC_PARAM + " (VELOURS)",
        "usage_rangement": "facades discretes, fonds de tiroir",
    },
    "lin": {
        "nom": "Lin", "famille": "tissu", "gamme": "Incognito",
        "coloris": ["naturel", "ivoire", "gris_clair", "terre"], "coloris_defaut": "naturel",
        "epaisseur": 1.5, "cout": None, "source": S.INC_PARAM + " (LIN)",
        "usage_rangement": "facades discretes",
    },
    "laine_bouclee": {
        "nom": "Laine bouclee", "famille": "tissu", "gamme": "Incognito",
        "coloris": ["ivoire", "grege", "charbon", "camel"], "coloris_defaut": "ivoire",
        "epaisseur": 3.5, "cout": None, "source": S.INC_PARAM + " (LAINE_BOUCLEE)",
        "usage_rangement": "dessus de coffre-banquette discret",
    },
    "tissu_chine": {
        "nom": "Tissu chine", "famille": "tissu", "gamme": "Incognito",
        "coloris": ["gris_chine", "beige_chine", "bleu_gris"], "coloris_defaut": "gris_chine",
        "epaisseur": 2.0, "cout": None, "source": S.INC_PARAM + " (TISSU_CHINE)",
        "usage_rangement": "facades discretes",
    },
    "cuir_cognac": {
        "nom": "Cuir cognac (interieur cache)", "famille": "cuir", "gamme": "Incognito",
        "coloris": ["cognac"], "coloris_defaut": "cognac",
        "epaisseur": 2.0, "cout": None, "source": S.INC_PARAM + " (CUIR_COGNAC, usage interieur_cache)",
        "usage_rangement": "interieur des armoires discretes (regle « zero cuir visible »)",
    },
    "cuir_noir": {
        "nom": "Cuir noir (interieur cache)", "famille": "cuir", "gamme": "Incognito",
        "coloris": ["noir"], "coloris_defaut": "noir",
        "epaisseur": 2.0, "cout": None, "source": S.INC_PARAM + " (CUIR_NOIR, usage interieur_cache)",
        "usage_rangement": "interieur des armoires discretes",
    },
    "cuir_sobre_facade": {
        "nom": "Cuir sobre de facade (derogation)", "famille": "cuir", "gamme": "Incognito",
        "coloris": ["cognac_clair", "havane", "noir_mat"], "coloris_defaut": "havane",
        "epaisseur": 2.0, "cout": None, "source": S.INC_PARAM + " (CUIR_SOBRE_FACADE, exterieur_derogation)",
        "usage_rangement": "facade d'armoire si derogation a « zero cuir visible »",
    },
    # --- Tantra (TANTRA_PARAM, REVETEMENTS) : coloris explicites seulement pour les cuirs ---
    "tantra_cuir_cognac": {
        "nom": "Cuir pleine fleur pigmente cognac", "famille": "cuir", "gamme": "Tantra",
        "coloris": ["cognac"], "coloris_defaut": "cognac", "epaisseur": 1.3, "cout": None,
        "source": S.TANTRA_PARAM + " (CUIR_COGNAC : lavable, deperlant)",
        "usage_rangement": "fonds de tiroir et portes capitonnees lavables",
    },
    "tantra_cuir_noir": {
        "nom": "Cuir pleine fleur pigmente noir", "famille": "cuir", "gamme": "Tantra",
        "coloris": ["noir"], "coloris_defaut": "noir", "epaisseur": 1.3, "cout": None,
        "source": S.TANTRA_PARAM + " (CUIR_NOIR)", "usage_rangement": "idem, masque mieux les marques",
    },
    "simili_pu_medical": {
        "nom": "Simili-cuir PU qualite medicale", "famille": "simili", "gamme": "Tantra",
        "coloris": [], "coloris_defaut": None, "epaisseur": 1.0, "cout": None,
        "source": S.TANTRA_PARAM + " (SIMILI_PU_MEDICAL, coloris non precises)",
        "usage_rangement": "alveoles d'instruments desinfectables",
    },
    "simili_vinyle_marine": {
        "nom": "Vinyle marine graine", "famille": "simili", "gamme": "Tantra",
        "coloris": [], "coloris_defaut": None, "epaisseur": 1.1, "cout": None,
        "source": S.TANTRA_PARAM + " (SIMILI_VINYLE_MARINE)", "usage_rangement": "fonds tres sollicites",
    },
    "tissu_technique_deperlant": {
        "nom": "Tissu technique deperlant (type Crypton / Aquaclean)", "famille": "tissu", "gamme": "Tantra",
        "coloris": [], "coloris_defaut": None, "epaisseur": 1.2, "cout": None,
        "source": S.TANTRA_PARAM + " (TISSU_TECHNIQUE_DEPERLANT)", "usage_rangement": "facades discretes lavables",
    },
    "velours_deperlant": {
        "nom": "Velours ras deperlant", "famille": "tissu", "gamme": "Tantra",
        "coloris": [], "coloris_defaut": None, "epaisseur": 1.4, "cout": None,
        "source": S.TANTRA_PARAM + " (VELOURS_DEPERLANT)", "usage_rangement": "facades discretes",
    },
    "bouclette": {
        "nom": "Laine bouclee (bouclette)", "famille": "tissu", "gamme": "Tantra",
        "coloris": [], "coloris_defaut": None, "epaisseur": 2.5, "cout": None,
        "source": S.TANTRA_PARAM + " (BOUCLETTE, non lavable)", "usage_rangement": "jamais en zone de contact",
    },
    # --- GammeCuir (GC_CUIRS : CUIRS et DOUBLURES) ; epaisseur = milieu de la plage ---
    "vachette_vegetale_pleine_fleur": {
        "nom": "Vachette pleine fleur tannage vegetal (croupon)", "famille": "cuir_veritable", "gamme": "GammeCuir",
        "coloris": ["cognac", "tan", "havane", "noir", "brun_fonce", "bordeaux", "vert_bouteille", "bleu_nuit"],
        "coloris_defaut": "cognac", "epaisseur": 3.5, "epaisseur_plage": (2.0, 5.0), "cout": "eleve",
        "source": S.GC_CUIRS + " (CUIRS)", "usage_rangement": "passants, tirettes, assorti aux accessoires GammeCuir",
    },
    "cuir_harnais_vegetal": {
        "nom": "Cuir de harnais tannage vegetal, nourri", "famille": "cuir_veritable", "gamme": "GammeCuir",
        "coloris": ["noir", "brun_fonce", "havane", "cognac"], "coloris_defaut": "noir",
        "epaisseur": 4.25, "epaisseur_plage": (3.5, 5.0), "cout": "eleve",
        "source": S.GC_CUIRS + " (CUIRS)", "usage_rangement": "sangles porteuses des rateliers",
    },
    "vachette_chrome_pleine_fleur": {
        "nom": "Vachette pleine fleur tannage chrome (souple)", "famille": "cuir_veritable", "gamme": "GammeCuir",
        "coloris": ["noir", "cognac", "bordeaux", "bleu_nuit"], "coloris_defaut": "noir",
        "epaisseur": 2.75, "epaisseur_plage": (2.0, 3.5), "cout": "moyen",
        "source": S.GC_CUIRS + " (CUIRS)", "usage_rangement": "garnitures souples",
    },
    "agneau_pleine_fleur": {
        "nom": "Doublure agneau pleine fleur", "famille": "doublure", "gamme": "GammeCuir",
        "coloris": ["noir", "cognac", "tan", "havane", "bordeaux"], "coloris_defaut": "noir",
        "epaisseur": 1.15, "epaisseur_plage": (0.8, 1.5), "cout": None,
        "source": S.GC_CUIRS + " (DOUBLURES)", "usage_rangement": "alveoles de rangement des accessoires cuir",
    },
    "veau_velours": {
        "nom": "Veau velours (croute retournee)", "famille": "doublure", "gamme": "GammeCuir",
        "coloris": ["noir", "brun_fonce", "tan", "bordeaux"], "coloris_defaut": "noir",
        "epaisseur": 1.5, "epaisseur_plage": (1.0, 2.0), "cout": None,
        "source": S.GC_CUIRS + " (DOUBLURES)", "usage_rangement": "fonds antiderapants (les objets ne glissent pas)",
    },
}

#: Revetements Incognito autorises a l'interieur seulement (regle « zero cuir visible »).
INTERIEUR_CACHE_SEULEMENT = ("cuir_cognac", "cuir_noir")


def _teintes_cuir():
    res = {}
    for cle, ent in GARNISSAGES.items():
        if ent["famille"] not in FAMILLES_CUIR:
            continue
        for c in ent["coloris"]:
            res.setdefault(c, []).append("%s:%s" % (ent["gamme"], cle))
    return res


#: teinte -> liste « Gamme:famille » qui la definissent (calcule, rien d'ajoute).
TEINTES_CUIR = _teintes_cuir()


def est_cuir(cle):
    return cle in GARNISSAGES and GARNISSAGES[cle]["famille"] in FAMILLES_CUIR


def coloris_valide(cle, coloris):
    return cle in GARNISSAGES and coloris in GARNISSAGES[cle]["coloris"]
