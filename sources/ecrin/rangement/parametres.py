# -*- coding: utf-8 -*-
"""Couche 1 - Parametres globaux partages de la gamme Rangement.

Chaque parametre est une feuille ``Param`` du schema ``SCHEMA`` : valeur par
defaut, unite, role, plage, choix, statut, modules utilisateurs, SOURCE et
justification.

Statuts :

- ``repris``    : valeur reprise telle quelle d'une autre gamme ; ``source``
  donne le fichier et la cle d'origine (obligatoire) ;
- ``a_valider`` : valeur proposee pour Rangement, sans equivalent ailleurs ou
  choix a trancher par Fabien (« À VALIDER ») ; ``justification`` obligatoire ;
- ``derive``    : recalcule par ``rangement.regles`` a partir d'autres valeurs ;
- ``todo``      : inconnue (``valeur=None``) - a relever, rien n'est invente ;
- ``libre``     : nom, prefixe...

Unites internes : mm, kg, kg/m, kg/m2, N, MPa, deg, % (jamais de cm ici).

Usage ::

    from rangement.parametres import Parametres
    p = Parametres.pour_typologie("ratelier_mural")
    p.get("ports.pas_ports")                    # 200.0
    p.set("bois.essence", "noyer")
    problemes = p.valider()
    p.exporter_user_parameters(design)          # dans Fusion uniquement
"""

import copy
import json
import os
import re

from . import sources as S
from .catalogues import bois as _bois, garnissage as _garn, quincaillerie as _quin
from .catalogues import systemes as _sys, jonctions as _jonc

_MANQUANT = object()

#: Fichier JSON optionnel d'overrides utilisateur ({"commun": {...}, "typologies": {...}}).
CHEMIN_JSON = os.path.join(os.path.dirname(__file__), "parametres_rangement.json")
#: Copie de reference des valeurs par defaut (regeneree par outils/generer_docs.py).
CHEMIN_DEFAUTS = os.path.join(os.path.dirname(__file__), "parametres_rangement.defauts.json")

REP, VAL, DER, TODO, LIB = "repris", "a_valider", "derive", "todo", "libre"
STATUTS = (REP, VAL, DER, TODO, LIB, "impose")


class Param(object):
    """Description d'un parametre (feuille du schema)."""

    __slots__ = ("valeur", "unite", "role", "plage", "choix", "statut", "utilise_par", "source", "justification")

    def __init__(self, valeur, unite, role, plage=None, choix=None, statut=LIB, utilise_par=(),
                 source="", justification=""):
        self.valeur, self.unite, self.role = valeur, unite, role
        self.plage, self.choix, self.statut = plage, choix, statut
        self.utilise_par = tuple(utilise_par)
        self.source, self.justification = source, justification

    def __repr__(self):
        return "Param(%r %s, %s)" % (self.valeur, self.unite, self.statut)


TYPOLOGIES = ("ratelier_mural", "armoire_accessoires", "coffre", "support_exposition", "armoire_verrouillable")
TOUS = TYPOLOGIES
RAT = ("ratelier_mural",)
CAISSONS = ("armoire_accessoires", "coffre", "support_exposition", "armoire_verrouillable")

_ESS = sorted(_bois.ESSENCES)
_SYS = {f: _sys.par_famille(f) for f in _sys.FAMILLES}

