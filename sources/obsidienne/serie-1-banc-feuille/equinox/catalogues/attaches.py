# -*- coding: utf-8 -*-
"""Catalogue des systemes d'attache et de jonction.

Proprietes :

- ``famille`` : 'jonction_bois' | 'quincaillerie' | 'ancrage' | 'mecanisme'
- ``capacite_service`` : charge de service indicative [N] (CMU / WLL).
  A VALIDER : prendre la CMU marquee du fabricant pour les ancrages.
- ``dimensionnement`` : regle d'atelier lisible
- ``regles`` : regles declaratives (cf. catalogues.__init__)

Les ancrages (oeillets, anneaux) doivent etre des pieces forgees ou
soudees-testees avec CMU marquee ; ne jamais utiliser de piton visse dans
le bois de bout comme point de retenue.
"""

ATTACHES = {
    "tourillon_hetre": {
        "nom": "Tourillon hetre cannele", "famille": "jonction_bois",
        "diametres": [6, 8, 10, 12, 14], "capacite_service": 1500.0,
        "dimensionnement": "d ~ section/5 arrondi au standard ; longueur >= 5 d ; 2 tourillons mini par jonction",
        "regles": [
            {"cible": "jonctions.diametre_tourillon", "calcul": "tourillon", "raison": "d = section_noeud / 5"},
            {"cible": "jonctions.longueur_tourillon", "calcul": "longueur_tourillon", "raison": "L = 5 d"}],
    },
    "tenon_mortaise": {
        "nom": "Tenon-mortaise colle (+ cheville)", "famille": "jonction_bois",
        "capacite_service": 3000.0,
        "dimensionnement": "tenon = section/3 ; profondeur = 0,8 x section ; cheville d 8 decalee 1 mm (tire-fort)",
        "regles": [
            {"cible": "jonctions.epaisseur_tenon", "calcul": "tenon", "raison": "regle du tiers"},
            {"cible": "jonctions.profondeur_mortaise", "calcul": "mortaise", "raison": "0,8 x section au noeud"}],
    },
    "vis_bois_inox": {
        "nom": "Vis bois inox A4 tete fraisee", "famille": "quincaillerie",
        "diametres": [4, 5, 6], "capacite_service": 800.0,
        "dimensionnement": "avant-trou 70 % du d dans les feuillus durs ; ancrage >= 8 d ; jamais en bois de bout seul",
        "regles": [],
    },
    "insert_filete_m8": {
        "nom": "Insert filete inox M8 a visser (type Ensat)", "famille": "quincaillerie",
        "filetage": "M8", "capacite_service": 2500.0,
        "dimensionnement": "longueur 20 mm dans densite >= 650 kg/m3, 25 mm en dessous ; colle epoxy conseillee",
        "regles": [{"cible": "jonctions.longueur_insert", "calcul": "longueur_insert", "raison": "selon densite"}],
    },
    "vis_barillet_m8": {
        "nom": "Boulon + ecrou barillet M8 (cross-dowel)", "famille": "quincaillerie",
        "capacite_service": 4000.0,
        "dimensionnement": "barillet d 10 a >= 2,5 d du bout ; demontable (traverse / pieds)",
        "regles": [],
    },
    "glissiere_inox_genou": {
        "nom": "Glissiere inox a billes + doigt d'indexage", "famille": "mecanisme",
        "course": 150.0, "capacite_service": 1200.0, "pas_indexage": 25.0,
        "dimensionnement": "charge par glissiere >= charge genou x coef dynamique ; doigt d'indexage a ressort",
        "regles": [],
    },
    "pivot_crans": {
        "nom": "Pivot d'helice : axe inox + bague bronze + doigt d'indexage a ressort", "famille": "mecanisme",
        "capacite_service": 2000.0,
        "dimensionnement": "axe d >= 16 ; 1 trou d'indexage par cran ; bague bronze frettee dans le pied",
        "regles": [],
    },
    "oeillet_inox_8": {
        "nom": "Oeillet inox A4 fil 8 mm sur platine 2 mm (soude, teste)", "famille": "ancrage",
        "fil": 8.0, "capacite_service": 2000.0,
        "dimensionnement": "platine vissee 4 x vis 5 + insert M8 traversant ; CMU fabricant >= effort calcule",
        "regles": [],
    },
    "anneau_inox_8": {
        "nom": "Anneau inox A4 fil 8 mm, di 40, sur pontet + tige filetee M8 traversante", "famille": "ancrage",
        "fil": 8.0, "capacite_service": 2500.0,
        "dimensionnement": "tige traversant la traverse et le tube, ecrou borgne + rondelle cote oppose",
        "regles": [],
    },
}
