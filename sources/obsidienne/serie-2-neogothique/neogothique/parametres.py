# -*- coding: utf-8 -*-
"""Couche 1 - Parametres globaux partages de la gamme Neogothique.

Chaque parametre est une *feuille* du schema ``SCHEMA`` decrite par ``Param``
(valeur par defaut, unite, role, plage, choix, statut, utilisateurs). Les
valeurs se lisent/ecrivent par chemin pointe (``"cremaillere.pas"``).

Unites internes : mm, kg, deg, N, MPa, % (jamais de cm ici ; la conversion
vers l'API Fusion est faite dans ``fusion_outils``).

Statuts :
  - ``impose``    : valeur fixee par Fabien dans la demande ;
  - ``a_valider`` : valeur proposee, a trancher (voir docs/points_a_trancher.md) ;
  - ``derive``    : valeur susceptible d'etre recalculee par les regles ;
  - ``libre``     : valeur de reference de la gamme.

Usage ::

    from neogothique.parametres import Parametres
    p = Parametres.pour_typologie("entrave")
    p.get("cremaillere.pas")                 # 25
    p.set("entrave.pied.section", "octogonal")
    for pb in p.valider(): print(pb)
    p.exporter_user_parameters(design)       # dans Fusion uniquement
"""

import copy
import json
import os
import re

from .catalogues import (BOIS, FINITIONS_BOIS, GARNISSAGE, METAUX, FINITIONS, PIVOTS, TERMINAISONS, HABILLAGES,
                         DECORS_BARRE)
from .catalogues.attaches import JONCTIONS_ADMISES
from .profils import TYPES_CHANT, PHI

_MANQUANT = object()

#: Fichier JSON optionnel d'overrides utilisateur : {"commun": {...},
#: "typologies": {"entrave": {...}}} avec les memes chemins que SCHEMA.
CHEMIN_JSON = os.path.join(os.path.dirname(__file__), "parametres_neogothique.json")

IMP, VAL, DER, LIB = "impose", "a_valider", "derive", "libre"


class Param(object):
    """Description d'un parametre (feuille du schema).

    :param valeur: valeur par defaut.
    :param unite: "mm", "kg", "deg", "N", "MPa", "%", "" (sans unite),
        "texte", "bool", "entier".
    :param role: a quoi sert le parametre.
    :param plage: (mini, maxi) pour les numeriques, ou None.
    :param choix: valeurs admises pour les textes, ou None.
    :param statut: impose | a_valider | derive | libre.
    :param utilise_par: modules / typologies qui le lisent.
    """

    __slots__ = ("valeur", "unite", "role", "plage", "choix", "statut", "utilise_par")

    def __init__(self, valeur, unite, role, plage=None, choix=None, statut=LIB, utilise_par=()):
        self.valeur = valeur
        self.unite = unite
        self.role = role
        self.plage = plage
        self.choix = list(choix) if choix is not None else None
        self.statut = statut
        self.utilise_par = tuple(utilise_par)

    def __repr__(self):
        return "Param(%r %s, %s)" % (self.valeur, self.unite, self.statut)


E = ("entrave",)           # utilise par la grammaire Entrave
R = ("regles",)            # utilise par le moteur de regles
G = ("gamme",)             # vocabulaire general (futures typologies)