# ---------------------------------------------------------------------------
# SCHEMA : le vocabulaire Rangement
# ---------------------------------------------------------------------------
SCHEMA = {
    "gamme": {
        "nom": Param("Rangement", "texte", "Nom de la gamme (prefixe des composants Fusion)."),
        "prefixe_fusion": Param("ran_", "texte", "Prefixe des User Parameters crees dans Fusion.",
                                statut=VAL, justification="Aligne sur eq_ / neo_ / inc_ / abo_ / tan_ (Tantra) / gc_ (GammeCuir)."),
    },
    "modules": {
        "pas_trous": Param(32.0, "mm", "Entraxe vertical des rangees de trous (taquets, charnieres) : trame de la gamme.",
                           (16.0, 64.0), statut=VAL, utilise_par=TOUS,
                           justification="Systeme 32 (standard industriel europeen) ; absent des autres gammes."),
        "recul_trous_avant": Param(37.0, "mm", "Distance du chant avant a l'axe de la premiere rangee de trous.",
                                   (20.0, 100.0), statut=VAL, utilise_par=CAISSONS,
                                   justification="Valeur usuelle du systeme 32 ; a confirmer avec les charnieres retenues."),
        "diametre_trous_taquets": Param(5.0, "mm", "Diametre des trous de taquets d'etageres.", (3.0, 8.0),
                                        statut=VAL, utilise_par=CAISSONS,
                                        justification="Taquets O5 courants ; aucun taquet dans les autres gammes."),
        "module_largeur": Param(600.0, "mm", "Largeur d'un module (ratelier mural, travee d'armoire).",
                                (300.0, 1200.0), statut=VAL, utilise_par=TOUS,
                                justification="600 mm : 2 a 4 crochets ou 2 ports au pas de 200 par module ; portee "
                                              "de barre courte (flexion faible). Proposition."),
        "module_hauteur": Param(320.0, "mm", "Hauteur d'un module (multiple du pas de trous).", (160.0, 960.0),
                                statut=VAL, utilise_par=TOUS,
                                justification="10 x 32 mm : trame verticale commune aux rateliers et aux armoires."),
        "hauteur_armoire": Param(1800.0, "mm", "Hauteur hors-tout des armoires.", (900.0, 2200.0), statut=VAL,
                                 utilise_par=("armoire_accessoires", "armoire_verrouillable"),
                                 justification="Accessible sans escabeau ; au-dela de ~1600 mm fixation anti-basculement "
                                               "obligatoire (verifiee par regles)."),
        "profondeur_armoire": Param(450.0, "mm", "Profondeur hors-tout des armoires.", (300.0, 650.0), statut=VAL,
                                    utilise_par=("armoire_accessoires", "armoire_verrouillable"),
                                    justification="Accepte des glissieres de 400 mm et des paddles a plat. Proposition."),
        "profondeur_coffre": Param(450.0, "mm", "Profondeur hors-tout des coffres.", (300.0, 700.0), statut=VAL,
                                   utilise_par=("coffre",), justification="Proposition (coffre-banc)."),
        "hauteur_coffre": Param(440.0, "mm", "Hauteur hors-tout des coffres (peut servir d'assise).",
                                (300.0, 600.0), statut=REP, utilise_par=("coffre",),
                                source=S.EQ_PARAM + " (OVERRIDES_TYPOLOGIE tabouret : dimensions.hauteur_assise 440)"),
    },
    "panneaux": {
        "epaisseur_caisson": Param(18.0, "mm", "Epaisseur des cotes, dessus, dessous des caissons.", (15.0, 40.0),
                                   statut=REP, utilise_par=CAISSONS,
                                   source=S.INC_PARAM + " (ParametresDiscretion.epaisseur_min_paroi_visible_mm = 18)"),
        "epaisseur_porte": Param(22.0, "mm", "Epaisseur des portes et couvercles.", (16.0, 40.0), statut=REP,
                                 utilise_par=CAISSONS,
                                 source=S.INC_FIX + " (CHARNIERE_SOSS : epaisseur_min_bois 22)"),
        "epaisseur_etagere": Param(22.0, "mm", "Epaisseur des etageres massives.", (15.0, 40.0), statut=VAL,
                                   utilise_par=CAISSONS, justification="Proposition ; la fleche est verifiee par regles."),
        "epaisseur_fond": Param(8.0, "mm", "Epaisseur des fonds (contreplaque en rainure).", (4.0, 18.0),
                                statut=VAL, utilise_par=CAISSONS, justification="Proposition."),
        "epaisseur_panneau_mural": Param(22.0, "mm", "Epaisseur du panneau dorsal des rateliers.", (15.0, 40.0),
                                         statut=VAL, utilise_par=RAT,
                                         justification="Recoit inserts M8 (20 mm), consoles tenonnees et douilles NPT."),
        "epaisseur_support_garni": Param(18.0, "mm", "Support contreplaque bouleau sous un fond garni de cuir.",
                                         (9.0, 30.0), statut=REP, utilise_par=CAISSONS,
                                         source=S.EQ_PARAM + " (garnissage.epaisseur_support = 18)"),
        "lamage_lecteur": Param(6.0, "mm", "Amincissement local au dos de la porte au droit d'un lecteur RFID / "
                                "verrou magnetique.", (0.0, 15.0), statut=VAL, utilise_par=CAISSONS,
                                justification="Permet de garder une porte de 22 mm (charnieres Soss) tout en restant "
                                              "sous l'epaisseur de lecture ; le bois restant doit garder le retrait "
                                              "de discretion de 10 mm (Incognito)."),
    },
    "bois": {
        "essence": Param("chene", "texte", "Cle de l'essence dans catalogues.bois.", choix=_ESS, statut=VAL,
                         utilise_par=TOUS, source=S.INC_PARAM + " (ESSENCE_DEFAUT = CHENE) ; " + S.NEO_PARAM,
                         justification="Chene : defaut d'Incognito, de Neogothique et de Tantra (essence de reference), "
                                       "defini dans les 5 gammes a meubles. Equinox est en frene. "
                                       "Choix a trancher par Fabien."),
        "finition": Param("cire_naturelle", "texte", "Cle de la finition dans catalogues.bois.FINITIONS_BOIS.",
                          choix=sorted(_bois.FINITIONS_BOIS), statut=VAL, utilise_par=TOUS,
                          source=S.NEO_BOIS + " (FINITIONS_BOIS)",
                          justification="Compatible avec toutes les essences ; l'interieur des armoires peut "
                                        "passer en vernis_pu_mat (Tantra : nettoyabilite 5/5, lessivable)."),
        "humidite_cible": Param(10.0, "%", "Humidite du bois a la mise en oeuvre (interieur chauffe).", (6.0, 15.0),
                                statut=REP, utilise_par=TOUS, source=S.EQ_PARAM + " (bois.humidite_cible = 10)"),
    },
    "cuir": {
        "famille": Param("cuir_classique_pleine_fleur", "texte", "Famille de cuir / garnissage (catalogues.garnissage).",
                         choix=sorted(_garn.GARNISSAGES), statut=VAL, utilise_par=TOUS,
                         source=S.EQ_GARN + " (GARNISSAGE_REFERENCE)",
                         justification="Cuir de reference Equinox (noir, cognac, havane, vert bouteille, bleu nuit), "
                                       "assorti a la vachette vegetale de GammeCuir (memes teintes + tan, "
                                       "bordeaux, brun fonce)."),
        "teinte": Param("noir", "texte", "Teinte du cuir ; doit exister dans la famille (catalogues.garnissage.TEINTES_CUIR).",
                        choix=sorted(_garn.TEINTES_CUIR), statut=VAL, utilise_par=TOUS,
                        source=S.EQ_GARN + " ; " + S.NEO_GARN + " ; " + S.INC_PARAM + " ; " + S.TANTRA_PARAM
                               + " ; " + S.GC_CUIRS,
                        justification="Noir : seule teinte presente dans les 5 gammes (Equinox, Neogothique, "
                                      "Incognito, Tantra, GammeCuir) ; cognac est dans 4 (pas Neogothique)."),
        "epaisseur": Param(1.8, "mm", "Epaisseur du cuir (derivee de la famille).", (0.5, 10.0), statut=DER,
                           utilise_par=TOUS, source=S.EQ_GARN + " (epaisseur_matiere)"),
    },
    "quincaillerie": {
        "metal": Param("inox_316", "texte", "Metal des crochets, barres, platines (catalogues.quincaillerie).",
                       choix=sorted(_quin.METAUX), statut=REP, utilise_par=TOUS,
                       source=S.EQ_PARAM + " (inox.nuance = inox_316) ; " + S.ABO_MAT),
        "finition_metal": Param("inox_electropoli", "texte", "Finition des pieces metalliques.",
                                choix=sorted(_quin.FINITIONS_METAL), statut=VAL, utilise_par=TOUS,
                                source=S.ABO_MAT + " (inox_316.hygiene)",
                                justification="Electropolissage/passivation conseilles par Aboutissants pour l'hygiene."),
        "filetage_insert": Param("M8", "texte", "Filetage des inserts (crochets, consoles, platines).",
                                 choix=["M6", "M8", "M10"], statut=REP, utilise_par=TOUS,
                                 source=S.EQ_PARAM + " (jonctions.filetage_insert) ; " + S.ABO_PARAM),
        "longueur_insert": Param(20.0, "mm", "Longueur des inserts filetes (20 si densite >= 650 kg/m3, sinon 25).",
                                 (10.0, 40.0), statut=DER, utilise_par=TOUS,
                                 source=S.EQ_ATT + " (insert_filete_m8.dimensionnement)"),
    },
    "charges": {
        "charge_crochet": Param(3.0, "kg", "Masse de service suspendue a un crochet.", (0.5, 20.0), statut=VAL,
                                utilise_par=TOUS,
                                justification="Une paire de menottes acier ou un paddle : < 1,5 kg ; marge x2. Proposition."),
        "charge_lineaire_barre": Param(10.0, "kg/m", "Charge repartie de service sur une barre de suspension.",
                                       (1.0, 60.0), statut=VAL, utilise_par=TOUS,
                                       justification="Martinets, cravaches, sangles serres sur la barre. Proposition."),
        "charge_etagere": Param(40.0, "kg/m2", "Charge surfacique de service des etageres.", (5.0, 200.0),
                                statut=VAL, utilise_par=CAISSONS,
                                justification="Accessoires et cordes, pas de livres. Proposition a recouper avec "
                                              "EN 16121 / EN 16122 (non consultees)."),
        "charge_tiroir": Param(15.0, "kg", "Charge de service d'un tiroir.", (2.0, 60.0), statut=VAL,
                               utilise_par=CAISSONS, justification="Proposition ; a comparer a la fiche des glissieres."),
        "effort_accidentel": Param(300.0, "N", "Traction accidentelle ponctuelle (on se retient a une barre ou un crochet).",
                                   (0.0, 2000.0), statut=VAL, utilise_par=TOUS,
                                   justification="~30 kg : chute evitee de justesse. Verifiee en ALERTE (deformation), "
                                                 "un ratelier n'est PAS un point d'ancrage de personne."),
        "longueur_instrument_suspendu": Param(500.0, "mm", "Longueur pendante typique sous une barre (martinet, sangle).",
                                              (100.0, 1200.0), statut=VAL, utilise_par=RAT,
                                              justification="Proposition ; sert a eviter que les instruments masquent "
                                                            "les crochets."),
    },
    "securite": {
        "coefficient_dynamique": Param(2.0, "", "Majoration des charges de service (accrochage brusque, choc).",
                                       (1.0, 4.0), statut=REP, utilise_par=TOUS,
                                       source=S.EQ_PARAM + " (securite.coefficient_dynamique = 2,0)"),
        "securite_metal": Param(1.8, "", "Coefficient de securite sur la limite elastique des metaux.", (1.2, 4.0),
                                statut=REP, utilise_par=TOUS, source=S.EQ_PARAM + " (securite.securite_metal = 1,8)"),
        "fleche_admissible": Param(300.0, "", "Fleche admissible = portee / ce nombre.", (100.0, 1000.0),
                                   statut=REP, utilise_par=TOUS, source=S.EQ_PARAM + " (securite.fleche_admissible = 300)"),
        "securite_renversement": Param(1.5, "", "Rapport mini moment stabilisant / renversant (armoires).",
                                       (1.0, 3.0), statut=REP, utilise_par=CAISSONS,
                                       source=S.EQ_PARAM + " (securite.securite_renversement = 1,5)"),
    },
    "discretion": {
        "niveau": Param("discret", "texte", "Niveau de discretion vise a l'etat ferme.",
                        choix=["apparent", "discret", "invisible"], statut=VAL, utilise_par=TOUS,
                        justification="'invisible' applique les regles Incognito (zero cuir, zero ferrure visibles)."),
        "retrait_min_ancre": Param(10.0, "mm", "Bois mini entre une piece metallique noyee et une surface visible.",
                                   (0.0, 30.0), statut=REP, utilise_par=TOUS,
                                   source=S.INC_PARAM + " (retrait_min_ancre_sous_surface_mm = 10)"),
        "epaisseur_cache": Param(10.0, "mm", "Epaisseur des caches bois affleurants (ports, inserts).", (4.0, 20.0),
                                 statut=REP, utilise_par=TOUS,
                                 source=S.INC_FIX + " (CACHE_AFFLEURANT) ; " + S.ABO_PARAM + " (vac_u_lock.cache_epaisseur)"),
        "jeu_mecanique": Param(2.0, "mm", "Jeu fonctionnel (portes, tiroirs, modules juxtaposes).", (0.5, 6.0),
                               statut=REP, utilise_par=TOUS, source=S.INC_PARAM + " (jeu_mecanique_mm = 2)"),
        "recul_mortaise_charniere": Param(8.0, "mm", "Distance mini mortaise de charniere invisible / chant visible.",
                                          (3.0, 20.0), statut=REP, utilise_par=CAISSONS,
                                          source=S.INC_PARAM + " (mortaise_charniere_recul_bord_mm = 8)"),
        "cuir_visible_ferme": Param(False, "bool", "Le cuir est-il visible meuble ferme ?", statut=VAL,
                                    utilise_par=TOUS, source=S.INC_PARAM + " (regle « zero cuir visible »)",
                                    justification="Incompatible avec niveau 'invisible' (regle Incognito)."),
    },
    "ports": {
        "vac_u_lock": Param(True, "bool", "Prevoir des ports Vac-U-Lock (ergot) compatibles Aboutissants.",
                            statut=VAL, utilise_par=TOUS, source=S.ABO_PARAM + " (cadre_modulaire.ports_vac_u_lock)",
                            justification="Exposer / ranger les accessoires Vac-U-Lock sur leur ergot."),
        "npt": Param(True, "bool", "Prevoir des douilles 1\" NPT femelles compatibles Aboutissants / Incognito.",
                     statut=VAL, utilise_par=TOUS, source=S.ABO_PARAM + " (cadre_modulaire.ports_npt)",
                     justification="La douille NPT recoit l'ergot Vac-U-Lock (arriere NPT male) ou un accessoire filete."),
        "plug_longueur": Param(76.2, "mm", "Longueur de l'ergot Vac-U-Lock (3 in).", (50.0, 100.0), statut=REP,
                               utilise_par=TOUS, source=S.ABO_PARAM + " (vac_u_lock.plug_longueur, brevet US 5,127,396)"),
        "plug_diametre_tete": Param(31.75, "mm", "Plus grand diametre de tete de l'ergot (1,25 in).", (25.0, 36.0),
                                    statut=REP, utilise_par=TOUS,
                                    source=S.ABO_PARAM + " (vac_u_lock.plug_diametre_tete_max ; a calibrer sur piece)"),
        "plug_diametre_tige": Param(19.05, "mm", "Plus grand diametre de tige de l'ergot (0,75 in).", (12.0, 25.0),
                                    statut=REP, utilise_par=TOUS, source=S.ABO_PARAM + " (vac_u_lock.plug_diametre_tige_max)"),
        "epaulement_epaisseur": Param(8.0, "mm", "Epaisseur de l'epaulement d'appui de l'ergot.", (4.0, 20.0),
                                      statut=REP, utilise_par=TOUS,
                                      source=S.ABO_PORT + " (EP_EPAULEMENT_ATELIER_MM = 8, hypothese d'atelier)"),
        "epaulement_diametre": Param(50.0, "mm", "Diametre de l'epaulement = max(tete + 16, 50).", (30.0, 80.0),
                                     statut=DER, utilise_par=TOUS, source=S.ABO_PORT + " (calculer_port : d_col)"),
        "montage_arriere": Param("npt_1_male", "texte", "Interface arriere de l'ergot (choix Aboutissants).",
                                 choix=["filete_machine", "npt_1_femelle", "npt_1_male", "filete_et_npt", "integré"],
                                 statut=VAL, utilise_par=TOUS,
                                 source=S.ABO_PARAM + " (vac_u_lock.montage_arriere ; defaut Aboutissants filete_machine)",
                                 justification="Sur un meuble, la douille femelle 1\" NPT est dans le bois : l'ergot "
                                               "porte un arriere MALE et la douille reste utilisable par les accessoires "
                                               "NPT (Incognito / housses). Le defaut Aboutissants (ergot filete M8 cote "
                                               "machine) est disponible via le systeme port_vac_u_lock_m8. A TRANCHER."),
        "filetage_ergot": Param("M8x1.25", "texte", "Filetage de l'ergot en montage filete (cote meuble).",
                                choix=["M6x1", "M8x1", "M8x1.25", "M10x1", "M10x1.5", "M12x1.75", "M16x2",
                                       "3/8-16 UNC", "3/4-10 UNC", "5/16-18 UNC", "1/4-20 UNC", "G1/8"],
                                statut=REP, utilise_par=TOUS,
                                source=S.ABO_PARAM + " (vac_u_lock.filetage_cote_machine) ; " + S.EQ_ATT
                                       + " (insert_filete_m8)"),
        "filetage_ergot_longueur": Param(16.0, "mm", "Longueur utile de la tige filetee de l'ergot.", (6.0, 40.0),
                                         statut=REP, utilise_par=TOUS,
                                         source=S.ABO_PARAM + " (vac_u_lock.filetage_cote_machine_longueur)"),
        "verrouillage_actif": Param(False, "bool", "Collier de serrage anti-arrachement sur l'ergot.", statut=VAL,
                                    utilise_par=TOUS, source=S.ABO_PARAM + " (vac_u_lock.verrouillage_actif)",
                                    justification="Aboutissants : desactivable sur un port meuble peu charge (exposition)."),
        "npt_diametre_exterieur": Param(33.401, "mm", "Diametre exterieur nominal du filetage 1\" NPT.", (33.3, 33.5),
                                        statut=REP, utilise_par=TOUS,
                                        source=S.ABO_PARAM + " (npt_1.diametre_exterieur) ; " + S.INC_HOUSSES + " (NPT_1_OD_MM)"),
        "npt_longueur_utile": Param(17.343, "mm", "Longueur utile de filet L2.", (17.2, 17.5), statut=REP,
                                    utilise_par=TOUS, source=S.ABO_PARAM + " (npt_1.longueur_utile_L2) ; " + S.INC_HOUSSES),
        "npt_longueur_totale": Param(25.006, "mm", "Longueur totale de filet L4 (filets imparfaits compris).",
                                     (24.9, 25.1), statut=REP, utilise_par=TOUS,
                                     source=S.ABO_PARAM + " (npt_1.longueur_totale_L4)"),
        "npt_depassement": Param(25.0, "mm", "Depassement recommande d'un embout NPT pour le visser a la main.",
                                 (18.0, 40.0), statut=REP, utilise_par=TOUS,
                                 source=S.INC_HOUSSES + " (NPT_1_DEPASSEMENT_RECOMMANDE_MM = 25)"),
        "npt_paroi_douille": Param(4.0, "mm", "Paroi radiale de la douille inox autour du filetage.", (2.0, 10.0),
                                   statut=REP, utilise_par=TOUS,
                                   source=S.ABO_PORT + " (d_npt = diametre_exterieur + 8)"),
        "fond_mini_douille": Param(6.0, "mm", "Bois mini sous le fond de la douille NPT.", (3.0, 20.0), statut=VAL,
                                   utilise_par=TOUS, justification="Proposition : evite de deboucher au dos du plot."),
        "paroi_bois_mini": Param(12.0, "mm", "Bois mini autour de la douille NPT (fendage).", (6.0, 30.0), statut=VAL,
                                 utilise_par=TOUS, justification="Proposition ; Aboutissants interdit de percer O33 dans "
                                                                 "une fibre tendue : plots rapportes."),
        "pas_ports": Param(200.0, "mm", "Entraxe des ports le long d'un module.", (80.0, 600.0), statut=REP,
                           utilise_par=TOUS, source=S.ABO_PARAM + " (cadre_modulaire.pas_ports = 200)"),
        "degagement_accessoire": Param(120.0, "mm", "Espace libre autour d'un ergot pour enfiler la base d'un accessoire.",
                                       (60.0, 300.0), statut=VAL, utilise_par=TOUS,
                                       justification="Proposition : bases d'accessoires du marche non cotees (Aboutissants TODO)."),
    },
    "pose": {
        "capacite_support_mur": Param(None, "N", "Capacite de calcul du support mural (chevilles, ossature).",
                                      statut=TODO, utilise_par=TOUS,
                                      source=S.ABO_PARAM + " (cadre_modulaire.capacite_support_mur = TODO)",
                                      justification="Support du batiment inconnu : releve sur place obligatoire."),
        "anti_basculement": Param(True, "bool", "Fixation murale anti-basculement des armoires hautes.", statut=VAL,
                                  utilise_par=("armoire_accessoires", "armoire_verrouillable"),
                                  justification="Obligatoire au-dela de ~1600 mm de haut (verifie par regles) ; "
                                                "ne reprend que de l'effort horizontal."),
    },
    "jonctions": {
        "type_caisson": Param("tourillons", "texte", "Jonction des panneaux de caisson (catalogues.jonctions).",
                              choix=sorted(_jonc.JONCTIONS), statut=VAL, utilise_par=CAISSONS,
                              source=S.INC_FIX + " (TOURILLON_10 : caissons)",
                              justification="Invisible et economique ; queues d'aronde pour tiroirs et coffres."),
        "diametre_tourillon": Param(8.0, "mm", "Diametre des tourillons = standard <= 0,5 x epaisseur caisson.",
                                    (6.0, 14.0), statut=DER, utilise_par=TOUS,
                                    source=S.NEO_ATT + " (ratio_diametre_max 0,5) ; " + S.EQ_ATT + " (diametres)"),
        "longueur_tourillon": Param(40.0, "mm", "Longueur des tourillons = 5 d.", (24.0, 80.0), statut=DER,
                                    utilise_par=TOUS, source=S.EQ_ATT + " (L = 5 d)"),
        "alesage_chant": Param(20.0, "mm", "Profondeur d'alesage cote chant = 2,5 d.", (12.0, 40.0), statut=DER,
                               utilise_par=TOUS, source=S.NEO_ATT + " (ratio_profondeur 2,5)"),
        "epaisseur_tenon": Param(7.0, "mm", "Tenon des consoles / cadres = 1/3 de la piece tenonnee "
                                 "(base : epaisseur_panneau_mural).", (4.0, 30.0), statut=DER, utilise_par=TOUS,
                                 source=S.EQ_ATT + " (tenon_mortaise : regle du tiers)"),
        "profondeur_mortaise": Param(17.6, "mm", "Mortaise = 0,8 x piece receveuse (base : epaisseur_panneau_mural).",
                                     (8.0, 60.0), statut=DER, utilise_par=TOUS,
                                     source=S.EQ_ATT + " (tenon_mortaise : 0,8 x section)"),
    },
    "systemes": {
        "tiroir": Param("glissiere_invisible_amortie", "texte", "Systeme de tiroir (catalogues.systemes).",
                        choix=_SYS["tiroir"], statut=VAL, utilise_par=CAISSONS,
                        justification="Discretion (silencieux, invisible) ; cout a arbitrer."),
        "porte": Param("battante_charniere_soss", "texte", "Systeme de porte.", choix=_SYS["porte"], statut=VAL,
                       utilise_par=CAISSONS, source=S.INC_FIX, justification="Invisible ferme, coherent Incognito."),
        "etagere": Param("taquets_systeme_32", "texte", "Systeme d'etagere.", choix=_SYS["etagere"], statut=VAL,
                         utilise_par=CAISSONS, justification="Reglage au pas de 32."),
        "crochet": Param("crochet_inox_double", "texte", "Type de crochet.", choix=_SYS["crochet"], statut=VAL,
                         utilise_par=TOUS, source=S.EQ_PARAM, justification="Inox 316 O8 (cotes Equinox)."),
        "barre": Param("tube_inox_20", "texte", "Type de barre de suspension.", choix=_SYS["barre"], statut=VAL,
                       utilise_par=TOUS, justification="Leger et hygienique ; dimension de tube À VALIDER."),
        "serrure": Param("serrure_came", "texte", "Systeme de verrouillage.", choix=_SYS["serrure"], statut=VAL,
                         utilise_par=CAISSONS, justification="Decision prioritaire de Fabien (cle / code / RFID)."),
        "port": Param("port_vac_u_lock_npt", "texte", "Type de port de fixation.", choix=_SYS["port"], statut=VAL,
                      utilise_par=TOUS, source=S.ABO_PARAM, justification="Ergot + douille NPT interchangeables."),
    },
}

