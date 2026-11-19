# -*- coding: utf-8 -*-
"""Catalogue des essences de la gamme Rangement.

REGLE : on reprend EXACTEMENT les essences deja definies dans les autres
gammes (union Equinox + Neogothique + Incognito + Aboutissants + Tantra),
sans en ajouter. ``famille`` : massif, lamelle_colle ou contreplaque (Tantra). Chaque propriete cite sa source ; quand les gammes divergent, la
valeur retenue est indiquee et les autres sont conservees dans
``valeurs_autres_gammes`` pour arbitrage.

Proprietes (bois sec ~12 %) :

- ``densite`` [kg/m3], ``module_elasticite`` (MOE) [MPa],
  ``resistance_flexion`` (MOR moyen) [MPa] : source principale Equinox
  (The Wood Database / Wood Handbook) quand l'essence y figure ;
- ``sigma_adm_flexion`` [MPa] : contrainte admissible de conception reprise
  d'Incognito (fm,k / 2,8 a 3,5, coefficient de securite deja inclus) ;
  ``None`` = absente des autres gammes -> À VALIDER, et ``regles`` utilise
  alors la plus faible valeur du catalogue avec une alerte ;
- ``teinte`` : texte repris de la gamme source (``None`` = À VALIDER) ;
- ``gammes`` : gammes ou l'essence est definie ;
- ``a_valider`` : liste des champs sans source.
"""

from .. import sources as S

