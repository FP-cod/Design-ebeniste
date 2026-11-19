# -*- coding: utf-8 -*-
import math

from equinox import calculs, geometrie as geo


def test_fuseau_volume_et_cylindre():
    f = geo.Fuseau("f", (0, 0, 0), (0, 0, 100), 20, 20, "frene")
    assert abs(f.volume_mm3() - math.pi * 100 * 100) < 1e-6
    c = geo.Fuseau("c", (0, 0, 0), (0, 0, 100), 50, 30, "frene")
    assert c.centroide()[2] < 50  # plus de matiere en bas (gros bout)
    assert abs(c.masse_kg() - c.volume_mm3() * 1e-9 * 680) < 1e-9


def test_rotation_y_convention_fusion():
    p = geo.rotation_y((100, 0, 0), (0, 0, 0), 90)
    assert abs(p[0]) < 1e-9 and abs(p[2] + 100) < 1e-9  # X -> -Z


def test_helice_depart_arrivee_et_tours():
    pts = geo.helice_elliptique((0, 0, 300), (100, 50, 360), 30, 120, 110, 2.0, angle_depart_deg=180)
    assert abs(geo.norme(geo.sub(pts[0], (-30, 0, 300)))) < 1e-6
    assert abs(pts[-1][2] - 360) < 1e-6
    # angle balaye : 2 tours
    tours = 0.0
    for a, b in zip(pts[:-1], pts[1:]):
        ca = math.atan2(a[1], a[0])
        cb = math.atan2(b[1], b[0])
        tours += (cb - ca + math.pi) % (2 * math.pi) - math.pi
    assert 1.0 < abs(tours) / (2 * math.pi) < 3.0


def test_superellipse_et_rayon():
    c = geo.contour_superellipse(1000, 300, 2.0, n=400)
    aire = geo.PlaqueContour("p", c, 0, 1, "contreplaque_bouleau").aire()
    assert abs(aire - math.pi * 500 * 150) / aire < 0.01
    r = geo.rayon_trois_points((1, 0, 0), (0, 1, 0), (-1, 0, 0))
    assert abs(r - 1) < 1e-9


def test_stabilite_cas_simple():
    appuis = [(0, 0), (1000, 0), (1000, 500), (0, 500)]
    res = calculs.stabilite([(100, (500, 250, 500))], [("F", (100.0, 0.0), 1000.0)], appuis, (500, 250), 1.5)
    # M stab = 100*9.81*500 ; M renv = 100*1000
    assert abs(res["cas"][0]["ratio"] - 100 * 9.81 * 500 / 1e5) < 1e-6
    assert res["marge_cg_mm"] == 250
    res2 = calculs.stabilite([(10, (500, 250, 500))], [("F", (500.0, 0.0), 1000.0)], appuis, (500, 250), 1.5)
    assert res2["lest_additionnel_kg"] > 0


def test_helice_formule_ressort():
    v, d_req = calculs.verifier_helice(353.0, 230.0, 12.0, 2, "inox_316", 1.8)
    assert v[0].niveau == "echec" and 14 < d_req < 17
    v2, _ = calculs.verifier_helice(353.0, 230.0, 20.0, 2, "inox_316", 1.8)
    assert v2[0].niveau == "ok"
