# -*- coding: utf-8 -*-
"""Couche 2 - Ferrures apparentes : metaux, finitions, composants, pivots.

Esthetique forge medievale : fer forge mat (acier doux forge) ou laiton mat.
Toutes les ferrures sont fixees SANS VIS : rivets forges traversants a
contre-plaque, embrevement, clavettes, goupilles.

Dictionnaires :

- ``METAUX``     : nuances (densite, module E, limite elastique Re, Rm,
  finition par defaut, sections commerciales) + ``regles`` de recalcul des
  sections au changement de metal.
- ``FINITIONS``  : traitements anticorrosion / aspect (compatibilite metal,
  protection 1-10, contact peau) + ``regles``.
- ``COMPOSANTS`` : description des ferrures de typologie (gond, loquet a pene,
  cremailleres, pignon, arbre, renvoi d'angle, penture, frette, rivet,
  palier) : parametres qui les pilotent et verification associee.
- ``PIVOTS``     : options de pivot des manilles (choix de
  ``entrave.manilles.pivot_cou`` / ``pivot_poignets``) + ``regles``.
- ``TERMINAISONS`` : terminaisons forgees des pentures (fleur de lys, queue
  d'aronde, trilobe, droite) : longueur de terminaison, temps de forge.
- ``HABILLAGES``  : habillage de la barre de calage (capot ajoure de
  lancettes, plaque decoupee de quadrilobes, aucun).
- ``DECORS_BARRE`` : decor de la barre crantee elle-meme (lisse, festonnee,
  ajouree) avec son taux d'enlevement de matiere -> regle de section nette.

Style v0.2 (« neogothique raffine ») : fers plus fins (28 x 4 au lieu de
40 x 5), rivets a tete goutte de suif (calotte) au lieu de tetes carrees,
terminaisons forgees ; chaque affinement est justifie par une verification
de la grammaire avec une marge >= ``charges.marge_mini_ferrures``.

Sources : NF EN 10025-2 (S235JR : Re 235 MPa, Rm 360-510 MPa, E 210 GPa) ;
NF EN 12163/12164 et fiches Deutsches Kupferinstitut pour CuZn37 (CW508L) et
CuZn39Pb3 (CW614N) : E ~ 100-110 GPa, Rp0,2 de ~180 MPa (etat recuit R300)
a ~300 MPa (etat demi-dur R370) ; densite 8 440-8 470 kg/m3.
"""