ESSENCES = {
    "frene": {
        "nom": "Frene europeen", "nom_latin": "Fraxinus excelsior", "famille": "massif",
        "densite": 680.0, "module_elasticite": 12310.0, "resistance_flexion": 103.6,
        "sigma_adm_flexion": 14.0, "tenue_vis": 3,
        "teinte": "clair, blond",
        "gammes": ("Equinox", "Incognito", "Aboutissants", "Tantra"),
        "source": S.EQ_BOIS + " (frene : densite, MOE, MOR, teinte) ; " + S.INC_PARAM + " (FRENE : sigma_adm 14 MPa)",
        "valeurs_autres_gammes": {"Incognito": {"densite": 690.0, "module_elasticite": 13000.0},
                                  "Aboutissants": {"densite": 690.0, "sigma_adm_flexion": 14.0},
                                  "Tantra": {"densite": 690.0, "module_elasticite": 13000.0, "fm_k": 40.0},
                                  "Tantra_lib": {"densite": 690.0, "module_elasticite": 12500.0, "fm_k": 38.0}},
        "notes": "Essence de reference Equinox. Vis : avant-trou obligatoire (Equinox).",
        "a_valider": (),
    },
    "frene_blanc": {
        "nom": "Frene blanc d'Amerique", "nom_latin": "Fraxinus americana", "famille": "massif",
        "densite": 675.0, "module_elasticite": 12000.0, "resistance_flexion": 103.5,
        "sigma_adm_flexion": None, "tenue_vis": 3,
        "teinte": "clair",
        "gammes": ("Equinox",),
        "source": S.EQ_BOIS + " (frene_blanc)",
        "valeurs_autres_gammes": {},
        "notes": "Espece menacee (agrile du frene) : verifier la provenance (Equinox).",
        "a_valider": ("sigma_adm_flexion",),
    },
    "chene": {
        "nom": "Chene (pedoncule / sessile)", "nom_latin": "Quercus robur / Quercus petraea", "famille": "massif",
        "densite": 675.0, "module_elasticite": 10600.0, "resistance_flexion": 97.1,
        "sigma_adm_flexion": 14.0, "tenue_vis": 4,
        "teinte": "blond a brun clair, maillure",
        "gammes": ("Equinox", "Neogothique", "Incognito", "Aboutissants", "Tantra"),
        "source": S.EQ_BOIS + " (chene) ; " + S.INC_PARAM + " (CHENE : sigma_adm 14 MPa)",
        "valeurs_autres_gammes": {
            "Neogothique": {"densite": 710.0, "module_elasticite": 11000.0, "resistance_flexion": 97.0,
                            "teinte": "brun moyen, fonce a l'huile/cire noire ; maille apparente sur quartier"},
            "Incognito": {"densite": 710.0, "module_elasticite": 12500.0},
            "Aboutissants": {"densite": 710.0, "sigma_adm_flexion": 14.0},
            "Tantra": {"densite": 710.0, "module_elasticite": 12500.0, "fm_k": 40.0},
            "Tantra_lib": {"densite": 700.0, "module_elasticite": 11000.0, "fm_k": 30.0}},
        "notes": "Tanins : taches noires au contact du fer/acier humide (Equinox, Neogothique) -> "
                 "inox 316, laiton, ou ferrures cirees/vernies.",
        "a_valider": (),
    },
    "chene_fume": {
        "nom": "Chene fume (fumage ammoniacal)", "nom_latin": "Quercus petraea / Quercus robur", "famille": "massif",
        "densite": 710.0, "module_elasticite": 11000.0, "resistance_flexion": 97.0,
        "sigma_adm_flexion": 14.0, "tenue_vis": 4,
        "teinte": "brun-gris profond a presque noir selon duree de fumage",
        "gammes": ("Neogothique",),
        "source": S.NEO_BOIS + " (chene_fume) ; sigma_adm = celle du chene (" + S.INC_PARAM +
                  "), Neogothique indiquant que le fumage ne modifie pas la mecanique",
        "valeurs_autres_gammes": {},
        "notes": "Usiner et assembler a blanc AVANT fumage (penetration 1-3 mm) - Neogothique.",
        "a_valider": (),
    },
    "noyer": {
        "nom": "Noyer commun / europeen", "nom_latin": "Juglans regia", "famille": "massif",
        "densite": 640.0, "module_elasticite": 10810.0, "resistance_flexion": 111.5,
        "sigma_adm_flexion": 12.0, "tenue_vis": 4,
        "teinte": "brun, contraste fort avec cuir cognac",
        "gammes": ("Equinox", "Neogothique", "Incognito", "Aboutissants", "Tantra"),
        "source": S.EQ_BOIS + " (noyer) ; " + S.INC_PARAM + " (NOYER : sigma_adm 12 MPa)",
        "valeurs_autres_gammes": {
            "Neogothique": {"densite": 640.0, "module_elasticite": 10800.0, "resistance_flexion": 111.0,
                            "teinte": "brun chocolat a veines sombres, s'eclaircit legerement a la lumiere"},
            "Incognito": {"densite": 650.0, "module_elasticite": 11600.0},
            "Aboutissants": {"densite": 650.0, "sigma_adm_flexion": 12.0},
            "Tantra": {"densite": 650.0, "module_elasticite": 11600.0, "fm_k": 35.0},
            "Tantra_lib": {"densite": 640.0, "module_elasticite": 11000.0, "fm_k": 30.0}},
        "notes": "Pas de classe EN 1912 publiee (Neogothique : hypothese D27 a confirmer).",
        "a_valider": (),
    },
    "noyer_noir": {
        "nom": "Noyer noir d'Amerique", "nom_latin": "Juglans nigra", "famille": "massif",
        "densite": 610.0, "module_elasticite": 11590.0, "resistance_flexion": 100.7,
        "sigma_adm_flexion": None, "tenue_vis": 4,
        "teinte": "brun chocolat",
        "gammes": ("Equinox", "Neogothique"),
        "source": S.EQ_BOIS + " (noyer_noir)",
        "valeurs_autres_gammes": {"Neogothique": {"densite": 610.0, "module_elasticite": 11600.0,
                                                  "resistance_flexion": 101.0,
                                                  "teinte": "brun tres fonce, violace - le plus sombre des noyers"}},
        "notes": "Plus disponible en fortes sections que le noyer europeen (Neogothique).",
        "a_valider": ("sigma_adm_flexion",),
    },
    "hetre": {
        "nom": "Hetre europeen", "nom_latin": "Fagus sylvatica", "famille": "massif",
        "densite": 710.0, "module_elasticite": 14310.0, "resistance_flexion": 110.1,
        "sigma_adm_flexion": 14.0, "tenue_vis": 4,
        "teinte": "clair rosé",
        "gammes": ("Equinox", "Incognito", "Tantra"),
        "source": S.EQ_BOIS + " (hetre) ; " + S.INC_PARAM + " (HETRE : sigma_adm 14 MPa)",
        "valeurs_autres_gammes": {"Incognito": {"densite": 720.0, "module_elasticite": 14000.0},
                                  "Tantra": {"densite": 720.0, "module_elasticite": 14000.0, "fm_k": 40.0}},
        "notes": "Retrait important : sensible aux variations d'humidite (Equinox) - eviter les grands panneaux massifs.",
        "a_valider": (),
    },
    "erable_sycomore": {
        "nom": "Erable sycomore", "nom_latin": "Acer pseudoplatanus", "famille": "massif",
        "densite": 615.0, "module_elasticite": 9920.0, "resistance_flexion": 98.1,
        "sigma_adm_flexion": None, "tenue_vis": 4,
        "teinte": "tres clair, blanc creme",
        "gammes": ("Equinox",),
        "source": S.EQ_BOIS + " (erable_sycomore)",
        "valeurs_autres_gammes": {},
        "notes": "Moins rigide que le frene (-19 % de MOE).",
        "a_valider": ("sigma_adm_flexion",),
    },
    "erable_dur": {
        "nom": "Erable dur (a sucre)", "nom_latin": "Acer saccharum", "famille": "massif",
        "densite": 705.0, "module_elasticite": 12620.0, "resistance_flexion": 109.0,
        "sigma_adm_flexion": None, "tenue_vis": 5,
        "teinte": "tres clair",
        "gammes": ("Equinox",),
        "source": S.EQ_BOIS + " (erable_dur)",
        "valeurs_autres_gammes": {},
        "notes": "Rigide et dur, excellente tenue de vis.",
        "a_valider": ("sigma_adm_flexion",),
    },
    "merisier": {
        "nom": "Merisier", "nom_latin": "Prunus avium", "famille": "massif",
        "densite": 610.0, "module_elasticite": 10300.0, "resistance_flexion": None,
        "sigma_adm_flexion": 10.0, "tenue_vis": None,
        "teinte": None,
        "gammes": ("Incognito",),
        "source": S.INC_PARAM + " (MERISIER : densite 610, MOE 10300, sigma_adm 10 MPa)",
        "valeurs_autres_gammes": {},
        "notes": "Defini seulement dans Incognito, sans MOR moyen ni teinte.",
        "a_valider": ("resistance_flexion", "teinte", "tenue_vis"),
    },
    "lamelle_hetre": {
        "nom": "Lamelle-colle de hetre (type BauBuche GL75)", "nom_latin": "Fagus sylvatica (lamibois)",
        "famille": "lamelle_colle",
        "densite": 800.0, "module_elasticite": 16800.0, "resistance_flexion": None,
        "sigma_adm_flexion": None, "tenue_vis": None,
        "teinte": None,
        "gammes": ("Tantra",),
        "source": S.TANTRA_PARAM + " (LAMELLE_HETRE : densite 800, E 16800, fm,k 75)",
        "valeurs_autres_gammes": {"Tantra": {"fm_k": 75.0, "fv_k": 4.5}},
        "notes": "Tres resistant : longerons fins, montants d'armoire elances ; chant lamelle assume ou plaque.",
        "a_valider": ("resistance_flexion", "sigma_adm_flexion", "teinte", "tenue_vis"),
    },
    "contreplaque_bouleau": {
        "nom": "Contreplaque de bouleau (cintre chez Tantra)", "nom_latin": "Betula sp. (contreplaque)",
        "famille": "contreplaque",
        "densite": 680.0, "module_elasticite": 9000.0, "resistance_flexion": None,
        "sigma_adm_flexion": None, "tenue_vis": None,
        "teinte": None,
        "gammes": ("Tantra", "Equinox"),
        "source": S.TANTRA_PARAM + " (CONTREPLAQUE_BOULEAU : densite 680, E 9000, fm,k 35) ; "
                  + S.EQ_PARAM + " (garnissage.epaisseur_support : contreplaque bouleau, sans proprietes)",
        "valeurs_autres_gammes": {"Tantra": {"fm_k": 35.0, "fv_k": 3.0}},
        "notes": "Fonds, supports garnis, fonds de tiroir ; pas une essence de facade massive.",
        "a_valider": ("resistance_flexion", "sigma_adm_flexion", "teinte", "tenue_vis"),
    },
}

