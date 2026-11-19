# -*- coding: utf-8 -*-
"""Couche 2 - Catalogue des essences sombres de la gamme Neogothique.

Chaque entree decrit une essence massive (bois a 12 % d'humidite) :

- ``densite_kg_m3``                : masse volumique a 12 % (kg/m3).
- ``module_elasticite_mpa``        : module d'elasticite moyen en flexion,
  bois sans defaut (MPa).
- ``resistance_flexion_mpa``       : module de rupture (MOR) bois sans
  defaut, eprouvette normalisee (MPa) - valeur *physique*, pas de calcul.
- ``resistance_flexion_calcul_mpa``: resistance caracteristique f_m,k
  utilisee pour les verifications (classe de resistance EN 338 ou
  hypothese prudente si l'essence n'est pas classee).
- ``compression_perp_mpa``         : f_c,90,k, compression perpendiculaire
  au fil (matage dans les mortaises / fourreaux).
- ``cisaillement_mpa``             : f_v,k, cisaillement (MPa).
- ``retrait_tangentiel_coef`` / ``retrait_radial_coef`` : variation
  dimensionnelle en % par % de variation d'humidite (dimensionne les
  mortaises oblongues des plateaux massifs).
- ``classe_resistance``            : classe EN 338 retenue (ou hypothese).
- ``teinte`` / ``aspect``          : rendu, coherence avec l'identite.
- ``sources``                      : references des valeurs.
- ``regles``                       : regles declaratives appliquees par
  ``neogothique.regles`` quand on passe A cette essence (voir la syntaxe
  dans ``neogothique/regles.py``).

Sources principales (valeurs indicatives, a recouper avec la fiche du
fournisseur et un classement visuel du lot) :

- USDA Forest Products Laboratory, *Wood Handbook - Wood as an Engineering
  Material*, GTR-282 (2021) : ch. 4 (coefficients de variation
  dimensionnelle, tab. 4-5) et ch. 5 (proprietes mecaniques, tab. 5-3a).
- The Wood Database (wood-database.com), fiches English Oak, European
  Walnut, Black Walnut (MOR, MOE, densite a 12 %).
- NF EN 338:2016 (classes de resistance D) et NF EN 1912 (affectation des
  essences/tri visuel aux classes ; chene francais : D24 a D30 selon tri).
- CIRAD / FCBA : fiches essences (chene, noyer) pour recoupement.
"""

#: Regles communes a toutes les essences : quand on change d'essence, la
#: grammaire recalcule masse, epaisseur mini de platine (resistance), cote mini
#: des pieds (rigidite) et jeu des mortaises oblongues (retrait).
REGLES_ESSENCE = [
    {
        "id": "bois_masse",
        "operation": "recalcul",
        "propriete": "densite_kg_m3",
        "explication": "Masse des pieces bois recalculee par la grammaire (densite {ancien_val:g} -> "
                       "{nouveau_val:g} kg/m3, x{ratio_brut:.3f}) ; la stabilite au renversement est reverifiee.",
    },
    {
        "id": "bois_epaisseur_platine",
        "cibles": ["*.platine.epaisseur"],
        "operation": "echelle",
        "propriete": "resistance_flexion_calcul_mpa",
        "exposant": 0.5,
        "arrondi": 1.0,
        "mini": 35.0,
        "explication": "Flexion : sigma = 6M/(b.h^2) => h proportionnelle a f_m^-1/2 "
                       "(f_m,k {ancien_val:g} -> {nouveau_val:g} MPa, facteur {ratio:.3f}).",
    },
    {
        "id": "bois_cote_pieds",
        "cibles": ["*.pied.cote"],
        "operation": "echelle",
        "propriete": "module_elasticite_mpa",
        "exposant": 0.25,
        "arrondi": 5.0,
        "mini": 80.0,
        "explication": "Rigidite des pieds courts (flambement/flexion) : I ~ a^4 => cote proportionnelle "
                       "a E^-1/4 (E {ancien_val:g} -> {nouveau_val:g} MPa, facteur {ratio:.3f}), arrondi 5 mm.",
    },
    {
        "id": "bois_mortaise_oblongue",
        "cibles": ["tolerances.jeu_mortaise_oblongue"],
        "operation": "echelle",
        "propriete": "retrait_tangentiel_coef",
        "exposant": -1.0,
        "arrondi": 0.5,
        "mini": 1.0,
        "explication": "Plateau massif : le jeu des mortaises oblongues suit le retrait tangentiel "
                       "({ancien_val:g} -> {nouveau_val:g} %/%, facteur {ratio:.3f}).",
    },
]

