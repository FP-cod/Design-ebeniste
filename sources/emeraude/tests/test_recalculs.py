# -*- coding: utf-8 -*-
"""Tests pur Python des couches 1-2 (sans Fusion).

Lancer depuis /workspace/tantra :  python -m unittest discover -s tests -v
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "TantraGamme"))

from lib import catalogues as cat  # noqa: E402
from lib import params_globaux as pg  # noqa: E402
from lib import fusion_params  # noqa: E402,F401  (doit s'importer sans adsk)


class TestCouche1(unittest.TestCase):
    def test_charge_conception(self):
        # 2 × 120 kg × 9,81 × 2,0
        self.assertAlmostEqual(pg.PARAMS.charges.charge_verticale_N(), 4708.8, places=1)

    def test_conversion_fusion(self):
        self.assertEqual(pg.mm_vers_cm(450), 45.0)

    def test_parametres_fusion_noms_valides(self):
        params = pg.parametres_fusion()
        self.assertGreaterEqual(len(params), 15)
        for nom, (val, unite, _) in params.items():
            self.assertTrue(nom.isascii() and nom.replace("_", "").isalnum(), nom)
            self.assertIn(unite, ("mm", "deg"))
            self.assertGreater(val, 0)

    def test_essences_coherentes(self):
        for e in pg.ESSENCES.values():
            self.assertLess(e.prix_m3_bas, e.prix_m3_haut)
        self.assertGreater(pg.ESSENCES["noyer"].prix_m3_moyen, pg.ESSENCES["chene"].prix_m3_moyen)


class TestCouche2(unittest.TestCase):
    def test_diametre_tourillon(self):
        self.assertEqual(cat.diametre_tourillon(22), 8)
        self.assertEqual(cat.diametre_tourillon(30), 10)
        self.assertEqual(cat.diametre_tourillon(40), 14)
        with self.assertRaises(ValueError):
            cat.diametre_tourillon(10)

    def test_spec_tourillons(self):
        s = cat.spec_tourillons(22, 300)
        self.assertEqual(s.diametre, 8)
        self.assertEqual(s.longueur, 40)
        self.assertGreaterEqual(s.nombre, 2)
        self.assertGreaterEqual(s.entraxe, 4 * s.diametre)

    def test_spec_tenon(self):
        t = cat.spec_tenon(30, 100, 55)
        self.assertEqual(t.epaisseur, 10)
        self.assertTrue(t.double_tenon)
        self.assertLessEqual(t.longueur, 55 * 2 / 3 + 1e-6)
        self.assertIn("Paroi", cat.spec_tenon(40, 80, 40).alerte)

    def test_section_pied_croit_avec_hauteur(self):
        e = pg.ESSENCES["chene"]
        bas = cat.section_pied(20000, 300, e, section_min=0)
        haut = cat.section_pied(20000, 900, e, section_min=0)
        self.assertGreater(haut.cote_stabilite, bas.cote_stabilite)
        self.assertEqual(cat.section_pied(4709, 300, e).critere, "esthétique/minimum")

    def test_hauteur_traverse_fleche(self):
        e = pg.ESSENCES["chene"]
        r = cat.hauteur_traverse(1100, 2354, 30, e)
        self.assertEqual(r.critere, "flèche")
        self.assertEqual(r.cote, 60)

    def test_prix_volume(self):
        e = pg.ESSENCES["chene"]
        bas, haut = cat.prix_bois(0.1, e)  # 0,1 m³ × 1,5 × 1800/3000
        self.assertAlmostEqual(bas, 270.0)
        self.assertAlmostEqual(haut, 450.0)
        self.assertGreater(cat.prix_bois(0.1, e, cintre=True)[0], bas)

    def test_colle_et_avant_trou(self):
        self.assertEqual(cat.recommandation_colle("insert").nom, "Époxy structurelle")
        self.assertEqual(cat.avant_trou_vis(6, pg.ESSENCES["chene"]), 4.0)
        self.assertGreater(cat.resistance_arrachement_vis(6, 50, pg.ESSENCES["chene"]), 1000)

    def test_basculement(self):
        self.assertEqual(cat.marge_basculement(500, 0, 1800), 500)
        self.assertLess(cat.marge_basculement(1900, 0, 1800), 0)

    def test_chiffrage_ordre(self):
        n = cat.Nomenclature("test", 0.02, 0.01, {"HR45": 0.03}, 1.5, 1.5, 50, (30, 40), (8, 12))
        c = cat.chiffrage(n, "chene")
        self.assertLess(c["total"][0], c["total"][1])
        self.assertGreater(cat.chiffrage(n, "noyer")["bois"][1], c["bois"][1])


if __name__ == "__main__":
    unittest.main()
