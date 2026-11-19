# -*- coding: utf-8 -*-
"""Couche 1 - Parametres globaux partages de la gamme Equinox.

Chaque parametre est une *feuille* du schema ``SCHEMA`` decrite par
``Param`` : valeur par defaut, unite, role, plage admissible, statut
(impose par Fabien / propose a valider) et liste des modules qui l'utilisent.

Unites internes : mm, kg, deg, N, MPa, % (jamais de cm ici).

Usage ::

    from equinox.parametres import Parametres
    p = Parametres.pour_typologie("banc_flore")
    p.get("bois.section_noeud")            # 50
    p.set("garnissage.materiau", "tissu_krypton")
    problemes = p.valider()
    p.exporter_user_parameters(design)     # dans Fusion uniquement
"""

import copy
import json
import os
import re

_MANQUANT = object()

#: Fichier JSON optionnel d'overrides utilisateur (memes chemins que SCHEMA).
CHEMIN_JSON = os.path.join(os.path.dirname(__file__), "parametres_equinox.json")


class Param(object):
    """Description d'un parametre (feuille du schema).

    :param valeur: valeur par defaut.
    :param unite: unite interne ("mm", "kg", "deg", "N", "MPa", "%", "kg/m3",
        "" sans unite, "texte", "bool", "liste").
    :param role: phrase expliquant a quoi sert le parametre.
    :param plage: tuple (mini, maxi) pour les numeriques, ou None.
    :param choix: liste des valeurs admises pour les textes, ou None.
    :param statut: "impose" (valeur fixee par Fabien), "a_valider" (valeur
        proposee, a trancher), "derive" (recalcule par les regles), "libre".
    :param utilise_par: modules / typologies qui lisent ce parametre.
    """

    __slots__ = ("valeur", "unite", "role", "plage", "choix", "statut", "utilise_par")

    def __init__(self, valeur, unite, role, plage=None, choix=None,
                 statut="libre", utilise_par=()):
        self.valeur = valeur
        self.unite = unite
        self.role = role
        self.plage = plage
        self.choix = choix
        self.statut = statut
        self.utilise_par = tuple(utilise_par)

    def __repr__(self):
        return "Param(%r %s, %s)" % (self.valeur, self.unite, self.statut)


TOUS = ("banc_flore", "croix_saint_andre", "tabouret", "chaise_trone", "cheval_arcon")
IMP, VAL, DER = "impose", "a_valider", "derive"

