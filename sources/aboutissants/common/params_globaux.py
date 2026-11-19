# -*- coding: utf-8 -*-
"""Couche 1 — Paramètres globaux partagés de la gamme Aboutissants.

Accessoires de contention (bracelets, sangles, colliers, manilles, anneaux)
et modules rapportés (premier module : machine de mouvement mécanique),
destinés exclusivement à des adultes consentants.

Chaque feuille du schéma ``SCHEMA`` est un ``Param`` : valeur, unité, plage
admissible, justification, source (chemin de fichier si la cote vient d'un
meuble Equinox / Néogothique / Incognito / Tantra / Rangement). Les cotes de meubles qui n'existent
pas dans les scripts sont à ``None`` avec ``statut="todo"`` — elles ne sont
pas inventées.

Unités internes : mm, kg, deg, N, MPa, % (jamais de cm ici). L'API Fusion
travaille en cm : la conversion est exclusive à ``common.fusion_utils``.

Usage ::

    from common.params_globaux import Parametres
    p = Parametres()
    p.get("interface_oeillet_m8.filetage")   # "M8"
    p.get("mouvement.course")                # 80.0
    p.excentricite()                         # course / 2
    problemes = p.valider()
    p.exporter_user_parameters(design)       # dans Fusion uniquement
"""

from __future__ import annotations

import copy
import math
import os
import re

_MANQUANT = object()

# Accélération de la pesanteur (m/s²), même valeur que Néogothique ``charges.g``.
G = 9.81

# Préfixe des User Parameters Fusion (convention eq_ / neo_ / inc_).
PREFIXE_FUSION_DEFAUT = "abo_"

# Statuts
IMP, VAL, DER, LIB, TODO = "impose", "a_valider", "derive", "libre", "todo"

# Sources (chemins sous /workspace, ne pas modifier ces dépôts).
SRC_EQ_PARAM = "equinox/equinox/parametres.py"
SRC_EQ_DEF = "equinox/equinox/parametres_equinox.defauts.json"
SRC_EQ_ATT = "equinox/equinox/catalogues/attaches.py"
SRC_EQ_ANC = "equinox/equinox/grammaires/ancrages.py"
SRC_EQ_MET = "equinox/equinox/catalogues/metaux.py"
SRC_EQ_TAB = "equinox/equinox/grammaires/tabouret.py"
SRC_EQ_CROIX = "equinox/equinox/grammaires/croix_saint_andre.py"
SRC_EQ_CHAISE = "equinox/equinox/grammaires/chaise_trone.py"
SRC_EQ_BANC = "equinox/equinox/grammaires/banc_flore.py"
SRC_NEO_PARAM = "neogothique/neogothique/parametres.py"
SRC_NEO_ENT = "neogothique/neogothique/grammaires/entrave.py"
SRC_NEO_PTS = "neogothique/docs/points_a_trancher.md"
SRC_INC_PARAM = "incognito/incognito/parametres.py"
SRC_INC_FIX = "incognito/incognito/catalogues/fixations.py"
SRC_INC_BANQ = "incognito/incognito/grammaires/banquette.py"
SRC_INC_DOC = "incognito/docs/parametres.md"
SRC_TAN_PARAM = "tantra/tantra/parametres.py"
SRC_TAN_FIX = "tantra/tantra/catalogues/fixations.py"
SRC_TAN_REG = "tantra/tantra/regles.py"
SRC_TAN_GEO = "tantra/tantra/geometrie.py"
SRC_TAN_SIEGE = "tantra/tantra/grammaires/_siege.py"
SRC_TAN_SALON = "tantra/tantra/grammaires/_salon.py"
SRC_TAN_CHAISE = "tantra/tantra/grammaires/tantra_chaise_double_courbe.py"
SRC_TAN_FAUT = "tantra/tantra/grammaires/tantra_fauteuil_lombaire.py"
SRC_TAN_BANQ = "tantra/tantra/grammaires/tantra_banquette_deux_niveaux.py"
SRC_TAN_GENOUX = "tantra/tantra/grammaires/tantra_siege_repose_genoux.py"
SRC_TAN_CAMO_CAN = "tantra/tantra/grammaires/camo_canape.py"
SRC_TAN_CAMO_FAU = "tantra/tantra/grammaires/camo_fauteuil.py"
SRC_TAN_DESSERTE = "tantra/tantra/grammaires/cadre_desserte_genoux.py"
SRC_TAN_DOC_TABLE = "tantra/docs/cadre_table_inclinee.md"
SRC_RAN_PARAM = "rangement/rangement/parametres.py"
SRC_RAN_QUIN = "rangement/rangement/catalogues/quincaillerie.py"
SRC_RAN_SYS = "rangement/rangement/catalogues/systemes.py"
SRC_RAN_RAT = "rangement/rangement/grammaires/ratelier_mural.py"

# Gammes dont les ancrages sont relevés dans SCHEMA["ancrages"].
GAMMES_ANCRAGES = ("equinox", "neogothique", "incognito", "tantra", "rangement")


class Param(object):
    """Description d'un paramètre (feuille du schéma).

    :param valeur: valeur par défaut, ou ``None`` si la cote est inconnue
        (alors ``statut`` doit être ``todo``).
    :param unite: unité interne (mm, kg, deg, N, MPa, %, texte, bool, liste…).
    :param role: phrase courte (à quoi sert le paramètre).
    :param plage: tuple (mini, maxi) pour les numériques, ou None.
    :param choix: liste des valeurs admises pour les textes, ou None.
    :param statut: impose / a_valider / derive / libre / todo.
    :param utilise_par: modules qui lisent ce paramètre.
    :param justification: pourquoi cette valeur (formule, compromis, hypothese).
    :param source: fichier (et éventuellement identifiant) d'où vient la cote ;
        vide s'il s'agit d'une valeur Aboutissants à valider.
    """

    __slots__ = (
        "valeur", "unite", "role", "plage", "choix", "statut",
        "utilise_par", "justification", "source",
    )

    def __init__(self, valeur, unite, role, plage=None, choix=None,
                 statut="libre", utilise_par=(), justification="", source=""):
        self.valeur = valeur
        self.unite = unite
        self.role = role
        self.plage = plage
        self.choix = choix
        self.statut = statut
        self.utilise_par = tuple(utilise_par)
        self.justification = justification or ""
        self.source = source or ""
        if valeur is None and statut != TODO:
            raise ValueError("Une valeur None exige statut='todo' (%s)." % role)

    def __repr__(self):
        return "Param(%r %s, %s)" % (self.valeur, self.unite, self.statut)


# ---------------------------------------------------------------------------
# SCHEMA
# ---------------------------------------------------------------------------
SCHEMA = {
    "gamme": {
        "nom": Param(
            "Aboutissants", "texte",
            "Nom de la gamme (préfixe des composants Fusion).",
            justification="Gamme d'accessoires et de modules rapportés, distincte des meubles.",
        ),
        "version": Param(
            "0.1.0", "texte", "Version du vocabulaire de paramètres.",
        ),
        "prefixe_fusion": Param(
            PREFIXE_FUSION_DEFAUT, "texte",
            "Préfixe des User Parameters créés dans Fusion.",
            justification="Aligné sur eq_ (Equinox), neo_ (Néogothique), inc_ (Incognito).",
        ),
        "destinataires": Param(
            "adultes_consentants", "texte",
            "Public visé : exclusivement des adultes consentants.",
            choix=["adultes_consentants"], statut=IMP,
            justification="Même cadre que les gammes de meubles (Incognito README, Néogothique Entrave).",
        ),
    },

    # -- Unités / conversion cm Fusion ---------------------------------------
    "unites": {
        "mm_par_cm": Param(
            10.0, "",
            "Facteur de conversion : longueurs internes (mm) vers unités internes Fusion (cm).",
            plage=(10.0, 10.0), statut=IMP, utilise_par=("fusion_utils",),
            justification="L'API Fusion (Point3D, ValueInput.createByReal) exprime les longueurs en cm. "
                          "Les User Parameters s'écrivent en expressions '80 mm' ; Fusion convertit lui-même.",
            source="equinox/equinox/fusion_outils.py (MM_PAR_CM), "
                   "neogothique/neogothique/fusion_outils.py, "
                   "incognito/incognito/fusion_outils.py",
        ),
        "g": Param(
            G, "m/s2",
            "Accélération de la pesanteur utilisée pour convertir kg → N.",
            plage=(9.80, 9.82), statut=LIB, utilise_par=("securite", "mouvement"),
            justification="Identique à charges.g de l'Entrave.",
            source=SRC_NEO_PARAM + " (charges.g = 9.81)",
        ),
    },

    # -- Tolérances ----------------------------------------------------------
    "tolerances": {
        "jeu_fonctionnel": Param(
            0.5, "mm",
            "Jeu fonctionnel général (pièces mobiles d'accessoires, glissières courtes).",
            plage=(0.1, 3.0), statut=VAL, utilise_par=("mouvement", "accessoires"),
            justification="Compromis entre fluidité et ballant. Plus serré que le jeu mécanique "
                          "Incognito (2 mm, charnières/trappes) et que le jeu coulisseau Néogothique "
                          "(1,5 mm, mouvement du bois). À valider sur prototype.",
            source="Ordre de grandeur inspiré de neogothique tolerances.jeu_axes (0,3 mm) "
                   "et incognito jeu_mecanique_mm (2,0 mm) — valeur Aboutissants à valider.",
        ),
        "jeu_axe": Param(
            0.3, "mm",
            "Jeu diamétral axes / alésages des ferrures.",
            plage=(0.1, 1.0), statut=VAL, utilise_par=("mouvement",),
            justification="Repris du jeu d'axes de l'Entrave (dérivé, à valider pour l'inox usiné).",
            source=SRC_NEO_PARAM + " (tolerances.jeu_axes = 0.3 mm)",
        ),
        "jeu_glissiere_bois": Param(
            1.5, "mm",
            "Jeu radial type coulisseau / fourreau bois (retrait hygroscopique + glissement).",
            plage=(0.5, 4.0), statut=VAL,
            justification="Valeur Entrave, inadaptée à un rail métallique de machine (voir jeu_fonctionnel).",
            source=SRC_NEO_PARAM + " (tolerances.jeu_coulisseau = 1.5 mm, a_valider)",
        ),
        "jeu_mortaise": Param(
            0.2, "mm",
            "Jeu d'ajustement tenon / mortaise (jonctions d'ébénisterie).",
            plage=(0.0, 0.6), statut=LIB, utilise_par=("jonctions",),
            justification="Ajustement collé classique, repris de l'Entrave.",
            source=SRC_NEO_PARAM + " (tolerances.jeu_mortaise = 0.2 mm)",
        ),
        "tolerance_usinage": Param(
            0.2, "mm",
            "Tolérance linéaire typique d'usinage (fraisage / tournage, classe moyenne).",
            plage=(0.05, 0.8), statut=VAL,
            justification="Ordre de grandeur ISO 2768-m pour cotes 30–120 mm. À préciser sur plan "
                          "par cote fonctionnelle (alésages H7/g6, etc.).",
        ),
        "tolerance_impression": Param(
            0.3, "mm",
            "Tolérance typique d'impression 3D (FDM technique ou résine, pièces non structurales).",
            plage=(0.1, 1.0), statut=VAL,
            justification="Hypothèse d'atelier : les pièces de structure et de sécurité ne sont pas "
                          "imprimées. Jeu à prévoir en plus du jeu fonctionnel.",
        ),
        "tolerance_fonderie": Param(
            0.8, "mm",
            "Tolérance typique de fonderie / coulée (pièces laiton ou alu coulées, avant usinage).",
            plage=(0.3, 3.0), statut=VAL,
            justification="Ordre de grandeur CT8 / pièces décoratives. Les portées d'axe et les "
                          "plans de bride doivent être repris en usinage.",
        ),
        "jeu_axe_petit_oeil": Param(
            None, "mm",
            "Jeu diamétral de l'axe de bride dans l'œillet bas Equinox (DI 12 mm).",
            statut=TODO, utilise_par=("mouvement",),
            justification="TODO : DI intérieur œillet bas = 12 mm (dérivé du modèle Equinox) ; "
                          "le diamètre d'axe de bride n'est pas coté dans les meubles. À choisir "
                          "pour passer dans l'œil sans forcer, avec bague si besoin.",
            source=SRC_EQ_ANC + " (commentaire : oeil di 12 mm mini pour un mousqueton)",
        ),
    },

    # -- Anthropométrie : RÉFÉRENCES GÉNÉRIQUES À VALIDER --------------------
    "anthropometrie": {
        "avertissement": Param(
            "valeurs_generiques_a_valider", "texte",
            "Toutes les cotes de ce bloc sont des références génériques d'atelier, "
            "à valider par mesurage sur la personne. Elles ne proviennent pas des scripts de meubles.",
            choix=["valeurs_generiques_a_valider"], statut=VAL,
            justification="Les tours S/M/L/XL ci-dessous sont des ordres de grandeur d'adultes "
                          "européens (confection / tablature courante), pas une norme NF ni un "
                          "relevé clinique. Une manille doit être réglable et ne jamais être "
                          "dimensionnée sur la seule taille affichée.",
        ),
        "poignet_tour_S": Param(
            150.0, "mm", "Tour de poignet taille S (référence générique à valider).",
            plage=(130.0, 165.0), statut=VAL, utilise_par=("bracelets",),
            justification="Référence générique adulte, pas une cote de meuble.",
        ),
        "poignet_tour_M": Param(
            170.0, "mm", "Tour de poignet taille M (référence générique à valider).",
            plage=(155.0, 185.0), statut=VAL, utilise_par=("bracelets",),
            justification="Référence générique adulte, pas une cote de meuble.",
        ),
        "poignet_tour_L": Param(
            190.0, "mm", "Tour de poignet taille L (référence générique à valider).",
            plage=(175.0, 205.0), statut=VAL, utilise_par=("bracelets",),
            justification="Référence générique adulte, pas une cote de meuble.",
        ),
        "poignet_tour_XL": Param(
            210.0, "mm", "Tour de poignet taille XL (référence générique à valider).",
            plage=(195.0, 240.0), statut=VAL, utilise_par=("bracelets",),
            justification="Référence générique adulte, pas une cote de meuble.",
        ),
        "cheville_tour_S": Param(
            200.0, "mm", "Tour de cheville taille S (référence générique à valider).",
            plage=(170.0, 215.0), statut=VAL,
            justification="Référence générique adulte, pas une cote de meuble.",
        ),
        "cheville_tour_M": Param(
            220.0, "mm", "Tour de cheville taille M (référence générique à valider).",
            plage=(205.0, 240.0), statut=VAL,
            justification="Référence générique adulte, pas une cote de meuble.",
        ),
        "cheville_tour_L": Param(
            245.0, "mm", "Tour de cheville taille L (référence générique à valider).",
            plage=(225.0, 265.0), statut=VAL,
            justification="Référence générique adulte, pas une cote de meuble.",
        ),
        "cheville_tour_XL": Param(
            270.0, "mm", "Tour de cheville taille XL (référence générique à valider).",
            plage=(250.0, 310.0), statut=VAL,
            justification="Référence générique adulte, pas une cote de meuble.",
        ),
        "cou_tour_S": Param(
            330.0, "mm", "Tour de cou taille S (référence générique à valider).",
            plage=(300.0, 355.0), statut=VAL, utilise_par=("colliers",),
            justification="Référence générique adulte, pas une cote de meuble.",
        ),
        "cou_tour_M": Param(
            370.0, "mm", "Tour de cou taille M (référence générique à valider).",
            plage=(345.0, 395.0), statut=VAL, utilise_par=("colliers",),
            justification="Référence générique adulte, pas une cote de meuble.",
        ),
        "cou_tour_L": Param(
            410.0, "mm", "Tour de cou taille L (référence générique à valider).",
            plage=(385.0, 435.0), statut=VAL, utilise_par=("colliers",),
            justification="Référence générique adulte, pas une cote de meuble.",
        ),
        "cou_tour_XL": Param(
            450.0, "mm", "Tour de cou taille XL (référence générique à valider).",
            plage=(425.0, 500.0), statut=VAL, utilise_par=("colliers",),
            justification="Référence générique adulte, pas une cote de meuble.",
        ),
        "cuisse_tour_S": Param(
            480.0, "mm", "Tour de cuisse (mi-cuisse) taille S (référence générique à valider).",
            plage=(400.0, 520.0), statut=VAL,
            justification="Grande variabilité individuelle : toujours mesurer. Référence générique, pas une cote de meuble.",
        ),
        "cuisse_tour_M": Param(
            540.0, "mm", "Tour de cuisse (mi-cuisse) taille M (référence générique à valider).",
            plage=(500.0, 590.0), statut=VAL,
            justification="Référence générique adulte, pas une cote de meuble.",
        ),
        "cuisse_tour_L": Param(
            600.0, "mm", "Tour de cuisse (mi-cuisse) taille L (référence générique à valider).",
            plage=(560.0, 650.0), statut=VAL,
            justification="Référence générique adulte, pas une cote de meuble.",
        ),
        "cuisse_tour_XL": Param(
            680.0, "mm", "Tour de cuisse (mi-cuisse) taille XL (référence générique à valider).",
            plage=(630.0, 800.0), statut=VAL,
            justification="Référence générique adulte, pas une cote de meuble.",
        ),
        "jeu_circonference_manille": Param(
            20.0, "mm",
            "Surplus de circonférence intérieure d'une manille par rapport au tour anatomique "
            "(réglage + confort, hors épaisseur de cuir).",
            plage=(5.0, 50.0), statut=VAL,
            justification="Hypothèse Aboutissants à valider. Ne pas caler une manille de cou au plus juste.",
        ),
        # Précédents meubles (manilles Entrave) — ce ne sont PAS des tours anatomiques.
        "neo_diametre_int_cou": Param(
            130.0, "mm",
            "Diamètre intérieur nominal de la manille de cou de l'Entrave Néogothique "
            "(réglable par boucle ±15 mm). Ce n'est pas un tour anatomique.",
            plage=(100.0, 170.0), statut=VAL, utilise_par=("colliers",),
            justification="Précédent meuble, à ajuster aux mensurations. Tour approximatif = π × DI ≈ 408 mm "
                          "(autour d'un L générique), plus le réglage boucle.",
            source=SRC_NEO_PARAM + " (garnissage.diametre_int_cou, a_valider)",
        ),
        "neo_diametre_int_poignet": Param(
            75.0, "mm",
            "Diamètre intérieur nominal des manilles de poignets de l'Entrave. Ce n'est pas un tour anatomique.",
            plage=(55.0, 100.0), statut=VAL, utilise_par=("bracelets",),
            justification="Précédent meuble. Tour intérieur ≈ π × 75 ≈ 236 mm, largement au-dessus d'un "
                          "poignet M (170 mm) : place pour le cuir (6,5 mm) et le confort.",
            source=SRC_NEO_PARAM + " (garnissage.diametre_int_poignet, a_valider)",
        ),
        "neo_reglage_boucle": Param(
            15.0, "mm",
            "Demi-plage de réglage par boucle des manilles de l'Entrave (sur le diamètre intérieur).",
            plage=(5.0, 40.0), statut=VAL,
            justification="Texte du paramètre Néogothique : « réglable par boucle ±15 mm ».",
            source=SRC_NEO_PARAM + " (garnissage.diametre_int_cou, rôle)",
        ),
    },

    # -- Sangles -------------------------------------------------------------
    "sangles": {
        "largeurs_standard": Param(
            [15.0, 20.0, 25.0, 38.0, 50.0], "liste_mm",
            "Largeurs commerciales typiques de sangle (polyester / nylon).",
            statut=VAL, utilise_par=("sangles",),
            justification="Série courante du commerce (15/20/25/38/50 mm). Référence générique à "
                          "valider selon le fabricant et la CMU de la sangle. Pas issu des meubles.",
        ),
        "largeur_poignet": Param(
            25.0, "mm", "Largeur de sangle proposée pour un bracelet de poignet.",
            plage=(15.0, 50.0), statut=VAL,
            justification="25 mm répartit mieux la pression qu'une 15 mm, tout en restant discrète. À valider.",
        ),
        "largeur_cheville": Param(
            25.0, "mm", "Largeur de sangle proposée pour une cheville.",
            plage=(15.0, 50.0), statut=VAL,
            justification="Même série que le poignet, à valider.",
        ),
        "largeur_cuisse": Param(
            50.0, "mm", "Largeur de sangle proposée pour une cuisse.",
            plage=(25.0, 80.0), statut=VAL,
            justification="Largeur supérieure pour limiter la pression locale. Référence générique à valider.",
        ),
        "largeur_corps": Param(
            50.0, "mm", "Largeur de sangle proposée pour un sanglage de buste ou de bassin.",
            plage=(38.0, 80.0), statut=VAL,
            justification="Référence générique à valider ; CMU fabricant obligatoire.",
        ),
        "epaisseur_sangle": Param(
            1.5, "mm", "Épaisseur typique d'une sangle polyester tissée.",
            plage=(1.0, 4.0), statut=VAL,
            justification="Ordre de grandeur commerce. Les sangles de levage sont plus épaisses. À valider sur fiche fabricant.",
        ),
        "neo_largeur_manille_cou": Param(
            60.0, "mm", "Largeur de bande de la manille de cou de l'Entrave (cuir, pas sangle).",
            plage=(40.0, 90.0), statut=DER,
            justification="Précédent cuir Néogothique, distinct d'une sangle tissée.",
            source=SRC_NEO_PARAM + " (garnissage.largeur_manille_cou)",
        ),
        "neo_largeur_manille_poignet": Param(
            50.0, "mm", "Largeur de bande des manilles de poignets de l'Entrave (cuir, pas sangle).",
            plage=(35.0, 80.0), statut=DER,
            justification="Précédent cuir Néogothique.",
            source=SRC_NEO_PARAM + " (garnissage.largeur_manille_poignet)",
        ),
    },

    # -- Confort / contact peau ----------------------------------------------
    "confort": {
        "rayon_min_arete_peau": Param(
            3.0, "mm",
            "Rayon minimal des tranches et arêtes en contact avec la peau.",
            plage=(1.0, 10.0), statut=LIB, utilise_par=("accessoires", "mouvement"),
            justification="Repris de l'Entrave (securite.arrondi_contact_peau). Pour les pièces "
                          "porteuses ou longuement appliquées, viser plutôt 5 mm (confort).",
            source=SRC_NEO_PARAM + " (securite.arrondi_contact_peau = 3 mm)",
        ),
        "rayon_recommande_arete_peau": Param(
            5.0, "mm",
            "Rayon recommandé des arêtes longuement en contact peau (manilles, poignées, tige).",
            plage=(3.0, 15.0), statut=VAL,
            justification="Marge de confort au-dessus du minimum Néogothique de 3 mm. À valider au prototype.",
        ),
    },
}