SCHEMA = {
    "gamme": {
        "nom": Param("Neogothique", "texte", "Nom de la gamme.", utilise_par=G),
        "version": Param("0.2.0", "texte", "Version du vocabulaire de parametres.", utilise_par=G),
        "prefixe_fusion": Param("neo_", "texte", "Prefixe des User Parameters crees dans Fusion.",
                                utilise_par=("fusion_outils",)),
    },
    "style": {
        "proportions": Param("nombre_or", "texte", "Regle de proportion des pieds (plinthe / fut / chapiteau) et "
                             "des semelles : 'nombre_or' (H/phi^4, H/phi, H/phi^3 : 1/phi + 1/phi^3 + 1/phi^4 = 1), "
                             "'harmonique' (1:5:2 : octave plinthe/chapiteau, dixieme majeure chapiteau/fut), 'libre' (parts ci-dessous).",
                             choix=["nombre_or", "harmonique", "libre"], statut=VAL, utilise_par=E + G),
        "part_plinthe": Param(round(1 / PHI ** 4, 4), "", "Part de la hauteur visible du pied occupee par la plinthe "
                              "(utilisee si proportions = 'libre').", plage=(0.08, 0.3), utilise_par=E),
        "part_chapiteau": Param(round(1 / PHI ** 3, 4), "", "Part occupee par le chapiteau, astragale comprise "
                                "(si proportions = 'libre').", plage=(0.12, 0.35), utilise_par=E),
        "motif_ajours": Param("ogive", "texte", "Motif des ajours (ceinture) : arc brise, trilobe ou quadrilobe.",
                              choix=["ogive", "trilobe", "quadrilobe"], statut=VAL, utilise_par=E + G),
        "ratio_rayon_ogive": Param(1.0, "", "Rayon des arcs brises / largeur de baie : 1 = ogive equilaterale, "
                                   "> 1 = lancette, < 1 = surbaissee.", plage=(0.6, 1.6), utilise_par=E + G),
        "montant_mini": Param(14.0, "mm", "Largeur mini de bois laissee entre deux ajours (section nette des "
                              "montants de ceinture).", plage=(8.0, 40.0), utilise_par=E + R),
    },
    "bois": {
        "essence": Param("chene", "texte", "Essence par defaut de la gamme (cle du catalogue bois). "
                         "L'Entrave l'impose a 'noyer' (override de typologie).",
                         choix=sorted(BOIS), statut=IMP, utilise_par=E + R),
        "finition": Param("huile_cire_noire", "texte", "Finition du bois.", choix=sorted(FINITIONS_BOIS),
                          utilise_par=E + R),
        "humidite_cible": Param(10.0, "%", "Humidite d'equilibre visee a la fabrication (interieur chauffe).",
                                plage=(6.0, 14.0), utilise_par=E),
        "variation_humidite": Param(3.0, "%", "Variation saisonniere d'humidite a absorber (mortaises oblongues).",
                                    plage=(1.0, 6.0), utilise_par=E),
        "chanfrein_aretes": Param(1.5, "mm", "Adoucissement des aretes NON moulurees (abaque, plinthe, "
                                  "traverses) : angles francs mais sans echarde.", plage=(0.5, 6.0), utilise_par=E + G),
        "section_mini": Param(40.0, "mm", "Plus petite section admise pour une piece bois porteuse "
                              "(coulisseau).", plage=(30.0, 80.0), utilise_par=E + G),
    },
    "garnissage": {
        "cuir_manilles": Param("cuir_sellier_fin_noir", "texte", "Cuir des manilles (cle du catalogue).",
                               choix=sorted(k for k, v in GARNISSAGE.items() if "manille" in v["usages"]),
                               statut=IMP, utilise_par=E + R),
        "coloris": Param("noir", "texte", "Coloris impose de la gamme (verifie contre le catalogue).",
                         choix=["noir"], statut=IMP, utilise_par=E),
        "epaisseur_manille": Param(7.5, "mm", "Epaisseur du complexe cuir des manilles (exterieur + ame + "
                                   "rembourrage + doublure).", plage=(3.0, 12.0),
                                   statut=DER, utilise_par=E + R),
        "largeur_manille_cou": Param(60.0, "mm", "Largeur (hauteur de bande) de la manille de cou.",
                                     plage=(40.0, 90.0), statut=DER, utilise_par=E + R),
        "largeur_manille_poignet": Param(50.0, "mm", "Largeur de bande des manilles de poignets.",
                                         plage=(35.0, 80.0), statut=DER, utilise_par=E + R),
        "diametre_int_cou": Param(130.0, "mm", "Diametre interieur nominal de la manille de cou (reglable "
                                  "par boucle +/-15 mm).", plage=(100.0, 170.0), statut=VAL, utilise_par=E),
        "diametre_int_poignet": Param(75.0, "mm", "Diametre interieur nominal des manilles de poignets.",
                                      plage=(55.0, 100.0), statut=VAL, utilise_par=E),
        "epaisseur_rembourrage": Param(30.0, "mm", "Rembourrage des coussinets (futures typologies).",
                                       plage=(10.0, 60.0), utilise_par=G + R),
    },
    "sellerie": {
        "point": Param("sellier_double", "texte", "Point de couture : sellier double a deux aiguilles (main, "
                       "indecousable) ou piqure machine.", choix=["sellier_double", "piqure_machine"], statut=VAL,
                       utilise_par=E + R),
        "pas_point": Param(3.2, "mm", "Pas du point (pricot) : 3,2 mm = 8 points / pouce, fin et regulier.",
                           plage=(2.0, 6.0), statut=DER, utilise_par=E + R),
        "fil": Param("lin_cire", "texte", "Fil de couture.", choix=["lin_cire", "polyester_cire"],
                     utilise_par=E + R),
        "fil_diametre": Param(0.55, "mm", "Diametre du fil cire (0,55 mm : fin, visible sans etre grossier).",
                              plage=(0.35, 1.2), statut=DER, utilise_par=E + R),
        "filet_bordure": Param(3.0, "mm", "Retrait de la couture et du filet d'embellissement (abattage) au "
                               "bord de la sangle.", plage=(2.0, 6.0), utilise_par=E),
        "tranches": Param("teintees_lustrees", "texte", "Finition des tranches : teintees noir puis lustrees "
                          "(gomme adragante, os), ou simplement cirees.", choix=["teintees_lustrees", "cirees"],
                          utilise_par=E),
        "rembourrage_manille": Param(3.0, "mm", "Rembourrage fin (mousse latex haute densite) entre exterieur et "
                                     "doublure des manilles.", plage=(0.0, 8.0), statut=DER, utilise_par=E + R),
        "coussin_avant": Param(True, "bool", "Coussin d'appui en cuir sur l'avant de la platine (devant les "
                               "manilles).", statut=VAL, utilise_par=E),
        "coussin_epaisseur": Param(15.0, "mm", "Epaisseur du coussin d'appui (cuir + mousse).", plage=(8.0, 40.0),
                                   utilise_par=E),
        "matelassage_platine": Param("losange", "texte", "Matelassage du coussin : 'aucun', 'losange' (piqures "
                                     "en losange) ou 'capitonne' (losanges + boutons recouverts).",
                                     choix=["aucun", "losange", "capitonne"], statut=VAL, utilise_par=E),
        "matelassage_pas": Param(50.0, "mm", "Pas (diagonale) des losanges du matelassage.", plage=(30.0, 120.0),
                                 utilise_par=E),
        "bouton_diametre": Param(12.0, "mm", "Diametre des boutons de capiton (cuir noir).", plage=(8.0, 20.0),
                                 utilise_par=E),
    },
    "ferrures": {
        "metal": Param("fer_forge_mat", "texte", "Metal des ferrures apparentes.", choix=sorted(METAUX),
                       statut=VAL, utilise_par=E + R),
        "finition": Param("cire_noire", "texte", "Finition des ferrures ('fer forge cire noir', 'bruni', "
                          "'laiton vieilli'...).", choix=sorted(FINITIONS), utilise_par=E + R),
        "terminaison_pentures": Param("fleur_de_lys", "texte", "Terminaison forgee des pentures (cle du "
                                      "catalogue TERMINAISONS).", choix=sorted(TERMINAISONS), statut=VAL,
                                      utilise_par=E + R),
        "fer_plat_largeur": Param(28.0, "mm", "Largeur des fers plats (pentures, brides) : 28 mm, plus fin que "
                                  "la v1 (40) ; non porteur (decor + anti-fente).", plage=(20.0, 60.0),
                                  utilise_par=E),
        "fer_plat_epaisseur": Param(4.0, "mm", "Epaisseur des fers plats.", plage=(3.0, 12.0), statut=DER,
                                    utilise_par=E + R),
        "rivet_diametre": Param(5.0, "mm", "Diametre de tige des rivets forges.", plage=(3.0, 12.0),
                                statut=DER, utilise_par=E + R),
        "tete_rivet_diametre": Param(8.0, "mm", "Diametre de la tete goutte de suif des rivets (>= 1,5 x tige).",
                                     plage=(5.0, 18.0), statut=DER, utilise_par=E + R),
        "tete_rivet_hauteur": Param(3.0, "mm", "Hauteur de la calotte goutte de suif.", plage=(1.5, 8.0),
                                    utilise_par=E),
        "axe_pivot_diametre": Param(18.0, "mm", "Diametre des axes de pivot des manilles.", plage=(10.0, 30.0),
                                    statut=DER, utilise_par=E + R),
        "gond_diametre": Param(8.0, "mm", "Diametre d'axe des gonds de manilles.", plage=(6.0, 20.0),
                               statut=DER, utilise_par=E + R),
        "platine_pivot_cote": Param(70.0, "mm", "Cote de la platine forgee sous chaque pivot (coins abattus).",
                                    plage=(50.0, 140.0), utilise_par=E),
        "platine_pivot_epaisseur": Param(5.0, "mm", "Epaisseur de la platine de pivot.", plage=(4.0, 12.0),
                                         statut=DER, utilise_par=E + R),
    },
    "cremaillere": {
        "hauteur_mini": Param(300.0, "mm", "Hauteur du DESSUS de platine au cran 0 (position basse). "
                              "Interpretation de 'debattement 15 cm ... a 45 cm' : 450 - 150.",
                              plage=(150.0, 600.0), statut=VAL, utilise_par=E),
        "hauteur_maxi": Param(450.0, "mm", "Hauteur du dessus de platine au dernier cran.",
                              plage=(200.0, 700.0), statut=IMP, utilise_par=E),
        "nombre_crans": Param(7, "entier", "Nombre de crans = nombre de POSITIONS de calage (convention "
                              "'positions' : debattement = (n-1) x pas).", plage=(2, 20), statut=VAL,
                              utilise_par=E),
        "pas": Param(25.0, "mm", "Pas entre deux crans.", plage=(10.0, 60.0), statut=VAL, utilise_par=E),
        "convention": Param("positions", "texte", "'positions' : n crans = n hauteurs, debattement=(n-1).pas ; "
                            "'intervalles' : n intervalles, n+1 hauteurs, debattement=n.pas.",
                            choix=["positions", "intervalles"], utilise_par=E),
        "cran_courant": Param(0, "entier", "Cran courant (0 = position basse) : pilote la geometrie et "
                              "le User Parameter Fusion.", plage=(0, 20), utilise_par=E),
        "barre_largeur": Param(24.0, "mm", "Largeur de la barre crantee de calage.", plage=(16.0, 50.0),
                               statut=DER, utilise_par=E + R),
        "barre_epaisseur": Param(8.0, "mm", "Epaisseur de la barre crantee de calage.", plage=(6.0, 20.0),
                                 statut=DER, utilise_par=E + R),
        "module": Param(3.0, "mm", "Module de denture pignon / cremaillere de synchronisation.",
                        plage=(1.5, 6.0), statut=DER, utilise_par=E + R),
        "angle_pression": Param(20.0, "deg", "Angle de pression de la denture.", plage=(14.5, 25.0),
                                utilise_par=E),
        "largeur_denture": Param(20.0, "mm", "Largeur de denture (pignon et cremaillere).", plage=(10.0, 40.0),
                                 utilise_par=E),
        "dents_mini": Param(14, "entier", "Nombre de dents mini du pignon (sous-coupe a 20 deg).",
                            plage=(12, 30), utilise_par=E),
        "marge_engrenement": Param(15.0, "mm", "Marge de denture au-dela du point de contact en position haute.",
                                   plage=(5.0, 40.0), utilise_par=E),
        "habillage": Param("capot_ajoure", "texte", "Habillage de la barre de calage visible : aucun, capot ajoure "
                           "de lancettes, plaque decoupee de quadrilobes (catalogue HABILLAGES).",
                           choix=sorted(HABILLAGES), statut=VAL, utilise_par=E + R),
        "decor_barre": Param("lisse", "texte", "Decor de la barre crantee : lisse, festonnee (rives en festons), "
                             "ajouree (catalogue DECORS_BARRE).", choix=sorted(DECORS_BARRE), statut=VAL,
                             utilise_par=E + R),
        "capot_epaisseur": Param(2.5, "mm", "Epaisseur de la tole du capot / de la plaque d'habillage.",
                                 plage=(1.5, 5.0), utilise_par=E),
    },
    "loquet": {
        "pene_diametre": Param(12.0, "mm", "Diametre du pene rond du loquet.", plage=(10.0, 30.0), statut=DER,
                               utilise_par=E + R),
        "engagement": Param(10.0, "mm", "Profondeur d'entree du pene dans la gache au-dela de la barre.",
                            plage=(6.0, 30.0), utilise_par=E),
        "course": Param(20.0, "mm", "Course du pene (retrait complet hors de la barre).", plage=(10.0, 50.0),
                        utilise_par=E),
        "boitier_hauteur": Param(32.0, "mm", "Hauteur du boitier forge du loquet.", plage=(30.0, 80.0),
                                 utilise_par=E),
        "loquets_porteurs_min": Param(2, "entier", "Nombre de loquets supposes porteurs pour la verification "
                                      "(cas d'un oubli de verrouillage).", plage=(1, 4), utilise_par=E),
    },
    "synchro": {
        "mode": Param("quatre_points", "texte", "'deux_cotes' : un arbre transversal par extremite (avant/"
                      "arriere) ; 'quatre_points' : + arbre longitudinal et renvois d'angle 1:1 (platine "
                      "horizontale dans les deux directions).", choix=["deux_cotes", "quatre_points"],
                      statut=VAL, utilise_par=E),
        "arbre_diametre": Param(16.0, "mm", "Diametre des arbres de transmission.", plage=(12.0, 40.0),
                                statut=DER, utilise_par=E + R),
        "carter_cote": Param(60.0, "mm", "Cote du carter forge des renvois d'angle.", plage=(40.0, 100.0),
                             utilise_par=E),
    },
    "jonctions": {
        "ratio_tenon": Param(1.0 / 3.0, "", "Epaisseur tenon / epaisseur piece (regle du tiers).",
                             plage=(0.25, 0.45), utilise_par=E + R),
        "tolerance_ratio_tenon": Param(0.05, "", "Ecart admis autour de 1/3 avant alerte.", plage=(0.0, 0.15),
                                       utilise_par=("parametres",)),
        "tourillon_diametre": Param(6.0, "mm", "Diametre des tourillons (<= 1/2 de la piece la plus fine).",
                                    plage=(6.0, 16.0), utilise_par=E + R),
        "cheville_diametre": Param(10.0, "mm", "Diametre des chevilles de chene.", plage=(6.0, 16.0),
                                   utilise_par=E + R),
        "decalage_drawbore": Param(1.5, "mm", "Decalage du chevillage a tire.", plage=(0.5, 3.0), utilise_par=E),
        "saillie_tenon_clavete": Param(45.0, "mm", "Saillie des tenons a clef hors de la semelle.",
                                       plage=(30.0, 90.0), utilise_par=E + R),
        "type_coulisseau_platine": Param("tenon_traversant_cale", "texte", "Jonction coulisseau -> platine.",
                                         choix=JONCTIONS_ADMISES["coulisseau_platine"], utilise_par=E + R),
        "type_fourreau_semelle": Param("tenon_traversant_cheville", "texte", "Jonction fourreau -> semelle.",
                                       choix=JONCTIONS_ADMISES["fourreau_semelle"], utilise_par=E + R),
        "type_traverse_semelle": Param("tenon_traversant_clavete", "texte", "Jonction traverse basse -> "
                                       "semelles (demontable).", choix=JONCTIONS_ADMISES["traverse_semelle"],
                                       utilise_par=E + R),
        "type_joues_fourreau": Param("tourillons", "texte", "Assemblage des deux demi-fourreaux rainures.",
                                     choix=JONCTIONS_ADMISES["joues_fourreau"], utilise_par=E + R),
    },
    "tolerances": {
        "jeu_coulisseau": Param(1.5, "mm", "Jeu radial coulisseau / fourreau (mouvement du bois + glissement).",
                                plage=(0.5, 4.0), statut=VAL, utilise_par=E),
        "jeu_mortaise": Param(0.2, "mm", "Jeu d'ajustement tenon / mortaise.", plage=(0.0, 0.6), utilise_par=E),
        "jeu_mortaise_oblongue": Param(2.0, "mm", "Jeu mini des mortaises oblongues (dilatation du plateau).",
                                       plage=(0.5, 8.0), statut=DER, utilise_par=E + R),
        "jeu_axes": Param(0.3, "mm", "Jeu diametral axes / alesages des ferrures.", plage=(0.1, 1.0),
                          statut=DER, utilise_par=E + R),
        "ecart_debattement": Param(0.5, "mm", "Ecart admis entre debattement demande et crans x pas.",
                                   plage=(0.0, 5.0), utilise_par=("parametres",)),
    },
    "charges": {
        "verticale_service": Param(1500.0, "N", "Charge verticale de service sur la platine (appui du corps).",
                                   plage=(300.0, 4000.0), statut=VAL, utilise_par=E),
        "traction_manille": Param(500.0, "N", "Traction laterale de verification sur une manille.",
                                  plage=(100.0, 3000.0), statut=VAL, utilise_par=E),
        "coef_dynamique": Param(1.5, "", "Majoration dynamique des charges.", plage=(1.0, 3.0), utilise_par=E),
        "gamma_m_bois": Param(1.3, "", "Coefficient partiel bois massif (EC5).", plage=(1.0, 2.0), utilise_par=E),
        "kmod_bois": Param(0.8, "", "Coefficient de modification (classe de service 1, moyen terme).",
                           plage=(0.5, 1.1), utilise_par=E),
        "gamma_m_metal": Param(1.1, "", "Coefficient partiel acier/laiton.", plage=(1.0, 1.5), utilise_par=E),
        "gamma_cuir": Param(4.0, "", "Coefficient de securite sur la traction du cuir / de l'ame.",
                            plage=(2.0, 8.0), utilise_par=E),
        "fleche_limite_ratio": Param(300.0, "", "Fleche admissible = portee / ratio.", plage=(150.0, 600.0),
                                     utilise_par=E),
        "coef_frottement_sol": Param(0.3, "", "Frottement semelle bois / sol (glissement).", plage=(0.1, 0.8),
                                     utilise_par=E),
        "recouvrement_ratio_mini": Param(1.5, "", "Recouvrement mini coulisseau/fourreau en position haute, "
                                         "en multiple de la section du coulisseau.", plage=(0.5, 4.0),
                                         utilise_par=E),
        "marge_mini_ferrures": Param(1.5, "", "Marge mini (admissible / sollicitation) exigee des ferrures "
                                     "affinees : en dessous, alerte meme si la verification passe.",
                                     plage=(1.0, 3.0), utilise_par=E),
        "g": Param(9.81, "", "Acceleration de la pesanteur (m/s2).", plage=(9.8, 9.82), utilise_par=E),
    },
    "securite": {
        "ouverture_rapide_cou": Param(True, "bool", "Manille de cou a ouverture rapide sans outil (obligatoire "
                                      "recommande : goupille a anneau ou boucle a degagement).", statut=VAL,
                                      utilise_par=E),
        "arrondi_contact_peau": Param(3.0, "mm", "Rayon mini des tranches et aretes en contact peau.",
                                      plage=(1.0, 10.0), utilise_par=E),
    },
    "ancrage": {
        "anneaux_sol": Param(True, "bool", "Anneaux d'ancrage au sol encastres sous les semelles.", statut=VAL,
                             utilise_par=E),
        "capacite_point": Param(2000.0, "N", "Effort admissible par point d'ancrage (cheville + anneau).",
                                plage=(200.0, 10000.0), utilise_par=E),
        "lest": Param(0.0, "kg", "Lest additionnel integre (barres d'acier dans la traverse), 0 = aucun.",
                      plage=(0.0, 80.0), utilise_par=E),
    },
    "entrave": {
        "platine": {
            "longueur": Param(800.0, "mm", "Longueur de la platine (axe X).", plage=(600.0, 1200.0), statut=IMP,
                              utilise_par=E),
            "largeur": Param(400.0, "mm", "Largeur (profondeur) de la platine (axe Y).", plage=(300.0, 600.0),
                             statut=IMP, utilise_par=E),
            "epaisseur": Param(50.0, "mm", "Epaisseur de la platine en noyer massif.", plage=(35.0, 80.0),
                               statut=VAL, utilise_par=E + R),
            "chant_dessus": Param("conge", "texte", "Profil du chant superieur (cote corps : doux au toucher).",
                                  choix=list(TYPES_CHANT), statut=VAL, utilise_par=E),
            "chant_dessus_taille": Param(4.0, "mm", "Rayon / cote du chant superieur.", plage=(0.0, 15.0),
                                         utilise_par=E),
            "chant_dessous": Param("bec_de_corbin", "texte", "Profil du chant inferieur : bec-de-corbin (tore + "
                                   "gorge + listel) qui allege visuellement les 50 mm de noyer.",
                                   choix=list(TYPES_CHANT), statut=VAL, utilise_par=E),
            "chant_dessous_hauteur": Param(31.0, "mm", "Hauteur moulee du chant inferieur (e/phi = 30,9 mm).",
                                           plage=(0.0, 45.0), utilise_par=E),
            "chant_dessous_profondeur": Param(14.0, "mm", "Profondeur (retrait) du chant inferieur.",
                                              plage=(0.0, 25.0), utilise_par=E),
        },
        "pied": {
            "section": Param("carre", "texte", "Section des pieds (fourreaux).", choix=["carre", "octogonal"],
                             statut=VAL, utilise_par=E),
            "cote": Param(100.0, "mm", "Cote du FUT au pied de la colonne : cote du carre ou distance sur "
                          "plats de l'octogone.", plage=(70.0, 180.0), statut=VAL, utilise_par=E + R),
            "retrait_bord": Param(30.0, "mm", "Retrait du CHAPITEAU (partie la plus large) par rapport aux bords "
                                  "de la platine.", plage=(0.0, 120.0), utilise_par=E),
            "debord_base": Param(12.0, "mm", "Debord de la plinthe et de l'abaque du chapiteau sur le fut, par "
                                 "face.", plage=(0.0, 30.0), utilise_par=E),
            "fuselage": Param(3.0, "mm", "Retrait par face du haut du fut (fruit / leger fuselage, 1,5 deg).",
                              plage=(0.0, 10.0), utilise_par=E),
            "rayon_astragale": Param(3.0, "mm", "Rayon du boudin d'astragale sous le chapiteau.", plage=(0.0, 8.0),
                                     utilise_par=E),
            "rayon_cavet": Param(9.0, "mm", "Rayon du cavet sous l'abaque du chapiteau.", plage=(0.0, 20.0),
                                 utilise_par=E),
            "rayon_conge_plinthe": Param(6.0, "mm", "Rayon du conge de raccord fut / plinthe.", plage=(0.0, 15.0),
                                         utilise_par=E),
            "part_abaque": Param(0.35, "", "Part du chapiteau occupee par l'abaque (tailloir).", plage=(0.15, 0.6),
                                 utilise_par=E),
            "chanfrein_arrete": Param(8.0, "mm", "Largeur (face vue) du chanfrein arrete des aretes du fut "
                                      "(section carree) ; 0 = arete vive.", plage=(0.0, 20.0), statut=VAL,
                                      utilise_par=E),
            "longueur_arret": Param(18.0, "mm", "Distance entre l'extremite du fut et le debut du chanfrein.",
                                    plage=(5.0, 60.0), utilise_par=E),
            "type_arret": Param("droit", "texte", "Arret du chanfrein : 'droit' (biais a 45 deg) ou "
                                "'langue_de_boeuf' (cuilleron concave).", choix=["droit", "langue_de_boeuf"],
                                statut=VAL, utilise_par=E),
        },
        "fourreau": {
            "paroi": Param(15.0, "mm", "Epaisseur de paroi du fourreau sur les plats, mesuree au plus fin "
                           "(haut du fut).", plage=(12.0, 40.0), utilise_par=E),
            "paroi_diagonale_min": Param(12.0, "mm", "Paroi mini dans les pans coupes (section octogonale).",
                                         plage=(8.0, 30.0), utilise_par=E),
            "jeu_haut": Param(10.0, "mm", "Jour entre le haut du fourreau et le dessous de platine au cran 0.",
                              plage=(3.0, 30.0), utilise_par=E),
            "frette_hauteur": Param(12.0, "mm", "Hauteur de la bague forgee au pied du fut, au-dessus du conge de "
                                    "plinthe (0 = sans).",
                                    plage=(0.0, 60.0), utilise_par=E),
        },
        "semelle": {
            "longueur": Param(566.0, "mm", "Longueur des semelles (patins) le long de Y : W x racine(2) "
                              "(trace ad quadratum, 566 mm) ; elargit le polygone de sustentation.",
                              plage=(400.0, 900.0), statut=VAL, utilise_par=E),
            "largeur": Param(140.0, "mm", "Largeur des semelles (axe X) : plinthe + 2 x chant (la plinthe ne "
                             "deborde plus de la semelle).", plage=(60.0, 200.0), utilise_par=E),
            "hauteur": Param(54.0, "mm", "Hauteur des semelles = largeur / phi^2 (54 mm).", plage=(40.0, 120.0),
                             utilise_par=E),
            "chant": Param("quart_de_rond", "texte", "Profil des aretes superieures longues de la semelle.",
                           choix=list(TYPES_CHANT), utilise_par=E),
            "chant_taille": Param(8.0, "mm", "Rayon du chant superieur de la semelle.", plage=(0.0, 20.0),
                                  utilise_par=E),
            "garde_cavet": Param(12.0, "mm", "Hauteur droite laissee sous le cavet des bouts de semelle "
                                 "(le cavet a pour rayon hauteur - garde).", plage=(5.0, 40.0), utilise_par=E),
            "profondeur_logement": Param(36.0, "mm", "Profondeur du logement ou descend le coulisseau en "
                                         "position basse.", plage=(0.0, 80.0), utilise_par=E),
        },
        "coulisseau": {
            "garde_bas": Param(5.0, "mm", "Jour sous le coulisseau au fond du logement, cran 0.",
                               plage=(2.0, 30.0), utilise_par=E),
        },
        "traverse": {
            "largeur": Param(60.0, "mm", "Largeur (Y) de la traverse basse longitudinale.", plage=(40.0, 100.0),
                             utilise_par=E),
            "hauteur": Param(70.0, "mm", "Hauteur (Z) de la traverse basse.", plage=(40.0, 120.0), utilise_par=E),
            "garde_sol": Param(10.0, "mm", "Jour sous la traverse basse.", plage=(0.0, 40.0), utilise_par=E),
        },
        "ceinture": {
            "active": Param(True, "bool", "Ceintures ajourees (bandeaux avant et arriere sous la platine).",
                            statut=VAL, utilise_par=E),
            "hauteur": Param(80.0, "mm", "Hauteur de la ceinture (e x phi = 81 mm).", plage=(40.0, 140.0),
                             utilise_par=E),
            "epaisseur": Param(20.0, "mm", "Epaisseur de la ceinture.", plage=(12.0, 40.0), utilise_par=E),
            "retrait": Param(20.0, "mm", "Retrait de la face de la ceinture sous le bord de platine.",
                             plage=(5.0, 60.0), utilise_par=E),
            "nombre_arcades": Param(5, "entier", "Nombre de baies ajourees par ceinture (impair : baie axiale).",
                                    plage=(1, 12), utilise_par=E),
            "ratio_largeur": Param(0.55, "", "Largeur de baie / entraxe des baies.", plage=(0.3, 0.8),
                                   utilise_par=E + R),
            "marge": Param(10.0, "mm", "Bois plein au-dessus et au-dessous des ajours.", plage=(5.0, 30.0),
                           utilise_par=E),
            "chanfrein_bas": Param(4.0, "mm", "Chanfrein des aretes inferieures de la ceinture.", plage=(0.0, 10.0),
                                   utilise_par=E),
        },
        "manilles": {
            "ecartement_poignets": Param(600.0, "mm", "Entraxe des deux manilles de poignets (epaules ouvertes).",
                                         plage=(450.0, 760.0), statut=IMP, utilise_par=E),
            "position_y": Param(0.0, "mm", "Decalage en Y de la ligne des manilles par rapport au milieu.",
                                plage=(-150.0, 150.0), utilise_par=E),
            "pivot_cou": Param("axe_vertical_chape", "texte", "Type de pivot de la manille de cou.",
                               choix=sorted(PIVOTS), statut=VAL, utilise_par=E + R),
            "pivot_poignets": Param("axe_vertical_chape", "texte", "Type de pivot des manilles de poignets.",
                                    choix=sorted(PIVOTS), utilise_par=E + R),
            "hauteur_pivot": Param(30.0, "mm", "Hauteur du pivot au-dessus de sa platine forgee.",
                                   plage=(15.0, 60.0), statut=DER, utilise_par=E + R),
        },
        "pentures": {
            "longueur": Param(160.0, "mm", "Longueur de chaque branche des pentures d'angle, terminaison "
                              "comprise.", plage=(60.0, 250.0), utilise_par=E),
            "recul_bord": Param(3.0, "mm", "Jour entre la terminaison la plus large et le bord de platine.",
                                plage=(0.0, 20.0), utilise_par=E),
            "rivets_par_branche": Param(3, "entier", "Rivets apparents par branche de penture.", plage=(1, 6),
                                        utilise_par=E),
        },
    },
}