# ---------------------------------------------------------------------------
# SCHEMA : le vocabulaire Equinox
# ---------------------------------------------------------------------------
SCHEMA = {
    "gamme": {
        "nom": Param("Equinox", "texte", "Nom de la gamme (prefixe des composants Fusion)."),
        "prefixe_fusion": Param("eq_", "texte", "Prefixe des User Parameters crees dans Fusion."),
    },
    "dimensions": {
        "hauteur_assise": Param(700.0, "mm", "Hauteur du dessus de garnissage (plateau / assise) au sol, point haut.",
                                (350.0, 950.0), statut=IMP, utilise_par=TOUS),
        "hauteur_structure": Param(652.0, "mm", "Dessous du support garni = hauteur_assise - rembourrage - "
                                   "support : recalculee quand le rembourrage change pour garder l'assise.",
                                   (200.0, 950.0), statut=DER, utilise_par=("banc_flore",)),
        "longueur_plateau": Param(1150.0, "mm", "Longueur nominale du plateau garni (mode 'complet').",
                                  (500.0, 1600.0), statut=IMP, utilise_par=("banc_flore", "cheval_arcon")),
        "mode_longueur": Param("complet", "texte",
                               "'complet' = longueur_plateau ; 'bassin_epaules' = plateau raccourci a "
                               "longueur_bassin_epaules + marges.",
                               choix=["complet", "bassin_epaules"], statut=VAL, utilise_par=("banc_flore",)),
        "longueur_bassin_epaules": Param(540.0, "mm", "Distance bassin (grand trochanter) - epaules (acromion) "
                                         "de l'utilisateur, a mesurer sur la personne.",
                                         (380.0, 700.0), statut=VAL, utilise_par=("banc_flore",)),
        "marge_bassin": Param(80.0, "mm", "Debord du plateau cote bassin (arriere) au-dela du trochanter.",
                              (0.0, 200.0), statut=VAL, utilise_par=("banc_flore",)),
        "marge_epaules": Param(60.0, "mm", "Debord du plateau cote epaules (avant), degage la poitrine.",
                               (0.0, 200.0), statut=VAL, utilise_par=("banc_flore",)),
        "largeur_plateau": Param(340.0, "mm", "Largeur du plateau garni (buste).",
                                 (220.0, 600.0), statut=VAL, utilise_par=("banc_flore", "cheval_arcon", "tabouret")),
        "porte_a_faux": Param(110.0, "mm", "Retrait longitudinal du noeud de pied par rapport au bout du plateau.",
                              (40.0, 250.0), statut=VAL, utilise_par=("banc_flore", "cheval_arcon")),
        "retrait_lateral_pieds": Param(40.0, "mm", "Retrait lateral du noeud de pied par rapport au chant du plateau.",
                                       (0.0, 120.0), statut=VAL, utilise_par=("banc_flore", "cheval_arcon")),
        "hauteur_appui_genoux": Param(430.0, "mm", "Hauteur du dessus des repose-genoux (position levrette).",
                                      (250.0, 600.0), statut=VAL, utilise_par=("banc_flore",)),
        "entraxe_genoux": Param(480.0, "mm", "Entraxe lateral des deux repose-genoux (genoux de part et d'autre du plateau, cuisses le long des chants).",
                                (250.0, 600.0), statut=VAL, utilise_par=("banc_flore",)),
        "recul_genoux": Param(100.0, "mm", "Position longitudinale du centre genou depuis le bout arriere du "
                              "plateau (positif = sous le plateau).", (-100.0, 300.0), statut=VAL,
                              utilise_par=("banc_flore",)),
        "hauteur_appui_coudes": Param(570.0, "mm", "Hauteur du dessus des repose-coudes.",
                                      (400.0, 750.0), statut=VAL, utilise_par=("banc_flore",)),
        "entraxe_coudes": Param(480.0, "mm", "Entraxe lateral des repose-coudes (plus large que le plateau).",
                                (300.0, 800.0), statut=VAL, utilise_par=("banc_flore",)),
        "avance_coudes": Param(60.0, "mm", "Avance des repose-coudes par rapport au bout avant du plateau "
                               "(negatif = en retrait sous le plateau).", (-200.0, 200.0), statut=VAL,
                               utilise_par=("banc_flore",)),
    },
    "bois": {
        "essence": Param("frene", "texte", "Cle de l'essence dans catalogues.bois.", statut=IMP, utilise_par=TOUS),
        "section_noeud": Param(50.0, "mm", "Diametre des sections bois au noeud (jonction, zone la plus sollicitee).",
                               (30.0, 90.0), statut=IMP, utilise_par=TOUS),
        "section_extremite": Param(30.0, "mm", "Diametre des sections bois aux extremites (pieds, bouts de branches).",
                                   (20.0, 70.0), statut=IMP, utilise_par=TOUS),
        "section_entre_noeuds": Param(40.0, "mm", "Diametre au plus fin entre deux noeuds d'une meme piece "
                                      "(galbe 'branche' : noeud 50 -> 40 -> noeud 50).", (25.0, 70.0), statut=VAL,
                                      utilise_par=TOUS),
        "rayon_courbure_min": Param(300.0, "mm", "Rayon de courbure minimal des pieces cintrees (verifie par les "
                                    "regles selon essence et methode de cintrage).", (100.0, 2000.0),
                                    statut=VAL, utilise_par=TOUS),
        "methode_cintrage": Param("lamelle_colle", "texte", "Methode de cintrage des courbes.",
                                  choix=["lamelle_colle", "vapeur", "massif_debite"], statut=VAL, utilise_par=TOUS),
        "epaisseur_lamelle": Param(3.0, "mm", "Epaisseur des lamelles en lamelle-colle cintre.",
                                   (1.0, 8.0), statut=VAL, utilise_par=TOUS),
        "angle_splay": Param(7.0, "deg", "Angle d'ecartement (splay) des pieds vers l'exterieur, par rapport a la "
                             "verticale.", (0.0, 20.0), statut=IMP, utilise_par=TOUS),
        "section_traverse": Param(60.0, "mm", "Cote de l'enveloppe bois carree de la traverse lestee "
                                  "(tube 40x40 + 2 x 10 mm de bois).", (50.0, 120.0), statut=VAL,
                                  utilise_par=("banc_flore", "cheval_arcon", "croix_saint_andre")),
        "longeron_largeur": Param(40.0, "mm", "Largeur des longerons sous plateau (ceinture).",
                                  (25.0, 80.0), statut=VAL, utilise_par=("banc_flore", "cheval_arcon")),
        "longeron_hauteur": Param(70.0, "mm", "Hauteur des longerons sous plateau.",
                                  (40.0, 140.0), statut=VAL, utilise_par=("banc_flore", "cheval_arcon")),
        "humidite_cible": Param(10.0, "%", "Humidite du bois a la mise en oeuvre (interieur chauffe).",
                                (6.0, 15.0), statut=VAL, utilise_par=TOUS),
    },
    "garnissage": {
        "materiau": Param("cuir_classique_pleine_fleur", "texte", "Famille de revetement : cle dans "
                          "catalogues.garnissage (cuir_classique_pleine_fleur, cuir_vegan, tissu_krypton, "
                          "cuir_synthetique_hq, tissu_technique_enduit ; anciennes cles acceptees).",
                          statut=IMP, utilise_par=TOUS),
        "couleur": Param("cognac", "texte", "Coloris ; doit exister dans la famille choisie (valide).",
                         statut=IMP, utilise_par=TOUS),
        "epaisseur_rembourrage": Param(30.0, "mm", "Epaisseur de mousse sous le revetement : 30 mm pour le cuir "
                                       "classique (valeur de reference), recalculee par famille (vegan +5, "
                                       "Krypton 40...).", (10.0, 80.0), statut=DER, utilise_par=TOUS),
        "inclinaison_plateau": Param(2.0, "deg", "Inclinaison du plateau (sens donne par flore.sens_inclinaison ; "
                                     "defaut : bassin haut, epaules basses).",
                                     (0.0, 15.0), statut=IMP, utilise_par=("banc_flore", "cheval_arcon")),
        "epaisseur_support": Param(18.0, "mm", "Epaisseur du support contreplaque bouleau sous la mousse.",
                                   (9.0, 30.0), statut=VAL, utilise_par=TOUS),
        "densite_mousse": Param(50.0, "kg/m3", "Masse volumique de la mousse HR (portance).",
                                (25.0, 80.0), statut=VAL, utilise_par=TOUS),
        "methode_fixation": Param("agrafage_sous_plateau", "texte", "Mode de fixation du revetement (derive de la "
                                  "famille).", choix=["agrafage_sous_plateau", "agrafage_ou_scratch",
                                                      "collage_et_agrafage"], statut=DER, utilise_par=TOUS),
        "finition_bords": Param("ourlets_cousus", "texte", "Finition des bords (derivee de la famille).",
                                choix=["ourlets_cousus", "rembordage_sans_couture", "rembordage_colle"],
                                statut=DER, utilise_par=TOUS),
        "coutures_sur_courbes": Param(False, "bool", "La grammaire prevoit des coutures apparentes (surpiqures, "
                                      "passepoil) sur des bords courbes ; declenche l'avertissement du tissu Krypton.",
                                      statut=VAL, utilise_par=TOUS),
        "rayon_bord": Param(12.0, "mm", "Rayon des aretes du coussin (derive de la famille).",
                            (3.0, 40.0), statut=DER, utilise_par=TOUS),
    },
    "inox": {
        "nuance": Param("inox_316", "texte", "Cle de la nuance dans catalogues.metaux.", statut=VAL, utilise_par=TOUS),
        "diametre_tube_helice": Param(12.0, "mm", "Diametre exterieur du tube / rond de l'helice.",
                                      (8.0, 30.0), statut=IMP, utilise_par=("banc_flore",)),
        "section_helice": Param("plein", "texte", "'plein' (rond plein) ou 'tube' (tube, voir epaisseur_paroi_helice).",
                                choix=["plein", "tube"], statut=VAL, utilise_par=("banc_flore",)),
        "epaisseur_paroi_helice": Param(2.0, "mm", "Paroi si section_helice = 'tube'.", (1.0, 4.0), statut=VAL,
                                        utilise_par=("banc_flore",)),
        "nombre_tours_helice": Param(2.0, "", "Nombre de tours de l'helice.", (0.5, 5.0), statut=IMP,
                                     utilise_par=("banc_flore",)),
        "crans_verrouillage": Param(2, "", "Nombre de crans de verrouillage du pivot d'helice.", (1, 6), statut=IMP,
                                    utilise_par=("banc_flore",)),
        "angle_entre_crans": Param(35.0, "deg", "Angle de pivotement entre deux crans (position usage / rangee).",
                                   (10.0, 180.0), statut=VAL, utilise_par=("banc_flore",)),
        "diametre_axe_pivot": Param(16.0, "mm", "Diametre de l'axe de pivot d'helice dans le pied arriere.",
                                    (10.0, 30.0), statut=VAL, utilise_par=("banc_flore",)),
        "hauteur_pivot": Param(300.0, "mm", "Hauteur du pivot d'helice sur le pied arriere.",
                               (100.0, 600.0), statut=VAL, utilise_par=("banc_flore",)),
        "diametre_oeillet": Param(8.0, "mm", "Diametre du fil des oeillets d'ancrage.", (5.0, 16.0), statut=IMP,
                                  utilise_par=TOUS),
        "epaisseur_plaque": Param(2.0, "mm", "Epaisseur des plaques inox (platines, semelles d'oeillet).",
                                  (1.5, 6.0), statut=IMP, utilise_par=TOUS),
    },
    "laiton": {
        "nuance": Param("laiton_cw614n", "texte", "Cle du laiton dans catalogues.metaux.", statut=VAL,
                        utilise_par=TOUS),
        "diametre_capuchon": Param(40.0, "mm", "Diametre des capuchons / embouts laiton.", (20.0, 80.0),
                                   statut=IMP, utilise_par=TOUS),
        "epaisseur_capuchon": Param(3.0, "mm", "Epaisseur du fond des capuchons laiton.", (1.0, 8.0),
                                    statut=IMP, utilise_par=TOUS),
        "hauteur_jupe": Param(12.0, "mm", "Hauteur de la jupe du capuchon remontant sur le bois.",
                              (0.0, 40.0), statut=VAL, utilise_par=TOUS),
    },
    "traverse": {
        "cote_tube": Param(40.0, "mm", "Cote du tube carre inox de la traverse lestee.", (20.0, 80.0), statut=IMP,
                           utilise_par=("banc_flore", "cheval_arcon", "croix_saint_andre")),
        "epaisseur_paroi": Param(2.0, "mm", "Paroi du tube carre 40x40.", (1.5, 5.0), statut=VAL,
                                 utilise_par=("banc_flore", "cheval_arcon", "croix_saint_andre")),
        "lest_min": Param(15.0, "kg", "Lest integre minimal.", (0.0, 60.0), statut=IMP,
                          utilise_par=("banc_flore", "cheval_arcon", "croix_saint_andre")),
        "lest_max": Param(20.0, "kg", "Lest integre maximal.", (0.0, 80.0), statut=IMP,
                          utilise_par=("banc_flore", "cheval_arcon", "croix_saint_andre")),
        "lest_nominal": Param(18.0, "kg", "Lest vise (entre lest_min et lest_max).", (0.0, 80.0), statut=VAL,
                              utilise_par=("banc_flore", "cheval_arcon", "croix_saint_andre")),
        "materiau_lest": Param("plomb", "texte", "Cle du materiau de lest dans catalogues.metaux.", statut=VAL,
                               choix=["plomb", "acier_plein", "grenaille_acier"],
                               utilise_par=("banc_flore", "cheval_arcon", "croix_saint_andre")),
        "hauteur_axe": Param(130.0, "mm", "Hauteur de l'axe de la traverse arriere au sol (bas = CG bas).",
                             (60.0, 400.0), statut=VAL, utilise_par=("banc_flore", "cheval_arcon")),
    },
    "ancrage": {
        "oeillets_bas": Param(True, "bool", "Oeillets bas encastres sous les semelles des pieds arriere.",
                              statut=IMP, utilise_par=TOUS),
        "profondeur_encastrement": Param(10.0, "mm", "Profondeur de la feuillure sous semelle recevant la platine "
                                         "d'oeillet.", (3.0, 25.0), statut=VAL, utilise_par=TOUS),
        "saillie_oeillet": Param(18.0, "mm", "Saillie de l'oeil hors de l'empreinte du pied (accessible).",
                                 (8.0, 40.0), statut=VAL, utilise_par=TOUS),
        "anneau_arriere": Param(True, "bool", "Anneau arriere a mi-hauteur de traverse.", statut=IMP,
                                utilise_par=("banc_flore", "cheval_arcon")),
        "position_anneau": Param("mi_hauteur_traverse", "texte", "Position de l'anneau arriere.",
                                 choix=["mi_hauteur_traverse"], statut=IMP, utilise_par=("banc_flore",)),
        "diametre_interieur_anneau": Param(40.0, "mm", "Diametre interieur de l'anneau arriere.",
                                           (20.0, 80.0), statut=VAL, utilise_par=TOUS),
        "attache_oeillet": Param("oeillet_inox_8", "texte", "Cle de l'oeillet dans catalogues.attaches.",
                                 statut=VAL, utilise_par=TOUS),
        "attache_anneau": Param("anneau_inox_8", "texte", "Cle de l'anneau dans catalogues.attaches.",
                                statut=VAL, utilise_par=TOUS),
    },
    "securite": {
        "charge_utilisateur": Param(120.0, "kg", "Masse de l'utilisateur prise en compte.", (40.0, 200.0),
                                    statut=IMP, utilise_par=TOUS),
        "coefficient_dynamique": Param(2.0, "", "Majoration des efforts verticaux (mouvements, impacts).",
                                       (1.0, 4.0), statut=VAL, utilise_par=TOUS),
        "coefficient_horizontal_long": Param(0.30, "", "Effort horizontal longitudinal = coef x poids utilisateur "
                                             "(poussee du partenaire en levrette).", (0.0, 1.0), statut=VAL,
                                             utilise_par=TOUS),
        "coefficient_horizontal_lat": Param(0.15, "", "Effort horizontal lateral = coef x poids utilisateur.",
                                            (0.0, 1.0), statut=VAL, utilise_par=TOUS),
        "securite_bois": Param(3.0, "", "Coefficient de securite sur la resistance en flexion du bois (MOR).",
                               (1.5, 6.0), statut=VAL, utilise_par=TOUS),
        "securite_metal": Param(1.8, "", "Coefficient de securite sur la limite elastique des metaux.",
                                (1.2, 4.0), statut=VAL, utilise_par=TOUS),
        "securite_renversement": Param(1.5, "", "Rapport mini moment stabilisant / moment renversant.",
                                       (1.0, 3.0), statut=VAL, utilise_par=TOUS),
        "fleche_admissible": Param(300.0, "", "Fleche admissible = portee / ce nombre.", (100.0, 1000.0),
                                   statut=VAL, utilise_par=TOUS),
        "frottement_sol": Param(0.30, "", "Coefficient de frottement embout laiton / sol (parquet vitrifie).",
                                (0.1, 0.8), statut=VAL, utilise_par=TOUS),
    },
    "jonctions": {
        "diametre_tourillon": Param(10.0, "mm", "Diametre des tourillons (derive de la section).", (6.0, 16.0),
                                    statut=DER, utilise_par=TOUS),
        "longueur_tourillon": Param(50.0, "mm", "Longueur des tourillons (>= 5 x diametre).", (30.0, 100.0),
                                    statut=DER, utilise_par=TOUS),
        "epaisseur_tenon": Param(17.0, "mm", "Epaisseur des tenons (~ 1/3 de la section au noeud).", (8.0, 40.0),
                                 statut=DER, utilise_par=TOUS),
        "profondeur_mortaise": Param(40.0, "mm", "Profondeur des mortaises.", (20.0, 80.0), statut=DER,
                                     utilise_par=TOUS),
        "filetage_insert": Param("M8", "texte", "Filetage des inserts / taraudages (pivots, glissieres, ancrages).",
                                 choix=["M6", "M8", "M10"], statut=VAL, utilise_par=TOUS),
        "longueur_insert": Param(20.0, "mm", "Longueur des inserts filetes (derivee de la densite du bois).",
                                 (10.0, 40.0), statut=DER, utilise_par=TOUS),
    },
}