#: Regles communes aux metaux : au changement de nuance, chaque section est
#: mise a l'echelle selon le mode de sollicitation dominant.
#:   - cisaillement / traction (pene, rivet, barre de cremaillere) : aire ~ 1/Re
#:     => dimension lineaire ~ Re^-1/2 ;
#:   - flexion / torsion d'axes ronds (pivot, gond, arbre) : d^3 ~ 1/Re
#:     => d ~ Re^-1/3 ;
#:   - rigidite des fers plats (pentures, frettes) : e^3 ~ 1/E => e ~ E^-1/3 ;
#:   - dent d'engrenage (Lewis, sigma = F/(b.m.Y)) : m ~ 1/Re, serie normalisee.
REGLES_METAL = [
    {"id": "metal_pene", "cibles": ["loquet.pene_diametre"], "operation": "echelle",
     "propriete": "limite_elastique_mpa", "exposant": 0.5, "arrondi": 1.0,
     "explication": "Pene en cisaillement : aire ~ 1/Re (Re {ancien_val:g} -> {nouveau_val:g} MPa), "
                    "diametre x{ratio:.3f}."},
    {"id": "metal_rivet", "cibles": ["ferrures.rivet_diametre"], "operation": "echelle",
     "propriete": "limite_elastique_mpa", "exposant": 0.5, "arrondi": 1.0,
     "explication": "Rivets en cisaillement : diametre x{ratio:.3f}."},
    {"id": "metal_tete_rivet", "cibles": ["ferrures.tete_rivet_diametre"], "operation": "echelle",
     "propriete": "limite_elastique_mpa", "exposant": 0.5, "arrondi": 1.0,
     "explication": "Tete goutte de suif : suit la tige (tete >= 1,5 x tige), x{ratio:.3f}."},
    {"id": "metal_barre_cremaillere", "cibles": ["cremaillere.barre_epaisseur"], "operation": "echelle",
     "propriete": "limite_elastique_mpa", "exposant": 0.5, "arrondi": 1.0,
     "explication": "Barre de calage (matage du cran par le pene) : epaisseur x{ratio:.3f}."},
    {"id": "metal_largeur_barre", "cibles": ["cremaillere.barre_largeur"], "operation": "echelle",
     "propriete": "limite_elastique_mpa", "exposant": 0.5, "arrondi": 5.0,
     "explication": "Barre de calage : la largeur suit le diametre du pene (joues >= 6 mm), x{ratio:.3f}."},
    {"id": "metal_axes", "cibles": ["ferrures.axe_pivot_diametre", "ferrures.gond_diametre"],
     "operation": "echelle", "propriete": "limite_elastique_mpa", "exposant": 1.0 / 3.0, "arrondi": 1.0,
     "explication": "Axes en flexion : d^3 ~ 1/Re, diametre x{ratio:.3f}."},
    {"id": "metal_arbre", "cibles": ["synchro.arbre_diametre"], "operation": "echelle",
     "propriete": "limite_elastique_mpa", "exposant": 1.0 / 3.0, "arrondi": 1.0,
     "explication": "Arbre de synchronisation en torsion : d^3 ~ 1/tau, diametre x{ratio:.3f}."},
    {"id": "metal_fer_plat", "cibles": ["ferrures.fer_plat_epaisseur", "ferrures.platine_pivot_epaisseur"],
     "operation": "echelle", "propriete": "module_elasticite_mpa", "exposant": 1.0 / 3.0, "arrondi": 1.0,
     "explication": "Fers plats (pentures, platines) : rigidite ~ E.e^3, epaisseur x{ratio:.3f} "
                    "(E {ancien_val:g} -> {nouveau_val:g} MPa)."},
    {"id": "metal_module", "cibles": ["cremaillere.module"], "operation": "echelle",
     "propriete": "limite_elastique_mpa", "exposant": 1.0, "serie": [1.5, 2.0, 2.5, 3.0, 4.0, 5.0, 6.0],
     "explication": "Denture (Lewis) : module ~ 1/Re, x{ratio:.3f} puis module normalise superieur."},
    {"id": "metal_finition", "cibles": ["ferrures.finition"], "operation": "fixer_propriete",
     "propriete": "finition_defaut",
     "explication": "Finition par defaut du nouveau metal."},
    {"id": "metal_masse", "operation": "recalcul", "propriete": "densite_kg_m3",
     "explication": "Masse des ferrures recalculee (densite {ancien_val:g} -> {nouveau_val:g} kg/m3)."},
]

METAUX = {
    "fer_forge_mat": {
        "nom": "Fer forge mat (acier doux S235JR forge a chaud)",
        "famille": "acier",
        "nuance": "S235JR (EN 10025-2) - 'fer forge' au sens du ferronnier",
        "densite_kg_m3": 7850.0,
        "module_elasticite_mpa": 210000.0,
        "limite_elastique_mpa": 235.0,
        "resistance_rupture_mpa": 360.0,
        "finition_defaut": "cire_noire",
        "sections_commerciales": {"fer_plat_mm": ["30x5", "40x5", "40x6", "50x8", "30x10"],
                                  "rond_mm": [10, 12, 14, 16, 20, 25], "carre_mm": [12, 14, 16, 20]},
        "aspect": "noir mat a reflets bleutes, traces de marteau (martelage) recommandees",
        "sources": ["EN 10025-2 (S235JR)"],
        "regles": list(REGLES_METAL),
    },
    "laiton_mat": {
        "nom": "Laiton mat (CuZn37 / CuZn39Pb3, brosse ou patine)",
        "famille": "alliage_cuivreux",
        "nuance": "CuZn37 CW508L etat R300 (valeur prudente) ; CW614N pour pieces decolletees",
        "densite_kg_m3": 8440.0,
        "module_elasticite_mpa": 110000.0,
        "limite_elastique_mpa": 180.0,
        "resistance_rupture_mpa": 300.0,
        "finition_defaut": "laiton_brosse_vernis_mat",
        "sections_commerciales": {"fer_plat_mm": ["30x5", "40x6", "50x8"],
                                  "rond_mm": [10, 12, 16, 20, 25], "carre_mm": [12, 16, 20]},
        "aspect": "or sourd, brosse mat ou patine vieillie (brun-noir)",
        "sources": ["EN 12163/12164", "Deutsches Kupferinstitut, fiches CuZn37 / CuZn39Pb3"],
        "regles": list(REGLES_METAL) + [
            {"id": "laiton_engrenages", "operation": "signaler",
             "explication": "Laiton deconseille pour pignons, cremaillere dentee et arbres de "
                            "synchronisation (usure, grippage laiton/laiton) : garder ces pieces en acier "
                            "et reserver le laiton aux pieces vues (pentures, frettes, boitiers, pivots)."},
            {"id": "laiton_tanins", "operation": "signaler",
             "explication": "Le laiton ne tache pas le chene (pas de reaction tanin-fer)."},
        ],
    },
}