#: Overrides par typologie (fusion profonde sur les defauts de la gamme).
OVERRIDES_TYPOLOGIE = {
    # Fabien : « platine rectangulaire en noyer massif ».
    "entrave": {"bois": {"essence": "noyer"}},
}


# ---------------------------------------------------------------------------
# Outils sur arbres
# ---------------------------------------------------------------------------
def fusion_profonde(base, ajout):
    """Fusionne recursivement ``ajout`` dans une copie de ``base``."""
    res = copy.deepcopy(base)
    for cle, val in (ajout or {}).items():
        if isinstance(val, dict) and isinstance(res.get(cle), dict):
            res[cle] = fusion_profonde(res[cle], val)
        else:
            res[cle] = copy.deepcopy(val)
    return res


def _iter_schema(arbre, prefixe=""):
    for cle, val in arbre.items():
        chemin = prefixe + cle
        if isinstance(val, Param):
            yield chemin, val
        else:
            for item in _iter_schema(val, chemin + "."):
                yield item


def _valeurs_depuis_schema(arbre):
    return {c: (copy.deepcopy(v.valeur) if isinstance(v, Param) else _valeurs_depuis_schema(v))
            for c, v in arbre.items()}


class Probleme(object):
    """Probleme de validation : niveau ('erreur' | 'alerte'), chemin, message."""

    def __init__(self, niveau, chemin, message):
        self.niveau, self.chemin, self.message = niveau, chemin, message

    def __repr__(self):
        return "[%s] %s : %s" % (self.niveau, self.chemin, self.message)

    __str__ = __repr__