#: Overrides par typologie (fusion profonde sur les valeurs par defaut).
OVERRIDES_TYPOLOGIE = {
    "banc_flore": {"garnissage": {"coutures_sur_courbes": True}},  # surpiqure 'nervure' sur le contour feuille
    "cheval_arcon": {"dimensions": {"hauteur_assise": 760.0, "longueur_plateau": 700.0, "largeur_plateau": 260.0}},
    "tabouret": {"dimensions": {"hauteur_assise": 440.0, "largeur_plateau": 380.0}},
    "chaise_trone": {"dimensions": {"hauteur_assise": 460.0, "largeur_plateau": 480.0},
                     "garnissage": {"inclinaison_plateau": 4.0}},
    "croix_saint_andre": {"securite": {"coefficient_horizontal_long": 0.25}},
}


# ---------------------------------------------------------------------------
# Outils sur arbres de dictionnaires
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
    res = {}
    for cle, val in arbre.items():
        res[cle] = copy.deepcopy(val.valeur) if isinstance(val, Param) else _valeurs_depuis_schema(val)
    return res


class Probleme(object):
    """Probleme de validation : niveau ('erreur' | 'alerte'), chemin, message."""

    def __init__(self, niveau, chemin, message):
        self.niveau, self.chemin, self.message = niveau, chemin, message

    def __repr__(self):
        return "[%s] %s : %s" % (self.niveau, self.chemin, self.message)


