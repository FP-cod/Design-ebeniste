# -*- coding: utf-8 -*-
"""Courbes paramétriques et géométrie."""
import pytest

from tantra import courbes as C
from tantra.geometrie import CasStabilite, coefficient_stabilite, empreinte_au_sol, masse_et_cdg, prisme


def test_hermite_passe_par_les_points_cles():
    pts = (C.PointCle(0, 400, 0), C.PointCle(500, 300, -10), C.PointCle(1000, 700, 40))
    prof = C.profil_hermite(pts, n_par_segment=10)
    assert prof[0] == pytest.approx((0, 400))
    assert prof[-1] == pytest.approx((1000, 700))
    assert C.est_monotone_y(prof)
    assert C.z_a(prof, 500) == pytest.approx(300, abs=1)


def test_rayon_cercle_3_points():
    assert C.rayon_cercle_3_points((-100, 0), (0, 100), (100, 0)) == pytest.approx(100)


def test_aire_centroide_rectangle_tourner():
    r = C.rectangle(0, 0, 100, 50)
    assert C.aire_polygone(r) == pytest.approx(5000)
    assert C.centroide_polygone(r) == pytest.approx((50, 25))
    t = C.tourner(r, 180, (0, 0))
    assert C.centroide_polygone(t) == pytest.approx((-50, -25))


def test_masse_cdg_et_stabilite():
    p = [prisme("a", "pied", "chene", 0, 0, 0, 100, 100, 100)]
    m, cdg = masse_et_cdg(p, {"chene": 1000})
    assert m == pytest.approx(1.0)
    assert cdg == pytest.approx((50, 50, 50))
    emp = empreinte_au_sol(p)
    coef, _ = coefficient_stabilite(CasStabilite("t", (), (9.81, "+x", 50)), m, cdg, emp)
    assert coef == pytest.approx(1.0)