FINITIONS = {
    "cire_noire": {
        "nom": "Fer forge cire noir (cire d'abeille + noir de fumee a chaud)", "metaux": ["fer_forge_mat"], "protection_corrosion": 4,
        "contact_peau": "ok", "epaisseur_mm": 0.0,
        "entretien": "Recirer 1 fois par an ; interieur sec uniquement.",
        "regles": [],
    },
    "huile_brunie": {
        "nom": "Bruni (huile de lin cuite a chaud, reflets bleu-brun)", "metaux": ["fer_forge_mat"],
        "protection_corrosion": 5, "contact_peau": "ok", "epaisseur_mm": 0.0,
        "entretien": "Huiler legerement 1 a 2 fois par an.", "regles": [],
    },
    "phosphatation_vernis_mat": {
        "nom": "Phosphatation + vernis mat (fer)", "metaux": ["fer_forge_mat"], "protection_corrosion": 7,
        "contact_peau": "ok", "epaisseur_mm": 0.03,
        "entretien": "Chiffon humide ; retouches au vernis.", "regles": [],
    },
    "galvanisation_peinture_mate": {
        "nom": "Galvanisation a chaud + peinture noire mate (fer)", "metaux": ["fer_forge_mat"],
        "protection_corrosion": 9, "contact_peau": "ok", "epaisseur_mm": 0.08,
        "entretien": "Aucun ; pieces humides / nettoyages frequents.",
        "regles": [
            {"id": "galva_jeu", "cibles": ["tolerances.jeu_axes"], "operation": "minimum", "valeur": 0.5,
             "explication": "Galvanisation (~80 um par face) : jeu des axes et alesages porte a >= 0,5 mm."},
            {"id": "galva_aspect", "operation": "signaler",
             "explication": "La galvanisation efface une partie des traces de forge : marteler fort avant."},
        ],
    },
    "laiton_brosse_vernis_mat": {
        "nom": "Laiton brosse + vernis mat", "metaux": ["laiton_mat"], "protection_corrosion": 7,
        "contact_peau": "ok", "epaisseur_mm": 0.02,
        "entretien": "Chiffon sec ; pas de produit abrasif.", "regles": [],
    },
    "laiton_patine_vieilli": {
        "nom": "Laiton vieilli (patine chimique brun-noir, reliefs eclaircis, cire)", "metaux": ["laiton_mat"],
        "protection_corrosion": 5, "contact_peau": "eviter_contact_prolonge", "epaisseur_mm": 0.0,
        "entretien": "Cire 1 fois par an ; la patine evolue au toucher.",
        "regles": [
            {"id": "patine_contact", "operation": "signaler",
             "explication": "Patine chimique : eviter le contact prolonge avec la peau (manilles) ; "
                            "vernir les zones de contact."},
        ],
    },
}