# Complément du schéma : sécurité, interface M8, ancrages par gamme, mouvement.
SCHEMA.update({
    "securite": {
        "charge_utilisateur": Param(
            120.0, "kg",
            "Masse de l'utilisateur prise en compte (dimensionnement des ancrages et du châssis).",
            plage=(40.0, 200.0), statut=IMP, utilise_par=("securite", "mouvement"),
            justification="Valeur imposée Equinox, reprise comme hypothèse de gamme pour les accessoires. "
                          "Ne remplace pas un essai de charge réel.",
            source=SRC_EQ_PARAM + " (securite.charge_utilisateur = 120 kg, impose)",
        ),
        "coefficient_dynamique": Param(
            2.0, "",
            "Majoration des efforts (mouvements, impacts, à-coups). Conservateur vis-à-vis de l'Entrave (1,5).",
            plage=(1.0, 4.0), statut=VAL, utilise_par=("securite", "mouvement"),
            justification="Reprise d'Equinox (a_valider). Pour une machine cyclique, la fatigue peut "
                          "exiger une majoration ou une vérification spécifique (à traiter en note de calcul). "
                          "Néogothique utilise 1,5 ; Incognito n'a pas de coef dynamique séparé (CS 3 forfaitaire).",
            source=SRC_EQ_PARAM + " (securite.coefficient_dynamique = 2.0, a_valider)",
        ),
        "coefficient_dynamique_neo": Param(
            1.5, "",
            "Coefficient dynamique documenté pour l'Entrave Néogothique (référence, non utilisé par défaut).",
            plage=(1.0, 3.0), statut=LIB,
            justification="Documenté pour comparaison, pas pour dimensionner les Aboutissants.",
            source=SRC_NEO_PARAM + " (charges.coef_dynamique = 1.5)",
        ),
        "coefficient_bois": Param(
            3.0, "",
            "Coefficient de sécurité sur la résistance en flexion du bois (MOR), Equinox.",
            plage=(1.5, 6.0), statut=VAL,
            justification="Reprise Equinox. Incognito utilise aussi CS ≥ 3 sur les ancrages (minimum recommandé).",
            source=SRC_EQ_PARAM + " (securite.securite_bois = 3.0) ; "
                   "incognito/incognito/parametres.py (COEFFICIENT_SECURITE_MIN_RECOMMANDE = 3)",
        ),
        "coefficient_metal": Param(
            1.8, "",
            "Coefficient de sécurité Equinox sur la limite élastique des métaux de structure.",
            plage=(1.2, 4.0), statut=VAL,
            justification="Reprise Equinox pour les pièces de structure. Pour les ancrages de retenue "
                          "de personne, appliquer plutôt coefficient_ancrage (≥ 3 recommandé, Incognito).",
            source=SRC_EQ_PARAM + " (securite.securite_metal = 1.8, a_valider)",
        ),
        "coefficient_ancrage": Param(
            3.0, "",
            "Coefficient de sécurité recommandé sur la charge de service d'un point d'ancrage de retenue.",
            plage=(1.5, 8.0), statut=VAL, utilise_par=("ancrages", "mouvement"),
            justification="Minimum recommandé Incognito. Un CS < 3 y est signalé non conforme. "
                          "À conserver pour tout accessoire accroché à un œillet / insert.",
            source=SRC_INC_PARAM + " (COEFFICIENT_SECURITE_MIN_RECOMMANDE = 3.0)",
        ),
        "coefficient_cuir": Param(
            4.0, "",
            "Coefficient de sécurité sur la traction du cuir / de l'âme (Entrave).",
            plage=(2.0, 8.0), statut=LIB, utilise_par=("accessoires",),
            justification="Reprise Néogothique (charges.gamma_cuir).",
            source=SRC_NEO_PARAM + " (charges.gamma_cuir = 4)",
        ),
        "coefficient_renversement": Param(
            1.5, "",
            "Rapport minimal moment stabilisant / moment renversant (Equinox).",
            plage=(1.0, 3.0), statut=VAL, utilise_par=("mouvement",),
            justification="Reprise Equinox. Le châssis de la machine doit rester stable même si "
                          "l'œillet de meuble n'est pas sollicité en traction (bride desserrée).",
            source=SRC_EQ_PARAM + " (securite.securite_renversement = 1.5, a_valider)",
        ),
        "effort_retenue_formule": Param(
            "F = k_dyn × 0,5 × m × g", "texte",
            "Formule Equinox d'effort de calcul sur un point de retenue.",
            statut=LIB,
            justification="Hypothèse Equinox (un membre qui tire violemment sur un seul point), à valider. "
                          "Avec les défauts : F = 2.0 × 0.5 × 120 × 9.81 = 1177 N.",
            source=SRC_EQ_ANC + " (effort_retenue)",
        ),
        # Charges de service documentées par gamme (référence, pas inventées).
        "eq_cmu_oeillet": Param(
            2000.0, "N",
            "Capacité de service catalogue de l'œillet inox A4 fil 8 mm (Equinox).",
            plage=(200.0, 10000.0), statut=VAL,
            justification="CMU catalogue Equinox, à remplacer par la CMU marquée du fabricant. "
                          "Ne jamais utiliser de piton vissé dans le bois de bout comme point de retenue.",
            source=SRC_EQ_ATT + " (oeillet_inox_8.capacite_service = 2000 N)",
        ),
        "eq_cmu_anneau": Param(
            2500.0, "N",
            "Capacité de service catalogue de l'anneau inox A4 fil 8 mm, DI 40 (Equinox).",
            plage=(200.0, 10000.0), statut=VAL,
            justification="CMU catalogue Equinox, à confirmer fabricant.",
            source=SRC_EQ_ATT + " (anneau_inox_8.capacite_service = 2500 N)",
        ),
        "eq_cmu_insert_m8": Param(
            2500.0, "N",
            "Capacité de service catalogue de l'insert fileté inox M8 (type Ensat) dans le bois Equinox.",
            plage=(200.0, 10000.0), statut=VAL,
            justification="Valeur indicative du catalogue Equinox (densité ≥ 650 kg/m³, longueur 20 mm). À valider.",
            source=SRC_EQ_ATT + " (insert_filete_m8.capacite_service = 2500 N)",
        ),
        "neo_capacite_point": Param(
            2000.0, "N",
            "Effort admissible par point d'ancrage au sol de l'Entrave (cheville + anneau).",
            plage=(200.0, 10000.0), statut=LIB,
            justification="Paramètre Néogothique. Environ 300 N par anneau en pointe selon points_a_trancher.md.",
            source=SRC_NEO_PARAM + " (ancrage.capacite_point = 2000 N)",
        ),
        "neo_traction_manille": Param(
            500.0, "N",
            "Traction latérale de vérification sur une manille de l'Entrave.",
            plage=(100.0, 3000.0), statut=VAL,
            justification="Hypothèse Entrave à valider. Avec coef 1,5, l'Entrave bascule à vide sans ancrage au sol.",
            source=SRC_NEO_PARAM + " (charges.traction_manille = 500 N, a_valider)",
        ),
        "neo_verticale_service": Param(
            1500.0, "N",
            "Charge verticale de service sur la platine de l'Entrave.",
            plage=(300.0, 4000.0), statut=VAL,
            justification="Hypothèse Entrave à valider.",
            source=SRC_NEO_PARAM + " (charges.verticale_service = 1500 N, a_valider)",
        ),
        "inc_charge_service_ancrage": Param(
            1500.0, "N",
            "Charge de service par point d'ancrage Incognito (hypothèse : adulte, traction).",
            plage=(300.0, 4000.0), statut=VAL,
            justification="Cible de conception Incognito, essai réel obligatoire. Rupture visée = 1500 × 3 = 4500 N.",
            source=SRC_INC_PARAM + " (ParametresCharge.charge_service_ancrage_n = 1500 N)",
        ),
        "inc_charge_rupture_visee": Param(
            4500.0, "N",
            "Charge de rupture visée par ancrage Incognito (service × CS).",
            plage=(900.0, 20000.0), statut=DER,
            justification="1500 N × 3. Cible, non certifiée.",
            source=SRC_INC_PARAM + " (charge_rupture_visee_ancrage_n)",
        ),
        "charge_service_poussee_machine": Param(
            400.0, "N",
            "Charge de service nominale de poussée / traction de la tige de la machine de mouvement.",
            plage=(50.0, 1500.0), statut=IMP, utilise_par=("mouvement", "interfaces", "cadres"),
            justification="Poussée nominale VALIDÉE à 400 N (décision Fabien). Effort dynamique : "
                          "400 × k_dyn 2 = 800 N. Effort de calcul d'ancrage : 800 × CS 3 = 2400 N. "
                          "La machine n'est pas dimensionnée pour porter le poids du corps (120 kg), "
                          "mais pour cette poussée cyclique. Ce n'est pas une CMU certifiée : un essai "
                          "de qualification reste obligatoire. Ne pas dépasser la CMU du point d'ancrage "
                          "meuble si la bride reprend cet effort.",
        ),
    },

    # -- Interface d'ancrage normalisée œillet / filetage M8 -----------------
    "interface_oeillet_m8": {
        "filetage": Param(
            "M8", "texte",
            "Filetage normalisé de l'interface d'accroche Aboutissants (brides, tiges, inserts côté accessoire).",
            choix=["M6", "M8", "M10"], statut=VAL, utilise_par=("mouvement", "accessoires"),
            justification="Identique au filetage des inserts Equinox (pivots, glissières, ancrages). "
                          "Ce n'est PAS le filetage des ancrages Incognito (non documenté) ni des plaques "
                          "Néogothique (non documenté).",
            source=SRC_EQ_PARAM + " (jonctions.filetage_insert = M8, choix M6/M8/M10, a_valider)",
        ),
        "pas": Param(
            1.25, "mm",
            "Pas gros ISO du filetage M8.",
            plage=(0.75, 1.25), statut=LIB,
            justification="Pas gros normalisé ISO 261 / ISO 724 pour M8. Non coté dans les scripts de meubles, "
                          "valeur de norme (pas une cote inventée de meuble).",
            source="ISO 261 / ISO 724 (pas gros M8 = 1,25 mm)",
        ),
        "section_resistante": Param(
            36.6, "mm2",
            "Section résistante As d'une vis M8 (pas gros).",
            plage=(36.0, 37.0), statut=LIB,
            justification="Valeur tabulaire ISO 898-1 / ISO 3506 pour M8×1,25. Sert aux hypothèses de "
                          "charge admissible (voir catalogues.visserie).",
            source="ISO 898-1 / ISO 3506 (As M8 = 36,6 mm²)",
        ),
        "longueur_insert_equinox": Param(
            20.0, "mm",
            "Longueur des inserts filetés M8 Equinox (dérivée de la densité du bois, défaut 20 mm).",
            plage=(10.0, 40.0), statut=DER,
            justification="20 mm si densité ≥ 650 kg/m³, 25 mm en dessous (catalogue Equinox).",
            source=SRC_EQ_PARAM + " (jonctions.longueur_insert = 20 mm, derive) ; " + SRC_EQ_ATT,
        ),
        "vis_platine_oeillet": Param(
            "4 x vis inox A4 d4", "texte",
            "Visserie de la platine d'œillet bas Equinox (dans la jonction du module ancrages).",
            statut=LIB,
            justification="Documenté dans la grammaire d'ancrages Equinox, pas un diamètre M8 : les vis de "
                          "platine sont en Ø4, l'insert axial est M8.",
            source=SRC_EQ_ANC + " (vis_platine : 4 x vis inox A4 d4 ; insert = filetage_insert)",
        ),
        "percage_tube_anneau": Param(
            9.0, "mm",
            "Perçage du tube 40×40 pour la tige M8 traversante de l'anneau arrière Equinox.",
            plage=(8.0, 12.0), statut=LIB,
            justification="Jeu de passage d'une tige M8 (Ø nom. 8) : trou Ø9 + manchon entretoise Ø12 soudé.",
            source=SRC_EQ_ANC + " (percage_tube : d 9 à travers les 2 parois ; manchon entretoise d 12 soude)",
        ),
        "manchon_entretoise": Param(
            12.0, "mm",
            "Diamètre du manchon entretoise soudé dans le tube 40×40 (anneau arrière Equinox).",
            plage=(10.0, 20.0), statut=LIB,
            source=SRC_EQ_ANC + " (manchon entretoise d 12 soude)",
        ),
        "jeu_fixation_bride": Param(
            0.5, "mm",
            "Jeu de montage de la bride / clamp sur l'œillet (sans usiner le meuble).",
            plage=(0.1, 3.0), statut=VAL, utilise_par=("mouvement",),
            justification="La bride doit enserrer l'œil ou passer un axe dans l'œil existant, sans percage "
                          "ni modification de la structure visible du meuble. Valeur Aboutissants à valider.",
        ),
    },
})