class Parametres(object):
    """Jeu de parametres Equinox (valeurs + schema eventuellement etendu)."""

    def __init__(self, valeurs=None, schema=None):
        self.schema = copy.deepcopy(schema if schema is not None else SCHEMA)
        self.valeurs = _valeurs_depuis_schema(self.schema)
        self.typologie = None
        if valeurs:
            self.fusionner(valeurs)

    # -- construction -----------------------------------------------------
    @classmethod
    def pour_typologie(cls, typologie, overrides=None, json_utilisateur=True):
        """Defauts + overrides de typologie + JSON utilisateur + overrides explicites."""
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

    def etendre(self, racine, schema_specifique):
        """Ajoute un sous-schema propre a une typologie (ex. 'croix')."""
        self.schema[racine] = copy.deepcopy(schema_specifique)
        existant = self.valeurs.get(racine, {})
        self.valeurs[racine] = fusion_profonde(_valeurs_depuis_schema(schema_specifique), existant)
        return self

    def fusionner(self, overrides):
        """Fusion profonde d'overrides (dict imbrique ou {chemin: valeur})."""
        if not overrides:
            return self
        plats = {k: v for k, v in overrides.items() if "." in k}
        imbriques = {k: v for k, v in overrides.items() if "." not in k}
        self.valeurs = fusion_profonde(self.valeurs, imbriques)
        for chemin, val in plats.items():
            self.set(chemin, val, creer=True)
        return self

    # -- acces par chemin ---------------------------------------------------
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

    def meta(self, chemin):
        """Renvoie le ``Param`` du schema pour ce chemin (ou None)."""
        noeud = self.schema
        for cle in chemin.split("."):
            if not isinstance(noeud, dict) or cle not in noeud:
                return None
            noeud = noeud[cle]
        return noeud if isinstance(noeud, Param) else None

    def feuilles(self):
        """Itere (chemin, Param, valeur courante) sur tout le schema."""
        for chemin, meta in _iter_schema(self.schema):
            yield chemin, meta, self.get(chemin, None)

    def a_valider(self):
        return [(c, v, m) for c, m, v in self.feuilles() if m.statut == VAL]

    # -- validation ---------------------------------------------------------
    def valider(self):
        """Bornes, choix et coherences. Renvoie une liste de ``Probleme``."""
        pbs = []
        for chemin, meta, val in self.feuilles():
            if meta.plage and isinstance(val, (int, float)) and not isinstance(val, bool):
                mini, maxi = meta.plage
                if not (mini <= val <= maxi):
                    pbs.append(Probleme("erreur", chemin, "%s %s hors plage [%s ; %s]" %
                                        (val, meta.unite, mini, maxi)))
            if meta.choix and val not in meta.choix:
                pbs.append(Probleme("erreur", chemin, "valeur %r non admise (%s)" % (val, meta.choix)))
        g = self.get
        from .catalogues import garnissage as _garn  # import differe (pas de dependance circulaire)
        mat = g("garnissage.materiau")
        if mat not in _garn.GARNISSAGES:
            pbs.append(Probleme("erreur", "garnissage.materiau", "famille %r inconnue (%s)"
                                % (mat, sorted(dict.keys(_garn.GARNISSAGES)))))
        elif not _garn.coloris_valide(mat, g("garnissage.couleur")):
            pbs.append(Probleme("erreur", "garnissage.couleur", "coloris %r absent de %s (disponibles : %s)"
                                % (g("garnissage.couleur"), _garn.resoudre(mat), _garn.GARNISSAGES[mat]["coloris"])))
        hs = g("dimensions.hauteur_assise") - g("garnissage.epaisseur_rembourrage") - g("garnissage.epaisseur_support")
        if abs(hs - g("dimensions.hauteur_structure")) > 0.5:
            pbs.append(Probleme("alerte", "dimensions.hauteur_structure", "non recalculee (%.1f attendu) : "
                                "appliquer regles.appliquer_materiaux_actifs" % hs))
        if g("bois.section_extremite") > g("bois.section_noeud"):
            pbs.append(Probleme("erreur", "bois.section_extremite", "doit etre <= section_noeud (fuseau)"))
        if not (g("traverse.lest_min") <= g("traverse.lest_nominal") <= g("traverse.lest_max")):
            pbs.append(Probleme("erreur", "traverse.lest_nominal", "doit etre entre lest_min et lest_max"))
        if g("laiton.diametre_capuchon") < g("bois.section_extremite"):
            pbs.append(Probleme("erreur", "laiton.diametre_capuchon", "plus petit que la section d'extremite"))
        if g("bois.section_traverse") < g("traverse.cote_tube") + 2 * 8:
            pbs.append(Probleme("erreur", "bois.section_traverse", "enveloppe bois < tube + 2 x 8 mm"))
        if not (g("bois.section_extremite") <= g("bois.section_entre_noeuds") <= g("bois.section_noeud")):
            pbs.append(Probleme("erreur", "bois.section_entre_noeuds", "doit etre entre extremite et noeud"))
        if g("dimensions.hauteur_appui_genoux") >= g("dimensions.hauteur_assise"):
            pbs.append(Probleme("erreur", "dimensions.hauteur_appui_genoux", "doit etre sous le plateau"))
        if g("inox.diametre_oeillet") > g("inox.diametre_axe_pivot"):
            pbs.append(Probleme("alerte", "inox.diametre_oeillet", "fil d'oeillet plus gros que l'axe de pivot ?"))
        if g("inox.section_helice") == "tube" and 2 * g("inox.epaisseur_paroi_helice") >= g("inox.diametre_tube_helice"):
            pbs.append(Probleme("erreur", "inox.epaisseur_paroi_helice", "paroi incompatible avec le diametre"))
        if 2 * g("traverse.epaisseur_paroi") >= g("traverse.cote_tube"):
            pbs.append(Probleme("erreur", "traverse.epaisseur_paroi", "paroi incompatible avec le tube"))
        if g("jonctions.epaisseur_tenon") > g("bois.section_noeud") / 2.0:
            pbs.append(Probleme("alerte", "jonctions.epaisseur_tenon", "tenon > 1/2 section : joues trop fines"))
        if g("dimensions.mode_longueur") == "bassin_epaules" and self.longueur_plateau_effective() > g("dimensions.longueur_plateau"):
            pbs.append(Probleme("alerte", "dimensions.longueur_bassin_epaules",
                                "plateau bassin-epaules plus long que le plateau complet"))
        return pbs

    def erreurs(self):
        return [p for p in self.valider() if p.niveau == "erreur"]

    # -- grandeurs derivees simples -----------------------------------------
    def longueur_plateau_effective(self):
        """Longueur reelle du plateau selon ``dimensions.mode_longueur``."""
        g = self.get
        if g("dimensions.mode_longueur") == "bassin_epaules":
            return g("dimensions.longueur_bassin_epaules") + g("dimensions.marge_bassin") + g("dimensions.marge_epaules")
        return g("dimensions.longueur_plateau")

    # -- persistance ----------------------------------------------------------
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

    # -- export Fusion ----------------------------------------------------------
    @staticmethod
    def nom_fusion(chemin, prefixe="eq_"):
        """'bois.section_noeud' -> 'eq_bois_section_noeud' (nom valide Fusion)."""
        nom = prefixe + re.sub(r"[^A-Za-z0-9_]", "_", chemin.replace(".", "_"))
        if not nom[0].isalpha():
            nom = "p" + nom
        return nom

    UNITES_FUSION = {"mm": "mm", "deg": "deg", "kg": "kg", "": "", "%": "", "N": "N",
                     "MPa": "", "kg/m3": ""}

    def parametres_exportables(self):
        """Liste (nom, expression, unite_fusion, commentaire) des numeriques."""
        prefixe = self.get("gamme.prefixe_fusion", "eq_")
        res = []
        for chemin, meta, val in self.feuilles():
            if isinstance(val, bool) or not isinstance(val, (int, float)):
                continue
            unite = self.UNITES_FUSION.get(meta.unite, "")
            expression = ("%g %s" % (val, unite)).strip()
            commentaire = "%s [%s%s] %s" % (chemin, meta.statut, (" " + meta.unite) if meta.unite else "",
                                            meta.role)
            res.append((self.nom_fusion(chemin, prefixe), expression, unite, commentaire[:250]))
        return res

    def exporter_user_parameters(self, design):
        """Cree ou met a jour les User Parameters de ``design`` (Fusion).

        Fusion convertit lui-meme les expressions '700 mm' en cm internes.
        Renvoie (crees, mis_a_jour).
        """
        import adsk.core  # import differe : uniquement dans Fusion (ou mock)
        crees, maj = [], []
        ups = design.userParameters
        for nom, expression, unite, commentaire in self.parametres_exportables():
            existant = ups.itemByName(nom)
            if existant:
                existant.expression = expression
                existant.comment = commentaire
                maj.append(nom)
            else:
                ups.add(nom, adsk.core.ValueInput.createByString(expression), unite, commentaire)
                crees.append(nom)
        return crees, maj