#: Description des composants ferres (utilisee par la grammaire, la doc et la
#: nomenclature). ``pilote_par`` liste les chemins de parametres qui les
#: dimensionnent ; ``verification`` nomme le controle fait par la grammaire.
COMPOSANTS = {
    "cremaillere_calage": {
        "nom": "Cremaillere laterale de calage (barre crantee)",
        "description": "Fer plat cranté suspendu sous la platine par une equerre rivetee, coulissant "
                       "dans une bride forgee sur la face exterieure du pied ; trous de crans au pas.",
        "pilote_par": ["cremaillere.pas", "cremaillere.nombre_crans", "cremaillere.barre_largeur",
                       "cremaillere.barre_epaisseur"],
        "verification": "matage_cran",
    },
    "loquet_pene": {
        "nom": "Loquet a pene (verrou de cran)",
        "description": "Boitier forge rive sur la bride, pene rond rappele par ressort, poignee a "
                       "queue de cochon ; le pene traverse la barre et entre dans une gache ferree "
                       "du pied (double cisaillement).",
        "pilote_par": ["loquet.pene_diametre", "loquet.engagement", "loquet.course"],
        "verification": "cisaillement_pene",
    },
    "cremaillere_dentee": {
        "nom": "Cremaillere dentee de synchronisation",
        "description": "Barre dentee (module m) encastree dans la face interieure du coulisseau, "
                       "visible par une lumiere du fourreau.",
        "pilote_par": ["cremaillere.module", "cremaillere.largeur_denture"],
        "verification": "dent_lewis",
    },
    "pignon": {
        "nom": "Pignon droit de synchronisation",
        "description": "Pignon acier clavete sur l'arbre bas, engrene la cremaillere dentee.",
        "pilote_par": ["cremaillere.module", "cremaillere.angle_pression"],
        "verification": "dent_lewis",
    },
    "arbre_transmission": {
        "nom": "Arbre de transmission bas",
        "description": "Rond acier entre pied avant et pied arriere d'une meme extremite, tourne dans "
                       "des paliers forges rivetes ; option 4 points : arbre longitudinal + renvois.",
        "pilote_par": ["synchro.arbre_diametre", "synchro.mode"],
        "verification": "torsion_arbre",
    },
    "renvoi_angle": {
        "nom": "Renvoi d'angle 1:1 (couple conique sous carter forge)",
        "description": "Relie l'arbre longitudinal aux deux arbres transversaux (mode quatre_points).",
        "pilote_par": ["synchro.mode", "cremaillere.module"],
        "verification": None,
    },
    "palier": {
        "nom": "Palier forge (bague bronze)",
        "description": "Patte forgee rivetee sur le pied, bague bronze autolubrifiante.",
        "pilote_par": ["synchro.arbre_diametre"], "verification": None,
    },
    "penture_angle": {
        "nom": "Penture d'angle a terminaisons forgees",
        "description": "Deux bandes de fer plat (28 x 4) croisees a l'angle de la platine, terminees par "
                       "une fleur de lys, une queue d'aronde ou un trilobe forges ; rivets goutte de suif.",
        "pilote_par": ["ferrures.fer_plat_largeur", "ferrures.fer_plat_epaisseur", "entrave.pentures.longueur",
                       "ferrures.terminaison_pentures"],
        "verification": None,
    },
    "frette": {
        "nom": "Bague forgee au pied du fut",
        "description": "Bague fine (12 mm) ceinturant le pied du fut au-dessus de la plinthe (anti-fente + decor).",
        "pilote_par": ["ferrures.fer_plat_epaisseur"], "verification": None,
    },
    "gond": {
        "nom": "Gond de manille",
        "description": "Charniere forgee (axe + noeuds) qui ouvre la manille.",
        "pilote_par": ["ferrures.gond_diametre"], "verification": None,
    },
    "rivet_forge": {
        "nom": "Rivet forge a tete goutte de suif et contre-plaque",
        "description": "Fixation sans vis des ferrures : tige traversante, tete bombee (calotte) bouterollee, "
                       "contre-plaque et rivure cote cache.",
        "pilote_par": ["ferrures.rivet_diametre", "ferrures.tete_rivet_diametre", "ferrures.tete_rivet_hauteur"],
        "verification": "rivets_pivot",
    },
    "capot_cremaillere": {
        "nom": "Capot / plaque d'habillage de la barre de calage",
        "description": "Tole forgee 2,5 mm en U, rivetee au chapiteau, devant la barre crantee : lancettes "
                       "ou quadrilobes decoupes laissent voir les crans.",
        "pilote_par": ["cremaillere.habillage", "cremaillere.capot_epaisseur"], "verification": None,
    },
}