SCHEMA.update({
    # -- Interfaces d'ancrage déduites des scripts, par gamme ----------------
    # Règle : n'inventer aucune cote de meuble. None + todo si absent.
    "ancrages": {
        "equinox": {
            "filetage_insert": Param(
                "M8", "texte", "Filetage des inserts / taraudages Equinox (pivots, glissières, ancrages).",
                choix=["M6", "M8", "M10"], statut=VAL,
                source=SRC_EQ_PARAM + " (jonctions.filetage_insert)",
            ),
            "longueur_insert": Param(
                20.0, "mm", "Longueur des inserts filetés Equinox.",
                plage=(10.0, 40.0), statut=DER,
                source=SRC_EQ_PARAM + " (jonctions.longueur_insert)",
            ),
            "diametre_fil_oeillet": Param(
                8.0, "mm", "Diamètre du fil des œillets et anneaux d'ancrage Equinox.",
                plage=(5.0, 16.0), statut=IMP,
                source=SRC_EQ_PARAM + " (inox.diametre_oeillet, impose)",
            ),
            "epaisseur_platine": Param(
                2.0, "mm", "Épaisseur des plaques inox (platines, semelles d'œillet) Equinox.",
                plage=(1.5, 6.0), statut=IMP,
                source=SRC_EQ_PARAM + " (inox.epaisseur_plaque, impose)",
            ),
            "diametre_interieur_anneau": Param(
                40.0, "mm", "Diamètre intérieur de l'anneau arrière Equinox (pontet + tige M8 traversante).",
                plage=(20.0, 80.0), statut=VAL,
                source=SRC_EQ_PARAM + " (ancrage.diametre_interieur_anneau, a_valider)",
            ),
            "diametre_interieur_oeillet_bas": Param(
                12.0, "mm",
                "Diamètre intérieur de l'œil des œillets bas Equinox (modèle : r_oeil = fil/2 + 6).",
                plage=(10.0, 20.0), statut=LIB,
                justification="Dans ancrages.py : r_oeil = fil/2 + 6, commentaire « oeil di 12 mm mini "
                              "pour un mousqueton ». DI = 2 × (r_oeil − fil/2) = 12 mm. Ce n'est pas un "
                              "Param du schéma Equinox, c'est une cote codée dans la grammaire.",
                source=SRC_EQ_ANC + " (r_oeil = fil/2 + 6 ; commentaire di 12 mm)",
            ),
            "saillie_oeillet": Param(
                18.0, "mm", "Saillie de l'œil hors de l'empreinte du pied (accessible).",
                plage=(8.0, 40.0), statut=VAL,
                source=SRC_EQ_PARAM + " (ancrage.saillie_oeillet, a_valider)",
            ),
            "profondeur_encastrement": Param(
                10.0, "mm", "Profondeur de la feuillure sous semelle recevant la platine d'œillet.",
                plage=(3.0, 25.0), statut=VAL,
                source=SRC_EQ_PARAM + " (ancrage.profondeur_encastrement, a_valider)",
            ),
            "position_anneau": Param(
                "mi_hauteur_traverse", "texte", "Position de l'anneau arrière (banc / cheval d'arçon).",
                choix=["mi_hauteur_traverse"], statut=IMP,
                source=SRC_EQ_PARAM + " (ancrage.position_anneau, impose)",
            ),
            "hauteur_axe_traverse": Param(
                130.0, "mm",
                "Hauteur de l'axe de la traverse arrière au sol (banc Flore / cheval d'arçon). "
                "L'anneau est à mi-hauteur de la face de cette traverse.",
                plage=(60.0, 400.0), statut=VAL,
                justification="Cote de la traverse, pas une cote d'anneau nommée. Mi-hauteur ≈ 130 mm "
                              "si l'axe de la traverse est à 130 mm (tube 40×40).",
                source=SRC_EQ_PARAM + " (traverse.hauteur_axe = 130 mm, a_valider, typologies banc_flore / cheval_arcon)",
            ),
            "cote_tube_traverse": Param(
                40.0, "mm", "Côté du tube carré inox de la traverse lestée Equinox.",
                plage=(20.0, 80.0), statut=IMP,
                source=SRC_EQ_PARAM + " (traverse.cote_tube = 40 mm, impose)",
            ),
            "attache_oeillet": Param(
                "oeillet_inox_8", "texte", "Clé catalogue de l'œillet Equinox.",
                statut=VAL, source=SRC_EQ_PARAM + " / " + SRC_EQ_ATT,
            ),
            "attache_anneau": Param(
                "anneau_inox_8", "texte", "Clé catalogue de l'anneau Equinox.",
                statut=VAL, source=SRC_EQ_PARAM + " / " + SRC_EQ_ATT,
            ),
            "cmu_oeillet": Param(
                2000.0, "N", "CMU catalogue œillet Equinox (à confirmer fabricant).",
                plage=(200.0, 10000.0), statut=VAL, source=SRC_EQ_ATT,
            ),
            "cmu_anneau": Param(
                2500.0, "N", "CMU catalogue anneau Equinox (à confirmer fabricant).",
                plage=(200.0, 10000.0), statut=VAL, source=SRC_EQ_ATT,
            ),
            "nuance_inox": Param(
                "inox_316", "texte", "Nuance inox des ancrages Equinox (clé catalogues.metaux).",
                statut=VAL, source=SRC_EQ_PARAM + " (inox.nuance)",
            ),
            "tabouret_hauteur_ceinture": Param(
                160.0, "mm",
                "Hauteur de la ceinture basse du tabouret Equinox, portant quatre anneaux de retenue.",
                plage=(80.0, 300.0), statut=VAL,
                source=SRC_EQ_TAB + " / " + SRC_EQ_PARAM + " (tabouret.hauteur_ceinture, a_valider)",
            ),
            "chaise_hauteur_accoudoirs": Param(
                670.0, "mm",
                "Hauteur des accoudoirs de la chaise/trône au sol (anneaux de poignets aux bouts).",
                plage=(550.0, 800.0), statut=VAL,
                source="equinox/docs/parametres.md (chaise.hauteur_accoudoirs) ; " + SRC_EQ_CHAISE,
            ),
            "diametre_piton": Param(
                None, "mm",
                "Diamètre d'un piton visse Equinox — non utilisé : les scripts l'interdisent.",
                statut=TODO,
                justification="TODO : pas de cote de piton dans Equinox. Le catalogue attache interdit "
                              "explicitement le piton vissé dans le bois de bout comme point de retenue.",
                source=SRC_EQ_ATT + " (commentaire d'en-tête)",
            ),
            "filetage_piton": Param(
                None, "texte", "Filetage d'un piton Equinox — inexistant dans les scripts.",
                statut=TODO,
                justification="TODO : aucun piton coté. Accroche uniquement par œillet / anneau / insert M8.",
                source=SRC_EQ_ATT,
            ),
        },
        "neogothique": {
            "anneaux_sol": Param(
                True, "bool", "Anneaux d'ancrage au sol encastrés sous les semelles de l'Entrave.",
                statut=VAL,
                justification="Ancrage au sol recommandé obligatoire pour la stabilité (basculement à vide).",
                source=SRC_NEO_PARAM + " (ancrage.anneaux_sol, a_valider) ; " + SRC_NEO_PTS,
            ),
            "capacite_point": Param(
                2000.0, "N", "Effort admissible par point d'ancrage (cheville + anneau).",
                plage=(200.0, 10000.0), statut=LIB,
                source=SRC_NEO_PARAM + " (ancrage.capacite_point = 2000 N)",
            ),
            "plaque_cote": Param(
                40.0, "mm",
                "Côté de la plaque d'ancrage au sol modélisée (carré 40×40).",
                plage=(20.0, 80.0), statut=LIB,
                justification="Cote codée dans la grammaire (solide plaque_ancrage_sol), pas un Param du schéma.",
                source=SRC_NEO_ENT + " (rectangle(40, 40), hauteur extrusion 6 mm)",
            ),
            "plaque_epaisseur": Param(
                6.0, "mm", "Épaisseur de la plaque d'ancrage au sol de l'Entrave.",
                plage=(3.0, 16.0), statut=LIB,
                source=SRC_NEO_ENT + " (extrusion 6.0 mm, centre z=3.0)",
            ),
            "decalage_y_bout_semelle": Param(
                45.0, "mm",
                "Recul du centre de plaque depuis le bout de semelle : y = ±(Ls/2 − 45 mm).",
                plage=(10.0, 100.0), statut=LIB,
                justification="Avec Ls = 560 mm (défaut), y = ±235 mm. x = ±x_pied, x_pied = L/2 − retrait_bord − cote/2 "
                              "= 400 − 30 − 55 = 315 mm (platine 800, pied 110, retrait 30).",
                source=SRC_NEO_ENT + " (sy * (Ls/2 - 45.0) ; x = sx * x_pied)",
            ),
            "x_pied_defaut": Param(
                315.0, "mm",
                "Abscisse du centre de pied / plaque, typologie Entrave défauts (L=800, retrait=30, cote=110).",
                plage=(100.0, 500.0), statut=DER,
                justification="Formule de la grammaire : x_pied = L/2 − retrait_bord − cote/2. "
                              "Recalculer si les paramètres d'Entrave changent.",
                source=SRC_NEO_ENT + " (_cotes : x_pied = L/2 - retrait_bord - a/2)",
            ),
            "nombre_points": Param(
                4, "", "Nombre de plaques d'ancrage au sol (2 semelles × 2 bouts) si anneaux_sol est vrai.",
                plage=(2, 8), statut=LIB,
                source=SRC_NEO_ENT + " (boucle cotes_x × cotes_y)",
            ),
            "filetage": Param(
                None, "texte",
                "Filetage de la cheville / de l'anneau d'ancrage au sol Néogothique.",
                statut=TODO,
                justification="TODO : le rôle du paramètre parle de « cheville + anneau » mais aucun filetage "
                              "(M8 ou autre), aucun diamètre d'œil, aucun type de cheville n'est coté dans "
                              "parametres.py ni dans la grammaire (seule une plaque 40×40×6 est solidifiée). "
                              "Ne pas présumer une interface M8 compatible Equinox.",
                source=SRC_NEO_PARAM + " (ancrage.*) ; " + SRC_NEO_ENT + " (plaque_ancrage_sol)",
            ),
            "diametre_fil": Param(
                None, "mm", "Diamètre du fil de l'anneau au sol Néogothique.",
                statut=TODO,
                justification="TODO : non coté dans les scripts. La géométrie s'arrête à une plaque 40×40×6 mm.",
                source=SRC_NEO_ENT,
            ),
            "diametre_interieur_anneau": Param(
                None, "mm", "Diamètre intérieur de l'anneau au sol Néogothique.",
                statut=TODO,
                justification="TODO : non coté dans les scripts. Impossible de garantir le passage d'un axe de bride.",
                source=SRC_NEO_ENT,
            ),
            "diametre_cheville": Param(
                None, "mm", "Diamètre de la cheville d'ancrage au sol Néogothique.",
                statut=TODO,
                justification="TODO : mention « cheville + anneau » sans cote.",
                source=SRC_NEO_PARAM + " (ancrage.capacite_point, rôle)",
            ),
            "charge": Param(
                2000.0, "N", "Alias de capacite_point (effort admissible par point).",
                plage=(200.0, 10000.0), statut=LIB,
                source=SRC_NEO_PARAM,
            ),
        },
        "incognito": {
            "nombre_points_banquette": Param(
                4, "",
                "Nombre d'ancrages de la banquette (près des quatre coins du panneau d'appui).",
                plage=(2, 8), statut=LIB,
                source=SRC_INC_BANQ + " (nombre_ancrages = 4) ; incognito/docs/banquette.md",
            ),
            "diametre_insert": Param(
                12.0, "mm",
                "Diamètre de l'insert métallique noyé (bloc d'ancrage local Incognito).",
                plage=(6.0, 20.0), statut=LIB,
                justification="Cote d'un cylindre / insert Ø12, PAS un filetage documenté. Ne pas l'assimiler à du M8 "
                              "(M8 = Ø nom. 8) ni à du M12 sans confirmation.",
                source=SRC_INC_PARAM + " (GeometrieAncre.diametre_insert_mm = 12) ; " + SRC_INC_FIX,
            ),
            "longueur_encastrement": Param(
                80.0, "mm", "Longueur d'encastrement de l'insert dans le bloc.",
                plage=(20.0, 200.0), statut=LIB,
                source=SRC_INC_PARAM + " (GeometrieAncre.longueur_encastrement_mm = 80)",
            ),
            "epaisseur_bloc": Param(
                54.0, "mm", "Épaisseur du bloc d'ancrage local par défaut (avant recalage).",
                plage=(20.0, 120.0), statut=LIB,
                source=SRC_INC_PARAM + " (GeometrieAncre.epaisseur_bloc_mm = 54)",
            ),
            "largeur_bloc": Param(
                70.0, "mm", "Largeur du bloc d'ancrage local par défaut.",
                plage=(40.0, 200.0), statut=LIB,
                source=SRC_INC_PARAM + " (GeometrieAncre.largeur_bloc_mm = 70)",
            ),
            "longueur_bloc": Param(
                80.0, "mm", "Longueur du bloc d'ancrage local par défaut.",
                plage=(40.0, 200.0), statut=LIB,
                source=SRC_INC_PARAM + " (GeometrieAncre.longueur_bloc_mm = 80)",
            ),
            "recouvrement": Param(
                10.0, "mm", "Épaisseur du cache / retrait de discrétion au-dessus de l'ancre.",
                plage=(0.0, 30.0), statut=LIB,
                justification="Le cache n'est en général pas compté dans la section résistante.",
                source=SRC_INC_PARAM + " (epaisseur_recouvrement_mm = 10 ; retrait_min_ancre_sous_surface_mm = 10)",
            ),
            "distance_au_bord": Param(
                30.0, "mm", "Distance au bord du bloc par défaut (anti-fendage).",
                plage=(10.0, 80.0), statut=LIB,
                justification="Règle Incognito : bord mini = max(25 mm, 2 × Ø insert). Défaut 30 mm pour Ø12.",
                source=SRC_INC_PARAM + " (distance_au_bord_mm = 30 ; formule max(25, 2Ø))",
            ),
            "inset_x_min": Param(
                40.0, "mm",
                "Inset longitudinal minimal des blocs sur le panneau d'appui (max(distance_au_bord, 40)).",
                plage=(20.0, 150.0), statut=LIB,
                source=SRC_INC_BANQ + " (inset_x = max(bloc.distance_au_bord_mm, 40.0))",
            ),
            "charge_service": Param(
                1500.0, "N", "Charge de service par ancrage Incognito.",
                plage=(300.0, 4000.0), statut=VAL,
                source=SRC_INC_PARAM,
            ),
            "coefficient_securite": Param(
                3.0, "", "CS recommandé Incognito (minimum).",
                plage=(1.5, 8.0), statut=VAL,
                source=SRC_INC_PARAM + " (COEFFICIENT_SECURITE_MIN_RECOMMANDE = 3)",
            ),
            "filetage": Param(
                None, "texte",
                "Filetage de l'insert d'ancre noyé Incognito.",
                statut=TODO,
                justification="TODO : seul le diamètre 12 mm est documenté. Aucun filetage (M8, M10, M12 ou axe lisse) "
                              "n'apparaît dans parametres.py, fixations.py ni la grammaire banquette. "
                              "L'interface œillet M8 Aboutissants n'est donc PAS déduite d'Incognito. "
                              "Un adaptateur reste à spécifier — et toute pièce visible à l'état fermé "
                              "enfreindrait la règle de discrétion.",
                source=SRC_INC_PARAM + " ; " + SRC_INC_FIX + " (INSERT_ANCRE_NOYE.diametre_insert = 12 seulement)",
            ),
            "diametre_interieur_oeillet": Param(
                None, "mm",
                "Diamètre intérieur d'un œillet / anneau apparent Incognito.",
                statut=TODO,
                justification="TODO : il n'y a pas d'œillet ni d'anneau apparent. Les ancrages sont des inserts "
                              "noyés, invisibles à l'état fermé, destinés à des bracelets au déploiement.",
                source=SRC_INC_DOC + " ; " + SRC_INC_BANQ,
            ),
            "diametre_fil": Param(
                None, "mm", "Fil d'anneau Incognito — inexistant dans les scripts.",
                statut=TODO,
                justification="TODO : pas d'anneau apparent coté.",
                source=SRC_INC_FIX,
            ),
        },
        "tantra": {
            "filetage": Param(
                "M12", "texte",
                "Filetage de l'insert d'ancre Tantra (anneau à visser dans l'insert).",
                choix=["M12"], statut=IMP, utilise_par=("interfaces", "cadres"),
                justification="Catalogue INSERT_ANCRE_M12 : « Insert d'ancre inox A4 M12 ». "
                              "cotes_mm['filetage'] = 12.0 (diamètre nominal, pas une désignation ISO écrite 'M12'). "
                              "Ce n'est PAS le filetage M8 de l'interface œillet Aboutissants.",
                source=SRC_TAN_FIX + " (INSERT_ANCRE_M12.cotes_mm['filetage'] = 12.0)",
            ),
            "filetage_diametre": Param(
                12.0, "mm",
                "Valeur numérique brute de INSERT_ANCRE_M12.cotes_mm['filetage'].",
                plage=(12.0, 12.0), statut=IMP,
                source=SRC_TAN_FIX + " (INSERT_ANCRE_M12.cotes_mm['filetage'] = 12.0)",
            ),
            "pas": Param(
                1.75, "mm",
                "Pas gros ISO du filetage M12 — non coté dans les scripts Tantra.",
                plage=(1.25, 1.75), statut=LIB,
                justification="Pas gros normalisé ISO 261 / ISO 724 pour M12. Non coté dans Tantra "
                              "(seule la valeur 12.0 est dans le catalogue). Valeur de norme, pas une cote inventée de meuble.",
                source="ISO 261 / ISO 724 (pas gros M12 = 1,75 mm)",
            ),
            "diametre_insert": Param(
                16.0, "mm",
                "Diamètre extérieur de l'insert d'ancre inox A4 M12 Tantra.",
                plage=(10.0, 30.0), statut=IMP,
                source=SRC_TAN_FIX + " (INSERT_ANCRE_M12.cotes_mm['diametre_insert'] = 16.0)",
            ),
            "longueur_encastrement": Param(
                60.0, "mm",
                "Longueur d'encastrement de l'insert d'ancre M12 Tantra.",
                plage=(20.0, 120.0), statut=IMP,
                source=SRC_TAN_FIX + " (INSERT_ANCRE_M12.cotes_mm['longueur_encastrement'] = 60.0)",
            ),
            "charge_service": Param(
                1500.0, "N",
                "Charge de service par ancrage Tantra (hypothèse, essai réel obligatoire).",
                plage=(200.0, 10000.0), statut=VAL,
                justification="Même hypothèse qu'Incognito : traction d'un bracelet tendu avec à-coup. "
                              "Les charges Tantra sont des hypothèses de conception, pas des CMU fabricant.",
                source=SRC_TAN_PARAM + " (ParametresCharge.charge_service_ancrage_n = 1500.0)",
            ),
            "coefficient_securite": Param(
                3.0, "",
                "Coefficient de sécurité minimal Tantra (appliqué à la résistance caractéristique).",
                plage=(3.0, 10.0), statut=IMP,
                source=SRC_TAN_PARAM + " (COEFFICIENT_SECURITE_MIN = 3.0 ; ParametresCharge.coefficient_securite)",
            ),
            "charge_rupture_visee": Param(
                4500.0, "N",
                "Charge de rupture visée = charge_service × CS (1500 × 3).",
                plage=(600.0, 30000.0), statut=DER,
                justification="Propriété ParametresCharge.charge_rupture_visee_ancrage_n.",
                source=SRC_TAN_PARAM + " (charge_rupture_visee_ancrage_n = charge_service_ancrage_n * coefficient_securite)",
            ),
            "poids_personne": Param(
                1100.0, "N",
                "Poids de service d'une personne (hypothèse Tantra, ≈ 112 kg).",
                plage=(500.0, 2000.0), statut=VAL,
                source=SRC_TAN_PARAM + " (ParametresCharge.poids_personne_n = 1100.0)",
            ),
            "facteur_dynamique": Param(
                1.5, "",
                "Facteur dynamique Tantra sur le poids (mouvements rythmés).",
                plage=(1.0, 4.0), statut=VAL,
                justification="Valeur Tantra, distincte du coefficient_dynamique Equinox / Aboutissants (2,0).",
                source=SRC_TAN_PARAM + " (ParametresCharge.facteur_dynamique = 1.5)",
            ),
            "retrait_ancre_sous_surface": Param(
                10.0, "mm",
                "Bois (ou cache) minimal au-dessus d'un insert d'ancre masqué (volet camouflable).",
                plage=(0.0, 40.0), statut=VAL,
                source=SRC_TAN_PARAM + " (ParametresGlobaux.retrait_ancre_sous_surface_mm = 10.0)",
            ),
            "cache_diametre": Param(
                40.0, "mm",
                "Diamètre de la pastille de cache aimanté obturant l'insert au repos (volet 2).",
                plage=(20.0, 80.0), statut=LIB,
                source=SRC_TAN_FIX + " (CACHE_AIMANTE.cotes_mm['diametre'] = 40.0)",
            ),
            "cache_epaisseur": Param(
                10.0, "mm",
                "Épaisseur du cache aimanté affleurant Tantra.",
                plage=(4.0, 20.0), statut=LIB,
                source=SRC_TAN_FIX + " (CACHE_AIMANTE.cotes_mm['epaisseur'] = 10.0)",
            ),
            "anneau_diametre_cuvette": Param(
                50.0, "mm",
                "Diamètre de la cuvette fraisée recevant l'anneau rabattable (affleurant).",
                plage=(20.0, 100.0), statut=LIB,
                source=SRC_TAN_FIX + " (ANNEAU_RABATTABLE.cotes_mm['diametre_cuvette'] = 50.0)",
            ),
            "anneau_profondeur_cuvette": Param(
                12.0, "mm",
                "Profondeur de la cuvette de l'anneau rabattable Tantra.",
                plage=(5.0, 30.0), statut=LIB,
                source=SRC_TAN_FIX + " (ANNEAU_RABATTABLE.cotes_mm['profondeur_cuvette'] = 12.0)",
            ),
            "bloc_min_epaisseur": Param(
                50.0, "mm",
                "Minimum constructif d'épaisseur de bloc d'ancrage (hors recouvrement de discrétion).",
                plage=(50.0, 50.0), statut=LIB,
                justification="regles.recaler_bloc_ancrage : epaisseur = arrondir_dessus(max(2·paroi + Ø + recouvrement, 50 + recouvrement)). "
                              "Le commentaire d'en-tête fixe aussi « bloc ≥ 50 × 80 × 80 mm ».",
                source=SRC_TAN_REG + " (recaler_bloc_ancrage, minimum constructif 50 mm)",
            ),
            "bloc_min_largeur_formule": Param(
                60.0, "mm",
                "Plancher de largeur dans la formule de recalage (avant max avec Ø + 2·bord).",
                plage=(60.0, 60.0), statut=LIB,
                source=SRC_TAN_REG + " (largeur = arrondir_dessus(max(d + 2·bord, 60.0)))",
            ),
            "bloc_min_longueur": Param(
                80.0, "mm",
                "Minimum constructif de longueur de bloc (et plancher de la formule max(l_ef + 20, 80)).",
                plage=(80.0, 80.0), statut=LIB,
                source=SRC_TAN_REG + " (longueur = arrondir_dessus(max(l_ef + 20, 80.0)) ; en-tête « 50 × 80 × 80 mm »)",
            ),
            "distance_bord_min": Param(
                25.0, "mm",
                "Distance au bord minimale (plancher), avant le critère 2Ø.",
                plage=(25.0, 25.0), statut=LIB,
                source=SRC_TAN_REG + " (bord = max(25.0, 2.0 * d))",
            ),
            "bloc_epaisseur_defaut": Param(
                50.0, "mm",
                "Épaisseur de bloc recalée par défaut (chêne, recouvrement 0, insert M12 catalogue).",
                plage=(50.0, 200.0), statut=DER,
                justification="Résultat de recaler_bloc_ancrage(essence_structure=chêne, recouvrement_mm=0.0).",
                source=SRC_TAN_REG + " (recaler_bloc_ancrage, défauts PARAMETRES_DEFAUT, recouvrement 0 → 50 mm)",
            ),
            "bloc_largeur_defaut": Param(
                80.0, "mm",
                "Largeur de bloc recalée par défaut (max(16 + 2×32, 60) arrondi = 80 mm).",
                plage=(60.0, 200.0), statut=DER,
                source=SRC_TAN_REG + " (recaler_bloc_ancrage, défauts → 80 mm)",
            ),
            "bloc_longueur_defaut": Param(
                80.0, "mm",
                "Longueur de bloc recalée par défaut (max(60 + 20, 80) = 80 mm).",
                plage=(80.0, 200.0), statut=DER,
                source=SRC_TAN_REG + " (recaler_bloc_ancrage, défauts → 80 mm)",
            ),
            "tourillon_liaison_diametre": Param(
                12.0, "mm",
                "Diamètre des tourillons de liaison bloc / flasque (ou structure).",
                plage=(8.0, 20.0), statut=LIB,
                source=SRC_TAN_FIX + " (TOURILLON_12.cotes_mm['diametre'] = 12.0) ; " + SRC_TAN_SIEGE,
            ),
            "tourillon_liaison_longueur": Param(
                50.0, "mm",
                "Longueur des tourillons Ø12 de liaison des blocs d'ancrage.",
                plage=(30.0, 80.0), statut=LIB,
                source=SRC_TAN_FIX + " (TOURILLON_12.cotes_mm['longueur'] = 50.0)",
            ),
            "presence_npt": Param(
                False, "bool",
                "Un filetage 1\" NPT est-il prévu dans les scripts Tantra ?",
                statut=IMP,
                justification="Aucune occurrence dans les paramètres, catalogues, grammaires ou docs Tantra.",
                source="tantra/ (absence, grep 2026-11-18)",
            ),
            "presence_vac_u_lock": Param(
                False, "bool",
                "Un port Vac-U-Lock est-il prévu dans les scripts Tantra ?",
                statut=IMP,
                justification="Aucune occurrence. Les ancrages sont des inserts M12 + anneau rabattable / cache aimanté.",
                source="tantra/ (absence, grep 2026-11-18)",
            ),
            "diametre_interieur_anneau": Param(
                None, "mm",
                "Diamètre intérieur de l'anneau rabattable (ou de l'anneau à épaulement) Tantra.",
                statut=TODO,
                justification="TODO : ANNEAU_RABATTABLE cote seulement diametre_cuvette = 50 mm et "
                              "profondeur_cuvette = 12 mm. Ni le DI de l'œil ni le Ø de fil ne sont documentés. "
                              "On ne peut pas garantir le passage d'un axe de bride Aboutissants (M8 / Ø6 ou Ø8).",
                source=SRC_TAN_FIX + " (ANNEAU_RABATTABLE.cotes_mm : cuvette seulement)",
            ),
            "diametre_fil": Param(
                None, "mm",
                "Diamètre du fil de l'anneau rabattable / à épaulement Tantra.",
                statut=TODO,
                justification="TODO : pas de cote de fil dans fixations.py ni dans les grammaires.",
                source=SRC_TAN_FIX,
            ),
            "emplacement_collecteur": Param(
                None, "mm",
                "Emplacement réservé (cotes) pour un collecteur d'urine sur un meuble Tantra.",
                statut=TODO,
                justification="TODO : aucun emplacement de collecteur, d'entonnoir, de gouttière ou de cuve "
                              "n'est coté dans les scripts ou la documentation Tantra. Un caisson rapporté "
                              "sous / derrière un siège reste possible sans modifier le meuble, mais sans cote d'implantation.",
                source="tantra/ (absence)",
            ),
            "emplacement_machine": Param(
                None, "mm",
                "Emplacement réservé (cotes) pour une machine de mouvement sur un meuble Tantra.",
                statut=TODO,
                justification="TODO : aucun emplacement de machine n'est prévu. Accroche éventuelle sur insert M12 "
                              "sous réserve d'un adaptateur et du DI d'anneau (TODO).",
                source="tantra/ (absence)",
            ),
            "chaise_double_courbe_nombre": Param(
                4, "",
                "Nombre d'ancrages (insert M12 + anneau rabattable) de la chaise longue à double courbe.",
                plage=(4, 4), statut=LIB,
                justification="Deux positions en Y, une par flasque extérieure (g/d).",
                source=SRC_TAN_CHAISE + " (positions_ancrages, ancrages_flasques) ; " + SRC_TAN_SIEGE,
            ),
            "chaise_double_courbe_positions_y": Param(
                [760.0, 1560.0], "liste_mm",
                "Positions Y (mm) des paires d'ancrages sur la chaise à double courbe (défauts de grammaire).",
                statut=LIB,
                source=SRC_TAN_CHAISE + " (ParametresChaise.positions_ancrages = (760.0, 1560.0))",
            ),
            "fauteuil_lombaire_nombre": Param(
                2, "",
                "Nombre d'ancrages du fauteuil lombaire (une paire, une par flasque).",
                plage=(2, 2), statut=LIB,
                source=SRC_TAN_FAUT + " (ancrages_flasques(..., (pc['cale'].y + 40.0,)))",
            ),
            "banquette_deux_niveaux_nombre": Param(
                6, "",
                "Nombre d'ancrages de la banquette à deux niveaux (trois par flasque extérieure).",
                plage=(6, 6), statut=LIB,
                source=SRC_TAN_BANQ + " (six ancrages, ancrages_flasques) ; docstring de typologie",
            ),
            "siege_repose_genoux_nombre": Param(
                4, "",
                "Nombre d'ancrages du siège repose-genoux (genoux + assise, g/d).",
                plage=(4, 4), statut=LIB,
                source=SRC_TAN_GENOUX + " (ancrage_genoux_*, ancrage_assise_*)",
            ),
            "camo_canape_nombre": Param(
                6, "",
                "Nombre d'ancrages masqués du canapé camouflable (1/accoudoir + 2 avant + 2 arrière).",
                plage=(6, 6), statut=LIB,
                source=SRC_TAN_PARAM + " (CAMO_CANAPE, « Six ancrages masqués ») ; " + SRC_TAN_CAMO_CAN + " ; " + SRC_TAN_SALON,
            ),
            "camo_fauteuil_nombre": Param(
                4, "",
                "Nombre d'ancrages du fauteuil camouflable (2 accoudoirs + 2 avant ; pas d'ancrages arrière).",
                plage=(4, 4), statut=LIB,
                source=SRC_TAN_PARAM + " (CAMO_FAUTEUIL) ; " + SRC_TAN_CAMO_FAU + " (ancrages_arriere=False)",
            ),
            "cadre_desserte_nombre": Param(
                4, "",
                "Nombre d'ancrages de la desserte → cadre à genoux (2 poignets + 2 chevilles).",
                plage=(4, 4), statut=LIB,
                source=SRC_TAN_DESSERTE + " (ancrage_poignet_*, ancrage_cheville_*)",
            ),
            "cadre_desserte_hauteur_meuble": Param(
                750.0, "mm",
                "Hauteur du plateau / barre haute à l'état MEUBLE (axe des ancrages poignets, défaut typologie).",
                plage=(700.0, 800.0), statut=VAL,
                source=SRC_TAN_PARAM + " (CADRE_DESSERTE_GENOUX cote hauteur_meuble = 750.0)",
            ),
            "cadre_desserte_hauteur_cadre": Param(
                1150.0, "mm",
                "Dessus de la barre haute à l'état CADRE (axe des ancrages poignets, défaut typologie).",
                plage=(1100.0, 1300.0), statut=VAL,
                source=SRC_TAN_PARAM + " (CADRE_DESSERTE_GENOUX cote hauteur_cadre = 1150.0)",
            ),
            "cadre_table_inclinee_nombre": Param(
                None, "",
                "Nombre d'ancrages de la typologie table basse → cadre incliné.",
                statut=TODO,
                justification="TODO : typologie étudiée, pas de grammaire ni de script Fusion livrés "
                              "(docs/cadre_table_inclinee.md). Les cotes d'encombrement existent "
                              "(1100 × 700 × 420 mm, angle 78°) mais aucun point d'ancrage n'est coté. "
                              "La note d'étude exige une fixation murale ou au sol, ou une marche-plateforme, "
                              "parce que les efforts seraient extérieurs.",
                source=SRC_TAN_DOC_TABLE + " ; " + SRC_TAN_PARAM + " (CADRE_TABLE_INCLINEE, typologie seule)",
            ),
        },
        "rangement": {
            "filetage_insert": Param(
                "M8", "texte",
                "Filetage des inserts Rangement (crochets, consoles, platines, ports filetés).",
                choix=["M6", "M8", "M10"], statut=VAL,
                justification="Repris d'Equinox (jonctions.filetage_insert) et aligné sur l'interface Aboutissants.",
                source=SRC_RAN_PARAM + " (quincaillerie.filetage_insert = M8)",
            ),
            "longueur_insert": Param(
                20.0, "mm",
                "Longueur des inserts filetés Rangement (20 mm si densité ≥ 650 kg/m³, sinon 25).",
                plage=(10.0, 40.0), statut=DER,
                source=SRC_RAN_PARAM + " (quincaillerie.longueur_insert = 20.0) ; " + SRC_RAN_QUIN,
            ),
            "cmu_insert_m8": Param(
                2500.0, "N",
                "CMU catalogue de l'insert fileté M8 Rangement (reprise Equinox, à confirmer fabricant).",
                plage=(200.0, 10000.0), statut=VAL,
                source=SRC_RAN_QUIN + " (VISSERIE['insert_filete_m8'].capacite_service = 2500.0)",
            ),
            "point_ancrage_personne": Param(
                False, "bool",
                "Un râtelier / meuble de rangement est-il un point d'ancrage de personne ?",
                statut=IMP,
                justification="Explicite : « un ratelier n'est PAS un point d'ancrage de personne ». "
                              "L'effort_accidentel (300 N) n'est vérifié qu'en alerte (déformation).",
                source=SRC_RAN_PARAM + " (charges.effort_accidentel, justification)",
            ),
            "effort_accidentel": Param(
                300.0, "N",
                "Traction accidentelle ponctuelle (on se retient à une barre ou un crochet) — pas une retenue.",
                plage=(0.0, 2000.0), statut=VAL,
                source=SRC_RAN_PARAM + " (charges.effort_accidentel = 300.0, a_valider)",
            ),
            "ports_vac_u_lock": Param(
                True, "bool",
                "Rangement prévoit des ports Vac-U-Lock compatibles Aboutissants.",
                statut=VAL,
                source=SRC_RAN_PARAM + " (ports.vac_u_lock = True)",
            ),
            "ports_npt": Param(
                True, "bool",
                "Rangement prévoit des douilles 1\" NPT femelles compatibles Aboutissants / Incognito.",
                statut=VAL,
                source=SRC_RAN_PARAM + " (ports.npt = True)",
            ),
            "montage_arriere_defaut": Param(
                "npt_1_male", "texte",
                "Interface arrière de l'ergot sur un port de meuble Rangement (défaut typologie).",
                choix=["filete_machine", "npt_1_femelle", "npt_1_male", "filete_et_npt", "integré"],
                statut=VAL,
                justification="Sur un meuble, la douille femelle 1\" NPT est dans le bois : l'ergot porte un "
                              "arrière MÂLE. Le défaut Aboutissants (filete_machine, M8) reste disponible via "
                              "le système port_vac_u_lock_m8. Décision à trancher par Fabien (déjà signalée dans Rangement).",
                source=SRC_RAN_PARAM + " (ports.montage_arriere = npt_1_male, a_valider ; « A TRANCHER »)",
            ),
            "systeme_port_defaut": Param(
                "port_vac_u_lock_npt", "texte",
                "Système de port par défaut du râtelier (ergot + douille NPT).",
                statut=VAL,
                source=SRC_RAN_PARAM + " (systemes.port = port_vac_u_lock_npt) ; " + SRC_RAN_SYS,
            ),
            "filetage_ergot": Param(
                "M8x1.25", "texte",
                "Filetage de l'ergot en montage fileté (côté meuble), reprise Aboutissants.",
                statut=VAL,
                source=SRC_RAN_PARAM + " (ports.filetage_ergot = M8x1.25)",
            ),
            "filetage_ergot_longueur": Param(
                16.0, "mm",
                "Longueur utile de la tige filetée de l'ergot (montage fileté).",
                plage=(6.0, 40.0), statut=VAL,
                source=SRC_RAN_PARAM + " (ports.filetage_ergot_longueur = 16.0)",
            ),
            "pas_ports": Param(
                200.0, "mm",
                "Entraxe des ports le long d'un module de râtelier.",
                plage=(80.0, 600.0), statut=VAL,
                source=SRC_RAN_PARAM + " (ports.pas_ports = 200.0, repris de cadre_modulaire.pas_ports)",
            ),
            "epaisseur_panneau_mural": Param(
                22.0, "mm",
                "Épaisseur du panneau dorsal des râteliers (reçoit inserts M8 20 mm, consoles, douilles NPT).",
                plage=(15.0, 40.0), statut=VAL,
                source=SRC_RAN_PARAM + " (panneaux.epaisseur_panneau_mural = 22.0)",
            ),
            "epaisseur_cache": Param(
                10.0, "mm",
                "Épaisseur des caches bois affleurants (ports, inserts).",
                plage=(4.0, 20.0), statut=VAL,
                source=SRC_RAN_PARAM + " (discretion.epaisseur_cache = 10.0)",
            ),
            "plot_largeur": Param(
                70.0, "mm",
                "Largeur (X) et hauteur (Z) du plot bois porte-douille NPT du râtelier.",
                plage=(40.0, 150.0), statut=VAL,
                source=SRC_RAN_RAT + " (SCHEMA typologie plot_largeur = 70.0)",
            ),
            "plot_profondeur": Param(
                40.0, "mm",
                "Profondeur (Y) du plot porte-douille NPT du râtelier.",
                plage=(20.0, 120.0), statut=VAL,
                source=SRC_RAN_RAT + " (SCHEMA typologie plot_profondeur = 40.0)",
            ),
            "ports_par_module": Param(
                2, "",
                "Nombre de ports Aboutissants par module de râtelier (au pas ports.pas_ports).",
                plage=(0, 8), statut=VAL,
                source=SRC_RAN_RAT + " (ports_par_module = 2)",
            ),
            "hauteur_ports": Param(
                130.0, "mm",
                "Axe de la rangée de ports depuis le bas du panneau (hors hauteur de pose).",
                plage=(40.0, 1800.0), statut=VAL,
                source=SRC_RAN_RAT + " (hauteur_ports = 130.0)",
            ),
            "crochets_par_module": Param(
                4, "",
                "Nombre de crochets par module (inserts M8, pas un ancrage de personne).",
                plage=(0, 8), statut=VAL,
                source=SRC_RAN_RAT + " (crochets_par_module = 4)",
            ),
            "hauteur_crochets": Param(
                400.0, "mm",
                "Axe de la rangée de crochets depuis le bas du panneau.",
                plage=(40.0, 1800.0), statut=VAL,
                source=SRC_RAN_RAT + " (hauteur_crochets = 400.0)",
            ),
            "hauteur_pose": Param(
                900.0, "mm",
                "Hauteur du bas du panneau de râtelier au sol (défaut de typologie).",
                plage=(300.0, 1500.0), statut=VAL,
                source=SRC_RAN_RAT + " (hauteur_pose = 900.0)",
            ),
            "module_largeur": Param(
                600.0, "mm",
                "Largeur d'un module (râtelier mural, travée d'armoire).",
                plage=(300.0, 1200.0), statut=VAL,
                source=SRC_RAN_PARAM + " (modules.module_largeur = 600.0)",
            ),
            "module_hauteur": Param(
                320.0, "mm",
                "Hauteur d'un module (10 × 32 mm).",
                plage=(160.0, 960.0), statut=VAL,
                source=SRC_RAN_PARAM + " (modules.module_hauteur = 320.0)",
            ),
            "nombre_barres": Param(
                2, "",
                "Nombre de barres de suspension par module (défaut râtelier).",
                plage=(0, 4), statut=VAL,
                source=SRC_RAN_RAT + " (nombre_barres = 2)",
            ),
            "hauteur_premiere_barre": Param(
                680.0, "mm",
                "Axe de la barre la plus basse depuis le bas du panneau.",
                plage=(100.0, 1800.0), statut=VAL,
                source=SRC_RAN_RAT + " (hauteur_premiere_barre = 680.0)",
            ),
            "capacite_support_mur": Param(
                None, "N",
                "Capacité de calcul du support mural (chevilles, ossature) — non relevée.",
                statut=TODO,
                justification="TODO : pose.capacite_support_mur = None également dans Rangement "
                              "(reprise de cadre_modulaire.capacite_support_mur). Relevé sur place obligatoire.",
                source=SRC_RAN_PARAM + " (pose.capacite_support_mur = None, statut todo)",
            ),
            "emplacement_collecteur": Param(
                None, "mm",
                "Emplacement réservé pour un collecteur d'urine dans la gamme Rangement.",
                statut=TODO,
                justification="TODO : aucun collecteur n'est prévu. Le râtelier mural n'a pas d'assise. "
                              "Les typologies coffre / armoire n'ont pas encore de grammaire livrée, "
                              "et aucun volume de collecte n'y est coté.",
                source="rangement/ (absence) ; typologies sans grammaire : armoire_accessoires, coffre, "
                       "support_exposition, armoire_verrouillable",
            ),
            "emplacement_machine": Param(
                None, "mm",
                "Emplacement réservé pour une machine de mouvement sur un meuble Rangement.",
                statut=TODO,
                justification="TODO : aucun emplacement machine. Un râtelier mural n'est pas conçu pour "
                              "reprendre 800 N de poussée dynamique ; la capacité du support mural est elle-même TODO.",
                source="rangement/ (absence)",
            ),
            "diametre_interieur_anneau": Param(
                None, "mm",
                "Diamètre intérieur d'un anneau / œillet d'ancrage de personne Rangement.",
                statut=TODO,
                justification="TODO : la gamme n'expose pas d'anneau ni d'œillet de retenue. "
                              "Les crochets (tige Ø8, platine Ø40, saillie 60 mm, insert M8) et les barres "
                              "sont des supports d'accessoires, pas des points d'ancrage de personne.",
                source=SRC_RAN_SYS + " (crochet_inox_simple, barres) ; " + SRC_RAN_PARAM,
            ),
            "diametre_fil": Param(
                None, "mm",
                "Fil d'un anneau d'ancrage de personne Rangement — inexistant.",
                statut=TODO,
                justification="TODO : pas d'anneau de retenue. Ne pas confondre avec diametre_tige = 8.0 "
                              "des crochets inox (catalogue systèmes, pas une cote d'œillet de personne).",
                source=SRC_RAN_SYS + " (crochet_inox_simple.geometrie.diametre_tige = 8.0, hors ancrage personne)",
            ),
        },
    },
})