#: Overrides par typologie (fusion profonde sur les valeurs par defaut).
OVERRIDES_TYPOLOGIE = {
    "ratelier_mural": {},
    "armoire_accessoires": {},
    "coffre": {"systemes": {"porte": "abattant_compas"}},
    "support_exposition": {"systemes": {"porte": "coulissante_rainure"}},
    "armoire_verrouillable": {"discretion": {"niveau": "invisible"},
                              "systemes": {"serrure": "serrure_electronique_rfid"}},
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


def valeurs_par_defaut():
    """Arbre des valeurs par defaut du SCHEMA (contenu du JSON de reference)."""
    return _valeurs_depuis_schema(SCHEMA)


class Probleme(object):
    """Probleme de validation : niveau ('erreur' | 'alerte' | 'todo'), chemin, message."""

    def __init__(self, niveau, chemin, message):
        self.niveau, self.chemin, self.message = niveau, chemin, message

    def __repr__(self):
        return "[%s] %s : %s" % (self.niveau, self.chemin, self.message)


class Parametres(object):
    """Jeu de parametres Rangement (valeurs + schema eventuellement etendu)."""

    def __init__(self, valeurs=None, schema=None):
        self.schema = copy.deepcopy(schema if schema is not None else SCHEMA)
        self.valeurs = _valeurs_depuis_schema(self.schema)
        self.typologie = None
        if valeurs:
            self.fusionner(valeurs)

    # -- construction -------------------------------------------------------
    @classmethod
    def pour_typologie(cls, typologie, overrides=None, json_utilisateur=True):
        """Defauts + overrides de typologie + JSON utilisateur + overrides explicites."""
        if typologie not in TYPOLOGIES:
            raise KeyError("typologie inconnue %r (%s)" % (typologie, TYPOLOGIES))
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
        """Ajoute un sous-schema propre a une typologie (ex. 'ratelier')."""
        self.schema[racine] = copy.deepcopy(schema_specifique)
        existant = self.valeurs.get(racine, {})
        self.valeurs[racine] = fusion_profonde(_valeurs_depuis_schema(schema_specifique), existant)
        return self

    def fusionner(self, overrides):
        """Fusion profonde d'overrides (dict imbrique ou {chemin.pointe: valeur})."""
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

    def par_statut(self, statut):
        return [(c, v, m) for c, m, v in self.feuilles() if m.statut == statut]

    def a_valider(self):
        return self.par_statut(VAL)

    def repris(self):
        return self.par_statut(REP)

    def todos(self):
        return [(c, m) for c, m, v in self.feuilles() if m.statut == TODO or v is None]

    # -- validation -----------------------------------------------------------
    def valider(self):
        """Bornes, choix et appartenance aux catalogues. Les coherences
        physiques (charges, porte-a-faux, NPT...) sont dans ``rangement.regles``."""
        pbs = []
        for chemin, meta, val in self.feuilles():
            if val is None:
                pbs.append(Probleme("todo", chemin, "valeur inconnue : %s" % (meta.justification or meta.role)))
                continue
            if meta.plage and isinstance(val, (int, float)) and not isinstance(val, bool):
                mini, maxi = meta.plage
                if not (mini <= val <= maxi):
                    pbs.append(Probleme("erreur", chemin, "%s %s hors plage [%s ; %s]" % (val, meta.unite, mini, maxi)))
            if meta.choix and val not in meta.choix:
                pbs.append(Probleme("erreur", chemin, "valeur %r non admise (%s)" % (val, meta.choix)))
        g = self.get
        ess, fin = g("bois.essence"), g("bois.finition")
        if ess in _bois.ESSENCES and fin in _bois.FINITIONS_BOIS and not _bois.finition_compatible(ess, fin):
            pbs.append(Probleme("erreur", "bois.finition", "finition %r reservee a %s (Neogothique)"
                                % (fin, _bois.FINITIONS_BOIS[fin]["essences"])))
        fam, teinte = g("cuir.famille"), g("cuir.teinte")
        if fam in _garn.GARNISSAGES and not _garn.coloris_valide(fam, teinte):
            pbs.append(Probleme("erreur", "cuir.teinte", "teinte %r absente de %s (disponibles : %s)"
                                % (teinte, fam, _garn.GARNISSAGES[fam]["coloris"])))
        met, fm = g("quincaillerie.metal"), g("quincaillerie.finition_metal")
        if fm in _quin.FINITIONS_METAL and not _quin.finition_metal_compatible(met, fm):
            pbs.append(Probleme("erreur", "quincaillerie.finition_metal", "finition %r incompatible avec %r" % (fm, met)))
        pas, mh = g("modules.pas_trous"), g("modules.module_hauteur")
        if pas and abs(mh / pas - round(mh / pas)) > 1e-6:
            pbs.append(Probleme("alerte", "modules.module_hauteur", "%g mm n'est pas un multiple du pas %g mm" % (mh, pas)))
        return pbs

    def erreurs(self):
        return [p for p in self.valider() if p.niveau == "erreur"]

    # -- persistance ----------------------------------------------------------
    def vers_json(self, chemin_fichier=None):
        texte = json.dumps(self.valeurs, indent=2, ensure_ascii=False, sort_keys=True)
        if chemin_fichier:
            with open(chemin_fichier, "w", encoding="utf-8") as f:
                f.write(texte + "\n")
        return texte

    @classmethod
    def depuis_json(cls, texte_ou_chemin):
        if os.path.exists(str(texte_ou_chemin)):
            with open(texte_ou_chemin, "r", encoding="utf-8") as f:
                texte_ou_chemin = f.read()
        return cls(json.loads(texte_ou_chemin))

    # -- export Fusion ----------------------------------------------------------
    @staticmethod
    def nom_fusion(chemin, prefixe="ran_"):
        """'ports.pas_ports' -> 'ran_ports_pas_ports' (nom valide Fusion)."""
        nom = prefixe + re.sub(r"[^A-Za-z0-9_]", "_", chemin.replace(".", "_"))
        if not nom[0].isalpha():
            nom = "p" + nom
        return nom

    UNITES_FUSION = {"mm": "mm", "deg": "deg", "kg": "kg", "": "", "%": "", "N": "N",
                     "MPa": "", "kg/m": "", "kg/m2": ""}

    def parametres_exportables(self):
        """Liste (nom, expression, unite_fusion, commentaire) des numeriques definis."""
        prefixe = self.get("gamme.prefixe_fusion", "ran_")
        res = []
        for chemin, meta, val in self.feuilles():
            if val is None or isinstance(val, bool) or not isinstance(val, (int, float)):
                continue
            unite = self.UNITES_FUSION.get(meta.unite, "")
            expression = ("%g %s" % (val, unite)).strip()
            commentaire = "%s [%s%s] %s" % (chemin, meta.statut, (" " + meta.unite) if meta.unite else "", meta.role)
            res.append((self.nom_fusion(chemin, prefixe), expression, unite, commentaire[:250]))
        return res

    def exporter_user_parameters(self, design):
        """Cree ou met a jour les User Parameters de ``design`` (Fusion convertit
        lui-meme '22 mm' en cm internes). Renvoie (crees, mis_a_jour)."""
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