PIVOTS = {
    "axe_vertical_chape": {
        "nom": "Axe vertical a chape (rotation dans le plan de la platine)",
        "description": "Platine forgee rivetee, axe vertical, chape tournante portant la manille ; "
                       "butees reglables a +/-45 deg. Simple a forger, robuste, aucun pincement.",
        "degres_liberte": 1, "hauteur_pivot_mm": 30.0, "complexite": 1,
        "regles": [
            {"id": "pivot_axe_hauteur", "cibles": ["entrave.manilles.hauteur_pivot"], "operation": "fixer",
             "valeur": 30.0, "explication": "Chape + axe vertical : hauteur de pivot 30 mm."},
        ],
    },
    "rotule": {
        "nom": "Rotule (boule forgee dans coquille)",
        "description": "Boule acier dans une coquille rivetee : la manille suit tous les mouvements "
                       "de la tete ; plus confortable, mais plus d'usinage et de jeu a surveiller.",
        "degres_liberte": 3, "hauteur_pivot_mm": 40.0, "complexite": 3,
        "regles": [
            {"id": "pivot_rotule_hauteur", "cibles": ["entrave.manilles.hauteur_pivot"], "operation": "fixer",
             "valeur": 40.0, "explication": "Rotule : coquille plus haute, hauteur de pivot 40 mm."},
            {"id": "pivot_rotule_axe", "cibles": ["ferrures.axe_pivot_diametre"], "operation": "minimum",
             "valeur": 20.0, "explication": "Col de rotule : diametre >= 20 mm (flexion au col)."},
            {"id": "pivot_rotule_jeu", "operation": "signaler",
             "explication": "Rotule : prevoir un frein (ecrou de serrage cache ou ressort) pour limiter "
                            "le ballant ; verifier l'usure de la coquille."},
        ],
    },
    "charniere_basculante": {
        "nom": "Charniere basculante (axe horizontal)",
        "description": "Gond horizontal : la manille se rabat a plat sur la platine quand elle est "
                       "ouverte, et se releve pour l'usage. Tres 'pilori', 1 degre de liberte.",
        "degres_liberte": 1, "hauteur_pivot_mm": 25.0, "complexite": 2,
        "regles": [
            {"id": "pivot_charniere_hauteur", "cibles": ["entrave.manilles.hauteur_pivot"], "operation": "fixer",
             "valeur": 25.0, "explication": "Charniere : noeuds de gond, hauteur de pivot 25 mm."},
        ],
    },
}


#: Terminaisons forgees des pentures (selection ``ferrures.terminaison_pentures``).
#: ``longueur_relative`` : longueur de la terminaison / largeur de bande ;
#: ``envergure_relative`` : demi-envergure laterale maxi / largeur de bande.
TERMINAISONS = {
    "fleur_de_lys": {
        "nom": "Fleur de lys (petale central en ogive, deux crosses laterales, bague)",
        "longueur_relative": 2.0, "envergure_relative": 0.95, "heures_forge": 1.5, "complexite": 3,
        "regles": [
            {"id": "lys_longueur", "cibles": ["entrave.pentures.longueur"], "operation": "minimum", "valeur": 150.0,
             "explication": "Fleur de lys : terminaison de 2 largeurs de bande ; branche >= 150 mm pour garder "
                            "3 rivets dans la partie droite."},
            {"id": "lys_largeur", "cibles": ["ferrures.fer_plat_largeur"], "operation": "minimum", "valeur": 24.0,
             "explication": "Fleur de lys : bande >= 24 mm pour que les crosses gardent >= 5 mm de matiere."},
        ],
    },
    "queue_d_aronde": {
        "nom": "Queue d'aronde (bout fendu en V)",
        "longueur_relative": 1.2, "envergure_relative": 0.9, "heures_forge": 0.5, "complexite": 1,
        "regles": [
            {"id": "aronde_longueur", "cibles": ["entrave.pentures.longueur"], "operation": "minimum",
             "valeur": 130.0, "explication": "Queue d'aronde : terminaison courte, branche >= 130 mm."},
        ],
    },
    "trilobe": {
        "nom": "Trilobe (trefle forge)",
        "longueur_relative": 1.8, "envergure_relative": 0.95, "heures_forge": 1.0, "complexite": 2,
        "regles": [
            {"id": "trilobe_longueur", "cibles": ["entrave.pentures.longueur"], "operation": "minimum",
             "valeur": 140.0, "explication": "Trilobe : branche >= 140 mm."},
        ],
    },
    "droite": {
        "nom": "Bout droit a coins abattus (sobre)",
        "longueur_relative": 0.0, "envergure_relative": 0.5, "heures_forge": 0.1, "complexite": 0,
        "regles": [
            {"id": "droite_sobre", "operation": "signaler",
             "explication": "Terminaison droite : retour vers le style brut de la v1."},
        ],
    },
}