SCHEMA.update({
    # -- Mouvement mécanique (couche 1 : paramètres globaux du premier module)
    "mouvement": {
        "type_entrainement": Param(
            "manivelle", "texte",
            "Mode d'entraînement mécanique (la version électrique viendra plus tard).",
            choix=["manivelle", "pedalier", "treuil", "moteur_reserve"], statut=VAL,
            utilise_par=("mouvement",),
            justification="Premier module exclusivement mécanique. « moteur_reserve » active uniquement "
                          "l'interface de fixation et l'arbre commun, sans motorisation dans cette version.",
        ),
        # Course / amplitude. Formule : course = 2 × excentricité (bielle-manivelle alignée ou excentrique).
        "course": Param(
            80.0, "mm",
            "Course (amplitude linéaire) de la tige / du coulisseau, de bout en bout.",
            plage=(20.0, 160.0), statut=VAL, utilise_par=("mouvement",),
            justification="Formule : course = 2 × excentricité, pour une bielle-manivelle alignée "
                          "(axe du coulisseau passant par l'axe de vilebrequin) ou un excentrique / "
                          "joug écossais. Défaut 80 mm (e = 40 mm), hypothèse confort/encombrement à valider. "
                          "La course réellement atteinte se vérifie par parcours cinématique (voir grammaire).",
        ),
        "course_min": Param(
            30.0, "mm",
            "Plus petite course réglable (trou d'excentricité le plus proche de l'axe).",
            plage=(10.0, 80.0), statut=VAL, utilise_par=("mouvement",),
            justification="course_min = 2 × min(trous_excentricite). Défaut 2 × 15 = 30 mm.",
        ),
        "course_max": Param(
            140.0, "mm",
            "Plus grande course réglable (trou d'excentricité le plus éloigné).",
            plage=(40.0, 200.0), statut=VAL, utilise_par=("mouvement",),
            justification="course_max = 2 × max(trous_excentricite). Défaut 2 × 70 = 140 mm. "
                          "Doit rester ≤ plage de « course » et compatible avec la longueur de bielle.",
        ),
        "excentricite": Param(
            40.0, "mm",
            "Excentricité courante e (distance axe vilebrequin → axe de maneton).",
            plage=(10.0, 80.0), statut=DER, utilise_par=("mouvement",),
            justification="DÉRIVÉ : e = course / 2. Inversement, course = 2 × e. "
                          "Doit coïncider avec l'un des trous du disque (réglage discret).",
        ),
        "trous_excentricite": Param(
            [15.0, 25.0, 40.0, 55.0, 70.0], "liste_mm",
            "Rayons des trous de maneton sur le disque (réglage d'amplitude par trous multiples).",
            statut=VAL, utilise_par=("mouvement",),
            justification="Réglage positif (goupille / vis dans un trou), plus sûr qu'un excentrique "
                          "continu mal bloqué. Courses résultantes : 30, 50, 80, 110, 140 mm. "
                          "Un excentrique à deux disques (réglage continu) pourra s'ajouter plus tard ; "
                          "la formule course = 2e reste valable.",
        ),
        "longueur_bielle": Param(
            250.0, "mm",
            "Longueur d'axe en axe de la bielle (L).",
            plage=(120.0, 500.0), statut=VAL, utilise_par=("mouvement",),
            justification="Doit vérifier L > e_max (ici 70 mm) avec une marge : L / e_max ≥ 3 recommandé "
                          "pour limiter les efforts latéraux sur le rail (250/70 ≈ 3,6). "
                          "Position du coulisseau, bielle-manivelle alignée : "
                          "x(θ) = e·cos θ + √(L² − (e·sin θ)²). La course x(0)−x(π) vaut exactement 2e.",
        ),
        "ratio_bielle_min": Param(
            3.0, "",
            "Rapport minimal recommandé L / e_max.",
            plage=(2.0, 6.0), statut=VAL,
            justification="En dessous de ~3, l'effort de rappel transversal et l'irrégularité de vitesse "
                          "augmentent fortement. Alerte si L / max(trous) < cette valeur.",
        ),
        # Hauteur réglable
        "hauteur": Param(
            700.0, "mm",
            "Hauteur de l'axe de la tige (sortie) au sol, position courante.",
            plage=(300.0, 1000.0), statut=VAL, utilise_par=("mouvement",),
            justification="Défaut aligné sur la hauteur d'assise / d'appui Equinox banc Flore et sur "
                          "l'appui déployé Incognito (700 mm), pour travailler au niveau d'un banc. "
                          "Plage couvrant platine Entrave (300–450), assises basses (~430–460) et banc 700.",
            source="Ordre de grandeur des hauteurs de meubles : equinox dimensions.hauteur_assise "
                   "(banc 700 impose, tabouret 440, chaise 460) ; incognito hauteur_appui_banc 700 ; "
                   "neogothique cremaillere 300–450. La machine est un module rapporté, cette hauteur "
                   "est un paramètre Aboutissants à valider, pas une cote de meuble copiée telle quelle.",
        ),
        "hauteur_min": Param(
            350.0, "mm", "Plus basse hauteur réglable de l'axe de tige au sol.",
            plage=(250.0, 600.0), statut=VAL,
            justification="Couvre un usage près d'une platine d'Entrave (~300–450) ou d'une assise basse.",
        ),
        "hauteur_max": Param(
            900.0, "mm", "Plus haute hauteur réglable de l'axe de tige au sol.",
            plage=(600.0, 1200.0), statut=VAL,
            justification="Marge au-dessus d'un banc à 700 mm. Attention au moment de renversement "
                          "(bras de levier) : plus c'est haut, plus le châssis doit être large ou lesté.",
        ),
        "pas_hauteur": Param(
            25.0, "mm",
            "Pas des trous de réglage de hauteur sur la colonne (goupille).",
            plage=(10.0, 50.0), statut=VAL,
            justification="Identique au pas de crémaillère de l'Entrave (25 mm) pour un réglage familier. "
                          "Réglage discret par goupille : plus sûr qu'un collier seulement serré.",
            source="Pas inspiré de neogothique cremaillere.pas = 25 mm, appliqué ici à la colonne de la machine.",
        ),
        "diametre_colonne": Param(
            40.0, "mm", "Diamètre extérieur du tube de colonne (réglage de hauteur).",
            plage=(25.0, 80.0), statut=VAL,
            justification="Tube Ø40, même ordre que le tube de traverse Equinox (40×40). À vérifier en flexion "
                          "sous charge_service_poussee × bras (hauteur).",
        ),
        # Rail / châssis
        "rail_longueur": Param(
            280.0, "mm",
            "Longueur utile du rail linéaire (doit couvrir course_max + chariot + butées + jeu).",
            plage=(150.0, 600.0), statut=VAL,
            justification="Défaut : course_max (140) + longueur_chariot (60) + 2×butée (2×20) + marge (40) = 280 mm.",
        ),
        "longueur_chariot": Param(
            60.0, "mm", "Longueur du chariot / coulisseau sur le rail.",
            plage=(30.0, 150.0), statut=VAL,
            justification="Assez long pour encaisser l'effort transversal de bielle sans coincer.",
        ),
        "butee_course": Param(
            20.0, "mm", "Longueur réservée à chaque butée de fin de course en bout de rail.",
            plage=(8.0, 50.0), statut=VAL,
            justification="Butées positives (tampons) : le maneton ne doit jamais être le seul arrêt. "
                          "Elles sont dimensionnées hors de la course réglée (garde).",
        ),
        "chassis_longueur": Param(
            450.0, "mm", "Longueur hors-tout du châssis au sol (direction de la poussée).",
            plage=(250.0, 800.0), statut=VAL,
            justification="Empreinte propre de la machine : la stabilité ne doit pas reposer uniquement "
                          "sur l'œillet du meuble (bride = anti-glissement / anti-basculement et locateur).",
        ),
        "chassis_largeur": Param(
            300.0, "mm", "Largeur hors-tout du châssis au sol.",
            plage=(180.0, 600.0), statut=VAL,
            justification="Polygone de sustentation propre. À valider avec le lest et la hauteur max.",
        ),
        "chassis_hauteur_poutre": Param(
            40.0, "mm", "Hauteur des longerons du châssis.",
            plage=(20.0, 80.0), statut=VAL,
        ),
        "lest": Param(
            8.0, "kg", "Lest additionnel prévu dans le châssis (à valider selon essai de basculement).",
            plage=(0.0, 40.0), statut=VAL,
            justification="Complément au poids propre. L'Entrave montrait qu'un meuble de 47 kg bascule "
                          "sous 500 N × 1,5 à 56 cm sans ancrage : ne pas compter sur la seule masse.",
        ),
        # Bride / clamp sur œillet existant, sans modifier le meuble.
        "bride_type": Param(
            "chape_axe", "texte",
            "Type de fixation sur le point d'ancrage du meuble (aucune modification de la structure visible).",
            choix=["chape_axe", "collier_fil"], statut=VAL,
            justification="Chape + axe passant dans l'œil existant (préféré). Variante collier autour du fil "
                          "de l'œillet (fil Ø8 Equinox) si l'œil est trop petit pour un axe confortable. "
                          "Pas de perçage, pas d'insert ajouté dans le meuble.",
        ),
        "bride_diametre_axe_petit_oeil": Param(
            6.0, "mm",
            "Diamètre de l'axe de bride prévu pour l'œillet bas Equinox (DI 12 mm).",
            plage=(4.0, 10.0), statut=VAL,
            justification="L'œillet bas n'a que 12 mm de DI : un axe M8 (Ø 8) ne laisse que 2 mm au total. "
                          "Un axe Ø6 laisse 3 mm par côté avant bague. Charge admissible d'un Ø6 << M8 : "
                          "voir visserie et points critiques. L'anneau arrière DI 40 est préférable.",
            source="Contrainte déduite de " + SRC_EQ_ANC + " (DI œillet bas 12 mm). Valeur d'axe Aboutissants à valider.",
        ),
        "bride_diametre_axe_anneau": Param(
            10.0, "mm",
            "Diamètre de l'axe (ou manille) de bride prévu pour l'anneau Equinox DI 40 mm.",
            plage=(8.0, 16.0), statut=VAL,
            justification="L'anneau DI 40 accepte un axe Ø10 avec bague, beaucoup plus confortable et plus "
                          "résistant que l'œillet bas. Filetage de serrage de chape : M8 (interface normalisée).",
            source="Contrainte déduite de ancrage.diametre_interieur_anneau = 40 mm (Equinox).",
        ),
        "bride_ouverture_chape": Param(
            16.0, "mm",
            "Ouverture intérieure de la chape (doit envelopper le fil Ø8 + jeu, ou la platine).",
            plage=(10.0, 40.0), statut=VAL,
            justification="Fil Equinox Ø8 + jeu + éventuellement platine 2 mm. À valider sur pièce réelle.",
        ),
        # Interface moteur (réservée, version électrique ultérieure).
        "moteur_arbre_diametre": Param(
            12.0, "mm",
            "Diamètre de l'arbre commun (manivelle / pédalier / treuil aujourd'hui, moteur plus tard).",
            plage=(8.0, 20.0), statut=VAL,
            justification="Arbre unique : la manivelle se démonte, un moteur pourra se brider sur la même "
                          "interface. 12 mm, ordre de grandeur d'un arbre de réducteur compact. À valider "
                          "quand le moteur sera choisi.",
        ),
        "moteur_arbre_longueur": Param(
            40.0, "mm", "Longueur utile de l'arbre côté accouplement moteur / manivelle.",
            plage=(20.0, 80.0), statut=VAL,
        ),
        "moteur_entraxe_fixation": Param(
            None, "mm",
            "Entraxe des vis de bride moteur (interface électrique future).",
            statut=TODO,
            justification="TODO : dépend du moteur / réducteur qui sera choisi (NEMA 23, réducteur à vis, etc.). "
                          "Prévoir une platine d'adaptation percée sur l'arbre commun Ø12, sans modifier le châssis.",
        ),
        "moteur_nombre_vis": Param(
            4, "", "Nombre de vis prévu pour la platine d'adaptation moteur (réservé).",
            plage=(2, 8), statut=VAL,
            justification="Standard de face de réducteur (4 vis). Entraxe non figé (TODO).",
        ),
        "moteur_filetage_bride": Param(
            "M5", "texte", "Filetage prévu des vis de platine moteur (hypothèse, à recaler).",
            choix=["M4", "M5", "M6", "M8"], statut=VAL,
            justification="Hypothèse courante sur petites faces de réducteur. À valider avec le fournisseur.",
        ),
        "moteur_couple_nominal": Param(
            None, "N.m",
            "Couple nominal du moteur électrique futur.",
            statut=TODO,
            justification="TODO : à renseigner quand la motorisation sera choisie. En mécanique, le couple "
                          "est limité par l'opérateur (manivelle / pédalier) et par le débrayage.",
        ),
        "manivelle_longueur": Param(
            180.0, "mm", "Longueur de la manivelle (bras, axe → poignée).",
            plage=(80.0, 300.0), statut=VAL,
            justification="Bras de levier pour l'opérateur. Plus long = moins d'effort, plus d'encombrement "
                          "et de risque de heurt. À valider.",
        ),
        "debrayage": Param(
            True, "bool",
            "Présence d'un débrayage / démontage rapide de la manivelle (goupille sur l'arbre).",
            statut=VAL,
            justification="Arrêt d'urgence mécanique : retirer la goupille sépare l'entrée de la transmission. "
                          "Obligatoire recommandé tant qu'il n'y a pas de moteur avec arrêt électrique.",
        ),
    },
})


