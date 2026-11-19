# -*- coding: utf-8 -*-
"""Quincaillerie : metaux, boucles, anneaux D/O, mousquetons, cadenas, rivets, oeillets.

AUCUNE charge de rupture ci-dessous n'est sourcee : ce sont des ESTIMATIONS
d'ordre de grandeur (``statut_charge = "estimation_a_verifier_fournisseur"``)
qui servent seulement a hierarchiser les options. Les regles de securite ne
declarent jamais une piece conforme sur une estimation : elles demandent la
charge de rupture / CMU marquee du fournisseur retenu.

Dimensions (passage interieur = sangle nominale + 1 mm, fil, ardillon, profondeur) : valeurs nominales de conception, a
verifier sur la reference achetee (meme statut).
"""

EST = "estimation_a_verifier_fournisseur"
SRC_EQ_MET = "equinox/equinox/catalogues/metaux.py"
SRC_NEO_FER = "neogothique/neogothique/catalogues/ferrures.py"

METAUX = {
    "inox_316": {"nom": "Inox 316L brosse", "famille": "inox", "aspect": "gris acier", "contact_peau": "ok",
                 "corrosion": "excellente", "cout": "moyen", "reference_meuble": SRC_EQ_MET + " (inox_316)",
                 "rgb": (178, 180, 182), "apparences": ["Stainless Steel - Brushed", "Steel - Satin", "Steel"]},
    "inox_316_pvd_noir": {"nom": "Inox 316L revetu PVD noir", "famille": "inox", "aspect": "noir satine",
                          "contact_peau": "ok", "corrosion": "excellente (revetement rayable)", "cout": "eleve",
                          "reference_meuble": SRC_NEO_FER + " (accord visuel avec fer_forge_mat / cire_noire)",
                          "rgb": (40, 40, 42), "apparences": ["Paint - Enamel Glossy (Black)", "Steel - Satin"]},
    "laiton_massif_cw510l": {"nom": "Laiton massif sans plomb (CW510L), brosse vernis", "famille": "laiton",
                             "aspect": "dore chaud", "contact_peau": "ok", "corrosion": "bonne (ternit sans vernis)",
                             "cout": "eleve", "reference_meuble": SRC_EQ_MET + " (laiton_cw510l, option contact cutane)",
                             "rgb": (196, 160, 84), "apparences": ["Brass - Satin", "Brass - Polished", "Brass"]},
    "laiton_patine": {"nom": "Laiton patine vieilli", "famille": "laiton", "aspect": "brun-or",
                      "contact_peau": "eviter_contact_prolonge", "corrosion": "moyenne", "cout": "eleve",
                      "reference_meuble": SRC_NEO_FER + " (FINITIONS.laiton_patine_vieilli : eviter contact prolonge)",
                      "rgb": (120, 96, 52), "apparences": ["Brass - Satin", "Brass"]},
    "acier_nickele": {"nom": "Acier nickele (entree de gamme)", "famille": "acier", "aspect": "gris brillant",
                      "contact_peau": "deconseille_allergie_nickel", "corrosion": "faible (rouille aux eclats)",
                      "cout": "bas", "reference_meuble": "", "rgb": (200, 200, 205),
                      "apparences": ["Nickel - Polished", "Steel - Polished"]},
}


def _piece(nom, metal, charge, **kw):
    d = {"nom": nom, "metal": metal, "charge_rupture_n": charge, "statut_charge": EST}
    d.update(kw)
    return d


BOUCLES = {
    "boucle_rouleau_50_laiton": _piece("Boucle a rouleau pour sangle 50 mm, laiton massif", "laiton_massif_cw510l", 3000.0,
                                       passage=51.0, ardillon_diametre=4.0, cadre_fil=5.0, profondeur=22.0, verrouillable=False),
    "boucle_rouleau_50_inox": _piece("Boucle a rouleau pour sangle 50 mm, inox", "inox_316", 4000.0,
                                     passage=51.0, ardillon_diametre=4.0, cadre_fil=5.0, profondeur=22.0, verrouillable=False),
    "boucle_rouleau_60_laiton": _piece("Boucle a rouleau pour sangle 60 mm, laiton massif", "laiton_massif_cw510l", 3000.0,
                                       passage=61.0, ardillon_diametre=4.0, cadre_fil=5.0, profondeur=22.0, verrouillable=False),
    "boucle_rouleau_60_inox": _piece("Boucle a rouleau pour sangle 60 mm, inox", "inox_316", 4000.0,
                                     passage=61.0, ardillon_diametre=4.0, cadre_fil=5.0, profondeur=22.0, verrouillable=False),
    "boucle_verrouillable_50_inox": _piece("Boucle verrouillable pour sangle 50 mm, inox (ardillon perce pour cadenas)", "inox_316",
                                           4000.0, passage=51.0, ardillon_diametre=4.0, cadre_fil=5.0, profondeur=22.0,
                                           verrouillable=True),
}