#: Finitions du bois : quatre reprises de Neogothique (FINITIONS_BOIS), trois de
#: Tantra (TantraGamme/lib FINITIONS) ; Equinox, Incognito et Aboutissants n'en
#: definissent pas.
FINITIONS_BOIS = {
    "huile_cire_noire": {"nom": "Huile dure + cire teintee noire", "source": S.NEO_BOIS,
                         "essences": None, "lessivable": False, "a_valider": False},
    "cire_naturelle": {"nom": "Cire d'abeille / carnauba incolore", "source": S.NEO_BOIS,
                       "essences": None, "lessivable": False, "a_valider": False},
    "fumage_ammoniac": {"nom": "Fumage a l'ammoniaque (reaction avec les tanins)", "source": S.NEO_BOIS,
                        "essences": ("chene", "chene_fume"), "lessivable": False, "a_valider": False},
    "teinte_acetate_fer": {"nom": "Ebonisation a l'acetate de fer", "source": S.NEO_BOIS,
                           "essences": ("chene", "chene_fume"), "lessivable": False, "a_valider": False},
    # Reprises de Tantra (TantraGamme/lib FINITIONS : nettoyabilite 1-5)
    "huile_cire": {"nom": "Huile-cire dure", "source": S.TANTRA_LIB + " (FINITIONS, nettoyabilite 3)",
                   "essences": None, "lessivable": False, "a_valider": False},
    "vernis_pu_mat": {"nom": "Vernis PU bi-composant mat", "source": S.TANTRA_LIB + " (FINITIONS, nettoyabilite 5)",
                      "essences": None, "lessivable": True, "a_valider": False},
    "huile_teck": {"nom": "Huile simple", "source": S.TANTRA_LIB + " (FINITIONS, nettoyabilite 2)",
                   "essences": None, "lessivable": False, "a_valider": False},
}


def finition_compatible(essence, finition):
    """True si la finition est admise sur l'essence (regle Neogothique : fumage
    et acetate de fer reserves au chene, qui seul contient assez de tanins)."""
    ent = FINITIONS_BOIS.get(finition)
    if ent is None or essence not in ESSENCES:
        return False
    return ent["essences"] is None or essence in ent["essences"]


def sigma_adm(essence):
    """(contrainte admissible de flexion [MPa], methode).

    - ``"incognito"`` : valeur sourcee (Incognito, securite incluse) ;
    - ``"repli_min_catalogue"`` : l'essence n'a pas de valeur sourcee ; on prend
      la PLUS FAIBLE valeur sourcee du catalogue (prudent), a signaler comme
      alerte par ``regles``. (Le repli « MOR / 3 » d'Equinox donnerait ~2 fois
      plus : non retenu, car moins prudent que les valeurs Incognito.)
    """
    v = ESSENCES[essence]["sigma_adm_flexion"]
    if v is not None:
        return v, "incognito"
    return min(e["sigma_adm_flexion"] for e in ESSENCES.values() if e["sigma_adm_flexion"]), "repli_min_catalogue"