# ---------------------------------------------------------------------------
# Outils sur arbres de dictionnaires
# ---------------------------------------------------------------------------
def fusion_profonde(base, ajout):
    """Fusionne récursivement ``ajout`` dans une copie de ``base``."""
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


def course_depuis_excentricite(excentricite):
    """Course linéaire = 2 × excentricité (bielle-manivelle alignée ou excentrique)."""
    return 2.0 * float(excentricite)


def excentricite_depuis_course(course):
    """Excentricité e = course / 2."""
    return float(course) / 2.0


def effort_retenue(masse_kg, coefficient_dynamique, g=G):
    """Effort de calcul Equinox sur un point de retenue [N] : k_dyn × 0,5 × m × g."""
    return coefficient_dynamique * 0.5 * masse_kg * g


class Probleme(object):
    """Problème de validation : niveau ('erreur' | 'alerte' | 'todo'), chemin, message."""

    def __init__(self, niveau, chemin, message):
        self.niveau, self.chemin, self.message = niveau, chemin, message

    def __repr__(self):
        return "[%s] %s : %s" % (self.niveau, self.chemin, self.message)

    def __str__(self):
        return self.__repr__()


class Parametres(object):
    """Jeu de paramètres Aboutissants (valeurs + schéma)."""

    def __init__(self, valeurs=None, schema=None):
        self.schema = copy.deepcopy(schema if schema is not None else SCHEMA)
        self.valeurs = _valeurs_depuis_schema(self.schema)
        if valeurs:
            self.fusionner(valeurs)
        # Synchronise e = course/2 si les deux sont présents.
        self._synchroniser_course()
        _synchroniser_variante_tete(self.valeurs)

    def _synchroniser_course(self):
        try:
            course = self.get("mouvement.course")
            if course is not None:
                self.valeurs["mouvement"]["excentricite"] = excentricite_depuis_course(course)
        except KeyError:
            pass

    def copie(self):
        q = Parametres.__new__(Parametres)
        q.schema = copy.deepcopy(self.schema)
        q.valeurs = copy.deepcopy(self.valeurs)
        return q

    def fusionner(self, overrides):
        if not overrides:
            return self
        plats = {k: v for k, v in overrides.items() if isinstance(k, str) and "." in k}
        imbriques = {k: v for k, v in overrides.items() if k not in plats}
        self.valeurs = fusion_profonde(self.valeurs, imbriques)
        for chemin, val in plats.items():
            self.set(chemin, val, creer=True)
        self._synchroniser_course()
        _synchroniser_variante_tete(self.valeurs)
        return self

    def get(self, chemin, defaut=_MANQUANT):
        noeud = self.valeurs
        for cle in chemin.split("."):
            if isinstance(noeud, dict) and cle in noeud:
                noeud = noeud[cle]
            elif defaut is not _MANQUANT:
                return defaut
            else:
                raise KeyError("Paramètre inconnu : %s" % chemin)
        return noeud

    __getitem__ = get

    def set(self, chemin, valeur, creer=False):
        cles = chemin.split(".")
        noeud = self.valeurs
        for cle in cles[:-1]:
            if cle not in noeud:
                if not creer:
                    raise KeyError("Paramètre inconnu : %s" % chemin)
                noeud[cle] = {}
            noeud = noeud[cle]
        noeud[cles[-1]] = valeur
        if chemin == "mouvement.course" and valeur is not None:
            if "mouvement" in self.valeurs:
                self.valeurs["mouvement"]["excentricite"] = excentricite_depuis_course(valeur)
        elif chemin == "mouvement.excentricite" and valeur is not None:
            if "mouvement" in self.valeurs:
                self.valeurs["mouvement"]["course"] = course_depuis_excentricite(valeur)
        if chemin.startswith("vac_u_lock.variante_tete") or chemin.startswith("vac_u_lock.plug_diametre_tete_brevet") or chemin.startswith("vac_u_lock.plug_diametre_tete_boutique"):
            _synchroniser_variante_tete(self.valeurs)
        return self

    def meta(self, chemin):
        noeud = self.schema
        for cle in chemin.split("."):
            noeud = noeud[cle]
        if not isinstance(noeud, Param):
            raise KeyError("Pas une feuille : %s" % chemin)
        return noeud

    def feuilles(self):
        """Itère (chemin, meta, valeur)."""
        for chemin, meta in _iter_schema(self.schema):
            yield chemin, meta, self.get(chemin)

    def todos(self):
        """Liste (chemin, meta) des cotes manquantes (valeur None, statut todo)."""
        return [(c, m) for c, m, v in self.feuilles() if v is None or m.statut == TODO]

    def interface_gamme(self, nom):
        """Dict plat des paramètres d'ancrage d'une gamme (voir ``GAMMES_ANCRAGES``)."""
        return dict(self.valeurs["ancrages"][nom])

    def excentricite(self):
        return excentricite_depuis_course(self.get("mouvement.course"))

    def courses_reglables(self):
        """Liste de courses (mm) correspondant aux trous d'excentricité."""
        return [course_depuis_excentricite(e) for e in self.get("mouvement.trous_excentricite")]

    def effort_retenue(self):
        return effort_retenue(
            self.get("securite.charge_utilisateur"),
            self.get("securite.coefficient_dynamique"),
            self.get("unites.g"),
        )

    def valider(self):
        return valider_parametres(self)

    def exporter_user_parameters(self, design):
        from .fusion_utils import exporter_user_parameters
        return exporter_user_parameters(design, self)