BOIS = {
    "chene": {
        "nom": "Chene massif (chene sessile / pedoncule)",
        "nom_latin": "Quercus petraea / Quercus robur",
        "famille": "feuillu_dur",
        "densite_kg_m3": 710.0,
        "module_elasticite_mpa": 11000.0,
        "resistance_flexion_mpa": 97.0,
        "resistance_flexion_calcul_mpa": 30.0,
        "compression_perp_mpa": 8.0,
        "cisaillement_mpa": 4.0,
        "retrait_tangentiel_coef": 0.365,
        "retrait_radial_coef": 0.180,
        "classe_resistance": "D30 (EN 338) - tri visuel EN 1912 exige",
        "teinte": "brun moyen, fonce a l'huile/cire noire ; maille apparente sur quartier",
        "aspect": "maille et cernes marques, tres 'medieval'",
        "finitions_compatibles": ["huile_cire_noire", "cire_naturelle", "fumage_ammoniac", "teinte_acetate_fer"],
        "sources": ["Wood Handbook GTR-282 tab. 4-5 (chene blanc, coef. retrait)",
                    "The Wood Database - English Oak (MOR 97 MPa, densite ~675-710)",
                    "EN 338:2016 classe D30 (f_m,k 30 MPa, E0,mean 11 000 MPa)"],
        "remarques": "Tanins : tache noire au contact du fer humide (reaction tanin-fer) -> "
                     "isoler les ferrures (cire, vernis) ou l'utiliser comme effet d'ebonisation.",
        "regles": list(REGLES_ESSENCE) + [
            {"id": "chene_tanins", "operation": "signaler",
             "explication": "Chene + fer : risque de taches noires (tanins). Finition cire/vernis sur "
                            "ferrures et bois avant montage, ou ferrures laiton."},
        ],
    },
    "chene_fume": {
        "nom": "Chene massif fume (fumage ammoniacal)",
        "nom_latin": "Quercus petraea / Quercus robur",
        "famille": "feuillu_dur",
        "densite_kg_m3": 710.0,
        "module_elasticite_mpa": 11000.0,
        "resistance_flexion_mpa": 97.0,
        "resistance_flexion_calcul_mpa": 30.0,
        "compression_perp_mpa": 8.0,
        "cisaillement_mpa": 4.0,
        "retrait_tangentiel_coef": 0.365,
        "retrait_radial_coef": 0.180,
        "classe_resistance": "D30 (EN 338) - proprietes inchangees par le fumage",
        "teinte": "brun-gris profond a presque noir selon duree de fumage",
        "aspect": "teinte dans la masse sur 1 a 3 mm seulement",
        "finitions_compatibles": ["fumage_ammoniac", "huile_cire_noire"],
        "sources": ["Memes valeurs que 'chene' (le fumage ne modifie pas la mecanique)"],
        "remarques": "Usiner, chanfreiner et assembler a blanc AVANT fumage.",
        "regles": list(REGLES_ESSENCE) + [
            {"id": "fume_finition", "cibles": ["bois.finition"], "operation": "fixer",
             "valeur": "fumage_ammoniac",
             "explication": "Chene fume : la finition devient 'fumage_ammoniac'."},
            {"id": "fume_usinage", "operation": "signaler",
             "explication": "Le fumage ne penetre que 1-3 mm : tous les usinages (mortaises, chanfreins "
                            "de {bois.chanfrein_aretes} mm) doivent etre faits avant fumage."},
        ],
    },
    "noyer": {
        "nom": "Noyer europeen massif",
        "nom_latin": "Juglans regia",
        "famille": "feuillu_mi_dur",
        "densite_kg_m3": 640.0,
        "module_elasticite_mpa": 10800.0,
        "resistance_flexion_mpa": 111.0,
        "resistance_flexion_calcul_mpa": 27.0,
        "compression_perp_mpa": 7.0,
        "cisaillement_mpa": 3.5,
        "retrait_tangentiel_coef": 0.274,
        "retrait_radial_coef": 0.190,
        "classe_resistance": "Non classe EN 1912 - hypothese prudente assimilee D27 (a confirmer)",
        "teinte": "brun chocolat a veines sombres, s'eclaircit legerement a la lumiere",
        "aspect": "fil fin, tres noble ; supporte bien les angles francs",
        "finitions_compatibles": ["huile_cire_noire", "cire_naturelle"],
        "sources": ["The Wood Database - European Walnut (MOR 111,5 MPa, E 10,8 GPa, densite 640)",
                    "Wood Handbook GTR-282 tab. 4-5 (noyer noir, coef. retrait, utilise par defaut)",
                    "f_m,k 27 MPa : hypothese prudente (aucune classe EN 1912 publiee pour J. regia)"],
        "remarques": "Bois plus cher et plus rare en fortes sections : platine en panneau colle "
                     "de 3-4 alaises, barres a queue d'aronde dessous contre le tuilage.",
        "regles": list(REGLES_ESSENCE),
    },
    "noyer_noir": {
        "nom": "Noyer noir d'Amerique massif",
        "nom_latin": "Juglans nigra",
        "famille": "feuillu_mi_dur",
        "densite_kg_m3": 610.0,
        "module_elasticite_mpa": 11600.0,
        "resistance_flexion_mpa": 101.0,
        "resistance_flexion_calcul_mpa": 27.0,
        "compression_perp_mpa": 6.9,
        "cisaillement_mpa": 3.5,
        "retrait_tangentiel_coef": 0.274,
        "retrait_radial_coef": 0.190,
        "classe_resistance": "Non classe EN 1912 - hypothese prudente assimilee D27 (a confirmer)",
        "teinte": "brun tres fonce, violace - le plus sombre des noyers",
        "aspect": "fil droit, plus disponible en fortes sections que le noyer europeen",
        "finitions_compatibles": ["huile_cire_noire", "cire_naturelle"],
        "sources": ["Wood Handbook GTR-282 tab. 5-3a et 4-5 (Black walnut)",
                    "The Wood Database - Black Walnut (MOR 101 MPa, E 11,6 GPa, densite 610)"],
        "remarques": "Alternative au noyer europeen si sections > 60 mm introuvables.",
        "regles": list(REGLES_ESSENCE),
    },
}

#: Finitions bois admises (choix de ``bois.finition``).
FINITIONS_BOIS = {
    "huile_cire_noire": "Huile dure + cire teintee noire : noircit les pores, aspect patine ancienne.",
    "cire_naturelle": "Cire d'abeille / carnauba incolore : garde la teinte naturelle.",
    "fumage_ammoniac": "Fumage a l'ammoniaque (chene uniquement, reaction avec les tanins).",
    "teinte_acetate_fer": "Ebonisation a l'acetate de fer (vinaigre + laine d'acier) : chene presque noir.",
}