class ErreurParametres(ValueError):
    """Levee par ``Parametres.verifier()`` quand il reste des erreurs."""


class Parametres(object):
    """Jeu de parametres Neogothique (valeurs + schema)."""

    UNITES_FUSION = {"mm": "mm", "deg": "deg", "kg": "kg", "N": "N", "": "", "entier": "", "%": ""}

    def __init__(self, valeurs=None, schema=None):
        self.schema = copy.deepcopy(schema if schema is not None else SCHEMA)
        self.valeurs = _valeurs_depuis_schema(self.schema)
        self.typologie = None
        if valeurs:
            self.fusionner(valeurs)

    # -- construction -------------------------------------------------------
    @classmethod
    def pour_typologie(cls, typologie, overrides=None, json_utilisateur=True):
        """Defauts gamme + overrides de typologie + JSON utilisateur + overrides explicites."""
        p = cls()
        p.typologie = typologie
        p.fusionner(OVERRIDES_TYPOLOGIE.get(typologie, {}))
        if json_utilisateur and os.path.exists(CHEMIN_JSON):
            with open(CHEMIN_JSON, "r", encoding="utf-8") as f:
                donnees = json.load(f)
            p.fusionner(donnees.get("commun", {}))
            p.fusionner(donnees.get("typologies", {}).get(typologie, {}))
        if overrides:
            p.fusionner(overrides)
        return p

    def copie(self):
        q = Parametres.__new__(Parametres)
        q.schema = copy.deepcopy(self.schema)
        q.valeurs = copy.deepcopy(self.valeurs)
        q.typologie = self.typologie
        return q

    def fusionner(self, overrides):
        """Fusion profonde (dict imbrique et/ou cles pointees {chemin: valeur})."""
        if not overrides:
            return self
        plats = {k: v for k, v in overrides.items() if "." in k}
        imbriques = {k: v for k, v in overrides.items() if "." not in k}
        self.valeurs = fusion_profonde(self.valeurs, imbriques)
        for chemin, val in plats.items():
            self.set(chemin, val, creer=True)
        return self

    # -- acces par chemin -----------------------------------------------------
    def get(self, chemin, defaut=_MANQUANT):
        noeud = self.valeurs
        for cle in chemin.split("."):
            if isinstance(noeud, dict) and cle in noeud:
                noeud = noeud[cle]
            elif defaut is not _MANQUANT:
                return defaut
            else:
                raise KeyError("Parametre inconnu : %s" % chemin)
        return noeud

    __getitem__ = get

    def set(self, chemin, valeur, creer=False):
        cles = chemin.split(".")
        noeud = self.valeurs
        for cle in cles[:-1]:
            if cle not in noeud:
                if not creer:
                    raise KeyError("Parametre inconnu : %s" % chemin)
                noeud[cle] = {}
            noeud = noeud[cle]
        if cles[-1] not in noeud and not creer:
            raise KeyError("Parametre inconnu : %s" % chemin)
        noeud[cles[-1]] = valeur
        return self

    def meta(self, chemin):
        noeud = self.schema
        for cle in chemin.split("."):
            if not isinstance(noeud, dict) or cle not in noeud:
                return None
            noeud = noeud[cle]
        return noeud if isinstance(noeud, Param) else None

    def defaut(self, chemin):
        """Valeur par defaut de la gamme (schema), avant overrides."""
        m = self.meta(chemin)
        return None if m is None else m.valeur

    def feuilles(self):
        """Itere (chemin, Param, valeur courante)."""
        for chemin, meta in _iter_schema(self.schema):
            yield chemin, meta, self.get(chemin, None)

    def chemins(self):
        return [c for c, _ in _iter_schema(self.schema)]

    def a_valider(self):
        return [(c, v, m) for c, m, v in self.feuilles() if m.statut == VAL]

    # -- grandeurs derivees simples ----------------------------------------------
    def debattement(self):
        return self.get("cremaillere.hauteur_maxi") - self.get("cremaillere.hauteur_mini")

    def nombre_positions(self):
        n = int(self.get("cremaillere.nombre_crans"))
        return n if self.get("cremaillere.convention") == "positions" else n + 1

    def hauteur_cran(self, cran=None):
        """Hauteur du dessus de platine : hauteur_mini + cran x pas."""
        cran = self.get("cremaillere.cran_courant") if cran is None else cran
        return self.get("cremaillere.hauteur_mini") + cran * self.get("cremaillere.pas")

    # -- validation ----------------------------------------------------------------
    def valider(self):
        """Bornes, choix et coherences. Renvoie une liste de ``Probleme``."""
        pbs = []
        for chemin, meta, val in self.feuilles():
            if val is None:
                pbs.append(Probleme("erreur", chemin, "valeur manquante"))
                continue
            if meta.unite == "bool" and not isinstance(val, bool):
                pbs.append(Probleme("erreur", chemin, "booleen attendu"))
            if meta.unite == "entier" and (isinstance(val, bool) or int(val) != val):
                pbs.append(Probleme("erreur", chemin, "entier attendu"))
            if meta.plage and isinstance(val, (int, float)) and not isinstance(val, bool):
                mini, maxi = meta.plage
                if not (mini <= val <= maxi):
                    pbs.append(Probleme("erreur", chemin, "%s %s hors plage [%s ; %s]" % (val, meta.unite, mini, maxi)))
            if meta.choix and val not in meta.choix:
                pbs.append(Probleme("erreur", chemin, "valeur %r non admise (%s)" % (val, meta.choix)))
        g = self.get
        tol = g("tolerances.ecart_debattement")
        # Cremaillere
        if g("cremaillere.hauteur_mini") >= g("cremaillere.hauteur_maxi"):
            pbs.append(Probleme("erreur", "cremaillere.hauteur_mini", "doit etre < hauteur_maxi"))
        n_int = self.nombre_positions() - 1
        course_crans = n_int * g("cremaillere.pas")
        if abs(course_crans - self.debattement()) > tol:
            pbs.append(Probleme("erreur", "cremaillere.nombre_crans",
                                "convention '%s' : %d intervalle(s) x %g mm = %g mm != debattement %g mm "
                                "(hauteur_maxi - hauteur_mini)" % (g("cremaillere.convention"), n_int,
                                                                   g("cremaillere.pas"), course_crans,
                                                                   self.debattement())))
        if not (0 <= g("cremaillere.cran_courant") <= self.nombre_positions() - 1):
            pbs.append(Probleme("erreur", "cremaillere.cran_courant",
                                "cran hors [0 ; %d]" % (self.nombre_positions() - 1)))
        if g("loquet.pene_diametre") >= g("cremaillere.pas"):
            pbs.append(Probleme("erreur", "loquet.pene_diametre", "pene >= pas : les trous de crans se recoupent"))
        elif g("cremaillere.pas") - g("loquet.pene_diametre") < 6.0:
            pbs.append(Probleme("alerte", "loquet.pene_diametre", "moins de 6 mm de matiere entre deux crans"))
        taux = DECORS_BARRE.get(g("cremaillere.decor_barre"), {}).get("taux_enlevement", 0.0)
        if g("loquet.pene_diametre") + 2 * 6.0 > g("cremaillere.barre_largeur") * (1.0 - taux) + 1e-9:
            pbs.append(Probleme("erreur", "cremaillere.barre_largeur", "barre trop etroite pour le trou du pene "
                                "(>= 6 mm de joue de chaque cote, section nette apres decor '%s' : -%d %%)" %
                                (g("cremaillere.decor_barre"), round(taux * 100))))
        if g("loquet.course") < g("cremaillere.barre_epaisseur") + g("loquet.engagement"):
            pbs.append(Probleme("erreur", "loquet.course", "course < epaisseur barre + engagement : "
                                "le pene ne libere pas la barre"))
        # Jonctions : regle du tiers, tourillons
        r, tr = g("jonctions.ratio_tenon"), g("jonctions.tolerance_ratio_tenon")
        if abs(r - 1.0 / 3.0) > tr:
            pbs.append(Probleme("alerte", "jonctions.ratio_tenon", "ratio %.3f eloigne de la regle du tiers" % r))
        paroi = g("entrave.fourreau.paroi")
        if g("jonctions.tourillon_diametre") > paroi / 2.0:
            pbs.append(Probleme("erreur", "jonctions.tourillon_diametre",
                                "tourillon %g mm > 1/2 paroi du fourreau (%g mm)" % (g("jonctions.tourillon_diametre"), paroi)))
        coul_approx = g("entrave.pied.cote") - 2 * paroi - 2 * g("tolerances.jeu_coulisseau")
        if g("jonctions.cheville_diametre") > coul_approx * r / 2.0 + 1e-9:
            pbs.append(Probleme("alerte", "jonctions.cheville_diametre", "cheville > 1/2 epaisseur de tenon"))
        # Materiaux
        cuir = g("garnissage.cuir_manilles")
        if cuir in GARNISSAGE and g("garnissage.coloris") not in GARNISSAGE[cuir]["coloris"]:
            pbs.append(Probleme("erreur", "garnissage.coloris", "coloris %r indisponible pour %s" % (g("garnissage.coloris"), cuir)))
        met, fin = g("ferrures.metal"), g("ferrures.finition")
        if fin in FINITIONS and met not in FINITIONS[fin]["metaux"]:
            pbs.append(Probleme("erreur", "ferrures.finition", "finition %r incompatible avec %r" % (fin, met)))
        ess = g("bois.essence")
        if ess in BOIS and g("bois.finition") not in BOIS[ess]["finitions_compatibles"]:
            pbs.append(Probleme("erreur", "bois.finition", "finition %r incompatible avec %r" % (g("bois.finition"), ess)))
        # Entrave : geometrie simple
        L, ec = g("entrave.platine.longueur"), g("entrave.manilles.ecartement_poignets")
        if ec + g("ferrures.platine_pivot_cote") > L - 2 * g("entrave.pied.retrait_bord"):
            pbs.append(Probleme("erreur", "entrave.manilles.ecartement_poignets", "manilles hors de la platine"))
        cote_fut_haut = g("entrave.pied.cote") - 2 * g("entrave.pied.fuselage")
        if 2 * paroi + 2 * g("tolerances.jeu_coulisseau") + g("bois.section_mini") > cote_fut_haut:
            pbs.append(Probleme("erreur", "entrave.pied.cote", "pied trop fin : coulisseau < section mini "
                                "(au haut du fut, fuselage deduit)"))
        # Style : moulures, proportions, ferrures affinees
        if g("entrave.platine.chant_dessous_profondeur") > g("entrave.pied.retrait_bord") - 5.0:
            pbs.append(Probleme("erreur", "entrave.platine.chant_dessous_profondeur",
                                "la moulure de sous-face doit s'arreter >= 5 mm avant l'appui du chapiteau "
                                "(profondeur <= retrait_bord - 5)"))
        h_chants = g("entrave.platine.chant_dessus_taille") + g("entrave.platine.chant_dessous_hauteur")
        if h_chants > g("entrave.platine.epaisseur") - 6.0:
            pbs.append(Probleme("erreur", "entrave.platine.chant_dessous_hauteur",
                                "chants dessus + dessous (%g mm) : garder >= 6 mm de chant droit" % h_chants))
        if g("ferrures.tete_rivet_diametre") < 1.5 * g("ferrures.rivet_diametre") - 1e-9:
            pbs.append(Probleme("erreur", "ferrures.tete_rivet_diametre",
                                "tete de rivet < 1,5 x tige : la rivure ne tient pas (arrachement de tete)"))
        if g("style.proportions") == "libre" and g("style.part_plinthe") + g("style.part_chapiteau") > 0.7:
            pbs.append(Probleme("erreur", "style.part_chapiteau", "plinthe + chapiteau > 70 % du pied : fut trop court"))
        if g("entrave.semelle.largeur") < g("entrave.pied.cote") + 2 * g("entrave.pied.debord_base"):
            pbs.append(Probleme("alerte", "entrave.semelle.largeur", "la plinthe deborde de la semelle"))
        if g("style.proportions") == "nombre_or":
            hs_or = g("entrave.semelle.largeur") / PHI ** 2
            if abs(g("entrave.semelle.hauteur") - hs_or) > 3.0:
                pbs.append(Probleme("alerte", "entrave.semelle.hauteur", "hors proportion d'or (largeur/phi^2 = "
                                    "%.0f mm)" % hs_or))
        if g("entrave.semelle.garde_cavet") > g("entrave.semelle.hauteur") - 10.0:
            pbs.append(Probleme("erreur", "entrave.semelle.garde_cavet", "cavet de bout de semelle < 10 mm"))
        if g("entrave.semelle.profondeur_logement") > g("entrave.semelle.hauteur") - 15.0:
            pbs.append(Probleme("erreur", "entrave.semelle.profondeur_logement", "laisser >= 15 mm sous le logement"))
        if g("entrave.semelle.longueur") < g("entrave.platine.largeur"):
            pbs.append(Probleme("alerte", "entrave.semelle.longueur", "semelle plus courte que la platine : "
                                "polygone de sustentation reduit"))
        if g("securite.ouverture_rapide_cou") is not True:
            pbs.append(Probleme("alerte", "securite.ouverture_rapide_cou",
                                "manille de cou sans ouverture rapide : deconseille"))
        return pbs

    def erreurs(self):
        return [p for p in self.valider() if p.niveau == "erreur"]

    def verifier(self):
        """Leve ``ErreurParametres`` s'il reste des erreurs ; renvoie les alertes."""
        pbs = self.valider()
        err = [p for p in pbs if p.niveau == "erreur"]
        if err:
            raise ErreurParametres("\n".join(str(e) for e in err))
        return pbs

    # -- persistance -----------------------------------------------------------------
    def vers_json(self, chemin_fichier=None):
        texte = json.dumps(self.valeurs, indent=2, ensure_ascii=False, sort_keys=True)
        if chemin_fichier:
            with open(chemin_fichier, "w", encoding="utf-8") as f:
                f.write(texte)
        return texte

    @classmethod
    def depuis_json(cls, texte_ou_chemin):
        if os.path.exists(str(texte_ou_chemin)):
            with open(texte_ou_chemin, "r", encoding="utf-8") as f:
                texte_ou_chemin = f.read()
        return cls(json.loads(texte_ou_chemin))

    # -- export Fusion -------------------------------------------------------------------
    @staticmethod
    def nom_fusion(chemin, prefixe="neo_"):
        """'cremaillere.pas' -> 'neo_cremaillere_pas' (nom valide de User Parameter).

        Fusion exige : premiere lettre alphabetique, puis lettres/chiffres/_ ;
        pas d'espace ni d'accent ni de point.
        """
        nom = prefixe + re.sub(r"[^A-Za-z0-9_]", "_", chemin.replace(".", "_"))
        nom = re.sub(r"_+", "_", nom)
        if not nom[0].isalpha():
            nom = "p" + nom
        return nom

    def parametres_exportables(self):
        """Liste (nom, expression, unite_fusion, commentaire) des parametres numeriques."""
        prefixe = self.get("gamme.prefixe_fusion", "neo_")
        res = []
        for chemin, meta, val in self.feuilles():
            if isinstance(val, bool) or not isinstance(val, (int, float)):
                continue
            unite = self.UNITES_FUSION.get(meta.unite, "")
            expression = ("%.6g %s" % (val, unite)).strip()
            commentaire = "%s [%s%s] %s" % (chemin, meta.statut, (", " + meta.unite) if meta.unite else "", meta.role)
            res.append((self.nom_fusion(chemin, prefixe), expression, unite, commentaire[:250]))
        return res

    def exporter_user_parameters(self, design, extras=None):
        """Cree ou met a jour les User Parameters de ``design`` (Fusion).

        :param extras: liste supplementaire (nom, expression, unite, commentaire),
            p. ex. les parametres derives a expression liee de la grammaire.
        :return: (crees, mis_a_jour) listes de noms.

        Fusion convertit lui-meme '25 mm' en cm internes (pas de conversion ici).
        """
        from . import fusion_outils
        lignes = self.parametres_exportables() + list(extras or [])
        return fusion_outils.ecrire_user_parameters(design, lignes)


def tableau_markdown(params=None):
    """Tableau markdown (chemin, valeur, unite, role, plage, statut, utilise par)."""
    p = params or Parametres()
    lignes = ["| Chemin | Valeur | Unite | Role | Plage / choix | Statut | Utilise par |",
              "|---|---|---|---|---|---|---|"]
    for chemin, meta, val in p.feuilles():
        if meta.plage:
            plage = "%g - %g" % meta.plage
        elif meta.choix:
            plage = ", ".join(str(c) for c in meta.choix)
        else:
            plage = ""
        v = ("%.4g" % val) if isinstance(val, float) else str(val)
        lignes.append("| `%s` | %s | %s | %s | %s | %s | %s |" % (chemin, v, meta.unite, meta.role.replace("|", "/"),
                                                                plage, meta.statut, ", ".join(meta.utilise_par)))
    return "\n".join(lignes)