def valider_parametres(params):
    """Vérifie plages, tolérances positives, cohérence course / excentricité, todos."""
    pbs = []
    for chemin, meta, val in params.feuilles():
        if val is None or meta.statut == TODO:
            if val is not None and meta.statut == TODO:
                pbs.append(Probleme("alerte", chemin,
                                    "statut todo mais valeur renseignée (%r) : confirmer la source" % (val,)))
            elif val is None:
                pbs.append(Probleme("todo", chemin,
                                    "Cote manquante (None). %s" % (meta.justification or meta.role)))
            continue
        if meta.choix is not None and val not in meta.choix:
            pbs.append(Probleme("erreur", chemin, "valeur %r hors choix %s" % (val, meta.choix)))
        if isinstance(val, bool):
            continue
        if meta.unite == "liste_mm" or isinstance(val, (list, tuple)):
            for i, item in enumerate(val):
                if not isinstance(item, (int, float)) or item <= 0:
                    pbs.append(Probleme("erreur", chemin, "élément %d invalide (%r)" % (i, item)))
                elif meta.plage and not (meta.plage[0] <= item <= meta.plage[1]):
                    pbs.append(Probleme("erreur", chemin,
                                        "élément %r hors plage %s" % (item, meta.plage)))
            continue
        if isinstance(val, (int, float)) and meta.plage:
            lo, hi = meta.plage
            if not (lo - 1e-9 <= val <= hi + 1e-9):
                pbs.append(Probleme("erreur", chemin, "valeur %g hors plage %s" % (val, meta.plage)))

    # Tolérances et jeux : strictement positifs (0 admis seulement pour jeu_mortaise min).
    for chemin, meta, val in params.feuilles():
        if val is None or not isinstance(val, (int, float)) or isinstance(val, bool):
            continue
        racine = chemin.split(".")[0]
        nom = chemin.split(".")[-1]
        if racine == "tolerances" or nom.startswith("jeu_") or nom.startswith("tolerance_"):
            if val < 0:
                pbs.append(Probleme("erreur", chemin, "tolérance / jeu négatif (%g)" % val))
            elif val == 0 and "mortaise" not in nom:
                pbs.append(Probleme("erreur", chemin, "tolérance / jeu doit être > 0 (%g)" % val))

    # Coefficients de sécurité
    for cle in ("coefficient_bois", "coefficient_metal", "coefficient_ancrage",
                "coefficient_cuir", "coefficient_renversement", "coefficient_dynamique"):
        chemin = "securite." + cle
        try:
            v = params.get(chemin)
        except KeyError:
            continue
        if v is not None and v < 1.0:
            pbs.append(Probleme("erreur", chemin, "coefficient de sécurité < 1 (%g)" % v))

    if params.get("securite.coefficient_ancrage") < 3.0 - 1e-9:
        pbs.append(Probleme(
            "alerte", "securite.coefficient_ancrage",
            "CS ancrage %g < 3 recommandé (Incognito COEFFICIENT_SECURITE_MIN_RECOMMANDE)."
            % params.get("securite.coefficient_ancrage")))

    # Anthropométrie : S < M < L < XL pour chaque tour
    for groupe in ("poignet", "cheville", "cou", "cuisse"):
        cles = ["anthropometrie.%s_tour_%s" % (groupe, t) for t in ("S", "M", "L", "XL")]
        vals = [params.get(c) for c in cles]
        if any(v is None for v in vals):
            continue
        for a, b, ca, cb in zip(vals, vals[1:], cles, cles[1:]):
            if not (a < b):
                pbs.append(Probleme("erreur", cb, "les tours %s doivent être strictement croissants (S<M<L<XL)" % groupe))

    # Course / excentricité / trous
    course = params.get("mouvement.course")
    e = params.get("mouvement.excentricite")
    if course is not None and e is not None:
        if abs(course - course_depuis_excentricite(e)) > 1e-6:
            pbs.append(Probleme("erreur", "mouvement.course",
                                "incohérence : course (%g) ≠ 2 × excentricité (%g)" % (course, e)))
    trous = params.get("mouvement.trous_excentricite") or []
    if trous:
        cmin, cmax = params.get("mouvement.course_min"), params.get("mouvement.course_max")
        attendu_min, attendu_max = course_depuis_excentricite(min(trous)), course_depuis_excentricite(max(trous))
        if cmin is not None and abs(cmin - attendu_min) > 1e-6:
            pbs.append(Probleme("erreur", "mouvement.course_min",
                                "doit valoir 2 × min(trous) = %g (actuel %g)" % (attendu_min, cmin)))
        if cmax is not None and abs(cmax - attendu_max) > 1e-6:
            pbs.append(Probleme("erreur", "mouvement.course_max",
                                "doit valoir 2 × max(trous) = %g (actuel %g)" % (attendu_max, cmax)))
        if len(trous) != len(set(trous)):
            pbs.append(Probleme("erreur", "mouvement.trous_excentricite", "trous en double"))
        if list(trous) != sorted(trous):
            pbs.append(Probleme("alerte", "mouvement.trous_excentricite", "trous non triés par excentricité croissante"))
        if e is not None and min(abs(e - t) for t in trous) > 1e-6:
            pbs.append(Probleme("alerte", "mouvement.excentricite",
                                "e=%g mm ne correspond à aucun trou %s" % (e, trous)))

    L = params.get("mouvement.longueur_bielle")
    ratio = params.get("mouvement.ratio_bielle_min")
    if L is not None and trous:
        e_max = max(trous)
        if L <= e_max:
            pbs.append(Probleme("erreur", "mouvement.longueur_bielle",
                                "bielle L=%g ≤ e_max=%g : transmission bloquée" % (L, e_max)))
        elif ratio and L < ratio * e_max - 1e-9:
            pbs.append(Probleme("alerte", "mouvement.longueur_bielle",
                                "L/e_max = %.2f < %g recommandé" % (L / e_max, ratio)))

    h, hmin, hmax = (params.get("mouvement.hauteur"),
                     params.get("mouvement.hauteur_min"),
                     params.get("mouvement.hauteur_max"))
    if None not in (h, hmin, hmax) and not (hmin - 1e-9 <= h <= hmax + 1e-9):
        pbs.append(Probleme("erreur", "mouvement.hauteur",
                            "hauteur %g hors [%g, %g]" % (h, hmin, hmax)))

    # Rail assez long
    rail = params.get("mouvement.rail_longueur")
    chariot = params.get("mouvement.longueur_chariot")
    butee = params.get("mouvement.butee_course")
    cmax = params.get("mouvement.course_max")
    if None not in (rail, chariot, butee, cmax):
        besoin = cmax + chariot + 2.0 * butee
        if rail + 1e-9 < besoin:
            pbs.append(Probleme("erreur", "mouvement.rail_longueur",
                                "rail %g mm < course_max + chariot + 2 butées = %g mm" % (rail, besoin)))

    # Œillet bas : axe de bride doit passer dans le DI
    di = params.get("ancrages.equinox.diametre_interieur_oeillet_bas")
    axe = params.get("mouvement.bride_diametre_axe_petit_oeil")
    if di is not None and axe is not None and axe >= di:
        pbs.append(Probleme("erreur", "mouvement.bride_diametre_axe_petit_oeil",
                            "axe Ø%g ne passe pas dans l'œillet bas DI %g" % (axe, di)))

    di_a = params.get("ancrages.equinox.diametre_interieur_anneau")
    axe_a = params.get("mouvement.bride_diametre_axe_anneau")
    if di_a is not None and axe_a is not None and axe_a >= di_a:
        pbs.append(Probleme("erreur", "mouvement.bride_diametre_axe_anneau",
                            "axe Ø%g ne passe pas dans l'anneau DI %g" % (axe_a, di_a)))

    pbs.extend(_valider_vac_u_lock(params))
    pbs.extend(_valider_collecteur(params))
    pbs.extend(_valider_cadre(params))
    return pbs


def resume_todos(params=None):
    """Texte des cotes manquantes (pour le rapport)."""
    p = params or Parametres()
    lignes = []
    for chemin, meta in p.todos():
        lignes.append("- `%s` = None — %s (source : %s)" % (
            chemin, meta.justification or meta.role, meta.source or "non documenté dans les scripts"))
    return "\n".join(lignes)



# ---------------------------------------------------------------------------
# Vac-U-Lock, 1" NPT, collecteur d'urine (ajout couche 1)
# ---------------------------------------------------------------------------
SRC_BREVET_VUL = "Brevet US 5,127,396 (McAllister / Health Devices Corp., 1992), mode de réalisation préféré ; page https://vac-u-lock.com/vac-u-lock-patent.html"
SRC_DJ_DOUBLE = "https://www.shopdocjohnson.com/p/448707/1222120/vac-u-lock-double-up-plug (Doc Johnson, Double Up Plug, Dimensions 5.3 in × 1,1 in)"
SRC_ABS_DOUBLE = "https://www.absholdings.com/vac-u-lock-frosted-double-up-plug.html (même référence Double Up : L 5.5 in / 14 cm, largeur 1.25 in / 32 mm, circonférence 3.5 in / 89 mm)"
SRC_VACULOCKS = "https://vaculocks.com (adaptateurs usinés alu ou inox, filetage côté machine)"
SRC_NPT_ASME = "ASME B1.20.1 (1-11.5 NPT) ; également incognito/incognito/catalogues/housses.py"
SRC_INC_HOUSSES = "incognito/incognito/catalogues/housses.py"

