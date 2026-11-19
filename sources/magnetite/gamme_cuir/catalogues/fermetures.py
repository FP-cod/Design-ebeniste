# -*- coding: utf-8 -*-
"""Systemes de fermeture et jonctions (couture sellier, rivets, oeillets).

Notes 0-3 qualitatives (3 = meilleur), pas des mesures.
"""

FERMETURES = {
    "boucle_ardillon": {"nom": "Boucle a ardillon", "reglage": 3, "tenue_contention": 3, "ouverture_rapide": 2,
                        "cle": False, "pieces": ["boucle"], "cout": "moyen",
                        "notes": "Reference : reglable trou par trou, s'ouvre sans outil."},
    "boucle_ardillon_cadenas": {"nom": "Boucle verrouillable + cadenas", "reglage": 3, "tenue_contention": 3,
                                "ouverture_rapide": 0, "cle": True, "pieces": ["boucle", "cadenas"], "cout": "eleve",
                                "boucle_verrouillable_requise": True,
                                "notes": "Ouverture lente (cle) : deverrouillage rapide en aval obligatoire."},
    "mousqueton": {"nom": "Fermeture par mousqueton entre deux anneaux", "reglage": 0, "tenue_contention": 2,
                   "ouverture_rapide": 3, "cle": False, "pieces": ["mousqueton", "anneau"], "cout": "moyen",
                   "notes": "Pas de reglage : longueur fixe a la taille exacte."},
    "scratch": {"nom": "Bande auto-agrippante (scratch)", "reglage": 2, "tenue_contention": 0, "ouverture_rapide": 3,
                "cle": False, "pieces": [], "cout": "bas",
                "notes": "Jeu leger uniquement : s'ouvre sous traction, s'use, accroche les textiles."},
}

JONCTIONS = {
    "couture_sellier": {"nom": "Couture point sellier (deux aiguilles)", "solidite": 3, "finition": 3, "cout": "eleve",
                        "temps": "long", "reparable": True,
                        "notes": "Indecousable (un fil casse, l'autre tient). Reference Neogothique."},
    "rivets": {"nom": "Rivets (double calotte ou a contre-rivet)", "solidite": 2, "finition": 2, "cout": "bas",
               "temps": "court", "reparable": True,
               "notes": "Rapide ; effort concentre sur la tige ; tete metallique possible cote peau."},
    "rivets_et_couture": {"nom": "Couture sellier + rivets", "solidite": 3, "finition": 3, "cout": "eleve",
                          "temps": "long", "reparable": True, "notes": "Redondance pour la contention."},
    "oeillets": {"nom": "Oeillets (passage de lacet, mousqueton leger)", "solidite": 1, "finition": 2, "cout": "bas",
                 "temps": "court", "reparable": False, "notes": "Ne pas utiliser comme point d'attache de retenue."},
}
