# -*- coding: utf-8 -*-
"""Chiffrage indicatif des 4 typologies proposées (nomenclatures estimées à la main).

Ce n'est PAS un script de grammaire : les quantités ci-dessous sont des
estimations de pré-projet ; elles seront remplacées par les volumes réels
extraits des modèles Fusion (couche 3). Usage : python outils/chiffrage_indicatif.py
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "TantraGamme"))
from lib import catalogues as cat  # noqa: E402
from lib import params_globaux as pg  # noqa: E402

NOMENCLATURES = [
    cat.Nomenclature("T1 La Vague (chaise longue en S)", bois_droit_m3=0.021, bois_cintre_m3=0.042,
                     mousses_m3={"HR45": 0.075, "VISCO50": 0.027}, revetement_m2=1.8,
                     surface_finition_m2=2.5, quincaillerie_eur=60, heures_ebeniste=(50, 70),
                     heures_tapissier=(12, 18), fournitures_garnissage_eur=220),
    cat.Nomenclature("T2 Le Lotus (fauteuil bas incliné à cale)", bois_droit_m3=0.018, bois_cintre_m3=0.009,
                     mousses_m3={"HR45": 0.034, "HR55F": 0.010, "HR35": 0.030}, revetement_m2=2.0,
                     surface_finition_m2=1.8, quincaillerie_eur=70, heures_ebeniste=(35, 50),
                     heures_tapissier=(12, 16), fournitures_garnissage_eur=80),
    cat.Nomenclature("T3 L'Autel (banquette de position à appui lombaire)", bois_droit_m3=0.019,
                     bois_cintre_m3=0.0025, mousses_m3={"HR45": 0.050, "HR35": 0.016}, revetement_m2=1.8,
                     surface_finition_m2=1.2, quincaillerie_eur=50, heures_ebeniste=(22, 32),
                     heures_tapissier=(8, 12), fournitures_garnissage_eur=60),
    cat.Nomenclature("T4 Le Diptyque (fauteuil à double plan)", bois_droit_m3=0.062, bois_cintre_m3=0.005,
                     mousses_m3={"HR45": 0.058, "HR35": 0.024}, revetement_m2=1.9,
                     surface_finition_m2=2.6, quincaillerie_eur=80, heures_ebeniste=(45, 65),
                     heures_tapissier=(12, 18), fournitures_garnissage_eur=120),
]


def arrondi(x, pas=50):
    return int(round(x / pas) * pas)


def main():
    for n in NOMENCLATURES:
        print(f"\n## {n.nom}")
        print(f"bois net {n.bois_droit_m3 + n.bois_cintre_m3:.3f} m³")
        for ess in ("chene", "frene", "noyer"):
            c = cat.chiffrage(n, ess)
            b, g, q, mo, t = c["bois"], c["garnissage"], c["quincaillerie_finition"], c["main_oeuvre"], c["total"]
            print(f"  {ess:6s} brut {c['volume_brut_m3'][0]:.3f} m³ | bois {arrondi(b[0],10)}–{arrondi(b[1],10)} | "
                  f"garn {arrondi(g[0],10)}–{arrondi(g[1],10)} | quinc+fin {arrondi(q[0],10)} | "
                  f"MO {arrondi(mo[0])}–{arrondi(mo[1])} | TOTAL {arrondi(t[0],100)}–{arrondi(t[1],100)} € HT")


if __name__ == "__main__":
    main()
    p = pg.PARAMS
    ch = p.charges.charge_verticale_N()
    ess = p.essence()
    print("\nCharge de conception :", round(ch), "N")
    print("Pied T2 h300 :", cat.section_pied(ch, 300, ess, epaisseur_tenon=12))
    print("Pied T4 h570 :", cat.section_pied(ch, 570, ess, nb_pieds=6, epaisseur_tenon=10))
    print("Latte T1 portée 560, 1/5 charge :", cat.hauteur_traverse(560, ch / 5, 60, ess, hauteur_min=20))
    print("Latte T4 portée 680, 1/6 charge :", cat.hauteur_traverse(680, ch / 6, 60, ess, hauteur_min=20))
    print("Ceinture T3 portée 1100, 1/2 charge :", cat.hauteur_traverse(1100, ch / 2, 30, ess))
    print("Tourillons e=40, l=220 :", cat.spec_tourillons(40, 220))
    print("Tenon traverse 30x100 / pied 55 :", cat.spec_tenon(30, 100, 55))
    print("Tenon traverse 36x80 / flasque 45 :", cat.spec_tenon(36, 80, 45))
    print("Arrachement vis 6x80 (ancrage 50) chêne :", round(cat.resistance_arrachement_vis(6, 50, ess)), "N")