SCHEMA.update({
    "npt_1": {
        "designation": Param(
            '1" NPT', "texte",
            "Filetage pipe conique américain, interface déjà retenue par Incognito pour les housses / l'actionneur.",
            statut=LIB, utilise_par=("interfaces", "hygiene"),
            justification="Standard ASME, largement disponible. Distinct du Vac-U-Lock. Absent des scripts Equinox, Néogothique et Tantra ; présent dans Incognito (housses) et Rangement (douilles de ports) (grep 2026-11-18).",
            source=SRC_NPT_ASME,
        ),
        "norme": Param("ASME B1.20.1", "texte", "Norme du filetage.", statut=LIB, source=SRC_NPT_ASME),
        "tpi": Param(
            11.5, "", "Nombre de filets par pouce (1-11.5 NPT).",
            plage=(11.5, 11.5), statut=LIB, source=SRC_NPT_ASME,
        ),
        "pas": Param(
            2.209, "mm", "Pas = 25,4 / 11,5 mm.",
            plage=(2.20, 2.22), statut=DER,
            justification="25,4 / 11,5 ≈ 2,209 mm.",
            source=SRC_NPT_ASME,
        ),
        "diametre_exterieur": Param(
            33.401, "mm",
            "Diamètre extérieur nominal du filetage mâle (pipe OD 1,315 in). Ce n'est pas 1 pouce.",
            plage=(33.3, 33.5), statut=LIB, source=SRC_NPT_ASME,
        ),
        "diametre_primitif_E0": Param(
            30.826, "mm", "Diamètre primitif à l'extrémité du tube (E0 = 1,21363 in).",
            plage=(30.8, 30.9), statut=LIB, source=SRC_NPT_ASME,
        ),
        "diametre_minorant_K0": Param(
            29.060, "mm", "Diamètre minorant à l'extrémité (K0 = 1,1441 in), utile pour le choix du foret.",
            plage=(29.0, 29.2), statut=LIB, source=SRC_NPT_ASME,
        ),
        "conicite": Param(
            0.0625, "", "Conicité 1:16 sur le diamètre (3/4 in par pied).",
            plage=(0.0625, 0.0625), statut=LIB, source=SRC_NPT_ASME,
        ),
        "angle_filet": Param(
            60.0, "deg", "Angle inclus du filet NPT.",
            plage=(60.0, 60.0), statut=LIB, source=SRC_NPT_ASME,
        ),
        "engagement_main_L1": Param(
            10.160, "mm", "Longueur d'engagement à la main (L1 = 0,4000 in).",
            plage=(10.0, 10.3), statut=LIB, source=SRC_NPT_ASME,
        ),
        "longueur_utile_L2": Param(
            17.343, "mm", "Longueur utile de filet externe (L2 = 0,6828 in).",
            plage=(17.2, 17.5), statut=LIB, source=SRC_NPT_ASME,
        ),
        "longueur_totale_L4": Param(
            25.006, "mm", "Longueur totale de filet externe y compris filets imparfaits (L4 = 0,9845 in).",
            plage=(24.9, 25.1), statut=LIB,
            justification="0,9845 × 25,4 = 25,006 mm. Tableaux ASME B1.20.1 publiés (baetrocnc, Engineers Edge).",
            source="ASME B1.20.1, L4 = 0,9845 in pour 1\" NPT",
        ),
        "depassement_recommande": Param(
            25.0, "mm",
            "Dépassement recommandé au-dessus d'une surface pour visser à la main (Incognito).",
            plage=(18.0, 40.0), statut=VAL,
            justification="Un peu plus que L2, repris tel quel du catalogue housses Incognito.",
            source=SRC_INC_HOUSSES + " (NPT_1_DEPASSEMENT_RECOMMANDE_MM = 25)",
        ),
        "present_equinox": Param(
            False, "bool", "Le filetage 1\" NPT apparaît-il dans les scripts Equinox ?",
            statut=LIB,
            justification="grep du 18 nov. 2026 : aucune occurrence dans /workspace/equinox.",
            source="equinox/ (absence)",
        ),
        "present_neogothique": Param(
            False, "bool", "Le filetage 1\" NPT apparaît-il dans les scripts Néogothique ?",
            statut=LIB,
            justification="grep du 18 nov. 2026 : aucune occurrence dans /workspace/neogothique.",
            source="neogothique/ (absence)",
        ),
        "present_incognito": Param(
            True, "bool",
            "Incognito retient un embout mâle 1\" NPT pour housses / actionneur (pas pour les ancrages Ø12).",
            statut=LIB, source=SRC_INC_HOUSSES,
        ),
        "present_tantra": Param(
            False, "bool", "Le filetage 1\" NPT apparaît-il dans les scripts Tantra ?",
            statut=LIB,
            justification="grep du 18 nov. 2026 : aucune occurrence de NPT, Vac-U-Lock ou collecteur "
                          "dans /workspace/tantra (hors filetage d'insert M12, sans rapport).",
            source="tantra/ (absence)",
        ),
        "present_rangement": Param(
            True, "bool",
            "Rangement prévoit des douilles 1\" NPT femelles (ports Aboutissants) sur le râtelier mural.",
            statut=LIB,
            justification="ports.npt = True ; systèmes port_vac_u_lock_npt, port_npt_1_femelle, "
                          "port_cache_affleurant. Le montage arrière par défaut du râtelier est npt_1_male "
                          "(à trancher vs filete_machine).",
            source=SRC_RAN_PARAM + " (ports.npt, ports.montage_arriere) ; " + SRC_RAN_SYS,
        ),
    },

    "vac_u_lock": {
        "avertissement_calibration": Param(
            "calibrage_sur_piece_commerciale_obligatoire", "texte",
            "Les cotes publiques du plug divergent ; un calibrage sur pièce Doc Johnson réelle est obligatoire avant usinage de série.",
            choix=["calibrage_sur_piece_commerciale_obligatoire"], statut=VAL,
            justification="Le brevet donne 1,25 in en tête ; la fiche officielle du Double Up Plug donne 1,1 in ; un revendeur du même article donne 1,25 in de largeur et 3,5 in de circonférence (soit ≈ 1,11 in). LustMonster recommande un relevé au pied à coulisse.",
            source=SRC_BREVET_VUL + " ; " + SRC_DJ_DOUBLE + " ; " + SRC_ABS_DOUBLE + " ; https://lustmonster.com/glossary/vac-u-lock",
        ),
        "forme": Param(
            "tete_milieu_tige_de_revolution", "texte",
            "Forme du plug : tête, section médiane et tige, typiquement de révolution (section approximativement circulaire).",
            choix=["tete_milieu_tige_de_revolution"], statut=LIB,
            justification="Brevet : tête et milieu en « balle » / parabole, épaulements ; la cavité de l'accessoire a la même forme, légèrement plus petite. "
                          "Aucune source publique consultée ne décrit une cavité étoilée : le creux est l'empreinte du plug de révolution. "
                          "Ne pas usiner une étoile faute de cote.",
            source=SRC_BREVET_VUL,
        ),
        "plug_longueur": Param(
            76.2, "mm",
            "Longueur du plug (tête + milieu + tige), hors collerette éventuelle.",
            plage=(50.0, 100.0), statut=VAL, utilise_par=("interfaces", "mouvement"),
            justification="« In a preferred embodiment … the plug is about 3 in long » (76,2 mm). "
                          "Des fiches « Plug With Snaps » annoncent aussi 3 in de longueur, mais pour l'accessoire complet (collerette comprise) : à ne pas confondre.",
            source=SRC_BREVET_VUL,
        ),
        "variante_tete": Param(
            "brevet", "texte",
            "Variante de diamètre de tête : brevet (31,75 mm) ou boutique (27,94 mm). On ne tranche pas.",
            choix=["brevet", "boutique"], statut=VAL, utilise_par=("interfaces", "mouvement"),
            justification="Les deux diamètres restent des variantes paramétrées (décision Fabien). "
                          "Un jeu de cales d'ajustement rattrape le jeu plutôt que de choisir une seule cote. "
                          "Le diamètre actif (plug_diametre_tete_max) suit cette variante.",
            source=SRC_BREVET_VUL + " ; " + SRC_DJ_DOUBLE + " ; " + SRC_VACULOCKS,
        ),
        "plug_diametre_tete_brevet": Param(
            31.75, "mm",
            "Diamètre de tête, variante brevet (1,25 in).",
            plage=(25.0, 36.0), statut=LIB, utilise_par=("interfaces",),
            justification="1,25 in = 31,75 mm, mode préféré du brevet, aussi cité par un revendeur du Double Up (largeur 1,25 in / 32 mm).",
            source=SRC_BREVET_VUL + " ; " + SRC_ABS_DOUBLE,
        ),
        "plug_diametre_tete_boutique": Param(
            27.94, "mm",
            "Diamètre de tête, variante boutique officielle (1,1 in).",
            plage=(25.0, 36.0), statut=LIB, utilise_par=("interfaces",),
            justification="1,1 in = 27,94 mm, fiche Doc Johnson du Double Up Plug. "
                          "La circonférence 3,5 in d'un revendeur (Ø ≈ 28,3 mm) est plus proche de cette valeur.",
            source=SRC_DJ_DOUBLE + " ; circonférence " + SRC_ABS_DOUBLE,
        ),
        "plug_diametre_tete_max": Param(
            31.75, "mm",
            "Diamètre de tête actif (dérivé de variante_tete).",
            plage=(25.0, 36.0), statut=DER, utilise_par=("interfaces", "mouvement"),
            justification="Égal à plug_diametre_tete_brevet ou plug_diametre_tete_boutique selon variante_tete. "
                          "Écart typique 3,81 mm soit 1,905 mm de jeu radial à rattraper par les cales.",
            source="Dérivé des deux variantes sourcées.",
        ),
        "plug_diametre_tete_source_alternative": Param(
            27.94, "mm",
            "Alias documentaire de plug_diametre_tete_boutique (1,1 in).",
            plage=(25.0, 36.0), statut=LIB,
            justification="Conservé pour compatibilité. Utiliser variante_tete = boutique et plug_diametre_tete_boutique.",
            source=SRC_DJ_DOUBLE,
        ),

        "plug_diametre_tige_max": Param(
            19.05, "mm",
            "Plus grand diamètre de la tige (stem) du plug.",
            plage=(12.0, 25.0), statut=VAL,
            justification="« The widest diameter of the plug's stem is about 0.75 in » (19,05 mm). Une seule source chiffrée.",
            source=SRC_BREVET_VUL,
        ),
        "plug_diametre_milieu_max": Param(
            None, "mm",
            "Plus grand diamètre de la section médiane du plug.",
            statut=TODO,
            justification="TODO : le brevet indique seulement qu'il est « slightly less than the largest diameter of the head section », sans cote. Ne pas inventer. Caler sur une pièce commerciale.",
            source=SRC_BREVET_VUL,
        ),
        "plug_longueur_tete": Param(
            None, "mm", "Longueur de la seule tête du plug.",
            statut=TODO,
            justification="TODO : le brevet décrit la forme (pointe presque plate, flanc parabolique, face arrière inclinée) sans décomposer les 3 in en trois longueurs.",
            source=SRC_BREVET_VUL,
        ),
        "plug_longueur_milieu": Param(
            None, "mm", "Longueur de la seule section médiane.",
            statut=TODO,
            justification="TODO : non chiffrée dans le brevet ni sur les fiches fabricant consultées.",
            source=SRC_BREVET_VUL,
        ),
        "plug_longueur_tige": Param(
            None, "mm", "Longueur de la seule tige (stem).",
            statut=TODO,
            justification="TODO : non chiffrée. La collerette (flange) du modèle harnais a des bords d'environ 3 / 2 / 2,5 in, sans épaisseur.",
            source=SRC_BREVET_VUL,
        ),
        "conicite_angle_deg": Param(
            None, "deg",
            "Angle de conicité unique du plug / de la cavité.",
            statut=TODO,
            justification="TODO : le brevet décrit des flancs paraboliques (tête et milieu), pas un cône à angle unique. Aucune source publique n'a donné d'angle en degrés.",
            source=SRC_BREVET_VUL,
        ),
        "cavite_interference": Param(
            None, "mm",
            "Serrage diamétral de la cavité de l'accessoire par rapport au plug (« slightly smaller dimensions »).",
            statut=TODO, utilise_par=("interfaces",),
            justification="TODO : le brevet impose une cavité de même forme, légèrement plus petite, sans valeur. C'est ce serrage, plus l'expulsion d'air, qui fait le « vac-u-lock ». À relever sur pièce (LustMonster : pied à coulisse).",
            source=SRC_BREVET_VUL + " ; https://lustmonster.com/glossary/vac-u-lock",
        ),
        "cavite_profondeur": Param(
            76.2, "mm",
            "Profondeur de cavité visée pour recevoir un plug de 3 in (ordre de grandeur, égale à plug_longueur).",
            plage=(50.0, 100.0), statut=DER,
            justification="Dérivé : une cavité plus courte que le plug ne s'assiérait pas. La profondeur réelle des accessoires du marché n'est pas publiée (TODO de vérification sur pièce). Ce paramètre documente l'enveloppe, ce n'est pas une cote d'empreinte relevée.",
            source="Dérivé de plug_longueur (brevet, 3 in). Profondeur d'empreinte commerciale : non trouvée.",
        ),
        "durete_plug_shore": Param(
            80.0, "",
            "Dureté visée du plug (duromètre, ordre Shore A pour plastisol).",
            plage=(50.0, 100.0), statut=VAL,
            justification="Brevet : 50–100, optimum ≈ 80 pour un peu de souplesse (sécurité et démoulage). Pour un port usiné en inox 316L, la dureté du métal n'est plus celle du plastisol : le contact se fait alors uniquement par l'élasticité de l'accessoire. À valider (risque de déchirer une cavité PVC/silicone si l'ergot est trop abrupt).",
            source=SRC_BREVET_VUL,
        ),
        "collerette_epaisseur": Param(
            None, "mm", "Épaisseur de la collerette (flange) du plug harnais.",
            statut=TODO,
            justification="TODO : le brevet cote le contour de la collerette (haut ≈ 3 in, bas ≈ 2 in, côtés ≈ 2,5 in) mais pas son épaisseur.",
            source=SRC_BREVET_VUL,
        ),
        # Verrouillage complémentaire
        "verrouillage_type": Param(
            "collier_serrage", "texte",
            "Verrouillage mécanique complémentaire contre l'arrachement sous poussée répétée.",
            choix=["aucun", "collier_serrage", "goupille_transversale", "bague_baionnette"],
            statut=VAL, utilise_par=("interfaces", "mouvement"),
            justification="Le vide théorique sous la tête (Ø 31,75 mm) ne fournit qu'environ 80 N (patm × section), très inférieur à 400 N × k_dyn (800 N, poussée nominale validée). "
                          "Le collier de serrage est le seul mode compatible avec n'importe quel accessoire du marché : il appuie la base de l'accessoire contre un épaulement, sans percer le gode. "
                          "La goupille transversale exigerait un trou dans l'accessoire (incompatible « tout le marché »). "
                          "La bague à baïonnette exigerait un ergot correspondant, absent des fiches. Désactivable (aucun).",
        ),
        "verrouillage_actif": Param(
            True, "bool",
            "Active le verrouillage complémentaire (False = emboîtement seul, déconseillé sur la machine).",
            statut=VAL, utilise_par=("interfaces", "mouvement"),
            justification="Sur la machine (poussée nominale validée 400 N, 800 N dynamique), le verrouillage est recommandé obligatoire. Sur un port meuble peu chargé, on peut le désactiver.",
        ),
        "collier_vis": Param(
            "M4", "texte", "Filetage des vis du collier de serrage.",
            choix=["M3", "M4", "M5", "M6"], statut=VAL,
            justification="M4 inox A4 : largement suffisant pour 400 N × 2 vis, encombrement raisonnable.",
        ),
        "collier_nombre_vis": Param(
            2, "", "Nombre de vis (ou de vis + écrou) du collier.",
            plage=(1, 4), statut=VAL,
        ),
        # Montage du port
        "montage_arriere": Param(
            "filete_machine", "texte",
            "Interface arrière du port (côté aboutissant / machine), en plus de l'ergot Vac-U-Lock.",
            choix=["filete_machine", "npt_1_femelle", "npt_1_male", "filete_et_npt", "integré"],
            statut=VAL, utilise_par=("interfaces", "mouvement"),
            justification="Le marché des machines visse le Vac-U-Lock (adaptateurs filetés, vaculocks.com) : "
                          "défaut = ergot fileté côté machine. Le 1 pouce NPT reste disponible (Incognito / housses, "
                          "option Sybian) mais n'est plus le montage arrière par défaut. "
                          "Equinox et Néogothique n'ont pas de NPT : pas d'ajout rétroactif ici "
                          "(décision à prendre, voir le rapport).",
            source=SRC_VACULOCKS + " ; " + SRC_INC_HOUSSES,
        ),
        "filetage_cote_machine": Param(
            "M8x1.25", "texte",
            "Filetage de l'ergot côté machine (défaut M8x1.25, cohérent Equinox).",
            choix=["M6x1", "M8x1", "M8x1.25", "M10x1", "M10x1.5", "M12x1.75", "M16x2",
                   "3/8-16 UNC", "3/4-10 UNC", "5/16-18 UNC", "1/4-20 UNC", "G1/8"],
            statut=VAL, utilise_par=("interfaces", "mouvement"),
            justification="Jeu relevé sur vaculocks.com (adaptateurs usinés alu ou inox). "
                          "M8x1.25 par défaut : même pas que les inserts Equinox et l'interface_oeillet_m8, "
                          "et il passe dans la tige Ø16 de la machine sans raccord Ø 33 mm.",
            source=SRC_VACULOCKS + " ; " + SRC_EQ_ATT + " (insert_filete_m8)",
        ),
        "filetage_cote_machine_longueur": Param(
            16.0, "mm",
            "Longueur utile du filetage côté machine (tige filetée de l'ergot).",
            plage=(6.0, 40.0), statut=VAL, utilise_par=("interfaces",),
            justification="Défaut 16 mm ≈ 2 × d pour M8, engagement courant. Recalculer si le filetage choisi "
                          "a un Ø très différent (M16, 3/4-10).",
        ),
        "cales_epaisseurs": Param(
            [0.25, 0.5, 1.0, 2.0], "mm",
            "Jeu de cales d'ajustement (épaisseurs radiales, combinables) pour rattraper le jeu entre variantes de tête.",
            statut=VAL, utilise_par=("interfaces",),
            justification="L'écart de diamètre entre variantes est 31,75 − 27,94 = 3,81 mm, soit 1,905 mm de jeu radial. "
                          "Les cales 0,25 / 0,5 / 1,0 / 2,0 mm se combinent pour s'en approcher "
                          "(ex. 1,0 + 0,5 + 0,25 + 0,25 = 2,0 mm, ou 1,0 + 0,5 + 0,25 = 1,75 mm). "
                          "Elles rattrapent le jeu d'un ergot plus petit dans une cavité plus grande ; "
                          "elles ne font pas entrer un ergot 31,75 mm dans une cavité 27,94 mm "
                          "(dans ce cas, choisir la variante boutique). "
                          "Calibrage sur pièce réelle toujours recommandé (forme étoilée, cône, Ø milieu = TODO).",
        ),
        "cales_materiau": Param(
            "inox_316", "texte",
            "Matériau des cales d'ajustement (contact éventuel silicone / PVC / nettoyage).",
            choix=["inox_316", "pp_homopolymere", "pehd"], statut=VAL, utilise_par=("interfaces",),
            justification="Inox 316L ou polymère non poreux (PP, PE-HD), seuls matériaux admis au contact "
                          "de l'emboîtement. Même logique que l'ergot / le collecteur. Cuir et sangle exclus.",
            source="catalogues.materiaux (METAUX inox_316, POLYMERES) ; catalogues.vac_u_lock.COMPATIBILITE_CALES",
        ),
        "cales_actives": Param(
            True, "bool",
            "Inclure le jeu de cales dans la géométrie (désactivable).",
            statut=LIB, utilise_par=("interfaces",),
            justification="Les cales font partie de la stratégie d'ajustement (on ne tranche pas le diamètre). "
                          "On peut les omettre si la variante coïncide avec la cavité relevée.",
        ),
        "cales_epaisseur_en_place": Param(
            2.0, "mm",
            "Épaisseur radiale de cale actuellement montée (une valeur du jeu, ou une somme).",
            plage=(0.0, 6.0), statut=VAL, utilise_par=("interfaces",),
            justification="Défaut 2,0 mm : valeur du jeu qui approche le jeu radial typique 1,905 mm. "
                          "Doit être 0 ou une somme d'épaisseurs de cales_epaisseurs.",
        ),

        "cache_epaisseur": Param(
            10.0, "mm",
            "Épaisseur du cache / bouchon affleurant du port meuble (état fermé).",
            plage=(4.0, 20.0), statut=VAL,
            justification="Aligné sur le retrait de discrétion Incognito (10 mm) pour un cache invisible à l'état fermé.",
            source="incognito/incognito/parametres.py (retrait_min_ancre_sous_surface_mm = 10 ; cache affleurant)",
        ),
        "etat_deploiement": Param(
            0, "", "0 = port meuble fermé (cache en place), 1 = déployé (ergot accessible).",
            plage=(0, 1), statut=LIB, utilise_par=("interfaces",),
            justification="Même convention que inc_etat_deploiement.",
            source="incognito/incognito/grammaires/banquette.py (Etat.FERMEE=0, DEPLOYEE=1)",
        ),
    },

    "collecteur_urine": {
        "forme": Param(
            "entonnoir", "texte",
            "Forme de la partie de collecte (l'entonnoir se déverse dans le réservoir ou vers le point bas).",
            choix=["entonnoir", "gouttiere", "reservoir_integre"], statut=VAL,
            utilise_par=("hygiene",),
            justification="L'entonnoir concentre vers un orifice, plus facile à rincer qu'une gouttière longue. "
                          "La gouttière convient à un banc allongé (Equinox). Le réservoir intégré diminue les joints mais complique le lavage. "
                          "Paramétrable ; défaut entonnoir + réservoir amovible.",
        ),
        "vidange": Param(
            "reservoir_amovible", "texte",
            "Mode de vidange (paramétrable).",
            choix=["reservoir_amovible", "gravite_point_bas", "raccord_npt"], statut=VAL,
            utilise_par=("hygiene",),
            justification="Défaut : réservoir amovible — on l'emporte vers un point d'eau, on le lave, aucun raccordement au bâtiment. "
                          "La gravité vers un point bas est plus simple en usage mais exige une pente continue et un rejet prévu. "
                          "Le raccord 1\" NPT (déjà au catalogue Incognito) peut servir de vidange fixe ; c'est un gros Ø pour de l'urine (utilisable, pas obligatoire). "
                          "Recommandation : réservoir amovible, NPT en option de fond de réservoir pour une vidange assistée.",
        ),
        "volume_utile": Param(
            500.0, "mL",
            "Volume utile de collecte (une miction adulte typique + marge).",
            plage=(300.0, 2000.0), statut=VAL, utilise_par=("hygiene",),
            justification="Ordre de grandeur sourcé : vidange typique 200–300 mL (UnityPoint, Dr Newton) ou 200–350 mL le jour et 300–400 mL au lever (synthèse type journal mictionnel). "
                          "Capacité vésicale max souvent citée ≈ 400–600 mL, 500 mL (StatPearls NCBI). "
                          "Défaut 500 mL : couvre une miction typique et une grande première miction, sans viser deux cycles. À valider selon l'usage.",
            source="UnityPoint Health, « What Causes Frequent Urination… » (typical output 200–300 cc, max 500–600 cc) ; "
                   "NCBI StatPearls « Physiology, Urination » NBK562181 (first sensation 150–250 mL, fullness 350–400 mL, max ~500 mL) ; "
                   "Kettering Health (capacity 400–600 mL, urge 200–300 mL)",
        ),
        "coefficient_anti_debordement": Param(
            1.2, "",
            "Volume total du réservoir = volume utile × ce coefficient (garde anti-débordement / anti-éclaboussures).",
            plage=(1.05, 2.0), statut=VAL,
            justification="20 % de garde : 500 × 1,2 = 600 mL. Hypothèse Aboutissants, à valider.",
        ),
        "pente_min": Param(
            0.02, "",
            "Pente minimale d'écoulement (2 %, soit 1:50) des surfaces mouillées vers l'orifice.",
            plage=(0.01, 0.10), statut=VAL,
            justification="Ordre de grandeur des collecteurs d'eaux usées à petit diamètre (EN 12056-2, pente courante 1:50). "
                          "Pour une gouttière ouverte courte, 2 % est un minimum ; 3–5 % rince mieux. À valider au prototype (eau savonneuse).",
            source="EN 12056-2 (pentes de canalisations d'eaux usées, ordre de grandeur 1:50) — pas une cote de meuble.",
        ),
        "rayon_interieur_min": Param(
            5.0, "mm",
            "Rayon intérieur minimal des angles mouillés (rinçage, aucun recoin vif).",
            plage=(3.0, 20.0), statut=VAL,
            justification="Plus généreux que le rayon peau de 3 mm (Entrave) : une arête vive retient le film liquide. 5 mm permet un passage de brosse.",
        ),
        "materiau_contact": Param(
            "inox_316", "texte",
            "Matériau de toutes les pièces en contact avec l'urine.",
            choix=["inox_316", "pp_homopolymere", "pehd"], statut=VAL,
            justification="Inox 316L : référence de gamme, nettoyage agressif, non poreux. PP / PE-HD : alternative polymère non poreuse, bonne tenue urée/ammoniac, plus légère, à valider au contact des désinfectants choisis. "
                          "Cuir et sangle exclus de la zone humide (habillage seulement).",
        ),
        "joint": Param(
            "epdm", "texte", "Matière des joints d'étanchéité (couvercle, raccord, réservoir).",
            choix=["epdm", "silicone_platine", "fkm"], statut=VAL,
            justification="EPDM : bonne tenue à l'eau, à l'ammoniac dilué et à beaucoup de désinfectants. Silicone platine : hygiène, démoulage. FKM : spectre chimique plus large, plus cher.",
        ),
        "couvercle": Param(
            True, "bool", "Couvercle du réservoir (limitation des odeurs et des éclaboussures).",
            statut=VAL,
        ),
        "siphon": Param(
            True, "bool",
            "Garde d'eau type siphon sur la vidange (surtout si raccord fixe / gravité).",
            statut=VAL,
            justification="Utile pour un raccord NPT ou une descente gravitaire. Moins critique sur un réservoir amovible fermé, mais recommandé si le bouchon de vidange reste ouvert vers l'air.",
        ),
        "siphon_garde_eau": Param(
            50.0, "mm", "Hauteur de garde d'eau du siphon.",
            plage=(30.0, 80.0), statut=VAL,
            justification="Ordre de grandeur des siphons d'appareils sanitaires (EN 274, garde souvent 50 mm). À valider. Inutile si siphon=False.",
            source="EN 274 (siphons d'appareils, garde d'eau typique 50 mm) — ordre de grandeur, pas une cote de meuble.",
        ),
        "deploiement": Param(
            "tiroir", "texte",
            "Mode de déploiement discret (rien de visible à l'état fermé).",
            choix=["tiroir", "panneau_basculant"], statut=VAL,
            justification="Incognito ouvre un coffre (couvercle ~95°) et obture des lumières de fond par des trappes affleurantes ; le dossier basculant a été écarté. "
                          "Pour un collecteur, un tiroir bas ou un panneau basculant sous le meuble reprend cette logique d'affleurement, sans modifier la structure des meubles (module rapporté).",
            source="incognito/docs/banquette.md (trappes affleurantes, alternative dossier basculant écartée) ; incognito/grammaires/banquette.py",
        ),
        "etat_deploiement": Param(
            0, "", "0 = fermé (invisible), 1 = déployé.",
            plage=(0, 1), statut=LIB,
        ),
        "cuir_sangle_zone_humide": Param(
            False, "bool",
            "Interdit : cuir ou sangle en zone mouillée (la valeur doit rester False).",
            statut=IMP,
            justification="Habillage seulement, hors zone humide. Validation en erreur si True.",
        ),
    },
})