#: Habillage de la barre de calage (selection ``cremaillere.habillage``).
HABILLAGES = {
    "capot_ajoure": {
        "nom": "Capot en U ajoure de lancettes (arcs brises)",
        "motif": "ogive", "heures_atelier": 2.0,
        "regles": [
            {"id": "capot_jeu", "operation": "signaler",
             "explication": "Capot : garder >= 2 mm de jour devant la barre (graisse, poussiere) ; "
                            "les lancettes laissent lire le cran engage."},
        ],
    },
    "plaque_decoupee": {
        "nom": "Plaque decoupee de quadrilobes",
        "motif": "quadrilobe", "heures_atelier": 2.5,
        "regles": [
            {"id": "plaque_decoupe", "operation": "signaler",
             "explication": "Plaque decoupee : decoupe laser ou jet d'eau puis reprise a la lime et "
                            "martelage des rives (sinon aspect industriel)."},
        ],
    },
    "aucun": {
        "nom": "Barre apparente sans habillage",
        "motif": None, "heures_atelier": 0.0,
        "regles": [],
    },
}

#: Decor de la barre crantee (selection ``cremaillere.decor_barre``).
#: ``taux_enlevement`` : part de la largeur de joue retiree par le decor ;
#: la regle ``minimum_section_nette`` garde 6 mm de joue nette de chaque cote
#: du trou de pene : largeur >= (pene + 2 x 6) / (1 - taux).
DECORS_BARRE = {
    "lisse": {
        "nom": "Barre lisse a rives adoucies", "taux_enlevement": 0.0,
        "regles": [
            {"id": "barre_lisse", "cibles": ["cremaillere.barre_largeur"], "operation": "minimum_section_nette",
             "bases": ["loquet.pene_diametre"], "constante": 12.0, "taux": 0.0, "arrondi": 1.0,
             "explication": "Barre lisse : largeur >= pene + 2 x 6 mm = {mini:g} mm."},
        ],
    },
    "festonnee": {
        "nom": "Barre festonnee (rives en festons entre les crans)", "taux_enlevement": 0.2,
        "regles": [
            {"id": "barre_festons", "cibles": ["cremaillere.barre_largeur"], "operation": "minimum_section_nette",
             "bases": ["loquet.pene_diametre"], "constante": 12.0, "taux": 0.2, "arrondi": 1.0,
             "explication": "Festons (-20 % de section) : largeur >= (pene + 12) / 0,8 = {mini:g} mm pour "
                            "garder 6 mm de joue nette."},
        ],
    },
    "ajouree": {
        "nom": "Barre ajouree (quadrilobes entre les crans, partie haute)", "taux_enlevement": 0.3,
        "regles": [
            {"id": "barre_ajours", "cibles": ["cremaillere.barre_largeur"], "operation": "minimum_section_nette",
             "bases": ["loquet.pene_diametre"], "constante": 12.0, "taux": 0.3, "arrondi": 1.0,
             "explication": "Ajours (-30 % de section) : largeur >= (pene + 12) / 0,7 = {mini:g} mm."},
            {"id": "barre_ajours_epaisseur", "cibles": ["cremaillere.barre_epaisseur"], "operation": "minimum",
             "valeur": 10.0, "explication": "Ajours : epaisseur >= 10 mm (raideur de la barre percee)."},
        ],
    },
}