ANNEAUX = {
    "anneau_d_inox_soude_5x25": _piece("Anneau D inox soude fil 5 mm, passage 25 mm", "inox_316", 2500.0,
                                       forme="D", fil=5.0, passage=25.0, hauteur=22.0, soude=True),
    "anneau_d_inox_soude_6x30": _piece("Anneau D inox soude fil 6 mm, passage 30 mm", "inox_316", 4000.0,
                                       forme="D", fil=6.0, passage=30.0, hauteur=26.0, soude=True),
    "anneau_d_laiton_massif_6x30": _piece("Anneau D laiton massif (moule) fil 6 mm, passage 30 mm",
                                          "laiton_massif_cw510l", 2500.0, forme="D", fil=6.0, passage=30.0,
                                          hauteur=26.0, soude=False),
    "anneau_o_inox_soude_6x30": _piece("Anneau O inox soude fil 6 mm, diametre interieur 30 mm", "inox_316", 4000.0,
                                       forme="O", fil=6.0, passage=30.0, hauteur=30.0, soude=True),
}

MOUSQUETONS = {
    "mousqueton_panique_inox": _piece("Mousqueton panique (ouverture sous charge) inox", "inox_316", 3500.0,
                                      ouverture_sous_charge=True, notes="Attache de deverrouillage rapide recommandee."),
    "mousqueton_simple_inox": _piece("Mousqueton a doigt inox", "inox_316", 3000.0, ouverture_sous_charge=False),
    "mousqueton_laiton": _piece("Mousqueton a emerillon laiton", "laiton_massif_cw510l", 1500.0,
                                ouverture_sous_charge=False, notes="Decoratif : emerillon = maillon faible."),
}

CADENAS = {
    "cadenas_laiton_20": _piece("Petit cadenas laiton 20 mm a cle", "laiton_massif_cw510l", None, anse_diametre=3.5,
                                notes="Ne porte pas la charge (traverse l'ardillon / les anneaux). Cle a portee."),
    "cadenas_inox_25": _piece("Cadenas inox 25 mm a cle", "inox_316", None, anse_diametre=4.0,
                              notes="Ne porte pas la charge. Prevoir un double de cle."),
}

RIVETS = {
    "rivet_double_calotte_9": _piece("Rivet double calotte tete 9 mm", None, 500.0, tete=9.0, tige=3.0,
                                     longueurs_tige=[6.0, 8.0, 10.0, 12.0], metaux=["laiton_massif_cw510l", "inox_316"],
                                     notes="Charge = cisaillement par rivet, estimation."),
    "rivet_double_calotte_12": _piece("Rivet double calotte tete 12 mm", None, 700.0, tete=12.0, tige=3.5,
                                      longueurs_tige=[8.0, 10.0, 12.0, 14.0], metaux=["laiton_massif_cw510l", "inox_316"]),
    "rivet_cuivre_contre_rivet": _piece("Rivet cuivre a contre-rivet (rive au marteau)", None, 800.0, tete=9.5,
                                        tige=3.0, longueurs_tige=[10.0, 12.0, 15.0], metaux=["cuivre"],
                                        reference_meuble="neogothique/neogothique/catalogues/garnissage.py "
                                                         "(fixation : rivets cuivre a contre-rivet)",
                                        notes="Le plus solide et reparable ; tete cuivre (accord cognac / havane)."),
}

OEILLETS = {
    "oeillet_5": _piece("Oeillet a rondelle diametre interieur 5 mm", None, None, diametre_interieur=5.0,
                        collerette=10.0, metaux=["laiton_massif_cw510l", "inox_316"]),
    "oeillet_8": _piece("Oeillet a rondelle diametre interieur 8 mm", None, None, diametre_interieur=8.0,
                        collerette=15.0, metaux=["laiton_massif_cw510l", "inox_316"]),
}

TOUTES = {"boucle": BOUCLES, "anneau": ANNEAUX, "mousqueton": MOUSQUETONS, "cadenas": CADENAS,
          "rivet": RIVETS, "oeillet": OEILLETS}