def effort_vide_theorique_tete(diametre_mm, pression_pa=101325.0):
    """Arrachement maximal théorique par le seul vide sous la tête du plug [N].

    Hypothèse d'un vide parfait sur la section circulaire de la tête (plafond physique).
    Le vide réel est très inférieur (fuites, poudre, lubrifiant).
    """
    r = float(diametre_mm) / 2000.0
    return pression_pa * (3.141592653589793 * r * r)


def diametre_tete_actif(params):
    """Diamètre de tête correspondant à la variante (brevet ou boutique)."""
    var = params.get("vac_u_lock.variante_tete")
    if var == "boutique":
        return params.get("vac_u_lock.plug_diametre_tete_boutique")
    return params.get("vac_u_lock.plug_diametre_tete_brevet")


def jeu_radial_variantes(params):
    """Jeu radial typique entre les deux variantes de tête [mm]."""
    a = params.get("vac_u_lock.plug_diametre_tete_brevet")
    b = params.get("vac_u_lock.plug_diametre_tete_boutique")
    if a is None or b is None:
        return None
    return abs(float(a) - float(b)) / 2.0


def _synchroniser_variante_tete(valeurs):
    """Aligne plug_diametre_tete_max sur la variante choisie."""
    vul = valeurs.get("vac_u_lock") if isinstance(valeurs, dict) else None
    if not isinstance(vul, dict):
        return
    var = vul.get("variante_tete", "brevet")
    if var == "boutique":
        d = vul.get("plug_diametre_tete_boutique", 27.94)
    else:
        d = vul.get("plug_diametre_tete_brevet", 31.75)
    if d is not None:
        vul["plug_diametre_tete_max"] = d


def _valider_vac_u_lock(params):
    pbs = []
    _synchroniser_variante_tete(params.valeurs)
    tete = params.get("vac_u_lock.plug_diametre_tete_max", None)
    tige = params.get("vac_u_lock.plug_diametre_tige_max", None)
    if tete is not None and tige is not None and tige >= tete:
        pbs.append(Probleme("erreur", "vac_u_lock.plug_diametre_tige_max",
                            "la tige (Ø %g) doit rester < tête (Ø %g) selon le brevet" % (tige, tete)))
    typ = params.get("vac_u_lock.verrouillage_type", "collier_serrage")
    actif = params.get("vac_u_lock.verrouillage_actif", True)
    if typ == "aucun":
        actif = False
    poussee = params.get("securite.charge_service_poussee_machine", 400.0)
    k = params.get("securite.coefficient_dynamique", 2.0)
    f = poussee * k
    if tete:
        vide = effort_vide_theorique_tete(tete)
        if (not actif or typ == "aucun") and f > vide:
            pbs.append(Probleme(
                "alerte", "vac_u_lock.verrouillage_actif",
                "Emboîtement seul : vide théorique max ≈ %.0f N < effort de calcul %.0f N "
                "(poussée nominale validée %g N × k_dyn %g). Verrouillage mécanique recommandé sur la machine."
                % (vide, f, poussee, k)))
    if typ == "goupille_transversale" and actif:
        pbs.append(Probleme(
            "alerte", "vac_u_lock.verrouillage_type",
            "La goupille transversale n'est pas compatible avec n'importe quel accessoire du marché "
            "(elle exigerait un perçage du gode). Réserver à des pièces dédiées."))
    if typ == "bague_baionnette" and actif:
        pbs.append(Probleme(
            "alerte", "vac_u_lock.verrouillage_type",
            "La baïonnette n'existe pas sur les accessoires Vac-U-Lock du marché (aucune source). "
            "Elle ne peut verrouiller qu'une bague rapportée, pas le gode lui-même."))
    fil = params.get("vac_u_lock.filetage_cote_machine")
    choix_fil = params.meta("vac_u_lock.filetage_cote_machine").choix
    if fil is not None and choix_fil and fil not in choix_fil:
        pbs.append(Probleme("erreur", "vac_u_lock.filetage_cote_machine",
                            "filetage %s hors catalogue vaculocks.com" % fil))
    mat = params.get("vac_u_lock.cales_materiau")
    if mat is not None and mat not in ("inox_316", "pp_homopolymere", "pehd"):
        pbs.append(Probleme("erreur", "vac_u_lock.cales_materiau",
                            "cales : matériau %s non admis (316L, PP ou PE-HD)" % mat))
    jeu = jeu_radial_variantes(params)
    ep = params.get("vac_u_lock.cales_epaisseur_en_place")
    epaisseurs = params.get("vac_u_lock.cales_epaisseurs") or []
    if ep is not None and ep > 0 and epaisseurs:
        # Somme approchable à 0,05 mm près par des éléments du jeu (répétables).
        # On n'impose pas une combinaison unique.
        if ep < min(epaisseurs) - 1e-9 and ep != 0:
            pbs.append(Probleme(
                "alerte", "vac_u_lock.cales_epaisseur_en_place",
                "épaisseur en place %g mm inférieure à la plus petite cale du jeu %s"
                % (ep, epaisseurs)))
    return pbs


def _valider_collecteur(params):
    pbs = []
    if params.get("collecteur_urine.cuir_sangle_zone_humide") is True:
        pbs.append(Probleme(
            "erreur", "collecteur_urine.cuir_sangle_zone_humide",
            "cuir / sangle interdits en zone humide (habillage seulement)"))
    pente = params.get("collecteur_urine.pente_min", 0)
    if pente is not None and pente < 0.01 - 1e-12:
        pbs.append(Probleme("erreur", "collecteur_urine.pente_min",
                            "pente %g < 1 %% : risque de stagnation" % pente))
    vol = params.get("collecteur_urine.volume_utile")
    k = params.get("collecteur_urine.coefficient_anti_debordement")
    if vol is not None and vol < 200:
        pbs.append(Probleme("alerte", "collecteur_urine.volume_utile",
                            "volume %g mL inférieur à une miction typique basse (~200 mL)" % vol))
    if vol is not None and k is not None and vol * k < vol:
        pbs.append(Probleme("erreur", "collecteur_urine.coefficient_anti_debordement",
                            "le coefficient doit être ≥ 1"))
    if params.get("collecteur_urine.siphon") and not params.get("collecteur_urine.siphon_garde_eau"):
        pbs.append(Probleme("erreur", "collecteur_urine.siphon_garde_eau",
                            "siphon demandé sans garde d'eau"))
    return pbs


# ---------------------------------------------------------------------------
# Cadres de contention modulaires (la structure est l'aboutissant)
# ---------------------------------------------------------------------------
SCHEMA.update({
    "cadre_modulaire": {
        "typologie": Param(
            "cadre_sol", "texte",
            "Typologie du cadre : mural, au sol, ou poutre suspendue.",
            choix=["cadre_mural", "cadre_sol", "poutre_suspendue"], statut=VAL,
            utilise_par=("cadres",),
            justification="Trois typologies où l'aboutissant *est* la structure (poutres, montants), "
                          "avec ports Vac-U-Lock et 1 pouce NPT répartis. Le cadre au sol est autonome "
                          "(défaut) : il ne dépend pas d'un support de bâtiment inconnu.",
        ),
        "largeur": Param(
            1200.0, "mm",
            "Largeur hors-tout du cadre (portée des traverses), paramètre d'aboutissant.",
            plage=(600.0, 2500.0), statut=VAL, utilise_par=("cadres",),
            justification="Ordre de grandeur d'un portique / d'une traverse d'appui (pas une cote de meuble). "
                          "À caler selon la pièce. Une portée plus grande augmente le moment de flexion "
                          "(M = F·L/4 en travée simple).",
        ),
        "profondeur": Param(
            800.0, "mm",
            "Profondeur hors-tout du cadre au sol (écartement des portiques). Ignorée pour la poutre seule.",
            plage=(400.0, 2000.0), statut=VAL, utilise_par=("cadres",),
            justification="Emprise au sol d'un cadre autoportant, distincte des meubles. Sert aussi à juger "
                          "la stabilité (coefficient de renversement 1,5 déjà au vocabulaire).",
        ),
        "hauteur": Param(
            2000.0, "mm",
            "Hauteur des montants (cadre mural ou au sol).",
            plage=(1200.0, 2500.0), statut=VAL, utilise_par=("cadres",),
            justification="Hauteur d'un portique d'adulte debout, paramètre d'aboutissant à valider, "
                          "pas une cote de meuble.",
        ),
        "longueur_poutre": Param(
            1800.0, "mm",
            "Longueur de la poutre suspendue (entre appuis / suspentes).",
            plage=(800.0, 3000.0), statut=VAL, utilise_par=("cadres",),
            justification="Portée typique entre deux suspentes. Plus la portée est grande, plus la section "
                          "doit augmenter (flexion). Ne préjuge pas de l'entraxe réel des solives (TODO).",
        ),
        "section_montant_cote": Param(
            80.0, "mm",
            "Côté d'un montant carré (section aboutissant).",
            plage=(40.0, 160.0), statut=VAL, utilise_par=("cadres",),
            justification="80×80 mm : compromis rigidité / encombrement / usinage des tenons (règle du tiers → tenon 27 mm). "
                          "Ce n'est pas la section 40×40 des tubes Equinox (autre pièce).",
        ),
        "section_poutre_base": Param(
            80.0, "mm",
            "Base (largeur) de la section de poutre.",
            plage=(40.0, 200.0), statut=VAL, utilise_par=("cadres",),
            justification="Alignée sur le montant par défaut pour des assemblages tenon-mortaise réguliers.",
        ),
        "section_poutre_hauteur": Param(
            80.0, "mm",
            "Hauteur de la section de poutre (fibre pour la flexion).",
            plage=(40.0, 250.0), statut=VAL, utilise_par=("cadres",),
            justification="80 mm suffit en travée 1200 mm sous F_dyn de retenue à σ_adm 14 MPa (frêne/chêne). "
                          "Pour une poutre suspendue plus longue ou sous k_dyn·m·g (poids entier), augmenter "
                          "cette hauteur (le module W = b·h²/6).",
        ),
        "essence": Param(
            "frene", "texte",
            "Essence des poutres / montants (catalogue aboutissants, hypothèses de flexion).",
            choix=["frene", "chene", "noyer"], statut=VAL, utilise_par=("cadres",),
            justification="Frêne par défaut comme Equinox. σ_adm flexion 14 MPa (frêne, chêne) ou 12 MPa (noyer) : "
                          "hypothèses de conception déjà au catalogue, pas un calcul Eurocode 5.",
        ),
        "jonction": Param(
            "tenon_clavete", "texte",
            "Type de jonction montant / traverse.",
            choix=["tenon_mortaise", "queue_d_aronde", "tenon_clavete", "raccord_metallique"],
            statut=VAL, utilise_par=("cadres",),
            justification="Défaut : tenon traversant à clé (tusk tenon, Néogothique) — démontable, peu de métal apparent, "
                          "compromis modularité / discrétion / solidité. Le tenon-mortaise collé et la queue d'aronde "
                          "sont plus discrets et souvent plus rigides, mais peu reconfigurables. Le raccord métallique "
                          "(platine / barillet M8) maximise la modularité au détriment de la discrétion.",
            source="equinox/equinox/catalogues/attaches.py (tenon_mortaise, règle du tiers) ; "
                   "neogothique/neogothique/catalogues/attaches.py (tenon_traversant_clavete, démontable).",
        ),
        "pas_ports": Param(
            200.0, "mm",
            "Espacement nominal des ports (Vac-U-Lock et/ou 1 pouce NPT) le long des membrures.",
            plage=(80.0, 600.0), statut=VAL, utilise_par=("cadres",),
            justification="Assez serré pour offrir plusieurs positions, assez large pour laisser de la matière "
                          "entre plots. Les ports sont portés par des plots rapportés (on ne perce pas la fibre "
                          "tendue de la poutre à Ø 33 mm).",
        ),
        "ports_vac_u_lock": Param(
            True, "bool",
            "Répartir des ports Vac-U-Lock (ergot) sur la structure.",
            statut=LIB, utilise_par=("cadres",),
            justification="Cœur du brief : ports standard de marché, en plus des NPT et des anneaux.",
        ),
        "ports_npt": Param(
            True, "bool",
            "Répartir des raccords 1 pouce NPT sur la structure.",
            statut=LIB, utilise_par=("cadres",),
            justification="Interface distincte du Vac-U-Lock (arrière de port, vidange, accessoire fileté).",
        ),
        "nombre_suspentes": Param(
            2, "",
            "Nombre de suspentes de la poutre suspendue.",
            plage=(2, 6), statut=VAL, utilise_par=("cadres",),
            justification="Deux appuis minimum (travée simple). Au-delà, la descente de charge par suspente diminue "
                          "mais les appuis doivent tous exister dans le bâtiment (TODO).",
        ),
        "capacite_support_mur": Param(
            None, "N",
            "Capacité de calcul du support mural (chevilles, ossature, béton…).",
            statut=TODO, utilise_par=("cadres",),
            justification="TODO : le support du bâtiment n'est pas connu des scripts Aboutissants. "
                          "Ne pas inventer une CMU de cheville ou d'voile. Le cadre mural ne doit pas être "
                          "installé tant que cette valeur n'est pas relevée sur place et validée.",
        ),
        "capacite_support_plafond": Param(
            None, "N",
            "Capacité de calcul du support de plafond / solive pour une poutre suspendue.",
            statut=TODO, utilise_par=("cadres",),
            justification="TODO : solives, entraxe, section, bois, ancrage — inconnus. Une poutre suspendue "
                          "reprend des efforts de l'ordre de k_dyn·m·g (hypothèse poids entier) voire davantage "
                          "en cisaillement de solive. Sans relevé, pas de feu vert.",
        ),
        "entraxe_solives": Param(
            None, "mm",
            "Entraxe réel des solives du local (si poutre suspendue).",
            statut=TODO, utilise_par=("cadres",),
            justification="TODO : inconnu tant que le local n'est pas relevé. La longueur de poutre ne doit pas "
                          "être confondue avec cet entraxe.",
        ),
        "section_solive": Param(
            None, "texte",
            "Section et essence des solives du local (description).",
            statut=TODO, utilise_par=("cadres",),
            justification="TODO : support de bâtiment inconnu. Ne pas inventer de 63×175 ou équivalent.",
        ),
    },
})


def _valider_cadre(params):
    pbs = []
    typ = params.get("cadre_modulaire.typologie")
    if typ == "poutre_suspendue" and params.get("cadre_modulaire.capacite_support_plafond") is None:
        pbs.append(Probleme(
            "todo", "cadre_modulaire.capacite_support_plafond",
            "Poutre suspendue : capacité du support de plafond / solive inconnue — pas d'installation sans relevé."))
    if typ == "cadre_mural" and params.get("cadre_modulaire.capacite_support_mur") is None:
        pbs.append(Probleme(
            "todo", "cadre_modulaire.capacite_support_mur",
            "Cadre mural : capacité du support mural inconnue — pas d'installation sans relevé."))
    if typ == "poutre_suspendue":
        h = params.get("cadre_modulaire.section_poutre_hauteur")
        b = params.get("cadre_modulaire.section_poutre_base")
        L = params.get("cadre_modulaire.longueur_poutre")
        if h and b and L and h < 80 and L > 1500:
            pbs.append(Probleme(
                "alerte", "cadre_modulaire.section_poutre_hauteur",
                "Poutre longue (%g mm) et section basse (h=%g) : vérifier la flexion sous k_dyn·m·g."
                % (L, h)))
    pas = params.get("cadre_modulaire.pas_ports")
    if pas is not None and pas < params.get("vac_u_lock.plug_longueur", 76.2):
        pbs.append(Probleme(
            "alerte", "cadre_modulaire.pas_ports",
            "Pas de ports %g mm inférieur à la longueur d'ergot : risque de chevauchement." % pas))
    return pbs
